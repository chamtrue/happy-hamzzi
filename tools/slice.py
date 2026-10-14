#!/usr/bin/env python3
"""Gemini 가 그린 픽셀 아이콘 시트를 잘라 진짜 픽셀 격자로 내린다.
  python3 tools/slice.py sheet.png outdir name1 name2 ...   (왼→오, 위→아래 순)
  각 아이콘: 흰 배경에서 연결 요소로 분리 → 격자 칸 크기·위상 추정 → 칸 중심 샘플링 → RGBA(배경 투명) PNG 저장."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

def cell_size(a):  # 수평 색 변화 열의 간격 최빈값
    d = (np.abs(np.diff(a, axis=1)).sum(axis=2) > 40); s = d.sum(axis=0); xs = np.where(s > s.max() * 0.15)[0]
    cl = []
    for x in xs:
        if cl and x - cl[-1][-1] <= 2: cl[-1].append(x)
        else: cl.append([x])
    g = np.round(np.diff([np.mean(c) for c in cl])).astype(int); g = g[g >= 4]
    return int(np.bincount(g).argmax())

def phase(a, cs, axis):  # 색 변화가 격자선에 몰리는 오프셋
    d = (np.abs(np.diff(a, axis=axis)).sum(axis=2) > 40).sum(axis=1 - axis)
    best = max(range(cs), key=lambda p: d[p::cs].sum()); return (best + 1) % cs

def downsample(tile, cs):
    a = np.array(tile).astype(int); h, w = a.shape[:2]
    px, py = phase(a, cs, 1), phase(a, cs, 0)
    xs = list(range(px + cs // 2, w, cs)); ys = list(range(py + cs // 2, h, cs))
    out = np.array([[a[y, x] for x in xs] for y in ys]).astype(np.uint8)
    return Image.fromarray(out, "RGB")

def transparent(im):  # 테두리에서 닿는 흰 영역만 투명하게 (안쪽 흰 하이라이트는 유지)
    a = np.array(im.convert("RGB")).astype(int); white = (a > 235).all(axis=2)
    lab, n = ndimage.label(white); border = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1]); border.discard(0)
    alpha = np.where(np.isin(lab, list(border)), 0, 255).astype(np.uint8)
    out = np.dstack([a.astype(np.uint8), alpha]); return Image.fromarray(out, "RGBA")

def main(sheet, outdir, names, cell=None, grid=None):
    im = Image.open(sheet).convert("RGB"); a = np.array(im).astype(int)
    cs = cell or cell_size(a); print("cell", cs)
    if grid:  # 등간격 격자 모드: 조각난 아이콘(색종이·점)도 한 칸으로
        gc, gr = grid; cw, ch = im.width / gc, im.height / gr
        boxes = [(int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch)) for r in range(gr) for c in range(gc)]
        os.makedirs(outdir, exist_ok=True)
        for b, name in zip(boxes, names):
            small = transparent(downsample(im.crop(b), cs)); bb = small.getbbox(); small = small.crop(bb) if bb else small
            small.save(os.path.join(outdir, name + ".png")); print(name, small.size)
        return
    fg = ~(a > 235).all(axis=2); fg = ndimage.binary_dilation(fg, iterations=cs)  # 작은 조각(반짝이)도 한 아이콘으로
    lab, n = ndimage.label(fg); objs = ndimage.find_objects(lab)
    boxes = [(s[1].start, s[0].start, s[1].stop, s[0].stop) for s in objs]
    boxes = [b for b in boxes if (b[2] - b[0]) > cs * 6 and (b[3] - b[1]) > cs * 6]
    rows = []  # 행으로 묶어 왼→오, 위→아래 정렬
    for b in sorted(boxes, key=lambda b: b[1]):
        if rows and abs(rows[-1][0][1] - b[1]) < (b[3] - b[1]) * 0.6: rows[-1].append(b)
        else: rows.append([b])
    boxes = [b for r in rows for b in sorted(r, key=lambda b: b[0])]
    print(len(boxes), "icons found,", len(names), "names")
    os.makedirs(outdir, exist_ok=True)
    for b, name in zip(boxes, names):
        x0, y0, x1, y1 = b; pad = cs
        tile = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
        small = transparent(downsample(tile, cs))
        bb = small.getbbox(); small = small.crop(bb) if bb else small
        small.save(os.path.join(outdir, name + ".png")); print(name, small.size)

if __name__ == "__main__":
    args = sys.argv[1:]; cell = None; grid = None
    while args[0].startswith("--"):
        if args[0] == "--cell": cell = int(args[1])
        if args[0] == "--grid": grid = tuple(int(v) for v in args[1].split("x"))
        args = args[2:]
    main(args[0], args[1], args[2:], cell, grid)
