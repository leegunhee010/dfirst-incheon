# -*- coding: utf-8 -*-
"""기존 칼럼 4글을 관리자 DB(columns.json)에 등록 (2026-07-28 사용자
"관리자에서 칼럼 카테고리 들어가면 아무것도 안뜨고").

원인: 기존 글은 빌드 스크립트(_subpages.py)로 만든 정적 파일이라 관리자 DB에 기록이 없었음
      → 관리자 칼럼 탭이 '글이 없습니다'로 보였다.
방식: 각 글의 HTML에서 제목·카테고리·날짜·요약·썸네일·본문을 추출해 등록.
      기존 파일명을 file 필드로 보존해 URL·검색 노출을 유지하고(col-N.html로 바뀌면 안 됨),
      builtin 표시로 상세 페이지를 템플릿으로 덮어쓰지 않게 한다(공들인 목차·FAQ 보존)."""
import re, json, pathlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

R = pathlib.Path(__file__).parent
FILES = ["column-design.html", "column-catalog.html", "column-logo.html", "column-print.html"]

def pick(pat, s, default=""):
    m = re.search(pat, s, re.S)
    return m.group(1).strip() if m else default

rows = []
for i, name in enumerate(FILES, 1):
    p = R / name
    if not p.exists():
        print(f"⚠️{name} 없음"); continue
    s = p.read_text(encoding='utf-8')
    title = pick(r'<title>(.*?)\s*\|', s) or pick(r'<h1[^>]*>(.*?)</h1>', s)
    title = re.sub(r'<[^>]+>', '', title).strip()
    excerpt = pick(r'<meta name="description" content="([^"]*)"', s)
    cat = pick(r'"articleSection":\s*"([^"]*)"', s) or pick(r'blog-single-cat[^>]*>([^<]*)<', s)
    date = pick(r'"datePublished":\s*"([^"]*)"', s)
    thumb = pick(r'<meta property="og:image" content="[^"]*?/(theme/[^"]*)"', s)
    # 본문 컨테이너 안에 CTA 박스가 중첩돼 있어 정규식만으로는 끝을 잡을 수 없음
    # → 시작 위치부터 다음 섹션(FAQ/이전다음글) 앞까지 잘라내고, 닫는 </div>와 CTA 박스를 정리
    start = s.find('<div class="blog-single-body">')
    body = ""
    if start >= 0:
        start += len('<div class="blog-single-body">')
        # CTA 박스는 본문 컨테이너 '바깥'의 형제 요소 → 가장 먼저 오는 경계에서 자른다
        ends = [s.find(k, start) for k in
                ('<div class="blog-single-cta">', '<!--col-faq-->', '<section class="col-faq"',
                 '<nav class="blog-single-nav"', '<div class="blog-single-nav"')]
        ends = [e for e in ends if e > 0]
        body = s[start:min(ends)] if ends else ""
        body = re.sub(r'(</div>\s*)+$', '', body.strip()).strip()   # 컨테이너 닫는 태그
    rows.append({
        "id": i, "title": title, "category": cat or "Column",
        "excerpt": excerpt, "body": body.strip(),
        "thumbnail": thumb or "theme/assets/first/column-card.png",
        "status": "published", "date": date or "2026-07-20",
        "file": name,        # 기존 URL 유지
        "builtin": True,     # 상세 페이지는 템플릿 재생성 대상에서 제외
    })
    print(f"{name:22s} {title[:26]:28s} {cat:9s} {date}  본문 {len(body)}자")

out = R / 'admin' / 'data' / 'columns.json'
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
print(f"\ncolumns.json 등록: {len(rows)}건")
