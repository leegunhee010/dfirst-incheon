# -*- coding: utf-8 -*-
"""마케팅 세부 서비스(zrow) 블록 이미지 생성 (2026-07-27 사용자 "이것들도 바꿔야해").
기존엔 본사 firstd 상세이미지 히어로 밴드를 그대로 크롭해 썼는데
 ① 초록·핑크라 인천 틸 브랜드와 안 맞고 ② 이미지 안 제목이 옆 카드 제목과 중복됐다.
→ 채널별 '콘텐츠 목업' 일러스트를 굽는다. 글자를 넣지 않아 중복이 없고, 팔레트를 통일해 한 세트로 보인다.
출력: theme/assets/first/mkt/vis-*.jpg (1200×750 = zrow-img의 16:10)"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "theme" / "assets" / "first" / "mkt"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1200, 750

BG      = (238, 245, 244)
WHITE   = (255, 255, 255)
TEAL    = (12, 147, 132)
TEAL_D  = (10, 90, 82)
MUTED   = (198, 219, 215)
MUTED_2 = (222, 234, 231)

def canvas(tint):
    """연한 틸 배경 + 우상단 악센트 블롭"""
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for y in range(H):                     # 아주 옅은 세로 그라디언트
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(BG[0] - 6 * t), int(BG[1] - 5 * t), int(BG[2] - 5 * t)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([W - 380, -180, W + 140, 340], fill=tint + (46,))
    od.ellipse([-160, H - 260, 240, H + 140], fill=TEAL + (26,))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")

def shadow(im, box, radius, blur=26, alpha=42, dy=14):
    """부드러운 그림자 (요소를 띄워 보이게)"""
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0], box[1] + dy, box[2], box[3] + dy], radius, fill=(10, 60, 54, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB")

def card(im, box, radius=22, fill=WHITE):
    im = shadow(im, box, radius)
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=fill)
    return im

def bars(d, x, y, widths, h=13, gap=20, color=MUTED, r=7):
    for w in widths:
        d.rounded_rectangle([x, y, x + w, y + h], r, fill=color)
        y += h + gap
    return y

# ---------- 채널별 목업 ----------
def blog(tint):                                   # 브라우저 창 + 포스트
    im = card(canvas(tint), [110, 110, 1090, 660], 24)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 110, 1090, 186], 24, fill=(243, 248, 247))
    d.rectangle([110, 160, 1090, 186], fill=(243, 248, 247))
    for i, c in enumerate([(255, 110, 100), (255, 200, 90), (110, 210, 150)]):
        d.ellipse([150 + i * 34, 138, 170 + i * 34, 158], fill=c)
    d.rounded_rectangle([300, 134, 900, 162], 14, fill=(226, 236, 234))
    d.rounded_rectangle([160, 232, 520, 262], 15, fill=TEAL_D)      # 제목
    d.rounded_rectangle([160, 284, 380, 306], 11, fill=TEAL)        # 키워드 태그
    y = bars(d, 160, 350, [820, 780, 840, 700])
    d.rounded_rectangle([160, y + 18, 1040, y + 190], 18, fill=tint + ())  # 이미지 자리
    return im

def insta(tint):                                  # 폰 + 3×3 피드
    im = card(canvas(tint), [430, 70, 770, 700], 44)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([560, 92, 640, 106], 7, fill=(226, 236, 234))
    d.ellipse([466, 140, 526, 200], fill=MUTED_2)                    # 프로필
    d.rounded_rectangle([546, 150, 706, 170], 10, fill=TEAL_D)
    d.rounded_rectangle([546, 182, 646, 198], 8, fill=MUTED)
    x0, y0, s, g = 466, 240, 92, 12
    tones = [tint, MUTED_2, TEAL, MUTED_2, tint, MUTED, TEAL, tint, MUTED_2]
    for i in range(9):
        x = x0 + (i % 3) * (s + g); y = y0 + (i // 3) * (s + g)
        d.rounded_rectangle([x, y, x + s, y + s], 10, fill=tones[i])
    d.rounded_rectangle([466, 560, 734, 588], 12, fill=(236, 244, 242))
    d.rounded_rectangle([466, 606, 620, 630], 12, fill=MUTED_2)
    return im

def search(tint):                                 # 검색 결과 리스트 (준·최적배포)
    im = canvas(tint)
    im = card(im, [130, 120, 1070, 200], 40)
    d = ImageDraw.Draw(im)
    d.ellipse([166, 142, 202, 178], outline=TEAL, width=6)          # 돋보기
    d.line([(196, 172), (216, 192)], fill=TEAL, width=7)
    d.rounded_rectangle([250, 150, 640, 172], 11, fill=MUTED)
    y = 250
    for i in range(3):
        top = y + i * 152
        im = card(im, [130, top, 1070, top + 124], 20)
        d = ImageDraw.Draw(im)
        hot = (i == 0)
        d.rounded_rectangle([168, top + 26, 236, top + 52], 12, fill=TEAL if hot else MUTED_2)
        d.rounded_rectangle([252, top + 28, 252 + (520 if hot else 420), top + 50], 11,
                            fill=TEAL_D if hot else (150, 175, 170))
        bars(d, 168, top + 72, [700 if hot else 560], h=11, color=MUTED_2)
        if hot:
            d.rounded_rectangle([130, top, 138, top + 124], 4, fill=TEAL)
    return im

def rank(tint):                                   # 상위노출 랭킹
    im = canvas(tint)
    d = ImageDraw.Draw(im)
    rows = [(1, 1.0), (2, 0.82), (3, 0.66)]
    y = 170
    for n, scale in rows:
        h = int(150 * scale); w = int(760 * scale)
        top = y
        im = card(im, [150, top, 150 + w, top + h], 20,
                  fill=WHITE if n > 1 else (255, 255, 255))
        d = ImageDraw.Draw(im)
        if n == 1:
            d.rounded_rectangle([150, top, 150 + w, top + h], 20, outline=TEAL, width=4)
        d.ellipse([186, top + h // 2 - 26, 238, top + h // 2 + 26],
                  fill=TEAL if n == 1 else MUTED_2)
        d.rounded_rectangle([272, top + h // 2 - 26, 272 + int(w * 0.52), top + h // 2 - 4], 11,
                            fill=TEAL_D if n == 1 else (160, 182, 178))
        d.rounded_rectangle([272, top + h // 2 + 6, 272 + int(w * 0.34), top + h // 2 + 24], 9,
                            fill=MUTED_2)
        y += h + 40
    # 상승 화살표
    d.line([(950, 560), (1010, 470), (1070, 330)], fill=TEAL, width=10, joint="curve")
    d.polygon([(1070, 320), (1046, 372), (1094, 372)], fill=TEAL)
    return im

def perf(tint):                                   # 성과 그래프
    im = card(canvas(tint), [130, 120, 1070, 640], 26)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([180, 176, 420, 200], 12, fill=MUTED)
    base = 560
    for i, hgt in enumerate([120, 190, 160, 260, 330]):
        x = 200 + i * 150
        col = TEAL if i == 4 else (tint if i % 2 else MUTED_2)
        d.rounded_rectangle([x, base - hgt, x + 92, base], 12, fill=col)
    d.line([(180, base + 26), (1020, base + 26)], fill=MUTED_2, width=4)
    pts = [(246, 430), (396, 366), (546, 392), (696, 300), (846, 236)]
    d.line(pts, fill=TEAL_D, width=6, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=WHITE, outline=TEAL_D, width=5)
    return im

def short(tint):                                  # 숏폼 세로영상 + 재생
    im = canvas(tint)
    for i, (x, sc) in enumerate([(200, .78), (760, .78)]):
        w, h = int(300 * sc), int(560 * sc)
        top = (H - h) // 2
        im = card(im, [x, top, x + w, top + h], 26, fill=MUTED_2)
    im = card(im, [470, 75, 730, 675], 32, fill=WHITE)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([490, 95, 710, 590], 22, fill=tint)
    d.ellipse([540, 280, 660, 400], fill=(255, 255, 255, 255))
    d.polygon([(582, 312), (582, 368), (628, 340)], fill=TEAL)
    d.rounded_rectangle([510, 616, 660, 636], 10, fill=MUTED)
    d.rounded_rectangle([510, 646, 590, 662], 8, fill=MUTED_2)
    return im

def press(tint):                                  # 뉴스 기사
    im = card(canvas(tint), [120, 100, 1080, 660], 24)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([170, 150, 330, 176], 12, fill=TEAL)         # 매체명
    d.line([(170, 206), (1030, 206)], fill=MUTED_2, width=3)
    d.rounded_rectangle([170, 240, 860, 276], 16, fill=TEAL_D)       # 헤드라인
    d.rounded_rectangle([170, 292, 640, 320], 13, fill=(150, 175, 170))
    d.rounded_rectangle([170, 360, 520, 560], 16, fill=tint)         # 사진
    bars(d, 566, 366, [464, 440, 464, 410, 450], h=12, gap=22, color=MUTED_2)
    d.rounded_rectangle([170, 596, 380, 616], 10, fill=MUTED_2)
    return im

def app(tint):                                    # 모바일 앱 UI (svc-web '앱 개발' 블록용)
    im = canvas(tint)
    im = card(im, [180, 150, 560, 640], 24)       # 좌: 리스트 화면
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([216, 196, 380, 220], 12, fill=TEAL_D)
    d.rounded_rectangle([216, 244, 524, 300], 14, fill=(240, 246, 245))
    for i in range(3):
        top = 330 + i * 84
        d.rounded_rectangle([216, top, 524, top + 66], 14, fill=(243, 248, 247))
        d.rounded_rectangle([232, top + 14, 274, top + 52], 10, fill=tint if i == 0 else MUTED_2)
        d.rounded_rectangle([292, top + 20, 470, top + 34], 8, fill=MUTED)
        d.rounded_rectangle([292, top + 42, 400, top + 54], 7, fill=MUTED_2)
    im = card(im, [620, 90, 1020, 700], 34)       # 우: 상세 화면 (겹쳐서 앞으로)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([780, 112, 860, 126], 7, fill=(230, 239, 237))
    d.rounded_rectangle([652, 150, 988, 350], 20, fill=tint)
    d.rounded_rectangle([652, 380, 900, 408], 13, fill=TEAL_D)
    bars(d, 652, 428, [300, 336, 270], h=12, gap=18)
    d.rounded_rectangle([652, 540, 988, 596], 18, fill=TEAL)   # CTA 버튼
    d.rounded_rectangle([760, 560, 880, 576], 8, fill=(255, 255, 255))
    for i in range(4):                                          # 탭바
        x = 668 + i * 84
        d.rounded_rectangle([x, 636, x + 44, 664], 10,
                            fill=TEAL if i == 0 else MUTED_2)
    return im

SPECS = [("blog", blog, (46, 208, 189)), ("insta", insta, (232, 168, 214)),
         ("baepo", search, (120, 214, 170)), ("top", rank, (196, 152, 232)),
         ("perf", perf, (128, 186, 236)), ("short", short, (96, 216, 186)),
         ("press", press, (150, 184, 232))]

for key, fn, tint in SPECS:
    fn(tint).save(OUT / f"vis-{key}.jpg", quality=90)
    print("생성 vis-" + key + ".jpg")

# svc-web '앱 개발' 블록 — 실제 앱 실적이 없어 웹사이트 사진을 쓰면 사실과 다르므로 목업 사용
WEBOUT = ROOT / "theme" / "assets" / "first" / "web"
WEBOUT.mkdir(parents=True, exist_ok=True)
app((128, 186, 236)).save(WEBOUT / "vis-app.jpg", quality=90)
print("생성 web/vis-app.jpg")
print("완료:", len(SPECS) + 1, "장")
