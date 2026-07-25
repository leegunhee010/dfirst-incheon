# -*- coding: utf-8 -*-
"""회사소개 = hothaan.co.kr/content/about_new 디자인 이식.
_subpages.py가 만든 about.html의 <main>을 hothaan about_new 미러(퍼스트 오버레이)로 교체.
체인: mirror → overlay → subpages → about_hh → services"""
import os, re, pathlib, urllib.request

ROOT = pathlib.Path(__file__).parent
HOME = pathlib.Path(os.path.expanduser("~"))
# hothaan 미러 소스: 프로젝트 내 _src 사본 우선(임시폴더 스크래치는 유실될 수 있음)
SCRATCH = ROOT / "_src"
if not (SCRATCH / "hothaan-about.html").exists():
    SCRATCH = HOME / "AppData/Local/Temp/claude/C--Users----/54452de3-9fd5-4fdb-ab17-d592a917fbd9/scratchpad"
HH = ROOT / "theme" / "assets" / "hh"
HH.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PRIMARY = "#0C9384"

def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        print("FAIL", url, e)
        return False

# ---------- 1. about_new HTML 추출 (섹션 화이트리스트) ----------
src = (SCRATCH / "hothaan-about.html").read_text(encoding="utf-8", errors="ignore")
i0 = src.find('<div class="about_new"')
foot = src.find("<footer", i0)
region = src[i0:foot]
region = re.sub(r'<!--.*?-->', '', region, flags=re.S)   # 주석(비활성 sec_07~11 등) 제거 — 잘린 <!-- 로 CTA까지 삼키는 버그 방지
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="(?:sec )?(sec_\d+)"', region)]
KEEP = ["sec_02", "sec_03", "sec_04", "sec_05", "sec_12", "sec_06"]  # 히어로(sec_01)·We Use Tools(sec_13) 삭제, sec_08 원본 비활성
segs = {}
for idx, (pos, name) in enumerate(starts):
    end = starts[idx + 1][0] if idx + 1 < len(starts) else len(region)
    segs.setdefault(name, region[pos:end])

def balance(hh):
    d = hh.count("<div") - hh.count("</div>")
    if d > 0:
        hh += "</div>" * d
    elif d < 0:
        for _ in range(-d):
            hh = hh[:hh.rfind("</div>")]
    return hh

about = '<div class="about_new">\n' + "\n".join(balance(segs[k]) for k in KEEP if k in segs) + "\n</div>"

# ---------- 2. 콘텐츠 오버레이 ----------
R = [
    # sec_01 히어로
    ("가장 핫한 경험", "가장 가까운 디자인 파트너"),
    ('<span class="gra_01">크리에이티브</span>한', '<span class="gra_01">디자인부터 인쇄</span>까지'),
    ("풀스펙 에이전시", "풀스펙 디자인 컴퍼니"),
    ("클라이언트의 고객 중심 디자인을 기본으로\n", "클라이언트의 고객 중심 디자인을 기본으로 "),
    ("<strong>트렌디한 크리에이티브</strong>를 만들고", "<strong>이유 있는 크리에이티브</strong>를 만들고"),
    ("<strong>기업 및 브랜드에 핫한 경험을 제공하는 풀 스펙 에이전시 핫한</strong>입니다.",
     "<strong>기업과 관공서에 12년의 제작 경험을 전하는 풀스펙 디자인 회사 퍼스트디자인 인천지사</strong>입니다."),
    # sec_02
    ("핫한은 컨설팅부터 브랜딩, UIUX 디자인, 퍼블리싱, 개발까지",
     "퍼스트디자인은 기획부터 브랜딩, 편집 디자인, 인쇄·가공, 촬영까지"),
    ('<span class="gra_01">시작과 동시에 지속가능한 웹서비스 에이전시</span>입니다.',
     '<span class="gra_01">시작부터 납품까지 한 팀이 책임지는 디자인 회사</span>입니다.'),
    # sec_03 일하는 방식 (긴 문단을 먼저 치환해야 토큰 치환에 안 깨짐)
    ("우리는 유연한 근무를 위해서 8시부터 10시 사이의 자유로운 출근과 주 5일동안 70%는 재택, 30%는 출근으로 출퇴근 에너지낭비와 인간관계 스트레스,감정낭비를 없애고 효율적인 근무와 소통을 진행하여 즐겁게 업무를 진행하고 있습니다.",
     "우리는 파일과 전화로만 일하지 않습니다. 필요한 날 바로 만나 원고를 함께 정리하고, 시안 방향을 그 자리에서 맞춥니다. 본사 12년의 제작 시스템 그대로 — 초안을 먼저 확인하고 진행하기 때문에 방향이 틀어질 일이 없습니다."),
    ("HOT한 핫한의 업무환경", "퍼스트디자인이 일하는 방식"),
    ("8시부터 10시 사이의", "인천·부천·시흥 서부수도권"),
    ("자유로운 출근", "당일 대면 미팅"),
    ("주 5일동안", "본사 12년의"),
    ("70% 재택", "검증 프로세스"),
    ("핫한은 30대의 대표와 20-30대의 직원들이 모여있는 젊은 회사입니다.",
     "퍼스트디자인은 아트디렉터, 프로젝트 매니저, 편집·브랜딩 디자이너, 촬영 작가가 모인 회사입니다."),
    ("직급이 존재하지 않는 평등한 문화를 추구하여", "전문가 35명+가 프로젝트별 전담팀을 꾸려"),
    ("실력만 있으면 눈치 안보고 일 할 수 있는 핫한 회사", "처음부터 끝까지 한 팀이 책임지는 회사"),
    # sec_04
    ("집중해서 일하고 성과로 증명하는", "결과물 하나에도 이유가 있는"),
    ("핫한 문화", "퍼스트다운 문화"),
    # sec_05
    ("핫한은 클라이언트가 고객과 소통할 수 있도록", "퍼스트디자인은 클라이언트가 고객과 소통할 수 있도록"),
    ("컨설팅, 크리에이티브 분야에서 비즈니스를 함께합니다.", "기획, 크리에이티브 분야에서 비즈니스를 함께합니다."),
    ("핫한과의 여정은 매일 신비로운 가치를 발견하고", "퍼스트와의 여정에서 브랜드의 다음 단계를 발견하고"),
    # sec_06 crew — 우리 4팀 확정(2026-07-22): PLAN / DESIGN / PRINT / MKT
    # item_01 PM → PLAN
    ("PM TEAM", "PLAN TEAM"),
    ("웹기획, 홈페이지 기획 및 관리", "원고 정리와 콘텐츠 구성"),
    ("컨텐츠 기획 및 마케팅", "일정·견적·인쇄 사양 관리"),
    ("화면설계(story board)", "페이지 구성 설계"),
    # item_02 BX → DESIGN
    ("BX TEAM", "DESIGN TEAM"),
    ("크리에이티브 아이덴티티 브랜딩 디자인", "카탈로그부터 로고까지, 브랜드의 얼굴을 만드는 디자인"),
    ("상세페이지, SNS 컨텐츠 디자인", "카탈로그·브로슈어 디자인"),
    ("BX는 모든 디자인의 근본이다를 몸소 증명하는 팀", "디자인은 모든 결과물의 근본이다를 몸소 증명하는 팀"),
    ("못하는 게 없고 고고한 백조마냥 호수 위를 떠다니는 러블리 핫걸들",
     "못하는 게 없고, 백조처럼 우아하게 마감까지 해내는 디자이너들"),
    # item_03 UX → PRINT (기존 PRINT 콘텐츠 이동)
    ("UX TEAM", "PRINT TEAM"),
    ("사용자경험을 바탕으로 웹, 앱 등", "자체 인쇄소에서 인쇄부터 후가공, 검수,"),
    ("크리에이티브한 UI, UX Design", "납품까지 끝까지 책임지는 팀"),
    ("트렌디 UIUX", "옵셋 · 디지털 인쇄"),
    ("상상초월 UX", "후가공 (코팅 · 박 · 형압)"),
    ("디자인씽킹", "색 교정 · 검수 · 납품"),
    ("둥글둥글 성격도 너무 좋고, 배울점 많고, 디자인도 끝내주는!!", "잉크 냄새만 맡아도 상태를 아는 손끝,"),
    ("같이 있으면 즐거운 정말 좋은 사람들", "모니터와 인쇄물의 색 차이를 끝까지 잡아내는 장인들"),
    ("핫한 대표가 스카웃한 모두가 인정하는 일잘러 디자인 능력자 + 각종 툴능력자 + 뭐든지 퍼펙트하게 해냄",
     "마감 전날에도 흔들림 없는, 퍼스트의 든든한 최후의 보루"),
    # item_04 DEV → MKT (신규 카피)
    ("DEV TEAM", "MKT TEAM"),
    ("인터렉티브 웹 사이트 &amp; 웹 표준화와 프로젝트 완료 후 지속적인 유지까지",
     "촬영·콘텐츠부터 채널 운영까지, 만든 결과물을 성과로 알리는 팀"),
    ("인터렉티브 웹 사이트 & 웹 표준화와 프로젝트 완료 후 지속적인 유지까지",
     "촬영·콘텐츠부터 채널 운영까지, 만든 결과물을 성과로 알리는 팀"),
    ("프론트엔드", "제품 · 브랜드 촬영"),
    ("백엔드", "SNS · 블로그 콘텐츠"),
    ("퍼블리싱", "광고 · 채널 운영"),
    ("사이트 유지보수", "상세페이지 · 랜딩"),
    ("개발자 성향(?)이 정해져 있는건 아니지만 보편적인 개발자 분들의 성격과 달리 미친 친화력과 성격을 보유하신 보기 드문 풀스택 인재 인싸",
     "만드는 데서 멈추지 않고 알려지는 것까지 챙기는, 촬영부터 채널 운영까지 실행 속도가 다른 마케터들"),
    ("성격 세상 cool한 현실적인 조력자st 그녀는 진정한 능력자들",
     "트렌드는 제일 먼저 물어오고, 성과는 숫자로 증명하는 진정한 능력자들"),
]
def rrep(hh, a, b):
    # 공백 무시 매칭: 원본 마크업의 개행·들여쓰기를 \s+로 허용
    pat = r"\s+".join(re.escape(w) for w in a.split())
    new, n = re.subn(pat, lambda _m: b, hh)
    if n == 0:
        print("(!) 치환 실패:", a[:40])
    return new
for a, b in R:
    about = rrep(about, a, b)
about = about.replace("핫한", "퍼스트")  # 잔여 일괄
about = about.replace("퍼스트은", "퍼스트디자인은")

# ---------- 2.5 sec_03 스플릿 2개 → 1개 병합 (사용자 "하나로 합치자") ----------
# item_02(음식 사진) 통삭제, 전문가 35명 카피는 item_01 둘째 문단으로 흡수 (R 치환 이후에 실행해야 경고 안 뜸)
about, _n = re.subn(
    r'\s*<div class="item item_02">.*?</div>\s*<div class="img_wrap"[^>]*>.*?</div>\s*</div>',
    "", about, count=1, flags=re.S)
assert _n == 1, "sec_03 item_02 제거 실패"
_i = about.find("방향이 틀어질 일이 없습니다.")
assert _i != -1, "sec_03 item_01 문단 앵커 실패"
_j = about.find("</p>", _i) + len("</p>")
about = (about[:_j] + '\n<p>아트디렉터, 프로젝트 매니저, 편집·브랜딩 디자이너, 촬영 작가 — '
         '전문가 35명+가 프로젝트별 전담팀을 꾸려 <span class="gra_01">처음부터 끝까지 한 팀이 책임집니다</span>.</p>'
         + about[_j:])

# ---------- 3. 이미지 로컬라이즈 ----------
# 우리 작업물로 교체할 것들
OUR12 = ["theme/assets/first/banner_Gukgwasu01.jpg", "theme/assets/first/g29.png",
         "theme/assets/first/banner_kb01.jpg", "theme/assets/first/g02.png",
         "theme/assets/first/banner_Ewha01.jpg", "theme/assets/first/g17.png",
         "theme/assets/first/mainbanner0001.jpg", "theme/assets/first/g04.jpg",
         "theme/assets/first/banner_hitejinro01.jpg", "theme/assets/first/g26.png",
         "theme/assets/first/banner_mirae01.jpg", "theme/assets/first/g11.png"]
for n in range(1, 13):
    about = about.replace(f"https://hothaan.co.kr/html/img/new_01/about_02_{n:02d}.jpg", OUR12[n - 1])
SWAP = {
    "about_03_01.jpg": "theme/assets/first/office.jpg",
    "about_03_02.jpg": "theme/assets/first/pf/pf_1780560823003_754972d9.jpg",
    "about_04_01.png": "theme/assets/first/mainbanner0002.jpg",
    "about_12_01.png": "theme/assets/first/ourclients.png",
    "about_12_01_mb.png": "theme/assets/first/ourclients.png",
}
for k, v in SWAP.items():
    about = about.replace(f"https://hothaan.co.kr/html/img/new_01/{k}", v)

# 팀 아바타: 핫한 마스코트(오리 = 핫한 고유 IP) → 우리 워크스페이스 사진 4종(위치 순서대로 교체)
from PIL import Image as _Im
STUDIO = HOME / "dfirst-new" / "assets"
TEAM_SRC = [STUDIO / "studio" / "m013.jpg", STUDIO / "photocat" / "detail.jpg",
            STUDIO / "studio" / "m019.jpg", STUDIO / "photocat" / "space.jpg"]
team_imgs = []
for idx, sp in enumerate(TEAM_SRC):
    dst = ROOT / "theme" / "assets" / "first" / f"team_{idx+1}.jpg"
    if not dst.exists() and sp.exists():
        im = _Im.open(sp).convert("RGB")
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((600, 600))
        im.save(dst, quality=86)
    team_imgs.append(f"theme/assets/first/team_{idx+1}.jpg")
# sec_06 영역의 duck img 4개를 문서 순서대로 치환
_c = [0]
def _team_sub(m):
    i = _c[0]; _c[0] += 1
    return f'src="{team_imgs[i]}"' if i < len(team_imgs) else m.group(0)
# about_06 이미지(=크루 팀 아바타)는 sec_06에만 등장 → 섹션 경계 안 찾고 전체에서 순서대로 치환
# (sec_13 삭제로 sec_06이 마지막 섹션이 되면서 기존 경계 lookahead가 깨졌던 버그 수정)
about = re.sub(r'src="https://hothaan\.co\.kr/html/img/new_01/about_06_0[12]\.png"', _team_sub, about)
# 히어로 배경: 우리 스튜디오 사진을 어둡게 가공해서 사용
from PIL import Image, ImageEnhance
herobg = ROOT / "theme" / "assets" / "first" / "about-hero-bg.jpg"
if not herobg.exists():
    im = Image.open(HOME / "dfirst-new" / "assets" / "studio" / "m010.jpg").convert("RGB")
    im = ImageEnhance.Brightness(im).enhance(0.42)
    im = ImageEnhance.Color(im).enhance(0.75)
    im.save(herobg, quality=86)
about = about.replace("https://hothaan.co.kr/html/img/new_01/about_01_bg.jpg", "theme/assets/first/about-hero-bg.jpg")
# What we seek 밴드: hothaan 사무실 사진(PIXELART 모니터=타사) → 우리 화이트 스튜디오 m023(작업 테이블) 와이드 크롭
# (m022 빈 벽 크롭은 밋밋해서 탈락 — 테이블이 우측에 걸려야 구도가 삶)
seekbg = ROOT / "theme" / "assets" / "first" / "about-seek-bg.jpg"
if not seekbg.exists():
    im = Image.open(HOME / "dfirst-new" / "assets" / "studio" / "m023.jpg").convert("RGB")
    w, h = im.size
    im.crop((0, int(h * 0.22), w, int(h * 0.68))).save(seekbg, quality=88)

# 나머지 hothaan 이미지(팀 일러스트·아이콘)는 다운로드해서 self-host
for url in sorted(set(re.findall(r'https://hothaan\.co\.kr/html/img/[^"\'\s>]+', about))):
    name = url.split("/img/")[1].replace("/", "_")
    if fetch(url, HH / name):
        about = about.replace(url, "theme/assets/hh/" + name)

# hh 그래픽 블루/퍼플 → 틸 (1회)
def shift_blue_to_teal(path):
    from PIL import Image
    im = Image.open(path)
    has_a = im.mode in ("RGBA", "LA", "P")
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    hsv = rgba.convert("RGB").convert("HSV")
    ch, cs, cv = hsv.split()
    hd, sd = ch.load(), cs.load()
    w, ht = ch.size
    for y in range(ht):
        for x in range(w):
            hue = hd[x, y]
            if 130 <= hue <= 205 and sd[x, y] >= 30:  # 블루~퍼플
                hd[x, y] = 118 + int((hue - 130) * 0.15)
    out = Image.merge("HSV", (ch, cs, cv)).convert("RGB")
    out = Image.merge("RGBA", (*out.split(), a)) if has_a else out
    out.save(path)

hue_mark = HH / ".hue-done"
if not hue_mark.exists():
    for f in HH.glob("*.*"):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
            try:
                shift_blue_to_teal(f)
            except Exception as e:
                print("hue skip", f.name, e)
    hue_mark.write_text("done")

# ---------- 4. CSS 추출 (.about_new 스코프 + 키프레임) ----------
css_src = (SCRATCH / "hh-style_02.css").read_text(encoding="utf-8", errors="ignore")

def parse_blocks(css):
    out, i, n = [], 0, len(css)
    while True:
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        out.append((sel, css[j + 1:k - 1], css[i:k]))
        i = k
    return out

# style_02 전체를 .about_new 하위로 스코프(원본 캐스케이드 그대로 복제).
# 기존엔 'about_new' 셀렉터만 남겨서 베이스 타이포(.title_box/.tit/.sub/.gra_01)가 유실됐음.
def scope_sel(sel):
    out = []
    for p in sel.split(","):
        p = p.strip()
        if not p:
            continue
        if ".about_new" in p:
            out.append(p)                       # 이미 스코프됨
        elif p in ("html", "body", ":root", "*"):
            out.append(".about_new")
        else:
            out.append(".about_new " + p)       # 베이스 컴포넌트 → 스코프 주입
    return ", ".join(out)

# 스케일 히스토리(2026-07-22): 0.6 "본문 다 작다" → 1.0 "클론처럼" → "전체적으로 너무 커" → 0.7 확정.
# 0.7 = 본문 24→16.8px로 메인페이지(15~17px)와 정렬, 디스플레이 타이포는 포인트로 유지.
# ⚠️아래 override 블록의 px 리터럴은 이 SCALE 기준으로 수동 환산돼 있음 — SCALE 바꾸면 같이 환산할 것.
SCALE = 0.7
def scale_body(body):
    def rep(m):
        v = float(m.group(1))
        if v <= 2:            # 보더/하이라인은 유지
            return m.group(0)
        nv = round(v * SCALE, 1)
        return (f"{nv:g}") + "px"
    return re.sub(r'(\d+(?:\.\d+)?)px', rep, body)

kept = []
for sel, body, raw in parse_blocks(css_src):
    s = sel.strip()
    if s.startswith(("@keyframes", "@-webkit-keyframes", "@font-face", "@import", "@charset")):
        kept.append(raw)
    elif s.startswith("@media"):
        inner = "".join(scope_sel(s2) + "{" + scale_body(b2) + "}"
                        for s2, b2, r2 in parse_blocks(body) if not s2.strip().startswith("@"))
        if inner:
            kept.append(s + "{" + inner + "}")   # @media 조건값(max-width 등)은 그대로
    elif s.startswith("@"):
        kept.append(raw)
    else:
        kept.append(scope_sel(s) + "{" + scale_body(body) + "}")
css = "\n".join(kept)
# 리컬러: 핫한 블루/퍼플 → 인천 틸
css = css.replace("#2EBDEF", PRIMARY).replace("#2ebdef", PRIMARY)
css = css.replace("#56C0FE", "#2fd0bd").replace("#6D0EE6", "#0A7A6E")
css = css.replace("#4C00FF", PRIMARY).replace("#4c00ff", PRIMARY)
css = css.replace("#6D0EE6", "#0A7A6E").replace("#3D00CC", "#0A7A6E")
# 팀 4색 '진한' 액센트(핑크/그린/블루)만 틸로 — 연한 파스텔 카드 배경은 유지해 변화감 살림
for hexv in ["#ff0089", "#f83af0", "#f444a2", "#ff3068", "#ff7cc2",
             "#5dd400", "#80ce44", "#119cd4", "#119c8f"]:
    css = css.replace(hexv, PRIMARY).replace(hexv.upper(), PRIMARY)
# CSS 내 이미지 다운로드 + 경로 재작성 (about3.css는 theme/css/pages/에 위치)
for m in sorted(set(re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", css))):
    if m.startswith("data:"):
        continue
    full = m if m.startswith("http") else "https://hothaan.co.kr" + (m if m.startswith("/") else "/html/css/" + m)
    name = "css_" + full.split("/")[-1].split("?")[0]
    if fetch(full, HH / name):
        css = css.replace(m, "../../assets/hh/" + name)
base = f"""@font-face{{font-family:'montserrat';src:url('../../vendor/fonts/montserrat-600.woff2') format('woff2');font-weight:600;font-display:swap}}
@font-face{{font-family:'montserrat';src:url('../../vendor/fonts/montserrat-700.woff2') format('woff2');font-weight:700;font-display:swap}}
@font-face{{font-family:'montserrat';src:url('../../vendor/fonts/montserrat-800.woff2') format('woff2');font-weight:800;font-display:swap}}
.about_new{{overflow:hidden;word-break:keep-all;color:#111;--sec-pd:91px}}
.about_new .wrapper{{max-width:1400px;margin:0 auto;padding:0 24px}}
.about_new img{{max-width:100%}}
/* 스크롤 애니메이션(aos)은 안 쓰고 항상 최종 노출 상태로 — 콘텐츠가 숨겨질 위험 제거 */
.about_new [data-aos]{{opacity:1 !important;transform:none !important;visibility:visible !important}}
"""
# 히어로 어둡게 + 팀 카드/툴 탭 색 보정 (추출 CSS 뒤에 와서 확실히 이김)
# 히어로 어둡게: img_wrap은 원본대로 position:absolute·z-index:-1 유지(=풀블리드 배경). ::after만 추가(img_wrap이 이미 positioning context).
override = f""".about_new .sec_01 .img_wrap::after{{content:'';position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(6,20,18,.30),rgba(6,20,18,.60))}}
.about_new .gra_01{{background:linear-gradient(120deg,#2fd0bd,#0A7A6E);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.about_new .sub.purple,.about_new .sub.blue{{color:{PRIMARY}}}
/* 팀 라벨 4색(핫한 브랜드컬러) → 틸 계열로 통일 */
.about_new .tit.purple{{color:#0A7A6E}}
.about_new .tit.blue{{color:{PRIMARY}}}
.about_new .tit.green{{color:#119c8f}}
.about_new .tit.pink{{color:#12b3a0}}
/* ===== 사진 비율·레이아웃 통일 (object-fit cover로 회색여백 제거) ===== */
/* sec_02 회사전경 스와이퍼: 균일 카드(SCALE 0.7 기준) */
.about_new .sec_02 .swiper-slide{{width:420px !important;height:284px !important;border-radius:18px !important}}
.about_new .sec_02 .swiper-slide img{{width:100% !important;height:100% !important;object-fit:cover !important;display:block}}
/* sec_03 좌우 스플릿 이미지: 4:3 통일 */
.about_new .sec_03 .list .item .img_wrap{{aspect-ratio:4/3;height:auto !important;border-radius:22px !important;overflow:hidden}}
.about_new .sec_03 .list .item .img_wrap img{{width:100% !important;height:100% !important;object-fit:cover !important;display:block}}
/* ===== 위아래 간격 (SCALE 0.7 기준) ===== */
.about_new .sec_02 .sec_head .title_box{{padding-top:163px !important}}
.about_new .sec_03{{margin-top:93px !important}}
/* sec_06 크루 카드: 짝수 카드 translateY 스태거(210px/1199↓140px)만큼 하단 패딩 확보 — 부족하면 CTA에 잘림 */
.about_new .sec_06{{padding:91px 0 301px !important}}
@media all and (max-width:1199px){{.about_new .sec_06{{padding:91px 0 231px !important}}}}
@media all and (max-width:1023px){{.about_new .sec_06{{padding:91px 0 !important}}}}
/* sec_04 상단 장식 썸네일(원본 마스코트 자리) 제거 — 랜덤 이미지처럼 보임 */
.about_new .sec_04 .title_box img{{display:none}}
/* 모션(float/scale/rotate 등 장식 애니메이션) 전부 제거 (사용자) */
.about_new *,.about_new *::before,.about_new *::after{{animation:none !important}}
/* sec_02 How we work 밴드도 동일 화이트 페이드 (sec_05 규칙이 더 구체적이라 각자 이미지 유지) */
.about_new .sec_head::before{{background-image:linear-gradient(180deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.97) 94%),url('../../assets/hh/css_about_02_bg.jpg')}}
/* sec_05 What we seek: 사진=우리 화이트 스튜디오(hothaan 사무실 사진은 타사) + 하단 화이트 페이드(타이틀 가독) */
.about_new .sec_05 .sec_head::before{{background-image:linear-gradient(180deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.97) 94%),url('../../assets/first/about-seek-bg.jpg')}}
/* (본문 업스케일 오버라이드는 원본 1:1 스케일 전환으로 불필요해져 제거 — 원본 크기가 곧 정답) */
/* 크루 멤버 코멘트 폰트 업(사용자, SCALE 0.7 기본값 14px → 16px) + 리스트 왼쪽 여백(사용자) */
.about_new .sec_06 .list .item .btm ul{{padding-left:30px;padding-right:12px}}
.about_new .sec_06 .list .item .btm ul li{{font-size:16px;line-height:1.6}}
.about_new .sec_06 .list .item .btm ul li::before{{width:15px;height:15px;top:4px}}
/* 크루 팀 아바타: 마스코트 오프셋(span 107%/음수마진) 제거 → 사진이 원을 꽉 채우게 */
.about_new .sec_06 .list .item .img_wrap{{overflow:hidden}}
.about_new .sec_06 .list .item .img_wrap span{{width:100% !important;height:100% !important;margin:0 !important;display:block}}
.about_new .sec_06 .list .item .img_wrap img{{width:100% !important;height:100% !important;object-fit:cover !important;display:block}}
"""
(ROOT / "theme" / "css" / "pages" / "about3.css").write_text(base + css + override, encoding="utf-8")

# ---------- 5. about.html 패치 ----------
CTA2_MARK = '<section class="cta-section">'
page = (ROOT / "about.html").read_text(encoding="utf-8")
m = re.search(r'<main class="site-main">(.*?)</main>', page, re.S)
old_main = m.group(1)
cta = re.search(r'<section class="cta-section">.*?</section>', old_main, re.S)
cta_html = cta.group(0) if cta else ""
new_main = f'<main class="site-main">\n{about}\n{cta_html}\n</main>'
page = page[:m.start()] + new_main + page[m.end():]
# head: about css들 → about3 + swiper + aos
fetch("https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css", ROOT / "theme" / "vendor" / "aos.css")
fetch("https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js", ROOT / "theme" / "vendor" / "aos.js")
# Montserrat 셀프호스팅(구글폰트 외부링크는 이 프리뷰서 로드 안 됨 → 대형 영문 디스플레이 폰트 깨짐)
FONTDIR = ROOT / "theme" / "vendor" / "fonts"
FONTDIR.mkdir(parents=True, exist_ok=True)
for wght in (600, 700, 800):
    fetch(f"https://cdn.jsdelivr.net/npm/@fontsource/montserrat/files/montserrat-latin-{wght}-normal.woff2",
          FONTDIR / f"montserrat-{wght}.woff2")
head_add = ("<link rel='stylesheet' href='theme/vendor/swiper-bundle.min.css' />\n"
            "<link rel='stylesheet' href='theme/css/pages/about3.css' />\n</head>")
if "about3.css" not in page:
    page = page.replace("</head>", head_add, 1)
page = re.sub(r"<link[^>]*pages/(?:about|aboutx)\.css[^>]*/>\n?", "", page)
# body 끝: 스크립트 (스와이퍼 마퀴 / AOS / 툴 탭)
if "theme/vendor/aos.js" not in page:
    page = page.replace("</body>", """<script src="theme/vendor/swiper-bundle.min.js"></script>
<script>
(function(){
    var el = document.querySelector('.about_new .sec_02 .swiper');
    if (el && window.Swiper) new Swiper(el, {speed:4000, autoplay:{delay:0}, loop:true,
        slidesPerView:'auto', spaceBetween:20, allowTouchMove:false});
    var tabs = document.querySelectorAll('.about_new .sec_13 .tab_menu ul li > *');
    var conts = document.querySelectorAll('.about_new .sec_13 .tab_cont');
    tabs.forEach(function(t, i){
        t.addEventListener('click', function(e){
            e.preventDefault();
            tabs.forEach(function(x){x.classList.remove('on');});
            conts.forEach(function(x){x.classList.remove('on');});
            t.classList.add('on');
            if (conts[i]) conts[i].classList.add('on');
        });
    });
    if (tabs.length && !document.querySelector('.about_new .sec_13 .tab_menu .on')) tabs[0].click();
})();
</script>
</body>""", 1)
(ROOT / "about.html").write_text(page, encoding="utf-8")
print("about.html ← hothaan about_new 이식 완료 | 섹션:", [k for k in KEEP if k in segs])
