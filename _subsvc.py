# -*- coding: utf-8 -*-
"""인쇄 하위 서비스 전용 페이지 5종: catalog / leaflet / pamphlet / brochure / poster .html
(2026-07-22 사용자: "하오커뮤니케이션 디자인센터에 카탈로그란 이런 거 있걸랑 그거 만들어, 다른 레이아웃으로, 서비스마다")
구성은 design.haoc.co.kr/catalog-brochure.html 실측(히어로→진행과정→작업사례→정보성 소개글→FAQ→CTA)을 따르되,
레이아웃은 우리 언어로 재구성: hero2 밴드 + 가로 스플릿 소개글(상하 스택) + 4열 사례 그리드 + 타임라인 + FAQ 아코디언.
크롬(헤더/푸터/CTA) = 생성된 svc-print.html에서 추출 → 체인 맨 마지막에 실행.
체인: mirror → overlay → subpages → about_hh → services → hero2 → subsvc"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
P = "theme/assets/first/pf/"
F = "theme/assets/first/"

# ---------- 페이지 데이터 ----------
# (en제목, 한글키워드[이형표기], 히어로 서브 2줄, 소개글01/02, 사례4[(img,캡션)], FAQ5)
PAGES = {
    "catalog": {
        "en": "Catalog", "kw": "카탈로그 · 카다로그 제작 디자인",
        "sub": ('제품과 기업의 가치를 체계적으로 담는 카탈로그 제작.<br/>'
                '<span class="g">기획부터 인쇄·납품까지 한 팀이 진행합니다.</span>'),
        "intro": [
            ("카탈로그 제작에 대하여",
             "카탈로그(카다로그)는 제품과 서비스를 체계적으로 보여주는 가장 기본적인 기업 홍보물입니다. "
             "전시회·영업 현장·관공서 제출자료까지 활용 범위가 넓고, 잘 만든 카탈로그 한 권은 영업사원 몇 명의 역할을 대신합니다. "
             "퍼스트디자인 인천지사는 본사 12년의 편집 노하우로 제품 스펙을 읽기 쉬운 구조로 정리하고, "
             "브랜드 톤에 맞는 카탈로그 디자인을 제작합니다."),
            ("카탈로그 준비 방법",
             "카탈로그 제작을 준비할 때는 목적과 타깃을 먼저 정하고, 그에 맞는 페이지 구성과 분량을 잡는 것이 중요합니다. "
             "원고와 제품 사진이 준비되지 않아도 괜찮습니다 — 원고 정리와 제품 촬영까지 한 팀에서 해결됩니다. "
             "인쇄 단계에서는 용지·코팅·제본 방식에 따라 완성도가 크게 달라지므로, 대면 미팅에서 실물 샘플을 보고 결정하실 수 있습니다."),
        ],
        "works": [(P + "g17.png", "제품 카탈로그 — 해양장비 제조기업"),
                  (F + "banner_Gukgwasu01.jpg", "기관 브로슈어 — 국립과학수사연구원"),
                  (F + "banner_kb01.jpg", "사보 내지 — KB국민은행"),
                  (F + "banner_samsung01.jpg", "기업 브로슈어 — 삼성화재")],
        "blocks": [
            ("제품 카탈로그 제작", P + "g20.png",
             "제품 라인업과 스펙을 한눈에 비교할 수 있게 정리합니다. 사양표·이미지·설명의 위계를 잡아 영업 현장에서 바로 쓰이는 카탈로그를 만듭니다.",
             ["제품 라인업 정리", "사양표 편집", "영업용 판형 설계", "제품 촬영 연계"]),
            ("회사소개형 카탈로그", P + "pf_1781577049020_80075cf8.png",
             "제품 정보에 브랜드 스토리를 더해 회사의 격까지 전달합니다. 기업 소개와 제품 소개가 자연스럽게 이어지도록 구성합니다.",
             ["브랜드 스토리 구성", "실적·연혁 정리", "고급 용지·후가공", "국문·영문 혼용"]),
            ("영문 · 다국어 카탈로그", P + "g29.png",
             "해외 전시회와 수출 상담을 위한 영문·다국어 카탈로그를 제작합니다. 언어별 글자 길이에 맞춰 레이아웃을 다시 잡습니다.",
             ["영문·중문·일문 대응", "언어별 레이아웃 조정", "해외 전시회 판형", "수출바우처 활용 가능"]),
        ],
        "faq": [
            ("카탈로그 제작 기간은 보통 얼마나 걸리나요?",
             "페이지 수와 원고 준비 상태, 촬영 포함 여부에 따라 달라지지만 일반적으로 2~4주가량 소요됩니다. 행사·전시 일정이 있다면 역산해서 일정을 설계해 드립니다."),
            ("카탈로그와 브로슈어는 뭐가 다른가요?",
             "카탈로그는 제품 정보와 스펙을 체계적으로 정리한 인쇄물이고, 브로슈어는 회사소개·브랜드 스토리처럼 메시지 전달에 무게를 둔 홍보물입니다. 용도를 알려주시면 맞는 형태를 추천드립니다."),
            ("제품 사진이 없는데 촬영도 같이 되나요?",
             "네. 자체 촬영팀이 제품 컷과 연출 컷을 촬영해 바로 편집디자인에 반영합니다. 촬영과 디자인을 따로 맡길 때 생기는 톤 차이가 없습니다."),
            ("비용은 어떻게 산정되나요?",
             "페이지 수, 인쇄 수량, 용지·후가공(코팅·박·형압), 촬영 포함 여부로 산정됩니다. 사양을 알려주시면 무료로 견적을 안내드립니다."),
            ("디자인만 맡기고 인쇄는 따로 해도 되나요?",
             "가능합니다. 다만 자체 인쇄소에서 인쇄까지 원스톱으로 진행하면 색 보정과 인쇄 품질을 한 팀이 끝까지 관리할 수 있습니다."),
        ],
    },
    "leaflet": {
        "en": "Leaflet", "kw": "리플렛 · 리플릿 제작 디자인",
        "sub": ('접는 순간까지 설계하는 리플렛 제작.<br/>'
                '<span class="g">행사·매장·영업용 2단 3단 리플렛을 만듭니다.</span>'),
        "intro": [
            ("리플렛 제작에 대하여",
             "리플렛(리플릿)은 접지 형태로 정보를 압축해 전달하는 홍보물로, 행사장 배포·매장 비치·영업 방문용으로 가장 많이 쓰입니다. "
             "적은 예산으로 브랜드와 서비스를 알릴 수 있어 관공서 안내물부터 기업 제품 소개까지 활용 폭이 넓습니다. "
             "퍼스트디자인 인천지사는 펼치는 순서에 따라 메시지가 자연스럽게 읽히도록 접지 구조부터 설계합니다."),
            ("리플렛 준비 방법",
             "리플렛 디자인은 배포 환경을 먼저 정하는 것이 중요합니다. 손에 들고 읽는지, 거치대에 꽂히는지에 따라 표지 구성이 달라집니다. "
             "2단·3단·대문접지 등 접지 방식과 용지 두께에 따라 인상이 크게 바뀌므로, 용도와 수량을 알려주시면 가장 유리한 사양을 추천드립니다. "
             "소량은 디지털 인쇄, 대량 배포용은 옵셋 인쇄로 단가를 낮춰 드립니다."),
        ],
        "works": [(F + "banner_mirae01.jpg", "3단 리플렛 — 미래에셋"),
                  (F + "banner_hitejinro01.jpg", "리플렛 — 하이트진로"),
                  (P + "g26.png", "3단 리플렛 — Wemico"),
                  (P + "g34.png", "안내 리플렛 — 서비스 소개")],
        "blocks": [
            ("2단 · 3단 접지 리플렛", P + "pf_1780562846536_f1710b84.png",
             "가장 널리 쓰이는 접지 형태입니다. 펼치는 순서에 맞춰 정보를 배치해 어느 면을 먼저 보더라도 메시지가 전달되게 만듭니다.",
             ["2단·3단 접지 설계", "면별 메시지 배치", "용지 두께 컨설팅", "소량·대량 인쇄"]),
            ("대문 · 병풍 접지 리플렛", P + "pf_1780562860378_28805540.png",
             "제품 라인업이나 단계별 안내처럼 펼쳤을 때 임팩트가 필요한 내용에 적합합니다. 접는 방식부터 함께 설계합니다.",
             ["대문·병풍 접지", "펼침면 대형 이미지", "단계별 정보 구성", "특수 재단"]),
            ("행사 · 매장 배포용 리플렛", P + "pf_1781576837581_2c038044.jpg",
             "배포 환경까지 고려해 설계합니다. 거치대 비치, 현장 배포, 우편 발송 등 쓰임에 맞춰 판형과 재질을 정합니다.",
             ["거치대 규격 대응", "현장 배포 내구성", "DM 발송 규격", "대량 인쇄 단가 최적화"]),
        ],
        "faq": [
            ("리플렛과 팜플렛은 뭐가 다른가요?",
             "보통 리플렛은 한 장을 접어 만든 홍보물, 팜플렛은 여러 장을 묶은 소책자 형태를 말합니다. 분량이 적으면 리플렛, 내용이 많으면 팜플렛이 유리합니다."),
            ("접지는 어떤 종류가 있나요?",
             "2단 접지, 3단 접지, 대문 접지, 병풍 접지 등이 있습니다. 내용 분량과 읽는 순서에 맞춰 담당 디자이너가 추천드립니다."),
            ("소량 제작도 가능한가요?",
             "네. 디지털 인쇄로 소량도 부담 없이 제작하실 수 있고, 배포용 대량 인쇄는 옵셋으로 단가를 낮춰 드립니다."),
            ("행사 일정이 급한데 맞출 수 있나요?",
             "자체 인쇄소에서 인쇄·후가공까지 한 흐름으로 진행해 외주 대비 일정을 크게 줄일 수 있습니다. 행사일을 알려주시면 역산해 진행합니다."),
            ("원고가 없어도 시작할 수 있나요?",
             "네. 전하고 싶은 내용만 말씀해 주시면 원고 정리와 구성 기획부터 함께 시작합니다."),
        ],
    },
    "pamphlet": {
        "en": "Pamphlet", "kw": "팜플렛 · 팜플릿 제작 디자인",
        "sub": ('행사·기관 안내에 강한 팜플렛 제작.<br/>'
                '<span class="g">접지형부터 소책자형까지 목적에 맞게 설계합니다.</span>'),
        "intro": [
            ("팜플렛 제작에 대하여",
             "팜플렛(팜플릿)은 행사 안내, 기관 홍보, 전시 안내처럼 정보량이 있는 내용을 정리해 전달하는 홍보물입니다. "
             "접지형부터 중철 제본 소책자형까지 형태가 다양해, 분량과 용도에 맞는 구조 설계가 완성도를 좌우합니다. "
             "퍼스트디자인 인천지사는 관공서·교육기관 안내물 제작 경험을 바탕으로 읽는 순서가 명확한 팜플렛을 만듭니다."),
            ("팜플렛 준비 방법",
             "팜플렛 디자인은 전달할 정보의 우선순위를 정리하는 데서 시작합니다. 행사 개요·일정·오시는 길처럼 꼭 들어갈 항목을 먼저 확정하고, "
             "분량에 따라 접지형과 소책자형 중 유리한 형태를 고릅니다. 배포 현장에서 한눈에 읽히는 정보 위계를 만드는 것이 핵심이며, "
             "인쇄 수량과 일정에 맞춰 디지털·옵셋 인쇄를 선택해 드립니다."),
        ],
        "works": [(P + "pf_1781576961440_d52ed960.png", "관광 안내 팜플렛 — 목포시"),
                  (P + "pf_1780561866143_5889af83.png", "안내 팜플렛 — 지역 관광"),
                  (P + "pf_1780561954454_225acbab.png", "안내 책자 — 공공기관 캠페인"),
                  (P + "g08.png", "제품 매뉴얼 — 전자기기")],
        "blocks": [
            ("접지형 팜플렛", P + "pf_1780562838633_700b8156.png",
             "8면 이내 분량이라면 접지형이 경제적입니다. 제본 없이도 정보를 구조적으로 정리할 수 있어 현장 배포에 유리합니다.",
             ["4·6·8면 구성", "제본 없는 경제적 제작", "현장 배포 최적화", "빠른 납기"]),
            ("중철 제본 소책자", P + "pf_1781229209415_5f2c2500.jpg",
             "8페이지 이상 분량은 중철 제본으로 책자 형태를 만듭니다. 행사 안내서, 기관 소개서에 적합합니다.",
             ["8p 이상 4p 단위", "중철·무선 제본", "표지 별도 용지", "페이지 구성 기획"]),
            ("기관 · 관공서 안내 팜플렛", P + "g38.png",
             "관공서·교육기관 안내물 제작 경험을 바탕으로 정보 전달이 명확한 팜플렛을 만듭니다.",
             ["관공서 규격 대응", "다량 정보 구조화", "인포그래픽 편집", "납품 검수 지원"]),
        ],
        "faq": [
            ("팜플렛과 리플렛 중 뭐가 맞을까요?",
             "정보량이 기준입니다. 한 장 접지로 정리되면 리플렛, 페이지가 필요할 만큼 내용이 많으면 소책자형 팜플렛을 추천드립니다. 내용을 보내주시면 판단해 드립니다."),
            ("몇 페이지부터 제본이 필요한가요?",
             "중철 제본은 보통 8페이지부터 4페이지 단위로 늘어납니다. 분량이 애매하면 접지 구조로 페이지를 아끼는 방법도 함께 제안드립니다."),
            ("행사 날짜가 정해져 있는데 가능할까요?",
             "행사일 기준으로 역산해 기획·디자인·인쇄 일정을 잡아 드립니다. 자체 인쇄소라 막바지 수정에도 대응이 빠릅니다."),
            ("원고 없이 시작할 수 있나요?",
             "네. 행사 개요와 자료만 주시면 구성 기획과 원고 정리부터 함께 진행합니다."),
            ("수정은 몇 회까지 가능한가요?",
             "텍스트 변경·이미지 교체·오탈자 수정 등은 횟수 제한 없이 진행합니다. 구성이 완전히 바뀌는 재시안만 별도 협의됩니다."),
        ],
    },
    "brochure": {
        "en": "Brochure", "kw": "브로슈어 · 브로셔 제작 디자인",
        "sub": ('기업의 첫인상을 만드는 브로슈어 제작.<br/>'
                '<span class="g">회사소개서부터 IR·영업자료까지 격을 높입니다.</span>'),
        "intro": [
            ("브로슈어 제작에 대하여",
             "브로슈어(브로셔)는 기업의 신뢰도를 높이는 대표 홍보물입니다. 회사소개서, 기관 소개 책자, 영업 제안용 자료까지 — "
             "읽는 사람이 기업을 판단하는 첫 자료가 되는 만큼 편집의 완성도가 곧 회사의 인상이 됩니다. "
             "퍼스트디자인 인천지사는 국과수·삼성화재·KB국민은행 등과 작업한 본사 편집 노하우로 격이 다른 브로슈어를 만듭니다."),
            ("브로슈어 준비 방법",
             "브로슈어 디자인은 스토리 구성이 절반입니다. 회사 연혁·사업 영역·강점을 나열하는 대신, 읽는 사람이 궁금해할 순서로 재배치합니다. "
             "고급 용지와 후가공(무광 코팅·박·형압)은 손에 잡히는 질감으로 신뢰를 더해 주므로, 용도와 예산에 맞춰 사양을 추천드립니다. "
             "영문판·국영문 혼용 제작도 함께 진행됩니다."),
        ],
        "works": [(P + "g02.png", "브랜드 브로슈어 — GOURI"),
                  (P + "g11.png", "회사소개서 — IT·데이터 기업"),
                  (P + "g28.png", "기업 브로슈어 — 화학기업"),
                  (P + "g40.png", "브로슈어 · 폴더 — 기업 홍보")],
        "blocks": [
            ("회사소개서 제작", P + "pf_1780560047851_5ffb92e1.png",
             "회사의 첫인상을 만드는 자료입니다. 연혁을 나열하는 대신 읽는 사람이 궁금해할 순서로 재구성합니다.",
             ["스토리 구성 기획", "실적·연혁 시각화", "고급 용지·후가공", "영업·제출용 판형"]),
            ("기관 · 단체 브로슈어", F + "banner_Gukgwasu01.jpg",
             "기관의 사업과 성과를 신뢰감 있게 정리합니다. 국립과학수사연구원 등 공공기관 제작 경험을 바탕으로 합니다.",
             ["사업 소개 구조화", "데이터 인포그래픽", "기관 톤 편집 디자인", "대량 인쇄·납품"]),
            ("영문 · 국영문 브로슈어", P + "g29.png",
             "해외 파트너와 수출 상담용 영문 브로슈어를 제작합니다. 국문판과 같은 디자인으로 언어만 교체해 톤을 유지합니다.",
             ["영문·국영문 혼용", "언어별 레이아웃 조정", "해외 상담용 판형", "번역 원고 협의"]),
        ],
        "faq": [
            ("회사소개서와 브로슈어는 같은 건가요?",
             "회사소개서는 브로슈어의 대표적인 형태입니다. 영업 제출용인지, 전시 비치용인지 목적에 따라 판형과 분량 구성이 달라집니다."),
            ("페이지 구성은 어떻게 잡는 게 좋나요?",
             "표지—회사 개요—사업 영역—실적—비전—연락처의 기본 골격에서 목적에 맞게 조정합니다. 원고를 보내주시면 구성안을 먼저 제안드립니다."),
            ("고급스러운 느낌을 내려면 어떻게 하나요?",
             "용지 선택과 후가공이 좌우합니다. 무광 코팅, 부분 박, 형압 등을 실물 샘플로 보여드리고 예산에 맞는 조합을 추천드립니다."),
            ("영문판도 제작되나요?",
             "네. 국문판과 같은 디자인으로 영문판·국영문 혼용판을 함께 제작해 드립니다. (번역 원고는 협의)"),
            ("제작 기간은 얼마나 걸리나요?",
             "분량과 원고 상태에 따라 다르지만 보통 2~4주가량입니다. 제출 일정이 있다면 역산해 진행합니다."),
        ],
    },
    "poster": {
        "en": "Poster", "kw": "포스터 제작 디자인",
        "sub": ('한 장으로 시선을 잡는 포스터 제작.<br/>'
                '<span class="g">행사·전시·프로모션 포스터를 디자인부터 인쇄까지.</span>'),
        "intro": [
            ("포스터 제작에 대하여",
             "포스터는 한 장 안에서 승부하는 홍보물입니다. 지나가는 사람의 시선을 3초 안에 잡아야 하므로, "
             "메시지 위계와 시각적 임팩트 설계가 무엇보다 중요합니다. 퍼스트디자인 인천지사는 이화여대 세미나 포스터 등 "
             "행사·전시·캠페인 포스터를 제작해온 노하우로 멀리서도 읽히는 포스터를 만듭니다."),
            ("포스터 준비 방법",
             "포스터 디자인은 부착 환경을 먼저 확인합니다. 실내 게시판인지 옥외인지, 부착 거리가 어느 정도인지에 따라 "
             "글자 크기와 대비 설계가 달라집니다. A1·A2·A3 등 규격과 수량, 부착 방식(게시·거치·현수)을 알려주시면 "
             "재질과 인쇄 방식까지 한 번에 안내드립니다."),
        ],
        "works": [(F + "banner_Ewha01.jpg", "세미나 포스터 — 이화여자대학교"),
                  (P + "g04.jpg", "캠페인 — KOMA"),
                  (P + "pf_1781576786008_68ef4688.jpg", "프로모션 — 레디큐"),
                  (P + "pf_1780561831138_2f3f236e.png", "홍보 전단 — Wemico")],
        "blocks": [
            ("행사 · 세미나 포스터", P + "pf_1780560349800_ca2e5f7c.png",
             "행사 정보를 위계에 맞춰 정리하고, 멀리서도 읽히는 대비와 크기로 설계합니다. 게시 환경까지 고려해 규격을 정합니다.",
             ["정보 위계 설계", "가독 거리 계산", "A1·A2·A3 규격", "게시판 부착 대응"]),
            ("홍보 · 캠페인 포스터", P + "pf_1780560331761_d8ccf30c.png",
             "브랜드 캠페인과 프로모션을 한 장에 담습니다. 시선을 잡는 키비주얼과 핵심 메시지에 집중합니다.",
             ["키비주얼 제작", "핵심 메시지 카피", "SNS 겸용 규격", "시리즈 전개"]),
        ],
        "faq": [
            ("포스터 규격은 어떤 걸 선택해야 하나요?",
             "실내 게시판은 A2·A3, 행사장·옥외는 A1 이상을 주로 씁니다. 부착 위치와 거리(가독 거리)를 알려주시면 규격과 글자 크기를 추천드립니다."),
            ("행사 포스터인데 일정이 촉박해요.",
             "포스터는 단면 1장 구조라 다른 인쇄물보다 일정 압축이 쉽습니다. 행사일 기준으로 최대한 맞춰 드리니 먼저 문의해 주세요."),
            ("소량만 인쇄할 수도 있나요?",
             "네. 디지털 인쇄로 몇 장 단위 소량도 제작됩니다. 대량 배포·부착용은 옵셋 인쇄로 단가를 낮춰 드립니다."),
            ("옥외 부착용은 재질이 다른가요?",
             "네. 비·햇빛에 강한 유포지나 합성지, 코팅 옵션을 사용합니다. 부착 환경을 알려주시면 맞는 재질을 안내드립니다."),
            ("시안은 몇 개 받아볼 수 있나요?",
             "방향이 다른 시안을 복수로 제안드리고, 선택안을 피드백으로 다듬습니다. 시안이 모두 아쉬우면 방향을 다시 잡아 드립니다."),
        ],
    },
}

# 히어로 아래 포폴 롤링 마퀴 (svc-* 페이지와 동일 — service.css .svc-roll 재사용)
ROLL = {
    "catalog": [P + "g17.png", F + "banner_Gukgwasu01.jpg", P + "g20.png", F + "banner_kb01.jpg",
                P + "pf_1781577049020_80075cf8.png", F + "banner_samsung01.jpg", P + "g29.png",
                P + "g02.png", P + "g11.png", P + "g28.png"],
    "leaflet": [F + "banner_mirae01.jpg", P + "pf_1780562846536_f1710b84.png", P + "g26.png",
                F + "banner_hitejinro01.jpg", P + "pf_1780562860378_28805540.png", P + "g34.png",
                P + "pf_1781576837581_2c038044.jpg", P + "g08.png"],
    "pamphlet": [P + "pf_1781576961440_d52ed960.png", P + "pf_1780562838633_700b8156.png",
                 P + "pf_1780561866143_5889af83.png", P + "pf_1781229209415_5f2c2500.jpg",
                 P + "pf_1780561954454_225acbab.png", P + "g38.png", P + "g08.png"],
    "brochure": [P + "g02.png", F + "banner_Gukgwasu01.jpg", P + "g11.png", F + "banner_samsung01.jpg",
                 P + "g28.png", P + "pf_1780560047851_5ffb92e1.png", P + "g40.png", P + "g29.png"],
    "poster": [F + "banner_Ewha01.jpg", P + "g04.jpg", P + "pf_1781576786008_68ef4688.jpg",
               P + "pf_1780560349800_ca2e5f7c.png", P + "pf_1780561831138_2f3f236e.png",
               P + "pf_1780560331761_d8ccf30c.png"],
}

# 진행 과정(인쇄 공통 5단계 — _services PROC["print"]와 동일 카피)
PROC = [("문의 접수", "제작물 종류와 일정,<br>필요한 내용을 확인합니다."),
        ("상담 · 견적", "프로젝트 범위와 사양을 정리하고<br>견적과 일정을 안내드립니다."),
        ("기획 · 디자인", "자료를 검토한 뒤 브랜드에 맞는<br>방향으로 시안을 제작합니다."),
        ("수정 · 검수", "전달주신 의견을 반영하고<br>최종 제작 전 결과물을 검수합니다."),
        ("인쇄 · 납품", "자체 인쇄소에서 인쇄·후가공 뒤<br>완성된 결과물을 납품합니다.")]

# ---------- CSS ----------
CSS = """/* subsvc.css — 인쇄 하위 서비스 전용 페이지(카탈로그/리플렛/팜플렛/브로슈어/포스터) */
.ss-sec{max-width:1248px;margin:0 auto;padding:72px 24px 20px}
.ss-sec .section-tag{font-size:12.5px;letter-spacing:.25em;font-weight:700;color:#0C9384;margin:0 0 12px}
.ss-t{font-size:clamp(27px,3.6vw,40px);font-weight:800;letter-spacing:-.03em;color:#111;margin:0 0 26px}
/* 소개 글: 좌 번호+제목 / 우 본문 가로 스플릿, 상하 스택 (haoc 2열 병렬과 다른 레이아웃) */
.ss-item{display:grid;grid-template-columns:380px 1fr;gap:24px 56px;padding:38px 0;border-top:1px solid #e6eceb}
.ss-item:first-of-type{border-top:2px solid #111}
.ss-no{display:block;font-family:'Montserrat','Pretendard',sans-serif;font-size:14px;font-weight:800;color:#0C9384;letter-spacing:.1em;margin-bottom:10px}
.ss-item h3{font-size:23px;font-weight:800;letter-spacing:-0.02em;color:#111;line-height:1.4;margin:0;word-break:keep-all}
.ss-item p{font-size:16.5px;color:#555;line-height:1.85;margin:0;word-break:keep-all}
/* 작업 사례 — 정해진 레이아웃: 2열 균일 카드, 전부 3:2 고정(가로형), 크기·정렬 통일 */
.ss-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:40px;margin-top:8px}
.ss-grid figure{margin:0}
.ss-grid img{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:16px;display:block;box-shadow:0 26px 54px -32px rgba(10,52,46,.4)}
.ss-grid figcaption{font-size:15.5px;font-weight:600;color:#333;margin-top:16px;word-break:keep-all}
.ss-more{display:inline-flex;align-items:center;gap:8px;margin-top:44px;font-size:15.5px;font-weight:700;color:#0C9384;text-decoration:none}
.ss-more:hover{text-decoration:underline}
@media (max-width:1024px){
  .ss-item{grid-template-columns:1fr;gap:14px}
}
@media (max-width:767px){
  .ss-sec{padding:48px 24px 10px}
  .ss-item h3{font-size:19px}
  .ss-item p{font-size:15px}
  .ss-grid{grid-template-columns:1fr;gap:28px}
}
"""
(ROOT / "theme" / "css" / "pages" / "subsvc.css").write_text(CSS, encoding="utf-8")

# ---------- 크롬 추출 (svc-brand.html — hero2·네비 반영된 최신 상태.
#            ⚠️svc-print.html은 2026-07-22 폐지되어 소스로 못 씀) ----------
src = (ROOT / "svc-brand.html").read_text(encoding="utf-8")
m = re.search(r'^(.*?)<main class="site-main">.*?</main>(.*)$', src, re.S)
head_part, tail_part = m.group(1), m.group(2)
cta = re.search(r'<section class="cta-section">.*?</section>', src, re.S).group(0)

def build(key, d):
    en, kw = d["en"], d["kw"]
    # head: title·메타 교체
    head = re.sub(r'<title>.*?</title>', f'<title>{kw} | 퍼스트디자인 인천지사</title>', head_part, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  rf'\g<1>인천 {kw} 전문 — 기획부터 디자인·인쇄·납품까지 원스톱. 인천·부천·시흥 당일 대면 상담. 1600-9487\g<2>', head)
    if "subsvc.css" not in head:
        head = head.replace("</head>", '<link rel="stylesheet" href="theme/css/pages/subsvc.css">\n</head>', 1)
    # 히어로
    hero = ('<section class="hero2"><div class="hero2-wrap">'
            f'<h1 class="hero2-tit">{en}</h1>'
            f'<p class="hero2-sub">{d["sub"]}</p>'
            '</div></section>\n')
    # 포폴 롤링 마퀴 (트랙 2벌 복제 = CSS 무한 루프)
    imgs = ROLL.get(key) or []
    track = "".join(f'<img src="{p}" alt="{en} 작업물" loading="lazy">' for p in imgs) * 2
    roll = f'<section class="svc-roll"><div class="svc-roll-track">{track}</div></section>\n' if imgs else ""
    # 소개 글
    items = "".join(
        f'<div class="ss-item"><div><span class="ss-no">0{i}</span><h3>{t}</h3></div><p>{p}</p></div>'
        for i, (t, p) in enumerate(d["intro"], 1))
    intro = (f'<section class="ss-sec"><p class="section-tag">ABOUT</p>'
             f'<h2 class="ss-t">{kw.split(" 제작")[0]} 제작 안내</h2>{items}</section>\n')
    # 세부 서비스 — 지그재그 매거진 오버랩 (service.css .svcz/.zrow 재사용)
    zrows = ""
    for bi, (t, img, desc, chips) in enumerate(d.get("blocks", [])):
        rev = " zrow--rev" if bi % 2 == 1 else ""
        lis = "".join(f"<li>{c}</li>" for c in chips)
        zrows += (f'<article class="zrow{rev}">'
                  f'<div class="zrow-img"><img src="{img}" alt="{t}" loading="lazy"></div>'
                  f'<div class="zrow-card"><span class="zrow-no">{bi+1:02d}</span>'
                  f'<p class="zrow-cat">{en.upper()}</p>'
                  f'<h3>{t}</h3><p>{desc}</p><ul>{lis}</ul></div></article>\n')
    detail = (f'<section class="svcz"><div class="svcz-in">'
              f'<p class="section-tag">DETAIL</p>'
              f'<h2 class="svcz-t">{en} 세부 서비스</h2>'
              f'<p class="svcz-s">필요한 항목만 골라 의뢰하셔도 좋습니다.</p>'
              f'{zrows}</div></section>\n') if zrows else ""
    # 작업 사례
    figs = "".join(
        f'<figure><img src="{img}" alt="{cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>'
        for img, cap in d["works"])
    works = (f'<section class="ss-sec"><p class="section-tag">WORKS</p>'
             f'<h2 class="ss-t">{en.upper()} 작업 사례</h2>'
             f'<div class="ss-grid">{figs}</div>'
             '<a class="ss-more" href="portfolio.html">포트폴리오에서 더 보기 →</a></section>\n')
    # 진행 과정 (service.css .timeline 재사용)
    steps = "".join(
        f'<div class="tstep"><span class="tstep__no">0{i}</span><h3>{t}</h3><p>{p}</p></div>'
        for i, (t, p) in enumerate(PROC, 1))
    proc = ('<section class="svc-proc"><div class="svc-proc-inner">'
            '<p class="section-tag">PROCESS</p><h2 class="svc-proc-t">진행 과정</h2>'
            f'<div class="timeline" id="svcTimeline">'
            f'<div class="timeline__line"><i id="svcTimelineFill"></i></div>{steps}</div>'
            '</div></section>\n')
    js = ("<script>(function(){var tl=document.getElementById('svcTimeline'),"
          "fill=document.getElementById('svcTimelineFill');if(!tl||!fill)return;"
          "function clamp(v,a,b){return Math.max(a,Math.min(b,v))}var ticking=false;"
          "function upd(){ticking=false;var vh=window.innerHeight,tr=tl.getBoundingClientRect();"
          "var tp=clamp((vh*0.85-tr.top)/(tr.height+vh*0.3),0,1);fill.style.width=(tp*100)+'%';"
          "var steps=tl.querySelectorAll('.tstep');for(var i=0;i<steps.length;i++)"
          "steps[i].classList.toggle('is-on',tp>=(i+0.35)/steps.length);}"
          "function tick(){if(!ticking){ticking=true;requestAnimationFrame(upd)}}"
          "window.addEventListener('scroll',tick,{passive:true});"
          "window.addEventListener('resize',tick);upd();})();</script>")
    # FAQ (service.css .svc-faq 재사용)
    faqs = "".join(
        f'<details class="svc-faq-item"><summary>{q}</summary>'
        f'<div class="svc-faq-a"><p>{a}</p></div></details>'
        for q, a in d["faq"])
    faq = (f'<section class="svc-faq"><p class="section-tag">FAQ</p>'
           f'<h2 class="svc-faq-t">자주 묻는 질문</h2>'
           f'<p class="svc-faq-s">{kw.split(" 제작")[0]} 의뢰 전 가장 많이 받는 질문을 모았습니다.</p>'
           f'{faqs}</section>\n')
    main = f'<main class="site-main">\n{hero}{roll}{intro}{detail}{works}{proc}{faq}{cta}\n</main>{js}'
    page = head + main + tail_part
    (ROOT / f"{key}.html").write_text(page, encoding="utf-8")
    print("written", f"{key}.html")

for key, d in PAGES.items():
    build(key, d)
print("subsvc done:", len(PAGES), "pages")
