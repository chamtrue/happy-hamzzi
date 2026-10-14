# 노치 모드 32px. 22px 정의(art.py·props.py)를 재사용한다:
#  - 햄스터: 32 실루엣 + 각 스킨의 22 색 규칙을 비례 샘플링, 장식·눈·입은 비례 배치(up32)
#  - 소품·장면·로고·코스튬·오버레이: 22 이미지를 up32
from PIL import Image
import json, math, os, shutil
import art, props
from art import c, K, W, P, Y, RED, REDH, Z, SEED, MG, BL, LB, is_role, mixr, role, ROLE_NAMES, VARIANTS, export_indexed

N = 32
S = 32 / 22
def up32(im):
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0)); src = im.load(); px = out.load()
    for y in range(22):
        for x in range(22):
            col = src[x, y]
            if col[3] == 0: continue
            for yy in range(round(y * S), round((y + 1) * S)):
                for xx in range(round(x * S), round((x + 1) * S)): px[xx, yy] = col
    return out
def up_pts(pts):  # 22 좌표 집합 → 32 좌표 집합
    out = set()
    for x, y in pts:
        for yy in range(round(y * S), round((y + 1) * S)):
            for xx in range(round(x * S), round((x + 1) * S)): out.add((xx, yy))
    return out
def up_layers(layers): return [(col, up_pts(pts)) for col, pts in layers]
def mirror(pts): return set(pts) | {(31 - x, y) for x, y in pts}

WIDTHS = {6: 14, 7: 18, 8: 20, 9: 22, 10: 24, 11: 26, 12: 26, 13: 28, 14: 28, 15: 28, 16: 28, 17: 28, 18: 28, 19: 28, 20: 28, 21: 28,
          22: 26, 23: 26, 24: 24, 25: 22, 26: 20, 27: 16, 28: 12}
EGG = {(x, y) for y, w in WIDTHS.items() for x in range(16 - w // 2, 16 + w // 2)} | {(x, y) for y in range(3, 7) for x in (5, 6, 7, 8, 9, 22, 23, 24, 25, 26)}
def outline(px, fill, color):
    for x in range(N):
        for y in range(N):
            if (x, y) in fill: continue
            if any((x + dx, y + dy) in fill for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): px[x, y] = color

def eye_pixels(sk, style):
    ex, ey = round(sk["anchor"][0] * S), round(sk["anchor"][1] * S)
    if style == "open": return up_pts(sk["eyes"])
    if style == "closed": return {(ex - 1 + i, ey + 3) for i in range(4)}
    if style == "happy": return {(ex + 1, ey), (ex, ey + 1), (ex + 2, ey + 1), (ex - 1, ey + 2), (ex + 3, ey + 2)}
    if style == "flat": return {(ex - 1 + i, ey + 1) for i in range(4)}
    if style == "wide": return {(x, y) for x in range(ex - 1, ex + 3) for y in range(ey - 1, ey + 3)}
    if style == "x": return {(ex - 1, ey - 1), (ex + 2, ey - 1), (ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1), (ex - 1, ey + 2), (ex + 2, ey + 2)}
def mouth_pixels(sk, mouth):
    my = round(sk["mouth_y"] * S)
    if mouth == "open": return {(x, my) for x in range(14, 18)} | {(13, my + 1), (18, my + 1), (13, my + 2), (18, my + 2)} | {(x, my + 3) for x in range(14, 18)}
    if mouth == "smile": return {(12, my), (19, my), (13, my + 1), (18, my + 1)} | {(x, my + 2) for x in range(14, 18)}
    if mouth == "frown": return {(13, my + 2), (18, my + 2), (14, my + 1), (17, my + 1), (15, my), (16, my)}
    if mouth == "yawn": return {(x, y) for x in range(13, 19) for y in range(my, my + 4)}
    return set()

DETAIL = True
K_WARM = c(0.30, 0.22, 0.18); EYE_D = c(0.24, 0.16, 0.12)
def mix(col, other, t): return tuple(int(col[i] + (other[i] - col[i]) * t) for i in range(3)) + (255,)
def pastel(col):  # 채도를 낮추고 살짝 밝게. 역할 색은 그대로(팔레트에서 처리)
    if is_role(col): return col
    r, g, b = col[:3]; m = (r + g + b) / 3
    return tuple(int((v + (m - v) * 0.12) + (255 - v) * 0.12) for v in (r, g, b)) + (255,)
PASTEL_CACHE = {}
def paint32(sk):
    p = sk["paint"]
    if not DETAIL: return lambda x, y: p(min(21, int(x / S)), min(21, int(y / S)))
    def f(x, y):
        col = p(min(21, int(x / S)), min(21, int(y / S)))
        if col not in PASTEL_CACHE: PASTEL_CACHE[col] = pastel(col)
        return PASTEL_CACHE[col]
    return f
def shade(sk, px, paint):
    """실루엣만 보고 음영을 계산한다: 아래·옆 가장자리는 어둡게, 머리 위는 밝게, 배 아래쪽은 살짝 탁하게"""
    for x, y in EGG:
        base = paint(x, y)
        edge_below = (x, y + 1) not in EGG or (x, y + 2) not in EGG
        edge_side = ((x - 1, y) not in EGG or (x + 1, y) not in EGG) and y > 13
        cap, belly = paint(10, 7), paint(16, 26)
        if edge_below or edge_side: px[x, y] = mixr(base, 1)
        elif base == belly and y >= 24: px[x, y] = mixr(base, 4)
        elif base == cap and y <= 8: px[x, y] = mixr(base, 2 if y <= 7 else 3)  # 머리 위만 아주 옅게
def sb_front32(sk, eyes="open", mouth=None, layers=(), shift=(0, 0)):
    """스타일 B 32px: 둥근 네모 몸, 튀어나온 볼, 점 눈, ㅅ 입. 평면색(음영 없음)"""
    import math as _m
    def rrect(cx, cy, hw, hh, r):
        return {(x, y) for y in range(N) for x in range(N) if _m.hypot(max(abs(x + 0.5 - cx) - (hw - r), 0), max(abs(y + 0.5 - cy) - (hh - r), 0)) <= r}
    def circle(cx, cy, r): return {(x, y) for y in range(N) for x in range(N) if _m.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
    OUT, CH, NO, EY, ST = art.SB_OUT, art.SB_CHEEK, art.SB_NOSE, art.SB_EYE, art.SB_STRIPE
    eyes, mouth = "open", None   # 시안 얼굴 고정 (사용자 결정)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    body = rrect(15.5, 17.5, 12.5, 12.5, 7.5) | circle(8.5, 6.5, 3.2) | circle(23.5, 6.5, 3.2)
    cheeks = mirror(circle(3.0, 16.5, 2.6)); cap = sk["cap"]
    for x, y in body: px[x, y] = cap if y <= 19 else W
    for x, y in circle(15.5, 18.5, 4.2):
        if (x, y) in body: px[x, y] = W
    for x, y in mirror(circle(8.5, 6.5, 1.4)): px[x, y] = P
    if sk.get("stripes"):
        for x, y in mirror({(11, 7), (11, 8), (11, 9), (11, 10), (15, 6), (15, 7), (15, 8), (15, 9), (15, 10), (15, 11)}): px[x, y] = ST
    outline(px, body, OUT)
    for x, y in cheeks: px[x, y] = CH
    for x, y in {(x + dx, y + dy) for x, y in cheeks for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cheeks - body:
        if 0 <= x < N and 0 <= y < N: px[x, y] = OUT
    ex, ey = 10, 14
    E = {"open": {(ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)}, "closed": {(ex - 1 + i, ey + 1) for i in range(4)},
         "happy": {(ex + 1, ey - 1), (ex, ey), (ex + 2, ey), (ex - 1, ey + 1), (ex + 3, ey + 1)}, "flat": {(ex - 1 + i, ey) for i in range(4)},
         "wide": {(ex - 1 + dx, ey - 1 + dy) for dx in range(4) for dy in range(4)}, "x": {(ex - 1, ey - 1), (ex + 2, ey - 1), (ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1), (ex - 1, ey + 2), (ex + 2, ey + 2)}}[eyes]
    for x, y in mirror(E): px[x, y] = EY
    if eyes == "wide":
        for x, y in mirror({(ex, ey - 1), (ex + 1, ey - 1)}): px[x, y] = W
    for x, y in ((15, 17), (16, 17)): px[x, y] = NO
    M = {None: {(15, 18), (16, 18), (14, 19), (17, 19)}, "smile": {(12, 18), (19, 18), (13, 19), (18, 19), (14, 20), (15, 20), (16, 20), (17, 20)},
         "open": {(14, 18), (17, 18), (13, 19), (18, 19), (13, 20), (18, 20), (14, 21), (15, 21), (16, 21), (17, 21), (15, 18), (16, 18)},
         "frown": {(13, 20), (18, 20), (14, 19), (17, 19), (15, 18), (16, 18)}, "yawn": {(x, y) for x in range(13, 19) for y in range(18, 22)}}[mouth]
    for x, y in M: px[x, y] = EY
    if mouth == "open":
        for x, y in {(x, y) for x in (14, 15, 16, 17) for y in (19, 20)}: px[x, y] = NO
    for x, y in mirror({(10, 23), (11, 23), (12, 23), (10, 24), (11, 24), (12, 24)}): px[x, y] = P
    for x, y in mirror({(9, 23), (9, 24), (13, 23), (13, 24), (10, 22), (11, 22), (12, 22), (10, 25), (11, 25), (12, 25)}): px[x, y] = OUT
    for x, y in mirror({(10, 29), (11, 29), (12, 29), (10, 30), (11, 30), (12, 30)}): px[x, y] = P
    for x, y in mirror({(9, 29), (9, 30), (13, 29), (13, 30), (10, 31), (11, 31), (12, 31)}): px[x, y] = OUT
    if sk.get("bow"):
        for x, y in mirror({(12, 1), (13, 1), (11, 2), (12, 2), (13, 2), (14, 2), (12, 3), (13, 3), (14, 3), (13, 4)}): px[x, y] = P
        for x, y in mirror({(15, 2), (15, 3)}): px[x, y] = mix(P, (0, 0, 0), 0.2)
        for x, y in mirror({(11, 1), (14, 1), (10, 2), (10, 3), (11, 4), (12, 4), (14, 4)} | {(15, 1), (16, 1)}): px[x, y] = OUT
    for col, pts in layers:
        for x, y in pts:
            if 0 <= x < N and 0 <= y < N: px[x, y] = col
    if shift != (0, 0): im = im.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]))
    return im

def front(sk, eyes="open", mouth=None, layers=(), shift=(0, 0), hide_deco=False):
    if sk.get("sb"): return sb_front32(sk, eyes, mouth, layers, shift)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load(); paint = paint32(sk)
    for x, y in EGG: px[x, y] = paint(x, y)
    out = K_WARM if (DETAIL and sk["out"] == K) else sk["out"]
    if DETAIL: shade(sk, px, paint)
    outline(px, EGG, out)
    if not hide_deco:
        for col, pts in sk["deco"].items():
            for x, y in up_pts({p for p in pts if not DETAIL or p[1] < 13}): px[x, y] = col   # 디테일 모드는 머리 장식(귀 안·줄무늬·머리털)만
    if DETAIL:
        pink = pastel(P); pinkD = mix(pink, (0, 0, 0), 0.22); blush = pastel(BL)
        for x, y in mirror({(6, 4), (7, 4), (6, 5), (7, 5)}): px[x, y] = pink                     # 귀 안쪽
        for x, y in mirror({(7, 5), (8, 5)}): px[x, y] = pinkD
        for x, y in mirror({(x, y) for x in range(3, 8) for y in (15, 16)}): px[x, y] = blush      # 볼터치
        dark = mixr(paint(3, 18), 5)
        for x, y in mirror({(2, 18), (3, 18), (2, 20), (3, 20)}): px[x, y] = dark                   # 수염
        for x, y in mirror({(x, y) for x in range(9, 13) for y in (21, 22)}): px[x, y] = pink       # 앞손
        for x, y in mirror({(8, 21), (8, 22), (13, 21), (13, 22)} | {(x, 20) for x in range(9, 13)} | {(x, 23) for x in range(9, 13)}): px[x, y] = out
        for x, y in mirror({(10, 22), (12, 22)}): px[x, y] = pinkD                                  # 발가락
        for x, y in mirror({(x, y) for x in range(8, 12) for y in (26, 27)}): px[x, y] = pink       # 발 (C 방식, 전 스킨 공통)
        for x, y in mirror({(7, 26), (7, 27), (12, 26), (12, 27)} | {(x, 25) for x in range(8, 12)} | {(x, 28) for x in range(8, 12)}): px[x, y] = out
        for x, y in mirror({(9, 27), (11, 27)}): px[x, y] = pinkD
    ex, ey = round(sk["anchor"][0] * S), round(sk["anchor"][1] * S)
    if eyes != "open":  # 기본 눈 자리 지우기
        for x, y in mirror({(ex + dx, ey + dy) for dx in range(-1, 4) for dy in range(-1, 4)}):
            if (x, y) in EGG and (px[x, y] in (sk["eye"], W) or (is_role(px[x, y]) and px[x, y][0] == 6)): px[x, y] = paint(x, y)
    eye_col = EYE_D if (DETAIL and sk["eye"] == K) else sk["eye"]
    if DETAIL and eyes == "open":
        for x, y in mirror({(ex + dx, ey + dy) for dx in range(2) for dy in range(3)}): px[x, y] = eye_col
        for x, y in mirror({(ex, ey)}): px[x, y] = W
    else:
        for x, y in mirror(eye_pixels(sk, eyes)): px[x, y] = eye_col
    if eyes == "wide":
        for x, y in mirror({(ex + 1, ey - 1), (ex + 2, ey - 1)}): px[x, y] = W
    if not DETAIL and eyes == "open" and sk["name"].startswith("소프트"):
        for x, y in mirror({(ex + 1, ey)}): px[x, y] = W
    my = round(sk["mouth_y"] * S)
    if DETAIL:
        pink = sk["ear"] if sk["ear"] != art.C_B else P
        for x, y in up_pts(mirror22(sk["mouth"])): px[x, y] = paint(x, y)   # 22 코·입 지우고
        if sk["nose"] != P or True:
            for x, y in ((15, my - 2), (16, my - 2)): px[x, y] = pink           # 코
            for x, y in ((15, my - 1), (16, my - 1)): px[x, y] = mix(pink, (0, 0, 0), 0.25)
        if mouth is None:
            for x, y in ((13, my), (18, my), (14, my + 1), (15, my + 1), (16, my + 1), (17, my + 1), (15, my), (16, my)): px[x, y] = EYE_D  # ω
        else:
            for x, y in mouth_pixels(sk, mouth): px[x, y] = EYE_D
            if mouth in ("open", "yawn"):
                for x, y in {(x, y) for x in range(14, 18) for y in (my + 1, my + 2)}: px[x, y] = mix(pink, (0, 0, 0), 0.1)  # 혀
                if mouth == "yawn":
                    for x, y in {(x, my + 3) for x in range(14, 18)}: px[x, y] = EYE_D
    elif mouth is None:
        for x, y in up_pts(mirror22(sk["mouth"])): px[x, y] = sk["nose"]
    else:
        for x, y in up_pts(mirror22(sk["mouth"])): px[x, y] = paint(x, y)
        for x, y in mouth_pixels(sk, mouth): px[x, y] = K if mouth in ("open", "yawn") else sk["eye"]
    for col, pts in layers:
        for x, y in pts:
            if 0 <= x < N and 0 <= y < N: px[x, y] = col
    if shift != (0, 0): im = im.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]))
    return im
def mirror22(pts): return set(pts) | {(21 - x, y) for x, y in pts}

# 32 전용 소품 (손·씨)
def seed(y): return [(K, {(15, y), (16, y + 1), (15, y + 3)}), (SEED, {(16, y), (15, y + 1), (15, y + 2), (16, y + 2), (16, y + 3)}), (W, {(16, y + 1)})]
def hands(y, sk): return [(sk["ear"] if sk["ear"] != art.C_B else P, mirror({(x, yy) for x in range(11, 14) for yy in (y, y + 1)})), (K, mirror({(10, y), (10, y + 1), (14, y), (14, y + 1)}))]
NOPAWS = []  # 32 에선 발 장식을 그대로 둔다

SIDE = [
    "...........ccc.....", "......cccccc_pcc...", "....cccccccccccccc.", "..ccccccccccccccecc", ".cccccccccccccccecc", ".cccccccccccccccccp",
    "ccccccccccccccbbbbb", "cccccccccccbbbbbbbb", "cccccccccbbbbbbbbb.", "ccccccbbbbbbbbbbbb.", ".ccbbbbbbbbbbbbbb..", "..bbbbbbbbbbbbbb...", "....bbbbbbbbbb.....",
]
def wheel(sk, frame, sprint=False):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load(); cx = cy = 16.0
    for x in range(N):
        for y in range(N):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 14.0 < d <= 15.6: px[x, y] = c(0.70, 0.70, 0.68) if (x + y) % 2 == 0 or not DETAIL else c(0.52, 0.52, 0.50)
    if DETAIL:  # 살 8개가 회전
        for i in range(8):
            a = math.radians(frame * 9 + i * 45)
            for t in range(3, 14):
                xx, yy = int(cx + t * math.cos(a)), int(cy + t * math.sin(a))
                if 0 <= xx < N and 0 <= yy < N and px[xx, yy][3] == 0: px[xx, yy] = c(0.38, 0.38, 0.36)
    for i in range(10):
        a = math.radians(frame * 9 + i * 36); px[int(cx + 13.2 * math.cos(a)), int(cy + 13.2 * math.sin(a))] = c(0.88, 0.88, 0.86)
    fill = {}
    for j, row in enumerate(SIDE):
        for i, ch in enumerate(row):
            if ch == ".": continue
            eye32 = (EYE_D if sk["eye"] == K else sk["eye"]) if DETAIL else sk["eye"]
            fill[(7 + i, 11 + j)] = {"c": sk["cap"], "b": sk["belly"], "e": eye32, "p": sk["ear"] if sk["ear"] != art.C_B else P, "_": sk["cap"]}[ch]
    legs = [{(12, 25), (13, 25), (20, 25), (21, 25)}, {(14, 25), (15, 25), (18, 25), (19, 25)}, {(13, 25), (14, 25), (19, 25), (20, 25)}, {(15, 25), (16, 25), (21, 25), (22, 25)}][frame % 4]
    for pt in legs: fill[pt] = sk["cap"]
    if DETAIL:
        for k2, v in list(fill.items()):
            if v != eye32 and not sk.get("sb"): fill[k2] = pastel(v)   # 눈은 정면과 같은 색 규칙, 나머지는 파스텔 (스타일 B 는 평면색 그대로)
        for (x, y), col in list(fill.items()):
            if (x, y + 1) not in fill or (x, y + 2) not in fill: fill[(x, y)] = mixr(col, 7)
        fill[(23, 14)] = W  # 눈 하이라이트
        for pt in ((5, 19), (6, 19), (5, 20), (6, 20)): fill[pt] = mixr(sk["belly"] if sk.get("sb") else pastel(sk["belly"]), 8)  # 똥그란 꼬리 (그림자 뒤에)
    for pt, col in fill.items(): px[pt] = col
    outline(px, set(fill), K_WARM if (DETAIL and sk["out"] == K) else sk["out"])
    for pt, col in fill.items(): px[pt] = col
    if sprint:
        for x, y in {(0, 14), (1, 14), (2, 14), (3, 14), (0, 18), (1, 18), (0, 22), (1, 22), (2, 22), (3, 22)}: px[x, y] = c(0.75, 0.75, 0.75)
        im = im.transform(im.size, Image.AFFINE, (1, 0, -(1 if frame % 2 else -1), 0, 1, 0))
    return im
def ball(sk, rot):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load(); cx, cy, r = 16.0, 17.0, 11.5; fill = {}
    for x in range(N):
        for y in range(N):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                a = (math.atan2(y + 0.5 - cy, x + 0.5 - cx) + rot) % (2 * math.pi)
                fill[(x, y)] = (sk["belly"] if 0 < a < math.pi else sk["cap"]) if sk.get("sb") else (pastel(sk["belly"]) if 0 < a < math.pi else pastel(sk["cap"]))
    for ang, kind in ((-2.2, "eye"), (-1.0, "eye"), (-1.6, "ear")):
        a = ang + rot; rr = r - 3.5 if kind == "eye" else r - 0.5
        x, y = int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a))
        for dx in (0, 1):
            if (x + dx, y) in fill: fill[(x + dx, y)] = ((EYE_D if sk["eye"] == K else sk["eye"]) if DETAIL else sk["eye"]) if kind == "eye" else (P if sk.get("sb") else pastel(sk["ear"] if sk["ear"] != art.C_B else P))
    for pt, col in fill.items(): px[pt] = col
    outline(px, set(fill), K_WARM if (DETAIL and sk["out"] == K) else sk["out"])
    return im.transform(im.size, Image.AFFINE, (1, 0, -(int(rot * 2) % 3 - 1), 0, 1, 0))
def groom(sk, up):
    y = 12 if up else 14
    pink = sk["ear"] if sk["ear"] != art.C_B else P
    return front(sk, eyes="closed", layers=[(K, mirror({(3, y), (7, y), (3, y + 1), (7, y + 1), (3, y + 2), (7, y + 2), (4, y - 1), (5, y - 1), (6, y - 1), (4, y + 3), (5, y + 3), (6, y + 3)})),
                                             (pink, mirror({(x, yy) for x in (4, 5, 6) for yy in (y, y + 1, y + 2)}))])
def cheeks(sk, level):
    base_col = paint32(sk)(3, 16); light = mixr(base_col, 6)
    r = {1: 3.2, 2: 4.6}[level]; cx, cy = 3.5, 16.5
    if sk.get("sb"): light = mix(art.SB_CHEEK, (255, 255, 255), 0.3); cx, cy = 3.0, 16.5
    puff = {(x, y) for x in range(0, 11) for y in range(10, 24) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
    rim = {(x, y) for x in range(0, 12) for y in range(9, 25) if (x, y) not in puff and any((x + dx, y + dy) in puff for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    return front(sk, eyes="closed", mouth="smile", layers=[(K, mirror(rim)), (light, mirror(puff))])

# 액세서리 32px (sketch/style25b.py 에서 가져옴)
import math as _mm
def _c32(cx, cy, r): return {(x, y) for y in range(N) for x in range(N) if _mm.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
_OUT = art.SB_OUT; _HALO = c(1.0, 0.86, 0.43); _HALOD = c(0.86, 0.67, 0.24); _WING = c(1.0, 0.96, 0.98); _HEART = c(0.98, 0.73, 0.78)
_wing = {(0, 14), (1, 13), (2, 13), (1, 14), (2, 14), (0, 15), (1, 15), (2, 15), (0, 16), (1, 16), (0, 17), (1, 17), (0, 18)}
_heart = _c32(13.0, 22.0, 2.6) | _c32(18.5, 22.0, 2.6) | {(x, y) for y in range(22, 28) for x in range(10, 22) if abs(x - 15.5) <= 6 - (y - 22) * 1.1}
_tomato = _c32(15.5, 3.5, 3.2)
def _ring(pts): return {(x + dx, y + dy) for x, y in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - pts
ACCESSORIES32 = {
    "halo": [(_OUT, {(x, 0) for x in range(11, 21)} | {(x, 2) for x in range(11, 21)} | {(10, 1), (21, 1)}), (_HALO, {(x, 1) for x in range(11, 21)}), (_HALOD, {(12, 1), (13, 1)}),
             (_OUT, mirror({(0, 12), (1, 12), (2, 12), (3, 13), (3, 14), (3, 15), (2, 16), (2, 17), (1, 18), (0, 19), (1, 19)})), (_WING, mirror(_wing))],
    "heart": [(_OUT, _ring(_heart)), (_HEART, _heart), (c(1.0, 0.84, 0.88), {(12, 21), (11, 22)})],
    "tomato": [(_OUT, _ring(_tomato) - {(15, 0), (16, 0), (14, 1), (17, 1)}), (c(0.92, 0.27, 0.27), _tomato), (c(1.0, 0.51, 0.51), {(13, 2), (14, 2)}), (c(0.35, 0.67, 0.35), {(15, 0), (16, 0), (14, 1), (17, 1)})],
    "headphones": [(_OUT, {(x, 2) for x in range(8, 24)} | {(7, 3), (24, 3), (6, 4), (25, 4), (5, 5), (26, 5)} | {(4, y) for y in range(6, 12)} | {(27, y) for y in range(6, 12)}
                     | mirror({(1, 12), (1, 17), (2, 11), (5, 11), (2, 18), (5, 18), (6, 12), (6, 13), (6, 16), (6, 17)} | {(1, y) for y in range(13, 17)})),
                   (c(0.78, 0.78, 0.80), mirror({(x, y) for x in (2, 3, 4, 5) for y in range(12, 18)})), (c(0.47, 0.47, 0.50), mirror({(3, 14), (3, 15), (4, 14), (4, 15)}))],
    "glasses": [(c(0.92, 0.27, 0.27), mirror({(7, 13), (8, 12), (9, 12), (10, 12), (11, 12), (12, 12), (13, 13), (13, 14), (13, 15), (12, 16), (11, 17), (10, 17), (9, 17), (8, 16), (7, 15), (7, 14)}) | {(14, 14), (15, 14), (16, 14), (17, 14)})],
    "bow": [(P, mirror({(12, 1), (13, 1), (11, 2), (12, 2), (13, 2), (14, 2), (12, 3), (13, 3), (14, 3), (13, 4)})), (mix(P, (0, 0, 0), 0.2), mirror({(15, 2), (15, 3)})),
            (_OUT, mirror({(11, 1), (14, 1), (10, 2), (10, 3), (11, 4), (12, 4), (14, 4)} | {(15, 1), (16, 1)}))],
}
L = up_layers  # 22 레이어 → 32
def frames(sk):
    eatA = front(sk, layers=seed(18) + hands(20, sk)); eatB = front(sk, layers=seed(16) + hands(18, sk))
    base = front(sk); blink = front(sk, eyes="closed"); chew = front(sk, eyes="closed", layers=[(BL, up_pts(mirror22({(2, 11), (3, 11), (4, 11), (2, 12), (3, 12)})))])
    shock = lambda Ls, dx: front(sk, eyes="wide", mouth="open", layers=L(Ls), shift=(dx, 0))
    happy = lambda Ls=[], dy=0: front(sk, eyes="happy", mouth="smile", layers=L(Ls), shift=(0, dy))
    sh = lambda dx=0, dy=0: (round(dx * S), round(dy * S))
    out = {
        "idle": [(eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (chew, 4), (blink, 4), (chew, 4), (blink, 4), (base, 12), (blink, 1), (base, 6)],
        "idle_groom": [(groom(sk, True), 2), (groom(sk, False), 2)] * 3 + [(front(sk, eyes="closed", mouth="smile"), 6)],
        "idle_cheeks": [(eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (cheeks(sk, 1), 5), (eatA, 3), (eatB, 3), (cheeks(sk, 2), 10), (front(sk, eyes="closed", mouth="smile"), 6)],
        "idle_roll": [(front(sk, eyes="closed"), 4)] + [(ball(sk, i * 0.785), 1) for i in range(16)] + [(front(sk, eyes="closed"), 2), (base, 4)],
        "idle_peek": [(front(sk, shift=sh(0, 6)), 3), (front(sk, shift=sh(0, 12)), 10), (front(sk, shift=sh(0, 9)), 8), (front(sk, eyes="closed", shift=sh(0, 9)), 1), (front(sk, shift=sh(0, 9)), 8), (front(sk, shift=sh(0, 12)), 6), (front(sk, shift=sh(0, 6)), 2), (base, 6)],
        "working": [(wheel(sk, i), 1) for i in range(4)], "focus": [(wheel(sk, i), 1) for i in range(4)], "sprint": [(wheel(sk, i, True), 1) for i in range(8)],
        "done": [(happy(art.POMPOM_L and [(Y, art.POMPOM_L)]), 3), (happy([(Y, art.POMPOM_U)]), 3)],
        "surprised": [(shock(art.SIREN_ON, -1), 1), (shock(art.SIREN_ON, 1), 1), (shock(art.SIREN_ON, 0), 3), (shock(art.SIREN_OFF, 0), 3)],
        "faint": [(front(sk, eyes="x", mouth="open", layers=L(art.SOUL1)), 5), (front(sk, eyes="x", mouth="open", layers=L(art.SOUL2)), 5)],
        "sleep": [(front(sk, eyes="closed", layers=L(art.ZZ1)), 8), (front(sk, eyes="closed", layers=L(art.ZZ2), shift=(0, 1)), 8)],
        "notify": [(happy(art.envelope(0)), 4), (happy(art.envelope(1), -1), 4)],
        "lunch": [(eatA, 3), (eatB, 3)], "charging": [(eatA, 3), (eatB, 3)],
        "leave": [(base, 20), (blink, 2), (happy(), 10)],
        "night": [(front(sk, eyes="closed", layers=L(art.NIGHTCAP)), 10), (front(sk, eyes="closed", mouth="yawn", layers=L(art.NIGHTCAP)), 6)],
        "friday": [(happy(art.PARTYHAT), 4), (happy(art.PARTYHAT, -1), 4)], "birthday": [(happy(art.PARTYHAT), 4), (happy(art.PARTYHAT, -1), 4)],
        "music": [(front(sk, eyes="closed", mouth="smile", layers=L(art.HEADPHONES)), 5), (front(sk, eyes="closed", mouth="smile", layers=L(art.HEADPHONES), shift=(0, 1)), 5)],
        "break": [(front(sk, eyes="closed", mouth="smile"), 12), (front(sk, eyes="closed", mouth="smile", shift=(0, 1)), 12)],
        "water": [(front(sk, eyes="closed", mouth="smile"), 12), (front(sk, eyes="closed", mouth="smile", shift=(0, 1)), 12)],
        "battery_low": [(front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT), shift=(0, 1)), 8), (front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT), shift=(0, 3)), 8)],
        "cpu": [(front(sk, eyes="wide", layers=L(art.SWEAT), shift=(-1, 0)), 1), (front(sk, eyes="wide", layers=L(art.SWEAT), shift=(1, 0)), 1)],
        "meeting_soon": [(front(sk, eyes="wide", mouth="open", shift=(-1, 0)), 1), (front(sk, eyes="wide", mouth="open", shift=(1, 0)), 1), (front(sk, eyes="wide", mouth="open"), 2)],
        "meeting": [(front(sk, layers=L(art.HEADPHONES)), 20), (front(sk, eyes="closed", layers=L(art.HEADPHONES)), 2)],
        "pet": [(happy(art.HEARTS), 3), (happy(art.HEARTS, -1), 3)],
        "pet_meeting": [(happy(art.HEADPHONES + art.HEARTS), 3), (happy(art.HEADPHONES + art.HEARTS, -1), 3)],
        "grumpy": [(front(sk, eyes="flat", mouth="frown", layers=L(art.ZZ2), shift=(1, 0)), 2), (front(sk, eyes="flat", mouth="frown", layers=L(art.ZZ2), shift=(-1, 0)), 2)],
        "dizzy": [(front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT), shift=(-1, 0)), 2), (front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT), shift=(1, 0)), 2), (front(sk, eyes="closed", layers=L(art.SWEAT)), 4)],
        "wake": [(front(sk, eyes="closed", mouth="yawn", layers=L(art.ARMS_UP)), 8), (front(sk, eyes="closed", mouth="yawn", layers=L(art.ARMS_UP), shift=(0, -1)), 6), (front(sk, eyes="closed", mouth="smile"), 6), (base, 6)],
        "stash": [(cheeks(sk, 1), 3), (cheeks(sk, 2), 8), (front(sk, eyes="closed", mouth="smile"), 4)],
        "typing": [(base, 20), (blink, 1), (front(sk, mouth="smile"), 10)],
        "rain": [(base, 20), (blink, 2), (front(sk, mouth="open"), 6)],
        "snow": [(front(sk, eyes="closed", shift=(-1, 0)), 1), (front(sk, eyes="closed", shift=(1, 0)), 1), (front(sk, eyes="closed"), 1)],
        "hot": [(front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT)), 8), (front(sk, eyes="closed", mouth="open", layers=L(art.SWEAT), shift=(0, 1)), 8)],
        "update": [(front(sk, eyes="happy", mouth="smile"), 4), (front(sk, eyes="happy", mouth="smile", shift=(0, -1)), 4)],
    }
    if sk.get("sb"):  # 시안 그대로: 손·씨·볼주머니·세수 없이 살짝 끄덕이는 대기
        calm = [(base, 30), (front(sk, shift=(0, 1)), 6)]
        for k in ("idle", "idle_groom", "idle_cheeks", "stash", "lunch", "charging", "typing"): out[k] = calm
    return out

def palette32(sk):
    if sk.get("sb"): return {"cap": sk["cap"], "belly": W, "eye": sk["eye"], "nose": sk["nose"], "out": sk["out"], "shine": sk["eye"]}  # 스타일 B 는 평면색 그대로
    eye32 = EYE_D if sk["eye"] == K else sk["eye"]
    return {"cap": pastel(sk["cap"]), "belly": pastel(sk["belly"]), "eye": eye32, "nose": eye32,
            "out": K_WARM if sk["out"] == K else sk["out"], "shine": W if sk.get("shine") else eye32}

# 봉고 키보드 32px: 외곽선 + 파스텔 몸체, 키 두 줄(3px 키·1px 틈), 스페이스바, 앞발 4×3 + 외곽선 + 반짝
KB32 = [(art.KB_OUT, {(x, 22) for x in range(4, 28)} | {(x, 28) for x in range(4, 28)} | {(4, y) for y in range(22, 29)} | {(27, y) for y in range(22, 29)}),
        (art.KB_BODY, {(x, y) for x in range(5, 27) for y in range(23, 28)}),
        (art.KB_KEY, {(x, y) for x in range(6, 26) for y in (23, 24) if (x - 6) % 4 != 3} | {(x, y) for x in list(range(6, 9)) + list(range(10, 22)) + list(range(23, 26)) for y in (26, 27)}),  # 키 두 줄, 둘째 줄 가운데는 스페이스바
        (art.KB_KEYD, {(x, 24) for x in range(6, 26) if (x - 6) % 4 != 3} | {(x, 27) for x in list(range(6, 9)) + list(range(10, 22)) + list(range(23, 26))}),  # 키 아랫면 그늘
        (art.KB_GAP, {(x, y) for x in range(9, 26, 4) for y in (23, 24)} | {(x, 25) for x in range(5, 27)} | {(x, y) for x in (9, 22) for y in (26, 27)})]       # 키 사이 틈
def paw32(x0, y0): return [(art.KB_OUT, {(x, y0 - 1) for x in range(x0, x0 + 4)} | {(x, y0 + 3) for x in range(x0, x0 + 4)} | {(x0 - 1, y) for y in range(y0, y0 + 3)} | {(x0 + 4, y) for y in range(y0, y0 + 3)}),
                            (art.PAW_P, {(x, y) for x in range(x0, x0 + 4) for y in range(y0, y0 + 3)}), (W, {(x0 + 2, y0), (x0 + 3, y0)})]
OVERLAYS32 = {"type_l": KB32 + paw32(7, 22) + paw32(20, 17), "type_r": KB32 + paw32(7, 17) + paw32(20, 22)}

if __name__ == "__main__":
    import props32
    shutil.rmtree("frames/n32", ignore_errors=True)
    meta = {"skins": {}, "templates": {}, "props": {}, "scenes": {}}
    all_templates = dict(art.TEMPLATES)
    for key, sk in art.SKINS.items():
        if not sk["template"].startswith(("pat_", "sb_")): all_templates[key] = sk
    for tname, tsk in all_templates.items():
        meta["templates"][tname] = export_indexed(frames(tsk), f"frames/n32/{tname}")
    import hamster_c
    for key, (name, _) in hamster_c.STATIC_SKINS.items():  # 디자인 D·E
        meta["templates"][key] = export_indexed(hamster_c.frames_static(key, N), f"frames/n32/{key}")
        meta["skins"][key] = {"name": name, "template": key, "pal32": {}}
    for key, (name, _, _) in hamster_c.C_SKINS.items():
        meta["templates"][key] = export_indexed(hamster_c.frames_c(key, N), f"frames/n32/{key}")
        meta["skins"][key] = {"name": name, "template": key, "pal32": {}}
    for key, sk in art.SKINS.items():
        pal = {r: list(col) for r, col in palette32(sk).items()} if sk["template"].startswith(("pat_", "sb_")) else {}
        meta["skins"][key] = {"name": sk["name"], "template": sk["template"], "pal32": pal}
    for kind, src, src32 in (("props", props.PROPS, props32.PROPS32), ("scene", props.SCENES, props32.SCENES32)):
        os.makedirs(f"frames/n32/{kind}", exist_ok=True)
        for state, fr in src.items():
            gen = props.GEN_PROPS if kind == "props" else props.GEN_SCENES
            fr = props.gen_frames(gen[state], 28, N) if state in gen else props.normalize(src32.get(state) or [(up32(im), t) for im, t in fr], 28)
            for i, (im, t) in enumerate(fr): im.save(f"frames/n32/{kind}/{state}-{i}.png")
            meta["props" if kind == "props" else "scenes"][state] = [t for _, t in fr]
    for d in ("logo", "costume", "overlay"):
        os.makedirs(f"frames/n32/{d}", exist_ok=True)
        for f in os.listdir(f"frames/{d}"): up32(Image.open(f"frames/{d}/{f}")).save(f"frames/n32/{d}/{f}")
    for name, layers in OVERLAYS32.items():  # 봉고 키보드·앞발은 32px 전용으로 다시 그림 (확대본 대체)
        im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
        for col, pts in layers:
            for x, y in pts:
                if 0 <= x < N and 0 <= y < N: px[x, y] = col
        im.save(f"frames/n32/overlay/{name}.png")
    for name, layers in ACCESSORIES32.items():
        im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
        for col, pts in layers:
            for x, y in pts:
                if 0 <= x < N and 0 <= y < N: px[x, y] = col
        im.save(f"frames/n32/costume/{name}.png")
    for name, im in props32.LOGOS32.items(): (props.gen(props.GEN_LOGOS[name], 28, N) if name in props.GEN_LOGOS else props.normalize(im, 28)).save(f"frames/n32/logo/{name}.png")
    json.dump(meta, open("frames/n32/meta.json", "w"), ensure_ascii=False)
    print("n32 templates", len(all_templates), "skins", len(meta["skins"]))
