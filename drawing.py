from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import os
import numpy as np

def draw_rounded_rectangle(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)

def parse_sizes(size_str, type_str):
    if type_str.lower() == 'talla':
        talla_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']
        sizes = size_str.split()
        return sorted(sizes, key=lambda x: talla_order.index(x) if x in talla_order else len(talla_order))
    
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

def create_final_image(i, urls, prices, delivery_times, sizes, genders, types, dates, logos, input_paths, output_paths, final_dir, font_path, card_path, template_path, mode, with_price=True):
    # Set colors based on the mode
    if mode == 'light':
        primary_color = "#EE0701"
        background_color = "#FFFFFF"
        price_color = "#EE0701"
        rect_color_1 = "#FD5647"
        rect_color_2 = "#4FAFFB"
        text_color = "black"
    else:  # dark mode
        primary_color = "#FF5733"
        background_color = "#1E1E1E"
        price_color = "#FF5733"
        rect_color_1 = "#FF5733"
        rect_color_2 = "#3498DB"
        text_color = "white"

    fonts = {
        "price": ImageFont.truetype(font_path, 48),
        "label": ImageFont.truetype(font_path, 40),
        "delivery": ImageFont.truetype(font_path, 25),
        "sizes_label": ImageFont.truetype(font_path, 20),
        "rect": ImageFont.truetype(font_path, 18),
        "chip": ImageFont.truetype(font_path, 18)
    }

    card_image = Image.open(card_path)
    card_width, card_height = card_image.size
    template_image = Image.open(template_path)
    template_width, template_height = template_image.size
    today = datetime.today().strftime('%d/%m/%Y')

    final_image = template_image.copy()
    draw = ImageDraw.Draw(final_image)

    price_y = 14
    price_x = 517

    for j in range(3):
        index = i + j
        if index >= len(urls):
            break

        try:
            image = Image.open(output_paths[index])
            image_ratio = image.width / image.height
        except FileNotFoundError:
            print(f"Image {output_paths[index]} not found, skipping.")
            continue

        # Resize and place the image
        new_width = 450
        new_height = int(new_width / image_ratio)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        if resized_image.height > 340:
            new_height = 340
            new_width = int(new_height * image_ratio)
            resized_image = resized_image.resize((new_width, new_height), Image.LANCZOS)

        card_with_image = card_image.copy()
        card_draw = ImageDraw.Draw(card_with_image)

        if types[index].lower() == 'talla':
            box_width = 356
            box_x_offset = 19
            box_y_offset = card_height - 27 - 356

            image_x_offset = box_x_offset + (box_width - resized_image.width) // 2
            image_y_offset = box_y_offset + (356 - resized_image.height) // 2
        else:
            image_x_offset = 60
            image_y_offset = card_height - 70 - resized_image.height

        card_with_image.paste(resized_image, (image_x_offset, image_y_offset), resized_image)

        # Draw the price text only if with_price is True
        if with_price:
            price_text = f"${int(prices[index]):,}".replace(",", ".")
            card_draw.text((price_x, price_y), price_text, font=fonts["price"], fill=price_color)

        # Place the logo if available
        logo_name = f"{logos[index]}.png"
        logo_path = os.path.join('templates/logos', logo_name)
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)

            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')

            logo_width = 60
            logo_ratio = logo_image.height / logo_image.width
            logo_height = int(logo_width * logo_ratio)
            logo_resized = logo_image.resize((logo_width, logo_height), Image.LANCZOS)

            logo_x = 40
            logo_y = 60

            logo_mask = logo_resized.split()[3]
            card_with_image.paste(logo_resized, (logo_x, logo_y), logo_mask)

        # Determine sizes label and chips
        sizes_label_y = price_y + fonts["price"].size + 13
        gender_text = genders[index].capitalize()
        if sizes[index].strip() and sizes[index].lower() != 'nan':
            sizes_label_text = f"Tallas disponibles para {gender_text}:"
            sizes_list = parse_sizes(sizes[index], types[index])
        else:
            sizes_label_text = ""
            sizes_list = []

        card_draw.text((price_x, sizes_label_y), sizes_label_text, font=fonts["sizes_label"], fill=text_color)

        if sizes_list:
            chip_x_start, chip_y_start = price_x, sizes_label_y + fonts["sizes_label"].size + 11
            chip_size, chip_gap_x, chip_gap_y = 44, 9, 5
            chip_x, chip_y = chip_x_start, chip_y_start

            for size in sizes_list:
                chip_text = str(int(size)) if isinstance(size, float) and size.is_integer() else str(size)
                light_color = "#D2EBFF" if mode == 'light' else "#2C3E50"
                dark_color = "#1E232B" if mode == 'light' else "#ECF0F1"
                draw_rounded_rectangle(card_draw, (chip_x, chip_y, chip_x + chip_size, chip_y + chip_size), 5, light_color)
                text_bbox = card_draw.textbbox((0, 0), chip_text, font=fonts["chip"])
                text_x = chip_x + (chip_size - (text_bbox[2] - text_bbox[0])) // 2
                text_y = chip_y + (chip_size - (text_bbox[3] - text_bbox[1])) // 2
                card_draw.text((text_x, text_y), chip_text, font=fonts["chip"], fill=text_color)

                chip_x += chip_size + chip_gap_x
                if chip_x + chip_size > card_width:
                    chip_x, chip_y = chip_x_start, chip_y + chip_size + chip_gap_y

        # Draw rectangles with rounded corners and text inside
        rect_width, rect_height, corner_radius = 327, 41, 5
        rect_x = card_width - 28 - rect_width

        rect1_y = card_height - 28 - rect_height
        date_text = dates[index].strftime('%d/%m/%Y') if not pd.isnull(dates[index]) else dates[index]
        rect1_text = f"Precios válidos hasta {'hoy' if date_text == today else 'el'} {date_text}"
        draw_rounded_rectangle(card_draw, (rect_x, rect1_y, rect_x + rect_width, rect1_y + rect_height), corner_radius, rect_color_1)
        bbox_price = card_draw.textbbox((0, 0), rect1_text, font=fonts["rect"])
        text_x = rect_x + (rect_width - (bbox_price[2] - bbox_price[0])) // 2
        text_y = rect1_y + (rect_height - (bbox_price[3] - bbox_price[1])) // 2
        card_draw.text((text_x, text_y), rect1_text, font=fonts["rect"], fill="white")

        rect2_y = rect1_y - rect_height - 5
        rect2_text = f"Entrega Inmediata." if delivery_times[index] == "inmediata" else f"Entrega en {delivery_times[index]} días aprox."
        draw_rounded_rectangle(card_draw, (rect_x, rect2_y, rect_x + rect_width, rect2_y + rect_height), corner_radius, rect_color_2)
        bbox_delivery = card_draw.textbbox((0, 0), rect2_text, font=fonts["rect"])
        text_x = rect_x + (rect_width - (bbox_delivery[2] - bbox_delivery[0])) // 2
        text_y = rect2_y + (rect_height - (bbox_delivery[3] - bbox_delivery[1])) // 2
        card_draw.text((text_x, text_y), rect2_text, font=fonts["rect"], fill="white")

        card_x_position = (template_width - card_width) // 2
        card_y_position = 50 + j * (card_height + 20)
        final_image.paste(card_with_image, (card_x_position, card_y_position), card_with_image)

    mode_dir = os.path.join(final_dir, mode, "with_prices" if with_price else "without_prices")
    os.makedirs(mode_dir, exist_ok=True)
    final_image_name = os.path.join(mode_dir, f"final_image_{i//3 + 1}.png")
    final_image.save(final_image_name)
    tqdm.write(f"{mode.capitalize()} final image saved as {final_image_name}")
