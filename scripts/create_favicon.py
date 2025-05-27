from PIL import Image, ImageDraw, ImageFont
import os

# Create a 32x32 image with a blue background
img = Image.new('RGB', (32, 32), color=(0, 102, 204))
d = ImageDraw.Draw(img)

# Draw a white "F" in the center
d.text((10, 5), "F", fill=(255, 255, 255))

# Save as ICO
img.save('static/favicon.ico')

print("Favicon created successfully!")
