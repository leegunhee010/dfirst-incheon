# -*- coding: utf-8 -*-
"""퍼스트디자인 인천지사 오버레이: 브랜딩 치환 + 퍼스트 실적 교체 + 틸 리컬러.
_mirror.py 실행 후 돌린다. index.html을 다시 만들려면 _mirror.py → _overlay.py 순."""
import os, re, json, html as htmlmod, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
HOME = pathlib.Path(os.path.expanduser("~"))
IMG = ROOT / "theme" / "assets" / "images"
FIRST = ROOT / "theme" / "assets" / "first"
FIRST.mkdir(parents=True, exist_ok=True)

PRIMARY = "#0C9384"   # 인천 딥 틸
PRIMARY_DARK = "#0A7A6E"
PHONE = "1600-9487"   # 본사 대표번호(인천 전용번호 확정 시 교체)
EMAIL = "firstmk1111@gmail.com"

# ---------- 1. 퍼스트 실적 이미지 복사 ----------
SRC = HOME / "dfirst-new" / "assets"
HERO = [  # (파일, 기관, 제작유형, 설명)
    ("banner_Gukgwasu01.jpg", "국립과학수사연구원", "브로슈어 제작", "'진실을 밝히는 과학의 힘' 기관 브로슈어"),
    ("banner_samsung01.jpg", "삼성화재", "리플렛 제작", "신상품 출시 안내 리플렛"),
    ("banner_kb01.jpg", "KB국민은행", "사보 제작", "글로벌 네트워크 사보 내지 디자인"),
    ("banner_mirae01.jpg", "미래에셋", "3단 리플렛 제작", "태아·어린이보험 안내 리플렛"),
    ("banner_Ewha01.jpg", "이화여자대학교", "포스터 제작", "AI 산학협력·미래전망 세미나 포스터"),
    ("banner_hitejinro01.jpg", "하이트진로", "홍보물 제작", "두꺼비 캐릭터 홍보 리플렛"),
    ("mainbanner0001.jpg", "Black Loel", "패키지 디자인", "브랜드 패키지·어플리케이션 디자인"),
]
PORTFOLIO_L = [  # (파일, 유형, 클라이언트, wide)
    ("gallery/g02.png", "전시 브로슈어", "문화예술 전시관", False),
    ("gallery/g11.png", "회사소개서", "IT·데이터 기업", True),
    ("gallery/g17.png", "카탈로그", "해양장비 제조기업", False),
    ("gallery/g21.jpg", "명함·브랜딩", "프랜차이즈 브랜드", False),
    ("gallery/g23.jpg", "홈페이지", "HD코퍼레이션", True),
]
PORTFOLIO_R = [
    ("gallery/g09.jpg", "명함 디자인", "MG건설", False),
    ("gallery/g04.jpg", "캠페인 브로슈어", "KOMA", True),
    ("gallery/g26.png", "3단 리플렛", "Wemico", False),
    ("gallery/g38.png", "안내 책자", "공공기관 캠페인", False),
    ("gallery/g29.png", "브로슈어", "제약·바이오 기업", True),
]
PROMISE = [  # 뉴스섹션 대체 3카드
    ("mainbanner0003.jpg", "인천·부천·시흥 서부수도권<br>당일 대면 미팅이 가능합니다"),
    ("mainbanner0002.jpg", "디자인부터 인쇄·촬영·패키지까지<br>원스톱으로 진행합니다"),
    ("mainbanner0004.jpg", "본사 12년 제작 노하우를<br>인천에서 그대로 만나보세요"),
]
REVIEW_LOGOS = ["LOGO_Kookmin-bank.jpg", "LOGO_hite-jinro.jpg", "LOGO_mirae.jpg",
                "LOGO_ewha-university.png", "LOGO_nationalforensic-logo.jpg",
                "LOGO_samsung-bio.jpg", "LOGO_cj-enm.png", "LOGO_k-league.jpg"]

for f, *_ in HERO + PORTFOLIO_L + PORTFOLIO_R + PROMISE:
    shutil.copy(SRC / f, FIRST / os.path.basename(f))
for f in REVIEW_LOGOS:
    shutil.copy(SRC / "partners" / f, FIRST / f)
shutil.copy(HOME / "dfirst-busan-v2" / "theme" / "images" / "main" / "ourclients.png",
            FIRST / "ourclients.png")

# ---------- 2. 생성 이미지 (파비콘 / 칼럼 카드) ----------
from PIL import Image, ImageDraw, ImageFont
def font(sz, bold=True):
    for name in (["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf"]):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, sz)
        except OSError:
            pass
    return ImageFont.load_default()

fav = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
d = ImageDraw.Draw(fav)
d.rounded_rectangle([0, 0, 127, 127], 28, fill=PRIMARY)
d.text((64, 60), "F", font=font(84), fill="white", anchor="mm")
fav.save(FIRST / "favicon.png")

card = Image.new("RGB", (826, 464), "#0B2E2A")
d = ImageDraw.Draw(card)
for x in range(826):  # 틸 그라디언트
    t = x / 826
    r = int(11 + (12 - 11) * t); g = int(46 + (147 - 46) * t); b = int(42 + (132 - 42) * t)
    d.line([(x, 0), (x, 464)], fill=(r, g, b))
d.rounded_rectangle([56, 96, 300, 144], 22, fill=PRIMARY)
d.text((178, 120), "퍼스트디자인 블로그", font=font(20), fill="white", anchor="mm")
d.text((56, 190), "좋은 디자인은 무엇이 다를까?", font=font(40), fill="white", anchor="lm")
d.text((56, 250), "카탈로그·브로슈어·로고까지, 제작 전에 알아두면 좋은 이야기", font=font(20, False), fill=(210, 230, 227), anchor="lm")
d.text((56, 392), "FIRST DESIGN INCHEON", font=font(18), fill=(150, 190, 185), anchor="lm")
card.save(FIRST / "column-card.png")

# ---------- 3. 오렌지 → 틸 hue-shift (그래픽 이미지만, 사진 제외) ----------
HUESHIFT = ["Group-799.png", "Group-800.png", "Group-801.png", "Group-802.png",
            "Group-803.png", "Group-804.png", "difference-icon.png",
            "Group-813-1.png", "Group-809-1.png", "Group-811-1.png",
            "mob-차이점1.png", "mob-차이점3.png", "mob-차이점4.png",
            "그라디언트_배경.png", "맞춤디자이너_배경.png", "mob-datasection_bg.png",
            "process-bg.png", "mob-process_bg.png", "이동.png", "Group-547.png"]

def shift_orange_to_teal(path):
    im = Image.open(path)
    has_a = im.mode in ("RGBA", "LA", "P")
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    hsv = rgba.convert("RGB").convert("HSV")
    h, s, v = hsv.split()
    hd, sd = h.load(), s.load()
    w, ht = h.size
    for y in range(ht):
        for x in range(w):
            hue = hd[x, y]
            if hue <= 40 and sd[x, y] >= 8:  # 오렌지·피치 계열
                hd[x, y] = (hue + 110) % 256   # → 틸
    out = Image.merge("HSV", (h, s, v)).convert("RGB")
    out = Image.merge("RGBA", (*out.split(), a)) if has_a else out
    out.save(path)

marker = ROOT / ".hueshift-done"
if not marker.exists():
    for name in HUESHIFT:
        p = IMG / name
        if p.exists():
            shift_orange_to_teal(p)
            print("hue", name)
    marker.write_text("done")

# ---------- 4. index.html 오버레이 ----------
html = (ROOT / "index.html").read_text(encoding="utf-8")

SITE = "퍼스트디자인 인천지사"
TITLE = "퍼스트디자인 인천지사 – 카탈로그·브로슈어·리플렛·포스터·로고 디자인 전문"
DESC = "인천·부천·서부수도권 기업·관공서·교육기관 전문 디자인 제작소, 퍼스트디자인 인천지사"

# head
html = re.sub(r"<title>.*?</title>", "<title>" + TITLE + "</title>", html, flags=re.S)
html = re.sub(r'(<meta name="description" content=")[^"]*', r"\1" + DESC, html)
html = re.sub(r'(<meta property="og:site_name" content=")[^"]*', r"\1" + SITE, html)
html = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\1" + TITLE, html)
html = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\1" + DESC, html)
html = re.sub(r'(<meta property="og:image" content=")[^"]*', r"\1theme/assets/first/banner_Gukgwasu01.jpg", html)
html = re.sub(r'<meta property="og:url"[^>]*>\n?', "", html)
html = re.sub(r'<link rel="canonical"[^>]*/>\n?', "", html)
html = re.sub(r'<meta name="(naver|google)-site-verification"[^>]*/>\n?', "", html)
html = re.sub(r'<link rel="(icon|apple-touch-icon)"[^>]*/?>\n?', "", html)
html = re.sub(r'<meta name="msapplication-TileImage"[^>]*/>\n?', "", html)
html = html.replace("</head>", '<link rel="icon" type="image/png" href="theme/assets/first/favicon.png">\n'
                    '<link rel="stylesheet" href="theme/css/incheon.css">\n</head>')

# JSON-LD
biz = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": SITE,
       "description": DESC, "telephone": "+82-" + PHONE.replace("-", "-"), "email": EMAIL,
       "address": {"@type": "PostalAddress", "addressCountry": "KR", "addressRegion": "인천광역시"},
       "parentOrganization": {"@type": "Organization", "name": "㈜퍼스트마케팅컴퍼니"}}
html = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema\.org","@type":"LocalBusiness".*?</script>',
              '<script type="application/ld+json">' + json.dumps(biz, ensure_ascii=False) + "</script>", html, flags=re.S)

# 상단바: 월 한정 건수 20→12, 잔여 8→5
html = html.replace("매달 20건의 프로젝트만 진행합니다.", "이번 달 신규 프로젝트 12건만 진행합니다.")
html = html.replace('<span class="top-box center" id="remaining-projects">8</span>', '<span class="top-box center" id="remaining-projects">5</span>')

# 로고 → 텍스트 (헤더 / 모바일메뉴 / 푸터)
LOGO = ('<span class="logo-first">퍼스트<em>디자인</em><small>인천지사</small></span>')
html = re.sub(r'<img src="theme/assets/images/포에디트_로고_헤더\.png"[^>]*/>', LOGO, html)

# 문의현황 티커 메시지
msgs = [
    {"text": "송도 바이오 기업으로부터 [브로슈어 · 회사소개서] 상담 설문지가 접수되었습니다.", "date": "2일 전"},
    {"text": "남동공단 제조기업으로부터 [카탈로그 · 리플렛] 상담 설문지가 접수되었습니다.", "date": "3일 전"},
    {"text": "부평 소재 병원으로부터 [리플렛 · 포스터] 상담 설문지가 접수되었습니다.", "date": "4일 전"},
    {"text": "인천 관공서로부터 [소식지 · 백서] 상담 설문지가 접수되었습니다.", "date": "6일 전"},
]
html = re.sub(r"data-messages='[^']*'", "data-messages='" + htmlmod.escape(json.dumps(msgs, ensure_ascii=False), quote=True).replace("'", "&#39;") + "'", html)

# ---- 히어로 재구성: beauwell.kr 골격(헤드라인+대형 배너 캐러셀 01/04 + 우측 카드 2장) ----
BW_SLIDES = [
    {"h2": '결과로 증명하는<br><b>공공기관</b> 디자인 파트너',
     "img": "theme/assets/first/banner_Gukgwasu01.jpg", "cat": "브로슈어 제작",
     "desc": "국립과학수사연구원 — '진실을 밝히는 과학의 힘'<br>기관 브로슈어 기획·디자인·인쇄"},
    {"h2": '금융권이 선택한<br><b>정확한</b> 편집 디자인',
     "img": "theme/assets/first/banner_kb01.jpg", "cat": "사보 제작",
     "desc": "KB국민은행 — 글로벌 네트워크 사보 내지<br>복잡한 정보를 명확한 편집으로"},
    {"h2": '캠페인의 얼굴을 만드는<br><b>포스터</b> 디자인',
     "img": "theme/assets/first/banner_Ewha01.jpg", "cat": "포스터 제작",
     "desc": "이화여자대학교 — AI 산학협력 세미나 포스터<br>행사·전시·프로모션 포스터 제작"},
]
slides_html = ""
for i, s in enumerate(BW_SLIDES):
    on = " on" if i == 0 else ""
    if s.get("promo"):
        bnr = ('<a class="bw-bnr bw-promo" href="contact.html">'
               '<div class="bw-promo-txt">'
               '<span class="bw-badge">이번 달 신규 프로젝트 12건 한정</span>'
               '<strong>인천지사 오픈,<br>첫 상담을 환영합니다</strong>'
               '<p>본사 12년 노하우 그대로 —<br>기획부터 디자인 · 인쇄 · 납품까지 원스톱</p>'
               '<em>인천 · 부천 · 시흥 서부수도권 당일 대면 미팅</em>'
               '</div>'
               '<div class="bw-promo-imgs">'
               '<img class="pi1" src="theme/assets/first/g29.png" alt="브로슈어" loading="lazy">'
               '<img class="pi2" src="theme/assets/first/g02.png" alt="브로슈어" loading="lazy">'
               '<img class="pi3" src="theme/assets/first/g04.jpg" alt="포스터" loading="lazy">'
               '</div></a>')
    else:
        bnr = (f'<a class="bw-bnr" href="portfolio.html">'
               f'<img src="{s["img"]}" alt="{s["cat"]}" loading="lazy">'
               f'<div class="bw-txt"><div class="bw-cat">{s["cat"]}</div><p>{s["desc"]}</p></div></a>')
    slides_html += f'<div class="bw-slide{on}"><h2>{s["h2"]}</h2>{bnr}</div>\n'
hero_html = f'''<section class="bw-hero">
    <div class="bw-main">
        <div class="bw-ctrl"><span class="bw-count"><b class="cur">01</b> / 0{len(BW_SLIDES)}</span>
            <button class="bw-next" aria-label="다음">
                <svg xmlns="http://www.w3.org/2000/svg" width="46" height="16" viewBox="0 0 46 16" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="0" y1="15" x2="44" y2="15"/><path d="M32 3l12 12"/></svg>
            </button></div>
{slides_html}    </div>
    <div class="bw-aside">
        <a class="bw-card bw-card-photo" href="contact.html">
            <img src="theme/assets/first/office.jpg" alt="퍼스트디자인 인천지사" loading="lazy">
            <span class="bw-cap">본사 12년 노하우 그대로,<br>인천에서 바로 만나보세요</span>
            <span class="bw-tit"><small>퍼스트디자인 인천지사</small>전문가 1:1 대면 상담</span>
        </a>
        <a class="bw-card bw-card-grad" href="portfolio.html">
            <img src="theme/assets/first/g29.png" alt="포트폴리오" loading="lazy">
            <span class="bw-tit"><strong>포트폴리오 3,200+</strong>실제 작업물로<br>퀄리티를 확인하세요</span>
        </a>
    </div>
</section>
<script>
(function () {{
    var slides = document.querySelectorAll('.bw-slide');
    var cur = document.querySelector('.bw-count .cur');
    if (!slides.length) return;
    var i = 0, n = slides.length, timer;
    function go(k) {{
        slides[i].classList.remove('on');
        i = (k + n) % n;
        slides[i].classList.add('on');
        cur.textContent = ('0' + (i + 1)).slice(-2);
    }}
    function start() {{ timer = setInterval(function () {{ go(i + 1); }}, 4500); }}
    document.querySelector('.bw-next').addEventListener('click', function () {{
        clearInterval(timer); go(i + 1); start();
    }});
    start();
}})();
</script>'''
html = re.sub(r'<section class="hero-section">.*?</section>', hero_html, html, count=1, flags=re.S)
# 스와이퍼 의존 제거(히어로가 사라졌으므로)
html = re.sub(r"<link[^>]*swiper-bundle\.min\.css[^>]*/>\n?", "", html)
html = re.sub(r"<script[^>]*swiper-bundle\.min\.js[^>]*></script>\n?", "", html)
html = re.sub(r"<script[^>]*js/swiper-init\.js[^>]*></script>\n?", "", html)

# ---- 상단바 전체 삭제(사용자 지시) ----
html = re.sub(r'<div class="top-bar">.*?</div>\s*<div class="divider-line"></div>\s*', "", html, count=1, flags=re.S)

# ---- 소개 타이틀 + 로고월 ----
html = html.replace("인쇄물 제작소, 포에디트", "디자인 제작소, 퍼스트디자인 인천지사")
html = re.sub(r'<img src="theme/assets/images/로고-scaled\.png"[^>]*>',
              '<img src="theme/assets/first/ourclients.png" alt="퍼스트디자인 고객사 로고" class="logo-desktop" loading="lazy">', html)
html = re.sub(r'<img src="theme/assets/images/Mob-ourclients\.png"[^>]*>',
              '<img src="theme/assets/first/ourclients.png" alt="퍼스트디자인 고객사 로고" class="logo-mobile" loading="lazy">', html)

# ---- 통계: 본사 공식 수치(12년+ / 3,200+ / 98% / 400+) ----
def stat(label, number, suffix):
    wraps = '<div class="count-num-item-wrap"><ul class="count-num-item-box"></ul></div>' * len(str(number))
    cls = "percent" if suffix == "%" else "plus"
    sfx = f'<span class="{cls}">{suffix}</span>'
    return (f'<div class="stat-item"><span class="stat-label">{label}</span>'
            f'<div class="stat-number" data-number="{number}">{wraps}{sfx}</div></div>')
stats_html = ('<section class="stats-section"><div class="stats-container">'
              + stat("축적된 디자인 노하우", 12, "년+") + '<div class="stat-divider"></div>'
              + stat("완료한 프로젝트", 3200, "+") + '<div class="stat-divider"></div>'
              + stat("재의뢰 · 추천율", 98, "%") + '<div class="stat-divider"></div>'
              + stat("정부지원사업 수행", 400, "+") + "</div></section>")
html = re.sub(r'<section class="stats-section">.*?</section>', stats_html, html, count=1, flags=re.S)

# ---- 포트폴리오: 포에디트 2열 패럴랙스 → 오버레이 라벨 3열 그리드 ----
picks = (PORTFOLIO_L + PORTFOLIO_R)[:9]
tiles = ""
for f, kind, client, _ in picks:
    src = "theme/assets/first/" + os.path.basename(f)
    tiles += (f'<a class="ih-pf-item" href="portfolio.html" style="background-image:url(\'{src}\')">'
              f'<div class="ih-pf-label"><h3>{kind}</h3><p>{client}</p></div></a>\n')
grid = f'<div class="ih-pf-grid">\n{tiles}</div>'
html = re.sub(r'<div class="portfolio-grid">.*?(?=<div class="portfolio-more">)', grid, html, count=1, flags=re.S)
# 패럴랙스 스크립트 제거(옛 그리드 전용)
html = re.sub(r"<script>\s*\(function\(\) \{\s*var left = document\.querySelector\('\.portfolio-col-left'\).*?</script>", "", html, count=1, flags=re.S)

# ---- 프로세스: 아이콘 그리드 → 번호 타임라인 ----
STEPS = [("01", "문의/상담", "설문지로 프로젝트를<br>파악합니다"),
         ("02", "초안 제작", "디자인 초안을<br>제작합니다"),
         ("03", "시안 디자인", "확정된 초안으로<br>디자인이 진행됩니다"),
         ("04", "피드백/수정", "피드백을 토대로<br>수정 작업을 진행합니다"),
         ("05", "인쇄/가공", "고품질 인쇄와<br>가공이 진행됩니다"),
         ("06", "납품", "기한에 맞추어<br>납품합니다")]
steps_html = ('<div class="ih-steps">'
              + "".join(f'<div class="ih-step"><span class="ih-step-no">{n}</span>'
                        f'<h3>{t}</h3><p>{d}</p></div>' for n, t, d in STEPS)
              + "</div>")
html = re.sub(r'<div class="process-grid">.*?</div>\s*</section>', steps_html + "\n    </div>\n</section>", html, count=1, flags=re.S)

# ---- 뉴스 섹션 → 인천지사 강점 3카드 ----
promise_cards = ""
for i, (f, title) in enumerate(PROMISE, 1):
    src = "theme/assets/first/" + os.path.basename(f)
    promise_cards += (f'<a href="#contact" class="news-link"><div class="news-card">'
                      f'<div class="news-imgbox"><img src="{src}" class="news-img" alt="퍼스트디자인 인천지사" loading="lazy"></div>'
                      f'<div class="news-meta"><div class="news-num">0{i}</div>'
                      f'<div class="news-title">{title}</div></div></div></a>\n')
news_html = f'''<section class="news-section">
    <div class="news-header">
        <p class="section-label">가까이 있어 더 빠릅니다</p>
        <p class="section-heading">왜 퍼스트디자인 인천지사일까요?</p>
    </div>
    <div class="scroll-wrap" id="scrollContainer"><div class="news-carousel-track">
{promise_cards}    </div></div>
    <div class="scroll-progress-wrap"><div class="scroll-progress-bar" id="scrollProgressBar"></div></div>
</section>'''
html = re.sub(r'<section class="news-section">.*?</section>', news_html, html, count=1, flags=re.S)

# ---- 포에디트 전용 섹션 제거(대체 불가 자산) ----
# 섹션 7: 고객 리뷰(사용자 지시로 후기 전체 삭제)
html = re.sub(r'<!-- ========== 섹션 7:.*?-->\s*<section class="review-section">.*?</section>\s*', "", html, flags=re.S)
# 네비의 고객 후기 항목 제거(데스크톱+모바일)
html = re.sub(r'\s*<a href="#review"[^>]*>(?:<span[^>]*>)?고객 후기(?:</span>)?</a>', "", html)
# 섹션 8: 3D 디자이너 아바타 캐러셀(제임스·소피아 등 = 포에디트 캐릭터)
html = re.sub(r'<!-- ========== 섹션 8:.*?-->\s*<section class="designer-section">.*?</section>\s*', "", html, flags=re.S)
# 섹션 9: 차별점(소아암재단 목업·포에디트 팀 사진·라이선스 UI 등 포에디트 실물 이미지) + 제어 스크립트
html = re.sub(r'<!-- ========== 섹션 9:.*?-->\s*<section class="difference-section">.*?</section>\s*<script>.*?</script>\s*', "", html, flags=re.S)

# ---- 차별점: 20건 → 12건 ----
html = html.replace("매월 20건 한정", "매월 12건 한정")
html = html.replace("한 달에 20건의 작업만", "한 달에 12건의 작업만")

# ---- CTA 리디자인: 좌 카피 / 우 전화+버튼 / 고스트 타이포 ----
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
html = re.sub(r'<section class="cta-section">.*?</section>', CTA2, html, count=1, flags=re.S)

# ---- CTA / 칼럼·공지 ----
html = html.replace("인쇄물 전문가에게 무료 상담 받기", "디자인 전문가에게 무료 상담 받기")
html = html.replace("칼럼 + 공지사항", "칼럼")
html = html.replace(">전문 칼럼</a>", ">블로그</a>")
html = html.replace("인쇄물 제작과 관련한 모든 고민을 해결해보세요.", "디자인·인쇄 제작과 관련한 모든 고민을 해결해보세요.")
# 보드 섹션 → 전문 칼럼 슬라이더(3개씩 보임, 공지는 삭제됨)
COLSL_ITEMS = [
    ("column-design.html", "theme/assets/first/column-card.png", "좋은 디자인은 무엇이 다를까?", "디자인 일반 · 4분 분량"),
    ("column-catalog.html", "theme/assets/first/col-2.png", "카탈로그 제작 전 체크리스트 5가지", "인쇄·홍보물 · 5분 분량"),
    ("column-logo.html", "theme/assets/first/col-3.png", "로고 리뉴얼, 언제 해야 할까?", "브랜딩·로고 · 4분 분량"),
    ("column-print.html", "theme/assets/first/col-4.png", "인쇄 사고를 막는 원고 준비법", "인쇄·홍보물 · 5분 분량"),
]
colsl_cards = "".join(
    f'<a class="colsl-card" href="{href}"><div class="colsl-thumb"><img src="{img}" alt="{t}" loading="lazy"></div>'
    f'<div class="colsl-meta"><b>{t}</b><span>{m}</span></div></a>' for href, img, t, m in COLSL_ITEMS)
COLSL = f'''<section class="colsl-section">
    <div class="colsl-inner">
        <div class="colsl-head">
            <div><h3>블로그</h3><p>디자인·인쇄 제작과 관련한 모든 고민을 해결해보세요.</p></div>
            <div class="colsl-nav">
                <button class="colsl-prev" aria-label="이전"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button>
                <button class="colsl-next" aria-label="다음"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button>
            </div>
        </div>
        <div class="colsl-viewport"><div class="colsl-track">{colsl_cards}</div></div>
    </div>
</section>
<script>
(function () {{
    var track = document.querySelector('.colsl-track');
    if (!track) return;
    var cards = track.children, idx = 0;
    function perView() {{ return window.innerWidth <= 640 ? 1 : (window.innerWidth <= 1024 ? 2 : 3); }}
    function maxIdx() {{ return Math.max(0, cards.length - perView()); }}
    function go(k) {{
        idx = Math.max(0, Math.min(k, maxIdx()));
        track.style.transform = 'translateX(-' + cards[idx].offsetLeft + 'px)';
    }}
    document.querySelector('.colsl-prev').addEventListener('click', function () {{ go(idx - 1); reset(); }});
    document.querySelector('.colsl-next').addEventListener('click', function () {{ go(idx >= maxIdx() ? 0 : idx + 1); reset(); }});
    var timer = setInterval(auto, 4000);
    function auto() {{ go(idx >= maxIdx() ? 0 : idx + 1); }}
    function reset() {{ clearInterval(timer); timer = setInterval(auto, 4000); }}
    window.addEventListener('resize', function () {{ go(idx); }});
}})();
</script>'''
html = re.sub(r'<!-- ========== 섹션 13:.*?-->\s*<section class="board-section">.*?</section>', COLSL, html, count=1, flags=re.S)
html = re.sub(r'<section class="board-section">.*?</section>', COLSL, html, count=1, flags=re.S)  # 주석 없을 때 안전망
html = re.sub(r'\s*<a href="#notice"[^>]*>공지사항</a>', "", html)

# ---- 푸터 ----
html = re.sub(r"상호 : 포에디트.*?이메일 : contact@poedit\.co\.kr",
              "상호 : 퍼스트디자인 인천지사(㈜퍼스트마케팅컴퍼니) &nbsp;|&nbsp; 대표자 : 김우석 &nbsp;|&nbsp; 사업자 번호 : 884-88-01123<br>"
              "소재지 : 인천광역시 &nbsp;|&nbsp; 이메일 : " + EMAIL, html, flags=re.S)
html = html.replace("1666-5183", PHONE)
html = html.replace("contact@poedit.co.kr", EMAIL)

# ---- 잔여 전역 치환 ----
html = html.replace("포에디트는", "퍼스트디자인은").replace("포에디트가", "퍼스트디자인이")
html = html.replace("포에디트에", "퍼스트디자인에").replace("포에디트", "퍼스트디자인 인천지사")
html = html.replace("#FF6E3F", PRIMARY).replace("#FF6431", PRIMARY)
html = html.replace('alt="포에디트 로고"', 'alt="퍼스트디자인 인천지사"')

(ROOT / "index.html").write_text(html, encoding="utf-8")

# ---------- 5. CSS 리컬러 + incheon.css ----------
for rel in ["theme/css/tokens.css", "theme/css/common.css", "theme/css/pages/front-page.css"]:
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    t = t.replace("#FF6E3F", PRIMARY).replace("#ff6e3f", PRIMARY).replace("#FF3D00", PRIMARY_DARK)
    t = t.replace("#e55a2f", PRIMARY_DARK)
    t = re.sub(r"rgba\(255,\s*110,\s*63", "rgba(12, 147, 132", t)
    p.write_text(t, encoding="utf-8")

incheon_css = """/* 퍼스트디자인 인천지사 — 차별화 오버라이드 */
.logo-first{font-weight:800;font-size:24px;letter-spacing:-0.04em;color:#111;display:inline-flex;align-items:center;line-height:1;white-space:nowrap}
.logo-first em{font-style:normal;color:""" + PRIMARY + """}
.logo-first small{font-size:12px;font-weight:700;color:#8a8a8a;margin-left:8px;padding:4px 8px;border:1px solid #ddd;border-radius:999px;letter-spacing:0}
.site-footer .logo-first{font-size:26px}
/* 버튼: 라운드 → 샤프(6px) */
.btn-outline,.btn-primary-sm,.mobile-menu-cta{border-radius:6px !important}
/* 헤더 문의하기: 포에디트 블록 버튼 → 필 그라디언트 */
.contact-btn{width:auto !important;height:auto !important;padding:15px 28px !important;border-radius:999px !important;background:linear-gradient(115deg,""" + PRIMARY + """ 0%,#12b3a0 100%) !important;box-shadow:0 6px 16px rgba(12,147,132,.32);transition:all .25s ease;font-weight:700 !important}
.contact-btn:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(12,147,132,.45);background:linear-gradient(115deg,""" + PRIMARY_DARK + """ 0%,""" + PRIMARY + """ 100%) !important}
/* ===== 히어로: 헤드라인 + 대형 배너 캐러셀 + 우측 카드 2장 ===== */
.bw-hero{max-width:1560px;margin:0 auto;padding:56px 32px 26px;display:grid;grid-template-columns:1fr 360px;gap:26px;align-items:stretch}
/* 문의현황 티커: 히어로 바로 아래, 히어로 그리드 폭에 정렬 */
.inquiry-status-section{padding:0 32px !important}
.inquiry-status{max-width:1496px !important;width:100%;margin:0 auto !important;border-radius:26px !important}
.bw-main{position:relative;display:flex;flex-direction:column}
.bw-slide{display:none;flex:1;flex-direction:column}
.bw-slide.on{display:flex;animation:bwfade .55s ease}
@keyframes bwfade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.bw-slide h2{font-size:46px;font-weight:800;letter-spacing:-0.035em;line-height:1.28;color:#111;margin:0 0 30px;min-height:120px}
.bw-slide h2 b{color:""" + PRIMARY + """}
.bw-ctrl{position:absolute;top:96px;right:8px;display:flex;align-items:center;gap:16px;z-index:5}
.bw-count{font-size:19px;font-weight:700;color:#c9c9c9;letter-spacing:.04em}
.bw-count .cur{color:#111}
.bw-next{background:none;border:none;cursor:pointer;color:#111;padding:6px;display:flex}
.bw-next:hover{color:""" + PRIMARY + """}
.bw-bnr{position:relative;display:block;flex:1;min-height:430px;border-radius:26px;overflow:hidden;text-decoration:none}
.bw-bnr>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bw-txt{position:absolute;left:40px;bottom:34px;z-index:1;color:#fff}
.bw-txt::before{content:"";position:absolute;inset:-40px -60px -34px -40px;background:linear-gradient(transparent,rgba(8,20,18,.55));z-index:-1;filter:blur(2px)}
.bw-cat{font-size:15px;font-weight:700;color:#7fe0d3;margin-bottom:8px}
.bw-txt p{font-size:17px;line-height:1.6;margin:0;font-weight:500}
.bw-promo{background:linear-gradient(115deg,#0B2E2A 0%,""" + PRIMARY + """ 62%,#12b3a0 100%);display:flex;flex-direction:row;align-items:center;justify-content:space-between;text-align:left;color:#fff;padding:0 64px;gap:30px;overflow:hidden}
.bw-promo-txt{display:flex;flex-direction:column;align-items:flex-start;max-width:56%}
.bw-badge{display:inline-block;border:1.5px solid rgba(255,255,255,.55);border-radius:999px;padding:9px 20px;font-size:14px;font-weight:700;color:#d8fff8;margin-bottom:22px}
.bw-promo strong{font-size:42px;font-weight:800;letter-spacing:-0.03em;line-height:1.3;margin-bottom:16px}
.bw-promo p{font-size:17px;color:rgba(255,255,255,.85);line-height:1.6;margin:0 0 24px}
.bw-promo em{font-style:normal;font-size:14px;color:rgba(255,255,255,.6)}
.bw-promo-imgs{position:relative;flex:1;height:100%;min-height:380px}
.bw-promo-imgs img{position:absolute;border-radius:14px;box-shadow:0 18px 44px rgba(0,0,0,.35);object-fit:cover}
.bw-promo-imgs .pi1{width:250px;height:250px;right:130px;top:50%;transform:translateY(-58%) rotate(-7deg);z-index:2}
.bw-promo-imgs .pi2{width:200px;height:200px;right:0;top:14%;transform:rotate(9deg);z-index:1;opacity:.92}
.bw-promo-imgs .pi3{width:170px;height:170px;right:60px;bottom:6%;transform:rotate(4deg);z-index:3}
@media (max-width:1100px){
  .bw-promo{padding:36px 28px}
  .bw-promo-txt{max-width:100%}
  .bw-promo-imgs{display:none}
}
.bw-aside{position:relative;display:flex;flex-direction:column;gap:22px;padding-top:150px}
.bw-card{position:relative;flex:1;border-radius:22px;overflow:hidden;display:block;text-decoration:none;min-height:230px}
.bw-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .35s}
.bw-card:hover img{transform:scale(1.04)}
.bw-card-photo::after{content:"";position:absolute;inset:0;background:linear-gradient(rgba(10,24,21,.42) 0%,transparent 40%,rgba(8,20,18,.62) 100%)}
.bw-cap{position:absolute;top:20px;left:22px;right:22px;z-index:1;font-size:15px;font-weight:700;color:#fff;line-height:1.5}
.bw-tit{position:absolute;left:22px;bottom:20px;right:22px;z-index:1;color:#fff}
.bw-tit small{display:block;font-size:13px;font-weight:600;color:#9fe8dd;margin-bottom:6px}
.bw-tit{font-size:21px;font-weight:800;line-height:1.4}
.bw-card-grad{background:linear-gradient(120deg,#0a4b8f 0%,""" + PRIMARY + """ 100%)}
.bw-card-grad img{left:auto;width:58%;right:-12%;top:12%;height:auto;transform:rotate(-8deg);opacity:.9;border-radius:10px}
.bw-card-grad:hover img{transform:rotate(-8deg) scale(1.03)}
.bw-card-grad .bw-tit strong{display:block;font-size:24px;margin-bottom:8px}
.bw-card-grad .bw-tit{font-size:15px;font-weight:600}
@media (max-width:1100px){
  .bw-hero{grid-template-columns:1fr;padding:40px 20px 64px}
  .bw-slide h2{font-size:32px;min-height:0;margin-bottom:20px}
  .bw-ctrl{position:static;justify-content:flex-end;margin-bottom:12px}
  .bw-bnr{min-height:300px}
  .bw-promo strong{font-size:30px}
  .bw-aside{flex-direction:row;padding-top:0}
  .bw-card{min-height:200px}
}
@media (max-width:640px){.bw-aside{flex-direction:column}}
/* ===== 통계: 다크 틸 밴드 ===== */
.stats-section{background:linear-gradient(120deg,#0B2E2A 0%,#0d5f55 100%) !important}
.stats-section .stat-label{color:rgba(255,255,255,.62) !important}
.stats-section .stat-number,.stats-section .count-num-item-box{color:#fff !important}
.stats-section .plus,.stats-section .percent{color:#2fd0bd !important}
.stats-section .stat-divider{background:rgba(255,255,255,.16) !important}
/* ===== 포트폴리오: 오버레이 3열 그리드 ===== */
.ih-pf-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;width:100%;margin:0 0 48px;padding:0}
.ih-pf-item{position:relative;display:block;aspect-ratio:1/1;overflow:hidden;background-size:cover;background-position:center;text-decoration:none}
.ih-pf-item::after{content:"";position:absolute;inset:0;background:linear-gradient(transparent 55%,rgba(8,24,21,.78));opacity:0;transition:opacity .25s}
.ih-pf-item:hover::after{opacity:1}
.ih-pf-label{position:absolute;left:22px;right:22px;bottom:18px;z-index:1;opacity:0;transform:translateY(8px);transition:all .25s}
.ih-pf-item:hover .ih-pf-label{opacity:1;transform:none}
.ih-pf-label h3{font-size:18px;font-weight:800;color:#fff;margin:0 0 4px}
.ih-pf-label p{font-size:14px;color:rgba(255,255,255,.75);margin:0}
@media (max-width:900px){.ih-pf-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){.ih-pf-grid{grid-template-columns:1fr}.ih-pf-item::after{opacity:1}.ih-pf-label{opacity:1;transform:none}}
/* ===== 프로세스: 번호 타임라인 ===== */
.ih-steps{display:grid;grid-template-columns:repeat(6,1fr);gap:0;margin-top:56px;position:relative}
.ih-steps::before{content:"";position:absolute;top:19px;left:8.3%;right:8.3%;height:2px;background:linear-gradient(90deg,""" + PRIMARY + """ 0%,#bfe3de 100%)}
.ih-step{position:relative;text-align:center;padding:0 10px}
.ih-step-no{position:relative;z-index:1;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:#fff;border:2px solid """ + PRIMARY + """;color:""" + PRIMARY + """;font-size:13px;font-weight:800;margin-bottom:16px}
.ih-step h3{font-size:17px;font-weight:800;color:#111;margin:0 0 8px}
.ih-step p{font-size:13.5px;color:#767676;line-height:1.55;margin:0}
@media (max-width:900px){.ih-steps{grid-template-columns:repeat(3,1fr);row-gap:36px}.ih-steps::before{display:none}}
/* CTA 배너: 포에디트 목업 이미지 → 틸 그라디언트 */
.cta-section{background-image:none !important;background:linear-gradient(100deg,#0B2E2A 0%,""" + PRIMARY + """ 60%,#12b3a0 100%) !important;padding:96px 32px !important;height:auto !important;position:relative;overflow:hidden}
.cta2{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:48px;position:relative}
.cta2-eyebrow{font-size:13px;font-weight:800;letter-spacing:.22em;color:rgba(255,255,255,.5);margin:0 0 16px}
.cta2-copy{font-size:24px;font-weight:500;color:rgba(255,255,255,.82);line-height:1.5;margin:0}
.cta2-copy strong{display:block;font-size:42px;font-weight:800;color:#fff;letter-spacing:-0.025em;margin-top:8px}
.cta2-right{display:flex;align-items:center;gap:44px;position:relative;z-index:1}
.cta2-phone{text-align:right;color:#fff}
.cta2-phone span{display:block;font-size:14px;font-weight:600;color:rgba(255,255,255,.55);margin-bottom:6px}
.cta2-phone b{font-size:36px;font-weight:800;letter-spacing:.01em}
.cta2-btn{display:inline-flex;align-items:center;gap:10px;background:#fff;color:""" + PRIMARY_DARK + """;font-size:17px;font-weight:800;padding:20px 32px;border-radius:10px;text-decoration:none;box-shadow:0 12px 30px rgba(0,0,0,.18);transition:transform .2s}
.cta2-btn:hover{transform:translateY(-3px)}
.cta2-ghost{position:absolute;right:-30px;bottom:-105px;font-size:230px;font-weight:900;letter-spacing:-0.05em;color:rgba(255,255,255,.055);line-height:1;pointer-events:none;user-select:none}
@media (max-width:1024px){
  .cta2{flex-direction:column;align-items:flex-start;gap:32px}
  .cta2-copy strong{font-size:30px}
  .cta2-right{width:100%;justify-content:space-between;gap:20px;flex-wrap:wrap}
  .cta2-phone{text-align:left}
  .cta2-ghost{font-size:130px;bottom:-55px}
}
/* 상단바 뱃지 컬러 */
.top-box.center{background:""" + PRIMARY + """;color:#fff}
/* 전문 칼럼 슬라이더(3개씩) */
.colsl-section{padding:110px 24px;background:#fff}
.colsl-inner{max-width:1280px;margin:0 auto}
.colsl-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:30px}
.colsl-head h3{font-size:30px;font-weight:800;color:#111;margin:0 0 8px;letter-spacing:-0.02em}
.colsl-head p{font-size:15px;color:#767676;margin:0}
.colsl-nav button{width:46px;height:46px;border-radius:50%;border:1px solid #ddd;background:#fff;cursor:pointer;color:#111;display:inline-flex;align-items:center;justify-content:center;margin-left:8px;transition:all .2s}
.colsl-nav button:hover{border-color:""" + PRIMARY + """;color:""" + PRIMARY + """}
.colsl-viewport{overflow:hidden}
.colsl-track{display:flex;gap:20px;transition:transform .45s ease}
.colsl-card{flex:0 0 calc((100% - 40px)/3);display:block;text-decoration:none}
.colsl-thumb{border-radius:14px;overflow:hidden}
.colsl-thumb img{width:100%;display:block;transition:transform .35s}
.colsl-card:hover .colsl-thumb img{transform:scale(1.04)}
.colsl-meta{margin-top:14px}
.colsl-meta b{display:block;font-size:17px;font-weight:800;color:#111;margin-bottom:5px;letter-spacing:-0.01em}
.colsl-meta span{font-size:13.5px;color:#8a8a8a}
@media (max-width:1024px){.colsl-card{flex:0 0 calc((100% - 20px)/2)}}
@media (max-width:640px){.colsl-card{flex:0 0 100%}}
"""
(ROOT / "theme" / "css" / "incheon.css").write_text(incheon_css, encoding="utf-8")

# ---------- 6. animations.js 리뷰 데이터 ----------
p = ROOT / "theme" / "js" / "animations.js"
t = p.read_text(encoding="utf-8")
reviews = [
    ("LOGO_Kookmin-bank.jpg", "디자인부터 인쇄까지 빠르게 받아볼 수 있었습니다", "시안을 2가지로 제안해주셔서 선택의 폭이 넓었고, 수정도 신속하게 진행되어 인쇄까지 빠르게 받아볼 수 있었습니다."),
    ("LOGO_hite-jinro.jpg", "캐릭터 활용 홍보물, 기대 이상이었습니다", "브랜드 캐릭터를 활용한 홍보물을 의뢰했는데 톤앤매너를 정확히 살려주셔서 내부 반응이 아주 좋았습니다."),
    ("LOGO_mirae.jpg", "너무 만족스럽고 수정이 필요없네요", "너무 만족스러운 디자인이고 수정 없이 마무리하면 될 것 같습니다 ^^ 대표님께서도 감사하다고 전해달라 하시네요."),
    ("LOGO_ewha-university.png", "수정없이 한번에 컨펌되었습니다!", "컨셉이 정해진 것이 없었는데 원하는 디자인으로 잘 나왔습니다. 수정 없이 한번에 컨펌되어 편하게 작업했습니다~"),
    ("LOGO_nationalforensic-logo.jpg", "보고서·브로슈어 모두 믿고 맡깁니다", "기관 발간물 특성상 검수 기준이 까다로운데도 일정과 품질 모두 정확하게 맞춰주셨습니다."),
    ("LOGO_samsung-bio.jpg", "빠르고 신속한 작업! 다음에 또 요청드리겠습니다!", "리플렛 디자인 의뢰 후 마음에 들어서 포스터 디자인까지 의뢰하게 되었네요^^ 빠르고 친절하게 작업해주셔서 감사드립니다!"),
    ("LOGO_cj-enm.png", "전체적으로 디자인이 좋아서 수정할 필요가 없습니다!", "전체적으로 디자인이 좋아서 개선할 것이 없습니다! 포스터와 랜딩페이지까지 시간 내에 빠르게 제작해주셔서 감사드립니다."),
    ("LOGO_k-league.jpg", "좋은 작업물 만들어주셔서 감사드립니다!", "일정이 타이트했는데 기한에 맞춰 잘 작업해주셨습니다~ 두 가지 제작물의 톤앤매너까지 잘 맞춰주셔서 마음에 드네요."),
]
arr = ",\n            ".join('{ logo: "theme/assets/first/%s", title: "%s", text: "%s" }' % r for r in reviews)
t = re.sub(r"var reviewData = \[.*?\];", "var reviewData = [\n            " + arr + "\n        ];", t, flags=re.S)
t = t.replace("포에디트", "퍼스트디자인")
p.write_text(t, encoding="utf-8")

print("overlay done")
