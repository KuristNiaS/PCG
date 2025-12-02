from PIL import Image
import os

folder ="frontend/public/images"

for filename in os.listdir(folder):
    if filename.lower().endswith(".png"):
        png_path = os.path.join(folder, filename)
        jpg_path = os.path.join(folder, filename[:-4] + ".jpg")

        try:
            img = Image.open(png_path).convert("RGB")
            img.save(jpg_path, "JPEG", quality=95)
            print(f"Converted: {png_path} -> {jpg_path}")
        except Exception as e:
            print(f"Failed: {png_path}, {e}")

print("✔ PNG → JPG conversion completed!")
