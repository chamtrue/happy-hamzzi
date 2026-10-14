# 디자인 C: Gemini 생성 포즈(art/hamster_c_src/q/*.png, 공용 팔레트)를 22/32 셀에 맞춰 상태별 프레임으로. 색 변형은 몸·음영 두 톤만 교체.
import os
import numpy as np
from PIL import Image
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art", "hamster_c_src", "q")
BODY, SHADE, OUTLINE = (247, 231, 195), (228, 193, 155), (51, 10, 9)
C_SKINS = {  # 키 → (이름, 몸, 음영)
    "CA": ("크림 햄찌", BODY, SHADE), "CB": ("골든 햄찌", (250, 205, 120), (215, 160, 85)), "CC": ("회색 햄찌", (212, 212, 218), (165, 165, 175)),
    "CD": ("갈색 햄찌", (180, 130, 95), (135, 90, 65)), "CE": ("흰 햄찌", (252, 250, 244), (222, 214, 200)), "CF": ("주황 햄찌", (255, 185, 120), (225, 135, 80)),
}
STAND_H = 39  # 기준 서 있는 키(원본 px). 이 키가 target 에 오도록 공용 배율
CENTER = {"sleep", "roll", "faint", "wheel", "headphones"}  # 바닥 정렬 대신 가운데
_cache = {}

def pose(name, n, body, shade):
    key = (name, n, body, shade)
    if key in _cache: return _cache[key]
    im = Image.open(f"{SRC}/{name}.png").convert("RGBA"); im = im.crop(im.getbbox())
    target = n - 2; sc = min(target / STAND_H, target / im.height, n / im.width)
    a = np.array(im); pal = np.unique(a[a[:, :, 3] > 0][:, :3], axis=0)
    small = np.array(im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BOX)).astype(int)  # BOX+재양자화+윤곽 재추적이 가장 또렷 (LANCZOS·NEAREST 비교 결과)
    idx = ((small[:, :, None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1); rgb = pal[idx].astype(int); al = small[:, :, 3] > 120
    pad = np.pad(al, 1); edge = al & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]); rgb[edge] = OUTLINE  # 실루엣 경계 1px 외곽선
    for src, dst in ((BODY, body), (SHADE, shade)):
        m = (np.abs(rgb - np.array(src)).sum(-1) <= 3); rgb[m] = dst
    sp = Image.fromarray(np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    y = (n - sp.height) // 2 if name in CENTER else n - 1 - sp.height
    out.paste(sp, ((n - sp.width) // 2, max(0, y))); _cache[key] = out; return out

def spin(im, k, steps=4, inner=0.78):  # 쳇바퀴: 테두리 띠(반지름 78%~100%)만 회전, 햄스터는 그대로
    import math
    a = np.array(im); al = a[:, :, 3] > 0; ys, xs = np.where(al); x0, x1 = xs.min(), xs.max()
    R = (x1 - x0) / 2; cx = (x0 + x1) / 2; cy = ys.min() + R; ang = -2 * math.pi / steps * k / 2.4  # 한 바퀴를 천천히
    out = a.copy(); H, W = al.shape
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if inner * R <= d <= R + 0.5:
                t = math.atan2(y - cy, x - cx) - ang; sx, sy = int(round(cx + d * math.cos(t))), int(round(cy + d * math.sin(t)))
                if 0 <= sx < W and 0 <= sy < H and inner * R <= math.hypot(sx - cx, sy - cy) <= R + 0.5: out[y, x] = a[sy, sx]
    return Image.fromarray(out, "RGBA")

def sh(im, dx=0, dy=0): return im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy))

def frames_c(key, n):
    _, body, shade = C_SKINS[key]; P = lambda name: pose(name, n, body, shade)
    bob = lambda name, t=4: [(P(name), t), (sh(P(name), dy=-1), t)]          # 통통
    breathe = lambda name, t=10: [(P(name), t), (sh(P(name), dy=1), t // 2)]  # 숨쉬기
    shake = lambda name, t=2: [(sh(P(name), dx=-1), t), (sh(P(name), dx=1), t)]
    idle = [(P("idle"), 24), (sh(P("idle"), dy=1), 4)]
    out = {
        "idle": idle, "charging": idle, "rain": idle, "typing": [(P("typing"), 3), (sh(P("typing"), dy=1), 3)],
        "idle_groom": bob("groom", 3) * 3 + [(P("idle"), 8)], "idle_cheeks": [(P("idle"), 8), (P("cheeks"), 14), (P("idle"), 6)],
        "idle_roll": [(sh(P("roll"), dx=d), 2) for d in (0, 1, 2, 3, 2, 1, 0, -1, -2, -1)] + [(P("idle"), 6)],
        "idle_peek": [(sh(P("peek"), dy=d), t) for d, t in ((6, 3), (0, 12), (2, 6), (0, 6), (6, 2))] + [(P("idle"), 6)],
        "working": [(spin(P("wheel"), k), 2) for k in range(4)], "focus": [(spin(P("wheel"), k), 2) for k in range(4)], "sprint": [(spin(P("wheel"), k), 1) for k in range(4)],
        "done": bob("pompom_shock", 3), "surprised": shake("hurry"), "faint": breathe("faint", 8), "dizzy": shake("dizzy", 3),
        "sleep": breathe("sleep", 14), "night": breathe("sleep", 14), "notify": bob("wave", 4), "update": bob("partyhat", 4),
        "lunch": [(P("lunch"), 5), (sh(P("lunch"), dy=1), 5)], "leave": bob("bag", 5), "break": breathe("coffee", 12), "water": breathe("water", 12),
        "friday": bob("partyhat", 4), "birthday": bob("partyhat", 4), "battery_low": breathe("tired", 10), "cpu": shake("hot"), "hot": breathe("hot", 8),
        "meeting_soon": shake("hurry", 2), "meeting": breathe("headphones", 20), "pet": bob("hearts", 3), "pet_meeting": bob("hearts", 3),
        "grumpy": shake("grumpy", 2), "wake": [(P("wake"), 8), (sh(P("wake"), dy=-1), 6), (P("idle"), 8)],
        "snow": shake("shiver", 1), "stash": [(P("cheeks"), 12), (P("idle"), 4)],
    }
    return out

# ---------- 디자인 D(줄무늬)·E(리본): 레퍼런스 픽셀 그대로, 색만 다른 정지 스프라이트. 모든 상태가 살짝 끄덕이는 대기 ----------
D_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art", "d_src")
STATIC_SKINS = {
    "DA": ("골든 줄무늬", "stripe_golden"), "DB": ("회색 줄무늬", "stripe_grey"), "DC": ("초코 줄무늬", "stripe_choco"), "DD": ("피치 줄무늬", "stripe_peach"), "DE": ("모래 줄무늬", "stripe_sand"),
    "EA": ("크림 리본", "bow_cream_red"), "EB": ("분홍 리본", "bow_pink"),
}

def static_sprite(file, n):
    im = Image.open(f"{D_SRC}/{file}.png").convert("RGBA"); im = im.crop(im.getbbox()); target = n - 2
    sc = min(1, target / im.height, target / im.width)
    a = np.array(im); pal = np.unique(a[a[:, :, 3] > 0][:, :3], axis=0)
    small = np.array(im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BOX)).astype(int)
    idx = ((small[:, :, None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1); rgb = pal[idx].astype(int); al = small[:, :, 3] > 120
    pad = np.pad(al, 1); edge = al & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]); rgb[edge] = (0, 0, 0)
    sp = Image.fromarray(np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0)); out.paste(sp, ((n - sp.width) // 2, n - 1 - sp.height)); return out

# 얼굴 앵커(측정값): 눈 상자 [x0,y0,x1,y1) 와 입 상자. 스프라이트가 고정이라 좌표도 고정
FACE = {("stripe", 32): ((9, 12, 11, 15), (21, 12, 23, 15), (13, 17, 19, 19)), ("bow", 32): ((11, 15, 12, 16), (20, 15, 21, 16), (14, 18, 18, 20)),
        ("stripe", 22): ((6, 8, 7, 10), (14, 8, 15, 10), (9, 12, 13, 13)), ("bow", 22): ((7, 10, 8, 11), (13, 10, 14, 11), (9, 12, 12, 13))}
K, W_, PINK = (0, 0, 0), (255, 255, 255), (255, 150, 170)

def face(im, kind, n, eyes="open", mouth="default"):
    """눈·입만 바꿔 그린다. 원본 픽셀을 지우고(주변 색으로 메움) 상태별 모양을 그림. s=2(32셀)/1(22셀) 배율"""
    if eyes == "open" and mouth == "default": return im
    a = np.array(im); eL, eR, mo = FACE[(kind, n)]; s = 2 if n == 32 else 1
    def fill(box):
        x0, y0, x1, y1 = box; bg = a[y0, x0 - 1].copy() if a[y0, x0 - 1][3] else a[y1, x0].copy(); a[y0 - (s - 1):y1 + 1, x0 - 1:x1 + 1] = bg
    def dot(x, y, col=K):
        a[y:y + s, x:x + s, :3] = col; a[y:y + s, x:x + s, 3] = 255
    def draw_eye(box):
        x0, y0, x1, y1 = box; cx, cy = (x0 + x1 - s) // 2, (y0 + y1 - s) // 2
        if eyes == "closed": [dot(cx + d, cy + s // 2) for d in (-s, 0, s)]
        elif eyes == "happy": dot(cx - s, cy + s); dot(cx, cy); dot(cx + s, cy + s)
        elif eyes == "wide":
            for dx in (-s, 0, s):
                for dy in (-s, 0, s): dot(cx + dx, cy + dy, W_ if (dx == 0 and dy == 0 and s == 2) else K)
        elif eyes == "x": [dot(cx + d, cy + d) for d in (-s, 0, s)] + [dot(cx + d, cy - d) for d in (-s, s)]
        elif eyes == "flat": [dot(cx + d, cy) for d in (-s, 0, s)]; dot(cx - s, cy - s - (s - 1)); dot(cx, cy - 2 * s)  # 째림 눈썹
    def draw_mouth(box):
        x0, y0, x1, y1 = box; cx, cy = (x0 + x1 - s) // 2, y0
        if mouth == "open": [dot(cx + dx, cy + dy, PINK if (dx == 0 and dy == s) else K) for dx in (-s, 0, s) for dy in (0, s, 2 * s)]
        elif mouth == "smile": dot(cx - s, cy); dot(cx, cy + s); dot(cx + s, cy)
        elif mouth == "frown": dot(cx - s, cy + s); dot(cx, cy); dot(cx + s, cy + s)
        elif mouth == "yawn": [dot(cx + dx, cy + dy, PINK if (dx == 0 and dy in (s, 2 * s)) else K) for dx in (-s, 0, s) for dy in (0, s, 2 * s, 3 * s)]
    if eyes != "open":
        for b in (eL, eR): fill(b)
        for b in (eL, eR): draw_eye(b)
    if mouth != "default": fill(mo); draw_mouth(mo)
    return Image.fromarray(a, "RGBA")

def frames_static(key, n):
    file = STATIC_SKINS[key][1]; kind = file.split("_")[0]; base = static_sprite(file, n)
    F = lambda e="open", m="default": face(base, kind, n, e, m)
    calm = [(base, 24), (sh(base, dy=1), 4), (base, 10), (F("closed"), 2)]
    bob = lambda im, t=4: [(im, t), (sh(im, dy=-1), t)]
    breathe = lambda im, t=10: [(im, t), (sh(im, dy=1), t // 2)]
    shake = lambda im, t=2: [(sh(im, dx=-1), t), (sh(im, dx=1), t)]
    happy = F("happy", "smile"); closed_smile = F("closed", "smile")
    out = {
        "idle": calm, "charging": calm, "rain": calm, "typing": [(base, 3), (sh(base, dy=1), 3)], "stash": [(F("open", "smile"), 12), (base, 4)],
        "idle_groom": bob(closed_smile, 3) * 3 + [(base, 8)], "idle_cheeks": [(base, 8), (F("closed"), 14), (base, 6)],
        "idle_roll": shake(F("closed"), 1) * 5 + [(base, 6)],
        "idle_peek": [(sh(base, dy=d), t) for d, t in ((n // 2, 3), (n // 3, 12), (n // 2, 2))] + [(base, 6)],
        "working": [(sh(base, dy=-1), 1), (base, 1)], "focus": [(sh(base, dy=-1), 1), (base, 1)], "sprint": [(sh(F("wide"), dy=-1), 1), (F("wide"), 1)],  # 제자리 뛰기
        "done": bob(happy, 3), "surprised": shake(F("wide", "open")), "faint": breathe(F("x", "open"), 8), "dizzy": shake(F("x", "open"), 3),
        "sleep": breathe(F("closed"), 14), "night": breathe(F("closed"), 14), "notify": bob(happy, 4), "update": bob(happy, 4),
        "lunch": [(closed_smile, 5), (sh(closed_smile, dy=1), 5)], "leave": bob(F("open", "smile"), 5), "break": breathe(closed_smile, 12), "water": breathe(closed_smile, 12),
        "friday": bob(happy, 4), "birthday": bob(happy, 4), "battery_low": breathe(F("flat", "frown"), 10), "cpu": shake(F("wide")), "hot": breathe(F("closed", "open"), 8),
        "meeting_soon": shake(F("wide", "open"), 2), "meeting": [(base, 20), (F("closed"), 2)], "pet": bob(happy, 3), "pet_meeting": bob(happy, 3),
        "grumpy": shake(F("flat", "frown"), 2), "wake": [(F("closed", "yawn"), 8), (sh(F("closed", "yawn"), dy=-1), 6), (base, 8)],
        "snow": shake(F("closed"), 1),
    }
    return out
