# -*- coding: utf-8 -*-
"""마케팅 카테고리 페이지: svc-mkt.html 생성 + 전 페이지 네비 삽입.
(2026-07-27 사용자: "인천 홈페이지에는 마케팅 카테고리도 있어야해"
 + "firstd.co.kr/shopinfo/marketing.html 이런 내용을 좀 담아야해")
콘텐츠 = 본사 퍼스트마케팅 상품 라인업 실측(firstd.co.kr/shopinfo/marketing*.html 상세이미지 판독):
브랜드 블로그/브랜드 인스타그램/네이버 준·최적배포/인스타 상위노출/퍼포먼스/숏폼/언론홍보 7종.
블록 이미지 = 본사 상세이미지 히어로 밴드 크롭(theme/assets/first/mkt/mkt-*.jpg, 960x600).
⚠️_services.py 재실행 금지(hero2·SNS버튼 등 후속 패치 롤백됨) — _subsvc.py 방식으로
현재 svc-brand.html에서 크롬 추출 → 단독 생성. 구성 = svc-* 카테고리 페이지와 동일
(hero2 밴드 + 포폴 롤링 + ss-sec 소개(subsvc.css) + svcz 지그재그 + 타임라인 + FAQ + CTA).
체인: mirror → overlay → subpages → about_hh → services → hero2 → subsvc → svcmkt"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
P = "theme/assets/first/pf/"
F = "theme/assets/first/"

KEY, EN, LABEL = "mkt", "Marketing", "마케팅 · 광고"
M = "theme/assets/first/mkt/"
TITLE = f"{LABEL} | 퍼스트디자인 인천지사"
DESC = ("인천 마케팅 대행 — 브랜드 블로그·인스타그램 운영, 네이버 준·최적배포, 인스타그램 상위노출, "
        "퍼포먼스 광고, 숏폼 콘텐츠, 언론홍보까지. 전담 디자이너·작가가 만들고 결과로 보고합니다. 1600-9487")
KEYWORDS = ("인천 마케팅 대행, 블로그 운영대행, 인스타그램 운영대행, 네이버 기자단 배포, "
            "인스타그램 상위노출, 퍼포먼스 마케팅, 숏폼 제작, 언론홍보")

SUB = ('광고가 아닌 콘텐츠로, 찾게 만드는 마케팅 대행.<br/>'
       '<span class="g">블로그·인스타그램·숏폼·언론홍보까지 한 팀이 운영합니다.</span>')

# 히어로 아래 포폴 롤링 (본사 마케팅 배너 크롭 + 콘텐츠 성격 자산 믹스)
ROLL = [M + "mkt-blog.jpg", P + "pf_1780560331761_d8ccf30c.png",
        M + "mkt-insta.jpg", P + "g04.jpg",
        M + "mkt-short.jpg", P + "pf_1780560349800_ca2e5f7c.png",
        M + "mkt-press.jpg", P + "pf_1781576786008_68ef4688.jpg"]

# 소개 글 2개 (subsvc.css .ss-item 재사용 — 본사 마케팅 페이지 핵심 카피 요약)
INTRO = [
    ("단순한 상위노출이 아닌, 콘텐츠 마케팅입니다",
     "고객은 솔직한 이야기에서 신뢰를 느끼고, 그 이야기를 찾기 위해 검색합니다. 무작정 노출보다 중요한 건 "
     "고객이 찾는 자리에 있는 것. 퍼스트디자인 인천지사는 퍼스트 마케팅팀과 한 팀으로, 광고가 아닌 "
     "콘텐츠로 브랜드의 설득력을 만듭니다. 검색광고를 대체하는 효과를 클릭당 비용 없이 얻을 수 있습니다."),
    ("전담 팀이 만들고, 숫자로 보고합니다",
     "1:1 전담 디자이너와 작가가 배정되어 원고·카드뉴스·영상 소재를 직접 만들고, 포스팅 URL·노출 순위·"
     "인사이트를 정리한 결과보고 시스템으로 성과를 투명하게 공유합니다. 변화하는 네이버·인스타그램 "
     "로직을 공부하고 테스트하는 것까지 저희의 일입니다."),
]

# 세부 서비스 7종 (제목, 이미지, 설명, 칩4) — 본사 상품 라인업 순서 그대로
BLOCKS = [
    ("브랜드 블로그", M + "mkt-blog.jpg",
     "단순한 글쓰기가 아닙니다. 브랜드의 방향성과 톤앤매너를 담아, 홈페이지를 대신할 수 있는 공식 블로그를 전반적으로 운영·관리합니다. 브랜드 인지도를 높이는 저비용 고효율의 운영대행 서비스입니다.",
     ["전담 디자이너 · 작가 배정", "키워드 원고 월 10건 발행", "카드뉴스 · 이미지 월 60개", "포스팅 · 노출순위 결과보고"]),
    ("브랜드 인스타그램", M + "mkt-insta.jpg",
     "비주얼 중심의 인스타그램은 브랜드 아이덴티티를 시각적으로 전달하고, 브랜드 가치를 효과적으로 확장하는 데 최적의 채널입니다. 피드 하나하나에 브랜드의 감도·분위기·메시지를 담아 운영합니다.",
     ["피드 포스팅 월 10건", "카드뉴스 월 20건 이상", "소통 · 품앗이 · DM 작업", "인사이트 결과보고"]),
    ("네이버 준·최적배포", M + "mkt-baepo.jpg",
     "광고는 넘기고, 콘텐츠엔 멈춥니다. 경쟁도가 강한 키워드는 최적화 기자단, 약한 키워드는 준최 기자단으로 — 광고가 아닌 콘텐츠로 상위노출되어 브랜드 신뢰를 높이고 많은 키워드에 동시 노출합니다.",
     ["최적화 기자단 배포", "준최 기자단 배포", "다수 키워드 동시 노출", "경쟁도 · 연관도 복합 분석"]),
    ("인스타그램 상위노출", M + "mkt-top.jpg",
     "이제는 검색도 인스타그램에서 시작됩니다. 해시태그 검색 시 브랜드의 비주얼 콘텐츠를 추천 탭 상단에 노출시켜, 상단의 콘텐츠가 브랜드의 첫인상이 되고 선택의 기준이 되게 만듭니다.",
     ["해시태그 추천탭 상단 노출", "리그램 · 포스팅 상위노출", "키워드별 노출 방법 선정", "계정 최적화 작업"]),
    ("퍼포먼스 마케팅", M + "mkt-perf.jpg",
     "네이버·구글 검색광고(SA)부터 정교한 타겟팅의 메타 광고(DA)까지, 마케팅 목표에 가장 적합한 매체와 소재를 전략적으로 분석하고 효율적인 광고 운영으로 성과를 극대화합니다.",
     ["네이버 · 구글 검색광고", "메타 광고 운영", "광고 소재 직접 제작", "성과 분석 리포트"]),
    ("숏폼 콘텐츠", M + "mkt-short.jpg",
     "브랜드를 기억시키는 가장 빠른 방법, 숏폼. 스튜디오·PD·기획자·마케터가 한 팀으로 기획부터 촬영·편집·알고리즘 확산까지 운영합니다. 조회수보다 중요한 건 결과 — 성과 중심으로 만들어 드립니다.",
     ["기획 · 촬영 · 편집 원스톱", "릴스 · 쇼츠 제작", "인플루언서 숏폼", "알고리즘 확산 운영"]),
    ("언론홍보", M + "mkt-press.jpg",
     "브랜드 런칭, 신제품 출시 등 기업의 PR 이슈를 주요 포털 뉴스 탭에 노출하는 마케팅입니다. 마케터와 전문 작가가 핵심 키워드를 전략적으로 배치한 보도자료를 제작해 신속하고 정확하게 송출합니다.",
     ["포털 뉴스 탭 노출", "보도자료 작성 · 송출", "분야별 매체사 제안", "언론사 데스크 직접 소통"]),
]

# 진행 과정 5단계 (_services PROC 톤 유지)
PROC = [("문의 접수", "업종과 목표, 현재 운영 중인<br>채널 상황을 확인합니다."),
        ("상담 · 견적", "필요한 채널과 범위를 정리하고<br>견적과 일정을 안내드립니다."),
        ("전략 · 기획", "키워드·타깃을 분석해 채널별<br>콘텐츠 방향을 설계합니다."),
        ("제작 · 운영", "전담 디자이너·작가가 소재를<br>만들고 발행·운영합니다."),
        ("결과 보고", "포스팅 URL·노출 순위·인사이트를<br>정리해 전략과 함께 전달합니다.")]

FAQ = [
    ("디자인 회사인데 마케팅도 직접 하나요?",
     "네. 퍼스트디자인은 마케팅 전담 조직(퍼스트마케팅)과 한 회사로 움직입니다. 원고·카드뉴스·영상 같은 소재를 자체 디자인·촬영팀이 직접 만들기 때문에, 소재를 외주로 돌리는 대행사보다 품질과 속도에서 유리합니다."),
    ("블로그·인스타그램 운영은 어떻게 진행되나요?",
     "1:1 전담 디자이너와 작가가 배정됩니다. 블로그는 키워드 원고 월 10건과 카드뉴스·이미지 월 60개, 인스타그램은 피드 포스팅 월 10건과 카드뉴스 월 20건 이상을 발행하고, 소통·품앗이·DM 작업까지 함께 운영합니다."),
    ("상위노출은 보장되나요?",
     "특정 키워드 1위를 무조건 보장하는 방식은 오히려 위험합니다. 저희는 경쟁도·연관도·노출 가능성을 복합적으로 고려해 최적화·준최 기자단을 운영하고, 많은 키워드에 동시 노출시키는 방식으로 실제 유입을 만듭니다."),
    ("성과는 어떻게 확인하나요?",
     "결과보고 시스템으로 투명하게 공유합니다. 전체 포스팅 URL, 상위노출 체크, 키워드·노출 분석(인스타그램은 계정 인사이트·도달률)을 정리해 드리고, 다음 달 전략과 피드백까지 함께 전달합니다."),
    ("인천이 아닌 다른 지역도 가능한가요?",
     "네, 온라인 마케팅 특성상 전국 어디든 진행됩니다. 다만 인천·부천·시흥 등 서부수도권은 촬영·대면 미팅 일정을 잡기 쉬워 더 밀착해서 운영해 드릴 수 있습니다."),
]

# ---------- 크롬 추출 (svc-brand.html — hero2·네비·SNS 플로팅 반영된 최신 상태) ----------
src = (ROOT / "svc-brand.html").read_text(encoding="utf-8")
m = re.search(r'^(.*?)<main class="site-main">.*?</main>(.*)$', src, re.S)
head, tail = m.group(1), m.group(2)
cta = re.search(r'<section class="cta-section">.*?</section>', src, re.S).group(0)

# head: 메타 전량 교체
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', head, flags=re.S)
head = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{DESC}\g<2>', head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf'\g<1>{TITLE}\g<2>', head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{DESC}\g<2>', head)
head = re.sub(r'(<meta name="keywords" content=")[^"]*(")', rf'\g<1>{KEYWORDS}\g<2>', head)
head = head.replace("https://incheondesign.co.kr/svc-brand.html",
                    f"https://incheondesign.co.kr/svc-{KEY}.html")
if "subsvc.css" not in head:  # ss-sec 소개 레이아웃용
    head = head.replace("</head>", '<link rel="stylesheet" href="theme/css/pages/subsvc.css">\n</head>', 1)
# 브랜딩 active 해제 (크롬 출처가 svc-brand라 자기 링크에 active가 붙어 있음)
head = head.replace('href="svc-brand.html" class="active"', 'href="svc-brand.html"')
tail = tail.replace('href="svc-brand.html" class="active"', 'href="svc-brand.html"')

# ---------- 본문 ----------
hero = ('<section class="hero2"><div class="hero2-wrap">'
        f'<h1 class="hero2-tit">{EN}</h1>'
        f'<p class="hero2-sub">{SUB}</p>'
        '</div></section>\n')

track = "".join(f'<img src="{p}" alt="{LABEL} 작업물" loading="lazy">' for p in ROLL) * 2
roll = f'<section class="svc-roll"><div class="svc-roll-track">{track}</div></section>\n'

intro_items = "".join(
    f'<div class="ss-item"><div><span class="ss-no">0{i}</span><h3>{t}</h3></div><p>{p}</p></div>'
    for i, (t, p) in enumerate(INTRO, 1))
intro = (f'<section class="ss-sec"><p class="section-tag">ABOUT</p>'
         f'<h2 class="ss-t">퍼스트의 마케팅은 다릅니다</h2>{intro_items}</section>\n')

zrows = ""
for bi, (t, img, desc, chips) in enumerate(BLOCKS):
    rev = " zrow--rev" if bi % 2 == 1 else ""
    lis = "".join(f"<li>{c}</li>" for c in chips)
    zrows += (f'<article class="zrow{rev}">'
              f'<div class="zrow-img"><img src="{img}" alt="{t}" loading="lazy"></div>'
              f'<div class="zrow-card"><span class="zrow-no">{bi+1:02d}</span>'
              f'<p class="zrow-cat">{EN.upper()}</p>'
              f'<h3>{t}</h3><p>{desc}</p><ul>{lis}</ul></div></article>\n')
detail = (f'<section class="svcz"><div class="svcz-in">'
          f'<p class="section-tag">DETAIL</p>'
          f'<h2 class="svcz-t">{LABEL} 세부 서비스</h2>'
          f'<p class="svcz-s">필요한 채널만 골라 의뢰하셔도 좋습니다.</p>'
          f'{zrows}</div></section>\n')

steps = "".join(
    f'<div class="tstep"><span class="tstep__no">{i:02d}</span><h3>{t}</h3><p>{p}</p></div>'
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

faqs = "".join(
    f'<details class="svc-faq-item"><summary>{q}</summary>'
    f'<div class="svc-faq-a"><p>{a}</p></div></details>'
    for q, a in FAQ)
faq = (f'<section class="svc-faq"><p class="section-tag">FAQ</p>'
       f'<h2 class="svc-faq-t">자주 묻는 질문</h2>'
       f'<p class="svc-faq-s">마케팅 의뢰 전 가장 많이 받는 질문을 모았습니다.</p>'
       f'{faqs}</section>\n')

main = f'<main class="site-main">\n{hero}{roll}{intro}{detail}{proc}{faq}{cta}\n</main>{js}'
page = head + main + tail
# 새 페이지 자신의 네비 링크는 active (아래 네비 패치에서 삽입될 링크를 미리 반영하려면
# 패치 후 처리 필요 → 일단 쓰고, 네비 패치 루프에 svc-mkt.html도 포함시켜 active 처리)
(ROOT / f"svc-{KEY}.html").write_text(page, encoding="utf-8")
print("written", f"svc-{KEY}.html")

# ---------- 전 페이지 네비 삽입 (촬영·스튜디오 뒤 = svc-dd/svc-mob 닫는 주석 직전) ----------
DESK = f'<a href="svc-{KEY}.html">{LABEL}</a>'
MOB = DESK
import glob
n = 0
for f in sorted(ROOT.glob("*.html")):
    t = f.read_text(encoding="utf-8")
    if "<!--/svc-dd-->" not in t:
        continue
    # 재실행 대비: 기존 마케팅 링크(active 유무 불문) 제거 후 재삽입
    t = re.sub(rf'<a href="svc-{KEY}\.html"[^>]*>{re.escape(LABEL)}</a>', "", t)
    on = ' class="active"' if f.name == f"svc-{KEY}.html" else ""
    link = f'<a href="svc-{KEY}.html"{on}>{LABEL}</a>'
    t = t.replace("<!--/svc-dd-->", link + "<!--/svc-dd-->")
    t = t.replace("<!--/svc-mob-->", link + "<!--/svc-mob-->")
    f.write_text(t, encoding="utf-8")
    n += 1
    print("nav patched", f.name)
print("nav done:", n, "pages")

# ---------- sitemap ----------
sm = ROOT / "sitemap.xml"
t = sm.read_text(encoding="utf-8")
if f"svc-{KEY}.html" not in t:
    entry_m = re.search(r'(<url>\s*<loc>https://incheondesign\.co\.kr/svc-studio\.html</loc>.*?</url>)', t, re.S)
    new_entry = entry_m.group(1).replace("svc-studio.html", f"svc-{KEY}.html")
    t = t.replace(entry_m.group(1), entry_m.group(1) + "\n" + new_entry)
    sm.write_text(t, encoding="utf-8")
    print("sitemap: svc-mkt added")
