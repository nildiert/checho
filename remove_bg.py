from rembg import remove
from PIL import Image

# Paths
input_path = "footlocker_image.png"
image_without_bg_path = "footlocker_image_no_bg.png"
output_path = "footlocker_image_720x1280_black.png"

# Remove background from the input image
input_image = Image.open(input_path)
output_image = remove(input_image)
output_image.save(image_without_bg_path)

# Load the image without background
image = Image.open(image_without_bg_path)

# Calculate the new height and width for the image to occupy one-third of the vertical length
new_height = 1280 // 3
new_width = int((new_height / image.height) * image.width)
resized_image = image.resize((new_width, new_height))

# Create a new image with black background
new_image = Image.new("RGBA", (720, 1280), "BLACK")

# Positions to paste the resized image three times
positions = [
    ((720 - new_width) // 2, 0),
    ((720 - new_width) // 2, new_height),
    ((720 - new_width) // 2, 2 * new_height)
]

# Paste the resized image three times onto the new image
for position in positions:
    new_image.paste(resized_image, position, resized_image)

# Save the new image
new_image.save(output_path)
print(f"New image with dimensions 720x1280 and the original image repeated three times saved as {output_path}")
