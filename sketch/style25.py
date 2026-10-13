# 참고 이미지 25 스타일 실험: 40x32 격자, 굵은 외곽선·평면색·점 눈
from PIL import Image
import base64, io, json
PAL = {"k": (40, 36, 40), "t": (236, 220, 190), "T": (120, 110, 100), "w": (255, 255, 255), "p": (250, 185, 200), "P": (240, 140, 165),
       "e": (50, 46, 50), "y": (255, 220, 110), "Y": (220, 170, 60), "r": (235, 70, 70), "R": (255, 120, 120), "v": (90, 170, 90),
       "g": (200, 200, 205), "G": (120, 120, 128), "h": (255, 240, 245)}
W, H = 40, 32
def img(rows):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = im.load()
    for y, r in enumerate(rows[:H]):
        for x, ch in enumerate(r[:W]):
            if ch != ".": px[x, y] = PAL[ch] + (255,)
    return im
# 몸통 (황갈 줄무늬) — 32 높이, 가운데 x 4..35
BODY = [
    "........................................",
    "...........kkkk......kkkk...............",
    "..........kppppk....kppppk..............",
    ".........kppttppk..kppttppk.............",
    ".........ktttttttkkttttttttk............",
    "........kttttTtttttttTttttttk...........",
    "........kttttTtttttttTttttttk...........",
    "........kttttTtttttttTttttttk...........",
    "........kttttTtttttttTttttttk...........",
    ".......kttttttttttttttttttttk...........",
    ".......kttttttttttttttttttttk...........",
    ".......kttttteettttttteettttk...........",
    "......kpptttteettttttteetttppk..........",
    "......kpptttttttttttttttttttppk.........",
    "......kpptttttttkkkttttttttppk..........",
    ".......kttttttttkkktttttttttk...........",
    ".......kwwwwwwwwwwwwwwwwwwwwk...........",
    "......kwwwwwwwwwwwwwwwwwwwwwwk..........",
    "......kwwwwwwwwwwwwwwwwwwwwwwk..........",
    "......kwwwwwkkkwwwwwwkkkwwwwwk..........",
    "......kwwwwkpppkwwwwkpppkwwwwk..........",
    "......kwwwwkpppkwwwwkpppkwwwwk..........",
    "......kwwwwwkkkwwwwwwkkkwwwwwk..........",
    "......kwwwwwwwwwwwwwwwwwwwwwwk..........",
    ".......kwwwwwwwwwwwwwwwwwwwwk...........",
    ".......kwwwwwwwwwwwwwwwwwwwwk...........",
    "........kwwwwwwwwwwwwwwwwwwk............",
    ".........kkkkppkkkkkkppkkkk.............",
    "............kppk....kppk................",
    "............kkkk....kkkk................",
    "........................................",
    "........................................",
]
def place(base, rows, x0, y0):
    base = [list(r) for r in base]
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != "." and 0 <= y0 + j < H and 0 <= x0 + i < W: base[y0 + j][x0 + i] = ch
    return ["".join(r) for r in base]
WHITE = [r.replace("t", "w").replace("T", "w") for r in BODY]
HALO = ["..kkkkkkkk..", ".kyyyyyyyyk.", "kyYYYYYYYYyk", ".kyyyyyyyyk.", "..kkkkkkkk.."]
WINGS_L = ["....kk", "..kkhhk", ".khhhhk", "khhhhhk", "khhhhk.", ".kkkk.."]
WINGS_R = [r[::-1] for r in WINGS_L]
HEART = ["..kkk...kkk..", ".kpppk.kpppk.", "kpphppkpppppk", "kppppppppppppk"[:13], ".kppppppppppk", "..kppppppppk.", "...kppppppk..", "....kppppk...", ".....kppk....", "......kk....."]
BOW = ["kk.....kk", "kppk.kppk", "kpppkpppk", "kpppkpppk", "kppk.kppk", "kk.....kk"]
HEADPHONES = None
TOMATO = ["....vv....", "...kvvk...", ".kkkrrkkk.", "krrRrrrrrk", "krRrrrrrrk", "krrrrrrrrk", ".krrrrrrk.", "..kkkkkk.."]
def headphones(base):
    rows = place(base, ["....kkkkkkkkkkkkkkk....", "...kk...............kk.", "..k...................k", ".kk...................kk"], 7, 1)
    rows = place(rows, ["kkkk", "kggk", "kGgk", "kggk", "kggk", "kkkk"], 4, 10)
    rows = place(rows, ["kkkk", "kggk", "kgGk", "kggk", "kggk", "kkkk"], 28, 10)
    return rows
variants = {
    "황갈 줄무늬": BODY,
    "흰색 + 리본": place(WHITE, BOW, 13, 0),
    "천사 (후광·날개·하트)": place(place(place(place(BODY, HALO, 12, 0), WINGS_L, 1, 15), WINGS_R, 33, 15), HEART, 11, 17),
    "토마토 모자": place(BODY, TOMATO, 13, 0),
    "헤드폰": headphones(BODY),
    "흰색 천사": place(place(place(place(WHITE, HALO, 12, 0), WINGS_L, 1, 15), WINGS_R, 33, 15), HEART, 11, 17),
}
def uri(im):
    b = io.BytesIO(); im.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
cells = "".join(f'<div class="cell"><div class="lbl">{n}</div><div class="box"><img class="big" src="{uri(img(r))}"></div><div class="tray"><img class="n" src="{uri(img(r))}"></div></div>' for n, r in variants.items())
open("sketch/style25.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>스타일 25 실험</title>
<style>body{{font-family:-apple-system,sans-serif;background:#f4f1ea;margin:24px}}.row{{display:flex;gap:14px;flex-wrap:wrap}}.cell{{text-align:center}}.lbl{{font-size:12px;color:#666;margin-bottom:4px}}
img{{image-rendering:pixelated;display:block}}.box{{background:#fff;border-radius:8px;padding:8px}}.big{{width:200px;height:160px}}
.tray{{background:#000;border-radius:0 0 10px 10px;padding:1px 10px;margin-top:6px;display:flex;justify-content:center;height:34px;align-items:center}}.n{{width:40px;height:32px}}</style>
<h1 style="font-size:18px">참고 이미지 25 스타일 — 40×32 격자 실험</h1>
<p style="font-size:13px;color:#666">위: 5배 확대. 아래 검은 띠: 노치 트레이 실제 크기(햄스터 칸을 40px로 넓힘).</p><div class="row">{cells}</div>''')
im = Image.new("RGBA", (200 * len(variants), 160), (235, 230, 220, 255))
for i, r in enumerate(variants.values()): im.paste(img(r).resize((200, 160), Image.NEAREST), (i * 200, 0), img(r).resize((200, 160), Image.NEAREST))
im.save("sketch/style25.png")
print("ok")
