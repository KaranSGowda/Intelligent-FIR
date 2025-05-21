from PIL import Image, ImageDraw, ImageFont

# Create a 64x64 image with a blue background
img = Image.new('RGB', (64, 64), color=(0, 102, 204))
d = ImageDraw.Draw(img)

# Draw a white circle in the center
d.ellipse((8, 8, 56, 56), fill=(255, 255, 255))

# Draw a blue "FIR" in the center
try:
    # Try to use a font if available
    font = ImageFont.truetype("arial.ttf", 20)
    d.text((16, 20), "FIR", fill=(0, 102, 204), font=font)
except:
    # Fallback to default font
    d.text((16, 20), "FIR", fill=(0, 102, 204))

# Create smaller versions for multi-resolution favicon
img16 = img.resize((16, 16))
img32 = img.resize((32, 32))

# Save as ICO with multiple sizes
img.save('static/favicon.ico')

# Also save as PNG for modern browsers
img.save('static/favicon.png')

print("Favicon created successfully!")
