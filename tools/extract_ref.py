#!/usr/bin/env python3
"""스크린샷 속 픽셀 아트를 정확한 격자로 추출. python3 tools/extract_ref.py in.png out.png [tol]
흰 배경(테두리에 닿는 흰 영역)만 투명, 셀 크기는 셀 내부 분산이 최소인 칸 수로 추정, 비슷한 색은 tol 이내로 병합."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from collections import Counter

def extract(f, tol=15):
    im = Image.open(f).convert("RGB"); a = np.array(im).astype(int)
    white = (a > 235).all(axis=2); lab, _ = ndimage.label(white)
    border = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1]); border.discard(0)
    bg = np.isin(lab, list(border)); ys, xs = np.where(~bg); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    w, h = x1 - x0, y1 - y0
    d = (np.abs(np.diff(a[y0:y1, x0:x1], axis=1)).sum(axis=2) > 40).sum(axis=0); xs2 = np.where(d > d.max() * 0.15)[0]
    cl = []
    for x in xs2:
        if cl and x - cl[-1][-1] <= 2: cl[-1].append(x)
        else: cl.append([x])
    gaps = np.diff([np.mean(c) for c in cl]); gaps = gaps[(gaps >= 4) & (gaps <= 40)]
    cell = float(np.median(gaps)); n, m = round(w / cell), round(h / cell); cell = w / n
    px = []
    for j in range(m):
        for i in range(n):
            y, x = int(y0 + (j + 0.5) * cell), int(x0 + (i + 0.5) * cell)
            px.append((0, 0, 0, 0) if bg[y, x] else tuple(int(v) for v in a[y, x]) + (255,))
    cols = Counter([p for p in px if p[3]]).most_common(); total = sum(c for _, c in cols); reps = []
    for c, cnt in cols:
        if cnt < total * 0.004: break  # 2% 미만은 가장자리 잔상 → 가까운 주요 색으로
        if not any(sum((c[i] - r[i]) ** 2 for i in range(3)) ** 0.5 < tol for r in reps): reps.append(c)
    lut = {c: min(reps, key=lambda r: sum((c[i] - r[i]) ** 2 for i in range(3))) for c, _ in cols}
    out = Image.new("RGBA", (n, m)); out.putdata([lut[p] if p[3] else p for p in px])
    return out, [r[:3] for r in reps]

if __name__ == "__main__":
    im, reps = extract(sys.argv[1], float(sys.argv[3]) if len(sys.argv) > 3 else 15); im.save(sys.argv[2]); print(im.size, reps)
