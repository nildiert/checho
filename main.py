# main.py

import pandas as pd
import os
import argparse
from tqdm import tqdm
import webbrowser
from datetime import datetime

from utils import clear_directory, download_image
from image_processing import remove_background
from drawing import create_final_image, create_square_image
from constants import base_dir, downloaded_dir, no_background_dir, final_dir, font_path, card_path, template_path, square_template_path

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process images for promotions.')
parser.add_argument('--skip-download', action='store_true', help='Skip downloading and processing images')
parser.add_argument('--imagenes-cuadradas', action='store_true', help='Crear imágenes cuadradas en images/final/cuadradas')
args = parser.parse_args()

# Load the Excel file
file_path = 'Promos Fotos Datos.xlsx'
df = pd.read_excel(file_path, header=0)

# Extract the relevant columns
urls = df['Link Foto'].dropna().tolist()
prices_raw = df['Precio de venta'].tolist()
prices = [float(p) if pd.notnull(p) else None for p in prices_raw]
delivery_times = df['TIEMPO DE ENTREGA'].dropna().tolist()
sizes = df['Talla'].astype(str).tolist()
genders = df['Genero'].fillna('hombre').tolist()
types = df['Tipo'].fillna('').tolist()
dates = df['fecha'].apply(lambda date: pd.to_datetime(date, format='%d/%m/%Y', dayfirst=True, errors='coerce')).tolist()
logos = df['Logo'].fillna('').tolist()
custom_texts = df['Texto Personalizado'].fillna('').tolist()

# Asegurarse de usar la longitud de URLs para cortar las listas (evita errores con precios nulos)
min_length = len(urls)
urls = urls[:min_length]
prices = prices[:min_length]
delivery_times = delivery_times[:min_length]
sizes = sizes[:min_length]
genders = genders[:min_length]
types = types[:min_length]
dates = dates[:min_length]
logos = logos[:min_length]
custom_texts = custom_texts[:min_length]

# Create directories if they don't exist
for dir_path in [downloaded_dir, no_background_dir, final_dir]:
    os.makedirs(dir_path, exist_ok=True)

# Clear directories before processing
if not args.skip_download and not args.imagenes_cuadradas:
    clear_directory(downloaded_dir)
    clear_directory(no_background_dir)
clear_directory(final_dir)

# Paths for saving images
input_paths = [os.path.join(downloaded_dir, f"image_{i}.png") for i in range(len(urls))]
output_paths = [os.path.join(no_background_dir, f"image_no_bg_{i}.png") for i in range(len(urls))]

# Path for error log
error_log_path = os.path.join(base_dir, 'error_log.txt')
if not args.skip_download:
    with open(error_log_path, "w") as log_file:
        log_file.write("")

# Download and process images if flag is not set
if not args.skip_download and not args.imagenes_cuadradas:
    print("Downloading and processing images...")
    for i, url in enumerate(tqdm(urls, desc="\033[94mDownloading images\033[0m", unit="image", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} left: {remaining}]')):
        if download_image(url, input_paths[i], error_log_path):
            remove_background(input_paths[i], output_paths[i], error_log_path)

if args.imagenes_cuadradas:
    print("Creating square images...")
    for i in tqdm(range(len(urls)), desc="\033[92mProcessing square images\033[0m", unit="image", ncols=100):
        create_square_image(i, urls, prices, delivery_times, sizes, genders, types, dates, logos, input_paths, output_paths, final_dir, font_path, square_template_path, custom_texts)
else:
    print("Creating final images...")
    for mode in ['light', 'dark']:
        if mode == 'light':
            card_paths = {
                'with_prices': 'templates/light_card.png',
                'without_prices': 'templates/light_card.png'
            }
            template_paths = {
                'with_prices': 'templates/light_template.png',
                'without_prices': 'templates/without_price_light_template.png'
            }
        else:
            card_paths = {
                'with_prices': 'templates/dark_card.png',
                'without_prices': 'templates/dark_card.png'
            }
            template_paths = {
                'with_prices': 'templates/dark_template.png',
                'without_prices': 'templates/without_price_dark_template.png'
            }

        for with_price_key, with_price_flag in [('with_prices', True), ('without_prices', False)]:
            current_card_path = card_paths[with_price_key]
            current_template_path = template_paths[with_price_key]

            for i in tqdm(range(0, len(urls), 3), desc=f"\033[92mProcessing {mode} images ({with_price_key})\033[0m", unit="batch", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} left: {remaining}]'):
                if with_price_flag and any(prices[i + j] is None for j in range(3) if i + j < len(prices)):
                    continue  # Saltar si se requiere precio pero alguno de los 3 no lo tiene
                if with_price_flag:
                    create_final_image(i, urls, prices, delivery_times, sizes, genders, types, dates, logos, input_paths, output_paths, final_dir, font_path, current_card_path, current_template_path, mode, with_price=True)
                else:
                    create_final_image(i, urls, prices, delivery_times, sizes, genders, types, dates, logos, input_paths, output_paths, final_dir, font_path, current_card_path, current_template_path, mode, with_price=False)

# Open the final directory in the file explorer
if args.imagenes_cuadradas:
    webbrowser.open('file://' + os.path.realpath(os.path.join(final_dir, "cuadradas")))
else:
    webbrowser.open('file://' + os.path.realpath(final_dir))

print(f"All images processed and saved. You can view them in the following directory: {final_dir}")
