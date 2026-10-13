# 노치 모드 32px 전용 소품·장면 (음영 포함). 문자 격자, 32x32.
from PIL import Image
from props import PAL as PAL22, shift
N = 32
PAL = dict(PAL22); PAL.update({
    "K": (58, 42, 30),        # 따뜻한 외곽선
    "h": (255, 240, 200),     # 하이라이트
    "O": (200, 110, 40),      # 주황 그림자
    "x": (215, 215, 212), "X": (150, 150, 148),  # 밝은/어두운 회색
    "q": (255, 225, 120), "Q": (210, 150, 30),   # 노랑 밝/어둠
    "i": (255, 120, 110), "I": (160, 35, 30),    # 빨강 밝/어둠
    "j": (255, 200, 210), "J": (190, 60, 90),    # 분홍 밝/어둠
    "f": (120, 210, 140), "F": (60, 150, 90),    # 초록 밝/어둠
    "n": (120, 80, 45), "N": (80, 50, 25),       # 갈색 밝/어둠
    "s": (90, 70, 55),
    "r": (240, 100, 95), "m": (236, 100, 140), "y": (255, 214, 110), "v": (120, 200, 150), "u": (120, 200, 240), "p": (250, 175, 190), "o": (245, 165, 90),
    "l": (170, 215, 245), "z": (150, 170, 230), "g": (190, 190, 188), "G": (110, 110, 108), "a": (52, 52, 66),
})
def grid(rows):
    out = []
    for r in rows:
        assert len(r) <= N, (len(r), r); out.append(r.ljust(N, "."))
    while len(out) < N: out.append("." * N)
    return out[:N]
def img(rows):
    g = grid(rows); im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = im.load()
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch != ".": px[x, y] = PAL[ch] + (255,)
    return im

BOWL = [
    "", "", "", "", "", "", "", "",
    "...........s..ss..s.............",
    ".........ssKssKssKsss...........",
    ".......sKsssKsssKsssKss.........",
    "......KssKssssKsssKssKsK........",
    "....KKKKKKKKKKKKKKKKKKKKKK......",
    "...KjjjjjjjjjjjjjjjjjjjjjjK.....",
    "...KjhhjjjjjjjjjjjjjjjjjjjK.....",
    "...KjjjjjjjjjjjjjjjjjjjjjjK.....",
    "....KJJJJJJJJJJJJJJJJJJJJK......",
    "....KjjjjjjjjjjjjjjjjjjjjK......",
    ".....KjjjjjjjjjjjjjjjjjjK.......",
    "......KJJJJJJJJJJJJJJJJK........",
    ".......KKKKKKKKKKKKKKKK.........",
]
SIREN = [
    "", "",
    "..............KKKK..............",
    "............KKiiiiKK............",
    "...........KiihhrrriK...........",
    "..........KiihhrrrrriK..........",
    ".........KihhrrrrrrrriK.........",
    ".........KirrrrrrrrrriK.........",
    "........KrrrrrrrrrrrrrrK........",
    "........KrrrrrrrrrrrrIrK........",
    "........KrrrrrrrrrrrrIIK........",
    "........KrrrrrrrrrrrIIIK........",
    "........KIrrrrrrrrrIIIIK........",
    ".......KKKKKKKKKKKKKKKKKK.......",
    "......KxxxxxxxxxxxxxxxxxxK......",
    "......KXXXXXXXXXXXXXXXXXXK......",
    "......KxxxxxxxxxxxxxxxxxxK......",
    ".......KKKKKKKKKKKKKKKKKK.......",
]
def siren(on):
    rows = list(SIREN)
    if not on: rows = [r.replace("i", "I").replace("r", "I").replace("h", "I") for r in rows]
    else:
        rows = grid(rows)
        for x, y in ((4, 4), (27, 4), (2, 9), (29, 9), (6, 1), (25, 1), (15, 0), (16, 0)):
            r = list(rows[y]); r[x] = "i"; rows[y] = "".join(r)
    return rows
ENVELOPE = [
    "", "", "", "", "", "",
    "...KKKKKKKKKKKKKKKKKKKKKKKKK....",
    "...KhhhhhhhhhhhhhhhhhhhhhhhK....",
    "...KKhhhhhhhhhhhhhhhhhhhhhKK....",
    "...KwKhhhhhhhhhhhhhhhhhhhKwK....",
    "...KwwKhhhhhhhhhhhhhhhhhKwwK....",
    "...KwwwKhhhhhhhhhhhhhhhKwwwK....",
    "...KwwwwKhhhhhhhhhhhhhKwwwwK....",
    "...KwwwwwKhhhhhhhhhhhKwwwwwK....",
    "...KwwwwwwKhhhhhhhhhKwwwwwwK....",
    "...KwwwwwwwKhhhhhhhKwwwwwwwK....",
    "...KwwwwwwwwKhhhhhKwwwwwwwwK....",
    "...KwwwwwwwwwKmJmKwwwwwwwwwK....",
    "...KwwwwwwwwwjmmmjwwwwwwwwwK....",
    "...KwwwwwwwwwwJmJwwwwwwwwwwK....",
    "...KwwwwwwwwwwwJwwwwwwwwwwwK....",
    "...KxxxxxxxxxxxxxxxxxxxxxxxK....",
    "...KKKKKKKKKKKKKKKKKKKKKKKKK....",
]
CHECK_PATH = [(4 + i, 15 + i) for i in range(8)] + [(12 + i, 22 - i) for i in range(1, 16)]
def check(n, sparkle=False):
    rows = grid([])
    for i, (x, y) in enumerate(CHECK_PATH[:n]):
        for dx in range(3):
            for dy in range(3):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N:
                    r = list(rows[yy]); r[xx] = "L" if dy < 2 else "F"; rows[yy] = "".join(r)
    if sparkle:
        def diamond(cx, cy, r):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if abs(dx) + abs(dy) <= r:
                        x, y = cx + dx, cy + dy
                        if 0 <= x < N and 0 <= y < N:
                            rr = list(rows[y]); rr[x] = "h" if (dx, dy) == (0, 0) or abs(dx) + abs(dy) == 1 else ("q" if abs(dx) + abs(dy) < r else "Q"); rows[y] = "".join(rr)
        diamond(26, 5, 4); diamond(5, 9, 3); diamond(29, 14, 2); diamond(13, 4, 2)
    return rows
PAL["L"] = (140, 225, 150)
def zzz():
    rows = grid([])
    def Z(x0, y0, w, h):
        for i in range(w): put(x0 + i, y0); put(x0 + i, y0 + h - 1)
        for i in range(1, h - 1): put(x0 + w - 1 - (i * (w - 1)) // (h - 1), y0 + i)
    def put(x, y):
        if 0 <= x < N and 0 <= y < N: r = list(rows[y]); r[x] = "z"; rows[y] = "".join(r)
    Z(21, 1, 8, 7); Z(12, 10, 6, 6); Z(5, 18, 4, 4)
    return rows
HEART = [
    "", "", "", "", "",
    ".....mmmmm.........mmmmm........",
    "....mjjmmmm.......mmmmmmm.......",
    "...mjhjmmmmm.....mmmmmmmmm......",
    "...mjjmmmmmmm...mmmmmmmmmmm.....",
    "...mmmmmmmmmmm.mmmmmmmmmmmm.....",
    "...mmmmmmmmmmmmmmmmmmmmmmmJ.....",
    "...mmmmmmmmmmmmmmmmmmmmmmmJ.....",
    "....mmmmmmmmmmmmmmmmmmmmmJ......",
    ".....mmmmmmmmmmmmmmmmmmmJJ......",
    "......mmmmmmmmmmmmmmmmmJJ.......",
    ".......mmmmmmmmmmmmmmmJJ........",
    "........mmmmmmmmmmmmmJJ.........",
    ".........mmmmmmmmmmmJJ..........",
    "..........mmmmmmmmmJJ...........",
    "...........mmmmmmmJJ............",
    "............mmmmmJJ.............",
    ".............mmmJJ..............",
    "..............mJ................",
]
def coffee(steam):
    rows = [
        "........x....x....x.............",
        ".........x....x....x............",
        "........x....x....x.............",
        ".........x....x....x............",
        "", "",
        ".....KKKKKKKKKKKKKKKK...........",
        ".....KhhhhhhhhhhhhhhKKKK........",
        ".....KhnnnnnnnnnnnnhKxxxK.......",
        ".....KhnNnnnnnnnnnnhKxhxxK......",
        ".....KhnnnnnnnnnnnnhKxhxxK......",
        ".....KhnnnnnnnnnnnnhKxxxxK......",
        ".....KhnnnnnnnnnnnnhKxxxK.......",
        ".....KhnnnnnnnnnnnnhKKKK........",
        "......KhnnnnnnnnnnhK............",
        "......KhhnnnnnnnnhhK............",
        ".......KhhhhhhhhhhK.............",
        "........KKKKKKKKKK..............",
        ".....KKKKKKKKKKKKKKKK...........",
        "....KxxxxxxxxxxxxxxxxK..........",
        ".....KKKKKKKKKKKKKKKK...........",
    ]
    return rows if steam else [""] * 4 + rows[4:]
def clock(f):
    rows = [
        "", "",
        ".......KKK..........KKK.........",
        "......KiiiK........KiiiK........",
        ".......KKKKKKKKKKKKKKKK.........",
        "..........KKKhhhhKKK............",
        "........KKhhhhhhhhhhKK..........",
        ".......KhhhhhhhhhhhhhhK.........",
        "......KhhhhhhhKhhhhhhhhK........",
        "......KhhhhhhhKhhhhhhhhK........",
        ".....KhhhhhhhhKhhhhhhhhhK.......",
        ".....KhhhhhhhhKhhhhhhhhhK.......",
        ".....KhhhhhhhhKKKKhhhhhhK.......",
        ".....KhhhhhhhhhhhhhhhhhhK.......",
        ".....KxhhhhhhhhhhhhhhhhhK.......",
        "......KxhhhhhhhhhhhhhhhK........",
        "......KxxhhhhhhhhhhhhhxK........",
        ".......KxxxhhhhhhhhhxxK.........",
        "........KKxxxxxxxxxxKK..........",
        "..........KKKKKKKKKK............",
        "........KKK........KKK..........",
    ]
    return rows if f == 0 else [r.replace("iii", "hii") for r in rows]
HOUSE = [
    "", "",
    "...............KK...............",
    "..............KjjK..............",
    ".............KjjjjK.............",
    "............KjjjjjjK............",
    "...........KjjjjjjjjK...........",
    "..........KjjjjjjjjjjK..........",
    ".........KjjjjjjjjjjjjK.........",
    "........KjjjjjjjjjjjjjjK........",
    ".......KjjjjjjjjjjjjjjjjK.......",
    "......KJJJJJJJJJJJJJJJJJJK......",
    "......KKKKKKKKKKKKKKKKKKKK......",
    "......KcccccccccccccccccccK.....",
    "......KccKKKKKccccccKKKKccK.....",
    "......KccKllhKccccccKnnKccK.....",
    "......KccKlllKccccccKnnKccK.....",
    "......KccKKKKKccccccKnNKccK.....",
    "......KcccccccccccccKnnKccK.....",
    "......KcccccccccccccKnnKccK.....",
    "......KKKKKKKKKKKKKKKKKKKKK.....",
]
def window(cursor):
    rows = [
        "", "", "", "",
        "..KKKKKKKKKKKKKKKKKKKKKKKKKKK...",
        "..KGGGGGGGGGGGGGGGGGGGGGGGGGK...",
        "..KGrGyGvGGGGGGGGGGGGGGGGGGGK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KaauuuuuuaaaeeeeeeeeeaaaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KaaaavvvvvvvvvaaaammmmmaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KaaaauuuaaaeeeeeeaaaaaaaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KaaaavvvvvvvvvvvvvvaaaaaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KaaaauuuuaaaammmmmmmaaaaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..Kaaaa" + ("ww" if cursor else "aa") + "aaaaaaaaaaaaaaaaaaaK...",
        "..KaaaaaaaaaaaaaaaaaaaaaaaaaK...",
        "..KKKKKKKKKKKKKKKKKKKKKKKKKKK...",
    ]
    return rows
def dots(up):
    rows = grid([])
    for i, x in enumerate((3, 12, 21)):
        y = 12 if i == up else 16
        for j, r in enumerate([".xxxx.", "xhhxxx", "xhxxxx", "xxxxxX", ".xxXX."]):
            for k, ch in enumerate(r):
                if ch != ".": rr = list(rows[y + j]); rr[x + k] = ch; rows[y + j] = "".join(rr)
    return rows

SOUL = [
    "", "",
    "..........KKKKKKKKKK............",
    "........KKwwwwwwwwwwKK..........",
    ".......KwwwwwwwwwwwwwwK.........",
    "......KwwwwwwwwwwwwwwwwK........",
    "......KwwwKKwwwwwwKKwwwK........",
    "......KwwwKKwwwwwwKKwwwK........",
    "......KwwwwwwwwwwwwwwwwK........",
    "......KwwwwwwwKKKwwwwwwK........",
    "......KwwwwwwwwwwwwwwwwK........",
    "......KwwwwwwwwwwwwwwwwK........",
    "......KwwwwwwwwwwwwwwwwK........",
    "......KxwwwwwwwwwwwwwwxK........",
    "......KxxwwwwwwwwwwwwxxK........",
    "......KxxxwwwwwwwwwwxxxK........",
    "......KxxKKxxxKKxxxKKxxK........",
    "......KxK..KxK..KxK..KxK........",
    "......KK....KK....KK....KK......",
]
def battery(level, charging):
    fill = "v" if charging else "r"; dark = "F" if charging else "I"
    rows = ["", "", "", "", "", "", "", "",
        "....KKKKKKKKKKKKKKKKKKKK........",
        "...KhhhhhhhhhhhhhhhhhhhhKK......",
        "...KhwwwwwwwwwwwwwwwwwwhKxK.....",
    ]
    for i in range(6):
        rows.append("...Khw" + fill * level + "w" * (16 - level) + "whK" + ("xxK" if 1 <= i <= 4 else "KK.") + "....")
    rows += ["...KhwwwwwwwwwwwwwwwwwwhKxK.....", "...KxxxxxxxxxxxxxxxxxxxxKK......", "....KKKKKKKKKKKKKKKKKKKK........"]
    rows = grid(rows)
    for i in range(6):
        y = 11 + i; r = list(rows[y])
        for x in range(6, 6 + level): r[x] = dark if i == 5 else fill
        rows[y] = "".join(r)
    if charging:
        for x, y in ((14, 10), (15, 10), (13, 11), (14, 11), (12, 12), (13, 12), (14, 12), (15, 12), (16, 12), (14, 13), (15, 13), (13, 14), (14, 14), (12, 15), (13, 15)):
            r = list(rows[y]); r[x] = "q"; rows[y] = "".join(r)
    return rows
def fire(f):
    rows = [
        "", "",
        "...............r................",
        "..............rr................",
        ".............rrr......r.........",
        "............rrrr.....rr.........",
        "...........rrrrr....rrr.........",
        "..........rrrrrr...rrrr.........",
        ".........rrrrrrrr.rrrrr.........",
        "........rrrrrrrrrrrrrrr.........",
        ".......rrrrrooorrrrrrrrr........",
        "......rrrrrooooorrrrrrrr........",
        "......rrrrooooooorrrrrrr........",
        ".....rrrrooooooooorrrrrr........",
        ".....rrrroooqqqoooorrrrr........",
        ".....rrrooqqqqqqqooorrrr........",
        ".....rrrooqqqhqqqooorrrr........",
        "......rrooqqqhqqqooorrr.........",
        "......rrrooqqqqqooorrrr.........",
        ".......rrroooqqoooorrr..........",
        "........rrrooooooorrr...........",
        ".........rrrrooorrrr............",
        "...........rrrrrrr..............",
    ]
    return rows if f == 0 else [""] + rows[:-1]
BENTO = [
    "", "", "", "", "",
    "....KKKKKKKKKKKKKKKKKKKKKK......",
    "...KjjjjjjjjjjjjjjjjjjjjjjK.....",
    "...KjhhjjjjjjjjjjjjjjjjjjjK.....",
    "...KJJJJJJJJJJJJJJJJJJJJJJK.....",
    "...KKKKKKKKKKKKKKKKKKKKKKKK.....",
    "...KhhhhhhhhhKhhhhhhhhhhhhK.....",
    "...KhhhhhhhhhKhhoooooohhhhK.....",
    "...KhhwwwhhhhKhhoOoOoohhhhK.....",
    "...KhhwwwhhhhKhhoooooohhhhK.....",
    "...KhhhhhhhhhKhhhhhhhhhhhhK.....",
    "...KKKKKKKKKKKhhrrhhhrrhhhK.....",
    "...KhfffffhhhKhhrIhhhrIhhhK.....",
    "...KhfFfFfhhhKhhhhhhhhhhhhK.....",
    "...KhfffffhhhKhhhhhhhhhhhhK.....",
    "...KhhhhhhhhhKhhhhhhhhhhhhK.....",
    "...KKKKKKKKKKKKKKKKKKKKKKKK.....",
]
BAG = [
    "", "",
    "............KKKKKKK.............",
    "...........KK.....KK............",
    "...........K.......K............",
    "...........K.......K............",
    ".....KKKKKKKKKKKKKKKKKKKKK......",
    "....KnnnnnnnnnnnnnnnnnnnnnK.....",
    "....KnhhnnnnnnnnnnnnnnnnnnK.....",
    "....KnnnnnnnnnnnnnnnnnnnnnK.....",
    "....KnnnnnKKKKKKKKKKnnnnnnK.....",
    "....KnnnnnKssssssssKnnnnnnK.....",
    "....KnnnnnKsqqssssSKnnnnnnK.....",
    "....KnnnnnKssssssssKnnnnnnK.....",
    "....KnnnnnKKKKKKKKKKnnnnnnK.....",
    "....KnnnnnnnnnnnnnnnnnnnnnK.....",
    "....KnnnnnnnnnnnnnnnnnnnnnK.....",
    "....KNNNNNNNNNNNNNNNNNNNNNK.....",
    ".....KKKKKKKKKKKKKKKKKKKKK......",
]
PAL["S"] = (60, 45, 35)
WATER = [
    "", "",
    "............KKKKKKKK............",
    "............KuuuuuuK............",
    "............KUUUUUUK............",
    "............KKKKKKKK............",
    "...........KhhhhhhhhK...........",
    "..........KhhhhhhhhhhK..........",
    ".........KhhhhhhhhhhhhK.........",
    ".........KhwhhhhhhhhhhK.........",
    ".........KhwhlllllllhhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhwlllllllllhK.........",
    ".........KhhlllllllllhK.........",
    "..........KhhlllllllhK..........",
    "...........KhhhhhhhhK...........",
    "............KKKKKKKK............",
]
PAL["U"] = (70, 150, 200)
POMPOM = [
    "", "",
    ".........q....q....q............",
    "........qqq..qqq..qqq...........",
    ".......qqqqqqqqqqqqqqq..........",
    "......qqqqqqqqqqqqqqqqq.........",
    ".....qqqqhqqqqqqqqqqqqqq........",
    ".....qqhhhqqqqqqqqqqqqqq........",
    "....qqqqhqqqqqqqqqqqqqqqq.......",
    "....qqqqqqqqqqqqqqqqqqqQq.......",
    "....qqqqqqqqqqqqqqqqqqqQq.......",
    "....qqqqqqqqqqqqqqqqqqQQq.......",
    ".....qqqqqqqqqqqqqqqQQQQ........",
    ".....qqQqqqqqqqqqqqQQQQQ........",
    "......qqQQqqqqqqqQQQQQQ.........",
    ".......qqQQQQQQQQQQQQQ..........",
    "........qqqqQQQQQQQQQ...........",
    "..........KKKK..................",
    "..........KssK..................",
    "..........KssK..................",
    "..........KssK..................",
    "..........KssK..................",
    "..........KKKK..................",
]
PROPS32 = {
    "faint": [(img(SOUL), 5), (shift(img(SOUL), dy=-1), 5)],
    "battery_low": [(img(battery(3, False)), 5), (img(battery(0, False)), 3)],
    "charging": [(img(battery(6, True)), 3), (img(battery(11, True)), 3), (img(battery(16, True)), 3)],
    "cpu": [(img(fire(0)), 2), (img(fire(1)), 2)],
    "lunch": [(img(BENTO), 10)],
    "leave": [(img(BAG), 10)],
    "water": [(img(WATER), 6), (shift(img(WATER), dy=-1), 2)],
    "friday": [(img(POMPOM), 3), (shift(img(POMPOM), dx=-1), 3)],
    "idle": [(img(BOWL), 10)],
    "working": [(img(dots(i)), 2) for i in range(3)],
    "done": [(img(check(4)), 1), (img(check(9)), 1), (img(check(15)), 1), (img(check(23)), 1), (img(check(23, True)), 4), (img(check(23)), 2), (img(check(23, True)), 3), (img(check(23)), 9)],
    "surprised": [(img(siren(True)), 3), (img(siren(False)), 3)],
    "sleep": [(img(zzz()), 8), (shift(img(zzz()), dy=-1), 8)],
    "notify": [(img(ENVELOPE), 4), (shift(img(ENVELOPE), dy=-1), 4)],
    "pet": [(img(HEART), 3), (shift(img(HEART), dy=-1), 3)],
    "break": [(img(coffee(True)), 5), (img(coffee(False)), 5)],
    "meeting_soon": [(img(clock(0)), 2), (shift(img(clock(1)), dx=1), 1), (img(clock(0)), 2), (shift(img(clock(1)), dx=-1), 1)],
}
SCENES32 = {
    "idle": [(img(HOUSE), 10)],
    "working": [(img(window(True)), 4), (img(window(False)), 4)],
}

# ---------- 나머지 소품 ----------
CONFETTI_PTS = [((4, 5, "y"), (10, 3, "u"), (20, 6, "m"), (27, 11, "v"), (7, 16, "r"), (16, 14, "p"), (24, 21, "y"), (3, 24, "u"), (13, 26, "m"), (28, 3, "r"), (18, 23, "v"), (9, 9, "q")),
                ((5, 8, "u"), (13, 4, "y"), (22, 9, "v"), (27, 16, "m"), (9, 20, "p"), (18, 18, "r"), (25, 25, "u"), (4, 28, "y"), (14, 29, "v"), (29, 6, "m"), (20, 2, "q"), (11, 13, "r"))]
def confetti(f):
    rows = grid([])
    def put(x, y, ch):
        if 0 <= x < N and 0 <= y < N: r = list(rows[y]); r[x] = ch; rows[y] = "".join(r)
    for x, y, ch in CONFETTI_PTS[f]: put(x, y, ch); put(x + 1, y, ch)
    for cx, cy in [((8, 12), (21, 19))[f], ((22, 4), (7, 24))[f]]:
        for d in range(-2, 3): put(cx + d, cy, "h"); put(cx, cy + d, "h")
    return rows
SUN = ["", "", "...............q................", ".......q.......q.......q........", "........q.....qqq.....q.........", ".........q...qqqqq...q..........",
       "...........qqqqqqqqq............", "..........qqqqqqqqqqq...........", ".........qqqqhhqqqqqq...........", "...qqq...qqqqhqqqqqqq...qqq.....",
       ".........qqqqqqqqqqqq...........", ".........qqqqqqqqqqqq...........", "..........qqqqqqqqqqq...........", "...........qqqqqqqqq............",
       ".........q...qqqqq...q..........", "........q.....qqq.....q.........", ".......q.......q.......q........", "...............q................"]
def sun(f): return SUN if f == 0 else [r.replace("q", "Q", 1) if i in (3, 15) else r for i, r in enumerate(SUN)]
CLOUD = ["", "", "", "", "............xxxxxx..............", "..........xxxxxxxxxx............", "........xxxxxxxxxxxxxx..........", "......xxxxxxxxxxxxxxxxxx........",
         ".....xxxxxxxxxxxxxxxxxxxx.......", "....xxxxxxxxxxxxxxxxxxxxxx......", "....xxxxxxxxxxxxxxxxxxxxxx......", ".....XXXXXXXXXXXXXXXXXXXX.......",
         "", ".......l....l....l....l.........", "........l....l....l....l........", ".........l....l....l....l.......", "..........l....l....l....l......"]
MIC = ["", "", "............KKKKKKKK............", "...........KGGGGGGGGK...........", "..........KGggGggGggGK..........", "..........KGggGggGggGK..........",
       "..........KGggGggGggGK..........", "..........KGggGggGggGK..........", "..........KGggGggGggGK..........", "..........KGggGggGggGK..........",
       "..........KGGGGGGGGGGK..........", "......KK..KGGGGGGGGGGK..KK......", "......K...KKKKKKKKKKKK...K......", "......KK................KK......",
       ".......KK..............KK.......", "........KKK..........KKK........", "..........KKKKKKKKKKKK..........", "...............KK...............",
       "...............KK...............", "...............KK...............", "...........KKKKKKKKKK...........", "...........KXXXXXXXXK...........", "...........KKKKKKKKKK..........."]
CALENDAR = ["", "", ".......K.......K.......K........", "....KKKKKKKKKKKKKKKKKKKKKKK.....", "....KrrrrrrrrrrrrrrrrrrrrrK.....", "....KrrrrrrrrrrrrrrrrrrrrrK.....",
            "....KIIIIIIIIIIIIIIIIIIIIIK.....", "....KKKKKKKKKKKKKKKKKKKKKKK.....", "....KhhhhhhhhhhhhhhhhhhhhhK.....", "....KhKKhhKKhhKKhhKKhhKKhK.....",
            "....KhhhhhhhhhhhhhhhhhhhhhK.....", "....KhKKhhKKhhrrhhKKhhKKhK.....", "....KhhhhhhhhhrrhhhhhhhhhhK.....", "....KhKKhhKKhhKKhhKKhhKKhK.....",
            "....KhhhhhhhhhhhhhhhhhhhhhK.....", "....KhKKhhKKhhKKhhKKhhKKhK.....", "....KhhhhhhhhhhhhhhhhhhhhhK.....", "....KKKKKKKKKKKKKKKKKKKKKKK....."]
UMBRELLA = ["", "", "...............K................", "...........KKKKKKKKK............", ".........KKmmmmmmmmmKK..........", "........KmmmmmmmmmmmmmK.........",
            ".......KmmmhmmmmmmhmmmmK........", "......KmmmmhmmmmmmhmmmmmK.......", ".....KmmmmmmmmmmmmmmmmmmmK......", "....KmmJmmmmmJmmmmmJmmmmmmK.....",
            "....KKKKKKKKKKKKKKKKKKKKKKK.....", "...............KK...............", "...............KK...............", "...............KK...............",
            "...............KK...............", "...............KK...............", "...............KK...............", "...........K...KK...............",
            "...........KK.KK................", "............KKK................."]
SNOWMAN = ["", "...........KKKKKKKK.............", "...........KaaaaaaK.............", "..........KKKKKKKKKK............", ".........KhhhhhhhhhhK...........",
           "........KhhhKhhhhKhhhK..........", "........KhhhhhhhhhhhhK..........", "........KhhhhhoooohhhK..........", "........KhhhhhhhhhhhhK..........",
           ".........KhhhhhhhhhhK...........", "......KKKKKKKhhhhKKKKKKK........", ".....KrrrrrrrKhhKrrrrrrrK.......", "......KKKKKKKhhhhKKKKKKK........",
           ".......KhhhhhhhhhhhhhhK.........", "......KhhhhhhhKKhhhhhhhK........", ".....KhhhhhhhhhhhhhhhhhhK.......", ".....KhhhhhhhhKKhhhhhhhhK.......",
           ".....KhhhhhhhhhhhhhhhhhhK.......", ".....KxhhhhhhhhhhhhhhhhxK.......", "......KxxhhhhhhhhhhhhxxK........", ".......KKKKKKKKKKKKKKKK........."]
def fan(f):
    blades = [["..............lll...............", ".............lllll..............", "............lllllll.............", "...........lllllllll............",
               ".........llllllGGllllll.........", "........lllllGGGGGGlllll........", ".........llllllGGllllll.........", "...........lllllllll............",
               "............lllllll.............", ".............lllll..............", "..............lll..............."],
              ["......llll..........llll........", ".....llllll........llllll.......", "......llllll......llllll........", ".......llllllGGGGllllll.........",
               "........lllGGGGGGGGlll..........", ".........GGGGGGGGGGGG...........", "........lllGGGGGGGGlll..........", ".......llllllGGGGllllll.........",
               "......llllll......llllll........", ".....llllll........llllll.......", "......llll..........llll........"]][f]
    return [""] * 3 + blades + ["...............KK...............", "...............KK...............", "...............KK...............",
                                "..........KKKKKKKKKKKK..........", "..........KXXXXXXXXXXK..........", "..........KKKKKKKKKKKK.........."]
CAKE = ["", "...............q................", "..............KqK...............", "..............KhK...............", "..............KKK...............",
        ".....KKKKKKKKKKKKKKKKKKKKKK.....", "....KmmmmmmmmmmmmmmmmmmmmmmK....", "....KmmhmmmhmmmhmmmhmmmhmmmK....", "....KmmmmmmmmmmmmmmmmmmmmmmK....",
        "....KJJJJJJJJJJJJJJJJJJJJJJK....", "....KhhhhhhhhhhhhhhhhhhhhhhK....", "....KccccccccccccccccccccccK....", "....KccccccccccccccccccccccK....",
        "....KhhhhhhhhhhhhhhhhhhhhhhK....", "....KccccccccccccccccccccccK....", "....KccccccccccccccccccccccK....", "....KKKKKKKKKKKKKKKKKKKKKKKK....",
        "...KjjjjjjjjjjjjjjjjjjjjjjjjK...", "...KJJJJJJJJJJJJJJJJJJJJJJJJK...", "....KKKKKKKKKKKKKKKKKKKKKKKK...."]
GIFT = ["", "", "", "...........qq.....qq............", "..........q..q...q..q...........", "...........q..qqq..q............",
        "....KKKKKKKKKKKqqKKKKKKKKKK.....", "...KrrrrrrrrrrrqqrrrrrrrrrrK....", "...KrhrrrrrrrrrqqrrrrrrrrrrK....", "...KqqqqqqqqqqqqqqqqqqqqqqqK....",
        "...KQQQQQQQQQQQQQQQQQQQQQQQK....", "...KKKKKKKKKKKKKKKKKKKKKKKKK....", "....KrrrrrrrrrrqqrrrrrrrrrK.....", "....KrrrrrrrrrrqqrrrrrrrrrK.....",
        "....KrrrrrrrrrrqqrrrrrrrrrK.....", "....KrrrrrrrrrrqqrrrrrrrrrK.....", "....KrrrrrrrrrrqqrrrrrrrrrK.....", "....KrrrrrrrrrrqqrrrrrrrrrK.....",
        "....KIIIIIIIIIIqqIIIIIIIIIK.....", "....KKKKKKKKKKKKKKKKKKKKKKK....."]
JACK = ["", "", "..............vv................", ".............KvvK...............", "........KKKKKKKKKKKKKKK.........", "......KKooooooooooooooKK........",
        ".....KooooooooooooooooooK.......", "....KooohoooooooooooooooK.......", "....KooohKKoooooooooKKooooK.....", "...KoooKKKKooooooooKKKKoooK.....",
        "...KooooooooooooooooooooooK.....", "...KoooooooooooKooooooooooK.....", "...KooooooooooKKKoooooooooK.....", "...KooooooooooooooooooooooK.....",
        "...KoooKKKKKKKKKKKKKKKoooK......", "....KoooooKKoooooKKoooooK.......", "....KOoooooooooooooooooOK.......", ".....KOOOooooooooooOOOK.........",
        "......KKOOOOOOOOOOOKK...........", "........KKKKKKKKKKK............."]
POUCH = ["", "...........qq....qq.............", "............qqqqqq..............", ".............KKKK...............", "...........KKrrrrKK.............",
         "..........KmrrrrrrmK............", ".........KmmrrrrrrmmK...........", "........KmmmrrrrrrmmmK..........", ".......KmmmmrrrrrrmmmmK.........",
         "......KmmmmmrrqqrrmmmmmK........", "......KmmmmmrqqqqrmmmmmK........", "......KmmmmmrqqqqrmmmmmK........", "......KmmmmmrrqqrrmmmmmK........",
         "......KmmmmmrrrrrrmmmmmK........", "......KmmmmmmrrrrmmmmmmK........", ".......KmmmmmmmmmmmmmmK.........", "........KJJJJJJJJJJJJK..........",
         ".........KKKKKKKKKKKK..........."]
SONGPYEON = ["", "", "", "", "", "", ".........KKKKK..................", "........KhhhhhK......KKKKK......", ".......KhhhhhhhK....KvvvvvK.....",
             "......KhhhhhhhhhK..KvvvvvvvK....", ".....KhhhhhhhhhhhKKvvvvvvvvvK...", "....KKKKKKKKKKKKKKKKKKKKKKKKK...", "............KKKKK...............",
             "...........KjjjjjK..............", "..........KjjjjjjjK.............", ".........KjjjjjjjjjK............", "........KjjjjjjjjjjjK...........",
             "...KKKKKKKKKKKKKKKKKKKKKKKKKK...", "..KhhhhhhhhhhhhhhhhhhhhhhhhhhK..", "..KxxxxxxxxxxxxxxxxxxxxxxxxxxK..", "...KKKKKKKKKKKKKKKKKKKKKKKKKK..."]
BEACHBALL = ["", "", "", "..........KKKKKKKKKK............", "........KKhhhhhrrrrrKK..........", ".......KhhhhhhhhrrrrrrK.........",
             "......KhhhhhhhhhrrrrrrrK........", ".....KuuuuhhhhhhrrrqqqqqK.......", "....KuuuuuuuhhhhrrqqqqqqqK......", "....KuuuuuuuuhhhrqqqqqqqqK......",
             "....KuuuuuuuuuhhqqqqqqqqqK......", "....KuuuuuuuuuhhqqqqqqqqqK......", "....KuuuuuuuuhhhrqqqqqqqqK......", ".....KvvvvvvvhhhrrmmmmmmK.......",
             ".....KvvvvvvvvhhrrmmmmmmK.......", "......KvvvvvvvhhrrmmmmmK........", ".......KvvvvvvhhrrmmmmK.........", "........KKvvvvhhrrmmKK..........",
             "..........KKKKKKKKKK............"]
CLIPBOARD = ["", "", "............KKKKKKKK............", "......KKKKKKKGGGGGGKKKKKKK......", ".....KcccccccKKKKKKcccccccK.....", ".....KccccccccccccccccccccK.....",
             ".....KcccKKKKKKKKKKKKKKcccK.....", ".....KccccccccccccccccccccK.....", ".....KcccKKKKKKKKKKKKKKcccK.....", ".....KccccccccccccccccccccK.....",
             ".....KcccKKKKKKKKKKcccccccK.....", ".....KccccccccccccccccccccK.....", ".....KcccKKKKKKKKKKKKKKcccK.....", ".....KccccccccccccccccccccK.....",
             ".....KcccKKKKKKKKKcccccccсK.....".replace("с", "c"), ".....KccccccccccccccccccccK.....", ".....KxxxxxxxxxxxxxxxxxxxxK.....", ".....KKKKKKKKKKKKKKKKKKKKKK....."]
TOMATO = ["", "", "...............vv...............", "...........vvvvvvvvvv...........", "............KKKvvKKK............", "..........KKrrrrrrrrKK..........",
          "........KKrrrrrrrrrrrrKK........", ".......KrrrhhrrrrrrrrrrrK.......", "......KrrrhhhrrrrrrrrrrrrK......", "......KrrrrhrrrrrrrrrrrrrK......",
          ".....KrrrrrrrrrrrrrrrrrrrrK.....", ".....KrrrrrrrrrrrrrrrrrrrrK.....", ".....KrrrrrrrrrrrrrrrrrrrrK.....", ".....KrrrrrrrrrrrrrrrrrrrrK.....",
          "......KrrrrrrrrrrrrrrrrrrK......", "......KIrrrrrrrrrrrrrrrrIK......", ".......KIIrrrrrrrrrrrrIIK.......", "........KKIIIIIIIIIIIIKK........",
          "..........KKKKKKKKKKKK.........."]
PROPS32.update({
    "dizzy": [(img(confetti(0)), 2), (img(confetti(1)), 2)],
    "wake": [(img(sun(0)), 5), (img(sun(1)), 5)],
    "grumpy": [(img(CLOUD), 10)],
    "meeting": [(img(MIC), 10)],
    "pet_meeting": [(img(HEART), 3), (shift(img(HEART), dy=-1), 3)],
    "rain": [(img(UMBRELLA), 10)],
    "snow": [(img(SNOWMAN), 10)],
    "hot": [(img(fan(0)), 1), (img(fan(1)), 1)],
    "birthday": [(img(CAKE), 6), (shift(img(CAKE), dy=-1), 2)],
    "xmas": [(img(GIFT), 10)],
    "halloween": [(img(JACK), 8), (shift(img(JACK), dy=-1), 2)],
    "seollal": [(img(POUCH), 8), (shift(img(POUCH), dy=-1), 2)],
    "chuseok": [(img(SONGPYEON), 10)],
    "summer": [(img(BEACHBALL), 6), (shift(img(BEACHBALL), dy=-1), 2)],
    "stash": [(img(CLIPBOARD), 4), (shift(img(CLIPBOARD), dy=-1), 2)],
    "focus": [(img(TOMATO), 10)],
    "night": [(img(zzz()), 8), (shift(img(zzz()), dy=-1), 8)],
    "sprint": [(img(dots(i)), 1) for i in range(3)],
})
for k in ("idle_groom", "idle_cheeks", "idle_roll", "idle_peek", "typing"): PROPS32[k] = PROPS32["idle"]
# ---------- 장면 ----------
QMARK = ["", "", ".........qqqqqqqqqq.............", "........qqqqqqqqqqqq............", ".......qqqq......qqqq...........", ".......qqq........qqq...........",
         ".......qqq........qqq...........", "..................qqq...........", ".................qqqq...........", "................qqqq............",
         "...............qqqq.............", "..............qqqq..............", ".............qqqq...............", ".............qqq................",
         ".............qqq................", "", "", ".............qqqq...............", ".............qqqq...............", ".............qqqq..............."]
def storm(bolt):
    rows = list(CLOUD[:12])
    if bolt:
        rows += ["", "...............qqqq.............", "..............qqqq..............", ".............qqqqqqq............", "...............qqqq.............",
                 "..............qqq...............", ".............qqq................", "............qq..................", "...........q...................."]
    return rows
def night(f):
    rows = ["", "", "..........qqqqqq................", "........qqqqqqqqqq..............", ".......qqqqqqq..................", "......qqqqqq....................",
            ".....qqqqq......................", ".....qqqqq......................", ".....qqqqq......................", ".....qqqqqq.....................",
            "......qqqqqq....................", ".......qqqqqqq..................", "........qqqqqqqqqq..............", "..........qqqqqq................"]
    rows = grid(rows)
    for x, y in [((22, 5), (25, 16), (18, 23)), ((24, 9), (20, 19), (28, 4))][f]:
        for d in range(-2, 3):
            for xx, yy in ((x + d, y), (x, y + d)):
                if 0 <= xx < N and 0 <= yy < N: r = list(rows[yy]); r[xx] = "h"; rows[yy] = "".join(r)
    return rows
BUBBLE = ["", "", "......KKKKKKKKKKKKKKKKKKKK......", ".....KhhhhhhhhhhhhhhhhhhhhK.....", "....KhhhhhhhhhhhhhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....",
          "....KhhhhhhhhhhKKhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....",
          "....KhhhhhhhhhhKKhhhhhhhhhhK....", "....KhhhhhhhhhhhhhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....", "....KhhhhhhhhhhKKhhhhhhhhhhK....",
          "....KhhhhhhhhhhhhhhhhhhhhhhK....", ".....KhhhhhhhhhhhhhhhhhhhhK.....", "......KKKKKKKhhhhKKKKKKKKK......", "...........KhhhK................",
          "..........KhhK..................", ".........KhK....................", ".........KK....................."]
TREE = ["", "..............h.................", ".............hhh................", "..............v.................", ".............vvv................",
        "............vvvvv...............", "...........vvrvvvv..............", "..........vvvvvvvvv.............", ".........vvvvvqvvvvv............",
        "..........vvvvvvvvv.............", ".........vvvvvvvrvvv............", "........vvrvvvvvvvvvv...........", ".......vvvvvvvqvvvvvvv..........",
        "......vvvvvvvvvvvvvvvvv.........", ".....vvvqvvvvvvvvvrvvvvv........", "....vvvvvvvvvvrvvvvvvvvvv.......", "...vvvvvvvvvvvvvvvvvvqvvvv......",
        "..vvvvrvvvvvqvvvvvvvvvvvvvv.....", "..............nn................", "..............nn................", "............KKKKKK..............",
        "............KxxxxK..............", "............KKKKKK.............."]
FULLMOON = ["", "", "...........qqqqqqqqqq...........", ".........qqqqqqqqqqqqqq.........", "........qqqqqqqqqqqqqqqq........", ".......qqqqqqqqqqqqqqqqqq.......",
            "......qqqqqqqqqqqqqqqqqqqq......", ".....qqqqqqqqqqqqqqqqqqqqqq.....", ".....qqqqqqQqqqqqqqqqqqqqqq.....", "....qqqqqqQQQqqqqqqqqqqqqqqq....",
            "....qqqqqqqQqqqqqqqqqqQqqqqq....", "....qqqqqqqqqqqqqqqqqQQQqqqq....", "....qqqqqqqqqqqqqqqqqqQqqqqq....", "....qqqqqqqqqqqqqqqqqqqqqqqq....",
            ".....qqqqqqqqqqqqqqqqqqqqqq.....", ".....qqqqqqqqqqqqqqqqqqqqqq.....", "......qqqqqqqqqqqqqqqqqqqq......", ".......qqqqqqqqqqqqqqqqqq.......",
            "........qqqqqqqqqqqqqqqq........", ".........qqqqqqqqqqqqqq.........", "...........qqqqqqqqqq..........."]
SEA = ["", "......................qqqq......", ".....................qqqqqq.....", ".....................qqqqqq.....", "......................qqqq......",
       "", "", "", "", "", "", "", "..llllllllllllllllllllllllllll..", ".llllllllllllllllllllllllllll..",
       "hhllllhhlllllhhllllhhlllllhhllll", "llllllllllllllllllllllllllllllll", "lllhhlllllhhllllhhlllllhhlllllll", "llllllllllllllllllllllllllllllll",
       "llllllllllllllllllllllllllllllll", "llllllllllllllllllllllllllllllll"]
def rainscene(f):
    rows = grid(storm(False))
    for x, y in [((5, 15), (12, 18), (19, 15), (9, 23), (16, 26), (24, 21), (27, 27)), ((7, 18), (14, 21), (21, 18), (11, 26), (18, 29), (26, 24), (4, 27))][f]:
        for dy in (0, 1, 2):
            if y + dy < N: r = list(rows[y + dy]); r[x] = "l"; rows[y + dy] = "".join(r)
    return rows
def snowscene(f):
    rows = grid([])
    for x, y in [((4, 4), (13, 8), (22, 3), (8, 16), (17, 19), (26, 13), (6, 25), (20, 26)), ((6, 7), (15, 11), (24, 6), (10, 19), (19, 22), (28, 16), (7, 28), (22, 29))][f]:
        for d in range(-2, 3):
            for xx, yy in ((x + d, y), (x, y + d)):
                if 0 <= xx < N and 0 <= yy < N: r = list(rows[yy]); r[xx] = "h"; rows[yy] = "".join(r)
    return rows
SCENES32.update({
    "done": [(img(confetti(0)), 3), (img(confetti(1)), 3)],
    "surprised": [(img(QMARK), 4), (shift(img(QMARK), dy=1), 4)],
    "faint": [(img(storm(True)), 2), (img(storm(False)), 4)],
    "sleep": [(img(night(0)), 8), (img(night(1)), 8)],
    "notify": [(img(BUBBLE), 10)],
    "xmas": [(img(TREE), 6), (img([r.replace("h", "q", 1) for r in TREE]), 3)],
    "chuseok": [(img(FULLMOON), 10)],
    "summer": [(img(SEA), 6), (img([r.replace("hh", "lh", 1) if "hh" in r else r for r in SEA]), 6)],
    "rain": [(img(rainscene(0)), 3), (img(rainscene(1)), 3)],
    "snow": [(img(snowscene(0)), 4), (img(snowscene(1)), 4)],
    "hot": [(img(sun(0)), 5), (img(sun(1)), 5)],
    "meeting_soon": [(img(CALENDAR), 10)], "meeting": [(img(CALENDAR), 10)],
    "focus": [(img(TOMATO), 8), (shift(img(TOMATO), dy=-1), 2)],
    "halloween": [(img(night(0)), 8), (img(night(1)), 8)], "night": [(img(night(0)), 8), (img(night(1)), 8)],
    "seollal": [(img(confetti(0)), 3), (img(confetti(1)), 3)], "friday": [(img(confetti(0)), 3), (img(confetti(1)), 3)], "birthday": [(img(confetti(0)), 3), (img(confetti(1)), 3)],
    "pet": [(img(confetti(0)), 3), (img(confetti(1)), 3)], "dizzy": [(img(storm(True)), 2), (img(storm(False)), 4)], "grumpy": [(img(night(0)), 8), (img(night(1)), 8)],
    "wake": [(img(HOUSE), 10)], "cpu": [(img(window(True)), 4), (img(window(False)), 4)], "sprint": [(img(window(True)), 4), (img(window(False)), 4)],
})
for k in ("idle_groom", "idle_cheeks", "idle_roll", "idle_peek", "typing", "lunch", "leave", "break", "water", "battery_low", "charging", "stash", "pet_meeting"):
    SCENES32.setdefault(k, SCENES32["idle"] if k not in ("pet_meeting",) else SCENES32["meeting"])
# ---------- 로고 ----------
SLACK = ["", "", ".....KKKKKKKKKKKKKKKKKKKKKK.....", "....KSSSSSSSSSSSSSSSSSSSSSSK....", "...KSSSSSSSSSSSSSSSSSSSSSSSSK...", "...KSSSSSSSuuSSSSSSSSSSSSSSK...",
         "...KSSSSSSSuuSSSSSSSSSSSSSSK...", "...KSSSSSSSuuSSSvvvvvvvvSSSK...", "...KSSSSSSSuuSSSvvvvvvvvSSSK...", "...KSSSSSSSuuSSSSSSSSSSSSSSK...",
         "...KSSSSSSSuuSSSSSSSSSSSSSSK...", "...KSSSSSSSSSSSSSSSSSeeSSSSK...", "...KSSSSSSSSSSSSSSSSSeeSSSSK...", "...KSSSmmmmmmmmSSSSSSeeSSSSK...",
         "...KSSSmmmmmmmmSSSSSSeeSSSSK...", "...KSSSSSSSSSSSSSSSSSeeSSSSK...", "...KSSSSSSSSSSSSSSSSSeeSSSSK...", "....KSSSSSSSSSSSSSSSSSSSSSSK....",
         ".....KKKKKKKKKKKKKKKKKKKKKK....."]
KAKAO = ["", "", ".....KKKKKKKKKKKKKKKKKKKKKK.....", "....KqqqqqqqqqqqqqqqqqqqqqqK....", "...KqqqqqqqqqqqqqqqqqqqqqqqqK...", "...KqqqqqqqqqqqqqqqqqqqqqqqqK...",
         "...KqqqqqnnnnnnnnnnnnnnqqqqqK...", "...KqqqqnnnnnnnnnnnnnnnnqqqqK...", "...KqqqnnnnnnnnnnnnnnnnnnqqqK...", "...KqqqnnnnnnnnnnnnnnnnnnqqqK...",
         "...KqqqnnnnnnnnnnnnnnnnnnqqqK...", "...KqqqnnnnnnnnnnnnnnnnnnqqqK...", "...KqqqqnnnnnnnnnnnnnnnnqqqqK...", "...KqqqqqnnnnnnnnnnnnnnqqqqqK...",
         "...KqqqqqnnnnqqqqqqqqqqqqqqqK...", "...KqqqqqqnnnqqqqqqqqqqqqqqqK...", "...KqqqqqqqnnqqqqqqqqqqqqqqqK...", "....KqqqqqqqqqqqqqqqqqqqqqqK....",
         ".....KKKKKKKKKKKKKKKKKKKKKK....."]
OUTLOOK = ["", "", ".....KKKKKKKKKKKKKKKKKKKKKK.....", "....KUUUUUUUUUUUUUUUUUUUUUUK....", "...KUUUUUUUUUUUUUUUUUUUUUUUUK...", "...KUUUUUUUUUhhhhhhhhhhhhUUUK...",
           "...KUUUhhhhhhhhhhhhhhhhhhUUUK...", "...KUUhhhhhhhhhhhhhhhhhhhhUUK...", "...KUUhhUUUUUUhhhhhhhhhhhhUUK...", "...KUUhhUUUUUUhhUUUUUUUUhhUUK...",
           "...KUUhhUUUUUUhhhhhhhhhhhhUUK...", "...KUUhhUUUUUUhhhhhhhhhhhhUUK...", "...KUUhhUUUUUUhhhhhhhhhhhhUUK...", "...KUUhhhhhhhhhhhhhhhhhhhhUUK...",
           "...KUUUhhhhhhhhhhhhhhhhhhUUUK...", "...KUUUUUUUUUUUUUUUUUUUUUUUUK...", "...KUUUUUUUUUUUUUUUUUUUUUUUUK...", "....KUUUUUUUUUUUUUUUUUUUUUUK....",
           ".....KKKKKKKKKKKKKKKKKKKKKK....."]
LOGOS32 = {"slack": img(SLACK), "kakao": img(KAKAO), "outlook": img(OUTLOOK), "generic": img(BUBBLE)}
