# -*- coding: utf-8 -*-
"""포트폴리오·블로그 히어로 = 회사소개 sec_head 스타일 이식 (사용자 "히어로 이렇게 가자", 2026-07-22).
틸 글라스 밴드(우측 오프셋+좌하단 라운드+하단 화이트 페이드) + Montserrat 대형 타이틀 + 서브카피.
값은 about3.css(SCALE 0.7)와 동일. 재실행 가능(마커 교체).
체인: mirror → overlay → subpages → about_hh → services → hero2  ← ★subpages가 두 페이지를 리빌드하므로 반드시 마지막에."""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
PRIMARY = "#0C9384"

CSS = """@font-face{font-family:'montserrat';src:url('../../vendor/fonts/montserrat-700.woff2') format('woff2');font-weight:700;font-display:swap}
.hero2{position:relative;word-break:keep-all}
.hero2::before{content:'';display:block;width:100%;height:385px;background:linear-gradient(180deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.97) 94%),url('../../assets/hh/css_about_02_bg.jpg') no-repeat left center/cover;border-radius:0 0 0 154px;position:absolute;left:50%;transform:translateX(-525px);z-index:-1}
.hero2 .hero2-wrap{max-width:1400px;margin:0 auto;padding:0 24px}
.hero2 .hero2-tit{font-size:126px;font-weight:700;line-height:1.4;font-family:'montserrat',sans-serif;color:#111;padding-top:280px;margin:0}
.hero2 .hero2-sub{font-size:22.4px;font-weight:600;color:#111;line-height:1.7;margin:0}
.hero2 .hero2-sub .g{color:%PRIMARY%}
@media all and (max-width:1539px){.hero2::before{width:calc(100%% - 14px);height:315px;left:auto;right:0;transform:none}.hero2 .hero2-tit{padding-top:217px;font-size:105px}.hero2 .hero2-sub{font-size:18.2px;margin-top:11.2px}}
@media all and (max-width:1199px){.hero2::before{height:161px;border-radius:0 0 0 105px}.hero2 .hero2-tit{padding-top:94.5px;font-size:70px}}
@media all and (max-width:767px){.hero2::before{height:112px;border-radius:0 0 0 70px}.hero2 .hero2-tit{padding-top:82.6px;font-size:35px}.hero2 .hero2-sub{font-size:14px}}
/* 히어로 아래 콘텐츠 여백 축소 — 원래 페이지 자체 상단 패딩(pf 80/blog 96+48)이 히어로와 겹쳐 첫 화면에 콘텐츠가 안 걸림 */
.pf-page{padding-top:36px}
.pf-filters{margin-top:0}
.blog-list-con{padding-top:28px}
.blog-layout{margin-top:12px}
/* 서비스 페이지들도 hero2 체제(구 다크 그라디언트 svc-hero 대체, 히어로 바로 아래 = 포폴 롤링) */
.svc-page{padding-top:36px}
""".replace("%PRIMARY%", PRIMARY).replace("100%%", "100%")

(ROOT / "theme" / "css" / "pages" / "hero2.css").write_text(CSS, encoding="utf-8")

def hero_html(tit, sub_html):
    return ('<!--hero2--><section class="hero2"><div class="hero2-wrap">'
            f'<h1 class="hero2-tit">{tit}</h1>'
            f'<p class="hero2-sub">{sub_html}</p>'
            '</div></section><!--/hero2-->\n')

def patch(fname, anchor, hero, removals):
    p = ROOT / fname
    s = p.read_text(encoding="utf-8")
    # 히어로 삽입/교체 (마커 idempotent)
    if "<!--hero2-->" in s:
        s = re.sub(r'<!--hero2-->.*?<!--/hero2-->\n?', hero, s, flags=re.S)
    else:
        assert anchor in s, f"{fname}: anchor not found"
        s = s.replace(anchor, hero + anchor, 1)
    # 기존 타이틀 요소 제거 (없으면 no-op)
    for rx in removals:
        s = re.sub(rx, "", s, flags=re.S)
    # css 링크
    if "hero2.css" not in s:
        s = s.replace("</head>", '<link rel="stylesheet" href="theme/css/pages/hero2.css">\n</head>', 1)
    # 로드 시 첫 화면 안에 있는 리빌 요소 즉시 노출 (공용 옵저버 threshold 미달로 첫 카드가 안 보이는 문제)
    js = ('<!--hero2-js--><script>document.querySelectorAll(".fade-up,.fade-up-child").forEach(function(el){'
          'if(el.getBoundingClientRect().top<window.innerHeight)el.classList.add("visible");});</script><!--/hero2-js-->\n')
    if "<!--hero2-js-->" in s:
        s = re.sub(r'<!--hero2-js-->.*?<!--/hero2-js-->\n?', js, s, flags=re.S)
    else:
        s = s.replace("</body>", js + "</body>", 1)
    p.write_text(s, encoding="utf-8")
    print(fname, "OK")

patch("portfolio.html", '<section class="pf-page">',
      hero_html("Portfolio",
                '기업·관공서·교육기관과 함께한 실제 작업물입니다.<br/>'
                '<span class="g">카탈로그부터 로고까지, 퀄리티로 확인하세요.</span>'),
      [r'\s*<h1 class="pf-page-title">[^<]*</h1>'])

patch("column.html", '<section class="blog-list-con">',
      hero_html("Blog",
                '카탈로그·브로슈어·로고까지,<br/>'
                '<span class="g">제작 전에 알아두면 좋은 인사이트를 모았습니다.</span>'),
      [r'\s*<div class="blog-tit-box">.*?</div>',
       r'\s*<nav class="blog-breadcrumb">.*?</nav>'])

# ---------- 서비스 페이지 6종 (2026-07-22 사용자 "서비스 페이지들 다 정리하자 지금 느낌 그대로") ----------
patch("services.html", '<section class="svc-page">',
      hero_html("Services",
                '기획부터 디자인, 인쇄·촬영, 납품까지 —<br/>'
                '<span class="g">퍼스트디자인 인천지사의 5가지 서비스를 확인해 보세요.</span>'),
      [r'\s*<h1 class="svc-page-title">[^<]*</h1>',
       r'\s*<p class="svc-page-sub">.*?</p>'])

SVC_HERO = {
    "svc-brand": ("Branding",
                  '브랜드의 첫인상은 디자인에서 시작됩니다.<br/>'
                  '<span class="g">로고·CI·BI, 오래 쓰는 아이덴티티를 함께 설계합니다.</span>'),
    # svc-print는 페이지 폐지(2026-07-22) — 인쇄는 catalog/leaflet 등 하위 5페이지(_subsvc.py)만
    "svc-ppt": ("Presentation",
                '결과를 만드는 제안서 · 발표자료.<br/>'
                '<span class="g">흐름과 위계를 다시 설계해 설득력을 높입니다.</span>'),
    "svc-web": ("Web",
                '브랜드를 담는 홈페이지 · 쇼핑몰.<br/>'
                '<span class="g">고객이 머물고 행동하게 하는 웹 경험을 설계합니다.</span>'),
    "svc-studio": ("Studio",
                   '제품을 돋보이게 하는 촬영 스튜디오.<br/>'
                   '<span class="g">디자인을 아는 팀이 촬영해 바로 쓰기 좋은 결과물을 만듭니다.</span>'),
}
for key, (tit, sub) in SVC_HERO.items():
    patch(f"{key}.html", '<section class="svc-roll">',
          hero_html(tit, sub),
          [r'\s*<section class="svc-hero">.*?</section>'])
