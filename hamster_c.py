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
