# -*- coding: utf-8 -*-
"""포트폴리오 카드 대량 주입 (_pfimport.py가 만든 _pf_items.json 사용).
기존 44카드 + firstd/dfirst 수집분 → 카테고리 매핑 후 pf-grid 교체 + '더보기' 페이징.
체인 맨 마지막(_subsvc.py 뒤)에서 실행. ⚠️_subpages.py가 portfolio.html을 리빌드하므로 그 뒤에 돌 것."""
import json, re, pathlib, hashlib

ROOT = pathlib.Path(__file__).parent
items = json.loads((ROOT / "_pf_items.json").read_text(encoding="utf-8"))

# ---------- 카테고리 매핑 (우리 필터 5종) ----------
# 제목 키워드 우선 → 소스 카테고리 폴백
KW = [
    ("리플릿", ["리플렛", "리플릿", "팜플렛", "팜플릿", "전단", "쿠폰북", "접지"]),
    ("책자", ["카탈로그", "카다로그", "브로슈어", "브로셔", "회사소개", "사보", "독서기록장", "매뉴얼", "안내서"]),
    ("기타", ["포스터", "배너", "현수막", "공모전", "캠페인"]),
    ("로고", ["로고", "브랜딩", "ci", "bi", "네이밍", "심볼"]),
    ("촬영", ["촬영", "제품컷", "상세페이지", "패키지", "영상", "카드뉴스", "썸네일", "바이럴", "상세"]),
]
SRC_CAT = {"catalog": "책자", "brand": "로고", "poster": "기타",
           "package": "촬영", "detail": "촬영", "photo": "촬영", "etc": "촬영"}

def classify(it):
    t = (it["title"] or "").lower()
    for our, kws in KW:
        if any(k in t for k in kws):
            return our
    return SRC_CAT.get(it["cat"], "촬영")

# ---------- 제목/부제 분리 ----------
TYPE_WORDS = ["카탈로그", "카다로그", "브로슈어", "브로셔", "리플렛", "리플릿", "팜플렛", "팜플릿",
              "포스터", "로고", "패키지", "브랜딩", "회사소개서", "독서기록장", "쿠폰북", "전단",
              "제품컷", "상세페이지", "영상", "매뉴얼"]
CAT_LABEL = {"책자": "카탈로그 · 브로슈어", "리플릿": "리플렛 · 팜플렛", "로고": "로고 · 브랜딩",
             "촬영": "촬영 · 콘텐츠", "기타": "포스터 · 기타"}

def split_title(title, cat):
    t = (title or "").strip().replace("_", " ")
    t = re.sub(r"\s+", " ", t)
    if " · " in t:                      # dfirst 형식 "브랜드 · 종류"
        name, _, typ = t.partition(" · ")
        return name.strip(), typ.strip()
    for w in TYPE_WORDS:                # firstd 형식 "브랜드 종류"
        if t.endswith(" " + w) or t.endswith(w):
            name = t[: len(t) - len(w)].strip(" ·-")
            if name:
                return name, w
    return (t or "퍼스트디자인"), CAT_LABEL.get(cat, "디자인 제작")

# ---------- 카드 생성 ----------
seen_file, seen_key, cards = set(), set(), []
for it in items:
    f = it.get("file")
    if not f:
        continue
    cat = classify(it)
    name, typ = split_title(it["title"], cat)
    key = (name, typ)
    if f in seen_file or key in seen_key:
        continue
    seen_file.add(f); seen_key.add(key)
    cards.append((cat, name, typ, f))

# 카테고리별 균형 정렬(전체 탭에서 한 종류만 몰리지 않게 라운드로빈)
from collections import defaultdict, deque
buckets = defaultdict(deque)
for c in cards:
    buckets[c[0]].append(c)
order = ["책자", "로고", "리플릿", "촬영", "기타"]
mixed = []
while any(buckets[o] for o in order):
    for o in order:
        if buckets[o]:
            mixed.append(buckets[o].popleft())

INIT = 60          # 처음 노출 개수 (나머지는 '더보기')
html = ""
for i, (cat, name, typ, f) in enumerate(mixed):
    hide = ' style="display:none"' if i >= INIT else ""
    html += (f'<div class="pf-card{" pf-more" if i >= INIT else ""}" data-cat="{cat}"{hide}>'
             f'<div class="pf-card-thumb" data-modal="{f}">'
             f'<div class="pf-card-img" style="background-image:url(\'{f}\')"></div></div>'
             f'<h2 class="pf-card-name">{name}</h2>'
             f'<p class="pf-card-type">{typ}</p></div>\n')

# ---------- portfolio.html 주입 ----------
p = ROOT / "portfolio.html"
s = p.read_text(encoding="utf-8")
m = re.search(r'(<div class="pf-grid"[^>]*>)(.*?)(</div>\s*</div>\s*</section>)', s, re.S)
assert m, "pf-grid 블록을 찾지 못함"
btn = ('<div class="pf-morewrap"><button type="button" id="pfMore" class="pf-morebtn">'
       f'작업물 더 보기 <span>({len(mixed) - INIT})</span></button></div>')
s = s[:m.start()] + m.group(1) + "\n" + html + m.group(3).replace("</div>", btn + "</div>", 1) + s[m.end():]

# 더보기 + 필터 연동 스크립트 (기존 필터 JS 뒤에 추가, 마커로 재실행 안전)
JS = """<!--pf-more-->
<script>
(function(){
  var btn = document.getElementById('pfMore');
  if (!btn) return;
  var STEP = 60;
  function activeCat(){
    var b = document.querySelector('.pf-filter-btn.active');
    return b ? b.getAttribute('data-filter') : 'all';
  }
  function hiddenCards(){
    var cat = activeCat();
    return [].slice.call(document.querySelectorAll('.pf-card.pf-more')).filter(function(c){
      return c.style.display === 'none' && (cat === 'all' || c.getAttribute('data-cat') === cat);
    });
  }
  function sync(){
    var n = hiddenCards().length;
    btn.parentNode.style.display = n ? '' : 'none';
    btn.querySelector('span').textContent = '(' + n + ')';
  }
  btn.addEventListener('click', function(){
    hiddenCards().slice(0, STEP).forEach(function(c){
      c.style.display = '';
      c.classList.add('visible');
    });
    sync();
  });
  document.querySelectorAll('.pf-filter-btn').forEach(function(b){
    b.addEventListener('click', function(){ setTimeout(sync, 30); });
  });
  sync();
})();
</script>
<style>
.pf-morewrap{grid-column:1/-1;text-align:center;margin:56px 0 0}  /* 그리드 전체 폭 차지(없으면 첫 칸에 갇혀 왼쪽 치우침) */
.pf-morebtn{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid #0C9384;color:#0C9384;
  font-family:inherit;font-size:16px;font-weight:700;padding:15px 34px;border-radius:999px;cursor:pointer;transition:all .2s ease}
.pf-morebtn:hover{background:#0C9384;color:#fff}
.pf-morebtn span{font-weight:600;opacity:.7}
</style>
<!--/pf-more-->"""
if "<!--pf-more-->" in s:
    s = re.sub(r'<!--pf-more-->.*?<!--/pf-more-->', JS, s, flags=re.S)
else:
    s = s.replace("</body>", JS + "\n</body>", 1)
p.write_text(s, encoding="utf-8")

from collections import Counter
print("portfolio cards:", len(mixed), dict(Counter(c[0] for c in mixed)))
