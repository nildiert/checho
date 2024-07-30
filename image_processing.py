from rembg import remove
from PIL import Image

def remove_background(input_path, output_path, error_log_path):
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        cropped_image = crop_image(output_image)
        cropped_image.save(output_path)
    except Exception as e:
        error_message = f"Failed to process image {input_path}. Reason: {e}\n\n"
        with open(error_log_path, "a") as log_file:
            log_file.write(error_message)
        print(error_message.strip())

def crop_image(image):
    return image.convert("RGBA").crop(image.getbbox())
