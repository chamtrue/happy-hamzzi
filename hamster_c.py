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
    fix_eyes(rgb, al, edge, n)
    sp = Image.fromarray(np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    y = (n - sp.height) // 2 if name in CENTER else n - 1 - sp.height
    out.paste(sp, ((n - sp.width) // 2, max(0, y))); _cache[key] = out; return out

def fix_eyes(rgb, al, edge, n):
    """축소로 제각각 작아진 눈을 표준 크기로 다시 그린다 (32: 2×3 + 흰 점, 22: 1×2). 감은 눈(납작한 호)은 건드리지 않는다"""
    from scipy import ndimage
    dark = al & (rgb.sum(-1) < 200) & ~edge
    lab, k = ndimage.label(dark, structure=np.ones((3, 3))); H = al.shape[0]
    cands = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sl is None: continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; size = (lab == i + 1).sum()
        if 1 <= size <= 12 and w <= 4 and h <= 4 and sl[0].start < H * 0.6: cands.append((i + 1, (sl[1].start + sl[1].stop - 1) / 2, (sl[0].start + sl[0].stop - 1) / 2, w, h))
    best = None
    for a in cands:
        for b in cands:
            dx = b[1] - a[1]
            if not (3 <= dx <= (12 if n == 32 else 8)) or abs(a[2] - b[2]) > 1.5: continue
            if a[3] > a[4] + 1 and b[3] > b[4] + 1: continue  # 둘 다 납작 = 감은 눈
            sc = abs(a[2] - b[2]) + abs(dx - (8 if n == 32 else 5)) * 0.3
            if best is None or sc < best[0]: best = (sc, a, b)
    if best is None: return
    ew, eh = (2, 3) if n == 32 else (1, 2)
    for _, cx, cy, w, h in best[1:]:
        x0, y0 = int(round(cx - (ew - 1) / 2)), int(round(cy - (eh - 1) / 2))
        box = rgb[max(0, y0 - 2):y0 + eh + 2, max(0, x0 - 2):x0 + ew + 2]; abox = al[max(0, y0 - 2):y0 + eh + 2, max(0, x0 - 2):x0 + ew + 2]
        cols = box[abox & (box.sum(-1) >= 200)]
        if len(cols):
            vals, cnt = np.unique(cols, axis=0, return_counts=True); fill = vals[cnt.argmax()]
            for i in (best[1][0], best[2][0]): rgb[lab == i] = fill
        rgb[y0:y0 + eh, x0:x0 + ew] = (40, 20, 18)
        if n == 32: rgb[y0, x0 + ew - 1] = (255, 255, 255)
        al[y0:y0 + eh, x0:x0 + ew] = True

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
        "working": wheel_frames(body + (255,), n), "focus": wheel_frames(body + (255,), n), "sprint": wheel_frames(body + (255,), n, True),  # 쳇바퀴는 A·B 렌더러 공용
        "done": bob("pompom_shock", 3), "surprised": shake("hurry"), "faint": breathe("faint", 8), "dizzy": shake("dizzy", 3),
        "sleep": breathe("sleep", 14), "night": breathe("sleep", 14), "notify": bob("wave", 4), "update": bob("partyhat", 4),
        "lunch": [(P("lunch"), 5), (sh(P("lunch"), dy=1), 5)], "leave": bob("bag", 5), "break": breathe("coffee", 12), "water": breathe("water", 12),
        "friday": bob("partyhat", 4), "birthday": bob("partyhat", 4), "battery_low": breathe("tired", 10), "cpu": shake("hot"), "hot": breathe("hot", 8),
        "meeting_soon": shake("hurry", 2), "meeting": breathe("headphones", 20), "pet": bob("hearts", 3), "pet_meeting": bob("hearts", 3),
        "grumpy": shake("grumpy", 2), "wake": [(P("wake"), 8), (sh(P("wake"), dy=-1), 6), (P("idle"), 8)],
        "snow": shake("shiver", 1), "stash": [(P("cheeks"), 12), (P("idle"), 4)],
        "music": [(P("headphones"), 5), (sh(P("headphones"), dy=1), 5)],
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
    """눈·입만 바꿔 그린다(획 1px). 원본 눈·입 자리를 주변 색으로 메우고 상태별 모양을 그림. r=2(32셀)/1(22셀)는 반폭"""
    a = np.array(im); eL, eR, mo = FACE[(kind, n)]; r = 2 if n == 32 else 1
    def center(box): x0, y0, x1, y1 = box; return (x0 + x1 - 1) // 2, (y0 + y1 - 1) // 2
    def clear(cx, cy, hw, hh):
        reg = a[cy - hh:cy + hh + 1, cx - hw:cx + hw + 1]; cols = reg[(reg[:, :, 3] > 0) & (reg[:, :, :3].sum(-1) > 100)][:, :3]
        vals, cnt = np.unique(cols, axis=0, return_counts=True); a[cy - hh:cy + hh + 1, cx - hw:cx + hw + 1, :3] = vals[cnt.argmax()]
    def dot(x, y, col=K): a[y, x, :3] = col; a[y, x, 3] = 255
    def draw_eye(box, side):
        cx, cy = center(box); clear(cx, cy, r + 1, r + 1)
        if eyes == "open":
            if r == 2: [dot(cx + dx, cy + dy) for dx in (0, 1) for dy in (-1, 0, 1)]   # 2×3 (디자인 D 원본과 같은 크기)
            else: dot(cx, cy); dot(cx, cy + 1)
        elif eyes == "closed": [dot(cx + d, cy) for d in range(-r, r + 1)]
        elif eyes == "happy": dot(cx - r, cy); dot(cx + r, cy); [dot(cx + d, cy + 1) for d in range(-r + 1, r)]  # ︶
        elif eyes == "wide":
            if r == 2: [dot(cx + dx, cy + dy, W_ if dx == 0 and dy == 0 else K) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            else: [dot(cx + dx, cy + dy) for dx in (0, 1) for dy in (0, 1)]
        elif eyes == "x": [dot(cx + d, cy + d) for d in (-1, 0, 1)]; [dot(cx + d, cy - d) for d in (-1, 1)]
        elif eyes == "flat": [dot(cx + d, cy) for d in range(-r, r + 1)]; dot(cx - side * r, cy - 2); dot(cx - side * (r - 1), cy - 1)  # 눈 + 안쪽으로 처진 눈썹
    def draw_mouth(box):
        cx, cy = center(box); clear(cx, cy, r + 1, r + 1)
        if mouth == "open":
            if r == 2: [dot(cx + dx, cy + dy, PINK if dx == 0 and dy == 1 else K) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            else: [dot(cx + dx, cy + dy) for dx in (0, 1) for dy in (0, 1)]
        elif mouth == "smile":
            if r == 2: dot(cx - 2, cy); dot(cx, cy); dot(cx + 2, cy); dot(cx - 1, cy + 1); dot(cx + 1, cy + 1)  # ω
            else: dot(cx - 1, cy); dot(cx + 1, cy); dot(cx, cy + 1)
        elif mouth == "frown": dot(cx - r, cy + 1); dot(cx + r, cy + 1); [dot(cx + d, cy) for d in range(-r + 1, r)]  # ∩
        elif mouth == "yawn":
            if r == 2: [dot(cx + dx, cy + dy, PINK if dx == 0 and 0 <= dy <= 1 else K) for dx in (-1, 0, 1) for dy in (-1, 0, 1, 2)]
            else: [dot(cx + dx, cy + dy) for dx in (0, 1) for dy in (0, 1, 2)]
    if eyes != "keep": draw_eye(eL, 1); draw_eye(eR, -1)
    if mouth != "default": draw_mouth(mo)
    return Image.fromarray(a, "RGBA")

def wheel_frames(body, n, sprint=False):  # 디자인 A·B 와 같은 쳇바퀴 렌더러에 몸 색만 넣는다
    import art
    sk = {"cap": body, "belly": (255, 255, 255, 255), "eye": art.K, "ear": art.P, "out": art.K, "name": "D", "sb": True}
    if n == 32:
        import art32; return [(art32.wheel(sk, i, sprint), 1) for i in range(8 if sprint else 4)]
    return [(art.sprint(sk, i) if sprint else art.wheel(sk, i), 1) for i in range(8 if sprint else 4)]

STATIC_BODY = {"stripe_golden": (244, 196, 110), "stripe_grey": (205, 205, 210), "stripe_choco": (160, 112, 80), "stripe_peach": (255, 210, 180), "stripe_sand": (237, 232, 203),
               "bow_cream_red": (255, 246, 220), "bow_pink": (255, 255, 255)}

def headphones(im, n):
    """D·E 정지 스프라이트에 헤드폰: 머리 윗선을 따라 1px 띠 + 눈 높이 양옆에 이어컵"""
    a = np.array(im); al = a[:, :, 3] > 0; H, W = al.shape
    ys, xs = np.where(al); x0, x1 = xs.min(), xs.max(); top = ys.min()
    eye_y = int(np.mean([FACE[(k, n)][0][1] for k in ("stripe", "bow")]))  # 눈 높이(두 디자인 평균)
    cw, ch = (2, 4) if n == 32 else (1, 3)
    for x in range(x0 + W // 6, x1 - W // 6 + 1):  # 띠: 각 열의 맨 위 픽셀 한 칸 위
        col = np.where(al[:, x])[0]
        if len(col) and col[0] - 1 >= 0: a[col[0] - 1, x] = (0, 0, 0, 255)
    for y in range(eye_y - ch // 2, eye_y - ch // 2 + ch):  # 이어컵: 실루엣 바깥쪽 가장자리에 붙여서
        row = np.where(al[y])[0]
        if len(row):
            a[y, max(0, row[0] - cw):row[0]] = (60, 60, 70, 255); a[y, row[-1] + 1:min(W, row[-1] + 1 + cw)] = (60, 60, 70, 255)
    return Image.fromarray(a, "RGBA")

def frames_static(key, n):
    file = STATIC_SKINS[key][1]; kind = file.split("_")[0]; raw = static_sprite(file, n)
    base = face(raw, kind, n, "open")  # 기본 눈을 D·E 같은 크기로 통일 (리본은 축소로 1px 이 됐었다)
    F = lambda e="open", m="default": face(raw, kind, n, e, m)
    body = STATIC_BODY[file] + (255,); wheel = wheel_frames(body, n); fast = wheel_frames(body, n, True)
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
        "working": wheel, "focus": wheel, "sprint": fast,
        "done": bob(happy, 3), "surprised": shake(F("wide", "open")), "faint": breathe(F("x", "open"), 8), "dizzy": shake(F("x", "open"), 3),
        "sleep": breathe(F("closed"), 14), "night": breathe(F("closed"), 14), "notify": bob(happy, 4), "update": bob(happy, 4),
        "lunch": [(closed_smile, 5), (sh(closed_smile, dy=1), 5)], "leave": bob(F("open", "smile"), 5), "break": breathe(closed_smile, 12), "water": breathe(closed_smile, 12),
        "friday": bob(happy, 4), "birthday": bob(happy, 4), "battery_low": breathe(F("flat", "frown"), 10), "cpu": shake(F("wide")), "hot": breathe(F("closed", "open"), 8),
        "meeting_soon": shake(F("wide", "open"), 2), "meeting": [(headphones(base, n), 20), (headphones(F("closed"), n), 2)], "pet": bob(happy, 3), "pet_meeting": bob(headphones(happy, n), 3),
        "grumpy": shake(F("flat", "frown"), 2), "wake": [(F("closed", "yawn"), 8), (sh(F("closed", "yawn"), dy=-1), 6), (base, 8)],
        "snow": shake(F("closed"), 1),
        "music": [(headphones(closed_smile, n), 5), (sh(headphones(closed_smile, n), dy=1), 5)],
    }
    return out
