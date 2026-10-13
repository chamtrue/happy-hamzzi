# 참고 25 스타일 2차: 실루엣 기반. 32x32, 둥근 네모 몸 + 튀어나온 볼 + 작은 눈 + ㅅ 입
from PIL import Image
import math, base64, io
N = 32
OUT = (60, 55, 60, 255); TAN = (238, 222, 192, 255); WHITE = (255, 255, 255, 255); STRIPE = (150, 140, 130, 255)
CHEEK = (250, 190, 205, 255); NOSE = (238, 140, 165, 255); EYE = (55, 50, 55, 255); PINK = (250, 190, 205, 255); PINKD = (225, 150, 175, 255)
HALO = (255, 220, 110, 255); HALOD = (220, 170, 60, 255); WING = (255, 245, 250, 255); HEART = (250, 185, 200, 255); HEARTL = (255, 215, 225, 255)
def rrect(cx, cy, hw, hh, r):
    pts = set()
    for y in range(N):
        for x in range(N):
            dx = max(abs(x + 0.5 - cx) - (hw - r), 0); dy = max(abs(y + 0.5 - cy) - (hh - r), 0)
            if math.hypot(dx, dy) <= r: pts.add((x, y))
    return pts
def circle(cx, cy, r): return {(x, y) for y in range(N) for x in range(N) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
def outline(px, fill, col):
    for x in range(N):
        for y in range(N):
            if (x, y) in fill: continue
            if any((x + dx, y + dy) in fill for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): px[x, y] = col
def mirror(pts): return set(pts) | {(31 - x, y) for x, y in pts}

def hamster(white=False, bow=False, halo=False, wings=False, heart=False, tomato=False, headphones=False, glasses=False):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    body = rrect(15.5, 17.5, 12.5, 12.5, 7.5)                       # 둥근 네모 몸 (x 3..28, y 5..30)
    ears = circle(8.5, 6.5, 3.2) | circle(23.5, 6.5, 3.2)           # 귀
    cheeks = mirror(circle(3.0, 16.5, 2.6))                           # 튀어나온 볼
    fill = body | ears
    cap = TAN if not white else WHITE
    for x, y in fill:
        px[x, y] = cap if y <= 19 else WHITE
    # 흰 주둥이 (코·입 주변)
    for x, y in circle(15.5, 18.5, 4.2):
        if (x, y) in fill: px[x, y] = WHITE
    # 귀 안쪽
    for x, y in mirror(circle(8.5, 6.5, 1.4)): px[x, y] = PINK
    # 이마 줄무늬 3개
    if not white:
        for x, y in mirror({(11, 7), (11, 8), (11, 9), (11, 10), (15, 6), (15, 7), (15, 8), (15, 9), (15, 10), (15, 11)}): px[x, y] = STRIPE
    outline(px, fill, OUT)
    # 볼 (몸 밖으로)
    for x, y in cheeks: px[x, y] = CHEEK
    outline_c = {p for p in set((x + dx, y + dy) for x, y in cheeks for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))) if p not in cheeks and p not in fill}
    for x, y in outline_c:
        if 0 <= x < N and 0 <= y < N: px[x, y] = OUT
    # 눈 (2x2 + 하이라이트), 코, ㅅ 입
    for x, y in mirror({(10, 14), (11, 14), (10, 15), (11, 15)}): px[x, y] = EYE
    for x, y in ((15, 17), (16, 17)): px[x, y] = NOSE
    for x, y in ((15, 18), (16, 18), (14, 19), (17, 19)): px[x, y] = EYE
    # 손 (배 위) / 발 (아래)
    for x, y in mirror({(10, 23), (11, 23), (12, 23), (10, 24), (11, 24), (12, 24)}): px[x, y] = PINK
    for x, y in mirror({(9, 23), (9, 24), (13, 23), (13, 24), (10, 22), (11, 22), (12, 22), (10, 25), (11, 25), (12, 25)}): px[x, y] = OUT
    for x, y in mirror({(10, 29), (11, 29), (12, 29), (10, 30), (11, 30), (12, 30)}): px[x, y] = PINK
    for x, y in mirror({(9, 29), (9, 30), (13, 29), (13, 30), (10, 31), (11, 31), (12, 31)}): px[x, y] = OUT
    # 장식
    if bow:
        for x, y in mirror({(12, 1), (13, 1), (11, 2), (12, 2), (13, 2), (14, 2), (12, 3), (13, 3), (14, 3), (13, 4)}): px[x, y] = PINK
        for x, y in mirror({(15, 2), (15, 3)}): px[x, y] = PINKD
        for x, y in mirror({(11, 1), (14, 1), (10, 2), (10, 3), (11, 4), (12, 4), (14, 4)} | {(15, 1), (16, 1)}): px[x, y] = OUT
    if halo:
        for x, y in {(x, 0) for x in range(11, 21)} | {(x, 2) for x in range(11, 21)} | {(10, 1), (21, 1)}: px[x, y] = OUT
        for x, y in {(x, 1) for x in range(11, 21)}: px[x, y] = HALO
        for x, y in ((12, 1), (13, 1)): px[x, y] = HALOD
    if wings:
        w = {(0, 14), (1, 13), (2, 13), (1, 14), (2, 14), (0, 15), (1, 15), (2, 15), (0, 16), (1, 16), (0, 17), (1, 17), (0, 18)}
        for x, y in mirror(w): px[x, y] = WING
        for x, y in mirror({(0, 12), (1, 12), (2, 12), (3, 13), (3, 14), (3, 15), (2, 16), (2, 17), (1, 18), (0, 19), (1, 19)}):
            if px[x, y][3] == 0: px[x, y] = OUT
    if heart:
        h = circle(13.0, 22.0, 2.6) | circle(18.5, 22.0, 2.6) | {(x, y) for y in range(22, 28) for x in range(10, 22) if abs(x - 15.5) <= 6 - (y - 22) * 1.1}
        for x, y in h: px[x, y] = HEART
        for x, y in ((12, 21), (11, 22)): px[x, y] = HEARTL
        for x, y in {(x + dx, y + dy) for x, y in h for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))} - h:
            if 0 <= x < N and 0 <= y < N: px[x, y] = OUT
    if tomato:
        t = circle(15.5, 3.5, 3.2)
        for x, y in t: px[x, y] = (235, 70, 70, 255)
        for x, y in ((13, 2), (14, 2)): px[x, y] = (255, 130, 130, 255)
        for x, y in ((15, 0), (16, 0), (14, 1), (17, 1)): px[x, y] = (90, 170, 90, 255)
        for x, y in {(x + dx, y + dy) for x, y in t for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))} - t:
            if 0 <= x < N and 0 <= y < N and px[x, y][3] == 0: px[x, y] = OUT
    if headphones:
        for x, y in {(x, 2) for x in range(8, 24)} | {(7, 3), (24, 3), (6, 4), (25, 4), (5, 5), (26, 5)} | {(4, y) for y in range(6, 12)} | {(27, y) for y in range(6, 12)}: px[x, y] = OUT
        for x, y in mirror({(x, y) for x in (2, 3, 4, 5) for y in range(12, 18)}): px[x, y] = (200, 200, 205, 255)
        for x, y in mirror({(3, 14), (3, 15), (4, 14), (4, 15)}): px[x, y] = (120, 120, 128, 255)
        for x, y in mirror({(1, 12), (1, 17), (2, 11), (5, 11), (2, 18), (5, 18), (6, 12), (6, 13), (6, 16), (6, 17)} | {(1, y) for y in range(13, 17)}): px[x, y] = OUT
    if glasses:
        R = (235, 70, 70, 255)
        for x, y in mirror({(7, 13), (8, 12), (9, 12), (10, 12), (11, 12), (12, 12), (13, 13), (13, 14), (13, 15), (12, 16), (11, 17), (10, 17), (9, 17), (8, 16), (7, 15), (7, 14)} | {(14, 14), (15, 14)}): px[x, y] = R
    return im

variants = [("황갈 줄무늬", dict()), ("흰색 + 리본", dict(white=True, bow=True)), ("천사", dict(halo=True, wings=True, heart=True)),
            ("흰 천사 + 리본", dict(white=True, bow=True, halo=True, wings=True, heart=True)), ("토마토 모자", dict(tomato=True)),
            ("헤드폰", dict(headphones=True)), ("빨간 안경", dict(glasses=True)), ("흰색 헤드폰 + 리본", dict(white=True, bow=True, headphones=True))]
def uri(im):
    b = io.BytesIO(); im.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
cells = "".join(f'<div class="cell"><div class="lbl">{n}</div><div class="box"><img class="big" src="{uri(hamster(**kw))}"></div><div class="tray"><img class="n" src="{uri(hamster(**kw))}"></div></div>' for n, kw in variants)
open("sketch/style25.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>스타일 25 실험 v2</title>
<style>body{{font-family:-apple-system,sans-serif;background:#f4f1ea;margin:24px}}.row{{display:flex;gap:14px;flex-wrap:wrap}}.cell{{text-align:center}}.lbl{{font-size:12px;color:#666;margin-bottom:4px}}
img{{image-rendering:pixelated;display:block}}.box{{background:#fff;border-radius:8px;padding:8px}}.big{{width:192px;height:192px}}
.tray{{background:#000;border-radius:0 0 10px 10px;padding:1px 10px;margin-top:6px;display:flex;justify-content:center;height:34px;align-items:center}}.n{{width:32px;height:32px}}</style>
<h1 style="font-size:18px">참고 이미지 25 스타일 v2 — 32×32</h1><p style="font-size:13px;color:#666">위: 6배 확대. 아래: 노치 실제 크기.</p><div class="row">{cells}</div>''')
im = Image.new("RGBA", (160 * len(variants), 160), (235, 230, 220, 255))
for i, (n, kw) in enumerate(variants):
    h = hamster(**kw).resize((160, 160), Image.NEAREST); im.paste(h, (i * 160, 0), h)
im.save("sketch/style25b.png"); print("ok")
