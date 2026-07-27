# -*- coding: utf-8 -*-
"""마케팅 페이지 롤링용 카드 이미지 생성 (2026-07-27 사용자: "마케팅은 지금 포폴이 없으니까
그냥 사진을 만들던지 해서 적용해").
실제 마케팅 작업물이 없으므로 포폴 사진 대신 채널별 브랜드 카드를 굽는다.
스타일 = 기존 칼럼 카드(_overlay.py column-card.png)와 동일 계열: 틸 그라디언트 + 필 라벨 +
대형 한글 + 서브카피 + FIRST DESIGN INCHEON. 채널 구분을 위해 카드마다 악센트 색·심볼만 다르게.
출력: theme/assets/first/mkt/card-*.jpg (840×568 = 롤링 표시크기 420×284의 2배)"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "theme" / "assets" / "first" / "mkt"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 840, 568

def font(sz, bold=True):
    for n in (["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + n, sz)
        except OSError:
            pass
    return ImageFont.load_default()

# (파일명, 라벨, 제목, 서브카피, 배경 시작색, 배경 끝색, 악센트)
CARDS = [
    ("blog",  "BRAND BLOG",   "브랜드 블로그",      "키워드 원고 · 카드뉴스 월 60개",
     (11, 46, 42),  (12, 147, 132), (46, 208, 189)),
    ("insta", "INSTAGRAM",    "브랜드 인스타그램",   "피드 · 카드뉴스 · 소통까지 운영",
     (14, 40, 60),  (18, 120, 150), (80, 200, 220)),
    ("baepo", "NAVER",        "네이버 준·최적배포",  "광고 아닌 콘텐츠로 상위노출",
     (10, 50, 38),  (16, 140, 96),  (74, 214, 150)),
    ("top",   "TOP EXPOSURE", "인스타그램 상위노출",  "해시태그 추천 탭 상단 노출",
     (40, 24, 60),  (120, 60, 150), (200, 140, 230)),
    ("perf",  "PERFORMANCE",  "퍼포먼스 마케팅",     "검색광고 · 메타 광고 운영",
     (12, 38, 70),  (24, 100, 170), (110, 180, 240)),
    ("short", "SHORT-FORM",   "숏폼 콘텐츠",        "기획 · 촬영 · 편집 원스톱",
     (18, 48, 44),  (26, 158, 130), (96, 226, 190)),
    ("press", "PR",           "언론홍보",           "포털 뉴스 탭 보도자료 노출",
     (24, 32, 52),  (52, 92, 150),  (140, 180, 235)),
]

def build(key, label, title, sub, c1, c2, accent):
    im = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(im)
    # 대각 그라디언트
    for y in range(H):
        for_t = y / H
        for x in range(0, W, 8):
            t = min(1.0, (x / W) * 0.75 + for_t * 0.25)
            d.rectangle([x, y, x + 8, y + 1],
                        fill=(int(c1[0] + (c2[0] - c1[0]) * t),
                              int(c1[1] + (c2[1] - c1[1]) * t),
                              int(c1[2] + (c2[2] - c1[2]) * t)))
    # 우하단 장식 원 (칼럼 카드의 여백감 유지)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([W - 250, H - 250, W + 90, H + 90], fill=accent + (38,))
    od.ellipse([W - 150, H - 190, W + 60, H + 20], fill=accent + (30,))
    od.ellipse([W - 96, 300, W - 26, 370], outline=accent + (110,), width=3)
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im)
    # 필 라벨
    lf = font(22)
    tw = d.textlength(label, font=lf)
    d.rounded_rectangle([56, 92, 56 + tw + 56, 148], 28, fill=accent)
    d.text((56 + 28 + tw / 2, 120), label, font=lf, fill=(10, 40, 36), anchor="mm")
    # 제목 · 서브
    d.text((56, 232), title, font=font(52), fill="white", anchor="lm")
    d.text((56, 300), sub, font=font(24, False), fill=(214, 236, 232), anchor="lm")
    # 하단 워드마크 + 라인
    d.line([(56, 452), (140, 452)], fill=accent, width=3)
    d.text((56, 492), "FIRST DESIGN INCHEON", font=font(20), fill=(168, 205, 200), anchor="lm")
    im.save(OUT / f"card-{key}.jpg", quality=90)
    print("생성", f"card-{key}.jpg")

for c in CARDS:
    build(*c)
print("완료:", len(CARDS), "장")
