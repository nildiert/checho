import requests
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import argparse
from tqdm import tqdm
import webbrowser
import shutil
from datetime import datetime

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

# Convert 'fecha' column to datetime, handling both string and numeric formats
def convert_dates(date):
    try:
        return pd.to_datetime(date, format='%d/%m/%Y', dayfirst=True)
    except (ValueError, TypeError):
        return pd.to_datetime(date, origin='1899-12-30', unit='D')

dates = df['fecha'].dropna().apply(convert_dates).tolist()

# Ensure the lists are of the same length
urls = urls[:len(prices)]

# Define directories
base_dir = 'images'
downloaded_dir = os.path.join(base_dir, 'downloaded')
no_background_dir = os.path.join(base_dir, 'no_background')
final_dir = os.path.join(base_dir, 'final')

# Create directories if they don't exist
os.makedirs(downloaded_dir, exist_ok=True)
os.makedirs(no_background_dir, exist_ok=True)
os.makedirs(final_dir, exist_ok=True)

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def download_image(url, path, error_log_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as file:
            file.write(response.content)
        return True
    else:
        error_message = f"Failed to download image from {url}. Status code: {response.status_code}\n\n"
        with open(error_log_path, "a") as log_file:
            log_file.write(error_message)
        print(error_message.strip())
        return False

def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    cropped_image = crop_image(output_image)
    cropped_image.save(output_path)

def crop_image(image):
    # Ensure image is in RGBA format
    image = image.convert("RGBA")
    bbox = image.getbbox()
    return image.crop(bbox)

def draw_rounded_rectangle(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)

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
        success = download_image(url, input_paths[i], error_log_path)
        if success:
            try:
                remove_background(input_paths[i], output_paths[i])
            except Exception as e:
                error_message = f"Failed to process image {input_paths[i]}. Reason: {e}\n\n"
                with open(error_log_path, "a") as log_file:
                    log_file.write(error_message)
                print(error_message.strip())

def parse_sizes(size_str):
    size_list = []
    for part in size_str.split():
        if '...' in part:
            start, end = map(float, part.split('...'))
            size_list.extend([start + 0.5 * i for i in range(int((end - start) * 2) + 1)])
        elif '..' in part:
            start, end = map(float, part.split('..'))
            size_list.extend(range(int(start), int(end) + 1))
        else:
            size_list.append(float(part))
    return sorted(set(size_list))

# Create final images with prices and size information
font_path = "fonts/label_font.ttf"
price_font = ImageFont.truetype(font_path, 48)  # Updated font size for price
label_font = ImageFont.truetype(font_path, 40)  # Increased font size for the label
delivery_font = ImageFont.truetype(font_path, 25)  # Smaller font size for the delivery text
sizes_label_font = ImageFont.truetype(font_path, 20)  # Font size for the sizes label
rect_font = ImageFont.truetype(font_path, 15)  # Font size for the text inside rectangles
chip_font = ImageFont.truetype(font_path, 18)  # Font size for the text inside chips

card_path = "templates/card.png"
card_image = Image.open(card_path)
card_width, card_height = card_image.size

template_path = "templates/template.png"
template_image = Image.open(template_path)
template_width, template_height = template_image.size

today = datetime.today().strftime('%d/%m/%Y')

print("Creating final images...")
for i in tqdm(range(0, len(urls), 3), desc=f"\033[92mProcessing images\033[0m", unit="batch", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} left: {remaining}]'):
    final_image = template_image.copy()
    draw = ImageDraw.Draw(final_image)

    for j in range(3):
        index = i + j
        if index < len(urls):
            try:
                image = Image.open(output_paths[index])
                image_ratio = image.width / image.height  # Calculate the image ratio here
            except FileNotFoundError:
                print(f"Image {output_paths[index]} not found, skipping.")
                continue

            # Resize image to have a width of 450 pixels, maintaining aspect ratio
            new_width = 450
            new_height = int(new_width / image_ratio)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            # Create a new card with the image
            card_with_image = card_image.copy()
            card_draw = ImageDraw.Draw(card_with_image)

            image_x_offset = 60  # 60 pixels from the left
            image_y_offset = card_height - 70 - resized_image.height  # 70 pixels from the bottom

            card_with_image.paste(resized_image, (image_x_offset, image_y_offset), resized_image)

            # Draw the price text with the specified requirements
            price_text = f"${int(prices[index]):,}".replace(",", ".")
            price_x = 517  # Left margin within the card
            price_y = 14  # Top margin within the card
            card_draw.text((price_x, price_y), price_text, font=price_font, fill="#EE0701")

            # Draw the sizes label 13 pixels below the price text
            sizes_label_y = price_y + price_font.size + 13
            gender_text = genders[index].capitalize()
            sizes_label_text = f"Tallas disponibles para {gender_text}:"
            card_draw.text((price_x, sizes_label_y), sizes_label_text, font=sizes_label_font, fill="black")

            # Draw the chips with sizes
            chip_x_start = price_x
            chip_y_start = sizes_label_y + sizes_label_font.size + 11
            chip_size = 44  # Size of each chip (square)
            chip_gap_x, chip_gap_y = 9, 5  # Gaps between chips

            sizes_list = parse_sizes(sizes[index])
            chip_x = chip_x_start
            chip_y = chip_y_start

            for size in sizes_list:
                if size.is_integer():
                    chip_text = str(int(size))
                else:
                    chip_text = str(size)
                draw_rounded_rectangle(card_draw, (chip_x, chip_y, chip_x + chip_size, chip_y + chip_size), 5, "#D2EBFF")
                text_bbox = card_draw.textbbox((0, 0), chip_text, font=chip_font)
                text_x = chip_x + (chip_size - (text_bbox[2] - text_bbox[0])) // 2
                text_y = chip_y + (chip_size - (text_bbox[3] - text_bbox[1])) // 2
                card_draw.text((text_x, text_y), chip_text, font=chip_font, fill="black")

                chip_x += chip_size + chip_gap_x
                if chip_x + chip_size > card_width:
                    chip_x = chip_x_start
                    chip_y += chip_size + chip_gap_y

            # Draw the two rectangles with rounded corners and text inside
            rect_width, rect_height = 327, 41
            corner_radius = 5
            rect_x = card_width - 28 - rect_width  # Shifted 2 pixels to the left

            # First rectangle
            rect1_y = card_height - 28 - rect_height
            date_text = dates[index].strftime('%d/%m/%Y')
            rect1_text = f"Precios válidos hasta {'hoy' if date_text == today else 'el'} {date_text}"
            draw_rounded_rectangle(card_draw, (rect_x, rect1_y, rect_x + rect_width, rect1_y + rect_height), corner_radius, "#FD5647")
            bbox_price = card_draw.textbbox((0, 0), rect1_text, font=rect_font)
            text_width = bbox_price[2] - bbox_price[0]
            text_height = bbox_price[3] - bbox_price[1]
            text_x = rect_x + (rect_width - text_width) // 2
            text_y = rect1_y + (rect_height - text_height) // 2
            card_draw.text((text_x, text_y), rect1_text, font=rect_font, fill="white")

            # Second rectangle
            rect2_y = rect1_y - rect_height - 5
            rect2_text = f"Entrega en {delivery_times[index]} días aprox."
            draw_rounded_rectangle(card_draw, (rect_x, rect2_y, rect_x + rect_width, rect2_y + rect_height), corner_radius, "#4FAFFB")
            bbox_delivery = card_draw.textbbox((0, 0), rect2_text, font=rect_font)
            text_width = bbox_delivery[2] - bbox_delivery[0]
            text_height = bbox_delivery[3] - bbox_delivery[1]
            text_x = rect_x + (rect_width - text_width) // 2
            text_y = rect2_y + (rect_height - text_height) // 2
            card_draw.text((text_x, text_y), rect2_text, font=rect_font, fill="white")

            # Calculate the x position to center the card
            card_x_position = (template_width - card_width) // 2
            card_y_position = 50 + j * (card_height + 20)  # 50 pixels from the top for the first card

            # Paste the card onto the final image without a black border
            final_image.paste(card_with_image, (card_x_position, card_y_position), card_with_image)

    final_image_name = os.path.join(final_dir, f"final_image_{i//3 + 1}.png")
    final_image.save(final_image_name)
    tqdm.write(f"Final image saved as {final_image_name}")

# Open the final directory in the file explorer
webbrowser.open('file://' + os.path.realpath(final_dir))

print(f"All images processed and saved. You can view them in the following directory: {final_dir}")
