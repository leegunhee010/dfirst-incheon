# -*- coding: utf-8 -*-
"""서비스 페이지 생성: services.html(개요) + svc-{brand,print,ppt,web,studio}.html(5종).
콘텐츠 = dfirst-busan-v2 서비스 페이지(원본 dfirst 카피)에서 추출 → 인천 오버레이.
크롬(헤더/푸터) = notice.html 재사용. 전 페이지 네비에 '서비스' 항목 삽입."""
import os, re, shutil, pathlib

ROOT = pathlib.Path(__file__).parent
HOME = pathlib.Path(os.path.expanduser("~"))
BUSAN = HOME / "dfirst-busan-v2"
ASSETS = HOME / "dfirst-new" / "assets"
SVC = ROOT / "theme" / "assets" / "first" / "svc"
SVC.mkdir(parents=True, exist_ok=True)

CATS = [
    ("brand", "브랜딩 · 로고", "BRANDING"),
    ("print", "인쇄 · 홍보물", "PRINT"),
    ("ppt", "PPT · 제안서", "PRESENTATION"),
    ("web", "홈페이지 · 웹", "WEB"),
    ("studio", "촬영 · 스튜디오", "STUDIO"),
]

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()

def incheonize(s):
    s = s.replace("부산·경남·울산 기업과 가장 가까운 거리에서", "인천·부천·시흥 등 서부수도권 기업과 가장 가까운 거리에서")
    s = s.replace("부산·경남·울산", "인천·서부수도권")
    s = s.replace("퍼스트디자인 부산지사", "퍼스트디자인 인천지사")
    s = s.replace("부산퍼스트디자인", "퍼스트디자인 인천지사")
    s = s.replace("부산", "인천")
    return s

def copy_img(src_attr):
    name = os.path.basename(src_attr)
    src = ASSETS / name
    if not src.exists():
        src = BUSAN / "assets" / name
    if not src.exists():
        return None
    dst = SVC / name
    if not dst.exists():
        shutil.copy(src, dst)
    return "theme/assets/first/svc/" + name

# 이미지 재매핑: 부산 v2 배치가 어긋나서(yummy BUSAN 간판 등) 콘텐츠에 맞게 지정
import glob as _glob
def pf_by_id(idpart):
    hits = _glob.glob(str(ROOT / "theme" / "assets" / "first" / "pf" / ("pf_" + idpart + "*")))
    return "theme/assets/first/pf/" + os.path.basename(hits[0]) if hits else None
PFDIR = "theme/assets/first/pf/"
FD = "theme/assets/first/"
# ★2026-07-22 사진 전면 재선별(사용자 "사진 싹 다 교체" → 기존 자산 재선별 승인):
#   콘택트시트로 실물 확인 후 카테고리 정합·중복 제거. 고량집 간판(카드+인트로 중복)·명함@인쇄·
#   독서기록장 중복·inote(실작업 불명) 퇴출, 검증된 banner_* 위주로 재배치.
INTRO_OVERRIDE = {
    "brand": pf_by_id("1780560604781"),      # WELLNESS KOREA 로고 시안
    "print": PFDIR + "g40.png",              # 폴더·브로슈어
    "ppt": pf_by_id("1781577049020"),        # 틸 커버 브로슈어
    "web": PFDIR + "g23.jpg",                # HD코퍼레이션 홈페이지
    "studio": pf_by_id("1780561005491"),     # 화장품 제품컷
}
BLOCK_OVERRIDE = {
    # 블록 제목 순서에 맞춰 배치(브랜드: 로고제작/CI/BI/캐릭터/네이밍/창업패키지)
    "brand": [pf_by_id("1780560617361"),     # 01 로고제작 — BIZPROS 로고
              pf_by_id("1781229227544"),     # 02 CI — 유리 로고 시공(사옥 적용)
              PFDIR + "g36.jpg",             # 03 BI — BOA 브랜드 명함
              pf_by_id("1780560592478"),     # 04 캐릭터 — 네이처셋 키즈(캐릭터형 로고)
              FD + "g21.jpg",                # 05 네이밍 — 그린 명함
              FD + "mainbanner0001.jpg"],    # 06 창업 패키지 — Black Loaf 제품 브랜딩
    # (인쇄: 카탈로그/브로슈어·회사소개/팜플렛·접지/팜플렛·리플렛/포스터/명함/전단)
    "print": [PFDIR + "g17.png",             # 01 카탈로그 — 제품 카탈로그
              FD + "banner_samsung01.jpg",   # 02 브로슈어·회사소개 — 삼성화재 브로슈어
              FD + "banner_mirae01.jpg",     # 03 팜플렛·접지 — 미래에셋 3단
              FD + "banner_hitejinro01.jpg", # 04 팜플렛·리플렛 — 하이트진로
              FD + "banner_Ewha01.jpg",      # 05 포스터 — 이화여대 포스터
              PFDIR + "g09.jpg",             # 06 명함 — MG 명함
              PFDIR + "g26.png"],            # 07 전단 — Wemico 3단
    "ppt": [PFDIR + "g29.png",               # 제약 브로슈어(카드의 g11과 중복 제거)
            pf_by_id("1780560047851"), PFDIR + "g28.png"],
    "web": [pf_by_id("1780560349800"),       # 세븐란스 상세페이지 세트
            pf_by_id("1780560331761"),       # 아이스크림 카드뉴스
            FD + "mainbanner0004.jpg"],
    "studio": [pf_by_id("1780560845032"), pf_by_id("1780560823003")],
}

# ---------- 0.4 카테고리별 포트폴리오 롤링 마퀴 (2026-07-22 사용자: 인트로 지우고 카테고리 포폴 롤링) ----------
# 소스 = portfolio.html 카테고리 풀에서 선별(yummy BUSAN·고량집 제외), about 스와이퍼 카드(420×284 r18) 룩.
_P = "theme/assets/first/pf/"
_F = "theme/assets/first/"
ROLL = {
    "brand": [_P + "pf_1780560577502_b8078642.png", _P + "pf_1780560617361_f7c12f45.jpg",
              _P + "pf_1780560592478_0b39f00f.png", _P + "pf_1780560604781_6df397f6.png",
              _P + "pf_1781229227544_c6b41c37.jpg", _P + "g36.jpg", _P + "g21.jpg", _P + "g09.jpg"],
    "print": [_F + "banner_Gukgwasu01.jpg", _P + "g02.png", _P + "g17.png", _F + "banner_kb01.jpg",
              _P + "g40.png", _F + "banner_Ewha01.jpg", _P + "g26.png", _F + "banner_mirae01.jpg",
              _P + "pf_1781229209415_5f2c2500.jpg", _P + "pf_1781576961440_d52ed960.png"],
    "ppt": [_P + "g11.png", _P + "pf_1781577049020_80075cf8.png", _P + "g28.png",
            _P + "g29.png", _P + "pf_1780560047851_5ffb92e1.png", _P + "g20.png",
            _P + "g02.png", _P + "pf_1780561017607_3e0d9891.jpg"],
    "web": [_P + "g23.jpg", _F + "mainbanner0004.jpg",
            _P + "pf_1780560349800_ca2e5f7c.png", _P + "pf_1780560331761_d8ccf30c.png"],
    "studio": [_P + "pf_1780563086805_c7213d22.jpg", _P + "pf_1780560845032_e681b9d1.jpg",
               _P + "pf_1780561005491_7deae254.png", _P + "pf_1780560823003_754972d9.jpg",
               _P + "pf_1781577126401_845fdfc5.jpg", _P + "pf_1780560831589_f9a32abf.jpg"],
}

# ---------- 0.45 진행 과정 (2026-07-22 사용자 "dfirst.co.kr 참고해서 프로세스" — 본사 catalog/leaflet.html
#             process 섹션 실측: eyebrow Process + '진행 과정' + 6단계 3열 뱃지 그리드. 카테고리별 변형) ----------
# ★디자인 = design.haoc.co.kr/catalog-brochure.html 진행 과정 섹션 1:1 미러(2026-07-22 사용자 "이거 따와",
#   markup/css/js 실측 이식, 하오 오렌지 #e83817→인천 틸 리컬러). 레퍼런스가 5단계라 5단계로 재편.
PROC = {
    "brand": [("문의 접수", "제작물 종류와 일정,<br>필요한 내용을 확인합니다."),
              ("상담 · 견적", "업종·타깃·원하는 느낌을 정리하고<br>견적과 일정을 안내드립니다."),
              ("시안 제작", "방향이 다른 로고 시안을 제안하고<br>피드백으로 다듬습니다."),
              ("확정 · 규정 정리", "확정안의 컬러·서체 규정과<br>적용 시안을 정리합니다."),
              ("원본 전달", "ai 원본과 인쇄·웹용 파일을<br>정리해 전달합니다.")],
    "print": [("문의 접수", "제작물 종류와 일정,<br>필요한 내용을 확인합니다."),
              ("상담 · 견적", "프로젝트 범위와 사양을 정리하고<br>견적과 일정을 안내드립니다."),
              ("기획 · 디자인", "자료를 검토한 뒤 브랜드에 맞는<br>방향으로 시안을 제작합니다."),
              ("수정 · 검수", "전달주신 의견을 반영하고<br>최종 제작 전 결과물을 검수합니다."),
              ("인쇄 · 납품", "자체 인쇄소에서 인쇄·후가공 뒤<br>완성된 결과물을 납품합니다.")],
    "ppt": [("문의 접수", "발표 목적과 일정,<br>원고 상태를 확인합니다."),
            ("상담 · 견적", "심사 기준과 분량을 정리하고<br>견적과 일정을 안내드립니다."),
            ("기획 · 디자인", "목차·스토리라인을 정리한 뒤<br>시안을 제작합니다."),
            ("수정 · 확정", "피드백을 반영하고 발표 일정에 맞춰<br>마감 수정까지 진행합니다."),
            ("파일 전달", "발표용·인쇄용 최종 파일을<br>정리해 전달합니다.")],
    "web": [("문의 접수", "제작 목적과 일정,<br>필요한 내용을 확인합니다."),
            ("상담 · 견적", "페이지 구성과 콘텐츠 준비 상태를<br>정리하고 견적을 안내드립니다."),
            ("디자인 · 제작", "시안 확정 후 PC·모바일<br>반응형으로 제작합니다."),
            ("검수 · 오픈", "기기별 화면을 함께 확인하고<br>오픈합니다."),
            ("오픈 후 관리", "초기 오류를 잡아드리고<br>운영 관리를 협의합니다.")],
    "studio": [("문의 접수", "촬영 품목과 일정,<br>필요한 내용을 확인합니다."),
               ("상담 · 견적", "컷 수와 연출 방향을 정리하고<br>견적과 일정을 안내드립니다."),
               ("촬영 진행", "스튜디오·출장 일정에 맞춰<br>기획한 컷 리스트대로 촬영합니다."),
               ("셀렉 · 보정", "컷을 골라 색보정·리터칭을<br>진행합니다."),
               ("파일 전달", "용도별 규격으로 정리해<br>고해상도로 전달합니다.")],
}

def proc_html(key):
    steps = PROC.get(key) or []
    if not steps:
        return ""
    items = "".join(
        f'<div class="tstep"><span class="tstep__no">{i:02d}</span><h3>{t}</h3><p>{p}</p></div>'
        for i, (t, p) in enumerate(steps, 1))
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
    return ('<section class="svc-proc"><div class="svc-proc-inner">'
            '<p class="section-tag">PROCESS</p><h2 class="svc-proc-t">진행 과정</h2>'
            f'<div class="timeline" id="svcTimeline">'
            f'<div class="timeline__line"><i id="svcTimelineFill"></i></div>{items}</div>'
            f'</div></section>{js}\n')

# ---------- 0.5 카테고리별 FAQ (2026-07-22 사용자 "각 서비스 페이지마다 FAQ") ----------
FAQ = {
    "brand": [
        ("로고 시안은 몇 개나 받아볼 수 있나요?",
         "방향이 서로 다른 시안을 복수로 제안드리고, 마음에 드는 방향을 골라 다듬어 갑니다. 시안이 모두 마음에 들지 않으면 컨셉을 다시 잡아 새로운 시안을 제작해 드립니다."),
        ("수정은 몇 회까지 가능한가요?",
         "선택한 시안의 컬러·서체·비례 조정 등 다듬는 작업은 횟수 제한을 두지 않습니다. 다만 컨셉 자체가 완전히 바뀌는 재시안 수준의 작업은 협의 후 진행됩니다."),
        ("완성되면 원본 파일도 주시나요?",
         "네. 최종 완료 시 ai 원본과 함께 인쇄용·웹용 파일(png/jpg/pdf)을 정리해 드립니다. 이후 명함·간판·패키지 등에 바로 활용하실 수 있습니다."),
        ("로고만 있으면 명함·간판도 이어서 제작되나요?",
         "네. 로고 규정에 맞춰 명함·봉투·간판·SNS 프로필까지 한 팀이 이어서 제작합니다. 창업 준비라면 처음부터 패키지로 진행하시는 편이 비용과 완성도 모두 유리합니다."),
        ("인천에서 직접 만나 상담할 수 있나요?",
         "네. 인천·부천·시흥 등 서부수도권은 필요한 날 바로 대면 미팅이 가능합니다. 전화 1600-9487 또는 상담 설문지로 편하게 요청해 주세요."),
    ],
    "print": [
        ("디자인이 마음에 들지 않으면 어떡하나요?",
         "전체 디자인에 들어가기 전 원고 초반부를 먼저 디자인해 초안으로 전달드립니다. 초안이 마음에 들지 않으시면 새로운 방향으로 다시 제작해 드리니 안심하고 시작하셔도 됩니다."),
        ("수정은 몇 회까지 가능한가요?",
         "텍스트 변경, 이미지 교체, 페이지 위치 변경, 오탈자 수정 등의 작업은 횟수 제한 없이 진행합니다. 원고가 완전히 바뀌어 새로운 시안을 만드는 수준의 작업만 별도 협의됩니다."),
        ("소량 인쇄도 가능한가요?",
         "네. 디지털 인쇄로 소량도 부담 없이 제작하실 수 있고, 수량이 많아지면 옵셋 인쇄로 단가를 낮춰 드립니다. 용도와 수량을 알려주시면 가장 유리한 방식을 추천드립니다."),
        ("일정이 급한데 맞출 수 있나요?",
         "자체 인쇄소에서 인쇄부터 후가공, 검수까지 한 흐름으로 진행하기 때문에 외주 대비 일정을 크게 줄일 수 있습니다. 행사일이 정해져 있다면 상담 시 미리 알려주세요."),
        ("종이나 후가공은 어떻게 정하나요?",
         "용도와 예산에 맞춰 용지·코팅·박·형압 등을 담당 디자이너가 추천드립니다. 대면 미팅 시 실물 샘플을 보면서 결정하실 수 있습니다."),
    ],
    "ppt": [
        ("원고가 정리되어 있지 않아도 되나요?",
         "네. 흩어진 자료와 말로 설명해 주신 내용만으로도 시작할 수 있습니다. 기획 단계에서 메시지 우선순위와 목차를 함께 정리한 뒤 디자인에 들어갑니다."),
        ("회사 템플릿만 제작할 수도 있나요?",
         "네. 표지·간지·본문 레이아웃과 색·서체 규정이 담긴 템플릿만 제작해 드릴 수 있습니다. 이후 내부에서 직접 작성하셔도 브랜드 톤이 유지됩니다."),
        ("발표 직전 수정도 가능한가요?",
         "발표 자료 특성상 마감 직전 수정이 잦다는 점을 알고 있습니다. 일정 협의 시 발표일을 기준으로 수정 가능한 기간을 함께 잡아 드립니다."),
        ("자료 보안이 걱정됩니다.",
         "제안서·IR 자료는 외부에 공개되지 않도록 관리하며, 요청하시면 비밀유지 협약(NDA) 후 진행합니다. 포트폴리오 공개도 사전 동의 없이는 하지 않습니다."),
        ("작업 기간은 얼마나 걸리나요?",
         "분량과 원고 상태에 따라 달라져 상담 시 정확한 일정을 안내드립니다. 심사·발표일이 정해져 있다면 역산해서 일정을 설계해 드립니다."),
    ],
    "web": [
        ("제작 기간은 얼마나 걸리나요?",
         "페이지 구성과 콘텐츠 준비 상태에 따라 달라집니다. 상담 시 구성안을 먼저 잡고 단계별 일정을 안내드리며, 오픈 목표일이 있다면 역산해 진행합니다."),
        ("모바일에서도 잘 보이나요?",
         "네. 모든 페이지를 PC·태블릿·모바일 반응형으로 제작합니다. 오픈 전 기기별 화면을 함께 확인하고 전달드립니다."),
        ("사진이나 문구가 없는데 가능한가요?",
         "네. 촬영팀과 편집 디자이너가 있어 사진 촬영부터 카피 정리까지 한 팀에서 해결됩니다. 홈페이지에 들어갈 콘텐츠 준비부터 함께 시작하셔도 됩니다."),
        ("오픈 이후 수정·관리는 어떻게 하나요?",
         "오픈 후 발견되는 오류는 기본으로 잡아드리고, 배너 교체·내용 수정 등 운영 단계의 유지관리는 범위를 협의해 진행합니다."),
        ("도메인과 호스팅은 어떻게 하나요?",
         "보유하신 도메인이 있으면 그대로 연결해 드리고, 없다면 취득부터 호스팅 세팅까지 안내드립니다. 소유권은 모두 고객사 명의로 정리해 드립니다."),
    ],
    "studio": [
        ("스튜디오는 어디에 있나요? 출장 촬영도 되나요?",
         "제품은 스튜디오에서, 공간·현장 컷은 출장으로 촬영합니다. 인천·부천·시흥 등 서부수도권은 일정 잡기가 수월하니 편하게 문의해 주세요."),
        ("보정은 포함인가요?",
         "네. 선택 컷에 대한 색보정·리터칭이 기본 포함됩니다. 상세페이지·홍보물에 바로 쓸 수 있는 수준으로 마무리해 드립니다."),
        ("결과물은 어떻게 받나요?",
         "보정 완료본을 고해상도 파일로 전달드리며, 용도(웹·인쇄)에 맞는 규격으로 정리해 드립니다. 원본(RAW)이 필요하시면 사전에 협의해 주세요."),
        ("촬영만 하고 디자인은 따로 해도 되나요?",
         "네, 촬영만 의뢰하셔도 됩니다. 다만 디자인을 아는 팀이 촬영 단계부터 지면 구성을 고려하기 때문에, 카탈로그·상세페이지까지 함께 진행하시면 결과물의 완성도가 높아집니다."),
        ("제품 수가 많으면 어떻게 진행되나요?",
         "품목 리스트를 받아 컷 수와 연출 방향을 먼저 정리한 뒤 일정을 나눠 촬영합니다. 수량이 많을수록 컷당 단가를 조정해 드립니다."),
    ],
}

def faq_html(key, label):
    qs = FAQ.get(key) or []
    if not qs:
        return ""
    items = "".join(
        f'<details class="svc-faq-item"><summary>{q}</summary>'
        f'<div class="svc-faq-a"><p>{a}</p></div></details>'
        for q, a in qs)
    return (f'<section class="svc-faq"><p class="section-tag">FAQ</p>'
            f'<h2 class="svc-faq-t">자주 묻는 질문</h2>'
            f'<p class="svc-faq-s">{label} 의뢰 전 가장 많이 받는 질문을 모았습니다.</p>'
            f'{items}</section>\n')

# ---------- 1. 콘텐츠 로드 ----------
# ⚠️부산 v2 폴더는 다른 인스턴스가 작업 중이라 마크업이 계속 바뀜 → 최초 성공 추출본을
# _services_data.json 캐시로 고정. 캐시 없으면 (a)기생성된 우리 svc-*.html에서 역추출,
# (b)그것도 없으면 busan v2 구버전 마크업 시도.
import json
CACHE = ROOT / "_services_data.json"
data = {}
if CACHE.exists():
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    print("services data: cache loaded")
else:
    for key, label, en in CATS:
        own = ROOT / f"svc-{key}.html"
        if not own.exists():
            raise SystemExit(f"캐시도 기존 svc-{key}.html도 없음 — 콘텐츠 소스 확보 필요")
        t = own.read_text(encoding="utf-8")
        hero_m = re.search(r'<h1>(.*?)</h1>\s*<p class="svc-hero-lead">(.*?)</p>', t, re.S)
        intro_m = re.search(r'<section class="svc-intro">\s*<div>\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>\s*'
                            r'<div class="svc-feat">(.*?)</div>\s*</div>\s*'
                            r'<div class="svc-intro-img"><img src="([^"]+)"', t, re.S)
        blocks = []
        for bm in re.finditer(r'<div class="svc-block"><div class="svc-block-img"'
                              r'(?:\s+style="background-image:url\(\'([^\']+)\'\)")?></div>'
                              r'<div class="svc-block-body"><div class="svc-block-no">(\d+)</div>'
                              r'<h3>(.*?)</h3><p>(.*?)</p><ul>(.*?)</ul>', t, re.S):
            img, no, title, desc, ul = bm.groups()
            items = [i.strip() for i in re.findall(r"<li>(.*?)</li>", ul, re.S)]
            blocks.append({"img": img, "no": no, "title": title.strip(),
                           "desc": desc.strip(), "items": items})
        data[key] = {
            "label": label, "en": en,
            "hero_title": hero_m.group(1).strip(),
            "hero_lead": hero_m.group(2).strip(),
            "intro_title": intro_m.group(1).strip(),
            "intro_p": intro_m.group(2).strip(),
            "intro_feats": [f.strip() for f in re.findall(r"<span>(.*?)</span>", intro_m.group(3), re.S)],
            "intro_img": intro_m.group(4),
            "blocks": blocks,
        }
        print(key, "blocks:", len(blocks), "(기생성 페이지에서 역추출)")
    CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("services data: cache saved →", CACHE.name)

# ---------- 2. service.css ----------
css = """/* 서비스 페이지 — 포에디트 톤 + 인천 틸 */
.svc-page{max-width:1200px;margin:0 auto;padding:80px 24px 40px}
.svc-page-title{font-size:44px;font-weight:800;letter-spacing:-0.03em;color:#111;margin:0 0 12px}
.svc-page-sub{font-size:18px;color:#767676;margin:0 0 56px;line-height:1.6}
/* 개요 카드 */
.svc-cards{display:grid;grid-template-columns:repeat(2,1fr);gap:28px;margin-bottom:40px}
.svc-cards .svc-card:first-child{grid-column:1/-1}
.svc-card{display:flex;flex-direction:column;background:#fff;border:1px solid #ececec;border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;transition:box-shadow .25s,transform .25s}
.svc-card:hover{box-shadow:0 14px 36px rgba(12,147,132,.16);transform:translateY(-4px)}
.svc-card-img{height:240px;background-size:cover;background-position:center}
.svc-card:first-child .svc-card-img{height:300px}
.svc-card-body{padding:26px 28px 30px}
.svc-card-en{font-size:12px;font-weight:700;letter-spacing:.14em;color:#0C9384;margin:0 0 8px}
.svc-card-t{font-size:24px;font-weight:800;letter-spacing:-0.02em;color:#111;margin:0 0 10px}
.svc-card-d{font-size:15px;color:#767676;line-height:1.65;margin:0 0 16px}
.svc-card-tags{display:flex;flex-wrap:wrap;gap:8px}
.svc-card-tags span{font-size:13px;font-weight:600;color:#0A7A6E;background:#e7f4f2;border-radius:999px;padding:6px 12px}
/* 상세: 히어로 */
.svc-hero{background:linear-gradient(105deg,#0B2E2A 0%,#0C9384 70%,#12b3a0 100%);color:#fff;padding:110px 24px 90px}
.svc-hero-inner{max-width:1200px;margin:0 auto}
.svc-hero-cat{display:inline-block;font-size:13px;font-weight:700;letter-spacing:.16em;background:rgba(255,255,255,.14);border-radius:999px;padding:8px 16px;margin-bottom:22px}
.svc-hero h1{font-size:46px;font-weight:800;letter-spacing:-0.03em;line-height:1.25;margin:0 0 18px}
.svc-hero-lead{font-size:18px;line-height:1.7;color:rgba(255,255,255,.82);max-width:720px;margin:0}
.svc-hero-bc{margin-top:34px;font-size:14px;color:rgba(255,255,255,.65)}
.svc-hero-bc a{color:#fff;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.4)}
/* 상세: 인트로 스플릿 */
.svc-intro{display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center;max-width:1200px;margin:0 auto;padding:90px 24px}
.svc-intro h2{font-size:32px;font-weight:800;letter-spacing:-0.02em;color:#111;line-height:1.4;margin:0 0 14px}
.svc-intro p{font-size:17px;color:#767676;line-height:1.7;margin:0 0 24px}
.svc-feat{display:flex;flex-direction:column;gap:10px}
.svc-feat span{position:relative;padding-left:26px;font-size:15px;color:#333;line-height:1.5}
.svc-feat span::before{content:"";position:absolute;left:0;top:4px;width:16px;height:16px;border-radius:50%;background:#0C9384 url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="4"><polyline points="20 6 9 17 4 12"/></svg>') center/10px no-repeat}
.svc-intro-img img{width:100%;border-radius:14px;display:block}
/* 상세: 세부 서비스 블록 */
.svc-detail{background:#f2f7f6;padding:90px 24px}
.svc-detail-inner{max-width:1200px;margin:0 auto}
.svc-detail-ey{font-size:13px;font-weight:800;letter-spacing:.18em;color:#0C9384;margin:0 0 10px}
.svc-detail-t{font-size:34px;font-weight:800;letter-spacing:-0.02em;color:#111;margin:0 0 8px}
.svc-detail-s{font-size:16px;color:#767676;margin:0 0 46px}
.svc-blocks{display:flex;flex-direction:column;gap:28px}
.svc-block{display:grid;grid-template-columns:380px 1fr;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e6eceb}
.svc-block-img{background-size:cover;background-position:center;min-height:260px}
.svc-block-body{padding:34px 38px}
.svc-block-no{font-size:14px;font-weight:800;color:#0C9384;letter-spacing:.1em;margin-bottom:8px}
.svc-block-body h3{font-size:22px;font-weight:800;letter-spacing:-0.02em;color:#111;margin:0 0 10px}
.svc-block-body>p{font-size:15px;color:#767676;line-height:1.65;margin:0 0 16px}
.svc-block-body ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:8px 20px}
.svc-block-body li{position:relative;padding-left:20px;font-size:14px;color:#444;line-height:1.5}
.svc-block-body li::before{content:"";position:absolute;left:0;top:7px;width:7px;height:7px;border-radius:50%;background:#0C9384}
@media (max-width:1024px){
  .svc-cards{grid-template-columns:1fr}
  .svc-intro{grid-template-columns:1fr;gap:32px;padding:60px 24px}
  .svc-block{grid-template-columns:1fr}
  .svc-block-img{min-height:220px}
  .svc-hero h1{font-size:34px}
  .svc-page-title{font-size:34px}
  .svc-block-body ul{grid-template-columns:1fr}
}

/* 포트폴리오 롤링 마퀴 (about 스와이퍼 카드 룩, CSS 무한루프 — 트랙 2벌 복제 + -50% 이동) */
.svc-roll{overflow:hidden;padding:34px 0 6px}
.svc-roll-track{display:flex;width:max-content;animation:svcRoll 38s linear infinite}
.svc-roll-track img{width:420px;height:284px;object-fit:cover;border-radius:18px;flex:none;margin-right:24px;display:block}
.svc-roll:hover .svc-roll-track{animation-play-state:paused}
@keyframes svcRoll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (max-width:767px){.svc-roll-track img{width:260px;height:176px;border-radius:12px;margin-right:14px}}

/* 세부 서비스 = 지그재그 매거진 오버랩 (자체 레이아웃):
   큰 사진 + 반대편에서 겹쳐 올라오는 화이트 카드 + 아웃라인 고스트 넘버 */
.svcz{background:#fff;padding:96px 24px 60px}
.svcz-in{max-width:1248px;margin:0 auto}
.svcz-in>.section-tag{font-size:12.5px;letter-spacing:.25em;font-weight:700;color:#0C9384;margin:0 0 12px}
.svcz-t{font-size:clamp(27px,3.6vw,40px);font-weight:800;letter-spacing:-.03em;color:#111;margin:0 0 8px}
.svcz-s{font-size:16px;color:#767676;margin:0}
.zrow{display:grid;grid-template-columns:7fr 5fr;align-items:center;margin-top:76px;position:relative}
.zrow-img{grid-area:1/1/2/2;position:relative;border-radius:20px;overflow:hidden;aspect-ratio:16/10;background:#f2f5f4}
.zrow-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .6s cubic-bezier(.16,1,.3,1)}
.zrow:hover .zrow-img img{transform:scale(1.04)}
.zrow-card{grid-area:1/2/2/3;position:relative;z-index:1;margin-left:-96px;background:#fff;border-radius:18px;padding:40px 38px 34px;box-shadow:0 34px 70px -34px rgba(10,52,46,.35);border:1px solid #eef2f1}
.zrow-no{position:absolute;top:-52px;right:6px;font-family:'Montserrat','Pretendard',sans-serif;font-size:104px;font-weight:800;line-height:1;color:transparent;-webkit-text-stroke:1.5px rgba(12,147,132,.30);letter-spacing:-.02em;pointer-events:none}
.zrow-cat{font-size:12px;font-weight:800;letter-spacing:.2em;color:#0C9384;margin:0 0 12px}
.zrow-card h3{font-size:clamp(19px,1.8vw,23px);font-weight:800;letter-spacing:-.02em;color:#111;line-height:1.4;margin:0 0 12px;word-break:keep-all}
.zrow-card>p{font-size:15px;color:#666;line-height:1.75;margin:0 0 22px;word-break:keep-all}
.zrow-card ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.zrow-card li{font-size:13px;font-weight:600;color:#0A7A6E;background:#eef7f5;border-radius:999px;padding:7px 13px;word-break:keep-all}
.zrow--rev{grid-template-columns:5fr 7fr}
.zrow--rev .zrow-img{grid-area:1/2/2/3}
.zrow--rev .zrow-card{grid-area:1/1/2/2;margin-left:0;margin-right:-96px}
.zrow--rev .zrow-no{right:auto;left:6px}
@media (max-width:1024px){
  .zrow,.zrow--rev{grid-template-columns:1fr;margin-top:64px}
  .zrow-img,.zrow--rev .zrow-img{grid-area:auto}
  .zrow-card,.zrow--rev .zrow-card{grid-area:auto;margin:-56px 16px 0;padding:30px 26px}
  .zrow-no{font-size:76px;top:-40px}
}
@media (max-width:767px){
  .svcz{padding:60px 24px 30px}
  .zrow,.zrow--rev{margin-top:48px}
  .zrow-card,.zrow--rev .zrow-card{margin:-40px 10px 0}
}

/* 진행 과정 — design.haoc.co.kr/catalog-brochure.html 타임라인 1:1 미러 (오렌지→틸 리컬러)
   스크롤 진행바 + 끝점 글로우 펄스 + 단계 순차 점등(is-on) */
.svc-proc{background:#fff;--tl-accent:#0C9384;--tl-accent2:#2fd0bd;--tl-line:rgba(17,17,17,.12);--tl-muted:#767676;--tl-ease:cubic-bezier(.16,1,.3,1)}
.svc-proc-inner{max-width:1248px;margin:0 auto;padding:96px 24px 40px}  /* 콘텐츠 폭 1200 = svc-detail과 정렬 */
.svc-proc .section-tag{font-size:12.5px;letter-spacing:.25em;font-weight:700;color:var(--tl-accent);margin:0 0 12px}
.svc-proc-t{font-size:clamp(27px,3.6vw,40px);font-weight:800;letter-spacing:-.03em;color:#111;margin:0 0 26px}
.timeline{position:relative;display:grid;grid-template-columns:repeat(5,1fr);gap:24px;padding-top:56px;margin-top:40px}
.timeline__line{position:absolute;top:0;left:0;right:0;height:2px;background:var(--tl-line)}
.timeline__line i{position:relative;display:block;height:100%;width:0%;background:linear-gradient(90deg,var(--tl-accent2),var(--tl-accent));transition:width .25s linear;box-shadow:0 0 12px rgba(12,147,132,.5)}
.timeline__line i::after{content:"";position:absolute;right:-7px;top:50%;transform:translateY(-50%);width:14px;height:14px;border-radius:50%;background:var(--tl-accent);box-shadow:0 0 0 5px rgba(12,147,132,.18),0 0 18px rgba(12,147,132,.8);animation:svcTipPulse 1.4s ease-in-out infinite}
@keyframes svcTipPulse{0%,100%{box-shadow:0 0 0 5px rgba(12,147,132,.18),0 0 18px rgba(12,147,132,.8)}50%{box-shadow:0 0 0 11px rgba(12,147,132,.06),0 0 26px rgba(12,147,132,.9)}}
.tstep{position:relative;opacity:.28;transform:translateY(16px);transition:opacity .5s var(--tl-ease),transform .5s var(--tl-ease)}
.tstep::before{content:"";position:absolute;top:-61px;left:2px;width:12px;height:12px;border-radius:50%;background:#fff;border:2px solid var(--tl-line);transition:background .3s,border-color .3s,transform .3s var(--tl-ease)}
.tstep.is-on{opacity:1;transform:none}
.tstep.is-on::before{background:var(--tl-accent);border-color:var(--tl-accent);transform:scale(1.25);box-shadow:0 0 0 6px rgba(12,147,132,.15)}
.tstep__no{display:inline-flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:50%;margin-bottom:16px;font-size:18px;font-weight:800;color:var(--tl-muted);border:2px solid var(--tl-line);background:#fff;transition:color .3s,border-color .3s,background .3s}
.tstep.is-on .tstep__no{color:#fff;background:var(--tl-accent);border-color:var(--tl-accent);animation:svcNoPop .55s var(--tl-ease)}
@keyframes svcNoPop{0%{transform:scale(.6)}55%{transform:scale(1.18)}100%{transform:scale(1)}}
.tstep h3{font-size:19px;font-weight:700;color:#111;margin:0 0 8px}
.tstep p{color:var(--tl-muted);font-size:15px;line-height:1.65;margin:0}
@media (max-width:1000px){
  .svc-proc-inner{padding:64px 24px 16px}
  .timeline{grid-template-columns:repeat(2,1fr);gap:36px 24px;padding-top:10px}
  .timeline__line{display:none}
  .tstep::before{display:none}
}
@media (max-width:479px){.timeline{grid-template-columns:1fr}}

/* FAQ (details/summary 아코디언 — JS 불필요) */
.svc-faq{max-width:1248px;margin:0 auto;padding:72px 24px 110px}  /* 콘텐츠 폭 1200 = svc-detail과 정렬 */
.svc-faq .section-tag{font-size:12.5px;letter-spacing:.25em;font-weight:700;color:#0C9384;margin:0 0 12px}  /* PROCESS 헤더와 동일 */
.svc-faq-t{font-size:clamp(27px,3.6vw,40px);font-weight:800;letter-spacing:-.03em;color:#111;margin:0 0 10px}  /* svc-proc-t와 동일 */
.svc-faq-s{font-size:16px;color:#767676;margin:0 0 40px}
.svc-faq-item{border-bottom:1px solid #e6eceb}
.svc-faq-item summary{display:flex;align-items:baseline;gap:12px;cursor:pointer;font-size:18px;font-weight:700;color:#111;padding:22px 34px 22px 4px;list-style:none;position:relative}
.svc-faq-item summary::-webkit-details-marker{display:none}
.svc-faq-item summary::before{content:"Q.";color:#0C9384;font-weight:800;flex:none}
.svc-faq-item summary::after{content:"+";position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:22px;font-weight:400;color:#9aa7a5;transition:transform .2s ease}
.svc-faq-item[open] summary::after{transform:translateY(-50%) rotate(45deg);color:#0C9384}
.svc-faq-a{padding:0 4px 26px 34px;font-size:16px;color:#555;line-height:1.8}
.svc-faq-a p{margin:0 0 12px}
.svc-faq-a p:last-child{margin-bottom:0}
@media (max-width:767px){
  .svc-faq{padding-bottom:70px}
  .svc-faq-t{font-size:26px}
  .svc-faq-item summary{font-size:15.5px;padding:17px 30px 17px 2px}
  .svc-faq-a{font-size:14px;padding-left:26px}
}
"""
(ROOT / "theme" / "css" / "pages" / "service.css").write_text(css, encoding="utf-8")

# ---------- 3. 크롬 템플릿 (column.html 재사용 — notice는 삭제됨) ----------
chrome = (ROOT / "column.html").read_text(encoding="utf-8")
head = chrome[:chrome.find("<main")]
tail = chrome[chrome.find("</main>") + len("</main>"):]
# 페이지 CSS 교체(칼럼 → 서비스) — href만 정확히 치환(파일명 변경에 안전하게 정규식)
head = re.sub(r"href='theme/css/pages/column2?\.css'", "href='theme/css/pages/service.css'", head)
if "pages/service.css" not in head:  # 링크가 아예 없으면 주입
    head = head.replace("</head>", "<link rel='stylesheet' href='theme/css/pages/service.css' /></head>")
assert "pages/service.css" in head, "service.css 링크 주입 실패"
# 칼럼 크롬에 딸려온 블로그 필터 스크립트 제거
tail = re.sub(r"<script>\s*\(function \(\) \{\s*var items = document\.querySelectorAll\('\.blog-item'\).*?</script>\s*", "", tail, flags=re.S)
# 칼럼 active 해제
head = head.replace('<a href="column.html" class="active">블로그</a>', '<a href="column.html" class="">블로그</a>')
tail = tail.replace('<a href="column.html" class="active">블로그</a>', '<a href="column.html" class="">블로그</a>')

CTA = '''<section class="cta-section">
    <div class="cta2">
        <div class="cta2-left">
            <p class="cta2-eyebrow">FIRST DESIGN INCHEON</p>
            <p class="cta2-copy">상담 설문지 작성하고<strong>디자인 전문가에게 무료 상담 받기</strong></p>
        </div>
        <div class="cta2-right">
            <div class="cta2-phone"><span>전화 상담</span><b>1600-9487</b></div>
            <a href="contact.html" class="cta2-btn">상담 설문지 작성하기
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg></a>
        </div>
        <span class="cta2-ghost" aria-hidden="true">FIRST</span>
    </div>
</section>'''

def page(title, main_html):
    h = head
    h = re.sub(r"<title>.*?</title>", f"<title>{title} | 퍼스트디자인 인천지사</title>", h, flags=re.S)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + title + " | 퍼스트디자인 인천지사", h)
    return h + "<main class=\"site-main\">\n" + main_html + "\n</main>" + tail

# ---------- 4. services.html 개요 ----------
CARD_IMG = {"brand": pf_by_id("1780560577502"),  # 청춘애찬 로고(고량집 간판 퇴출)
            "print": "theme/assets/first/banner_Gukgwasu01.jpg",
            "ppt": "theme/assets/first/pf/g11.png",
            "web": "theme/assets/first/mainbanner0004.jpg",
            "studio": "theme/assets/first/mainbanner0002.jpg"}
cards = ""
for key, label, en in CATS:
    d = data[key]
    tags = "".join(f"<span>{b['title'].split('·')[0].strip()}</span>" for b in d["blocks"][:5])
    card_href = "catalog.html" if key == "print" else f"svc-{key}.html"  # print 페이지 폐지 → 대표 하위로
    cards += (f'<a class="svc-card" href="{card_href}">'
              f'<div class="svc-card-img" style="background-image:url(\'{CARD_IMG[key]}\')"></div>'
              f'<div class="svc-card-body"><p class="svc-card-en">{en}</p>'
              f'<h2 class="svc-card-t">{label}</h2>'
              f'<p class="svc-card-d">{d["hero_lead"]}</p>'
              f'<div class="svc-card-tags">{tags}</div></div></a>\n')
overview = f"""<section class="svc-page">
    <h1 class="svc-page-title">서비스</h1>
    <p class="svc-page-sub">기획부터 디자인, 인쇄·촬영, 납품까지 —<br>퍼스트디자인 인천지사가 제공하는 5가지 서비스를 확인해보세요.</p>
    <div class="svc-cards">
{cards}    </div>
</section>
{CTA}"""
(ROOT / "services.html").write_text(page("서비스", overview), encoding="utf-8")
print("written services.html")

# ---------- 5. 상세 (print는 페이지 폐지 — 하위 5종은 _subsvc.py) ----------
for key, label, en in CATS:
    if key == "print":
        continue
    d = data[key]
    # 캐시의 이미지 대신 OVERRIDE 강제 적용(캐시 전환 때 적용 코드가 빠져 정의만 있던 버그 복구)
    # (svc-intro 섹션은 2026-07-22 사용자 지시로 삭제 — INTRO_OVERRIDE는 미사용, 롤링 마퀴로 대체)
    ov = BLOCK_OVERRIDE.get(key) or []
    roll_imgs = ROLL.get(key) or []
    roll_track = "".join(f'<img src="{p}" alt="{label} 작업물" loading="lazy">' for p in roll_imgs) * 2
    roll = (f'<section class="svc-roll"><div class="svc-roll-track">{roll_track}</div></section>'
            if roll_imgs else "")
    blocks = ""
    # 네비 드롭다운 앵커용 블록 id (인쇄: 블록 순서 = 카탈로그/브로슈어/팜플렛/리플렛/포스터/명함/전단)
    BLOCK_IDS = {"print": ["catalog", "brochure", "pamphlet", "leaflet", "poster", "namecard", "flyer"]}
    ids = BLOCK_IDS.get(key, [])
    # 지그재그 매거진 오버랩 — 짝수행은 사진/카드 반전, 아웃라인 고스트 넘버
    for bi, b in enumerate(d["blocks"]):
        if bi < len(ov) and ov[bi]:
            b["img"] = ov[bi]
        chips = "".join(f"<li>{i}</li>" for i in b["items"][:4])
        img = (f'<div class="zrow-img"><img src="{b["img"]}" alt="{strip_tags(b["title"])}" loading="lazy"></div>'
               if b["img"] else "")
        bid = f' id="{ids[bi]}"' if bi < len(ids) else ""
        rev = " zrow--rev" if bi % 2 == 1 else ""
        blocks += (f'<article class="zrow{rev}"{bid}>{img}'
                   f'<div class="zrow-card"><span class="zrow-no">{b["no"]}</span>'
                   f'<p class="zrow-cat">{en}</p>'
                   f'<h3>{b["title"]}</h3><p>{b["desc"]}</p><ul>{chips}</ul></div></article>\n')
    main_html = f"""<section class="svc-hero">
    <div class="svc-hero-inner">
        <span class="svc-hero-cat">SERVICE · {en}</span>
        <h1>{d["hero_title"]}</h1>
        <p class="svc-hero-lead">{d["hero_lead"]}</p>
        <div class="svc-hero-bc"><a href="services.html">서비스</a> › {label}</div>
    </div>
</section>
{roll}
<section class="svcz">
    <div class="svcz-in">
        <p class="section-tag">DETAIL</p>
        <h2 class="svcz-t">{label} 세부 서비스</h2>
        <p class="svcz-s">필요한 항목만 골라 의뢰하셔도 좋습니다.</p>
{blocks}    </div>
</section>
{proc_html(key)}{faq_html(key, label)}{CTA}"""
    (ROOT / f"svc-{key}.html").write_text(page(label, main_html), encoding="utf-8")
    print("written", f"svc-{key}.html")

# ---------- 6. 전 페이지 네비: 1뎁스 플랫 + 인쇄만 드롭다운 (2026-07-22 사용자 확정안) ----------
# 회사소개 | 브랜딩·로고 제작 | 인쇄·홍보물 제작▾(카탈로그/리플렛/팜플렛/브로슈어/포스터, 이형표기 병기)
# | PPT·제안서 | 홈페이지·웹 | 촬영·스튜디오 | ... — 하위 전용 페이지 없어서 svc-print 블록 앵커로 연결.
NAV_LABEL = {"brand": "브랜딩 · 로고 제작", "print": "인쇄 · 홍보물 제작"}
# 2026-07-22 하위 전용 페이지 승격(_subsvc.py 생성) — 앵커 → 전용 페이지 링크
PRINT_SUB = [("catalog.html", "카탈로그 · 카다로그"),
             ("leaflet.html", "리플렛 · 리플릿"),
             ("pamphlet.html", "팜플렛 · 팜플릿"),
             ("brochure.html", "브로슈어 · 브로셔"),
             ("poster.html", "포스터")]
_CARET = ('<svg class="caret" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" '
          'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
          '<polyline points="6 9 12 15 18 9"/></svg>')

def _acls(on):
    return ' class="active"' if on else ""

# ★svc-print.html 폐지(2026-07-22 사용자 "print라는 페이지는 없어도 돼") — 인쇄는 하위 5페이지만.
#   네비의 '인쇄·홍보물 제작'은 이동 없는 드롭다운 부모(void 링크).
def dd_markup(active_key):
    out = []
    for k, label, _ in CATS:
        label = NAV_LABEL.get(k, label)
        if k == "print":
            subs = "".join(f'<a href="{href}">{txt}</a>' for href, txt in PRINT_SUB)
            out.append('<div class="nav-item-dd">'
                       f'<a href="javascript:void(0)"{_acls(active_key == k)}>{label} {_CARET}</a>'
                       f'<div class="nav-dd-menu"><div class="nav-dd-inner">{subs}</div></div>'
                       '</div>')
        else:
            out.append(f'<a href="svc-{k}.html"{_acls(active_key == k)}>{label}</a>')
    return "<!--svc-dd-->" + "".join(out) + "<!--/svc-dd-->"

def mob_markup(active_key):
    out = []
    for k, label, _ in CATS:
        label = NAV_LABEL.get(k, label)
        if k == "print":
            out.append(f'<a href="javascript:void(0)"{_acls(active_key == k)}>{label}</a>')
            subs = "".join(f'<a href="{href}">{txt}</a>' for href, txt in PRINT_SUB)
            out.append(f'<div class="mobile-sub">{subs}</div>')
        else:
            out.append(f'<a href="svc-{k}.html"{_acls(active_key == k)}>{label}</a>')
    return "<!--svc-mob-->" + "".join(out) + "<!--/svc-mob-->"

ALL = ["index.html", "about.html", "portfolio.html", "column.html",
       "column-design.html", "column-catalog.html", "column-logo.html", "column-print.html",
       "contact.html", "services.html"] + [f"svc-{k}.html" for k, _, _ in CATS if k != "print"]
for f in ALL:
    p = ROOT / f
    t = p.read_text(encoding="utf-8")
    # 이전 삽입물(단순 링크·구버전 드롭다운) 제거 후 새로 삽입
    t = re.sub(r"<!--svc-dd-->.*?<!--/svc-dd-->", "", t, flags=re.S)
    t = re.sub(r"<!--svc-mob-->.*?<!--/svc-mob-->", "", t, flags=re.S)
    t = re.sub(r'\s*<a href="services\.html" class="[^"]*">서비스</a>', "", t)
    active_key = f[4:-5] if f.startswith("svc-") else None
    # 회사소개를 맨 앞으로(사용자 2026-07-22): 서비스 5링크는 회사소개 '뒤'에 삽입
    t, _n1 = re.subn(r'(<nav class="nav-menu">.*?<a href="about\.html"[^>]*>회사소개</a>)',
                     lambda m: m.group(1) + "\n                    " + dd_markup(active_key), t, count=1, flags=re.S)
    t, _n2 = re.subn(r'(<nav class="mobile-menu-nav">.*?<a href="about\.html"[^>]*>회사소개</a>)',
                     lambda m: m.group(1) + "\n        " + mob_markup(active_key), t, count=1, flags=re.S)
    assert _n1 == 1 and _n2 == 1, f"{f}: 회사소개 앵커 삽입 실패 ({_n1},{_n2})"
    p.write_text(t, encoding="utf-8")
    print("nav dd patched", f)

# ---------- 7. 드롭다운 CSS (incheon.css에 1회 append) ----------
inc = ROOT / "theme" / "css" / "incheon.css"
css_dd = """
/* svc-dd: 서비스 드롭다운 */
.nav-item-dd{position:relative;display:flex;align-items:center;height:100%}
.nav-item-dd>a{display:inline-flex;align-items:center;gap:6px}
.nav-item-dd .caret{transition:transform .2s ease;margin-top:1px}
.nav-item-dd:hover .caret{transform:rotate(180deg)}
.nav-dd-menu{position:absolute;top:100%;left:50%;transform:translateX(-50%);padding-top:16px;display:none;z-index:1200}
.nav-item-dd:hover .nav-dd-menu{display:block}
.nav-dd-inner{background:#fff;border:1px solid #ececec;border-radius:12px;box-shadow:0 18px 44px rgba(17,17,17,.12);padding:10px;min-width:210px}
.nav-menu .nav-dd-inner a{display:block;height:auto;padding:11px 16px;font-size:15px;font-weight:500;color:#333;border-radius:8px;white-space:nowrap}
.nav-menu .nav-dd-inner a:hover{background:#e7f4f2;color:#0A7A6E}
.nav-menu .nav-dd-inner a::after{display:none}
.nav-menu .nav-dd-inner a.dd-all{font-weight:700;color:#0C9384;border-bottom:1px solid #f0f0f0;border-radius:8px 8px 0 0;margin-bottom:4px}
.mobile-sub{display:flex;flex-direction:column;padding:2px 0 6px 14px;border-left:2px solid #e7f4f2;margin:4px 0 8px 2px}
.mobile-menu-nav .mobile-sub a{font-size:15px;font-weight:500;color:#666;padding:7px 0;border-bottom:none}
"""
t = inc.read_text(encoding="utf-8")
if "svc-dd" not in t:
    inc.write_text(t + css_dd, encoding="utf-8")
    print("incheon.css: dd styles appended")

# ---------- 7.5 플랫 네비(8항목) 피팅 CSS ----------
css_flat = """
/* svc-flat: 서비스 1뎁스 플랫 네비 — 8항목 한 줄 피팅 (abs+left:50% 특성상 max-content 필수, 없으면 절반 폭에서 줄바꿈) */
.nav-menu{gap:26px;font-size:15.5px;width:max-content;white-space:nowrap}
.nav-menu a{white-space:nowrap}
@media (max-width:1366px){.nav-menu{gap:16px;font-size:14px}}
"""
t = inc.read_text(encoding="utf-8")
if "svc-flat" not in t:
    inc.write_text(t + css_flat, encoding="utf-8")
    print("incheon.css: flat nav styles appended")

# ---------- 7.6 인쇄 드롭다운 복원 + 앵커 오프셋 ----------
css_flat2 = """
/* svc-flat2: 인쇄 하위 드롭다운 + 앵커 랜딩 오프셋 */
.svc-block{scroll-margin-top:96px}
.nav-item-dd>a .caret{margin-top:1px}
@media (max-width:1366px){.nav-menu .nav-dd-inner a{font-size:14px;padding:10px 14px}}
"""
t = inc.read_text(encoding="utf-8")
if "svc-flat2" not in t:
    inc.write_text(t + css_flat2, encoding="utf-8")
    print("incheon.css: flat2 styles appended")
