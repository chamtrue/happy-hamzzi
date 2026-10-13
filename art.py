# 햄스터 아트 파이프라인. 스킨 5종 × 상태 7종의 프레임을 frames/<skin>/<state>-<n>.png 로 내보내고
# samples.html 로 미리보기를 만든다. Swift 앱은 이 PNG만 읽는다.
from PIL import Image
import base64, io, json, math, os, shutil

N = 22
def c(r, g, b): return (int(r*255), int(g*255), int(b*255), 255)
K = c(0.16, 0.15, 0.15); W = (255,255,255,255); P = c(0.97, 0.63, 0.69); BL = c(0.99, 0.78, 0.80)
Y = c(1.0, 0.78, 0.24); RED = c(0.92, 0.24, 0.20); REDH = c(1.0, 0.55, 0.45); Z = c(0.45, 0.55, 0.85)
SEED = c(0.30, 0.24, 0.20); LB = c(0.59, 0.78, 0.94); MG = c(0.88, 0.12, 0.35); NAVY = c(0.35, 0.42, 0.75); GRAY = c(0.62, 0.62, 0.60); GRAYD = c(0.88, 0.88, 0.86)
def mirror(pts): return set(pts) | {(21 - x, y) for x, y in pts}

# ---------- 정면 실루엣(달걀형 + 귀) ----------
WIDTHS = {4:10, 5:14, 6:16, 7:18, 8:18, 9:20, 10:20, 11:20, 12:20, 13:20, 14:20, 15:20, 16:18, 17:16, 18:14, 19:10}
EGG = {(x, y) for y, w in WIDTHS.items() for x in range(11 - w // 2, 11 + w // 2)} | {(x, y) for y in (2, 3) for x in (4, 5, 6, 15, 16, 17)}

def outline(px, fill, color):
    for x in range(N):
        for y in range(N):
            if (x, y) in fill: continue
            if any((x+dx, y+dy) in fill for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))): px[x, y] = color

# ---------- 스킨 ----------
def two_tone(cap, belly, white):  # white: {y: range} 모자/배 경계
    def paint(x, y):
        if y in white: return belly if x in white[y] else cap
        return belly if y > max(white) else cap
    return paint

O_A = c(0.93, 0.56, 0.22); T_B = c(0.82, 0.62, 0.42); C_B = c(0.99, 0.94, 0.85); O_C = c(0.96, 0.78, 0.48)
M_C = c(0.45, 0.18, 0.18); C_D = c(0.96, 0.88, 0.72); G_D = c(0.38, 0.35, 0.35); P_E = c(0.98, 0.85, 0.65); L_E = c(1.0, 0.95, 0.84)

def paint_B(x, y):
    cream = {8: range(6, 16), 9: range(4, 18), 10: range(3, 19), 17: range(4, 18), 18: range(5, 17), 19: range(6, 16)}
    if y in cream: return C_B if x in cream[y] else T_B
    if 11 <= y <= 16: return C_B if 3 <= x <= 18 else T_B
    return T_B
def paint_D(x, y):
    if 9 <= y <= 11 and 8 <= x <= 13: return W
    if y >= 13 and 3 <= x <= 18: return W
    return C_D
def paint_E(x, y):
    if 9 <= y <= 10 and 8 <= x <= 13: return L_E
    if 12 <= y <= 18 and 4 <= x <= 17: return L_E
    return P_E

# eyes: 왼쪽 눈 픽셀(오른쪽은 미러). anchor: (ex, ey) 표정 교체 기준점. deco: 고정 장식
SKINS = {
 "B": dict(name="소프트 황갈", out=c(0.62, 0.42, 0.28), cap=T_B, belly=C_B, ear=C_B, eye=c(0.35, 0.20, 0.12), nose=c(0.95, 0.55, 0.45),
           paint=paint_B, eyes={(6, 8), (7, 9), (6, 9)}, anchor=(6, 8), mouth=set(), mouth_y=11,
           deco={C_B: mirror({(5, 3)}), W: mirror({(7, 8)}), c(0.95, 0.55, 0.45): mirror({(10, 10)}),
                 BL: mirror({(3, 11), (4, 11), (3, 12)}), P: mirror({(6, 18), (7, 18), (6, 19), (7, 19)})}),
 "C": dict(name="자주선 + 손자국", out=M_C, cap=O_C, belly=W, ear=P, eye=M_C, nose=M_C,
           paint=two_tone(O_C, W, {10: range(7, 15), 11: range(4, 18), 12: range(2, 20)}),
           eyes={(7, 7), (7, 8)}, anchor=(7, 7), mouth={(10, 9), (9, 10), (10, 10)}, mouth_y=10,
           deco={P: mirror({(5, 2), (5, 3), (4, 3), (5, 17), (6, 17), (7, 17), (5, 18), (6, 18), (7, 18)}),
                 M_C: mirror({(6, 13), (8, 13), (7, 14), (5, 16), (6, 16), (7, 16), (4, 17), (8, 17), (8, 18)})}),
 "D": dict(name="이마 줄무늬", out=K, cap=C_D, belly=W, ear=P, eye=K, nose=P,
           paint=paint_D, eyes={(6, 8), (6, 9)}, anchor=(6, 8), mouth={(9, 10), (10, 11)}, mouth_y=10,
           deco={P: mirror({(5, 3), (10, 9), (5, 17), (6, 17), (7, 17), (5, 18), (6, 18), (7, 18)}),
                 G_D: mirror({(7, 4), (7, 5), (10, 4), (10, 5), (10, 6)}), BL: mirror({(2, 10), (3, 10), (4, 10), (2, 11), (3, 11), (4, 11)})}),
 "E": dict(name="복숭아 + 머리털", out=K, cap=P_E, belly=L_E, ear=P, eye=K, nose=P,
           paint=paint_E, eyes={(6, 8), (7, 8)}, anchor=(6, 8), mouth=set(), mouth_y=10,
           deco={P: mirror({(5, 3), (10, 9), (6, 18), (7, 18), (6, 19), (7, 19)}), BL: mirror({(2, 9), (3, 9), (4, 9), (2, 10), (3, 10), (4, 10)}),
                 K: {(8, 2), (10, 1), (10, 2), (12, 2)}}),
}

# ---------- 역할 센티널: 템플릿 렌더링용 가짜 색. (역할, 변형, 0, 254) ----------
ROLE_NAMES = ["cap", "belly", "eye", "nose", "out", "shine"]
def role(r, v=0): return (r, v, 0, 254)
def is_role(col): return len(col) == 4 and col[3] == 254
# 변형(음영) 공식 — 앱 팔레트도 같은 공식으로 계산한다
VARIANTS = {0: lambda c_: c_, 1: lambda c_: mixc(c_, (0, 0, 0), 0.14), 2: lambda c_: mixc(c_, (255, 255, 255), 0.10), 3: lambda c_: mixc(c_, (255, 255, 255), 0.05),
            4: lambda c_: mixc(c_, (120, 110, 100), 0.07), 5: lambda c_: mixc(c_, (0, 0, 0), 0.30), 6: lambda c_: tuple(min(255, int(v + (255 - v) * 0.45)) for v in c_[:3]) + (255,),
            7: lambda c_: mixc(c_, (0, 0, 0), 0.16), 8: lambda c_: mixc(c_, (255, 255, 255), 0.3)}
def mixc(col, other, t): return tuple(int(col[i] + (other[i] - col[i]) * t) for i in range(3)) + (255,)
def mixr(col, variant):
    """역할 색이면 변형 번호만 바꾸고, 실제 색이면 공식을 적용한다"""
    if is_role(col): return (col[0], variant, 0, 254)
    return VARIANTS[variant](col)

# ---------- 골든 햄스터 모프 스킨 (색·패턴 값으로 생성, A 스타일 2톤 템플릿) ----------
A_WHITE = {9: range(8, 14), 10: range(5, 17), 11: range(3, 19), 12: range(2, 20), 13: range(2, 20)}
A_FEET = {P: mirror({(6, 17), (7, 17), (8, 17), (5, 18), (6, 18), (7, 18), (8, 18)}),
          c(0.85, 0.40, 0.50): mirror({(6, 16), (7, 16), (8, 16), (5, 17), (9, 17), (4, 18), (9, 18)})}
def darken(col, f=0.45): return tuple(int(v * f) for v in col[:3]) + (255,)
def morph(name, cap, belly=None, eye=K, pattern="solid", second=None, shine=False, out=None, shine_col=None):
    belly = belly or c(0.98, 0.95, 0.90)
    out = out or (c(0.40, 0.32, 0.26) if sum(cap[:3]) > 600 else darken(cap))
    base = two_tone(cap, belly, A_WHITE)
    def paint(x, y):
        col = base(x, y)
        if pattern == "banded":  # 몸통 가운데 흰 띠, 아래는 다시 모자색
            if 11 <= y <= 14: return belly
            if y >= 15: return cap
            return col
        if pattern == "spot":  # 흰 바탕에 모자색 반점 (왼눈 주변, 오른쪽 엉덩이)
            if (x - 6) ** 2 + (y - 7) ** 2 <= 12 or (x - 17) ** 2 + (y - 16) ** 2 <= 8 or (x - 15) ** 2 + (y - 4) ** 2 <= 5: return cap
            return belly
        if pattern == "polywhite":  # 머리 위만 모자색
            return cap if y <= 6 else belly
        if pattern == "roan":  # 흰 점이 섞인 털
            return belly if col == cap and (x * 7 + y * 13) % 5 == 0 else col
        if pattern == "tortie":  # 모자색·검정·흰 얼룩
            h = ((x // 4) * 3 + (y // 4) * 5) % 7
            return second if h in (1, 4) and col == cap else (belly if h == 6 and col == cap else col)
        return col
    deco = dict(A_FEET); deco[P] = deco[P] | mirror({(5, 3)})
    if shine_col is not None: deco[shine_col] = mirror({(6, 7)})
    elif shine: deco[W] = mirror({(6, 7)})
    return dict(name=name, out=out, cap=cap, belly=belly, ear=P, eye=eye, nose=eye if eye != K else K, paint=paint,
                eyes={(6, 7), (6, 8)}, anchor=(6, 7), mouth={(10, 9), (9, 10), (10, 11)}, mouth_y=10, deco=deco,
                pattern=pattern, shine=shine, template="pat_" + pattern)
RED_EYE = c(0.60, 0.18, 0.16); GOLD = c(0.85, 0.52, 0.22)
MORPHS = [  # (키, 이름, 모자색, 배색, 눈색, 패턴, 보조색, 하이라이트)
    ("F", "골든", GOLD, None, K, "solid", None, False),
    ("G", "엄브러스", c(0.60, 0.44, 0.30), c(0.85, 0.80, 0.72), K, "solid", None, False),
    ("H", "시나몬", c(0.93, 0.64, 0.33), None, RED_EYE, "solid", None, False),
    ("I", "러스트", c(0.80, 0.42, 0.18), c(0.95, 0.88, 0.78), K, "solid", None, False),
    ("J", "블론드", c(0.95, 0.82, 0.58), None, K, "solid", None, False),
    ("K", "샴페인", c(0.90, 0.78, 0.60), None, RED_EYE, "solid", None, False),
    ("L", "다크 그레이", c(0.36, 0.36, 0.38), c(0.86, 0.86, 0.88), K, "solid", None, True),
    ("M", "라이트 그레이", c(0.62, 0.58, 0.55), c(0.92, 0.90, 0.88), K, "solid", None, False),
    ("N", "실버 그레이", c(0.73, 0.73, 0.75), None, K, "solid", None, False),
    ("O", "도브", c(0.68, 0.62, 0.56), c(0.90, 0.87, 0.84), RED_EYE, "solid", None, False),
    ("P", "초콜릿", c(0.40, 0.25, 0.18), c(0.58, 0.42, 0.33), K, "solid", None, True),
    ("Q", "옐로 초콜릿", c(0.62, 0.48, 0.30), c(0.82, 0.72, 0.56), K, "solid", None, False),
    ("R", "크림", c(0.96, 0.85, 0.60), None, K, "solid", None, False),
    ("S", "레드아이 크림", c(0.96, 0.85, 0.60), None, RED_EYE, "solid", None, False),
    ("T", "옐로 블랙", c(0.70, 0.55, 0.32), c(0.90, 0.82, 0.65), K, "solid", None, False),
    ("U", "아이보리", c(0.95, 0.92, 0.82), None, K, "solid", None, False),
    ("V", "블랙아이 화이트", W, W, K, "solid", None, False),
    ("W", "레드아이 화이트", W, W, RED_EYE, "solid", None, False),
    ("X", "블랙", c(0.20, 0.20, 0.22), c(0.34, 0.34, 0.36), c(0.02, 0.02, 0.02), "solid", None, True),
    ("Y", "블루", c(0.55, 0.57, 0.65), c(0.86, 0.87, 0.91), K, "solid", None, False),
    ("Z", "레드아이 블루", c(0.55, 0.57, 0.65), c(0.86, 0.87, 0.91), RED_EYE, "solid", None, False),
    ("ZA", "라벤더", c(0.72, 0.65, 0.68), c(0.93, 0.89, 0.91), RED_EYE, "solid", None, False),
    ("ZB", "세이블", c(0.28, 0.22, 0.18), c(0.56, 0.46, 0.38), K, "solid", None, True),
    ("ZC", "초콜릿 세이블", c(0.42, 0.28, 0.20), c(0.64, 0.52, 0.42), K, "solid", None, True),
    ("ZD", "밴디드", GOLD, None, K, "banded", None, False),
    ("ZE", "도미넌트 스팟", GOLD, None, K, "spot", None, False),
    ("ZF", "폴리화이트", GOLD, None, K, "polywhite", None, False),
    ("ZG", "로안", GOLD, None, K, "roan", None, False),
    ("ZH", "토터셸", GOLD, None, K, "tortie", c(0.15, 0.13, 0.12), False),
]
SKINS["A"] = morph("클래식 2톤", O_A, W, K, "solid", out=K)
for key, name, cap, belly, eye, pattern, second, shine in MORPHS:
    SKINS[key] = morph(name, cap, belly, eye, pattern, second, shine, out=c(0.55, 0.55, 0.55) if cap == W else None)
SKINS = {"A": SKINS["A"], **{k: v for k, v in SKINS.items() if k != "A"}}
# 패턴별 역할 템플릿 스킨 (센티널 색으로 그린다)
TEMPLATES = {}
for pat in ("solid", "banded", "spot", "polywhite", "roan", "tortie"):
    TEMPLATES["pat_" + pat] = morph("tpl", role(1), role(2), role(3), pat, second=c(0.15, 0.13, 0.12), shine=True, out=role(5), shine_col=role(6))
    TEMPLATES["pat_" + pat]["nose"] = role(4)

def palette22(sk):
    """스킨의 22px 팔레트: 역할 → 색 (변형 0만 쓴다)"""
    return {"cap": sk["cap"], "belly": sk["belly"], "eye": sk["eye"], "nose": sk["nose"], "out": sk["out"], "shine": W if sk.get("shine") else sk["eye"]}

# ---------- 스타일 B (참고 이미지 25: 둥근 네모 몸, 튀어나온 볼, 점 눈, ㅅ 입) 22px ----------
import math as _m
def _rrect(cx, cy, hw, hh, r, n=22):
    pts = set()
    for y in range(n):
        for x in range(n):
            dx = max(abs(x + 0.5 - cx) - (hw - r), 0); dy = max(abs(y + 0.5 - cy) - (hh - r), 0)
            if _m.hypot(dx, dy) <= r: pts.add((x, y))
    return pts
def _circle(cx, cy, r, n=22): return {(x, y) for y in range(n) for x in range(n) if _m.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
SB_OUT = c(0.24, 0.22, 0.24); SB_TAN = c(0.93, 0.87, 0.75); SB_STRIPE = c(0.59, 0.55, 0.51); SB_CHEEK = c(0.98, 0.75, 0.80); SB_NOSE = c(0.93, 0.55, 0.65); SB_EYE = c(0.22, 0.20, 0.22)
SB_BODY22 = _rrect(10.5, 12.0, 8.5, 8.5, 5.0) | _circle(5.5, 4.5, 2.2) | _circle(15.5, 4.5, 2.2)
SB_CHEEKS22 = mirror(_circle(1.6, 11.5, 1.8))
def sb_front22(sk, eyes="open", mouth=None, layers=(), shift=(0, 0)):
    eyes, mouth = "open", None   # 시안 얼굴 고정 (사용자 결정)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    cap = sk["cap"]
    for x, y in SB_BODY22: px[x, y] = cap if y <= 13 else W
    for x, y in _circle(10.5, 13.0, 2.8):
        if (x, y) in SB_BODY22: px[x, y] = W
    for x, y in mirror(_circle(5.5, 4.5, 0.9)): px[x, y] = P
    if sk.get("stripes"):
        for x, y in {(7, 5), (7, 6), (7, 7), (10, 4), (10, 5), (10, 6), (10, 7), (13, 5), (13, 6), (13, 7)}: px[x, y] = SB_STRIPE
    outline(px, SB_BODY22, SB_OUT)
    for x, y in SB_CHEEKS22: px[x, y] = SB_CHEEK
    for x, y in {(x + dx, y + dy) for x, y in SB_CHEEKS22 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - SB_CHEEKS22 - SB_BODY22:
        if 0 <= x < N and 0 <= y < N: px[x, y] = SB_OUT
    ex, ey = 7, 9
    E = {"open": {(ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)}, "closed": {(ex - 1, ey + 1), (ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey + 1)},
         "happy": {(ex + 1, ey), (ex, ey + 1), (ex + 2, ey + 1)}, "flat": {(ex, ey), (ex + 1, ey)},
         "wide": {(ex - 1 + dx, ey - 1 + dy) for dx in range(3) for dy in range(3)}, "x": {(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)}}[eyes]
    for x, y in mirror(E): px[x, y] = SB_EYE
    if eyes == "wide":
        for x, y in mirror({(ex, ey - 1)}): px[x, y] = W
    for x, y in ((10, 12), (11, 12)): px[x, y] = SB_NOSE
    M = {None: {(10, 13), (11, 13), (9, 14), (12, 14)}, "smile": {(8, 13), (13, 13), (9, 14), (10, 14), (11, 14), (12, 14)},
         "open": {(9, 13), (12, 13), (9, 14), (12, 14), (10, 15), (11, 15), (10, 12 + 1), (11, 12 + 1)}, "frown": {(9, 14), (12, 14), (10, 13), (11, 13)},
         "yawn": {(x, y) for x in range(9, 13) for y in (13, 14, 15)}}[mouth]
    for x, y in M: px[x, y] = SB_EYE
    if mouth == "open":
        for x, y in ((10, 14), (11, 14)): px[x, y] = SB_NOSE
    for x, y in mirror({(6, 16), (7, 16), (6, 17), (7, 17)}): px[x, y] = P
    for x, y in mirror({(5, 16), (5, 17), (8, 16), (8, 17), (6, 15), (7, 15), (6, 18), (7, 18)}): px[x, y] = SB_OUT
    for x, y in mirror({(7, 20), (8, 20), (7, 21), (8, 21)}): px[x, y] = P
    for x, y in mirror({(6, 20), (6, 21), (9, 20), (9, 21)}): px[x, y] = SB_OUT
    if sk.get("bow"):
        for x, y in mirror({(8, 0), (9, 0), (8, 1), (9, 1), (10, 1)}): px[x, y] = P
        for x, y in mirror({(7, 0), (7, 1), (8, 2), (9, 2)} | {(10, 0)}): px[x, y] = SB_OUT
    for col, pts in layers:
        for x, y in pts:
            if 0 <= x < N and 0 <= y < N: px[x, y] = col
    if shift != (0, 0): im = im.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]))
    return im
def sb_skin(name, cap, stripes=False, bow=False, template=None):
    return dict(name=name, out=SB_OUT, cap=cap, belly=W, ear=P, eye=SB_EYE, nose=SB_NOSE, paint=lambda x, y, cap=cap: cap if y <= 13 else W,
                eyes={(7, 9), (8, 9), (7, 10), (8, 10)}, anchor=(7, 9), mouth=set(), mouth_y=13, deco={}, sb=True, stripes=stripes, bow=bow,
                template=template or ("sb_stripe" if stripes else "sb_bow"))
SB_COLORS = [  # (키, 이름, 몸 색, 줄무늬) — 리본은 줄무늬 없음
    ("SB", "줄무늬 햄찌", SB_TAN, True), ("SD", "줄무늬 · 골든", c(0.95, 0.72, 0.42), True), ("SE", "줄무늬 · 그레이", c(0.80, 0.80, 0.82), True),
    ("SF", "줄무늬 · 초코", c(0.72, 0.55, 0.42), True), ("SG", "줄무늬 · 크림", c(0.98, 0.93, 0.80), True),
    ("SC", "리본 햄찌", W, False), ("SH", "리본 · 핑크", c(1.0, 0.86, 0.90), False), ("SI", "리본 · 라벤더", c(0.90, 0.84, 0.96), False),
    ("SJ", "리본 · 민트", c(0.82, 0.95, 0.90), False), ("SK", "리본 · 레몬", c(1.0, 0.97, 0.80), False),
]
for key, name, cap, stripes in SB_COLORS: SKINS[key] = sb_skin(name, cap, stripes=stripes, bow=not stripes)
TEMPLATES["sb_stripe"] = sb_skin("tpl", role(1), stripes=True, template="sb_stripe")
TEMPLATES["sb_bow"] = sb_skin("tpl", role(1), bow=True, template="sb_bow")

for _k, _v in SKINS.items(): _v.setdefault("template", _k)   # 수제 스킨은 자기 이름이 템플릿

# ---------- 표정 ----------
def eye_pixels(sk, style):
    ex, ey = sk["anchor"]
    if style == "open": return sk["eyes"]
    if style == "closed": return {(ex, ey + 1), (ex + 1, ey + 1)}
    if style == "happy": return {(ex + 1, ey), (ex, ey + 1), (ex + 2, ey + 1)}
    if style == "wide": return {(ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)}
    if style == "flat": return {(ex, ey), (ex + 1, ey)}
    if style == "x": return {(ex, ey), (ex + 2, ey), (ex + 1, ey + 1), (ex, ey + 2), (ex + 2, ey + 2)}

def front(sk, eyes="open", mouth=None, layers=(), shift=(0, 0), hide_deco=False):
    """layers: [(color, pixel set)] 순서대로 덮어쓴다. 외곽선은 실루엣 기준 자동."""
    if sk.get("sb"): return sb_front22(sk, eyes, mouth, layers, shift)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    paint = sk["paint"]
    for x, y in EGG: px[x, y] = paint(x, y)
    outline(px, EGG, sk["out"])
    ex, ey = sk["anchor"]
    if not hide_deco:
        for col, pts in sk["deco"].items():
            for x, y in pts: px[x, y] = col
    # 기본 눈 자리 지우기(표정 교체용) — 눈 주변 3x3 을 바탕색으로
    if eyes != "open":
        for x, y in mirror({(ex + dx, ey + dy) for dx in range(3) for dy in range(3)}):
            if (x, y) in EGG and (px[x, y] in (sk["eye"], W) or (is_role(px[x, y]) and px[x, y][0] == 6)): px[x, y] = paint(x, y)
    for x, y in mirror(eye_pixels(sk, eyes)): px[x, y] = sk["eye"]
    if eyes == "wide":
        for x, y in mirror({(ex + 1, ey)}): px[x, y] = W
    if eyes == "open" and sk["name"].startswith("소프트"):
        for x, y in mirror({(7, 8)}): px[x, y] = W
    if mouth is None:
        for x, y in mirror(sk["mouth"]): px[x, y] = sk["nose"]
    else:
        my = sk["mouth_y"]
        for x, y in mirror(sk["mouth"]): px[x, y] = paint(x, y)
        if mouth == "open":
            for x, y in {(10, my + 1), (11, my + 1), (10, my + 2), (11, my + 2)}: px[x, y] = K
        if mouth == "frown":
            for x, y in {(9, my + 1), (12, my + 1), (10, my), (11, my)}: px[x, y] = sk["eye"]
        if mouth == "yawn":
            for x, y in {(9, my), (10, my), (11, my), (12, my), (9, my + 1), (10, my + 1), (11, my + 1), (12, my + 1), (10, my + 2), (11, my + 2)}: px[x, y] = K
        if mouth == "smile":
            for x, y in {(9, my), (12, my), (10, my + 1), (11, my + 1)}: px[x, y] = sk["eye"]
    for col, pts in layers:
        for x, y in pts:
            if 0 <= x < N and 0 <= y < N: px[x, y] = col
    if shift != (0, 0):
        im = im.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]))
    return im

# 소품
def seed(y): return [(K, {(10, y), (11, y + 2)}), (SEED, {(11, y), (10, y + 1), (10, y + 2)}), (W, {(11, y + 1)})]
def hands(y, sk): return [(sk["ear"] if sk["ear"] != C_B else P, mirror({(8, y), (9, y)}))]
POMPOM_L = mirror({(0, 10), (1, 10), (0, 11), (1, 11), (2, 11), (0, 12), (1, 12), (2, 12), (0, 13), (1, 13)})
POMPOM_U = {(x, y - 2) for x, y in POMPOM_L}
SIREN_ON = [(K, {(10, 0), (11, 0), (9, 1), (12, 1), (9, 2), (12, 2)} | {(x, 3) for x in range(8, 14)}), (RED, {(11, 1), (10, 2), (11, 2)}), (REDH, {(10, 1)})]
SIREN_OFF = [(K, {(10, 0), (11, 0), (9, 1), (12, 1), (9, 2), (12, 2)} | {(x, 3) for x in range(8, 14)}), (c(0.5, 0.15, 0.12), {(10, 1), (11, 1), (10, 2), (11, 2)})]
ZZ1 = [(Z, {(19, 0), (20, 0), (21, 0), (20, 1), (19, 2), (20, 2), (21, 2)})]
ZZ2 = [(Z, {(20, 0), (19, 1), (20, 2)})]
SOUL1 = [(W, {(20, 0), (21, 0), (19, 1), (20, 1), (21, 1), (19, 2), (21, 2)}), (K, {(20, 1)})]
SOUL2 = [(W, {(19, 0), (20, 0), (18, 1), (19, 1), (20, 1), (18, 2), (20, 2)}), (K, {(19, 1)})]
# 편지(알림): 머리 위에 흰 봉투가 둥실
def envelope(dy):
    pts = lambda S: {(x, y + dy) for x, y in S}
    return [(K, pts({(x, 0) for x in range(6, 16)} | {(x, 4) for x in range(6, 16)} | {(6, y) for y in (1, 2, 3)} | {(15, y) for y in (1, 2, 3)})),
            (W, pts({(x, y) for x in range(7, 15) for y in (1, 2, 3)})),
            (K, pts({(7, 1), (14, 1), (8, 2), (13, 2), (9, 3), (12, 3)})), (P, pts({(10, 3), (11, 3)}))]

# 오버레이(머리 위 장식)
NIGHTCAP = [(K, {(x, 3) for x in range(4, 18)} | {(13, 0), (14, 0), (10, 1), (15, 1), (7, 2), (16, 2)}),
            (NAVY, {(11, 1), (12, 1), (13, 1), (14, 1)} | {(x, 2) for x in range(8, 16)}),
            (W, {(x, 3) for x in range(5, 17)} | {(15, 0), (16, 0), (16, 1)})]
PARTYHAT = [(MG, {(10, 0), (11, 0)}), (Y, {(x, 1) for x in range(9, 13)} | {(x, 2) for x in range(8, 14)} | {(x, 3) for x in range(7, 15)}),
            (MG, {(10, 2), (11, 2), (8, 3), (13, 3)})]
HEADPHONES = [(K, {(x, 1) for x in range(7, 15)} | {(5, 2), (6, 2), (15, 2), (16, 2), (4, 3), (17, 3), (3, 4), (18, 4), (2, 5), (19, 5)}
                 | {(x, y) for x in (0, 1, 2) for y in range(6, 11)} | {(x, y) for x in (19, 20, 21) for y in range(6, 11)}),
              (NAVY, {(1, 7), (1, 8), (1, 9), (20, 7), (20, 8), (20, 9)})]
ARMS_UP = [(K, mirror({(0, 7), (0, 8), (3, 7), (3, 8), (1, 6), (2, 6), (1, 9), (2, 9)})), (P, mirror({(1, 7), (2, 7), (1, 8), (2, 8)}))]
SPEEDLINES = [(c(0.75, 0.75, 0.75), {(0, 10), (1, 10), (2, 10), (0, 13), (1, 13), (0, 16), (1, 16), (2, 16)})]
SWEAT = [(LB, {(19, 4), (18, 5), (19, 5), (20, 5), (18, 6), (19, 6), (20, 6), (19, 7)}), (W, {(20, 5)})]
HEARTS = [(MG, {(1, 11), (3, 11), (0, 12), (1, 12), (2, 12), (3, 12), (4, 12), (1, 13), (2, 13), (3, 13), (2, 14),
                (17, 13), (19, 13), (16, 14), (17, 14), (18, 14), (19, 14), (20, 14), (17, 15), (18, 15), (19, 15), (18, 16)})]

# 계절 코스튬 (앱이 햄스터 위에 실시간으로 얹는 모자 레이어)
SANTA = [(K, {(x, 3) for x in range(5, 17)} | {(8, 0), (9, 0), (7, 1), (10, 1), (6, 2), (11, 2), (12, 2), (13, 1), (14, 1), (12, 0)}),
         (RED, {(8, 1), (9, 1)} | {(x, 2) for x in range(7, 11)}),
         (W, {(x, 3) for x in range(6, 16)} | {(13, 0), (14, 0), (15, 1), (13, 2), (14, 2)} )]
PUMPKINHAT = [(K, {(x, 3) for x in range(5, 17)} | {(8, 1), (13, 1), (7, 2), (14, 2), (10, 0), (11, 0)}),
              (c(0.30, 0.60, 0.25), {(10, 1), (11, 1)}),
              (c(0.93, 0.50, 0.15), {(9, 1), (12, 1)} | {(x, 2) for x in range(8, 14)} | {(x, 3) for x in range(6, 16)}),
              (c(0.75, 0.35, 0.10), {(10, 2), (11, 3), (8, 3), (13, 3)})]
HOGEON = [(K, {(x, 0) for x in range(9, 13)} | {(x, 1) for x in range(7, 15)} | {(x, 3) for x in range(6, 16)}),
          (Y, {(x, 2) for x in range(6, 16)}), (RED, {(10, 2), (11, 2)})]
# 여름: 튜브 + 파도. 몸통 아래쪽을 덮는다
TUBE_RING = {(0, 13), (1, 13), (20, 13), (21, 13)} | {(x, y) for y in (14, 15) for x in (0, 1, 2, 19, 20, 21)} | {(x, 16) for x in (0, 1, 2, 3, 18, 19, 20, 21)} \
    | {(x, 17) for x in range(1, 21)} | {(x, 18) for x in range(2, 20)}
TUBE_STRIPE = {(x, y) for y in (17, 18) for x in (5, 6, 10, 11, 15, 16)} | {(0, 14), (21, 14)}
TUBE_EDGE = {(x, 19) for x in range(3, 19)} | {(0, 12), (21, 12), (1, 12), (20, 12), (2, 13), (19, 13), (3, 15), (18, 15), (4, 16), (17, 16)}
WAVES = {(x, y) for y in (20, 21) for x in range(22)} | {(x, 19) for x in (0, 1, 2, 19, 20, 21)}
SUMMER = [(c(0.55, 0.78, 0.95), WAVES), (W, {(2, 20), (8, 20), (14, 20), (20, 20)}),
          (K, TUBE_EDGE), (c(0.98, 0.55, 0.20), TUBE_RING), (W, TUBE_STRIPE)]
# 봉고 햄스터: 키보드 + 앞발 (키 입력마다 왼발/오른발 번갈아 내려간다)
KEYBOARD = [(K, {(x, 15) for x in range(3, 19)} | {(x, 19) for x in range(3, 19)} | {(3, y) for y in range(15, 20)} | {(18, y) for y in range(15, 20)}),
            (c(0.80, 0.80, 0.78), {(x, y) for x in range(4, 18) for y in range(16, 19)}),
            (c(0.55, 0.55, 0.53), {(x, y) for x in (6, 9, 12, 15) for y in (16, 17, 18)} | {(x, 17) for x in range(4, 18)})]
def paw(x0, y0): return [(K, {(x0 - 1, y0), (x0 + 3, y0), (x0 - 1, y0 + 1), (x0 + 3, y0 + 1), (x0, y0 - 1), (x0 + 1, y0 - 1), (x0 + 2, y0 - 1), (x0, y0 + 2), (x0 + 1, y0 + 2), (x0 + 2, y0 + 2)}),
                          (P, {(x0, y0), (x0 + 1, y0), (x0 + 2, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 2, y0 + 1)})]
TYPE_L = KEYBOARD + paw(5, 15) + paw(14, 12)   # 왼발 내림, 오른발 올림
TYPE_R = KEYBOARD + paw(5, 12) + paw(14, 15)   # 왼발 올림, 오른발 내림
OVERLAYS = {"type_l": TYPE_L, "type_r": TYPE_R}
# 액세서리 (설정에서 고르는 상시 장식, 22px 기준 위치)
HALO_WINGS = [(K, {(x, 0) for x in range(7, 15)} | {(x, 2) for x in range(7, 15)} | {(6, 1), (15, 1)}), (Y, {(x, 1) for x in range(7, 15)}), (c(0.86, 0.67, 0.24), {(8, 1), (9, 1)}),
              (W, mirror({(0, 9), (1, 9), (0, 10), (1, 10), (0, 11), (1, 11), (0, 12)})), (K, mirror({(0, 8), (1, 8), (2, 9), (2, 10), (2, 11), (1, 12), (0, 13)}))]
HELD_HEART = [(K, {(7, 13), (8, 13), (10, 13), (11, 13), (6, 14), (9, 14), (12, 14), (6, 15), (12, 15), (7, 16), (11, 16), (8, 17), (10, 17), (9, 18)}),
              (P, {(7, 14), (8, 14), (10, 14), (11, 14), (7, 15), (8, 15), (9, 15), (10, 15), (11, 15), (8, 16), (9, 16), (10, 16), (9, 17)}), (W, {(7, 14)})]
TOMATO_HAT = [(c(0.35, 0.67, 0.35), {(10, 0), (11, 0), (9, 1), (12, 1)}), (K, {(8, 1), (13, 1), (7, 2), (14, 2), (7, 3), (14, 3)}),
              (RED, {(x, 2) for x in range(8, 14)} | {(x, 3) for x in range(8, 14)}), (REDH, {(8, 2), (9, 2)})]
HEADPHONES_ACC = [(K, {(x, 1) for x in range(7, 15)} | {(5, 2), (6, 2), (15, 2), (16, 2), (4, 3), (17, 3), (3, 4), (18, 4), (2, 5), (19, 5)}
                      | {(x, y) for x in (0, 1, 2) for y in range(6, 11)} | {(x, y) for x in (19, 20, 21) for y in range(6, 11)}),
                  (c(0.78, 0.78, 0.80), {(1, 7), (1, 8), (1, 9), (20, 7), (20, 8), (20, 9)})]
GLASSES = [(RED, mirror({(3, 7), (4, 6), (5, 6), (6, 6), (7, 6), (8, 7), (8, 8), (8, 9), (7, 10), (6, 10), (5, 10), (4, 10), (3, 9), (3, 8)}) | {(9, 8), (10, 8), (11, 8), (12, 8)})]
BOW_ACC = [(P, mirror({(8, 0), (9, 0), (8, 1), (9, 1), (10, 1)})), (K, mirror({(7, 0), (7, 1), (8, 2), (9, 2)}) | {(10, 0), (11, 0)})]
ACCESSORIES = {"halo": HALO_WINGS, "heart": HELD_HEART, "tomato": TOMATO_HAT, "headphones": HEADPHONES_ACC, "glasses": GLASSES, "bow": BOW_ACC}
COSTUMES = {"xmas": SANTA, "halloween": PUMPKINHAT, "seollal": HOGEON, "chuseok": HOGEON, "summer": SUMMER, **ACCESSORIES}

# ---------- 대기 동작 4종 ----------
def groom(sk, up):  # 세수: 양손으로 볼 비비기
    y = 8 if up else 9
    return front(sk, eyes="closed", layers=[(K, mirror({(2, y), (5, y), (2, y + 1), (5, y + 1), (3, y - 1), (4, y - 1), (3, y + 2), (4, y + 2)})),
                                             (sk["ear"] if sk["ear"] != C_B else P, mirror({(3, y), (4, y), (3, y + 1), (4, y + 1)}))])
def cheeks(sk, level):  # 볼 채우기: 볼 안쪽에 밝은 볼주머니가 동그랗게 부푼다 (몸 색은 스킨에서)
    import math
    base_col = sk["paint"](2, 10)
    light = mixr(base_col, 6)
    r = {1: 2.2, 2: 3.2}[level]; cx, cy = 2.5, 11.5
    puff = {(x, y) for x in range(0, 8) for y in range(7, 17) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r}
    rim = {(x, y) for x in range(0, 9) for y in range(6, 18) if (x, y) not in puff and any((x + dx, y + dy) in puff for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    return front(sk, eyes="closed", mouth="smile", layers=[(K, mirror(rim)), (light, mirror(puff))])
def ball(sk, rot):  # 구르기: 공처럼 말려서 굴러간다. 모자색/배색 경계가 회전
    import math
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    cx, cy, r = 11.0, 12.0, 8.0; fill = {}
    for x in range(N):
        for y in range(N):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= r:
                a = (math.atan2(y + 0.5 - cy, x + 0.5 - cx) + rot) % (2 * math.pi)
                fill[(x, y)] = sk["belly"] if 0 < a < math.pi else sk["cap"]
    # 감은 눈·귀도 같이 회전
    for ang, kind in ((-2.2, "eye"), (-1.0, "eye"), (-1.6, "ear")):
        a = ang + rot; rr = r - 2.5 if kind == "eye" else r - 0.5
        x, y = int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a))
        if (x, y) in fill: fill[(x, y)] = sk["eye"] if kind == "eye" else (sk["ear"] if sk["ear"] != C_B else P)
    for pt, col in fill.items(): px[pt] = col
    outline(px, set(fill), sk["out"])
    return im.transform(im.size, Image.AFFINE, (1, 0, -(int(rot * 2) % 3 - 1), 0, 1, 0))
def peek(sk, dy, blink=False):  # 빼꼼: 아래로 숨었다가 눈만 내민다
    return front(sk, eyes="closed" if blink else "open", shift=(0, dy))

# ---------- 쳇바퀴 옆모습 ----------
SIDE = [  # x 4..16, y 8..17, 'c' 모자색 'b' 배색 'e' 눈 'p' 귀안/코
    "........cc...",
    "....ccccc_pcc",
    "..cccccccccec",
    ".ccccccccccec",
    ".ccccccccccc_",
    "cccccccccbbbp",
    "cccccccbbbbbb",
    "cccccbbbbbbb.",
    ".ccbbbbbbbb..",
    "..bbbbbbbb...",
]
def sprint(sk, frame):
    im = wheel(sk, frame % 4)
    px = im.load()
    for col, pts in SPEEDLINES:
        for x, y in pts: px[x, y] = col
    return im.transform(im.size, Image.AFFINE, (1, 0, -(1 if frame % 2 else -1), 0, 1, 0))

def wheel(sk, frame):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    cx = cy = 11.0
    for x in range(N):
        for y in range(N):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 9.6 < d <= 10.6: px[x, y] = GRAY
    for i in range(8):  # 안쪽 눈금 8개가 프레임마다 회전
        a = math.radians(frame * 11.25 + i * 45)
        x, y = int(cx + 8.6 * math.cos(a)), int(cy + 8.6 * math.sin(a))
        px[x, y] = GRAYD
    fill = {}
    for j, row in enumerate(SIDE):
        for i, ch in enumerate(row):
            if ch == ".": continue
            x, y = 4 + i, 8 + j
            if ch == "_": fill[(x, y)] = sk["cap"]
            else: fill[(x, y)] = {"c": sk["cap"], "b": sk["belly"], "e": sk["eye"], "p": sk["ear"] if sk["ear"] != C_B else P}[ch]
    legs = [{(6, 18), (12, 18)}, {(8, 18), (10, 18)}, {(7, 18), (11, 18)}, {(9, 18), (13, 18)}][frame % 4]
    for pt in legs: fill[pt] = sk["cap"]
    if sk["name"].startswith("소프트"): fill[(14, 11)] = sk["eye"]
    # 몸을 그린 뒤 외곽선(바퀴 위에 덮임)
    for pt, col in fill.items(): px[pt] = col
    outline(px, set(fill), sk["out"])
    for pt, col in fill.items(): px[pt] = col
    px[16, 12] = P  # 코
    return im

# ---------- 상태 → 프레임 (이미지, tick수; 1 tick = 120ms) ----------
def frames(sk, inline=True):
    eatA = front(sk, layers=seed(13) + hands(14, sk)); eatB = front(sk, layers=seed(12) + hands(13, sk))
    chew = front(sk, eyes="closed", layers=[(BL, mirror({(2, 11), (3, 11), (4, 11), (2, 12), (3, 12)}))])
    base = front(sk); blink = front(sk, eyes="closed")
    shock = lambda L, dx: front(sk, eyes="wide", mouth="open", layers=L if inline else [], shift=(dx, 0))
    P = lambda L: L if inline else []
    out = {
        "idle": [(eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (chew, 4), (blink, 4), (chew, 4), (blink, 4), (base, 12), (blink, 1), (base, 6)],
        "working": [(wheel(sk, i), 1) for i in range(4)],
        "focus": [(wheel(sk, i), 1) for i in range(4)],
        "done": [(front(sk, eyes="happy", mouth="smile", layers=P([(Y, POMPOM_L)])), 3), (front(sk, eyes="happy", mouth="smile", layers=P([(Y, POMPOM_U)]), shift=(0, -1 if not inline else 0)), 3)],
        "surprised": [(shock(SIREN_ON, -1), 1), (shock(SIREN_ON, 1), 1), (shock(SIREN_ON, 0), 3), (shock(SIREN_OFF, 0), 3)],
        "faint": [(front(sk, eyes="x", mouth="open", layers=P(SOUL1)), 5), (front(sk, eyes="x", mouth="open", layers=P(SOUL2)), 5)],
        "sleep": [(front(sk, eyes="closed", layers=P(ZZ1)), 8), (front(sk, eyes="closed", layers=P(ZZ2), shift=(0, 1)), 8)],
        "notify": [(front(sk, eyes="happy", mouth="smile", layers=P(envelope(0))), 4), (front(sk, eyes="happy", mouth="smile", layers=P(envelope(1)), shift=(0, -1 if not inline else 0)), 4)],
        # 분위기
        "lunch": [(eatA, 3), (eatB, 3)],
        "leave": [(base, 20), (blink, 2), (front(sk, eyes="happy", mouth="smile"), 10)],
        "night": [(front(sk, eyes="closed", layers=NIGHTCAP), 10), (front(sk, eyes="closed", mouth="yawn", layers=NIGHTCAP), 6)],
        "friday": [(front(sk, eyes="happy", mouth="smile", layers=PARTYHAT), 4), (front(sk, eyes="happy", mouth="smile", layers=PARTYHAT, shift=(0, -1)), 4)],
        "break": [(front(sk, eyes="closed", mouth="smile"), 12), (front(sk, eyes="closed", mouth="smile", shift=(0, 1)), 12)],
        "battery_low": [(front(sk, eyes="closed", mouth="open", layers=SWEAT, shift=(0, 1)), 8), (front(sk, eyes="closed", mouth="open", layers=SWEAT, shift=(0, 2)), 8)],
        "charging": [(eatA, 3), (eatB, 3)],
        "cpu": [(front(sk, eyes="wide", layers=SWEAT, shift=(-1, 0)), 1), (front(sk, eyes="wide", layers=SWEAT, shift=(1, 0)), 1)],
        "rain": [(base, 20), (blink, 2), (front(sk, mouth="open"), 6)],
        "snow": [(front(sk, eyes="closed", shift=(-1, 0)), 1), (front(sk, eyes="closed", shift=(1, 0)), 1), (front(sk, eyes="closed"), 1)],
        "hot": [(front(sk, eyes="closed", mouth="open", layers=SWEAT), 8), (front(sk, eyes="closed", mouth="open", layers=SWEAT, shift=(0, 1)), 8)],
        # 클릭 반응·기상
        "grumpy": [(front(sk, eyes="flat", mouth="frown", layers=P(ZZ2), shift=(1, 0)), 2), (front(sk, eyes="flat", mouth="frown", layers=P(ZZ2), shift=(-1, 0)), 2)],
        "sprint": [(sprint(sk, i), 1) for i in range(8)],
        "pet_meeting": [(front(sk, eyes="happy", mouth="smile", layers=HEADPHONES + HEARTS), 3), (front(sk, eyes="happy", mouth="smile", layers=HEADPHONES + HEARTS, shift=(0, -1)), 3)],
        "dizzy": [(front(sk, eyes="closed", mouth="open", layers=SWEAT, shift=(-1, 0)), 2), (front(sk, eyes="closed", mouth="open", layers=SWEAT, shift=(1, 0)), 2), (front(sk, eyes="closed", layers=SWEAT), 4)],
        "wake": [(front(sk, eyes="closed", mouth="yawn", layers=ARMS_UP), 8), (front(sk, eyes="closed", mouth="yawn", layers=ARMS_UP, shift=(0, -1)), 6), (front(sk, eyes="closed", mouth="smile"), 6), (base, 6)],
        "idle_groom": [(groom(sk, True), 2), (groom(sk, False), 2), (groom(sk, True), 2), (groom(sk, False), 2), (groom(sk, True), 2), (groom(sk, False), 2), (front(sk, eyes="closed", mouth="smile"), 6)],
        "idle_cheeks": [(eatA, 3), (eatB, 3), (eatA, 3), (eatB, 3), (cheeks(sk, 1), 5), (eatA, 3), (eatB, 3), (cheeks(sk, 2), 10), (front(sk, eyes="closed", mouth="smile"), 6)],
        "idle_roll": [(front(sk, eyes="closed"), 4)] + [(ball(sk, i * 0.785), 1) for i in range(16)] + [(front(sk, eyes="closed"), 2), (base, 4)],
        "typing": [(base, 20), (blink, 1), (front(sk, mouth="smile"), 10)],
        "stash": [(cheeks(sk, 1), 3), (cheeks(sk, 2), 8), (front(sk, eyes="closed", mouth="smile"), 4)],
        "idle_peek": [(peek(sk, 6), 3), (peek(sk, 12), 10), (peek(sk, 9), 8), (peek(sk, 9, True), 1), (peek(sk, 9), 8), (peek(sk, 12), 6), (peek(sk, 6), 2), (base, 6)],
        "water": [(front(sk, eyes="closed", mouth="smile"), 12), (front(sk, eyes="closed", mouth="smile", shift=(0, 1)), 12)],
        "birthday": [(front(sk, eyes="happy", mouth="smile", layers=PARTYHAT), 4), (front(sk, eyes="happy", mouth="smile", layers=PARTYHAT, shift=(0, -1)), 4)],
        # 이벤트·활동
        "meeting_soon": [(front(sk, eyes="wide", mouth="open", shift=(-1, 0)), 1), (front(sk, eyes="wide", mouth="open", shift=(1, 0)), 1), (front(sk, eyes="wide", mouth="open"), 2)],
        "meeting": [(front(sk, layers=HEADPHONES), 20), (front(sk, eyes="closed", layers=HEADPHONES), 2)],
        "pet": [(front(sk, eyes="happy", mouth="smile", layers=HEARTS), 3), (front(sk, eyes="happy", mouth="smile", layers=HEARTS, shift=(0, -1)), 3)],
        "update": [(front(sk, eyes="happy", mouth="smile"), 4), (front(sk, eyes="happy", mouth="smile", shift=(0, -1)), 4)],
    }
    if sk.get("sb"):  # 시안 그대로: 손·씨·볼주머니·세수 없이 살짝 끄덕이는 대기
        calm = [(base, 30), (front(sk, shift=(0, 1)), 6)]
        for k in ("idle", "idle_groom", "idle_cheeks", "stash", "lunch", "charging", "typing"): out[k] = calm
    return out

STATE_NAMES = {"idle": "대기 (씨 먹기)", "working": "작업 중 (쳇바퀴)", "done": "완료", "surprised": "권한 요청", "faint": "에러 (기절)", "sleep": "잠", "notify": "알림 도착",
    "lunch": "점심 12시", "leave": "퇴근 19시", "night": "밤 23시", "friday": "금요일 오후", "break": "50분 일함, 쉬어", "battery_low": "배터리 20%", "charging": "충전 중",
    "cpu": "CPU 과부하", "meeting_soon": "회의 5분 전", "meeting": "회의 중", "pet": "쓰다듬기",
    "rain": "비 오는 날", "snow": "눈 오는 날", "hot": "30도 이상", "birthday": "생일", "water": "물 마실 시간", "grumpy": "자는데 깨움 (짜증)", "sprint": "쳇바퀴 전력질주 (클릭)", "pet_meeting": "회의 중 쓰다듬기", "dizzy": "기절에서 부활 (클릭)", "wake": "기상 (기지개)", "focus": "집중 세션", "idle_groom": "대기: 세수", "idle_cheeks": "대기: 볼 채우기", "idle_roll": "대기: 구르기", "idle_peek": "대기: 빼꼼", "stash": "볼주머니에 넣기 (복사)", "typing": "같이 타자 치기 (봉고)", "update": "새 버전 알림 (선물)"}


CORE = ["idle", "working", "done", "surprised", "faint", "sleep", "notify"]
def uri(im):
    buf = io.BytesIO(); im.save(buf, "PNG"); return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
def anim_tag(fr, cls):
    return f'<img class="{cls} anim" data-f=\'{json.dumps([uri(im) for im, _ in fr])}\' data-t=\'{json.dumps([t for _, t in fr])}\'>'

def export_indexed(frames_by_state, dirpath):
    """모든 프레임을 가로로 이어 붙인 8비트 시트 한 장(sheet.png) + 색 테이블·오프셋(index.json). 0 = 투명"""
    table = [None]; index = {}
    def idx(col):
        if col[3] == 0: return 0
        key = tuple(col)
        if key not in index:
            index[key] = len(table); table.append({"role": col[0], "variant": col[1]} if is_role(col) else {"rgba": list(col)})
        return index[key]
    os.makedirs(dirpath, exist_ok=True)
    frames = [(state, im, t) for state, fr in frames_by_state.items() for im, t in fr]
    size = frames[0][1].size[0]
    sheet = Image.new("L", (size * len(frames), size), 0); sp = sheet.load(); states = {}; ticks = {}
    for n, (state, im, t) in enumerate(frames):
        px = im.load()
        for y in range(size):
            for x in range(size): sp[n * size + x, y] = idx(px[x, y])
        states.setdefault(state, n); ticks.setdefault(state, []).append(t)
    sheet.save(f"{dirpath}/sheet.png", optimize=True)
    json.dump({"table": table, "offset": states, "ticks": ticks, "size": size}, open(f"{dirpath}/index.json", "w"))
    return ticks

if __name__ == "__main__":
    import props
    shutil.rmtree("frames", ignore_errors=True)
    meta = {"skins": {}, "templates": {}, "props": {}, "scenes": {}, "logos": list(props.LOGOS)}
    def dump(fr, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        for i, (im, t) in enumerate(fr): im.save(f"{path}-{i}.png")
        return [t for _, t in fr]
    for state in props.PROPS:
        meta["props"][state] = dump(props.PROPS[state], f"frames/props/{state}")
        meta["scenes"][state] = dump(props.SCENES[state], f"frames/scene/{state}")
    os.makedirs("frames/costume", exist_ok=True)
    for name, layers in COSTUMES.items():
        im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
        for col, pts in layers:
            for x, y in pts: px[x, y] = col
        im.save(f"frames/costume/{name}.png")
    meta["costumes"] = list(COSTUMES); meta["accessories"] = list(ACCESSORIES)
    os.makedirs("frames/overlay", exist_ok=True)
    for name, layers in OVERLAYS.items():
        im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
        for col, pts in layers:
            for x, y in pts: px[x, y] = col
        im.save(f"frames/overlay/{name}.png")
    os.makedirs("frames/logo", exist_ok=True)
    for app, im in props.LOGOS.items(): im.save(f"frames/logo/{app}.png")
    # 템플릿: 패턴 6 + 수제 스킨(역할 없음, 자기 색 그대로)
    all_templates = dict(TEMPLATES)
    for key, sk in SKINS.items():
        if not sk["template"].startswith(("pat_", "sb_")): all_templates[key] = sk
    for tname, tsk in all_templates.items():
        inline, plain = frames(tsk, True), frames(tsk, False); plain["done"] = inline["done"]
        meta["templates"][tname] = {"inline": export_indexed(inline, f"frames/{tname}/inline"), "plain": export_indexed(plain, f"frames/{tname}/plain")}
    for key, sk in SKINS.items():
        pal = {r: list(col) for r, col in palette22(sk).items()} if sk["template"].startswith(("pat_", "sb_")) else {}
        meta["skins"][key] = {"name": sk["name"], "template": sk["template"], "pal22": pal}
    json.dump(meta, open("frames/meta.json", "w"), ensure_ascii=False, indent=1)
    print("templates", len(all_templates), "skins", len(SKINS))
