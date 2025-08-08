from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import pandas as pd
from tqdm import tqdm
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
        logo_folder = 'templates/logos/light'  # Select light logos
    else:  # dark mode
        primary_color = "#FF5733"
        background_color = "#1E1E1E"
        price_color = "#FF5733"
        rect_color_1 = "#FF5733"
        rect_color_2 = "#3498DB"
        text_color = "white"
        logo_folder = 'templates/logos/dark'  # Select dark logos

    fonts = {
        "price": ImageFont.truetype(font_path, 48),
        "label": ImageFont.truetype(font_path, 40),
        "delivery": ImageFont.truetype(font_path, 25),
        "sizes_label": ImageFont.truetype(font_path, 20),
        "rect": ImageFont.truetype(font_path, 24),
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
        new_width = 430
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
            image_x_offset = 30
            image_y_offset = card_height - 40 - resized_image.height

        if resized_image.mode != "RGBA":
            resized_image = resized_image.convert("RGBA")

        card_with_image.paste(resized_image, (image_x_offset, image_y_offset), resized_image)

        # Draw the price text only if with_price is True
        price_text = f"${int(prices[index]):,}".replace(",", ".")
        card_draw.text((price_x, price_y), price_text, font=fonts["price"], fill=price_color)

        # Place the logo if available
        logo_name = f"{logos[index]}.png"
        logo_path = os.path.join(logo_folder, logo_name)
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')
            logo_width = 100 if logos[index] == "gratis" else 60
            logo_ratio = logo_image.height / logo_image.width
            logo_height = int(logo_width * logo_ratio)
            logo_resized = logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            logo_x = 40
            logo_y = 60
            logo_mask = logo_resized.split()[3]
            card_with_image.paste(logo_resized, (logo_x, logo_y), logo_mask)

        sizes_label_y = price_y + fonts["price"].size + 13
        gender_text = genders[index].capitalize()

        if types[index].lower() == 'dimensiones':
            sizes_label_text = "Dimensiones:"
            sizes_list = [sizes[index]]
        elif sizes[index].strip() and sizes[index].lower() != 'nan':
            sizes_label_text = f"Tallas disponibles para {gender_text.upper()}:"
            sizes_list = parse_sizes(sizes[index], types[index])
        else:
            sizes_label_text = ""
            sizes_list = []

        card_draw.text((price_x, sizes_label_y), sizes_label_text, font=fonts["sizes_label"], fill=text_color)

        if sizes_list and types[index].lower() != 'dimensiones':
            chip_x_start, chip_y_start = price_x, sizes_label_y + fonts["sizes_label"].size + 11
            chip_size, chip_gap_x, chip_gap_y = 44, 9, 5
            chip_x, chip_y = chip_x_start, chip_y_start

            for size in sizes_list:
                chip_text = str(int(size)) if isinstance(size, float) and size.is_integer() else str(size)
                if mode == 'light':
                    chip_color = "#D2EBFF" if genders[index].lower() == 'hombre' else "#FFD2EB"
                else:
                    chip_color = "#2C3E50" if genders[index].lower() == 'hombre' else "#8B2CFF"

                draw_rounded_rectangle(card_draw, (chip_x, chip_y, chip_x + chip_size, chip_y + chip_size), 5, chip_color)
                text_bbox = card_draw.textbbox((0, 0), chip_text, font=fonts["chip"])
                text_x = chip_x + (chip_size - (text_bbox[2] - text_bbox[0])) // 2
                text_y = chip_y + (chip_size - (text_bbox[3] - text_bbox[1])) // 2
                card_draw.text((text_x, text_y), chip_text, font=fonts["chip"], fill=text_color)
                chip_x += chip_size + chip_gap_x
                if chip_x + chip_size > card_width:
                    chip_x, chip_y = chip_x_start, chip_y + chip_size + chip_gap_y

        elif types[index].lower() == 'dimensiones':
            dimensions_text = sizes_list[0]
            dimensions_y = sizes_label_y + fonts["sizes_label"].size + 11
            card_draw.text((price_x, dimensions_y), dimensions_text, font=fonts["chip"], fill=text_color)

        rect_width, rect_height, corner_radius = 327, 41, 5
        rect_x = card_width - 28 - rect_width
        rect1_y = card_height - 28 - rect_height
        if pd.isnull(dates[index]):
            date_text  = None
        else:
            date_text = dates[index].strftime('%d/%m/%Y')
        rect1_text = f"Válido hasta {'hoy' if date_text == today else 'el'} {date_text}"
        if not date_text == None:
            draw_rounded_rectangle(card_draw, (rect_x, rect1_y, rect_x + rect_width, rect1_y + rect_height), corner_radius, rect_color_1)
            bbox_price = card_draw.textbbox((0, 0), rect1_text, font=fonts["rect"])
            text_x = rect_x + (rect_width - (bbox_price[2] - bbox_price[0])) // 2
            text_y = rect1_y + (rect_height - (bbox_price[3] - bbox_price[1])) // 2
            card_draw.text((text_x, text_y), rect1_text, font=fonts["rect"], fill="white")

        rect2_y = rect1_y - rect_height - 5
        if delivery_times[index] == "inmediata":
            rect2_text = f"Entrega Inmediata."  
        elif delivery_times[index] == "navidad":
            rect2_text = f"Entrega antes de Navidad."  
        else:
            rect2_text = f"Entrega en {int(delivery_times[index])} días aprox."
        draw_rounded_rectangle(card_draw, (rect_x, rect2_y, rect_x + rect_width, rect2_y + rect_height), corner_radius, rect_color_2)
        bbox_delivery = card_draw.textbbox((0, 0), rect2_text, font=fonts["rect"])
        text_x = rect_x + (rect_width - (bbox_delivery[2] - bbox_delivery[0])) // 2
        text_y = rect2_y + (rect_height - (bbox_delivery[3] - bbox_delivery[1])) // 2
        card_draw.text((text_x, text_y), rect2_text, font=fonts["rect"], fill="white")

        card_x_position = (template_width - card_width) // 2
        card_y_position = 50 + j * (card_height + 20)
        final_image.paste(card_with_image, (card_x_position, card_y_position), card_with_image)

    # Agregar el ícono en la parte superior izquierda, separado 39 px de la izquierda y 24 px del borde superior
    icon_path = "templates/icon.png"
    if os.path.exists(icon_path):
        icon_image = Image.open(icon_path)
        if icon_image.mode != 'RGBA':
            icon_image = icon_image.convert('RGBA')
        final_image.paste(icon_image, (39, 24), icon_image)

    mode_dir = os.path.join(final_dir, mode, "with_payment_data" if with_price else "without_payment_data")
    os.makedirs(mode_dir, exist_ok=True)
    final_image_name = os.path.join(mode_dir, f"final_image_{i//3 + 1}.png")
    final_image.save(final_image_name)
    tqdm.write(f"{mode.capitalize()} final image saved as {final_image_name}")


def create_square_image(index, urls, prices, delivery_times, sizes, genders, types, dates, logos,
                        input_paths, output_paths, final_dir, font_path, square_template_path, custom_texts):
    # Cargar la plantilla cuadrada y escalarla a 737 px de ancho
    square_template = Image.open(square_template_path)
    final_width = 737
    template_ratio = square_template.height / square_template.width
    new_template_height = int(final_width * template_ratio)
    final_image = square_template.resize((final_width, new_template_height), Image.LANCZOS)
    draw = ImageDraw.Draw(final_image)

    # Cargar la imagen procesada del producto
    try:
        product_image = Image.open(output_paths[index])
    except FileNotFoundError:
        print(f"Image {output_paths[index]} not found, skipping.")
        return

    # Escalar al ancho base de 500px
    new_width = 500
    product_ratio = product_image.width / product_image.height
    new_height = int(new_width / product_ratio)
    resized_product = product_image.resize((new_width, new_height), Image.LANCZOS)

        # ————— Escalar proporcionalmente para width≤500px y height≤(rect_y–product_y) —————
    orig_w, orig_h = product_image.size
    max_w = 500
    product_y = 100       # misma Y donde pegamos la imagen
    rect_y = 415          # Y del tope del rectángulo azul
    max_h = rect_y - product_y

    scale = min(max_w / orig_w, max_h / orig_h)
    new_width  = int(orig_w * scale)
    new_height = int(orig_h * scale)
    resized_product = product_image.resize((new_width, new_height), Image.LANCZOS)
        
    product_x = (final_width - new_width) // 2
    product_y = 100
    final_image.paste(resized_product, (product_x, product_y), resized_product)

    # Definir fuentes
    font_rect         = ImageFont.truetype(font_path, 24)
    font_sizes_label  = ImageFont.truetype(font_path, 20)
    font_chip         = ImageFont.truetype(font_path, 18)
    max_price_size    = 80  # tamaño máximo de fuente para el precio

    # Definir posición y dimensiones de los rectángulos
    rect_y = 415
    rect_width = 340
    rect_height = 69

    # Calcular el texto de validación (para el rectángulo naranja)
    today = datetime.today().strftime('%d/%m/%Y')
    custom_text = custom_texts[index]
    if pd.isnull(custom_text):
        validity_text = ""
    else:
        validity_text = custom_text

    padding = 10
    orange_x = 20
    if validity_text:
        rect_color_orange = "#FD5647"
        draw_rounded_rectangle(draw, (orange_x, rect_y, orange_x + rect_width, rect_y + rect_height), 5, rect_color_orange)
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0,0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines
        available_width = rect_width - 2 * padding
        lines = wrap_text(validity_text, font_rect, available_width)
        line_heights = [
            draw.textbbox((0,0), line, font=font_rect)[3] - draw.textbbox((0,0), line, font=font_rect)[1]
            for line in lines
        ]
        total_text_height = sum(line_heights) + (len(lines) - 1) * 2
        start_y = rect_y + (rect_height - total_text_height) // 2
        for line, lh in zip(lines, line_heights):
            draw.text((orange_x + padding, start_y), line, font=font_rect, fill="white")
            start_y += lh + 2

    # Reservar espacio para chips
    sizes_y = rect_y + rect_height + 10

    # Dibujar el rectángulo azul
    blue_x = final_width - rect_width - 20
    rect_color_blue = "#4FAFFB"
    draw_rounded_rectangle(draw, (blue_x, rect_y, blue_x + rect_width, rect_y + rect_height), 5, rect_color_blue)

    # Texto de entrega
    if delivery_times[index] == "inmediata":
        delivery_text = "Entrega Inmediata."
    elif delivery_times[index] == "navidad":
        delivery_text = "Entrega antes de Navidad."
    else:
        delivery_text = f"Entrega en {int(delivery_times[index])} días aprox."
    bbox_delivery = draw.textbbox((0,0), delivery_text, font=font_rect)
    text_delivery_x = blue_x + (rect_width - (bbox_delivery[2] - bbox_delivery[0])) // 2
    text_delivery_y = rect_y + (rect_height - (bbox_delivery[3] - bbox_delivery[1])) // 2
    draw.text((text_delivery_x, text_delivery_y), delivery_text, font=font_rect, fill="white")

    # Texto "Tallas disponibles"
    if types[index].lower() == 'dimensiones':
        sizes_label_text = "Dimensiones:"
        sizes_list = [sizes[index]]
    elif sizes[index].strip() and sizes[index].lower() != 'nan':
        sizes_label_text = f"Tallas disponibles para {genders[index].capitalize()}:"
        sizes_list = parse_sizes(sizes[index], types[index])
    else:
        sizes_label_text = ""
        sizes_list = []

    if sizes_label_text:
        text_sizes_x = orange_x + 10
        draw.text((text_sizes_x, sizes_y), sizes_label_text, font=font_sizes_label, fill="black")
        bbox_sizes = draw.textbbox((0,0), sizes_label_text, font=font_sizes_label)
        sizes_y += (bbox_sizes[3] - bbox_sizes[1]) + 10

    # Dibujar chips
    if sizes_list and types[index].lower() != 'dimensiones':
        chip_size, chip_gap_x, chip_gap_y = 44, 9, 5
        chip_x, chip_y = orange_x, sizes_y
        for size in sizes_list:
            chip_text = str(int(size)) if isinstance(size, float) and size.is_integer() else str(size)
            chip_color = "#D2EBFF" if genders[index].lower() == 'hombre' else "#FFD2EB"
            if chip_x + chip_size > orange_x + rect_width:
                chip_x, chip_y = orange_x, chip_y + chip_size + chip_gap_y
            draw_rounded_rectangle(draw, (chip_x, chip_y, chip_x + chip_size, chip_y + chip_size), 5, chip_color)
            bbox_chip = draw.textbbox((0,0), chip_text, font=font_chip)
            text_chip_x = chip_x + (chip_size - (bbox_chip[2] - bbox_chip[0])) // 2
            text_chip_y = chip_y + (chip_size - (bbox_chip[3] - bbox_chip[1])) // 2
            draw.text((text_chip_x, text_chip_y), chip_text, font=font_chip, fill="black")
            chip_x += chip_size + chip_gap_x

    # ———————— dibujar precio con ajuste dinámico ————————
    price_y_blue = rect_y + rect_height + 10
    price_text = f"${int(prices[index]):,}".replace(",", ".")

    # 1. Fuente inicial al tamaño máximo
    font_size = max_price_size
    font_price = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), price_text, font=font_price)
    text_width = bbox[2] - bbox[0]

    # 2. Ajustar si excede el ancho del rectángulo azul
    if text_width > rect_width:
        scale = rect_width / text_width
        font_size = int(font_size * scale)
        font_size = max(font_size, 12)  # no bajar de 12 px
        font_price = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), price_text, font=font_price)

    # 3. Centrar y dibujar
    text_price_x = blue_x + (rect_width - (bbox[2] - bbox[0])) // 2
    draw.text((text_price_x, price_y_blue), price_text, font=font_price, fill="#EE0701")

    # Logo superior izquierdo (si aplica)
    if logos and index < len(logos) and logos[index].strip() and logos[index].lower() != 'nan':
        logo_name = f"{logos[index]}.png"
        logo_folder = 'templates/logos/light'  # o condición según modo
        logo_path = os.path.join(logo_folder, logo_name)
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path).convert("RGBA")
            logo_width = 120 if logos[index] == "gratis" else 90
            logo_ratio = logo_image.height / logo_image.width
            logo_height = int(logo_width * logo_ratio)
            logo_resized = logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            final_image.paste(logo_resized, (39, 24), logo_resized)

    # Guardar
    square_dir = os.path.join(final_dir, "cuadradas")
    os.makedirs(square_dir, exist_ok=True)
    final_image_name = os.path.join(square_dir, f"final_image_square_{index+1}.png")
    final_image.save(final_image_name)
    print(f"Square final image saved as {final_image_name}")

