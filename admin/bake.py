# -*- coding: utf-8 -*-
"""관리자 데이터 → 정적 HTML 굽기. 편집 결과가 실제 HTML 소스에 박혀 AI가 읽게 함(핵심 요구).
현재: 포트폴리오. (FAQ·카피·SEO·히어로는 순차 추가)"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data"
INIT = 60   # 첫 화면 노출 수, 나머지는 '더 보기'

def bake_portfolio():
    items = json.loads((DATA / "portfolio.json").read_text(encoding="utf-8"))
    items = sorted(items, key=lambda x: x.get("order", 0))
    html = ""
    for i, it in enumerate(items):
        cat = it["category"]; img = it["image"]
        name = it.get("title", ""); typ = it.get("type", "")
        more = i >= INIT
        hide = ' style="display:none"' if more else ""
        html += (f'<div class="pf-card{" pf-more" if more else ""}" data-cat="{cat}"{hide}>'
                 f'<div class="pf-card-thumb" data-modal="{img}">'
                 f'<div class="pf-card-img" style="background-image:url(\'{img}\')"></div></div>'
                 f'<h2 class="pf-card-name">{name}</h2>'
                 f'<p class="pf-card-type">{typ}</p></div>\n')
    p = ROOT / "portfolio.html"
    s = p.read_text(encoding="utf-8")
    # pf-grid 내부 교체 (morewrap 버튼 보존)
    m = re.search(r'(<div class="pf-grid"[^>]*>)(.*?)(<div class="pf-morewrap">.*?</div>\s*</div>\s*</section>|</div>\s*</div>\s*</section>)', s, re.S)
    if not m:
        raise RuntimeError("pf-grid 블록 못 찾음")
    remain = max(0, len(items) - INIT)
    btn = ('<div class="pf-morewrap"><button type="button" id="pfMore" class="pf-morebtn">'
           f'작업물 더 보기 <span>({remain})</span></button></div>')
    tail = m.group(3)
    if '<div class="pf-morewrap">' in tail:
        tail = re.sub(r'<div class="pf-morewrap">.*?</div>\s*(</div>\s*</div>\s*</section>)',
                      btn + r'\1', tail, flags=re.S)
    else:
        tail = tail.replace("</div>", btn + "</div>", 1)
    s = s[:m.start()] + m.group(1) + "\n" + html + tail + s[m.end():]
    p.write_text(s, encoding="utf-8")
    return len(items)

# ---------- FAQ ----------
# FAQ 있는 서비스 페이지 (page 파일명 → 라벨)
FAQ_PAGES = [
    ("svc-brand", "브랜딩 · 로고"), ("svc-ppt", "PPT · 제안서"),
    ("svc-web", "홈페이지 · 웹"), ("svc-studio", "촬영 · 스튜디오"),
    ("catalog", "카탈로그 · 카다로그"), ("leaflet", "리플렛 · 리플릿"),
    ("pamphlet", "팜플렛 · 팜플릿"), ("brochure", "브로슈어 · 브로셔"),
    ("poster", "포스터"),
]
FAQ_LABELS = dict(FAQ_PAGES)

def _extract_default_faq(html):
    """svc-faq 섹션에서 관리자추가 블록을 뺀 '기본' 문항 추출."""
    m = re.search(r'<section class="svc-faq">(.*?)</section>', html, re.S)
    if not m:
        return []
    body = re.sub(r'<!--faq-extra-->.*?<!--/faq-extra-->', '', m.group(1), flags=re.S)
    out = []
    for it in re.finditer(r'<details class="svc-faq-item"><summary>(.*?)</summary><div class="svc-faq-a"><p>(.*?)</p>', body, re.S):
        out.append((re.sub(r'<[^>]+>', '', it.group(1)).strip(),
                    re.sub(r'<[^>]+>', '', it.group(2)).strip()))
    return out

def bake_faq(page):
    """관리자가 저장한 경우 그 목록이 페이지 FAQ '전체'가 됨(기존 문항 편집·삭제 포함).
    저장 안 한 페이지는 기본 FAQ 유지."""
    import json
    store = json.loads((DATA / "faq_extra.json").read_text(encoding="utf-8")) if (DATA / "faq_extra.json").exists() else {}
    p = ROOT / f"{page}.html"
    if not p.exists():
        raise RuntimeError(f"{page}.html 없음")
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'<!--faq-extra-->.*?<!--/faq-extra-->', '', s, flags=re.S)
    s = re.sub(r'<!--faq-jsonld-->.*?<!--/faq-jsonld-->', '', s, flags=re.S)

    if page in store:
        # 관리자 목록으로 svc-faq 섹션의 모든 문항 교체
        items = store[page]
        m = re.search(r'(<section class="svc-faq">.*?</p>)(.*?)(</section>)', s, re.S)
        if not m:
            m2 = re.search(r'(<section class="svc-faq">.*?<h2[^>]*>.*?</h2>)(.*?)(</section>)', s, re.S)
            m = m2
        newitems = "".join(
            f'<details class="svc-faq-item"><summary>{it["q"]}</summary>'
            f'<div class="svc-faq-a"><p>{it["a"]}</p></div></details>' for it in items)
        s = s[:m.start()] + m.group(1) + newitems + m.group(3) + s[m.end():]
        allqa = [(it["q"], it["a"]) for it in items]
        n = len(items)
    else:
        allqa = _extract_default_faq(s)
        n = 0
    if allqa:
        ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in allqa]}
        jsonld = ('<!--faq-jsonld--><script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + '</script><!--/faq-jsonld-->')
        s = s.replace("</head>", jsonld + "\n</head>", 1)
    p.write_text(s, encoding="utf-8")
    return n, len(allqa)

# ---------- 사이트 설정(Head 코드·파비콘·대표이미지) ----------
ALL_SITE_PAGES = ["index", "about", "portfolio", "column", "contact",
                  "svc-brand", "svc-ppt", "svc-web", "svc-studio",
                  "catalog", "leaflet", "pamphlet", "brochure", "poster",
                  "column-design", "column-catalog", "column-logo", "column-print"]

def _all_html_files():
    files = [ROOT / f"{p}.html" for p in ALL_SITE_PAGES]
    files += list(ROOT.glob("col-*.html"))   # 관리자 생성 칼럼
    return [f for f in files if f.exists()]

def bake_settings():
    """settings.json의 headCode를 전 페이지 <head>에 삽입(네이버/구글 인증코드 등), 파비콘·og 반영."""
    import json
    st = json.loads((DATA / "settings.json").read_text(encoding="utf-8")) if (DATA / "settings.json").exists() else {}
    head = st.get("headCode", "").strip()
    favicon = st.get("favicon", "")
    ogimage = st.get("ogImage", "")
    n = 0
    for p in _all_html_files():
        s = p.read_text(encoding="utf-8")
        # Head 코드 (마커로 교체, 재실행 안전)
        s = re.sub(r'<!--head-code-->.*?<!--/head-code-->', '', s, flags=re.S)
        if head:
            s = s.replace("</head>", f"<!--head-code-->{head}<!--/head-code-->\n</head>", 1)
        # 파비콘
        if favicon:
            if re.search(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>', s):
                s = re.sub(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>',
                           f'<link rel="icon" href="/{favicon}">', s, count=1)
            else:
                s = s.replace("</head>", f'<link rel="icon" href="/{favicon}">\n</head>', 1)
        # 기본 og:image (페이지별 지정 없을 때 공통)
        if ogimage:
            s = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                       rf'\g<1>{DOMAIN}/{ogimage}\g<2>', s)
        p.write_text(s, encoding="utf-8")
        n += 1
    return n

# ---------- 히어로 (홈 bw-slide) ----------
def _title_to_h2(t):
    # dfirst UI 규칙: *단어*=강조, 줄바꿈=<br>  →  우리 h2(<b>+<br>)
    t = re.sub(r'\*([^*]+)\*', r'<b>\1</b>', t or "")
    return t.replace("\n", "<br>")

def _h2_to_title(h2):
    return h2.replace("<br>", "\n").replace("<b>", "*").replace("</b>", "*")

def seed_hero():
    """index.html 현재 슬라이드 → admin/data/hero.json (최초 1회)."""
    import json
    f = DATA / "hero.json"
    if f.exists():
        return
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    slides = []
    for m in re.finditer(r'<div class="bw-slide[^"]*">(.*?)</a></div>', s, re.S):
        seg = m.group(0)
        h2 = re.search(r'<h2>(.*?)</h2>', seg, re.S)
        href = re.search(r'href="([^"]*)"', seg)
        img = re.search(r'<img src="([^"]*)"', seg)
        cat = re.search(r'bw-cat">([^<]*)', seg)
        p = re.search(r'<p>(.*?)</p>', seg, re.S)
        slides.append({
            "title": _h2_to_title(h2.group(1).strip()) if h2 else "",
            "eyebrow": cat.group(1).strip() if cat else "",
            "subtitle": p.group(1).strip() if p else "",
            "image": img.group(1) if img else "",
            "btn1Link": href.group(1) if href else "portfolio.html",
            "textColor": "light", "btn1Text": "", "btn2Text": "", "btn2Link": "",
        })
    f.write_text(json.dumps(slides, ensure_ascii=False, indent=1), encoding="utf-8")

def bake_hero():
    import json
    slides = json.loads((DATA / "hero.json").read_text(encoding="utf-8"))
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    ms = list(re.finditer(r'<div class="bw-slide[^"]*">.*?</a></div>', s, re.S))
    if not ms:
        raise RuntimeError("bw-slide 없음")
    html = ""
    for i, sl in enumerate(slides):
        on = " on" if i == 0 else ""
        html += (f'<div class="bw-slide{on}"><h2>{_title_to_h2(sl.get("title",""))}</h2>'
                 f'<a class="bw-bnr" href="{sl.get("btn1Link") or "portfolio.html"}">'
                 f'<img src="{sl.get("image","")}" alt="{sl.get("eyebrow","")}" loading="lazy">'
                 f'<div class="bw-txt"><div class="bw-cat">{sl.get("eyebrow","")}</div>'
                 f'<p>{sl.get("subtitle","")}</p></div></a></div>')
    s = s[:ms[0].start()] + html + s[ms[-1].end():]
    p.write_text(s, encoding="utf-8")
    return len(slides)

# ---------- 칼럼(블로그) 글 ----------
DOMAIN = "https://incheondesign.co.kr"

def _slugfile(c):
    return f"col-{c['id']}.html"

def _toc_and_body(body_html):
    """본문 h2에 id 부여 + TOC 목록 생성."""
    items, n = [], [0]
    def repl(m):
        n[0] += 1
        sid = f"sec-{n[0]}"
        txt = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        items.append((sid, txt))
        return f'<h2 id="{sid}"{m.group(1)}>{m.group(2)}</h2>'
    body = re.sub(r'<h2([^>]*)>(.*?)</h2>', repl, body_html, flags=re.S)
    toc = "".join(f'<li class="blog-toc-item"><a href="#{sid}">{txt}</a></li>' for sid, txt in items)
    return body, toc, items

def _read_time(body_html):
    txt = re.sub(r'<[^>]+>', '', body_html)
    return max(1, round(len(txt) / 500))

def extract_faq(body_html):
    """본문 HTML에서 FAQ 자동 감지 → [(질문,답변)]. 별도 입력란 불필요.
    ① <details><summary>Q</summary>A</details>  ② '자주 묻는 질문'/'FAQ' 제목 아래 h3(Q)+본문(A)."""
    def clean(x):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x)).strip()
    out = []
    # ① details/summary
    for m in re.finditer(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', body_html, re.S | re.I):
        q, a = clean(m.group(1)), clean(m.group(2))
        if q and a:
            out.append((q, a))
    if out:
        return out
    # ② 'FAQ'/'자주 묻는 질문' 제목 이후 h3=질문, 다음 h3/h2 전까지=답변
    hm = re.search(r'<h[23][^>]*>\s*(?:자주\s*묻는\s*질문|FAQ|Q\s*&\s*A)\s*</h[23]>', body_html, re.I)
    if hm:
        region = body_html[hm.end():]
        parts = re.split(r'(<h3[^>]*>.*?</h3>)', region, flags=re.S | re.I)
        i = 1
        while i < len(parts):
            q = clean(parts[i])
            a = clean(parts[i + 1]) if i + 1 < len(parts) else ""
            # 다음 h2(다른 섹션) 만나면 중단
            if re.match(r'<h2', parts[i], re.I):
                break
            if q and a:
                out.append((q, a))
            i += 2
    return out

def bake_columns():
    import json
    cols = json.loads((DATA / "columns.json").read_text(encoding="utf-8")) if (DATA / "columns.json").exists() else []
    pub = [c for c in cols if c.get("status") != "draft"]
    pub = sorted(pub, key=lambda c: c.get("date", ""), reverse=True)
    # 템플릿 = 기존 블로그 상세(chrome+구조)
    tpl = (ROOT / "column-design.html").read_text(encoding="utf-8")
    for idx, c in enumerate(pub):
        s = tpl
        title = c["title"]; cat = c.get("category", "Column")
        date = c.get("date", "2026-07-24"); excerpt = c.get("excerpt", "")
        thumb = c.get("thumbnail") or "theme/assets/first/column-card.png"
        body, toc, items = _toc_and_body(c.get("body", ""))
        rt = _read_time(c.get("body", ""))
        url = f"{DOMAIN}/{_slugfile(c)}"
        # head: title·desc·canonical·og
        s = re.sub(r'<title>.*?</title>', f'<title>{title} | 퍼스트디자인 인천지사</title>', s, count=1, flags=re.S)
        s = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{excerpt or title}\g<2>', s)
        s = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{url}">', s)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf'\g<1>{title}\g<2>', s)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{excerpt or title}\g<2>', s)
        s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{url}\g<2>', s)
        # FAQ 잔재만 제거. localbiz(회사 엔티티)는 유지 → 새 글도 GEO 확보.
        # 템플릿 자체 col-jsonld(이전 글 스키마)는 제거하고 이 글 것으로 교체.
        s = re.sub(r'<!--faq-jsonld-->.*?<!--/faq-jsonld-->', '', s, flags=re.S)
        article_ld = {"@context": "https://schema.org", "@type": "BlogPosting",
                      "headline": title, "description": excerpt,
                      "image": DOMAIN + "/" + thumb,
                      "datePublished": date, "dateModified": date,
                      "author": {"@type": "Organization", "name": "퍼스트디자인 인천지사"},
                      "publisher": {"@type": "Organization", "name": "퍼스트디자인 인천지사",
                                    "logo": {"@type": "ImageObject", "url": DOMAIN + "/theme/assets/first/favicon.png"}},
                      "mainEntityOfPage": url, "articleSection": cat}
        crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "홈", "item": DOMAIN + "/"},
                        {"@type": "ListItem", "position": 2, "name": "블로그", "item": DOMAIN + "/column.html"},
                        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
        # FAQ 자동 감지 → FAQPage 구조화데이터(있을 때만, AEO)
        faq_pairs = extract_faq(c.get("body", ""))
        faq_script = ""
        if faq_pairs:
            faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                      "mainEntity": [{"@type": "Question", "name": q,
                                      "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_pairs]}
            faq_script = '<script type="application/ld+json">' + json.dumps(faq_ld, ensure_ascii=False) + '</script>'
        ld = ('<!--col-jsonld--><script type="application/ld+json">' + json.dumps(article_ld, ensure_ascii=False)
              + '</script><script type="application/ld+json">' + json.dumps(crumb_ld, ensure_ascii=False)
              + '</script>' + faq_script + '<!--/col-jsonld-->')
        s = re.sub(r'<!--col-jsonld-->.*?<!--/col-jsonld-->', '', s, flags=re.S)
        s = s.replace("</head>", ld + "\n</head>", 1)
        # 브레드크럼 마지막 span
        s = re.sub(r'(<nav class="blog-breadcrumb">.*?<span>)(.*?)(</span></nav>)',
                   rf'\g<1>{title}\g<3>', s, count=1, flags=re.S)
        # 카테고리·제목·메타·썸네일
        s = re.sub(r'(<a class="blog-single-cat"[^>]*>)(.*?)(</a>)', rf'\g<1>{cat}\g<3>', s, count=1, flags=re.S)
        s = re.sub(r'(<h1 class="blog-single-tit">)(.*?)(</h1>)', rf'\g<1>{title}\g<3>', s, count=1, flags=re.S)
        s = re.sub(r'(<ul class="blog-single-meta">).*?(</ul>)',
                   rf'\g<1><li>{date.replace("-",".")}</li><li>{rt}분 분량</li><li>퍼스트디자인 인천지사</li>\g<2>', s, count=1, flags=re.S)
        s = re.sub(r'(<div class="blog-single-thumb"><img src=")[^"]*(" alt=")[^"]*(">)',
                   rf'\g<1>{thumb}\g<2>{title}\g<3>', s, count=1, flags=re.S)
        # 모바일 TOC
        s = re.sub(r'(<details class="blog-single-toc-mobile"><summary>목차 <span>▾</span></summary><ol>).*?(</ol></details>)',
                   rf'\g<1>{toc}\g<2>', s, count=1, flags=re.S)
        # 데스크톱 TOC(사이드바)
        s = re.sub(r'(<ol class="blog-single-toc-list">).*?(</ol>)',
                   rf'\g<1>{toc}\g<2>', s, count=1, flags=re.S)
        # 본문
        s = re.sub(r'(<div class="blog-single-body">).*?(</div>\s*<div class="blog-single-cta">)',
                   lambda m: m.group(1) + body + '</div>\n<div class="blog-single-cta">', s, count=1, flags=re.S)
        # 이전/다음 글
        prev_c = pub[idx + 1] if idx + 1 < len(pub) else None
        next_c = pub[idx - 1] if idx > 0 else None
        def navitem(cc, label, cls=""):
            if not cc:
                return ""
            return (f'<a class="blog-single-nav-item{cls}" href="{_slugfile(cc)}">'
                    f'<span class="blog-single-nav-label">{label}</span>'
                    f'<span class="blog-single-nav-tit">{cc["title"]}</span></a>')
        nav = navitem(prev_c, "이전 글") + navitem(next_c, "다음 글", " blog-single-nav-next")
        s = re.sub(r'(<nav class="blog-single-nav">).*?(</nav>)', rf'\g<1>{nav}\g<2>', s, count=1, flags=re.S)
        (ROOT / _slugfile(c)).write_text(s, encoding="utf-8")
    # 블로그 목록(column.html)에 관리자 글 카드 prepend
    lp = ROOT / "column.html"
    ls = lp.read_text(encoding="utf-8")
    ls = re.sub(r'<!--adm-cols-->.*?<!--/adm-cols-->', '', ls, flags=re.S)
    cards = "<!--adm-cols-->" + "".join(
        f'<article class="blog-item" data-cat="{c.get("category","Column")}" data-title="{c["title"]}">'
        f'<a class="blog-item-link" href="{_slugfile(c)}">'
        f'<div class="blog-item-img"><img src="{c.get("thumbnail") or "theme/assets/first/column-card.png"}" alt="{c["title"]}" loading="lazy"></div>'
        f'<div class="blog-item-info"><span class="blog-item-cat">{c.get("category","Column")}</span>'
        f'<h3 class="blog-item-tit">{c["title"]}</h3>'
        f'<div class="blog-item-meta"><time class="blog-item-date">{c.get("date","2026-07-24").replace("-",".")}</time>'
        f'<span class="blog-item-readtime">{_read_time(c.get("body",""))}분 분량</span></div></div></a></article>'
        for c in pub) + "<!--/adm-cols-->"
    ls = re.sub(r'(<div class="blog-list">)', r'\1' + cards, ls, count=1)
    lp.write_text(ls, encoding="utf-8")
    return len(pub)

# ---------- SEO (페이지별 head 메타) ----------
SEO_PAGES = [
    ("index", "홈"), ("about", "회사소개"), ("portfolio", "포트폴리오"),
    ("column", "블로그"), ("contact", "문의"),
    ("svc-brand", "브랜딩·로고"), ("svc-ppt", "PPT·제안서"), ("svc-web", "홈페이지·웹"),
    ("svc-studio", "촬영·스튜디오"), ("catalog", "카탈로그"), ("leaflet", "리플렛"),
    ("pamphlet", "팜플렛"), ("brochure", "브로슈어"), ("poster", "포스터"),
]

def read_meta(page):
    p = ROOT / f"{page}.html"
    if not p.exists():
        return None
    s = p.read_text(encoding="utf-8")
    def grab(pat, default=""):
        m = re.search(pat, s, re.S | re.I)
        return (m.group(1).strip() if m else default)
    return {
        "title": grab(r'<title>(.*?)</title>'),
        "description": grab(r'<meta\s+name="description"\s+content="([^"]*)"'),
        "keywords": grab(r'<meta\s+name="keywords"\s+content="([^"]*)"'),
    }

def bake_seo(page, meta):
    """페이지 <head>의 title·description·keywords를 실제로 교체(정적 HTML → AI/검색 읽음)."""
    p = ROOT / f"{page}.html"
    s = p.read_text(encoding="utf-8")
    def esc_attr(v):
        return v.replace('"', "&quot;")
    if meta.get("title"):
        s = re.sub(r'<title>.*?</title>', f'<title>{meta["title"]}</title>', s, count=1, flags=re.S)
        # og:title·twitter:title 동기화
        s = re.sub(r'(<meta\s+property="og:title"\s+content=")[^"]*(")', rf'\g<1>{esc_attr(meta["title"])}\g<2>', s)
        s = re.sub(r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")', rf'\g<1>{esc_attr(meta["title"])}\g<2>', s)
    def set_meta(name, val):
        nonlocal s
        if re.search(rf'<meta\s+name="{name}"\s+content="[^"]*"', s):
            s = re.sub(rf'(<meta\s+name="{name}"\s+content=")[^"]*(")', rf'\g<1>{esc_attr(val)}\g<2>', s, count=1)
        elif val:
            s = s.replace("</head>", f'<meta name="{name}" content="{esc_attr(val)}">\n</head>', 1)
    if "description" in meta:
        set_meta("description", meta["description"])
        s = re.sub(r'(<meta\s+property="og:description"\s+content=")[^"]*(")', rf'\g<1>{esc_attr(meta["description"])}\g<2>', s)
    if "keywords" in meta:
        set_meta("keywords", meta["keywords"])
    p.write_text(s, encoding="utf-8")
    return True

if __name__ == "__main__":
    print("baked portfolio:", bake_portfolio())
    for pg, _ in FAQ_PAGES:
        print("faq", pg, bake_faq(pg))
