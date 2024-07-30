import pandas as pd
import os
import argparse
from tqdm import tqdm
import webbrowser
from datetime import datetime

from utils import clear_directory, download_image
from image_processing import remove_background
from drawing import create_final_image
from constants import base_dir, downloaded_dir, no_background_dir, final_dir, font_path, card_path, template_path

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process images for promotions.')
parser.add_argument('--skip-download', action='store_true', help='Skip downloading and processing images')
args = parser.parse_args()

# Load the Excel file
file_path = 'Promos Fotos Datos.xlsx'
df = pd.read_excel(file_path, header=0)

# Extract the relevant columns
urls = df['Link Foto'].dropna().tolist()
prices = df['Precio de venta'].dropna().astype(float).tolist()
delivery_times = df['TIEMPO DE ENTREGA'].dropna().tolist()
sizes = df['Talla'].dropna().astype(str).tolist()  # Convert to string
genders = df['Genero'].fillna('hombre').tolist()  # Fill missing values with 'hombre'
types = df['Tipo'].fillna('').tolist()  # Fill missing values with empty string
dates = df['fecha'].dropna().apply(lambda date: pd.to_datetime(date, format='%d/%m/%Y', dayfirst=True, errors='coerce')).tolist()

# Ensure the lists are of the same length
min_length = min(len(urls), len(prices), len(delivery_times), len(sizes), len(genders), len(types), len(dates))
urls = urls[:min_length]
prices = prices[:min_length]
delivery_times = delivery_times[:min_length]
sizes = sizes[:min_length]
genders = genders[:min_length]
types = types[:min_length]
dates = dates[:min_length]

# Create directories if they don't exist
for dir_path in [downloaded_dir, no_background_dir, final_dir]:
    os.makedirs(dir_path, exist_ok=True)

# Clear directories before processing
if not args.skip_download:
    clear_directory(downloaded_dir)
    clear_directory(no_background_dir)
clear_directory(final_dir)

# Paths for saving images
input_paths = [os.path.join(downloaded_dir, f"image_{i}.png") for i in range(len(urls))]
output_paths = [os.path.join(no_background_dir, f"image_no_bg_{i}.png") for i in range(len(urls))]

# Path for error log
error_log_path = os.path.join(base_dir, 'error_log.txt')
if not args.skip_download:
    # Clear the error log file
    with open(error_log_path, "w") as log_file:
        log_file.write("")

# Download and process images if flag is not set
if not args.skip_download:
    print("Downloading and processing images...")
    for i, url in enumerate(tqdm(urls, desc="\033[94mDownloading images\033[0m", unit="image", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} left: {remaining}]')):
        if download_image(url, input_paths[i], error_log_path):
            remove_background(input_paths[i], output_paths[i], error_log_path)

# Create final images
print("Creating final images...")
for i in tqdm(range(0, len(urls), 3), desc=f"\033[92mProcessing images\033[0m", unit="batch", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} left: {remaining}]'):
    create_final_image(i, urls, prices, delivery_times, sizes, genders, types, dates, input_paths, output_paths, final_dir, font_path, card_path, template_path)

# Open the final directory in the file explorer
webbrowser.open('file://' + os.path.realpath(final_dir))

print(f"All images processed and saved. You can view them in the following directory: {final_dir}")
