import requests
from rembg import remove
from PIL import Image

# URLs of the images
urls = [
    "https://images.footlocker.com/is/image/EBFL2/Z4178010_a1?wid=572&hei=572&fmt=png-alpha",
    "https://images.footlocker.com/is/image/EBFL2/Q8992101_a1?wid=581&hei=581&fmt=png-alpha",
    "https://images.footlocker.com/is/image/EBFL2/24453004_a1?wid=581&hei=581&fmt=png-alpha"
]

# Paths for saving images
input_paths = ["footlocker_image1.png", "footlocker_image2.png", "footlocker_image3.png"]
output_paths = ["footlocker_image1_no_bg.png", "footlocker_image2_no_bg.png", "footlocker_image3_no_bg.png"]

def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as file:
            file.write(response.content)
        print(f"Image downloaded and saved as {path}")
    else:
        print(f"Failed to download image from {url}. Status code: {response.status_code}")

def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    cropped_image = crop_image(output_image)
    cropped_image.save(output_path)
    print(f"Image with removed background and no margins saved as {output_path}")

def crop_image(image):
    # Ensure image is in RGBA format
    image = image.convert("RGBA")
    
    # Get the bounding box
    bbox = image.getbbox()
    return image.crop(bbox)

# Download images
for url, input_path in zip(urls, input_paths):
    download_image(url, input_path)

# Remove background and save images without margins
for input_path, output_path in zip(input_paths, output_paths):
    remove_background(input_path, output_path)

# Create the final image with a black background
final_image_width = 720
final_image_height = 420 * len(output_paths)  # 1260 if there are 3 images
final_image = Image.new("RGBA", (final_image_width, final_image_height), "BLACK")

# Resize and paste the images onto the final image
for i, output_path in enumerate(output_paths):
    image = Image.open(output_path)
    resized_image = image.resize((final_image_width, 420))
    final_image.paste(resized_image, (0, 420 * i), resized_image)

# Save the final image
final_image.save("final_image.png")
print("Final image saved as final_image.png")
