# 소품(prop, 2번째 칸)과 장면(scene, 3번째 칸) 스프라이트. 22x22, 문자 격자.
from PIL import Image
N = 22
PAL = {"k": (40,38,38), "w": (255,255,255), "y": (255,200,60), "Y": (220,160,30), "r": (235,60,50), "R": (255,140,115),
       "M": (150,40,35), "g": (170,170,168), "G": (100,100,98), "z": (115,140,217), "p": (247,160,175), "s": (77,61,51),
       "o": (237,143,56), "l": (150,200,240), "c": (250,227,178), "n": (120,80,45), "v": (46,182,125), "m": (224,30,90),
       "u": (54,197,240), "e": (236,178,46), "a": (38,38,52), "S": (74,21,75), "t": (255,255,200), "d": (80,80,110), "L": (140,225,150)}

def grid(rows):
    out = []
    for r in rows:
        assert len(r) <= N, (len(r), r)
        out.append(r.ljust(N, "."))
    while len(out) < N: out.append("." * N)
    return out[:N]

def img(rows, outline=None):
    g = grid(rows); im = Image.new("RGBA", (N, N), (0,0,0,0)); px = im.load()
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch != ".": px[x, y] = PAL[ch] + (255,)
    if outline:
        fill = {(x, y) for y, row in enumerate(g) for x, ch in enumerate(row) if ch != "."}
        for x in range(N):
            for y in range(N):
                if (x, y) not in fill and any((x+dx, y+dy) in fill for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))): px[x, y] = PAL[outline] + (255,)
    return im

def shift(im, dx=0, dy=0): return im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy))
def place(base, rows, x0, y0):  # 작은 조각을 좌표에 얹는다
    base = grid(base)
    for j, r in enumerate(rows):
        row = list(base[y0 + j])
        for i, ch in enumerate(r):
            if ch != ".": row[x0 + i] = ch
        base[y0 + j] = "".join(row)
    return base

EMPTY = ["." * N] * N

# ---------- 소품 ----------
BOWL = [
    "", "", "", "", "", "",
    "........s.ss..........",
    "......sksskssk........",
    ".....ksskskssksk......",
    "....kkkkkkkkkkkkkk....",
    "...kwwwwwwwwwwwwwwk...",
    "...kwpppppppppppppwk..",
    "....kppppppppppppk....",
    "....kwppppppppppwk....",
    ".....kwwwwwwwwwwk.....",
    "......kkkkkkkkkk......",
]
def dots(up):
    rows = list(EMPTY)
    for i, x in enumerate((3, 9, 15)):
        y = 9 if i == up else 12
        rows = place(rows, [".ww.", "wwww", "wwwg", ".gg."], x, y)
    return rows
POMPOM = [
    "", "",
    "......y...y...y.......",
    ".....yyy.yyy.yyy......",
    "....yyyyyyyyyyyyy.....",
    "...yyyyyyyyyyyyyyy....",
    "...yYyyyyyyyyyyyYy....",
    "..yyyyyyyyyyyyyyyyy...",
    "..yyyyyyyyyyyyyyyyy...",
    "..yYyyyyyyyyyyyyyYy...",
    "..yyYyyyyyyyyyyyYyy...",
    "...yyYYyyyyyyyYYyy....",
    "...yyyyYYYYYYYyyyy....",
    "....yyyyyyyyyyyyy.....",
    "......yyyyyyyyy.......",
    ".........kkk..........",
    ".........kkk..........",
    ".........kkk..........",
    ".........kkk..........",
]
def siren(on):
    dome = "r" if on else "M"; hi = "R" if on else "M"
    rows = [
        "",
        "..........kk..........",
        ".........kkkk.........",
        "........k" + hi * 2 + dome * 2 + "k........",
        ".......k" + hi * 2 + dome * 4 + "k.......",
        ".......k" + hi + dome * 5 + "k.......",
        "......k" + hi + dome * 7 + "k......",
        "......k" + dome * 8 + "k......",
        "......k" + dome * 8 + "k......",
        "......k" + dome * 8 + "k......",
        "......k" + dome * 8 + "k......",
        ".....kkkkkkkkkkkk.....",
        "....kGGGGGGGGGGGGk....",
        "....kGGGGGGGGGGGGk....",
        ".....kkkkkkkkkkkk.....",
    ]
    if on:
        for x, y in ((3, 3), (18, 3), (2, 7), (19, 7), (4, 1), (17, 1), (10, 0), (11, 0)):
            rows = place(rows, ["R"], x, y) if y < len(rows) else rows
    return rows
SOUL = [
    "", "",
    "........wwwwww........",
    ".......wwwwwwww.......",
    "......wwwwwwwwww......",
    "......wwkkwwwkkw......",
    "......wwkkwwwkkw......",
    "......wwwwwwwwww......",
    "......wwwwkkwwww......",
    "......wwwwwwwwww......",
    "......wwwwwwwwww......",
    "......wwwwwwwwww......",
    "......wwwwwwwwww......",
    "......ww.wwww.ww......",
    "......w...ww...w......",
]
def zzz():
    rows = list(EMPTY)
    rows = place(rows, ["zzzzz", "...z.", "..z..", ".z...", "zzzzz"], 15, 1)
    rows = place(rows, ["zzzz", "..z.", ".z..", "zzzz"], 9, 7)
    rows = place(rows, ["zzz", ".z.", "zzz"], 4, 12)
    return rows
ENVELOPE = [
    "", "", "", "",
    ".kkkkkkkkkkkkkkkkkkkk.",
    ".kwwwwwwwwwwwwwwwwwwk.",
    ".kkwwwwwwwwwwwwwwwwkk.",
    ".kwkwwwwwwwwwwwwwwkwk.",
    ".kwwkwwwwwwwwwwwwkwwk.",
    ".kwwwkwwwwwwwwwwkwwwk.",
    ".kwwwwkwwwwwwwwkwwwwk.",
    ".kwwwwwkwwwwwwkwwwwwk.",
    ".kwwwwwwkwwwwkwwwwwwk.",
    ".kwwwwwwwkwwkwwwwwwwk.",
    ".kwwwwwwwwkkwwwwwwwwk.",
    ".kwwwwwwwwwwwwwwwwwwk.",
    ".kwwwwwwwwwwwwwwwwwwk.",
    ".kkkkkkkkkkkkkkkkkkkk.",
]
ENVELOPE = place(ENVELOPE, [".m.m.", "mmmmm", ".mmm.", "..m.."], 8, 12)

# ---------- 장면 ----------
HOUSE = [
    "", "",
    "..........kk..........",
    ".........kppk.........",
    "........kppppk........",
    ".......kppppppk.......",
    "......kppppppppk......",
    ".....kppppppppppk.....",
    "....kppppppppppppk....",
    "...kkkkkkkkkkkkkkkk...",
    "....kcccccccccccck....",
    "....kcclllccckkkck....",
    "....kcclllccckaakck...",
    "....kcckkkccckaakck...",
    "....kcccccccckaakck...",
    "....kcccccccckaakck...",
    "....kkkkkkkkkkkkkkk...",
]
def window(cursor):
    rows = [
        "", "", "",
        ".kkkkkkkkkkkkkkkkkkk..",
        ".kGGGGGGGGGGGGGGGGGk..",
        ".kGrGyGvGGGGGGGGGGGk..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kauuuuaaeeeeeeaaaak..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kaaavvvvvvaaaammmak..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kaaauuaaeeeeaaaaaak..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kaaavvvvvvvvvaaaaak..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kaaa" + ("ww" if cursor else "aa") + "aaaaaaaaaaaak..",
        ".kaaaaaaaaaaaaaaaaak..",
        ".kkkkkkkkkkkkkkkkkkk..",
    ]
    return rows
def confetti(f):
    pts = [((3, 4, "y"), (8, 2, "u"), (14, 5, "m"), (18, 9, "v"), (5, 12, "r"), (11, 10, "p"), (16, 15, "y"), (2, 17, "u"), (9, 18, "m"), (19, 2, "r")),
           ((4, 6, "u"), (9, 3, "y"), (15, 7, "v"), (18, 11, "m"), (6, 14, "p"), (12, 12, "r"), (17, 17, "u"), (3, 19, "y"), (10, 20, "v"), (20, 4, "m"))][f]
    rows = list(EMPTY)
    for x, y, c in pts: rows = place(rows, [c], x, y)
    for x, y in [((6, 8), (14, 13))[f], ((15, 3), (5, 16))[f]]:  # 반짝이
        rows = place(rows, [".t.", "ttt", ".t."], x, y)
    return rows
QMARK = [
    "", "", "",
    ".......yyyyyyy........",
    "......yyyyyyyyy.......",
    ".....yyy.....yyy......",
    ".....yy.......yy......",
    ".............yyy......",
    "............yyy.......",
    "..........yyyy........",
    ".........yyy..........",
    ".........yy...........",
    ".........yy...........",
    "",
    ".........yyy..........",
    ".........yyy..........",
]
def storm(bolt):
    rows = [
        "", "",
        "........gggg..........",
        "......gggggggg........",
        "....gggggggggggg......",
        "...gggggggggggggg.....",
        "..gggggggggggggggg....",
        "..gggggggggggggggg....",
        "...GGGGGGGGGGGGGG.....",
    ]
    if bolt:
        rows += ["", "..........yyy.........", ".........yyy..........", "........yyyyy.........", "..........yyy.........", ".........yy...........", "........yy............", ".......y.............."]
    return rows
def night(f):
    rows = [
        "", "",
        ".......yyyy...........",
        ".....yyyyyyy..........",
        "....yyyyy.............",
        "...yyyyy..............",
        "...yyyy...............",
        "...yyyy...............",
        "...yyyyy..............",
        "....yyyyy.............",
        ".....yyyyyyy..........",
        ".......yyyy...........",
    ]
    stars = [((15, 4), (17, 12), (12, 16)), ((16, 7), (14, 14), (19, 3))][f]
    for x, y in stars: rows = place(grid(rows), [".t.", "ttt", ".t."], x, y)
    return rows
SLACK = [
    "", "",
    "....SSSSSSSSSSSSSS....",
    "...SSSSSSSSSSSSSSSS...",
    "..SSSSSSSSSSSSSSSSSS..",
    "..SSSSSuuSSSSSSSSSSS..",
    "..SSSSSuuSSvvvvvvSSS..",
    "..SSSSSuuSSvvvvvvSSS..",
    "..SSSSSuuSSSSSSSSSSS..",
    "..SSSSSuuSSSSSSSSSSS..",
    "..SSSSSSSSSSSSeeSSSS..",
    "..SSSSSSSSSSSSeeSSSS..",
    "..SSSmmmmmmSSSeeSSSS..",
    "..SSSmmmmmmSSSeeSSSS..",
    "..SSSSSSSSSSSSeeSSSS..",
    "..SSSSSSSSSSSSSSSSSS..",
    "...SSSSSSSSSSSSSSSS...",
    "....SSSSSSSSSSSSSS....",
]
KAKAO = [
    "", "",
    "....yyyyyyyyyyyyyy....",
    "...yyyyyyyyyyyyyyyy...",
    "..yyyyyyyyyyyyyyyyyy..",
    "..yyyyyyyyyyyyyyyyyy..",
    "..yyyynnnnnnnnnnyyyy..",
    "..yyynnnnnnnnnnnnyyy..",
    "..yynnnnnnnnnnnnnnyy..",
    "..yynnnnnnnnnnnnnnyy..",
    "..yynnnnnnnnnnnnnnyy..",
    "..yyynnnnnnnnnnnnyyy..",
    "..yyyynnnnnnnnnnyyyy..",
    "..yyyynnnyyyyyyyyyyy..",
    "..yyyyynnyyyyyyyyyyy..",
    "..yyyyyyyyyyyyyyyyyy..",
    "...yyyyyyyyyyyyyyyy...",
    "....yyyyyyyyyyyyyy....",
]
BUBBLE = [
    "", "",
    "....kkkkkkkkkkkkkk....",
    "...kwwwwwwwwwwwwwwk...",
    "..kwwwwwwwwwwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwwwwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwkkwwwwwwwk..",
    "..kwwwwwwwwwwwwwwwwk..",
    "...kwwwwwwwwwwwwwwk...",
    "....kkkkkwwwkkkkkk....",
    ".......kwwk...........",
    "......kwk.............",
    "......kk..............",
]

# 완료 체크: 획이 그려지는 순서대로 드러난다
CHECK_PATH = [(3 + i, 10 + i) for i in range(6)] + [(8 + i, 15 - i) for i in range(1, 11)]
def check(n, sparkle=False):
    rows = list(EMPTY)
    for x, y in CHECK_PATH[:n]:
        rows = place(rows, ["LL", "LL"], x, y)
    if sparkle:
        for x, y in ((18, 1), (20, 5), (14, 2)): rows = place(rows, ["t"], x, y)
        rows = place(rows, [".t.", "ttt", ".t."], 0, 4)
    return rows

# 상태 → (소품 프레임, 장면 프레임). 각 (이미지, tick)
PROPS = {
    "idle": [(img(BOWL), 10)],
    "working": [(img(dots(i)), 2) for i in range(3)],
    "done": [(img(check(4)), 1), (img(check(8)), 1), (img(check(12)), 1), (img(check(16)), 1), (img(check(16, True)), 3), (img(check(16)), 14)],
    "surprised": [(img(siren(True)), 3), (img(siren(False)), 3)],
    "faint": [(img(SOUL, outline="g"), 5), (shift(img(SOUL, outline="g"), dy=-1), 5)],
    "sleep": [(img(zzz()), 8), (shift(img(zzz()), dy=-1), 8)],
    "notify": [(img(ENVELOPE), 4), (shift(img(ENVELOPE), dy=-1), 4)],
}
SCENES = {
    "idle": [(img(HOUSE), 10)],
    "working": [(img(window(True)), 4), (img(window(False)), 4)],
    "done": [(img(confetti(0)), 3), (img(confetti(1)), 3)],
    "surprised": [(img(QMARK, outline="k"), 4), (shift(img(QMARK, outline="k"), dy=1), 4)],
    "faint": [(img(storm(True)), 2), (img(storm(False)), 4)],
    "sleep": [(img(night(0)), 8), (img(night(1)), 8)],
    "notify": [(img(BUBBLE), 10)],
}
LOGOS = {"slack": img(SLACK), "kakao": img(KAKAO), "generic": img(BUBBLE)}

# ---------- 2차: 분위기·이벤트 소품 ----------
BENTO = [
    "", "", "", "", "",
    "...kkkkkkkkkkkkkkkk...",
    "..kppppppppppppppppk..",
    "..kppppppppppppppppk..",
    "..kkkkkkkkkkkkkkkkkk..",
    "..kwwwwwwkwwwwwwwwwk..",
    "..kwwwwwwkwooooowwwk..",
    "..kwwwwwwkwooooowwwk..",
    "..kkkkkkkkwooooowwwk..",
    "..kwvvvvwkwwwwwwwwwk..",
    "..kwvvvvwkwrrwwwrrwk..",
    "..kwwwwwwkwrrwwwrrwk..",
    "..kkkkkkkkkkkkkkkkkk..",
]
BAG = [
    "", "", "",
    "........kkkkkk........",
    ".......kk....kk.......",
    ".......k......k.......",
    "...kkkkkkkkkkkkkkkk...",
    "..knnnnnnnnnnnnnnnnk..",
    "..knnnnnnnnnnnnnnnnk..",
    "..knnnnkkkkkkkknnnnk..",
    "..knnnnkssssssknnnnk..",
    "..knnnnkssssssknnnnk..",
    "..knnnnkkkkkkkknnnnk..",
    "..knnnnnnnnnnnnnnnnk..",
    "..knnnnnnnnnnnnnnnnk..",
    "..knnnnnnnnnnnnnnnnk..",
    "...kkkkkkkkkkkkkkkk...",
]
def coffee(steam):
    rows = [
        ".....g..g..g..........",
        "......g..g..g.........",
        ".....g..g..g..........",
        "", 
        "...kkkkkkkkkkkk.......",
        "...kwwwwwwwwwwkkk.....",
        "...kwnnnnnnnnwkwwk....",
        "...kwnnnnnnnnwkwwk....",
        "...kwnnnnnnnnwkwwk....",
        "...kwnnnnnnnnwkkk.....",
        "....kwnnnnnnwk........",
        "....kwwwwwwwwk........",
        ".....kkkkkkkk.........",
    ]
    return rows if steam else [""] * 3 + rows[3:]
def battery(level, charging):
    fill = "v" if charging else "r"
    rows = [
        "", "", "", "", "",
        "..kkkkkkkkkkkkkkkk....",
        "..kwwwwwwwwwwwwwwkk...",
        "..kw" + fill * level + "w" * (12 - level) + "wkkk..",
        "..kw" + fill * level + "w" * (12 - level) + "wkwk..",
        "..kw" + fill * level + "w" * (12 - level) + "wkwk..",
        "..kw" + fill * level + "w" * (12 - level) + "wkwk..",
        "..kw" + fill * level + "w" * (12 - level) + "wkkk..",
        "..kwwwwwwwwwwwwwwkk...",
        "..kkkkkkkkkkkkkkkk....",
    ]
    if charging:
        rows = place(rows, [".yy", "yy.", "yyy", ".yy", "y.."], 9, 7)
    return rows
def fire(f):
    rows = [
        "", "",
        "..........r...........",
        ".........rr...........",
        "........rrr..r........",
        ".......rrrr.rr........",
        "......rrrrrrrr........",
        ".....rrrrrrrrrr.......",
        ".....rrroorrrrrr......",
        "....rrroooorrrrr......",
        "....rrrooooorrrr......",
        "....rroooyyoorrr......",
        "....rrooyyyyoorr......",
        ".....rooyyyyoor.......",
        ".....rrooyyoorr.......",
        "......rrooorrr........",
        ".......rrrrrr.........",
    ]
    return rows if f == 0 else [""] + rows[:-1]
BOXES = [
    "", "", "",
    "......kkkkkkkk........",
    "......knnnnnnk........",
    "......knkkkknk........",
    "......knnnnnnk........",
    "..kkkkkkkkkkkkkkkk....",
    "..knnnnnnkknnnnnnk....",
    "..knkkkknkknkkkknk....",
    "..knnnnnnkknnnnnnk....",
    "..knnnnnnkknnnnnnk....",
    "..kkkkkkkkkkkkkkkk....",
    "..knnnnnnkknnnnnnk....",
    "..knkkkknkknkkkknk....",
    "..knnnnnnkknnnnnnk....",
    "..kkkkkkkkkkkkkkkk....",
]
def clock(f):
    rows = [
        "", 
        "....kk........kk......",
        "...krrk......krrk.....",
        "....kkkkkkkkkkkk......",
        ".....kkwwwwwwkk.......",
        "....kwwwwwwwwwwk......",
        "...kwwwwwkwwwwwwk.....",
        "...kwwwwwkwwwwwwk.....",
        "..kwwwwwwkwwwwwwwk....",
        "..kwwwwwwkkkwwwwwk....",
        "..kwwwwwwwwwwwwwwk....",
        "...kwwwwwwwwwwwwk.....",
        "...kwwwwwwwwwwwwk.....",
        "....kwwwwwwwwwwk......",
        ".....kkwwwwwwkk.......",
        "......kkkkkkkk........",
        ".....kk......kk.......",
    ]
    return rows if f == 0 else [r.replace("krrk", "kRRk") for r in rows]
HEART = [
    "", "", "", "",
    "....mmm......mmm......",
    "...mmmmm....mmmmm.....",
    "..mmmmmmm..mmmmmmm....",
    "..mmwmmmmmmmmmmmmm....",
    "..mmwmmmmmmmmmmmmm....",
    "..mmmmmmmmmmmmmmmm....",
    "...mmmmmmmmmmmmmm.....",
    "....mmmmmmmmmmmm......",
    ".....mmmmmmmmmm.......",
    "......mmmmmmmm........",
    ".......mmmmmm.........",
    "........mmmm..........",
    ".........mm...........",
]
CLOUD = [
    "", "", "", "", "",
    "........gggg..........",
    "......gggggggg........",
    "....gggggggggggg......",
    "...gggggggggggggg.....",
    "..gggggggggggggggg....",
    "..gggggggggggggggg....",
    "...GGGGGGGGGGGGGG.....",
    "", 
    ".....l...l...l........",
    "......l...l...l.......",
    ".......l...l...l......",
]
MIC = [
    "", "",
    "........kkkkkk........",
    ".......kGGGGGGk.......",
    ".......kGggGggGk......",
    ".......kGggGggGk......",
    ".......kGggGggGk......",
    ".......kGggGggGk......",
    ".......kGggGggGk......",
    ".......kGGGGGGGk......",
    "....kk.kGGGGGGGk.kk...",
    "....k..kkkkkkkkk..k...",
    "....kk...........kk...",
    ".....kkk.......kkk....",
    ".......kkkkkkkkk......",
    "..........kk..........",
    "..........kk..........",
    ".......kkkkkkkk.......",
]
CALENDAR = [
    "", "",
    ".....k....k....k......",
    "..kkkkkkkkkkkkkkkkk...",
    "..krrrrrrrrrrrrrrrk...",
    "..krrrrrrrrrrrrrrrk...",
    "..kkkkkkkkkkkkkkkkk...",
    "..kwwwwwwwwwwwwwwwk...",
    "..kwkkwwkkwwkkwwkwk...",
    "..kwwwwwwwwwwwwwwwk...",
    "..kwkkwwrrwwkkwwkwk...",
    "..kwwwwwrrwwwwwwwwk...",
    "..kwkkwwkkwwkkwwkwk...",
    "..kwwwwwwwwwwwwwwwk...",
    "..kkkkkkkkkkkkkkkkk...",
]
PROPS.update({
    "lunch": [(img(BENTO), 10)],
    "leave": [(img(BAG), 10)],
    "break": [(img(coffee(True)), 5), (img(coffee(False)), 5)],
    "battery_low": [(img(battery(2, False)), 5), (img(battery(0, False)), 3)],
    "charging": [(img(battery(4, True)), 3), (img(battery(8, True)), 3), (img(battery(12, True)), 3)],
    "cpu": [(img(fire(0)), 2), (img(fire(1)), 2)],

    "meeting_soon": [(img(clock(0)), 2), (shift(img(clock(1)), dx=1), 1), (img(clock(0)), 2), (shift(img(clock(1)), dx=-1), 1)],
    "meeting": [(img(MIC), 10)],
    "pet": [(img(HEART), 3), (shift(img(HEART), dy=-1), 3)],
    "night": [(img(zzz()), 8), (shift(img(zzz()), dy=-1), 8)],
    "friday": [(img(confetti(0)), 3), (img(confetti(1)), 3)],
})
SCENES.update({
    "lunch": SCENES["idle"], "leave": SCENES["idle"], "break": SCENES["idle"], "battery_low": SCENES["idle"],
    "charging": SCENES["idle"], "cpu": SCENES["working"],
    "meeting_soon": [(img(CALENDAR), 10)], "meeting": [(img(CALENDAR), 10)], "pet": SCENES["done"],
    "night": SCENES["sleep"], "friday": SCENES["done"],
})

# ---------- 3차: 날씨·생일·아웃룩 ----------
UMBRELLA = [
    "", "",
    "..........k...........",
    ".......kkkkkkk........",
    ".....kkmmmmmmmkk......",
    "....kmmmmmmmmmmmk.....",
    "...kmmmwmmmmmwmmmk....",
    "..kmmmmwmmmmmwmmmmk...",
    "..kkkkkkkkkkkkkkkkk...",
    "..........kk..........",
    "..........kk..........",
    "..........kk..........",
    "..........kk..........",
    "..........kk..........",
    "......k...kk..........",
    "......kk.kk...........",
    ".......kkk............",
]
SNOWMAN = [
    "",
    "........kkkkkk........",
    "........kaaaak........",
    "......kkkkkkkkkk......",
    ".......kwwwwwwk.......",
    "......kwwkwwkwwk......",
    "......kwwwwwwwwk......",
    "......kwwwooowwk......",
    ".......kwwwwwwk.......",
    "....kkkkkwwwwkkkkk....",
    "...krrrrrkwwkrrrrrk...",
    "....kkkkkwwwwkkkkk....",
    ".....kwwwwwwwwwwk.....",
    "....kwwwwwkkwwwwwk....",
    "....kwwwwwwwwwwwwk....",
    "....kwwwwwkkwwwwwk....",
    ".....kwwwwwwwwwwk.....",
    "......kkkkkkkkkk......",
]
def fan(f):
    blades = [
        ["........lll...........", ".......lllll..........", "......lllllll.........", "....lllllGGlllll......", "...llllGGGGGGllll.....", "....lllllGGlllll......", "......lllllll.........", ".......lllll..........", "........lll..........."],
        ["....lll......lll......", "...lllll....lllll.....", "....lllll..lllll......", ".....lllGGGGlll.......", "......GGGGGGGG........", ".....lllGGGGlll.......", "....lllll..lllll......", "...lllll....lllll.....", "....lll......lll......"],
    ][f]
    rows = ["", ""] + blades + ["..........kk..........", "..........kk..........", "..........kk..........", "......kkkkkkkkkk......", "......kGGGGGGGGk......", "......kkkkkkkkkk......"]
    return rows
CAKE = [
    "",
    "..........y...........",
    ".........kyk..........",
    ".........kkk..........",
    "...kkkkkkkkkkkkkkk....",
    "..kmmmmmmmmmmmmmmmk...",
    "..kmmwmmmwmmmwmmmmk...",
    "..kmmmmmmmmmmmmmmmk...",
    "..kwwwwwwwwwwwwwwwk...",
    "..kcccccccccccccccck..",
    "..kcccccccccccccccck..",
    "..kwwwwwwwwwwwwwwwwk..",
    "..kcccccccccccccccck..",
    "..kcccccccccccccccck..",
    "..kkkkkkkkkkkkkkkkkk..",
    ".kppppppppppppppppppk.",
    ".kkkkkkkkkkkkkkkkkkkk.",
]
def rainscene(f):
    rows = storm(False)
    drops = [((4, 11), (9, 13), (14, 11), (7, 16), (12, 18), (17, 15)), ((5, 13), (10, 15), (15, 13), (8, 18), (13, 20), (18, 17))][f]
    for x, y in drops: rows = place(grid(rows), ["l", "l"], x, y)
    return rows
def snowscene(f):
    rows = list(EMPTY)
    flakes = [((3, 3), (9, 6), (15, 2), (6, 11), (12, 13), (18, 9), (4, 17), (14, 18)), ((4, 5), (10, 8), (16, 4), (7, 13), (13, 15), (19, 11), (5, 18), (15, 18))][f]
    for x, y in flakes: rows = place(rows, [".w.", "www", ".w."], x, y)
    return rows
def sun(f):
    rows = ["", "", "..........y...........", ".....y....y....y......", "......y..yyy..y.......", "........yyyyy.........", ".......yyyyyyy........", "..yy..yyyyyyyyy..yy...", "......yyyyyyyyy.......", "......yyyyyyyyy.......", ".......yyyyyyy........", "........yyyyy.........", "......y..yyy..y.......", ".....y....y....y......", "..........y..........."]
    return rows if f == 0 else [r.replace("y", "Y", 1) if i in (3, 13) else r for i, r in enumerate(rows)]
OUTLOOK = [
    "", "",
    "....uuuuuuuuuuuuuu....",
    "...uuuuuuuuuuuuuuuu...",
    "..uuuuuuuuuuuuuuuuuu..",
    "..uuuuuuuwwwwwwwwwuu..",
    "..uuwwwwwwwwwwwwwwuu..",
    "..uwwwwwwwwwwwwwwwwu..",
    "..uwwuuuuwwwwwwwwwwu..",
    "..uwwuuuuwuuuuuuuuwu..",
    "..uwwuuuuwwwwwwwwwwu..",
    "..uwwuuuuwwwwwwwwwwu..",
    "..uwwwwwwwwwwwwwwwwu..",
    "..uuwwwwwwwwwwwwwwuu..",
    "..uuuuuuuuuuuuuuuuuu..",
    "..uuuuuuuuuuuuuuuuuu..",
    "...uuuuuuuuuuuuuuuu...",
    "....uuuuuuuuuuuuuu....",
]
PAL["u"] = (0, 114, 198)  # 아웃룩 파랑
PROPS.update({
    "rain": [(img(UMBRELLA), 10)],
    "snow": [(img(SNOWMAN), 10)],
    "hot": [(img(fan(0)), 1), (img(fan(1)), 1)],
    "birthday": [(img(CAKE), 6), (shift(img(CAKE), dy=-1), 2)],
})
SCENES.update({
    "rain": [(img(rainscene(0)), 3), (img(rainscene(1)), 3)],
    "snow": [(img(snowscene(0)), 4), (img(snowscene(1)), 4)],
    "hot": [(img(sun(0)), 5), (img(sun(1)), 5)],
    "birthday": SCENES["done"],
})
LOGOS["outlook"] = img(OUTLOOK)

# ---------- 4차: 물 마시기 ----------
WATER = [
    "", "",
    "........kkkkkk........",
    "........kuuuuk........",
    "........kkkkkk........",
    ".......kwwwwwwk.......",
    "......kwwwwwwwwk......",
    "......kwwwwwwwwk......",
    "......kwwllllwwk......",
    "......kwllllllwk......",
    "......kwllllllwk......",
    "......kwllllllwk......",
    "......kwllllllwk......",
    "......kwllllllwk......",
    "......kwwllllwwk......",
    "......kwwwwwwwwk......",
    ".......kkkkkkkk.......",
]
PROPS["water"] = [(img(WATER), 6), (shift(img(WATER), dy=-1), 2)]
SCENES["water"] = SCENES["idle"]

# ---------- 5차: 클릭 반응·기상 ----------
PROPS.update({
    "grumpy": [(img(CLOUD), 10)],
    "sprint": [(img(dots(i)), 1) for i in range(3)],
    "pet_meeting": [(img(HEART), 3), (shift(img(HEART), dy=-1), 3)],
    "dizzy": [(img(confetti(0)), 2), (img(confetti(1)), 2)],
    "wake": [(img(sun(0)), 5), (img(sun(1)), 5)],
})
SCENES.update({"grumpy": SCENES["sleep"], "sprint": SCENES["working"], "pet_meeting": SCENES["meeting"], "dizzy": SCENES["faint"], "wake": SCENES["idle"]})

# ---------- 6차: 계절 ----------
GIFT = [
    "", "", "",
    "........yy..yy........",
    ".......y..yy..y.......",
    "...kkkkkkkkyykkkkkk...",
    "..krrrrrrrryyrrrrrrk..",
    "..krrrrrrrryyrrrrrrk..",
    "..kyyyyyyyyyyyyyyyyk..",
    "..kkkkkkkkkkkkkkkkkk..",
    "...krrrrrrryyrrrrrk...",
    "...krrrrrrryyrrrrrk...",
    "...krrrrrrryyrrrrrk...",
    "...krrrrrrryyrrrrrk...",
    "...krrrrrrryyrrrrrk...",
    "...krrrrrrryyrrrrrk...",
    "...kkkkkkkkkkkkkkkk...",
]
JACK = [
    "", "",
    "..........vv..........",
    ".........kvvk.........",
    "......kkkkkkkkkk......",
    "....kkooooooooookk....",
    "...koooooooooooooook..",
    "..koooooooooooooooook.",
    "..kookkooooooookkook..",
    "..koookkoooooookkoook.",
    "..koooooooookoooooook.",
    "..kooooooookkkooooook.",
    "..koooooooooooooooook.",
    "..kookkkkkkkkkkkkkook.",
    "...koookkoookkoooook..",
    "....kooooooooooook....",
    ".....kkkkkkkkkkkk.....",
]
POUCH = [
    "", "",
    "........yy..yy........",
    ".........yyyy.........",
    "........kkkkkk........",
    ".......krrrrrrk.......",
    "......kmrrrrrrmk......",
    ".....kmmrrrrrrmmk.....",
    "....kmmmrrrrrrmmmk....",
    "...kmmmmrryyrrmmmmk...",
    "...kmmmmryyyyrmmmmk...",
    "...kmmmmrryyrrmmmmk...",
    "...kmmmmrrrrrrmmmmk...",
    "....kmmmmrrrrmmmmk....",
    ".....kmmmmmmmmmmk.....",
    "......kkkkkkkkkk......",
]
SONGPYEON = [
    "", "", "", "", "",
    "......kkkk............",
    ".....kwwwwk...kkkk....",
    "....kwwwwwwk.kvvvvk...",
    "...kwwwwwwwwkvvvvvvk..",
    "...kkkkkkkkkkkkkkkkk..",
    "........kkkk..........",
    ".......kppppk.........",
    "......kppppppk........",
    ".....kppppppppk.......",
    "..kkkkkkkkkkkkkkkkkk..",
    ".kwwwwwwwwwwwwwwwwwwk.",
    "..kkkkkkkkkkkkkkkkkk..",
]
TREE = [
    "",
    "..........t...........",
    ".........ttt..........",
    "..........v...........",
    ".........vvv..........",
    "........vvrvv.........",
    ".......vvvvvvv........",
    "......vvyvvvvvv.......",
    ".......vvvvvvv........",
    "......vvvvvrvvv.......",
    ".....vvrvvvvvvvv......",
    "....vvvvvvvyvvvvv.....",
    "...vvvvyvvvvvvvvvv....",
    "..vvvvvvvvvrvvvvvvv...",
    "..........nn..........",
    "..........nn..........",
    ".........kkkk.........",
]
FULLMOON = [
    "", "",
    ".......yyyyyyyy.......",
    ".....yyyyyyyyyyyy.....",
    "....yyyyyyyyyyyyyy....",
    "...yyyyyyyyyyyyyyyy...",
    "..yyyyyyyyyyyyyyyyyy..",
    "..yyyyyyyyyyyyyyyyyy..",
    "..yyyyyYyyyyyyyyyyyy..",
    "..yyyyYYYyyyyyyYyyyy..",
    "..yyyyyYyyyyyyYYYyyy..",
    "..yyyyyyyyyyyyyYyyyy..",
    "..yyyyyyyyyyyyyyyyyy..",
    "...yyyyyyyyyyyyyyyy...",
    "....yyyyyyyyyyyyyy....",
    ".....yyyyyyyyyyyy.....",
    ".......yyyyyyyy.......",
]
PROPS.update({"xmas": [(img(GIFT), 10)], "halloween": [(img(JACK), 8), (shift(img(JACK), dy=-1), 2)], "seollal": [(img(POUCH), 8), (shift(img(POUCH), dy=-1), 2)], "chuseok": [(img(SONGPYEON), 10)]})
SCENES.update({"xmas": [(img(TREE), 6), (img([r.replace("t", "Y", 1) for r in TREE]), 3)], "halloween": SCENES["sleep"], "seollal": SCENES["done"], "chuseok": [(img(FULLMOON), 10)]})

# ---------- 7차: 여름 ----------
BEACHBALL = [
    "", "", "",
    ".......kkkkkkkk.......",
    ".....kkwwwwrrrrkk.....",
    "....kwwwwwwrrrrrrk....",
    "...kwwwwwwwrrrrrrrk...",
    "...kuuuuwwwrrryyyyk...",
    "..kuuuuuuwwryyyyyyyk..",
    "..kuuuuuuuwyyyyyyyyk..",
    "..kuuuuuuuwyyyyyyyyk..",
    "..kuuuuuuwwryyyyyyyk..",
    "...kvvvvvwwrrrmmmmk...",
    "...kvvvvvvwrrmmmmmk...",
    "....kvvvvvwrrmmmmk....",
    ".....kkvvvwrrmkk......",
    ".......kkkkkkkk.......",
]
SEA = [
    "",
    "...............yyy....",
    "..............yyyyy...",
    "..............yyyyy...",
    "...............yyy....",
    "", "", "",
    "......................",
    "..lllllllllllllllllll.",
    ".llllllllllllllllllll.",
    "wwlllwwllllwwlllwwllll",
    "llllllllllllllllllllll",
    "lllwwllllwwllllwwlllll",
    "llllllllllllllllllllll",
    "llllllllllllllllllllll",
    "llllllllllllllllllllll",
]
PROPS["summer"] = [(img(BEACHBALL), 6), (shift(img(BEACHBALL), dy=-1), 2)]
SCENES["summer"] = [(img(SEA), 6), (img([r.replace("ww", "lw", 1) if "ww" in r else r for r in SEA]), 6)]

# ---------- 8차: 집중 세션 (토마토) ----------
TOMATO = [
    "", "",
    "..........vv..........",
    ".......vvvvvvvv.......",
    "........kkvvkk........",
    "......kkrrrrrrkk......",
    ".....krrrrrrrrrrk.....",
    "....krrRRrrrrrrrrk....",
    "...krrRRrrrrrrrrrrk...",
    "...krrRrrrrrrrrrrrk...",
    "...krrrrrrrrrrrrrrk...",
    "...krrrrrrrrrrrrrrk...",
    "...krrrrrrrrrrrrrrk...",
    "....krrrrrrrrrrrrk....",
    ".....krrrrrrrrrrk.....",
    "......kkrrrrrrkk......",
    "........kkkkkk........",
]
PROPS["focus"] = [(img(TOMATO), 10)]
SCENES["focus"] = [(img(TOMATO), 8), (shift(img(TOMATO), dy=-1), 2)]

for k in ("idle_groom", "idle_cheeks", "idle_roll", "idle_peek"): PROPS[k] = PROPS["idle"]; SCENES[k] = SCENES["idle"]

# ---------- 9차: 볼주머니(클립보드) ----------
CLIPBOARD = [
    "", "",
    "........kkkkkk........",
    "....kkkkkGGGGkkkkk....",
    "...kccccckkkkccccck...",
    "...kcccccccccccccck...",
    "...kcckkkkkkkkkkcck...",
    "...kcccccccccccccck...",
    "...kcckkkkkkkkkkcck...",
    "...kcccccccccccccck...",
    "...kcckkkkkkkcccccck..",
    "...kcccccccccccccck...",
    "...kcckkkkkkkkkkcck...",
    "...kcccccccccccccck...",
    "...kcccccccccccccck...",
    "...kkkkkkkkkkkkkkkk...",
]
PROPS["stash"] = [(img(CLIPBOARD), 4), (shift(img(CLIPBOARD), dy=-1), 2)]
SCENES["stash"] = SCENES["idle"]

PROPS["typing"] = PROPS["idle"]; SCENES["typing"] = SCENES["idle"]

PROPS["update"] = PROPS["xmas"]; SCENES["update"] = SCENES["done"]
