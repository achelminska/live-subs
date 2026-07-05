"""
tools/make_icon.py — one-off helper (Stage 5.2 prep) to turn a plain PNG
logo into a proper Windows .exe icon.

What it does:
1. Removes the white background, making it transparent.
2. Saves a transparent PNG (source of truth for the logo).
3. Bakes a multi-resolution .ico file for PyInstaller's --icon flag.

Usage:
    python tools/make_icon.py path/to/source.png

Requires Pillow (not part of the app's runtime requirements.txt —
only needed here, once, to prepare the icon asset).
"""

import sys
from pathlib import Path

from PIL import Image

WHITE_THRESHOLD = 245  # pixels with R,G,B all >= this are treated as background
ICO_SIZES = [(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]


def remove_white_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.getdata()

    new_pixels = []
    for r, g, b, a in pixels:
        if r >= WHITE_THRESHOLD and g >= WHITE_THRESHOLD and b >= WHITE_THRESHOLD:
            new_pixels.append((r, g, b, 0))
        else:
            new_pixels.append((r, g, b, a))

    rgba.putdata(new_pixels)
    return rgba


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/make_icon.py path/to/source.png")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    project_root = Path(__file__).resolve().parent.parent

    image = Image.open(source_path)
    transparent = remove_white_background(image)

    png_out = project_root / "assets" / "icon.png"
    ico_out = project_root / "icon.ico"

    transparent.save(png_out)
    transparent.save(ico_out, sizes=ICO_SIZES)

    print(f"Saved transparent PNG: {png_out}")
    print(f"Saved Windows icon:    {ico_out}")


if __name__ == "__main__":
    main()
