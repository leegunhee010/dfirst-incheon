# -*- coding: utf-8 -*-
"""기술 SEO 일괄: canonical + sitemap.xml + robots.txt + rss.xml + 페이지별 keywords.
도메인 incheondesign.co.kr. 관리자 SEO설정 탭에서도 재호출 가능(bake_seo_technical(domain))."""
import re, json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data"

# 페이지 → (우선순위, 변경빈도, 기본키워드)
PAGES = {
    "index": (1.0, "weekly", "인천 디자인, 카탈로그 제작, 브로슈어 제작, 리플렛 제작, 포스터 제작, 로고 디자인, 회사소개서 제작, 인천 인쇄"),
    "about": (0.7, "monthly", "퍼스트디자인 인천지사, 인천 디자인 회사, 카탈로그 브로슈어 전문, 편집디자인"),
    "portfolio": (0.8, "weekly", "인천 디자인 포트폴리오, 카탈로그 브로슈어 리플렛 로고 제작 사례"),
    "column": (0.7, "weekly", "인천 디자인 블로그, 카탈로그 제작 팁, 인쇄 가이드"),
    "contact": (0.6, "monthly", "인천 디자인 문의, 카탈로그 제작 견적, 인천 인쇄 상담"),
    "svc-brand": (0.9, "monthly", "로고 제작, 브랜딩, CI BI 디자인, 인천 로고 디자인, 네이밍"),
    "svc-ppt": (0.9, "monthly", "PPT 제작, 제안서 디자인, 회사소개 PPT, 인천 발표자료"),
    "svc-web": (0.9, "monthly", "홈페이지 제작, 웹 디자인, 반응형 홈페이지, 인천 웹사이트"),
    "svc-studio": (0.9, "monthly", "제품 촬영, 스튜디오 촬영, 인천 제품 사진, 상세페이지 촬영"),
    "catalog": (0.9, "monthly", "카탈로그 제작, 카다로그 제작, 카탈로그 디자인, 인천 카탈로그, 제품 카탈로그"),
    "leaflet": (0.9, "monthly", "리플렛 제작, 리플릿 제작, 2단 3단 접지, 인천 리플렛 디자인"),
    "pamphlet": (0.9, "monthly", "팜플렛 제작, 팜플릿 제작, 소책자 제작, 인천 팜플렛 디자인"),
    "brochure": (0.9, "monthly", "브로슈어 제작, 브로셔 제작, 회사소개서 제작, 인천 브로슈어 디자인"),
    "poster": (0.9, "monthly", "포스터 제작, 포스터 디자인, 행사 포스터, 인천 포스터 인쇄"),
    "column-catalog": (0.6, "yearly", "카탈로그 제작, 카탈로그 디자인 팁"),
    "column-design": (0.6, "yearly", "편집 디자인, 디자인 제작 가이드"),
    "column-logo": (0.6, "yearly", "로고 제작, 브랜딩 가이드"),
    "column-print": (0.6, "yearly", "인쇄 가이드, 후가공, 용지 선택"),
}

def _canon(domain, page):
    return domain + ("/" if page == "index" else f"/{page}.html")

def bake_seo_technical(domain="https://incheondesign.co.kr"):
    domain = domain.rstrip("/")
    today = "2026-07-24"
    changed = []
    urls = []
    for page, (prio, freq, kw) in PAGES.items():
        p = ROOT / f"{page}.html"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        url = _canon(domain, page)
        urls.append((url, prio, freq))
        # 1) canonical (없으면 추가, 있으면 교체)
        link = f'<link rel="canonical" href="{url}">'
        if re.search(r'<link\s+rel="canonical"[^>]*>', s):
            s = re.sub(r'<link\s+rel="canonical"[^>]*>', link, s, count=1)
        else:
            s = s.replace("</head>", link + "\n</head>", 1)
        # 2) og:url 동기화(없으면 추가)
        if re.search(r'<meta\s+property="og:url"[^>]*>', s):
            s = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")', rf'\g<1>{url}\g<2>', s)
        else:
            s = s.replace("</head>", f'<meta property="og:url" content="{url}">\n</head>', 1)
        # 3) keywords (없을 때만 채움 — 관리자 수정분 보존)
        if not re.search(r'<meta\s+name="keywords"', s):
            s = s.replace("</head>", f'<meta name="keywords" content="{kw}">\n</head>', 1)
        p.write_text(s, encoding="utf-8")
        changed.append(page)

    # 4) sitemap.xml
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, prio, freq in urls:
        sm.append(f'  <url><loc>{url}</loc><lastmod>{today}</lastmod>'
                  f'<changefreq>{freq}</changefreq><priority>{prio}</priority></url>')
    sm.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    # 5) robots.txt
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /admin/\n\n"
        f"Sitemap: {domain}/sitemap.xml\n", encoding="utf-8")

    # 6) rss.xml (블로그 글)
    items = []
    for page in ["column-design", "column-catalog", "column-logo", "column-print"]:
        p = ROOT / f"{page}.html"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        d = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', s)
        title = (t.group(1).split("|")[0].strip() if t else page)
        desc = (d.group(1) if d else "")
        items.append(f'    <item><title>{title}</title>'
                     f'<link>{_canon(domain, page)}</link>'
                     f'<description>{desc}</description>'
                     f'<pubDate>Thu, 24 Jul 2026 09:00:00 +0900</pubDate></item>')
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<rss version="2.0"><channel>\n'
           '    <title>퍼스트디자인 인천지사 블로그</title>\n'
           f'    <link>{domain}/column.html</link>\n'
           '    <description>카탈로그·브로슈어·로고 제작 인사이트</description>\n'
           '    <language>ko</language>\n' + "\n".join(items) +
           '\n</channel></rss>')
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")

    # 도메인 설정 저장(관리자 SEO 탭 반영)
    st = json.loads((DATA / "settings.json").read_text(encoding="utf-8")) if (DATA / "settings.json").exists() else {}
    st["domain"] = domain
    (DATA / "settings.json").write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(changed), len(urls)

if __name__ == "__main__":
    n, u = bake_seo_technical()
    print(f"canonical/keywords 적용: {n}페이지 | sitemap {u}개 URL | robots.txt·rss.xml 생성")
