import requests
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process images for promotions.')
parser.add_argument('--skip-download', action='store_true', help='Skip downloading and processing images')
args = parser.parse_args()

# Load the Excel file
file_path = 'PRUEBAS PROMOS Fotos.xlsx'
df = pd.read_excel(file_path, header=0)

# Extract the relevant columns
urls = df['Link Foto'].dropna().tolist()
prices = df['Precio de venta'].dropna().astype(float).tolist()
delivery_times = df['TIEMPO DE ENTREGA'].dropna().astype(str).tolist()

# Ensure the lists are of the same length
urls = urls[:len(prices)]
delivery_times = delivery_times[:len(prices)]

def download_image(url, path):
    print(f"Downloading image from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as file:
            file.write(response.content)
        print(f"Image downloaded and saved as {path}")
    else:
        print(f"Failed to download image from {url}. Status code: {response.status_code}")

def remove_background(input_path, output_path):
    print(f"Removing background from {input_path}...")
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    cropped_image = crop_image(output_image)
    cropped_image.save(output_path)
    print(f"Image with removed background and no margins saved as {output_path}")

def crop_image(image):
    # Ensure image is in RGBA format
    image = image.convert("RGBA")
    bbox = image.getbbox()
    return image.crop(bbox)

# Paths for saving images
input_paths = [f"image_{i}.png" for i in range(len(urls))]
output_paths = [f"image_no_bg_{i}.png" for i in range(len(urls))]

# Download and process images if flag is not set
if not args.skip_download:
    for i, url in enumerate(urls):
        download_image(url, input_paths[i])
        remove_background(input_paths[i], output_paths[i])

# Create final images with prices and delivery times
font_path = "fonts/label_font.ttf"
price_font = ImageFont.truetype(font_path, 50)  # Increased font size for price
label_font = ImageFont.truetype(font_path, 20)

for i in range(0, len(urls), 3):
    final_image_width = 720
    final_image_height = 420 * 3  # Adjusted for 3 images
    final_image = Image.new("RGBA", (final_image_width, final_image_height), "BLACK")

    margin_top = 20  # Margin from the top
    image_height = 420  # Height of each image area

    for j in range(3):
        index = i + j
        if index < len(urls):
            print(f"Processing image {index}...")
            image = Image.open(output_paths[index])
            image_ratio = image.width / image.height
            if image.width > final_image_width:
                new_width = final_image_width
                new_height = int(new_width / image_ratio)
                resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
            else:
                resized_image = image

            # Center the resized image horizontally and place it at the bottom of each section
            x_offset = (final_image_width - resized_image.width) // 2
            y_offset = final_image_height - (image_height * (j + 1)) + (image_height - resized_image.height) - margin_top
            final_image.paste(resized_image, (x_offset, y_offset), resized_image)
            
            draw = ImageDraw.Draw(final_image)

            # Draw the price text
            price_text = f"${int(prices[index]):,}".replace(",", ".")
            draw.text((10, y_offset + 10), price_text, font=price_font, fill="white")

            # Draw the delivery text on the right with a rounded rectangle
            delivery_text = delivery_times[index]
            bbox = draw.textbbox((0, 0), delivery_text, font=label_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            rectangle_x0 = final_image_width - text_width - 30  # Padding from the right
            rectangle_y0 = y_offset + 10
            rectangle_x1 = rectangle_x0 + text_width + 20
            rectangle_y1 = rectangle_y0 + text_height + 20
            draw.rounded_rectangle([(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)], radius=15, fill="red")
            draw.text((rectangle_x0 + 10, rectangle_y0 + 10), delivery_text, font=label_font, fill="black")

    final_image_name = f"final_image_{i//3 + 1}.png"
    final_image.save(final_image_name)
    print(f"Final image saved as {final_image_name}")

print("All images processed and saved.")
