# -*- coding: utf-8 -*-
"""칼럼글 AEO 보강 (2026-07-28 사용자 "칼럼글의 AEO 점수를 올릴려면 어떻게 할까").

칼럼글 감점 원인 3가지와 해법:
 ① FAQ 구조화데이터 없음  → 글 끝 FAQ + FAQPage 스키마
 ② 질문·답변 블록 없음     → 같은 FAQ가 화면에도 노출(AI는 본문과 스키마가 일치할 때 인용)
 ③ 소제목이 H2만 5개      → FAQ 섹션을 H2 + 각 질문을 H3로 마크업해 위계 확보
덤으로 GEO: 본문 '인천' 1회뿐이라 감점 → FAQ 답변에 지역 맥락을 자연스럽게 포함.
질문은 서비스 페이지 FAQ와 겹치지 않게 '글 주제'에 붙는 것만 골랐다(중복 콘텐츠 방지).
재실행 안전: <!--col-faq--> 마커로 교체."""
import re, json, pathlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

R = pathlib.Path(__file__).parent
DOMAIN = "https://incheondesign.co.kr"

FAQ = {
    "column-design": [
        ("디자인이 잘 나왔는지 어떻게 판단하나요?",
         "예쁜지보다 <b>목적을 달성하는지</b>로 보시는 게 정확합니다. 카탈로그라면 제품 정보가 읽는 순서대로 들어오는지, "
         "로고라면 명함 크기로 줄여도 알아볼 수 있는지가 기준입니다. 인천·부천·시흥 지역이라면 대면 미팅에서 "
         "실물 출력본으로 확인하시는 편이 화면으로 보는 것보다 훨씬 확실합니다."),
        ("시안은 몇 개를 받아보는 게 좋을까요?",
         "방향이 서로 다른 2~3개가 적당합니다. 시안이 많아지면 오히려 판단 기준이 흐려지고 결정이 늦어집니다. "
         "먼저 방향을 고르고, 고른 안을 다듬어 가는 순서가 결과물이 좋습니다."),
        ("디자인을 맡기기 전에 무엇을 준비하면 되나요?",
         "완성된 원고보다 <b>누구에게 무엇을 전달하고 싶은지</b>가 먼저입니다. 타깃과 사용 목적만 정리되어 있으면 "
         "원고 정리와 사진 촬영은 함께 진행할 수 있습니다."),
    ],
    "column-catalog": [
        ("카탈로그 제작 기간은 얼마나 걸리나요?",
         "일반적으로 <b>디자인 2주 + 인쇄·가공 1주</b>로 3주 전후입니다. 페이지 수와 원고 준비 상태에 따라 달라지며, "
         "전시회나 행사 일정이 있으면 그 날짜에서 역산해 일정을 잡아 드립니다."),
        ("원고와 제품 사진이 없어도 시작할 수 있나요?",
         "네. 원고 정리와 제품 촬영까지 한 팀에서 진행합니다. 인천·부천·시흥 등 서부수도권은 촬영 일정을 "
         "빠르게 잡을 수 있어 준비가 전혀 없는 상태에서도 시작하실 수 있습니다."),
        ("페이지 수는 어떻게 정하는 게 좋나요?",
         "중철 제본은 <b>4페이지 단위</b>로 늘어나므로 8·12·16페이지처럼 맞추는 것이 경제적입니다. "
         "제품 수와 설명 분량을 알려주시면 적정 페이지를 역산해 제안드립니다."),
    ],
    "column-logo": [
        ("로고 리뉴얼 주기가 정해져 있나요?",
         "연차로 정하기보다 <b>신호로 판단</b>하는 편이 맞습니다. 사업 영역이 처음과 달라졌을 때, 작은 크기에서 "
         "형태가 뭉개질 때, 원본 파일이 없어 매번 새로 그려야 할 때가 대표적인 리뉴얼 시점입니다."),
        ("기존 로고를 살리면서 다듬을 수도 있나요?",
         "가능합니다. 형태의 골격은 유지하고 비례·컬러·서체만 정리하는 <b>리프레시</b> 방식입니다. "
         "이미 인지도가 쌓인 브랜드라면 전면 교체보다 리프레시가 유리한 경우가 많습니다."),
        ("로고를 바꾸면 어디까지 다시 만들어야 하나요?",
         "명함·봉투 같은 서식, 간판·사이니지, SNS 프로필, 홈페이지 헤더가 기본 범위입니다. "
         "리뉴얼 단계에서 적용 목록을 먼저 정리하면 누락 없이 한 번에 교체할 수 있습니다."),
    ],
    "column-print": [
        ("인쇄 사고는 주로 무엇 때문에 생기나요?",
         "가장 많은 두 가지는 <b>이미지 해상도 부족</b>과 <b>재단 여유(도련) 누락</b>입니다. 화면에서 선명해 보이는 "
         "웹용 이미지는 인쇄하면 흐려지고, 배경이 재단선까지만 채워져 있으면 흰 테두리가 남습니다."),
        ("원본 파일은 어떤 형식으로 전달하면 되나요?",
         "편집 원본(ai·indd)과 함께 <b>폰트를 아웃라인 처리한 PDF</b>를 주시는 것이 가장 안전합니다. "
         "폰트가 없는 환경에서 열면 글자가 바뀌기 때문입니다."),
        ("인쇄물 색이 모니터와 다르게 나왔습니다.",
         "모니터는 빛(RGB), 인쇄는 잉크(CMYK)라 완전히 같게 만들 수는 없습니다. 브랜드 컬러처럼 중요한 색은 "
         "별색 지정이나 인쇄 감리로 맞추며, 인천 지역은 인쇄 전 실물 샘플 확인도 도와드립니다."),
    ],
}

CSS_MARK = "col-faq"
CSS = """
/* col-faq: 칼럼글 하단 FAQ (AEO — 화면 노출 + FAQPage 스키마 일치) */
.col-faq { max-width: 780px; margin: 64px auto 0; padding: 0 0 8px; }
.col-faq-t { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; color: #111;
             margin: 0 0 6px; padding-bottom: 18px; border-bottom: 2px solid #111; }
.col-faq-s { font-size: 15px; color: #767676; margin: 14px 0 4px; }
.col-faq-item { border-bottom: 1px solid #e6eceb; }
.col-faq-item summary { display: flex; align-items: baseline; gap: 9px; cursor: pointer;
    font-size: 17px; font-weight: 700; color: #111; padding: 20px 34px 20px 2px;
    list-style: none; position: relative; word-break: keep-all; }
.col-faq-item summary::-webkit-details-marker { display: none; }
.col-faq-item summary::before { content: "Q."; color: #0C9384; font-weight: 800; flex: none; }
.col-faq-item summary::after { content: "+"; position: absolute; right: 6px; top: 50%;
    transform: translateY(-50%); font-size: 21px; color: #9aa7a5; transition: transform .2s ease; }
.col-faq-item[open] summary::after { transform: translateY(-50%) rotate(45deg); color: #0C9384; }
.col-faq-item h3 { font-size: inherit; font-weight: inherit; color: inherit; margin: 0; display: inline; }
.col-faq-a { padding: 0 2px 24px 30px; font-size: 16px; color: #555; line-height: 1.85; }
.col-faq-a p { margin: 0; word-break: keep-all; }
.col-faq-a b { color: #222; font-weight: 700; }
@media (max-width: 767px) {
    .col-faq { margin-top: 44px; }
    .col-faq-t { font-size: 20px; }
    .col-faq-item summary { font-size: 15.5px; padding: 16px 30px 16px 2px; }
    .col-faq-a { font-size: 14.5px; padding-left: 24px; }
}
"""

def build_html(items):
    rows = ""
    for q, a in items:
        rows += (f'<details class="col-faq-item"><summary><h3>{q}</h3></summary>'
                 f'<div class="col-faq-a"><p>{a}</p></div></details>')
    return ('<!--col-faq--><section class="col-faq">'
            '<h2 class="col-faq-t">이 주제로 자주 받는 질문</h2>'
            '<p class="col-faq-s">퍼스트디자인 인천지사가 상담에서 실제로 많이 받는 질문을 정리했습니다.</p>'
            f'{rows}</section><!--/col-faq-->')

def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer",
                                               "text": re.sub(r"<[^>]+>", "", a)}} for q, a in items]}

# CSS 설치
css_path = R / "theme" / "css" / "pages" / "column2.css"
ct = css_path.read_text(encoding="utf-8")
if CSS_MARK not in ct:
    css_path.write_text(ct + CSS, encoding="utf-8")
    print("column2.css: FAQ 스타일 추가")

for page, items in FAQ.items():
    p = R / f"{page}.html"
    if not p.exists():
        print(f"⚠️{page}.html 없음"); continue
    s = p.read_text(encoding="utf-8")
    # 재실행 대비 기존 삽입분 제거
    s = re.sub(r'<!--col-faq-->.*?<!--/col-faq-->', '', s, flags=re.S)
    s = re.sub(r'<!--col-faq-ld-->.*?<!--/col-faq-ld-->', '', s, flags=re.S)

    # ① 화면 FAQ — 이전/다음 글 내비 앞(=본문 끝)에 삽입
    html = build_html(items)
    m = re.search(r'<nav class="blog-single-nav"|<div class="blog-single-nav"'
                  r'|<section class="cta-section"', s)
    if not m:
        print(f"⚠️{page}: 삽입 위치 못 찾음"); continue
    s = s[:m.start()] + html + "\n" + s[m.start():]

    # ② FAQPage 스키마
    ld = ('<!--col-faq-ld--><script type="application/ld+json">'
          + json.dumps(faq_schema(items), ensure_ascii=False) + '</script><!--/col-faq-ld-->')
    s = s.replace("</head>", ld + "\n</head>", 1)

    # ③ BlogPosting description이 미러 잔재 문구로 남아 있던 것 정정 → 실제 메타 설명과 동기화
    dm = re.search(r'<meta name="description" content="([^"]*)"', s)
    if dm:
        s = re.sub(r'("@type": "BlogPosting", "headline": "[^"]*", "description": ")[^"]*(")',
                   lambda x: x.group(1) + dm.group(1) + x.group(2), s)

    p.write_text(s, encoding="utf-8")
    print(f"{page}.html: FAQ {len(items)}문항 + 스키마 삽입")
print("완료")
