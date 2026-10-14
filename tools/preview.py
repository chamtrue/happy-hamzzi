#!/usr/bin/env python3
"""폴더의 PNG 들을 격자로 확대해 한 장으로. python3 tools/preview.py dir out.png [scale] [cols]"""
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; S = int(sys.argv[3]) if len(sys.argv) > 3 else 6; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
fs = sorted(glob.glob(os.path.join(d, "*.png"))); W = 40
rows = (len(fs) + cols - 1) // cols
canvas = Image.new("RGBA", (cols * W * S, rows * (W * S + 14)), (255, 240, 245, 255)); dr = ImageDraw.Draw(canvas)
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGBA"); big = im.resize((im.width * S, im.height * S), Image.NEAREST)
    x = (i % cols) * W * S + (W - im.width) * S // 2; y = (i // cols) * (W * S + 14) + (W - im.height) * S // 2
    canvas.paste(big, (x, y), big); dr.text(((i % cols) * W * S + 4, (i // cols) * (W * S + 14) + W * S), f"{os.path.basename(f)[:-4]} {im.width}x{im.height}", fill=(90, 60, 60, 255))
canvas.save(out); print(out, len(fs))
