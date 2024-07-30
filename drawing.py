from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from tqdm import tqdm
import pandas as pd

import os

def draw_rounded_rectangle(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)

def parse_sizes(size_str, type_str):
    if type_str == 'talla':
        return sorted(size_str.split())
    size_list = []
    for part in size_str.split():
        if '...' in part:
            start, end = map(float, part.split('...'))
            size_list.extend([start + 0.5 * i for i in range(int((end - start) * 2) + 1)])
        elif '..' in part:
            start, end = map(float, part.split('..'))
            size_list.extend(range(int(start), int(end) + 1))
        else:
            try:
                size_list.append(float(part))
            except ValueError:
                size_list.append(part)  # Handle non-numeric sizes
    return sorted(set(size_list), key=lambda x: (isinstance(x, str), x))

def create_final_image(i, urls, prices, delivery_times, sizes, genders, types, dates, input_paths, output_paths, final_dir, font_path, card_path, template_path):
    fonts = {
        "price": ImageFont.truetype(font_path, 48),
        "label": ImageFont.truetype(font_path, 40),
        "delivery": ImageFont.truetype(font_path, 25),
        "sizes_label": ImageFont.truetype(font_path, 20),
        "rect": ImageFont.truetype(font_path, 15),
        "chip": ImageFont.truetype(font_path, 18)
    }

    card_image = Image.open(card_path)
    card_width, card_height = card_image.size
    template_image = Image.open(template_path)
    template_width, template_height = template_image.size
    today = datetime.today().strftime('%d/%m/%Y')

    final_image = template_image.copy()
    draw = ImageDraw.Draw(final_image)

    for j in range(3):
        index = i + j
        if index >= len(urls):
            break

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

        # Ensure the image height does not exceed 275 pixels
        if resized_image.height > 340:
            new_height = 340
            new_width = int(new_height * image_ratio)
            resized_image = resized_image.resize((new_width, new_height), Image.LANCZOS)

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
        card_draw.text((price_x, price_y), price_text, font=fonts["price"], fill="#EE0701")

        # Draw the sizes label 13 pixels below the price text
        sizes_label_y = price_y + fonts["price"].size + 13
        gender_text = genders[index].capitalize()
        sizes_label_text = f"Tallas disponibles para {gender_text}:"
        card_draw.text((price_x, sizes_label_y), sizes_label_text, font=fonts["sizes_label"], fill="black")

        # Draw the chips with sizes
        chip_x_start, chip_y_start = price_x, sizes_label_y + fonts["sizes_label"].size + 11
        chip_size, chip_gap_x, chip_gap_y = 44, 9, 5
        sizes_list = parse_sizes(sizes[index], types[index])
        chip_x, chip_y = chip_x_start, chip_y_start

        for size in sizes_list:
            chip_text = str(size)  # Directly convert size to string as it might be float or str
            draw_rounded_rectangle(card_draw, (chip_x, chip_y, chip_x + chip_size, chip_y + chip_size), 5, "#D2EBFF")
            text_bbox = card_draw.textbbox((0, 0), chip_text, font=fonts["chip"])
            text_x = chip_x + (chip_size - (text_bbox[2] - text_bbox[0])) // 2
            text_y = chip_y + (chip_size - (text_bbox[3] - text_bbox[1])) // 2
            card_draw.text((text_x, text_y), chip_text, font=fonts["chip"], fill="black")

            chip_x += chip_size + chip_gap_x
            if chip_x + chip_size > card_width:
                chip_x, chip_y = chip_x_start, chip_y + chip_size + chip_gap_y

        # Draw the two rectangles with rounded corners and text inside
        rect_width, rect_height, corner_radius = 327, 41, 5
        rect_x = card_width - 28 - rect_width  # Shifted 2 pixels to the left

        # First rectangle
        rect1_y = card_height - 28 - rect_height
        date_text = dates[index].strftime('%d/%m/%Y') if not pd.isnull(dates[index]) else 'Fecha no disponible'
        rect1_text = f"Precios válidos hasta {'hoy' if date_text == today else 'el'} {date_text}"
        draw_rounded_rectangle(card_draw, (rect_x, rect1_y, rect_x + rect_width, rect1_y + rect_height), corner_radius, "#FD5647")
        bbox_price = card_draw.textbbox((0, 0), rect1_text, font=fonts["rect"])
        text_x = rect_x + (rect_width - (bbox_price[2] - bbox_price[0])) // 2
        text_y = rect1_y + (rect_height - (bbox_price[3] - bbox_price[1])) // 2
        card_draw.text((text_x, text_y), rect1_text, font=fonts["rect"], fill="white")

        # Second rectangle
        rect2_y = rect1_y - rect_height - 5
        rect2_text = f"Entrega en {delivery_times[index]} días aprox."
        draw_rounded_rectangle(card_draw, (rect_x, rect2_y, rect_x + rect_width, rect2_y + rect_height), corner_radius, "#4FAFFB")
        bbox_delivery = card_draw.textbbox((0, 0), rect2_text, font=fonts["rect"])
        text_x = rect_x + (rect_width - (bbox_delivery[2] - bbox_delivery[0])) // 2
        text_y = rect2_y + (rect_height - (bbox_delivery[3] - bbox_delivery[1])) // 2
        card_draw.text((text_x, text_y), rect2_text, font=fonts["rect"], fill="white")

        # Calculate the x position to center the card
        card_x_position = (template_width - card_width) // 2
        card_y_position = 50 + j * (card_height + 20)  # 50 pixels from the top for the first card
        # Paste the card onto the final image without a black border
        final_image.paste(card_with_image, (card_x_position, card_y_position), card_with_image)

    final_image_name = os.path.join(final_dir, f"final_image_{i//3 + 1}.png")
    final_image.save(final_image_name)
    tqdm.write(f"Final image saved as {final_image_name}")