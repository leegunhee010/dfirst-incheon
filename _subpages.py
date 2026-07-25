# -*- coding: utf-8 -*-
"""서브페이지 6종(about/portfolio/review/column/notice/contact) 빌드.
poedit 서브페이지 미러 → 로컬라이즈 → 퍼스트디자인 인천지사 오버레이 + 틸 리컬러.
스크래치의 sub-*.html / css-*.css 필요 (없으면 curl로 재다운로드)."""
import os, re, glob, shutil, pathlib

ROOT = pathlib.Path(__file__).parent
HOME = pathlib.Path(os.path.expanduser("~"))
SCRATCH = HOME / "AppData/Local/Temp/claude/C--Users----/54452de3-9fd5-4fdb-ab17-d592a917fbd9/scratchpad"
IMG = ROOT / "theme" / "assets" / "images"
FIRST = ROOT / "theme" / "assets" / "first"
PF = FIRST / "pf"
PF.mkdir(parents=True, exist_ok=True)
SRC = HOME / "dfirst-new" / "assets"

PRIMARY = "#0C9384"
PHONE = "1600-9487"
EMAIL = "firstmk1111@gmail.com"
SITE = "퍼스트디자인 인천지사"
PAGES = ["about", "portfolio", "review", "column", "notice", "contact"]

CTA2 = '''<section class="cta-section">
    <div class="cta2">
        <div class="cta2-left">
            <p class="cta2-eyebrow">FIRST DESIGN INCHEON</p>
            <p class="cta2-copy">상담 설문지 작성하고<strong>디자인 전문가에게 무료 상담 받기</strong></p>
        </div>
        <div class="cta2-right">
            <div class="cta2-phone"><span>전화 상담</span><b>''' + PHONE + '''</b></div>
            <a href="contact.html" class="cta2-btn">상담 설문지 작성하기
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg></a>
        </div>
        <span class="cta2-ghost" aria-hidden="true">FIRST</span>
    </div>
</section>'''

def find_upload(idpart):
    hits = glob.glob(str(SRC / "uploads" / ("pf_" + idpart + "*")))
    if not hits:
        raise FileNotFoundError(idpart)
    return pathlib.Path(hits[0])

# ---------- 1. 페이지 CSS 설치 + 리컬러 ----------
for c in ["page", "about", "portfolio", "review", "column", "notice", "contact"]:
    t = (SCRATCH / f"css-{c}.css").read_text(encoding="utf-8")
    t = t.replace("#FF6E3F", PRIMARY).replace("#ff6e3f", PRIMARY).replace("#e55a2f", "#0A7A6E")
    t = re.sub(r"rgba\(255,\s*110,\s*63", "rgba(12, 147, 132", t)
    (ROOT / "theme" / "css" / "pages" / f"{c}.css").write_text(t, encoding="utf-8")

# ---------- 2. 이미지 준비 ----------
from PIL import Image, ImageDraw, ImageFont
def font(sz, bold=True):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/" + ("malgunbd.ttf" if bold else "malgun.ttf"), sz)
    except OSError:
        return ImageFont.load_default()

def shift_orange_to_teal(path):
    im = Image.open(path)
    has_a = im.mode in ("RGBA", "LA", "P")
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    h, s, v = rgba.convert("RGB").convert("HSV").split()
    hd, sd = h.load(), s.load()
    w, ht = h.size
    for y in range(ht):
        for x in range(w):
            if hd[x, y] <= 40 and sd[x, y] >= 8:
                hd[x, y] = (hd[x, y] + 110) % 256
    out = Image.merge("HSV", (h, s, v)).convert("RGB")
    out = Image.merge("RGBA", (*out.split(), a)) if has_a else out
    out.save(path)

# about 아이콘 (틸화) — about-bg-top.png는 원본 서버에서도 404라 스킵
dst = IMG / "about1.png"
if not dst.exists():
    shutil.copy(SCRATCH / "sub-img-about1.png", dst)
    shift_orange_to_teal(dst)

# about 오피스 → 퍼스트 간판 실사
office = FIRST / "office.jpg"
if not office.exists():
    im = Image.open(find_upload("1781577434641")).convert("RGB")
    w, h = im.size
    th = int(w * 694 / 2560)
    im.crop((0, max(0, (h - th) // 2), w, max(0, (h - th) // 2) + th)).resize((2560, 694)).save(office, quality=88)

# about 배너 2종 생성 (2560x506 틸)
def make_banner(path, big, sub):
    im = Image.new("RGB", (2560, 506), "#0B2E2A")
    d = ImageDraw.Draw(im)
    for x in range(2560):
        t = x / 2560
        d.line([(x, 0), (x, 506)], fill=(int(11 + 1 * t), int(46 + 101 * t), int(42 + 90 * t)))
    d.text((140, 190), big, font=font(72), fill="white", anchor="lm")
    d.text((140, 320), sub, font=font(36, False), fill=(205, 230, 226), anchor="lm")
    d.text((2420, 253), "FIRST DESIGN\nINCHEON", font=font(30), fill=(150, 195, 189), anchor="rm", align="right")
    im.save(path)

make_banner(FIRST / "about-banner1.png", "매월 12건 한정, 끝까지 책임지는 프로젝트", "수보다 완성도 — 품질이 확보되지 않는 작업은 정중히 거절합니다")
make_banner(FIRST / "about-banner2.png", "기획 · 디자인 · 인쇄 · 촬영 원스톱", "본사 12년 노하우 그대로, 인천에서 당일 미팅으로 만나보세요")

# 칼럼 썸네일 3종 추가 생성 (826x464)
def make_col_thumb(path, title, sub):
    im = Image.new("RGB", (826, 464), "#0B2E2A")
    d = ImageDraw.Draw(im)
    for x in range(826):
        t = x / 826
        d.line([(x, 0), (x, 464)], fill=(int(11 + 1 * t), int(46 + 101 * t), int(42 + 90 * t)))
    d.rounded_rectangle([56, 96, 300, 144], 22, fill=PRIMARY)
    d.text((178, 120), "퍼스트디자인 블로그", font=font(20), fill="white", anchor="mm")
    d.text((56, 205), title, font=font(38), fill="white", anchor="lm")
    d.text((56, 262), sub, font=font(20, False), fill=(210, 230, 227), anchor="lm")
    d.text((56, 392), "FIRST DESIGN INCHEON", font=font(18), fill=(150, 190, 185), anchor="lm")
    im.save(path)

make_col_thumb(FIRST / "col-2.png", "카탈로그 제작 전 체크리스트 5가지", "원고·사진·일정, 시작 전에 이것만 준비하세요")
make_col_thumb(FIRST / "col-3.png", "로고 리뉴얼, 언제 해야 할까?", "브랜드가 보내는 신호와 리뉴얼 타이밍")
make_col_thumb(FIRST / "col-4.png", "인쇄 사고를 막는 원고 준비법", "재인쇄 없는 마감을 위한 데이터 체크포인트")

# ---------- 3. 포트폴리오 아이템 ----------
# (소스, 카테고리키, 클라이언트, 유형)  카테고리: 책자/리플릿/로고/촬영/기타
G = lambda n: SRC / "gallery" / n
ITEMS = [
    (G("g02.png"), "책자", "문화예술 전시관", "전시 브로슈어"),
    (G("g11.png"), "책자", "IT·데이터 기업", "회사소개서"),
    (G("g17.png"), "책자", "해양장비 제조기업", "카탈로그"),
    (G("g20.png"), "책자", "식품 브랜드", "브로슈어"),
    (G("g28.png"), "책자", "산업설비 기업", "카탈로그"),
    (G("g29.png"), "책자", "제약·바이오 기업", "브로슈어"),
    (G("g40.png"), "책자", "기업 홍보물", "폴더·브로슈어"),
    (find_upload("1780560047851"), "책자", "정밀기기 제조사", "제품 카탈로그"),
    (find_upload("1780561017607"), "책자", "공공기관", "안내 책자"),
    (find_upload("1780563086805"), "촬영", "과일 선물세트 브랜드", "패키지 연출 촬영"),
    (find_upload("1781229209415"), "책자", "기념사업회", "50주년 기념집"),
    (find_upload("1781229227544"), "책자", "의료기기 기업", "회사소개서"),
    (find_upload("1781577049020"), "책자", "환경·에너지 기업", "브로슈어"),
    (G("g08.png"), "리플릿", "보상 안내 캠페인", "리플렛"),
    (G("g26.png"), "리플릿", "Wemico", "3단 리플렛"),
    (G("g34.png"), "리플릿", "테크 스타트업", "3단 리플렛"),
    (find_upload("1780561831138"), "리플릿", "기업 뉴스레터", "신문형 리플렛"),
    (find_upload("1780561866143"), "리플릿", "생활안전 캠페인", "안내 리플렛"),
    (find_upload("1780561954454"), "리플릿", "교육기관", "팜플렛"),
    (find_upload("1780562838633"), "리플릿", "복지시설", "안내 리플렛"),
    (find_upload("1780562846536"), "리플릿", "관공서", "3단 리플렛"),
    (find_upload("1780562860378"), "리플릿", "환경 캠페인", "3단 리플렛"),
    (find_upload("1781576837581"), "리플릿", "제조기업", "리플렛"),
    (find_upload("1781576961440"), "리플릿", "맥키", "3단 리플렛"),
    (find_upload("1780560571458"), "로고", "고량점", "로고 · 간판"),
    (find_upload("1780560577502"), "로고", "청춘예찬", "로고 디자인"),
    (find_upload("1780560592478"), "로고", "네이처셋 키즈", "로고 디자인"),
    (find_upload("1780560617361"), "로고", "BIZPROS", "로고 · 브랜딩"),
    (find_upload("1781577004923"), "로고", "yummy BUSAN", "로고 · 사인"),
    (G("g36.jpg"), "로고", "BOA", "로고 · 명함"),
    (G("g21.jpg"), "로고", "늘품", "로고 · 명함"),
    (G("g09.jpg"), "로고", "MG푸드시스템", "명함 디자인"),
    (find_upload("1780560823003"), "촬영", "다이닝 브랜드", "음식 촬영"),
    (find_upload("1780560831589"), "촬영", "여행용품 브랜드", "제품 연출 촬영"),
    (find_upload("1780560845032"), "촬영", "뷰티 브랜드", "제품 연출 촬영"),
    (find_upload("1780561005491"), "촬영", "화장품 브랜드", "제품 촬영"),
    (find_upload("1781577126401"), "촬영", "간편식 브랜드", "패키지 · 촬영"),
    (G("g04.jpg"), "기타", "KOMA", "캠페인 포스터"),
    (G("g25.jpg"), "기타", "브랜드 굿즈", "에코백 디자인"),
    (G("g38.png"), "기타", "공공기관", "독서기록장"),
    (find_upload("1780560331761"), "기타", "SNS 콘텐츠", "카드뉴스"),
    (find_upload("1780560349800"), "기타", "정책 홍보", "카드뉴스"),
    (find_upload("1780560604781"), "기타", "WELLNESS KOREA", "키비주얼"),
    (find_upload("1781576786008"), "기타", "레디큐", "포스터"),
]
pf_items = []
for src, cat, client, kind in ITEMS:
    dst = PF / src.name
    if not dst.exists():
        shutil.copy(src, dst)
    pf_items.append(("theme/assets/first/pf/" + src.name, cat, client, kind))

# ---------- 4. 공통 변환 ----------
def localize_common(html, page):
    # WP 잡동사니
    html = re.sub(r"<script[^>]*>\s*/\* <!\[CDATA\[ \*/.*?/\* \]\]> \*/\s*</script>", "", html, flags=re.S)
    html = re.sub(r"<style id='wp-emoji-styles-inline-css'.*?</style>", "", html, flags=re.S)
    html = re.sub(r"<link rel=\"https://api\.w\.org/\".*?/>", "", html)
    html = re.sub(r"<link rel=\"alternate\"[^>]*/>", "", html)
    html = re.sub(r"<link rel=\"EditURI\"[^>]*/>", "", html)
    html = re.sub(r"<meta name=\"generator\"[^>]*/>", "", html)
    html = re.sub(r"<link rel='shortlink'[^>]*/>", "", html)
    html = re.sub(r"<script type=\"speculationrules\">.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<link rel='dns-prefetch'[^>]*/>", "", html)
    html = re.sub(r'<link rel="canonical"[^>]*/>\n?', "", html)
    html = re.sub(r'<meta name="(naver|google)-site-verification"[^>]*/>\n?', "", html)
    html = re.sub(r'<link rel="(icon|apple-touch-icon)"[^>]*/?>\n?', "", html)
    html = re.sub(r'<meta name="msapplication-TileImage"[^>]*/>\n?', "", html)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', "", html, flags=re.S)
    # 리소스 로컬라이즈
    html = html.replace("https://poedit.co.kr/wp-includes/css/dist/block-library/style.min.css?ver=6.8.6", "theme/vendor/wp-block-library.css")
    html = html.replace("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css", "theme/vendor/swiper-bundle.min.css")
    html = html.replace("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js", "theme/vendor/swiper-bundle.min.js")
    html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/css/(tokens|common)\.css\?ver=[\d.]+", r"theme/css/\1.css", html)
    html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/css/pages/([\w-]+)\.css\?ver=[\d.]+", r"theme/css/pages/\1.css", html)
    html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/js/([\w-]+)\.js\?ver=[\d.]+", r"theme/js/\1.js", html)
    html = html.replace("https://poedit.co.kr/wp-content/themes/Poedit/assets/images/", "theme/assets/images/")
    import urllib.parse
    html = re.sub(r"theme/assets/images/[^\"'()\s>]+", lambda m: urllib.parse.unquote(m.group(0)), html)
    # 내부 링크 → 로컬
    for p in PAGES:
        html = re.sub(r'href="https://poedit\.co\.kr/' + p + r'/?(\?[^"]*)?"', f'href="{p}.html"', html)
    html = re.sub(r'href="https://poedit\.co\.kr/poedit_(notice|column)/[^"]*"', 'href="column.html"', html)
    html = html.replace("칼럼 + 공지사항", "칼럼")
    html = html.replace("인쇄물 제작과 관련한 모든 고민을 해결해보세요.", "디자인·인쇄 제작과 관련한 모든 고민을 해결해보세요.")
    html = html.replace(">전문 칼럼</a>", ">블로그</a>")
    html = html.replace('href="https://poedit.co.kr/"', 'href="index.html"')
    html = re.sub(r'<a href="https://poedit\.imweb\.me/"[^>]*>카드결제</a>', "", html)
    # 고객 후기·공지사항 삭제: 네비 항목 제거
    html = re.sub(r'\s*<a href="review\.html"[^>]*>(?:<span[^>]*>)?고객 후기(?:</span>)?</a>', "", html)
    html = re.sub(r'\s*<a href="notice\.html"[^>]*>공지사항</a>', "", html)
    # 브랜딩 — 상단바는 전체 삭제(사용자 지시)
    html = re.sub(r'<div class="top-bar">.*?</div>\s*<div class="divider-line"></div>\s*', "", html, count=1, flags=re.S)
    html = re.sub(r'<img src="theme/assets/images/포에디트_로고_헤더\.png"[^>]*/?>',
                  '<span class="logo-first">퍼스트<em>디자인</em><small>인천지사</small></span>', html)
    html = html.replace("매월 20건 한정", "매월 12건 한정")
    html = html.replace("인쇄물 전문가에게 무료 상담 받기", "디자인 전문가에게 무료 상담 받기")
    html = re.sub(r'<section class="cta-section">.*?</section>', CTA2, html, flags=re.S)
    html = re.sub(r"상호 : 포에디트.*?이메일 : contact@poedit\.co\.kr",
                  "상호 : 퍼스트디자인 인천지사(㈜퍼스트마케팅컴퍼니) &nbsp;|&nbsp; 대표자 : 김우석 &nbsp;|&nbsp; 사업자 번호 : 884-88-01123<br>"
                  "소재지 : 인천광역시 &nbsp;|&nbsp; 이메일 : " + EMAIL, html, flags=re.S)
    html = html.replace("1666-5183", PHONE)
    html = html.replace("contact@poedit.co.kr", EMAIL)
    html = html.replace("포에디트는", "퍼스트디자인은").replace("포에디트가", "퍼스트디자인이")
    html = html.replace("포에디트에", "퍼스트디자인에").replace("포에디트", SITE)
    html = html.replace("#FF6E3F", PRIMARY).replace("#FF6431", PRIMARY)
    html = html.replace('alt="포에디트 로고"', f'alt="{SITE}"')
    html = html.replace("</head>", '<link rel="icon" type="image/png" href="theme/assets/first/favicon.png">\n'
                        '<link rel="stylesheet" href="theme/css/incheon.css">\n</head>')
    return html

def set_title(html, t):
    html = re.sub(r"<title>.*?</title>", f"<title>{t} | {SITE}</title>", html, flags=re.S)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + t + " | " + SITE, html)
    html = re.sub(r'(<meta property="og:site_name" content=")[^"]*', r"\g<1>" + SITE, html)
    html = re.sub(r'<meta property="og:url"[^>]*>\n?', "", html)
    return html

out = {}

# ---------- 5-1. about — 원복(포에디트 구조 유지판, 2026-07-20 리디자인 폐기) ----------
h = (SCRATCH / "sub-about.html").read_text(encoding="utf-8")
h = localize_common(h, "about")
h = set_title(h, "회사소개")
# 히어로: 포에디트 북 아이콘 제거, 담백한 에디토리얼 문장 + 마커 하이라이트
h = re.sub(r'<div class="about-hero-icon">.*?</div>\s*', "", h, count=1, flags=re.S)
h = re.sub(r'<p class="about-label">[^<]*</p>', "", h)
h = re.sub(r'<h1 class="about-heading">.*?</h1>',
           '<h1 class="about-heading">기업 · 관공서 · 교육기관과 12년,<br>이제 <span class="abh-mark">인천에서도</span> 만날 수 있습니다</h1>', h, flags=re.S)
h = re.sub(r'<p class="about-desc">.*?</p>',
           '<p class="about-desc">퍼스트디자인 인천지사입니다. 카탈로그와 브로슈어부터 로고, 홈페이지까지 —<br>'
           '디자인 의뢰가 처음이어도 괜찮습니다. 기획부터 납품까지 저희가 알아서 챙기겠습니다.</p>', h, flags=re.S)
# 순서 교체: 간판 이미지를 맨 위로, 카피를 아래로
h = re.sub(r'(<div class="about-hero-top">.*?</div>)\s*(<div class="about-hero-img">.*?</div>)',
           r'\2\n    \1', h, count=1, flags=re.S)
h = re.sub(r'<img src="theme/assets/images/about-office\.png"[^>]*>',
           '<img src="theme/assets/first/office.jpg" alt="퍼스트디자인 인천지사" loading="lazy">', h)
# 틸 배너 로테이션 삭제(사용자 지시)
h = re.sub(r'<div class="about-banner">.*?</div>\s*', "", h, count=1, flags=re.S)
h = re.sub(r"<script>\s*\(function \(\) \{\s*var slides = document\.querySelectorAll\('\.about-banner-slide'\).*?</script>\s*", "", h, flags=re.S)
h = h.replace("편집 디자인", "디자인")
h = re.sub(r'<img src="theme/assets/images/Group-781\.png"[^>]*>',
           '<img src="theme/assets/first/column-card.png" alt="퍼스트디자인 블로그">', h)
# about 보드 → 홈과 동일한 전문 칼럼 슬라이더로 교체 (index.html에서 복사)
_idx = (ROOT / "index.html").read_text(encoding="utf-8")
_m = re.search(r'<section class="colsl-section">.*?</script>', _idx, re.S)
if _m:
    h = re.sub(r'<section class="about-board">.*?</section>', _m.group(0), h, count=1, flags=re.S)
else:  # 안전망: 홈 빌드 전이면 공지 컬럼만 제거
    h = re.sub(r'<div class="about-board-col about-board-notice">.*?</section>', '</div>\n</section>', h, count=1, flags=re.S)

# ---- 본사(dfirst.co.kr) 콘텐츠로 채우기: CEO 메시지·Why first·스탯·연혁·오시는 길 ----
HISTORY = [
    ("2018.07", "㈜퍼스트마케팅컴퍼니 설립"),
    ("2019.07", "네이버 · 카카오 공식 대행사"),
    ("2019.12", "혁신바우처 수행기관 등록"),
    ("2020.10", "산업디자인전문회사 등록 (한국디자인진흥원)"),
    ("2021.07", "관광 · 수출바우처 수행기관 등록"),
    ("2022.06", "본사 이전 (대구 섬유회관)"),
    ("2023.06", "베트남 지사 설립"),
    ("2023.08", "기업부설연구소 설립"),
    ("2024.03", "대구지역 일자리창출 · 경제발전 기여 공로패 수상 (대구상공회의소)"),
    ("2026.07", "퍼스트디자인 인천지사 오픈"),
]
hist_html = "".join(f'<div class="abx-h-item"><span>{d}</span><p>{t}</p></div>' for d, t in HISTORY)
WHY = [
    ("01", "하나의 톤으로 완성합니다", "로고, 브로슈어, 촬영까지<br>브랜드의 일관성을 중요하게 생각합니다."),
    ("02", "디자인부터 인쇄까지", "자체 인쇄소를 통해<br>완성도 높은 결과물을 제공합니다."),
    ("03", "프로젝트별 전담팀 구성", "각 분야 담당자가<br>유기적으로 프로젝트를 진행합니다."),
    ("04", "경험이 결과를 만듭니다", "12년 동안 3,200건 이상의 프로젝트를<br>진행하며 디자인 경험을 쌓아왔습니다."),
]
why_html = "".join(f'<div class="abx-why-card"><span>{n}</span><h3>{t}</h3><p>{d}</p></div>' for n, t, d in WHY)
OFFICES = [
    ("인천지사", PHONE, "인천광역시 (상세 주소 곧 안내)", "인천 · 부천 · 시흥 당일 대면 미팅", True),
    ("서울 디자인 스튜디오", "070-4126-1138", "서울시 광진구 능동로49길 9, 2F", "", False),
    ("대구 본사", "1600-9487", "대구광역시 중구 국채보상로 488 섬유회관 3층", "", False),
]
off_html = "".join(
    f'<div class="abx-office{" abx-office--main" if main else ""}">'
    f'<h4>{name}</h4><b>{tel}</b><p>{addr}</p>' + (f'<em>{note}</em>' if note else '') + '</div>'
    for name, tel, addr, note, main in OFFICES)
ABX = f'''<section class="abx-ceo">
    <div class="abx-wrap abx-ceo-inner">
        <p class="abx-ey">CEO MESSAGE</p>
        <div class="abx-quote">“</div>
        <p class="abx-ceo-lead">좋은 디자인은 보기 좋은 결과물이 아니라,<br><b>브랜드의 생각을 전달하는 언어</b>라고 믿습니다.</p>
        <p class="abx-ceo-body">퍼스트디자인은 화려함보다 브랜드에 맞는 방향을 먼저 고민합니다.<br>
        왜 필요한 디자인인지, 누구에게 전달되어야 하는지, 어떤 인상을 남겨야 하는지 —<br>
        결과물 하나에도 분명한 이유가 있어야 한다고 생각합니다.<br>
        브랜드의 중요한 순간을 맡겨주신다면 그 책임감을 잊지 않고 함께하겠습니다.</p>
        <p class="abx-ceo-sign">퍼스트디자인 CEO <b>김우석</b></p>
    </div>
</section>
<section class="abx-why">
    <div class="abx-wrap">
        <p class="abx-ey">WHY FIRST</p>
        <h2 class="abx-t">브랜드의 가치는<br><span>디테일에서 완성됩니다</span></h2>
        <p class="abx-s">기획부터 결과물까지 하나의 흐름으로 완성합니다.</p>
        <div class="abx-why-grid">{why_html}</div>
        <p class="abx-team">아트디렉터 · 프로젝트 매니저 · 편집 디자이너 · UI/UX 디자이너 · 브랜드 촬영 작가 · 지원사업 컨설턴트 등 <b>전문가 35명+</b>가 프로젝트별 전담팀으로 함께합니다</p>
    </div>
</section>
<section class="abx-stats">
    <div class="abx-wrap abx-stats-grid">
        <div><b>12<i>년+</i></b><span>축적된 디자인 노하우</span></div>
        <div><b>3,200<i>+</i></b><span>완료한 프로젝트</span></div>
        <div><b>98<i>%</i></b><span>재의뢰 · 추천율</span></div>
        <div><b>400<i>+</i></b><span>정부지원사업 수행</span></div>
    </div>
</section>
<section class="abx-history">
    <div class="abx-wrap">
        <p class="abx-ey">HISTORY</p>
        <h2 class="abx-t">걸어온 길</h2>
        <div class="abx-h-list">{hist_html}</div>
    </div>
</section>
<section class="abx-offices">
    <div class="abx-wrap">
        <p class="abx-ey">OFFICES</p>
        <h2 class="abx-t">찾아오시는 길</h2>
        <div class="abx-office-grid">{off_html}</div>
    </div>
</section>
'''
h = h.replace('<section class="cta-section">', ABX + '<section class="cta-section">', 1)
h = h.replace("theme/css/pages/about.css' type='text/css' media='all' />",
              "theme/css/pages/about.css' type='text/css' media='all' />\n<link rel='stylesheet' href='theme/css/pages/aboutx.css' />")
out["about"] = h

aboutx_css = """/* 회사소개 확장(본사 콘텐츠) */
/* 배너 삭제 후 서비스분야 하단 여백 축소 */
.about-service{margin-bottom:30px !important}
/* 히어로: 담백한 에디토리얼 (이미지 상단 → 카피 하단) */
.about-hero-top{display:block !important;margin-top:52px}
.about-hero .about-hero-img{margin-top:0}
.about-hero-text{max-width:860px}
.abh-mark{background:linear-gradient(transparent 62%, rgba(18,179,160,.28) 62%);padding:0 2px}
.abx-wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.abx-ey{font-size:13px;font-weight:800;letter-spacing:.2em;color:#0C9384;margin:0 0 12px}
.abx-t{font-size:36px;font-weight:800;letter-spacing:-0.025em;color:#111;line-height:1.35;margin:0 0 14px}
.abx-t span{color:#0C9384}
.abx-s{font-size:16px;color:#767676;margin:0 0 48px}
/* CEO */
.abx-ceo{padding:24px 0 100px;background:#fff}
.abx-ceo-inner{max-width:860px;text-align:center}
.abx-quote{font-size:80px;font-weight:900;color:#0C9384;line-height:.6;margin:26px 0 30px}
.abx-ceo-lead{font-size:28px;font-weight:500;color:#111;line-height:1.55;margin:0 0 28px;letter-spacing:-0.02em}
.abx-ceo-lead b{font-weight:800;color:#0C9384}
.abx-ceo-body{font-size:16.5px;color:#666;line-height:1.9;margin:0 0 34px}
.abx-ceo-sign{font-size:15px;color:#8a8a8a}
.abx-ceo-sign b{font-size:19px;color:#111;margin-left:8px}
/* WHY */
.abx-why{padding:100px 0;background:#f2f7f6}
.abx-why-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.abx-why-card{background:#fff;border:1px solid #e6eceb;border-radius:14px;padding:30px 26px}
.abx-why-card span{font-size:14px;font-weight:800;color:#0C9384;letter-spacing:.08em}
.abx-why-card h3{font-size:18.5px;font-weight:800;color:#111;margin:12px 0 10px;letter-spacing:-0.01em}
.abx-why-card p{font-size:14px;color:#767676;line-height:1.65;margin:0}
.abx-team{margin:34px 0 0;font-size:15px;color:#666;line-height:1.7;text-align:center}
.abx-team b{color:#0C9384}
/* STATS */
.abx-stats{background:linear-gradient(120deg,#0B2E2A 0%,#0d5f55 100%);padding:72px 0}
.abx-stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;text-align:center}
.abx-stats b{display:block;font-size:46px;font-weight:800;color:#fff;letter-spacing:-0.02em}
.abx-stats b i{font-style:normal;font-size:26px;color:#2fd0bd;margin-left:2px}
.abx-stats span{display:block;font-size:14px;color:rgba(255,255,255,.65);margin-top:8px}
/* HISTORY */
.abx-history{padding:100px 0}
.abx-h-list{position:relative;margin-top:10px;padding-left:26px;border-left:2px solid #d8e8e5}
.abx-h-item{position:relative;padding:0 0 30px}
.abx-h-item::before{content:"";position:absolute;left:-33px;top:5px;width:12px;height:12px;border-radius:50%;background:#0C9384;border:3px solid #e7f4f2}
.abx-h-item span{display:block;font-size:14px;font-weight:800;color:#0C9384;margin-bottom:4px}
.abx-h-item p{font-size:16px;color:#333;margin:0;line-height:1.6}
.abx-h-item:last-child{padding-bottom:0}
.abx-h-item:last-child p{font-weight:800;color:#111}
/* OFFICES */
.abx-offices{padding:0 0 110px}
.abx-office-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.abx-office{border:1px solid #e6eceb;border-radius:16px;padding:32px 34px}
.abx-office--main{border:2px solid #0C9384;background:#f2f9f8}
.abx-office h4{font-size:19px;font-weight:800;color:#111;margin:0 0 14px}
.abx-office b{display:block;font-size:24px;font-weight:800;color:#0C9384;margin-bottom:10px}
.abx-office p{font-size:14.5px;color:#666;line-height:1.6;margin:0}
.abx-office em{display:block;font-style:normal;font-size:13px;font-weight:700;color:#0A7A6E;margin-top:12px}
@media (max-width:1024px){
  .abx-why-grid{grid-template-columns:repeat(2,1fr)}
  .abx-stats-grid{grid-template-columns:repeat(2,1fr);row-gap:36px}
  .abx-office-grid{grid-template-columns:1fr}
  .abx-ceo-lead{font-size:21px}
  .abx-t{font-size:28px}
}
"""
(ROOT / "theme" / "css" / "pages" / "aboutx.css").write_text(aboutx_css, encoding="utf-8")

# (아래 리디자인 블록은 비활성 — 코드 보존용)

# ---------- 5-2. portfolio ----------
h = (SCRATCH / "sub-portfolio.html").read_text(encoding="utf-8")
h = localize_common(h, "portfolio")
h = set_title(h, "포트폴리오")
filters = """<div class="pf-filters">
    <button class="pf-filter-btn active" data-filter="all">전체</button>
    <button class="pf-filter-btn" data-filter="책자">카탈로그 · 브로슈어</button>
    <button class="pf-filter-btn" data-filter="리플릿">리플렛 · 팜플렛</button>
    <button class="pf-filter-btn" data-filter="로고">로고 · 브랜딩</button>
    <button class="pf-filter-btn" data-filter="촬영">촬영 · 콘텐츠</button>
    <button class="pf-filter-btn" data-filter="기타">포스터 · 기타</button>
</div>"""
h = re.sub(r'<div class="pf-filters">.*?</div>', filters, h, count=1, flags=re.S)
cards = ""
for src, cat, client, kind in pf_items:
    cards += (f'<div class="pf-card" data-cat="{cat}">'
              f'<div class="pf-card-thumb" data-modal="{src}">'
              f'<div class="pf-card-img" style="background-image:url(\'{src}\')"></div></div>'
              f'<h2 class="pf-card-name">{client}</h2><p class="pf-card-type">{kind}</p></div>\n')
h = re.sub(r'<div class="pf-grid">.*?</div>\s*</div>\s*</section>\s*<!-- 모달 -->',
           '<div class="pf-grid">\n' + cards + '</div>\n    </div>\n</section>\n\n<!-- 모달 -->', h, count=1, flags=re.S)
out["portfolio"] = h

# ---------- 5-3. review — 사용자 지시로 삭제(생성 안 함) ----------
REVIEW_ENABLED = False
h = (SCRATCH / "sub-review.html").read_text(encoding="utf-8")
h = localize_common(h, "review")
h = set_title(h, "고객 후기")
RV = [
    ("banner_kb01.jpg", "KB국민은행", "디자인부터 인쇄까지 빠르게 받아볼 수 있었습니다", "시안을 2가지로 제안해주셔서 선택의 폭이 넓었고, 수정도 신속하게 진행되어 인쇄까지 빠르게 받아볼 수 있었습니다."),
    ("banner_hitejinro01.jpg", "하이트진로", "캐릭터 활용 홍보물, 기대 이상이었습니다", "브랜드 캐릭터의 톤앤매너를 정확히 살려주셔서 내부 반응이 아주 좋았습니다. 다음 시즌 홍보물도 함께하고 싶습니다."),
    ("banner_mirae01.jpg", "미래에셋", "너무 만족스럽고 수정이 필요없네요", "복잡한 금융 정보를 명확하게 풀어주셔서 수정 없이 마무리했습니다. 대표님께서도 감사하다고 전해달라 하시네요."),
    ("banner_Ewha01.jpg", "이화여자대학교", "수정없이 한번에 컨펌되었습니다!", "컨셉이 정해진 것이 없었는데 원하는 디자인으로 잘 나왔습니다. 세미나 포스터 반응이 좋아 다음 행사도 의뢰드릴 예정입니다."),
    ("banner_Gukgwasu01.jpg", "국립과학수사연구원", "보고서·브로슈어 모두 믿고 맡깁니다", "기관 발간물 특성상 검수 기준이 까다로운데도 일정과 품질 모두 정확하게 맞춰주셨습니다."),
    ("banner_samsung01.jpg", "삼성화재", "빠르고 신속한 작업! 다음에 또 요청드리겠습니다!", "리플렛 디자인 의뢰 후 마음에 들어 포스터 디자인까지 의뢰하게 되었네요. 빠르고 친절하게 작업해주셔서 감사드립니다!"),
    ("mainbanner0001.jpg", "Black Loel", "패키지부터 촬영까지 원스톱으로 해결했습니다", "패키지 디자인과 제품 촬영을 한 번에 진행하니 톤이 완벽하게 맞았습니다. 브랜드 론칭 일정도 여유있게 맞췄어요."),
    ("mainbanner0002.jpg", "오뚜기", "전체적으로 디자인이 좋아서 수정할 필요가 없습니다!", "패키지 리뉴얼과 촬영까지 시간 내에 빠르게 진행해주셔서 감사드립니다. 결과물 퀄리티가 기대 이상입니다."),
]
def rv_card(m):
    rv_card.i += 1
    f, client, title, desc = RV[(rv_card.i - 1) % len(RV)]
    return ('<div class="rv-card"><div class="rv-card-thumb">'
            f'<img src="theme/assets/first/{f}" alt="{client}" loading="lazy"></div>'
            f'<div class="rv-card-from"><span>From.</span><span>{client}</span></div>'
            f'<h3 class="rv-card-title">{title}</h3><p class="rv-card-desc">{desc}</p></div>')
rv_card.i = 0
h = re.sub(r'<div class="rv-card">.*?rv-card-desc">[^<]*</p>\s*</div>', rv_card, h, flags=re.S)
if REVIEW_ENABLED:
    out["review"] = h

# ---------- 5-4. column — unwebs.co.kr/blog 레이아웃(사이드바+2열 그리드) ----------
h = (SCRATCH / "sub-column.html").read_text(encoding="utf-8")
h = localize_common(h, "column")
h = set_title(h, "블로그")
h = h.replace("theme/css/pages/column.css", "theme/css/pages/column2.css")
COLS = [  # (슬러그, 썸네일, 제목, 카테고리, 날짜, 분량)
    ("column-design", "theme/assets/first/column-card.png", "좋은 디자인은 무엇이 다를까?", "디자인 일반", "2026.07.20", "4분 분량"),
    ("column-catalog", "theme/assets/first/col-2.png", "카탈로그 제작 전 체크리스트 5가지", "인쇄·홍보물", "2026.07.18", "5분 분량"),
    ("column-logo", "theme/assets/first/col-3.png", "로고 리뉴얼, 언제 해야 할까?", "브랜딩·로고", "2026.07.15", "4분 분량"),
    ("column-print", "theme/assets/first/col-4.png", "인쇄 사고를 막는 원고 준비법", "인쇄·홍보물", "2026.07.12", "5분 분량"),
]
from collections import Counter
cat_counts = Counter(c[3] for c in COLS)
cats_html = (f'<li class="blog-cat-item is-active" data-cat="all"><a href="#" class="blog-cat-link">'
             f'<span class="blog-cat-name">전체</span><span class="blog-cat-count">({len(COLS)})</span></a></li>')
for cat in ["브랜딩·로고", "인쇄·홍보물", "디자인 일반"]:
    cats_html += (f'<li class="blog-cat-item" data-cat="{cat}"><a href="#" class="blog-cat-link">'
                  f'<span class="blog-cat-name">{cat}</span><span class="blog-cat-count">({cat_counts.get(cat,0)})</span></a></li>')
items_html = ""
for slug, img, title, cat, date, mins in COLS:
    items_html += f'''<article class="blog-item" data-cat="{cat}" data-title="{title}">
        <a class="blog-item-link" href="{slug}.html">
            <div class="blog-item-img"><img src="{img}" alt="{title}" loading="lazy"></div>
            <div class="blog-item-info">
                <span class="blog-item-cat">{cat}</span>
                <h3 class="blog-item-tit">{title}</h3>
                <div class="blog-item-meta"><time class="blog-item-date">{date}</time><span class="blog-item-readtime">{mins}</span></div>
            </div>
        </a>
    </article>\n'''
col_main = f'''<main class="site-main">
<section class="blog-list-con">
    <div class="blog-area">
        <nav class="blog-breadcrumb"><a href="index.html">Home</a><span class="sep"> - </span><span>블로그</span></nav>
        <div class="blog-tit-box">
            <span class="blog-tit-sub">카탈로그·브로슈어·로고까지, 제작 전에 알아두면 좋은 인사이트를 확인해 보세요.</span>
            <h2 class="blog-tit">블로그</h2>
        </div>
        <div class="blog-layout">
            <aside class="blog-sidebar">
                <div class="blog-search">
                    <input id="blog-search-input" type="search" class="blog-search-input" placeholder="검색어를 입력해 주세요" autocomplete="off">
                    <button type="button" class="blog-search-btn" aria-label="검색">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    </button>
                </div>
                <h3 class="blog-sidebar-tit">카테고리</h3>
                <ul class="blog-cat-list">{cats_html}</ul>
            </aside>
            <div class="blog-main">
                <div class="blog-list">
{items_html}                </div>
                <div class="blog-empty" style="display:none">검색 결과가 없습니다.</div>
            </div>
        </div>
    </div>
</section>
{CTA2}
</main>
<script>
(function () {{
    var items = document.querySelectorAll('.blog-item');
    var cats = document.querySelectorAll('.blog-cat-item');
    var input = document.getElementById('blog-search-input');
    var empty = document.querySelector('.blog-empty');
    var curCat = 'all';
    function apply() {{
        var q = (input.value || '').trim().toLowerCase();
        var shown = 0;
        items.forEach(function (it) {{
            var ok = (curCat === 'all' || it.getAttribute('data-cat') === curCat)
                  && (!q || it.getAttribute('data-title').toLowerCase().indexOf(q) !== -1);
            it.style.display = ok ? '' : 'none';
            if (ok) shown++;
        }});
        empty.style.display = shown ? 'none' : '';
    }}
    cats.forEach(function (li) {{
        li.querySelector('.blog-cat-link').addEventListener('click', function (e) {{
            e.preventDefault();
            cats.forEach(function (x) {{ x.classList.remove('is-active'); }});
            li.classList.add('is-active');
            curCat = li.getAttribute('data-cat');
            apply();
        }});
    }});
    input.addEventListener('input', apply);
}})();
</script>'''
h = re.sub(r'<main class="site-main">.*?</main>', col_main, h, count=1, flags=re.S)
out["column"] = h

# ---- 칼럼 상세 4종 (unwebs 블로그 싱글 레이아웃) ----
ARTICLES = {
    "column-design": [
        ("보기 좋은 것과 잘 전달되는 것은 다릅니다",
         "<p>디자인 시안을 받아보면 대부분 \"예쁘다\"는 기준으로 판단하게 됩니다. 하지만 카탈로그, 브로슈어, 리플렛 같은 홍보물의 목적은 감상이 아니라 <strong>전달</strong>입니다. 받아본 사람이 3초 안에 무엇을 하는 회사인지, 왜 연락해야 하는지를 이해하지 못하면 아무리 아름다워도 실패한 디자인입니다.</p>"
         "<p>좋은 디자인은 화려한 장식이 아니라 정보의 순서를 설계하는 일에서 시작합니다. 무엇을 가장 크게 보여줄지, 무엇을 과감히 뺄지를 결정하는 것이 디자이너의 첫 번째 일입니다.</p>"),
        ("좋은 디자인의 3가지 조건",
         "<p>12년간 3,200건의 프로젝트를 진행하며 확인한, 성과로 이어지는 디자인의 공통점은 세 가지입니다.</p>"
         "<ul><li><strong>목적이 분명합니다</strong> — 전시회 배포용인지, 관공서 제출용인지, 매장 비치용인지에 따라 판형·분량·톤이 전부 달라집니다.</li>"
         "<li><strong>타깃이 좁습니다</strong> — \"모두에게\"는 \"아무에게도\"와 같습니다. 읽을 사람을 한 명으로 좁힐수록 카피와 이미지가 선명해집니다.</li>"
         "<li><strong>위계가 살아 있습니다</strong> — 제목, 소제목, 본문, 캡션이 한눈에 구분되면 읽지 않아도 훑는 것만으로 내용이 들어옵니다.</li></ul>"),
        ("나쁜 디자인이 더 비싼 이유",
         "<p>저렴하게 제작한 홍보물이 실제로는 더 비싸지는 경우가 많습니다. 전달이 안 되면 배포한 만큼 기회비용이 사라지고, 결국 다시 만들게 되기 때문입니다. 인쇄물은 한 번 찍으면 수정할 수 없습니다.</p>"
         "<blockquote><p>디자인 비용은 제작비가 아니라, 배포될 모든 접점의 첫인상에 대한 투자입니다.</p></blockquote>"),
        ("의뢰 전에 이것만 정리해 보세요",
         "<p>디자인 회사에 의뢰하기 전, 아래 세 가지만 정리되어 있어도 결과물의 방향이 크게 달라집니다.</p>"
         "<ul><li>이 홍보물을 받는 사람은 누구인가</li><li>받은 사람이 해줬으면 하는 행동 한 가지</li><li>참고하고 싶은 레퍼런스 2~3개</li></ul>"
         "<p>정리가 어려우시면 그대로 오셔도 됩니다. 퍼스트디자인 인천지사는 기획 단계부터 함께 정리해 드립니다.</p>"),
    ],
    "column-catalog": [
        ("① 원고 — 다 넣으려 하지 말고 골라내세요",
         "<p>카탈로그 제작에서 가장 오래 걸리는 단계는 디자인이 아니라 원고 정리입니다. 회사의 모든 것을 담으려 하면 아무것도 기억에 남지 않습니다. 페이지당 하나의 메시지를 원칙으로, 꼭 들어가야 할 내용부터 우선순위를 매겨보세요.</p>"),
        ("② 사진 — 해상도가 완성도의 절반입니다",
         "<p>모니터에서 선명해 보이는 웹용 이미지(72dpi)는 인쇄하면 흐릿하게 나옵니다. 인쇄용은 <strong>300dpi 이상</strong>의 원본이 필요합니다. 제품·시설 사진의 원본 파일을 미리 모아두시고, 상태가 좋지 않다면 재촬영을 계획에 넣는 것이 좋습니다.</p>"
         "<blockquote><p>퍼스트디자인은 자체 스튜디오에서 제품·시설 촬영까지 함께 진행할 수 있습니다.</p></blockquote>"),
        ("③ 사양 — 판형·페이지 수·후가공을 먼저",
         "<p>같은 내용이라도 A4 무선제본과 A5 중철제본은 인상도 비용도 완전히 다릅니다. 배포 방식(우편, 대면 전달, 행사장 비치)을 기준으로 판형을 정하고, 페이지 수는 표지 포함 4의 배수로 계획하세요. 무광 코팅, 에폭시, 박 등 후가공은 견적에 미리 반영해야 일정이 어긋나지 않습니다.</p>"),
        ("④ 일정 — 인쇄 1주일을 계산에 넣으세요",
         "<p>평균적인 제작 기간은 디자인 2주 + 인쇄·가공 1주, 총 3주 전후입니다. 행사나 전시회에 맞춰야 한다면 예비일까지 더해 최소 4주 전에는 시작하는 것이 안전합니다. 급한 일정은 가능 여부를 먼저 확인해 주세요.</p>"),
        ("⑤ 배포 — 어디서 쓰일지가 디자인을 결정합니다",
         "<p>바이어 미팅용이라면 회사 신뢰도를 보여주는 구성으로, 전시회 배포용이라면 한 손에 들어오는 판형과 강한 표지로, 관공서 제출용이라면 규정과 가독성 중심으로 — 같은 카탈로그도 쓰임에 따라 설계가 달라집니다. 문의하실 때 배포처를 알려주시면 가장 정확한 제안을 드릴 수 있습니다.</p>"),
    ],
    "column-logo": [
        ("로고 리뉴얼이 필요하다는 4가지 신호",
         "<ul><li>명함·홈페이지·간판마다 로고 색과 모양이 조금씩 다르다</li>"
         "<li>작게 줄이면(앱 아이콘, 도장 등) 뭉개져서 알아볼 수 없다</li>"
         "<li>사업 영역이 바뀌어 로고가 지금의 회사를 설명하지 못한다</li>"
         "<li>10년 전 유행하던 그라디언트·입체 효과가 그대로 남아 있다</li></ul>"
         "<p>두 개 이상 해당된다면 리뉴얼을 검토할 시점입니다.</p>"),
        ("전면 리뉴얼과 리프레시는 다릅니다",
         "<p>모든 리뉴얼이 로고를 완전히 새로 만드는 것은 아닙니다. 인지도가 쌓인 로고라면 형태는 유지하고 컬러·서체·비례만 정돈하는 <strong>리프레시</strong>가 더 효과적일 수 있습니다. 반대로 브랜드 방향 자체가 바뀌었다면 <strong>전면 리뉴얼</strong>이 맞습니다. 어느 쪽인지 판단이 어려우면 현재 로고의 문제를 먼저 진단해 보세요.</p>"),
        ("리뉴얼은 이렇게 진행됩니다",
         "<p>퍼스트디자인의 로고 리뉴얼은 업종·경쟁사·타깃 분석으로 컨셉을 도출하고, 심볼·워드마크·시그니처 조합을 설계한 뒤, 컬러 시스템과 서체 가이드까지 정리해 전달하는 순서로 진행됩니다. 명함·간판·패키지 적용 시안을 함께 드리기 때문에 리뉴얼 후 바로 실무에 적용할 수 있습니다.</p>"),
        ("리뉴얼할 때 꼭 챙길 것",
         "<ul><li><strong>원본 파일(AI)</strong>을 반드시 받아두세요 — 이후 모든 제작물의 기준이 됩니다.</li>"
         "<li>기존 인쇄물·간판의 교체 일정과 비용도 함께 계획하세요.</li>"
         "<li>바뀐 로고의 사용 규정(최소 크기, 여백, 금지 사례)을 문서로 남기세요.</li></ul>"
         "<p>퍼스트디자인은 작업 완료 후 원본 파일을 무상으로 제공합니다.</p>"),
    ],
    "column-print": [
        ("가장 흔한 인쇄 사고 3가지",
         "<p>인쇄는 한 번 찍으면 되돌릴 수 없습니다. 실제로 가장 자주 일어나는 사고는 화려한 실수가 아니라 사소한 누락입니다.</p>"
         "<ul><li>전화번호·주소 오타 (가장 많고, 가장 치명적입니다)</li><li>모니터 색과 인쇄 색의 차이</li><li>재단선에 잘려나간 글자</li></ul>"),
        ("텍스트 — 인쇄 전 원고는 '최종본'이어야 합니다",
         "<p>디자인이 끝난 뒤의 문구 수정은 오탈자를 만드는 가장 큰 원인입니다. 원고는 디자인 시작 전에 확정하고, 시안 검수 때는 디자인이 아니라 <strong>전화번호, 주소, 홈페이지, 이메일, 담당자명</strong>을 소리 내어 읽으며 확인하세요. 숫자는 두 사람이 교차 확인하는 것이 안전합니다.</p>"),
        ("이미지 — RGB와 CMYK는 다른 세계입니다",
         "<p>모니터는 빛(RGB)으로, 인쇄는 잉크(CMYK)로 색을 만듭니다. 형광톤의 밝은 파랑·초록은 인쇄하면 한 톤 가라앉습니다. 중요한 브랜드 컬러가 있다면 시안 단계에서 인쇄 교정지로 확인하는 것이 확실합니다. 이미지 해상도는 300dpi, 로고는 벡터(AI) 원본을 사용하세요.</p>"),
        ("여백 — 재단선 3mm의 법칙",
         "<p>인쇄물은 큰 종이에 인쇄한 뒤 칼로 잘라 만들기 때문에 1~2mm의 재단 오차가 늘 존재합니다. 배경은 사방 3mm 더 크게(블리드), 글자와 로고는 가장자리에서 최소 5mm 안쪽에 배치해야 잘림 사고를 막을 수 있습니다.</p>"
         "<blockquote><p>퍼스트디자인은 인쇄 데이터 검수를 자체 인쇄소와 이중으로 진행합니다.</p></blockquote>"),
        ("최종 검수 체크리스트",
         "<ul><li>연락처·주소·URL 오탈자 확인 (소리 내어 읽기)</li><li>이미지 300dpi · CMYK 변환 확인</li><li>재단 여백 3mm · 안전 여백 5mm 확인</li><li>페이지 순서와 쪽수 확인</li><li>최종 PDF를 처음 보는 사람에게 한 번 더 보여주기</li></ul>"),
    ],
}
_chead = h[:h.find('<main')]
_ctail = h[h.find('</main>') + len('</main>'):]
_ctail = re.sub(r'<script>\s*\(function \(\) \{\s*var items = document\.querySelectorAll\(\'\.blog-item\'\).*?</script>\s*', '', _ctail, flags=re.S)
for ci, (slug, img, title, cat, date, mins) in enumerate(COLS):
    secs = ARTICLES[slug]
    toc_items = "".join(f'<li class="blog-toc-item"><a href="#sec-{i+1}">{t}</a></li>' for i, (t, _) in enumerate(secs))
    body = "".join(f'<h2 id="sec-{i+1}">{t}</h2>{c}' for i, (t, c) in enumerate(secs))
    prev_ = COLS[ci - 1]
    next_ = COLS[(ci + 1) % len(COLS)]
    single = f'''<main class="site-main">
<div class="blog-reading-progress"><span class="blog-reading-progress-bar"></span></div>
<section class="blog-single-con">
    <div class="bs-area">
        <nav class="blog-breadcrumb"><a href="index.html">Home</a><span class="sep"> - </span><a href="column.html">블로그</a><span class="sep"> - </span><span>{title}</span></nav>
        <header class="blog-single-header">
            <a class="blog-single-cat" href="column.html">{cat}</a>
            <h1 class="blog-single-tit">{title}</h1>
            <ul class="blog-single-meta"><li>{date}</li><li>{mins}</li><li>퍼스트디자인 인천지사</li></ul>
        </header>
        <div class="blog-single-thumb"><img src="{img}" alt="{title}"></div>
        <details class="blog-single-toc-mobile"><summary>목차 <span>▾</span></summary><ol>{toc_items}</ol></details>
        <div class="blog-single-body">{body}</div>
        <div class="blog-single-cta">
            <p class="blog-single-cta-sub">FIRST DESIGN INCHEON</p>
            <p class="blog-single-cta-tit">제작을 고민 중이신가요?</p>
            <p class="blog-single-cta-txt">읽으신 내용 그대로, 기획부터 디자인·인쇄·납품까지 한 팀이 진행합니다.</p>
            <div class="blog-single-cta-actions">
                <a href="contact.html" class="bs-btn bs-btn-primary">무료 상담 받기</a>
                <a href="portfolio.html" class="bs-btn bs-btn-ghost">포트폴리오 보기</a>
            </div>
        </div>
        <nav class="blog-single-nav">
            <a class="blog-single-nav-item" href="{prev_[0]}.html"><span class="blog-single-nav-label">이전 글</span><span class="blog-single-nav-tit">{prev_[2]}</span></a>
            <a class="blog-single-nav-item blog-single-nav-next" href="{next_[0]}.html"><span class="blog-single-nav-label">다음 글</span><span class="blog-single-nav-tit">{next_[2]}</span></a>
        </nav>
    </div>
    <aside class="blog-single-toc"><p class="blog-single-toc-tit">CONTENTS</p><ol class="blog-single-toc-list">{toc_items}</ol></aside>
</section>
{CTA2}
</main>
<script>
(function () {{
    var bar = document.querySelector('.blog-reading-progress-bar');
    var body = document.querySelector('.blog-single-body');
    window.addEventListener('scroll', function () {{
        var r = body.getBoundingClientRect();
        var total = r.height - window.innerHeight;
        var done = Math.min(Math.max(-r.top, 0), Math.max(total, 1));
        bar.style.width = (total > 0 ? (done / total) * 100 : 100) + '%';
    }}, {{ passive: true }});
    var links = document.querySelectorAll('.blog-single-toc-list a');
    var heads = document.querySelectorAll('.blog-single-body h2');
    window.addEventListener('scroll', function () {{
        var cur = 0;
        heads.forEach(function (hd, i) {{ if (hd.getBoundingClientRect().top <= 140) cur = i; }});
        links.forEach(function (a, i) {{ a.classList.toggle('is-active', i === cur); }});
    }}, {{ passive: true }});
}})();
</script>'''
    page_h = _chead + single + _ctail
    page_h = re.sub(r'<title>.*?</title>', f'<title>{title} | 퍼스트디자인 인천지사</title>', page_h, flags=re.S)
    out[slug] = page_h

column2_css = """/* 전문 칼럼 — unwebs.co.kr/blog 레이아웃 재현(틸) */
.blog-list-con{padding:96px 0 110px}
.blog-area{max-width:1280px;margin:0 auto;padding:0 24px}
.blog-breadcrumb{font-size:14px;color:#8a8a8a;margin-bottom:28px}
.blog-breadcrumb a{color:#8a8a8a;text-decoration:none}
.blog-breadcrumb a:hover{color:#111}
.blog-breadcrumb .sep{margin:0 6px;opacity:.6}
.blog-tit-box{margin-bottom:0}
.blog-tit-sub{display:block;font-size:15px;color:#767676;margin-bottom:10px}
.blog-tit{font-size:40px;font-weight:800;letter-spacing:-0.03em;color:#111;margin:0}
.blog-layout{display:grid;grid-template-columns:220px 1fr;gap:60px;margin-top:48px}
.blog-sidebar{position:sticky;top:112px;align-self:start}
.blog-search{position:relative;margin-bottom:36px}
.blog-search-input{width:100%;height:46px;padding:0 48px 0 18px;border:1px solid #e3e5e8;border-radius:999px;background:#fff;font-size:14px;color:#111;letter-spacing:-0.01em;transition:border-color .2s;font-family:inherit}
.blog-search-input:focus{outline:none;border-color:#0C9384}
.blog-search-input::placeholder{color:#b5b9c1}
.blog-search-btn{position:absolute;right:6px;top:50%;transform:translateY(-50%);display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:transparent;border:0;border-radius:50%;color:#767676;cursor:pointer;transition:all .2s}
.blog-search-btn:hover{color:#0C9384;background:rgba(12,147,132,.08)}
.blog-sidebar-tit{font-size:22px;font-weight:800;color:#111;margin:0 0 20px;padding-bottom:16px;border-bottom:1px solid #e3e5e8;letter-spacing:-0.02em}
.blog-cat-list{list-style:none;margin:0;padding:0}
.blog-cat-item+.blog-cat-item{border-top:1px solid #f0f1f3}
.blog-cat-link{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:14px 4px;font-size:15px;font-weight:500;color:#767676;text-decoration:none;transition:color .2s;position:relative}
.blog-cat-link::before{content:'';position:absolute;left:-14px;top:50%;width:6px;height:6px;border-radius:50%;background:#0C9384;transform:translateY(-50%) scale(0);transition:transform .2s}
.blog-cat-link:hover{color:#111}
.blog-cat-item.is-active .blog-cat-link{color:#111;font-weight:700}
.blog-cat-item.is-active .blog-cat-link::before{transform:translateY(-50%) scale(1)}
.blog-cat-name{flex:1;letter-spacing:-0.01em}
.blog-cat-count{font-size:13px;color:#8a8a8a;font-weight:500}
.blog-main{min-width:0}
.blog-list{display:grid;grid-template-columns:repeat(2,1fr);gap:32px 24px}
.blog-item-link{display:flex;flex-direction:column;color:#111;background:#f7f8fa;border-radius:16px;overflow:hidden;transition:transform .35s ease,background-color .25s ease;cursor:pointer}
.blog-item-link:hover{transform:translateY(-2px);background:#f1f3f6}
.blog-item-link:hover .blog-item-tit{color:#0C9384}
.blog-item-img{width:100%;aspect-ratio:16/9;overflow:hidden;background:#eef0f2}
.blog-item-img img{width:100%;height:100%;object-fit:cover;transition:transform .6s cubic-bezier(.25,.8,.25,1)}
.blog-item-link:hover .blog-item-img img{transform:scale(1.05)}
.blog-item-info{padding:28px 28px 24px;display:flex;flex-direction:column;gap:10px}
.blog-item-cat{font-size:14px;color:#0C9384;font-weight:600;letter-spacing:-0.01em}
.blog-item-tit{font-size:19px;font-weight:700;line-height:1.45;color:#111;margin:0;letter-spacing:-0.02em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;word-break:keep-all;transition:color .2s}
.blog-item-meta{margin-top:2px;display:flex;align-items:center;gap:10px;font-size:13px;color:#8a8a8a}
.blog-item-readtime{position:relative;padding-left:11px}
.blog-item-readtime::before{content:'';position:absolute;left:0;top:50%;width:1px;height:10px;background:currentColor;opacity:.35;transform:translateY(-50%)}
.blog-empty{text-align:center;padding:80px 0;color:#8a8a8a}
@media (max-width:1024px){
  .blog-layout{grid-template-columns:1fr;gap:36px;margin-top:36px}
  .blog-sidebar{position:static}
  .blog-sidebar-tit{font-size:18px;margin-bottom:12px;padding-bottom:12px}
  .blog-cat-list{display:flex;flex-wrap:wrap;gap:8px}
  .blog-cat-item+.blog-cat-item{border-top:0}
  .blog-cat-link{padding:10px 16px;border:1px solid #e3e5e8;border-radius:999px;background:#fff;font-size:13px}
  .blog-cat-link::before{display:none}
  .blog-cat-item.is-active .blog-cat-link{background:#0C9384;border-color:#0C9384;color:#fff}
  .blog-cat-item.is-active .blog-cat-count{color:#fff;opacity:.85}
  .blog-list{grid-template-columns:repeat(2,1fr);gap:28px 20px}
  .blog-item-info{padding:24px 22px 20px}
  .blog-item-tit{font-size:17px}
}
@media (max-width:640px){.blog-list{grid-template-columns:1fr;gap:24px}.blog-tit{font-size:30px}}
/* ===== 칼럼 상세 (unwebs 블로그 싱글) ===== */
.blog-reading-progress{position:fixed;top:0;left:0;width:100%;height:3px;background:transparent;z-index:1999;pointer-events:none}
.blog-reading-progress-bar{display:block;height:100%;width:0;background:#0C9384;transition:width .1s linear}
.blog-single-con{padding:80px 24px 40px;position:relative}
.bs-area{max-width:780px;margin:0 auto}
.blog-single-header{text-align:center;padding:16px 0 56px;border-bottom:1px solid #e3e5e8;margin-bottom:56px}
.blog-single-cat{display:inline-flex;align-items:center;height:30px;padding:0 14px;font-size:13px;font-weight:600;color:#0C9384;background:rgba(12,147,132,.08);border-radius:999px;margin-bottom:24px;text-decoration:none}
.blog-single-cat:hover{background:rgba(12,147,132,.15)}
.blog-single-tit{font-size:38px;font-weight:800;line-height:1.35;letter-spacing:-0.03em;color:#111;margin:0 0 28px;word-break:keep-all}
.blog-single-meta{list-style:none;display:inline-flex;flex-wrap:wrap;justify-content:center;gap:22px;margin:0;padding:0}
.blog-single-meta li{font-size:14px;color:#8a8a8a;letter-spacing:-0.01em}
.blog-single-thumb{margin-bottom:56px;border-radius:16px;overflow:hidden;aspect-ratio:16/9}
.blog-single-thumb img{width:100%;height:100%;object-fit:cover;display:block}
.blog-single-body{font-size:17px;line-height:1.85;color:#333;letter-spacing:-0.01em;word-break:keep-all}
.blog-single-body h2{font-size:28px;font-weight:800;line-height:1.35;color:#111;margin:64px 0 20px;padding-bottom:14px;border-bottom:1px solid #e3e5e8;letter-spacing:-0.025em}
.blog-single-body h2:first-child{margin-top:0}
.blog-single-body p{margin:0 0 1.2em}
.blog-single-body strong{color:#111;font-weight:700}
.blog-single-body ul{padding-left:1.5em;margin:0 0 1.2em}
.blog-single-body ul li{list-style:disc;margin-bottom:.5em}
.blog-single-body blockquote{margin:28px 0;padding:20px 28px;border-left:4px solid #0C9384;background:rgba(12,147,132,.05);border-radius:0 10px 10px 0;color:#111}
.blog-single-body blockquote p:last-child{margin-bottom:0}
.blog-single-toc-mobile{display:none;margin:0 0 36px;padding:18px 22px;background:#f6f6f6;border-radius:12px}
.blog-single-toc-mobile summary{display:flex;align-items:center;justify-content:space-between;font-size:14px;font-weight:700;color:#111;cursor:pointer;list-style:none}
.blog-single-toc-mobile summary::-webkit-details-marker{display:none}
.blog-single-toc-mobile ol{list-style:none;margin:14px 0 0;padding:14px 0 0;border-top:1px solid #e3e5e8}
.blog-single-toc-mobile a{display:block;padding:6px 0;font-size:14px;color:#767676;line-height:1.5;text-decoration:none}
.blog-single-toc-mobile a:hover{color:#0C9384}
.blog-single-toc{display:block;position:fixed;top:150px;left:calc(50% + 390px + 56px);width:190px;max-height:calc(100vh - 240px);overflow-y:auto;padding:4px 0 4px 16px;border-left:1px solid #e3e5e8}
.blog-single-toc-tit{font-size:11px;font-weight:700;letter-spacing:.18em;color:#8a8a8a;margin:0 0 12px;text-transform:uppercase}
.blog-single-toc-list{list-style:none;margin:0;padding:0}
.blog-single-toc-list li{margin:4px 0}
.blog-single-toc-list a{display:block;padding:3px 0;font-size:12px;line-height:1.5;color:#8a8a8a;text-decoration:none;word-break:keep-all;transition:color .2s}
.blog-single-toc-list a:hover{color:#111}
.blog-single-toc-list a.is-active{color:#0C9384;font-weight:700}
@media (max-width:1400px){.blog-single-toc{display:none}.blog-single-toc-mobile{display:block}}
.blog-single-cta{margin-top:64px;padding:48px 40px;background:linear-gradient(135deg,rgba(12,147,132,.06) 0%,rgba(12,147,132,.02) 100%);border:1px solid rgba(12,147,132,.15);border-radius:16px;text-align:center}
.blog-single-cta-sub{font-size:13px;font-weight:700;color:#0C9384;margin:0 0 8px;letter-spacing:.08em}
.blog-single-cta-tit{font-size:24px;font-weight:800;color:#111;margin:0 0 12px;letter-spacing:-0.02em}
.blog-single-cta-txt{font-size:15px;color:#767676;margin:0 0 28px}
.blog-single-cta-actions{display:inline-flex;flex-wrap:wrap;justify-content:center;gap:10px}
.bs-btn{display:inline-flex;align-items:center;gap:8px;height:50px;padding:0 28px;border-radius:999px;font-size:15px;font-weight:600;text-decoration:none;transition:all .2s}
.bs-btn-primary{background:#0C9384;color:#fff}
.bs-btn-primary:hover{background:#111;transform:translateY(-2px)}
.bs-btn-ghost{background:#fff;color:#111;border:1px solid #e3e5e8}
.bs-btn-ghost:hover{border-color:#111}
.blog-single-nav{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:64px 0 40px}
.blog-single-nav-item{display:flex;flex-direction:column;gap:8px;padding:24px 28px;background:#f7f8fa;border-radius:12px;color:#111;text-decoration:none;transition:background .2s;min-height:96px}
.blog-single-nav-item:hover{background:#eef0f4}
.blog-single-nav-next{text-align:right}
.blog-single-nav-label{font-size:13px;color:#8a8a8a}
.blog-single-nav-tit{font-size:15px;font-weight:600;line-height:1.5}
@media (max-width:768px){.blog-single-tit{font-size:26px}.blog-single-body{font-size:15.5px}.blog-single-body h2{font-size:21px;margin:40px 0 16px}.blog-single-nav{grid-template-columns:1fr}}
"""
(ROOT / "theme" / "css" / "pages" / "column2.css").write_text(column2_css, encoding="utf-8")

# ---------- 5-5. notice — 사용자 지시로 삭제(생성 안 함) ----------
NOTICE_ENABLED = False
h = (SCRATCH / "sub-notice.html").read_text(encoding="utf-8")
h = localize_common(h, "notice")
h = set_title(h, "공지사항")
filters = """<div class="nt-filters">
    <button class="nt-filter active" data-cat="all">전체</button>
    <button class="nt-filter" data-cat="마감 안내">마감 안내</button>
    <button class="nt-filter" data-cat="휴무 일정">휴무 일정</button>
    <button class="nt-filter" data-cat="기타">기타</button>
</div>"""
h = re.sub(r'<div class="nt-filters">.*?</div>', filters, h, count=1, flags=re.S)
NT = [("기타", "홈페이지 오픈 및 포트폴리오 업데이트", "2026-07-20"),
      ("마감 안내", "2026년 7월, 제작 마감 임박 안내", "2026-07-18"),
      ("휴무 일정", "2026년 8월, 여름 휴무 안내", "2026-07-15"),
      ("기타", "퍼스트디자인 인천지사 오픈 안내", "2026-07-01"),
      ("마감 안내", "2026년 6월, 제작 마감 안내", "2026-06-30")]
rows = ""
for cat, title, date in NT:
    mod = " nt-row-cat--deadline" if cat == "마감 안내" else ""
    rows += (f'<div class="nt-row"><span class="nt-row-cat{mod}">{cat}</span>'
             f'<span class="nt-row-title">{title}</span><span class="nt-row-date">{date}</span></div>\n')
h = re.sub(r'<(a|div)[^>]*class="nt-row"[^>]*>.*?</\1>\s*', "", h, flags=re.S)
h = re.sub(r'(<div class="nt-thead">.*?</div>)', r"\1\n" + rows, h, count=1, flags=re.S)
h = re.sub(r'<div class="nt-pagination">.*?</div>', "", h, flags=re.S)
h = h.replace("</body>", """<script>
document.querySelectorAll('.nt-filter').forEach(function(btn){
    btn.addEventListener('click', function(){
        document.querySelectorAll('.nt-filter').forEach(function(b){b.classList.remove('active');});
        btn.classList.add('active');
        var cat = btn.getAttribute('data-cat');
        document.querySelectorAll('.nt-row').forEach(function(row){
            var c = row.querySelector('.nt-row-cat').textContent.trim();
            row.style.display = (cat === 'all' || c === cat) ? '' : 'none';
        });
    });
});
</script>
</body>""")
if NOTICE_ENABLED:
    out["notice"] = h

# ---------- 5-6. contact ----------
h = (SCRATCH / "sub-contact.html").read_text(encoding="utf-8")
h = localize_common(h, "contact")
h = set_title(h, "문의하기")
h = re.sub(r'action="https://poedit\.co\.kr/contact-processing/"', 'action="#"', h)
# 페이지 전용 인라인 스크립트(폼 제출 로직) 제거 → mailto 핸들러로 대체
scripts = re.findall(r'<script(?![^>]*src)[^>]*>.*?</script>', h, flags=re.S)
for s in scripts:
    if len(s) > 3500 and ("form" in s or "submit" in s or "fetch" in s):
        h = h.replace(s, "")
h = h.replace("</body>", """<script>
(function(){
    var form = document.querySelector('.ct-form');
    if(!form) return;
    form.addEventListener('submit', function(e){
        e.preventDefault();
        var lines = [];
        form.querySelectorAll('input, select, textarea').forEach(function(el){
            if(el.type === 'file' || el.type === 'submit') return;
            if((el.type === 'radio' || el.type === 'checkbox') && !el.checked) return;
            var label = el.closest('.ct-field') ? (el.closest('.ct-field').querySelector('.ct-field-label')||{}).textContent : el.name;
            var val = el.value;
            if(val) lines.push((label||'').trim() + ' : ' + val);
        });
        var body = encodeURIComponent('[퍼스트디자인 인천지사 문의]\\n\\n' + lines.join('\\n'));
        location.href = 'mailto:firstmk1111@gmail.com?subject=' + encodeURIComponent('[인천지사 문의] 프로젝트 상담 요청') + '&body=' + body;
    });
})();
</script>
</body>""")
out["contact"] = h

for p, h in out.items():
    (ROOT / f"{p}.html").write_text(h, encoding="utf-8")
    print("written", p, len(h))

# ---------- 6. index.html 네비 앵커 → 실제 페이지 ----------
idx = (ROOT / "index.html").read_text(encoding="utf-8")
for p in PAGES:
    idx = idx.replace(f'href="#{p}"', f'href="{p}.html"')
(ROOT / "index.html").write_text(idx, encoding="utf-8")
print("index nav linked")
