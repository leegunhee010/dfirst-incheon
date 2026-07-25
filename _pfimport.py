# -*- coding: utf-8 -*-
"""포트폴리오 대량 수집 (2026-07-22 사용자 "dfirst.co.kr이랑 firstd.co.kr에서 다 가져와 마니마니")
 1) firstd.co.kr 카페24 갤러리(PORTFOLIO 게시판 8번) 전 카테고리·전 페이지 크롤
    ⚠️봇 차단 회피: Referer/Accept-Language/크롬 UA 헤더 필수(없으면 목록 li가 안 옴)
 2) dfirst.co.kr portfolio.html + 서비스 페이지의 라벨 카드
 3) 이미지 다운로드 → theme/assets/first/pf2/, 해시 중복 제거
 4) _pf_items.json 으로 저장 (→ _portfolio.py가 카드 렌더)
"""
import os, re, json, hashlib, pathlib, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent
DST = ROOT / "theme" / "assets" / "first" / "pf2"
DST.mkdir(parents=True, exist_ok=True)
CACHE = ROOT / "_pf_items.json"

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,*/*",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

def get(url, referer=None, binary=False, timeout=30):
    h = dict(HDR)
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
    return b if binary else b.decode("utf-8", "ignore")

# ---------- 1. firstd 갤러리 ----------
FD = "https://firstd.co.kr"
LIST = FD + "/board/gallery/list.html?board_no=8"
# 카페24 카테고리 → 우리 필터 키
CAT_MAP = {1: "catalog", 3: "brand", 4: "poster", 5: "package",
           6: "detail", 7: "detail", 9: "etc", 11: "etc", 14: "etc"}

LI_RE = re.compile(
    r'<li class="xans-record-">(.*?)</li>', re.S)
IMG_RE = re.compile(r'<img src="(//firstd\.co\.kr/file_data/[^"]+)"')
TITLE_RE = re.compile(r'class="imgLink">([^<]*)</a>')

def parse_list(html):
    out = []
    for li in LI_RE.findall(html):
        m = IMG_RE.search(li)
        if not m:
            continue
        titles = [t.strip() for t in TITLE_RE.findall(li) if t.strip()]
        out.append(("https:" + m.group(1), titles[-1] if titles else ""))
    return out

def crawl_firstd():
    items, seen = [], set()
    def add(src, title, cat):
        if src in seen:
            # 카테고리 정보만 보강
            for it in items:
                if it["src"] == src and not it["cat"] and cat:
                    it["cat"] = cat
            return 0
        seen.add(src)
        items.append({"src": src, "title": title, "cat": cat, "from": "firstd"})
        return 1
    # 카테고리별 먼저 (라벨 정확도)
    for cno, cat in CAT_MAP.items():
        for p in range(1, 12):
            try:
                html = get(f"{LIST}&category_no={cno}&page={p}", referer=LIST)
            except Exception as e:
                print("  fail", cno, p, e); break
            rows = parse_list(html)
            if not rows:
                break
            n = sum(add(s, t, cat) for s, t in rows)
            print(f"  cat{cno} p{p}: {len(rows)} rows (+{n})")
    # 전체 목록 (카테고리 없는 것 포함)
    for p in range(1, 45):
        try:
            html = get(f"{LIST}&page={p}", referer=LIST)
        except Exception as e:
            print("  fail all", p, e); break
        rows = parse_list(html)
        if not rows:
            break
        n = sum(add(s, t, "") for s, t in rows)
        print(f"  all p{p}: {len(rows)} rows (+{n})")
    return items

# ---------- 2. dfirst 라벨 카드 ----------
DF = "https://dfirst.co.kr"
DF_PAGES = ["portfolio", "index", "catalog", "logo", "leaflet", "poster", "photo", "marketing"]
DF_CAT = {"brand": "brand", "catalog": "catalog", "leaflet": "catalog",
          "poster": "poster", "photo": "photo", "web": "etc", "detail": "detail", "video": "etc"}

def crawl_dfirst():
    items, seen = [], set()
    for pg in DF_PAGES:
        try:
            html = get(f"{DF}/{pg}.html")
        except Exception as e:
            print("  fail", pg, e); continue
        n = 0
        for m in re.finditer(r'<div class="pf"[^>]*data-cat="([^"]+)"[^>]*data-label="([^"]+)"[^>]*>\s*<img src="([^"]+)"', html):
            cat, label, src = m.groups()
            url = f"{DF}/{src}" if not src.startswith("http") else src
            if url in seen:
                continue
            seen.add(url)
            items.append({"src": url, "title": label, "cat": DF_CAT.get(cat, "etc"), "from": "dfirst"})
            n += 1
        for m in re.finditer(r'<img src="(assets/[^"]+\.(?:jpg|jpeg|png))" alt="([^"]*)"><div class="cap">([^<]*)</div>', html):
            src, alt, cap = m.groups()
            url = f"{DF}/{src}"
            if url in seen:
                continue
            seen.add(url)
            items.append({"src": url, "title": (cap or alt).strip(), "cat": "", "from": "dfirst"})
            n += 1
        print(f"  {pg}: +{n}")
    return items

# ---------- 3. 다운로드 ----------
def download(items):
    hashes, ok, fail = {}, 0, 0
    def one(it):
        nonlocal ok, fail
        ext = os.path.splitext(it["src"].split("?")[0])[1].lower() or ".jpg"
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            ext = ".jpg"
        name = "p_" + hashlib.md5(it["src"].encode()).hexdigest()[:14] + ext
        dst = DST / name
        if not dst.exists():
            try:
                b = get(it["src"], referer=FD + "/", binary=True, timeout=40)
                if len(b) < 3000:      # 깨진 썸네일/플레이스홀더
                    raise ValueError(f"too small {len(b)}")
                dst.write_bytes(b)
            except Exception as e:
                it["file"] = None
                fail += 1
                return
        it["file"] = "theme/assets/first/pf2/" + name
        ok += 1
    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(one, items))
    # 내용 해시 중복 제거
    uniq, dupes = [], 0
    for it in items:
        if not it.get("file"):
            continue
        p = ROOT / it["file"]
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h in hashes:
            it["file"] = hashes[h]     # 같은 파일 재사용
            dupes += 1
        else:
            hashes[h] = it["file"]
        uniq.append(it)
    print(f"downloaded ok={ok} fail={fail} content-dupes={dupes} kept={len(uniq)}")
    return uniq

if __name__ == "__main__":
    print("== firstd.co.kr ==")
    a = crawl_firstd()
    print("firstd items:", len(a))
    print("== dfirst.co.kr ==")
    b = crawl_dfirst()
    print("dfirst items:", len(b))
    items = a + b
    print("== download ==")
    items = download(items)
    CACHE.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", CACHE.name, len(items))
