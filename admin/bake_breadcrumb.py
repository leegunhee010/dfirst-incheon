# -*- coding: utf-8 -*-
"""전 페이지 BreadcrumbList 구조화데이터 일괄 굽기(AEO). 화면 X, 크롤러만 읽음. JS 0 정적.
경로: 홈 > [상위] > 현재. 마커 <!--crumb-ld--> 재실행 안전. 블로그 상세는 자체 col-jsonld 있어 제외."""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOMAIN = "https://incheondesign.co.kr"

# page → (표시명, 상위경로[(name, file)...])  상위 없으면 홈만
CRUMBS = {
    "about": ("회사소개", []),
    "portfolio": ("포트폴리오", []),
    "column": ("블로그", []),
    "contact": ("문의", []),
    "svc-brand": ("브랜딩 · 로고 제작", []),
    "svc-ppt": ("PPT · 제안서", []),
    "svc-web": ("홈페이지 · 웹", []),
    "svc-studio": ("촬영 · 스튜디오", []),
    "catalog": ("카탈로그 · 카다로그 제작", []),
    "leaflet": ("리플렛 · 리플릿 제작", []),
    "pamphlet": ("팜플렛 · 팜플릿 제작", []),
    "brochure": ("브로슈어 · 브로셔 제작", []),
    "poster": ("포스터 제작", []),
}

def bake_breadcrumbs():
    done = 0
    for page, (name, parents) in CRUMBS.items():
        p = ROOT / f"{page}.html"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        s = re.sub(r'<!--crumb-ld-->.*?<!--/crumb-ld-->', '', s, flags=re.S)
        items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": DOMAIN + "/"}]
        pos = 2
        for pn, pf in parents:
            items.append({"@type": "ListItem", "position": pos, "name": pn, "item": f"{DOMAIN}/{pf}"})
            pos += 1
        items.append({"@type": "ListItem", "position": pos, "name": name,
                      "item": f"{DOMAIN}/{page}.html"})
        ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
        block = ('<!--crumb-ld--><script type="application/ld+json">'
                 + json.dumps(ld, ensure_ascii=False) + '</script><!--/crumb-ld-->')
        s = s.replace("</head>", block + "\n</head>", 1)
        p.write_text(s, encoding="utf-8")
        done += 1
    return done

if __name__ == "__main__":
    print("BreadcrumbList 삽입:", bake_breadcrumbs(), "페이지")
