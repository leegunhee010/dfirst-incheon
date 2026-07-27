# -*- coding: utf-8 -*-
"""로컬(GEO) 완성: 완전한 LocalBusiness JSON-LD를 전 주요 페이지에 굽고, 푸터 주소 텍스트 갱신.
주소=인천 남동구 미래로 16 3층(우21558), 좌표 37.4514027/126.7050163, 평일 09:00–18:00."""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

ADDR_FULL = "인천광역시 남동구 미래로 16 3층"
PHONE = "+82-1600-9487"
GEO = (37.4514027, 126.7050163)

# LocalBusiness 삽입 대상 — 전 페이지(블로그·목록 포함, 회사 엔티티 사이트 전역)
GEO_PAGES = ["index", "about", "portfolio", "contact", "column",
             "svc-brand", "svc-ppt", "svc-web", "svc-studio", "svc-mkt",
             "catalog", "leaflet", "pamphlet", "brochure", "poster",
             "column-design", "column-catalog", "column-logo", "column-print"]

def localbusiness_ld(domain="https://incheondesign.co.kr"):
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": domain + "/#localbusiness",
        "name": "퍼스트디자인 인천지사",
        "description": "인천 카탈로그·브로슈어·리플렛·포스터·로고 디자인 제작 전문. 기획부터 인쇄·납품까지 원스톱.",
        "url": domain + "/",
        "telephone": PHONE,
        "email": "firstmk1111@gmail.com",
        "image": domain + "/theme/assets/first/mainbanner0001.jpg",
        "priceRange": "₩₩",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "미래로 16 3층",
            "addressLocality": "남동구",
            "addressRegion": "인천광역시",
            "postalCode": "21558",
            "addressCountry": "KR",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "09:00", "closes": "18:00",
        }],
        "areaServed": [{"@type": "City", "name": n} for n in ["인천광역시", "부천시", "시흥시"]],
        "parentOrganization": {"@type": "Organization", "name": "㈜퍼스트마케팅컴퍼니"},
    }

def bake_geo(domain="https://incheondesign.co.kr"):
    domain = domain.rstrip("/")
    ld = ('<!--localbiz--><script type="application/ld+json">'
          + json.dumps(localbusiness_ld(domain), ensure_ascii=False) + '</script><!--/localbiz-->')
    done = 0
    for page in GEO_PAGES:
        p = ROOT / f"{page}.html"
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        # 기존 관리자 삽입분 제거
        s = re.sub(r'<!--localbiz-->.*?<!--/localbiz-->', '', s, flags=re.S)
        # 홈의 기존(반쪽) LocalBusiness JSON-LD 제거 → 완전본으로 대체
        s = re.sub(r'<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"LocalBusiness".*?\}\s*</script>',
                   '', s, flags=re.S)
        s = s.replace("</head>", ld + "\n</head>", 1)
        # 푸터 주소 텍스트: "인천광역시"(단독) → 전체 주소
        s = re.sub(r'(소재지\s*:\s*)인천광역시(?!\S)', r'\g<1>' + ADDR_FULL, s)
        s = s.replace("소재지 : 인천광역시 &nbsp;", f"소재지 : {ADDR_FULL} &nbsp;")
        p.write_text(s, encoding="utf-8")
        done += 1
    return done

if __name__ == "__main__":
    print("LocalBusiness 삽입·주소 갱신:", bake_geo(), "페이지")
