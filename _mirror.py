# -*- coding: utf-8 -*-
"""poedit.co.kr 홈페이지 미러링: 에셋 다운로드 + 경로 로컬화 (부산 v2 방식)"""
import os, re, urllib.parse, urllib.request, pathlib

ROOT = pathlib.Path(__file__).parent
SCRATCH = pathlib.Path(os.path.expanduser(
    "~/AppData/Local/Temp/claude/C--Users----/54452de3-9fd5-4fdb-ab17-d592a917fbd9/scratchpad"))
BASE = "https://poedit.co.kr"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        print("FAIL", url, e)
        return False

# ---------- 1. 테마 이미지 ----------
img_dir = ROOT / "theme" / "assets" / "images"
urls = set()
for line in (SCRATCH / "asset-urls.txt").read_text(encoding="utf-8").splitlines():
    if line.strip():
        urls.add(line.strip())
# CSS 상대경로 참조 이미지
for name in ["faq-arrow.png", "mob-datasection_bg.png", "mob-process_bg.png",
             "process-bg.png", "board-more.png", "cta_bg.png", "mob-cta_bg.png",
             "그라디언트_배경.png", "맞춤디자이너_배경.png"]:
    urls.add(BASE + "/wp-content/themes/Poedit/assets/images/" + name)

ok = fail = 0
for u in sorted(urls):
    name = urllib.parse.unquote(u.split("/")[-1])
    q = u.rsplit("/", 1)[0] + "/" + urllib.parse.quote(name)
    if fetch(q, img_dir / name):
        ok += 1
    else:
        fail += 1
print("images:", ok, "ok /", fail, "fail")

# ---------- 2. 폰트 ----------
font_dir = ROOT / "theme" / "assets" / "fonts"
for w in ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold",
          "Bold", "ExtraBold", "Black"]:
    fetch(f"{BASE}/wp-content/themes/Poedit/assets/fonts/Pretendard-{w}.woff2",
          font_dir / f"Pretendard-{w}.woff2")

# ---------- 3. uploads (리뷰 로고, 파비콘) ----------
up_dir = ROOT / "theme" / "uploads"
for n in range(809, 817):
    fetch(f"{BASE}/wp-content/uploads/2025/07/Group-{n}.png", up_dir / f"Group-{n}.png")
for fav in ["파비콘-150x150.png", "파비콘-300x300.png"]:
    fetch(f"{BASE}/wp-content/uploads/2026/06/{urllib.parse.quote(fav)}", up_dir / fav)

# ---------- 4. vendor (swiper, wp block css) ----------
vend = ROOT / "theme" / "vendor"
fetch("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css", vend / "swiper-bundle.min.css")
fetch("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js", vend / "swiper-bundle.min.js")
fetch(f"{BASE}/wp-includes/css/dist/block-library/style.min.css", vend / "wp-block-library.css")

# ---------- 5. CSS/JS 복사 + 경로 로컬화 ----------
css_dir = ROOT / "theme" / "css"
(css_dir / "pages").mkdir(parents=True, exist_ok=True)
(ROOT / "theme" / "js").mkdir(parents=True, exist_ok=True)

def localize(text):
    text = text.replace(BASE + "/wp-content/themes/Poedit/assets/images/", "theme/assets/images/")
    text = text.replace(BASE + "/wp-content/uploads/2025/07/", "theme/uploads/")
    text = text.replace(BASE + "/wp-content/uploads/2026/06/", "theme/uploads/")
    # URL 인코딩된 한글 파일명 디코드
    def dec(m):
        return urllib.parse.unquote(m.group(0))
    text = re.sub(r"theme/[^\"'()\s>]+", dec, text)
    return text

for src, dst in [("poedit-tokens.css", css_dir / "tokens.css"),
                 ("poedit-common.css", css_dir / "common.css"),
                 ("poedit-front.css", css_dir / "pages" / "front-page.css")]:
    t = (SCRATCH / src).read_text(encoding="utf-8")
    dst.write_text(t, encoding="utf-8")  # 상대경로(../assets)라 그대로 유효

for src in ["main.js", "swiper-init.js", "animations.js", "consultation.js"]:
    t = (SCRATCH / ("poedit-" + src)).read_text(encoding="utf-8")
    t = localize(t)
    (ROOT / "theme" / "js" / src).write_text(t, encoding="utf-8")

# ---------- 6. index.html 생성 ----------
html = (SCRATCH / "poedit.html").read_text(encoding="utf-8")

# WP 잡동사니 제거
html = re.sub(r"<script[^>]*>\s*/\* <!\[CDATA\[ \*/.*?/\* \]\]> \*/\s*</script>", "", html, flags=re.S)  # emoji js
html = re.sub(r"<style id='wp-emoji-styles-inline-css'.*?</style>", "", html, flags=re.S)
html = re.sub(r"<link rel=\"https://api\.w\.org/\".*?/>", "", html)
html = re.sub(r"<link rel=\"alternate\"[^>]*wp-json[^>]*/>", "", html)
html = re.sub(r"<link rel=\"EditURI\"[^>]*/>", "", html)
html = re.sub(r"<meta name=\"generator\"[^>]*/>", "", html)
html = re.sub(r"<link rel='shortlink'[^>]*/>", "", html)
html = re.sub(r"<script type=\"speculationrules\">.*?</script>", "", html, flags=re.S)
html = re.sub(r"<link rel='dns-prefetch'[^>]*/>", "", html)

# 외부 리소스 → self-host
html = html.replace("https://poedit.co.kr/wp-includes/css/dist/block-library/style.min.css?ver=6.8.6",
                    "theme/vendor/wp-block-library.css")
html = html.replace("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css",
                    "theme/vendor/swiper-bundle.min.css")
html = html.replace("https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js",
                    "theme/vendor/swiper-bundle.min.js")
html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/css/tokens\.css\?ver=[\d.]+", "theme/css/tokens.css", html)
html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/css/common\.css\?ver=[\d.]+", "theme/css/common.css", html)
html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/css/pages/front-page\.css\?ver=[\d.]+", "theme/css/pages/front-page.css", html)
html = re.sub(r"https://poedit\.co\.kr/wp-content/themes/Poedit/js/(\w[\w-]*\.js)\?ver=[\d.]+", r"theme/js/\1", html)

html = localize(html)

# 내부 링크: 서브페이지 미구현 → 앵커로
for path in ["about", "portfolio", "review", "column", "notice", "contact"]:
    html = html.replace(f'href="https://poedit.co.kr/{path}/"', f'href="#{path}"')
    html = html.replace(f'href="https://poedit.co.kr/{path}"', f'href="#{path}"')
html = re.sub(r'href="https://poedit\.co\.kr/poedit_notice/[^"]*"', 'href="#notice"', html)
html = html.replace('href="https://poedit.co.kr/"', 'href="index.html"')
html = re.sub(r'<a href="https://poedit\.imweb\.me/"[^>]*>카드결제</a>', "", html)

(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html written:", len(html), "bytes")
