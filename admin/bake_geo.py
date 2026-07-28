# -*- coding: utf-8 -*-
"""로컬(GEO) 완성: 완전한 LocalBusiness JSON-LD를 전 주요 페이지에 굽고, 푸터 주소 텍스트 갱신.
주소=인천 남동구 미래로 16 3층(우21558), 좌표 37.4514027/126.7050163, 평일 09:00 ~ 18:00."""
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
        "email": "work@firstmkt.co.kr",
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

def organization_ld(domain="https://incheondesign.co.kr"):
    """메인 전용 Organization 스키마 — AI·검색엔진이 '지역 업체'가 아니라
    '회사 엔티티'로 인식하게 함(2026-07-28). ⚠️sameAs(SNS)는 실제 계정 확인 후 추가."""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": domain + "/#organization",
        "name": "퍼스트디자인 인천지사",
        "legalName": "주식회사 퍼스트마케팅컴퍼니",
        "url": domain + "/",
        "logo": {"@type": "ImageObject", "url": domain + "/theme/assets/first/favicon.png"},
        "image": domain + "/theme/assets/first/mainbanner0001.jpg",
        "description": ("인천·부천·시흥 등 서부수도권 기업·관공서·교육기관을 위한 디자인 제작 전문. "
                        "카탈로그·브로슈어·리플렛·포스터 인쇄물부터 로고·브랜딩, PPT·제안서, "
                        "홈페이지·웹, 촬영, 마케팅까지 기획에서 납품까지 한 팀이 진행합니다."),
        "telephone": PHONE,
        "email": "work@firstmkt.co.kr",
        "vatID": "884-88-01123",
        "founder": {"@type": "Person", "name": "김우석"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "미래로 16 3층",
            "addressLocality": "남동구",
            "addressRegion": "인천광역시",
            "postalCode": "21558",
            "addressCountry": "KR",
        },
        "areaServed": [{"@type": "City", "name": n} for n in ("인천광역시", "부천시", "시흥시")],
        "parentOrganization": {"@type": "Organization", "name": "㈜퍼스트마케팅컴퍼니"},
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": PHONE,
            "email": "work@firstmkt.co.kr",
            "contactType": "customer service",
            "areaServed": "KR",
            "availableLanguage": ["Korean"],
        }],
        "knowsAbout": ["카탈로그 제작", "브로슈어 제작", "리플렛 제작", "포스터 제작",
                       "로고 디자인", "브랜딩", "PPT 제안서 디자인", "홈페이지 제작",
                       "제품 촬영", "블로그 마케팅"],
    }

def bake_organization(domain="https://incheondesign.co.kr"):
    """메인에 Organization 스키마 삽입(멱등)."""
    domain = domain.rstrip("/")
    p = ROOT / "index.html"
    if not p.exists():
        return 0
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'<!--org-ld-->.*?<!--/org-ld-->', '', s, flags=re.S)
    ld = ('<!--org-ld--><script type="application/ld+json">'
          + json.dumps(organization_ld(domain), ensure_ascii=False) + '</script><!--/org-ld-->')
    s = s.replace("</head>", ld + "\n</head>", 1)
    p.write_text(s, encoding="utf-8")
    return 1

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
        # 푸터 주소 텍스트 갱신
        # ⚠️예전엔 '인천광역시'만 보고 치환해서, 재실행할 때마다 주소가 덧붙어
        #   "…미래로 16 3층 남동구 미래로 16 3층 남동구 미래로 16 3층"이 됐음(2026-07-28).
        #   → 소재지 항목 전체를 통째로 다시 씀(멱등).
        s = re.sub(r'(소재지\s*:\s*)[^|<]*', r'\g<1>' + ADDR_FULL + ' ', s)
        p.write_text(s, encoding="utf-8")
        done += 1
    return done

if __name__ == "__main__":
    print("LocalBusiness 삽입·주소 갱신:", bake_geo(), "페이지")
    print("Organization 스키마(메인):", bake_organization(), "페이지")
