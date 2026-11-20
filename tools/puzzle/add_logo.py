"""Add the BariLifestyle logo to a 'find the detail' puzzle image.

Usage: python3 tools/puzzle/add_logo.py INPUT_IMAGE OUTPUT.jpg [corner]
corner: br (default), bl, tr, tl. Pick a corner that does not hide the puzzle detail.
The logo (brand/logo-wordmark.png) sits on a white rounded card, 22% of the image width.
Output: JPEG, max 2048 px wide, under 8 MB (Instagram limit).
"""
import sys, os
from PIL import Image, ImageDraw

def main():
    src, out = sys.argv[1], sys.argv[2]
    corner = sys.argv[3] if len(sys.argv) > 3 else "br"
    here = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(here, "..", "..", "brand", "logo-wordmark.png")
    img = Image.open(src).convert("RGBA")
    if img.width > 2048:
        img = img.resize((2048, round(img.height * 2048 / img.width)), Image.LANCZOS)
    W, H = img.size
    logo = Image.open(logo_path).convert("RGBA")
    lw = int(W * 0.22); lh = int(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    pad = int(lw * 0.06); m = int(W * 0.02)
    cw, ch = lw + 2 * pad, lh + 2 * pad
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=int(ch * 0.12), fill=(255, 255, 255, 235))
    card.alpha_composite(logo, (pad, pad))
    x = m if corner in ("bl", "tl") else W - cw - m
    y = m if corner in ("tl", "tr") else H - ch - m
    img.alpha_composite(card, (x, y))
    img.convert("RGB").save(out, quality=90)
    print("ok", out, img.size)

if __name__ == "__main__":
    main()
