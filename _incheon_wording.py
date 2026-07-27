# -*- coding: utf-8 -*-
"""전 페이지 인천 워딩 보강 (2026-07-27 사용자 "다른 홈페이지들도 좀 녹아져 있어야해").
svc-mkt처럼 각 페이지 본문에 '인천'이 자연스럽게 들어가도록 in-place 패치.
⚠️생성 스크립트 재실행 없이 현재 HTML을 직접 수정 — 관리자 bake 산출물(crumb-ld/localbiz 등) 보존.
방식: ①히어로 카피 치환 ②서비스·인쇄 페이지 FAQ에 인천 대면상담 문항 1개 추가(페이지별 키워드 변형).
재실행 안전: 치환 전 존재 확인, FAQ는 '인천에서' 문항 중복 검사."""
import pathlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(__file__).parent

# ---------- ① 히어로·인트로 카피 치환 (파일: [(old, new), ...]) ----------
SWAPS = {
    "svc-ppt.html": [("결과를 만드는 제안서 · 발표자료.",
                      "인천 기업의 결과를 만드는 제안서 · 발표자료.")],
    "svc-web.html": [("브랜드를 담는 홈페이지 · 쇼핑몰.",
                      "인천 브랜드를 담는 홈페이지 · 쇼핑몰.")],
    "column.html": [("제작 전에 알아두면 좋은 인사이트를 모았습니다.",
                     "인천 기업이 제작 전에 알아두면 좋은 인사이트를 모았습니다.")],
    "portfolio.html": [("카탈로그부터 로고까지, 퀄리티로 확인하세요.",
                        "카탈로그부터 로고까지, 인천에서도 같은 퀄리티 그대로.")],
    "contact.html": [("설문지를 작성해주시면,<br>빠르고 자세한 상담이 가능합니다.",
                      "설문지를 작성해주시면,<br>인천 담당자가 빠르고 자세하게 상담해 드립니다.")],
}

# ---------- ② FAQ 인천 대면상담 문항 (페이지별 키워드 변형, svc-brand Q5 톤) ----------
FAQ_ADD = {
    "svc-ppt.html": ("인천에서 직접 만나 상담할 수 있나요?",
        "네. 인천·부천·시흥 등 서부수도권은 필요한 날 바로 대면 미팅이 가능합니다. 발표 자료 특성상 초반 방향 논의가 중요해, 원고를 함께 보며 상담드립니다. 전화 1600-9487로 편하게 요청해 주세요."),
    "svc-web.html": ("인천에서 직접 만나 상담할 수 있나요?",
        "네. 인천·부천·시흥 등 서부수도권은 필요한 날 바로 대면 미팅이 가능합니다. 페이지 구성과 레퍼런스를 화면으로 함께 보며 상담드리면 방향이 훨씬 빨리 잡힙니다. 전화 1600-9487로 편하게 요청해 주세요."),
    "svc-studio.html": ("촬영 전 인천에서 대면 미팅이 가능한가요?",
        "네. 인천·부천·시흥 등 서부수도권은 촬영 기획 단계부터 대면 미팅으로 품목과 컷 리스트를 함께 정리해 드립니다. 전화 1600-9487로 편하게 문의해 주세요."),
    "catalog.html": ("인천에서 카탈로그 제작 상담을 직접 받을 수 있나요?",
        "네. 인천·부천·시흥 등 서부수도권은 필요한 날 바로 대면 미팅이 가능합니다. 용지·후가공 실물 샘플을 보며 상담하실 수 있어 카탈로그 사양을 정하기 훨씬 수월합니다. 전화 1600-9487로 요청해 주세요."),
    "leaflet.html": ("인천에서 리플렛 제작 상담이 가능한가요?",
        "네. 인천·부천·시흥 등 서부수도권은 바로 대면 미팅이 가능합니다. 접지 방식과 용지를 실물 샘플로 보면서 정할 수 있어 완성도가 달라집니다. 전화 1600-9487로 편하게 문의해 주세요."),
    "pamphlet.html": ("인천에서 팜플렛 제작 상담이 가능한가요?",
        "네. 인천·부천·시흥 등 서부수도권은 바로 대면 미팅이 가능합니다. 행사 일정과 분량을 보고 접지형·소책자형 중 유리한 형태를 그 자리에서 추천드립니다. 전화 1600-9487로 요청해 주세요."),
    "brochure.html": ("인천에서 브로슈어 제작 상담이 가능한가요?",
        "네. 인천·부천·시흥 등 서부수도권은 바로 대면 미팅이 가능합니다. 고급 용지와 후가공(박·형압) 실물 샘플을 보며 사양을 정하실 수 있습니다. 전화 1600-9487로 요청해 주세요."),
    "poster.html": ("인천에서 포스터 제작 상담이 가능한가요?",
        "네. 인천·부천·시흥 등 서부수도권은 바로 대면 미팅이 가능합니다. 부착 환경과 규격을 알려주시면 재질과 인쇄 방식까지 한 번에 안내드립니다. 전화 1600-9487로 요청해 주세요."),
}

for name, swaps in SWAPS.items():
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    n = 0
    for old, new in swaps:
        if new in t:
            print(f"{name}: 이미 적용됨")
        elif old in t:
            t = t.replace(old, new); n += 1
        else:
            print(f"⚠️{name}: 원문 못 찾음 — {old[:30]}...")
    if n:
        p.write_text(t, encoding="utf-8")
        print(f"{name}: 카피 {n}건 치환")

for name, (q, a) in FAQ_ADD.items():
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    if q in t:
        print(f"{name}: FAQ 이미 있음"); continue
    item = (f'<details class="svc-faq-item"><summary>{q}</summary>'
            f'<div class="svc-faq-a"><p>{a}</p></div></details>')
    anchor = "</details></section>"
    cnt = t.count(anchor)
    if cnt == 0:
        print(f"⚠️{name}: FAQ 앵커 없음"); continue
    # 마지막 FAQ 항목 뒤(섹션 닫히기 직전)에 삽입 — 마지막 occurrence 사용
    i = t.rfind(anchor)
    t = t[:i] + "</details>" + item + "</section>" + t[i + len(anchor):]
    p.write_text(t, encoding="utf-8")
    print(f"{name}: FAQ 추가")

# ---------- ③ FAQPage JSON-LD에도 새 문항 반영 (bake_seo가 구운 <!--faq-jsonld--> 블록) ----------
import json, re
for name, (q, a) in FAQ_ADD.items():
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    m = re.search(r'(<!--faq-jsonld--><script type="application/ld\+json">)(.*?)(</script>)', t, re.S)
    if not m:
        print(f"{name}: faq-jsonld 없음(스킵)"); continue
    d = json.loads(m.group(2))
    if any(e.get("name") == q for e in d.get("mainEntity", [])):
        print(f"{name}: 스키마 이미 있음"); continue
    d["mainEntity"].append({"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}})
    t = t[:m.start(2)] + json.dumps(d, ensure_ascii=False) + t[m.end(2):]
    p.write_text(t, encoding="utf-8")
    print(f"{name}: 스키마 문항 추가")
print("done")
