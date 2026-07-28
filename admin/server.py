# -*- coding: utf-8 -*-
"""퍼스트디자인 인천지사 관리자 서버 (dfirst.co.kr/admin 기능 복제).
로컬 Flask → JSON 저장 → 정적 HTML 굽기(AI 읽기 가능) → GitHub Pages 푸시 파이프라인.
탭: 대시보드/히어로/문의/포트폴리오/칼럼/카피/FAQ/이미지/SEO/계정.
실행:  python admin/server.py   → http://localhost:5701/admin  (초기 비번 admin1234)"""
import os, re, json, time, hashlib, pathlib, mimetypes
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory, redirect

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data"
UI = HERE / "ui"
MEDIA = ROOT / "theme" / "assets" / "first" / "pf2"
DATA.mkdir(exist_ok=True)

import bake  # noqa

app = Flask(__name__, static_folder=None)
app.secret_key = "dfirst-incheon-admin-secret-2026"
# GitHub Pages(다른 도메인)에서 이 관리자 API를 호출할 수 있게 CORS + 크로스도메인 세션 쿠키
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
_ALLOWED_ORIGINS = {"https://leegunhee010.github.io"}

@app.after_request
def _cors(resp):
    origin = request.headers.get("Origin", "")
    if origin in _ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Vary"] = "Origin"
    return resp

@app.route("/api/<path:_p>", methods=["OPTIONS"])
def _preflight(_p):
    return ("", 204)

# ---------- 저장 헬퍼 ----------
def jload(name, default):
    p = DATA / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default

def jsave(name, obj):
    (DATA / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

def auth_cfg():
    cfg = jload("auth", None)
    if not cfg:
        cfg = {"user": "admin", "hash": hashlib.sha256("admin1234".encode()).hexdigest()}
        jsave("auth", cfg)
    return cfg

def require(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("uid"):
            return jsonify({"error": "unauthorized"}), 401
        return f(*a, **k)
    return w

# ---------- 인증 ----------
@app.post("/api/login")
def login():
    d = request.json or {}
    pw = d.get("password", "")
    admins = jload("admins", None)
    if admins:   # 다중 관리자 목록 우선
        for a in admins:
            if a["user"] == d.get("username") and a["hash"] == hashlib.sha256(pw.encode()).hexdigest():
                session["uid"] = a["user"]
                return jsonify({"ok": True, "user": a["user"]})
    cfg = auth_cfg()
    if hashlib.sha256(pw.encode()).hexdigest() == cfg["hash"]:
        session["uid"] = d.get("username") or cfg["user"]
        return jsonify({"ok": True, "user": session["uid"]})
    return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.get("/api/me")
def me():
    return jsonify({"authed": bool(session.get("uid")), "user": session.get("uid")})

@app.post("/api/account/password")
@require
def chpw():
    d = request.json or {}
    cfg = auth_cfg()
    if hashlib.sha256(d.get("current", "").encode()).hexdigest() != cfg["hash"]:
        return jsonify({"error": "현재 비밀번호가 틀립니다"}), 400
    if len(d.get("next", "")) < 4:
        return jsonify({"error": "새 비밀번호는 4자 이상"}), 400
    cfg["hash"] = hashlib.sha256(d["next"].encode()).hexdigest()
    jsave("auth", cfg)
    return jsonify({"ok": True})

# ---------- 대시보드 ----------
@app.get("/api/stats")
@require
def stats():
    inq = jload("inquiries", [])
    recent = sorted(inq, key=lambda x: -x.get("ts", 0))[:6]
    def row(q):
        return {"createdAt": q.get("createdAt") or (q.get("ts") and __import__("datetime").datetime.fromtimestamp(q["ts"]).isoformat()),
                "company": q.get("company", ""), "name": q.get("name", ""),
                "field": q.get("field", ""), "phone": q.get("phone", q.get("email", "")),
                "status": q.get("status", "new")}
    return jsonify({
        "inquiries": len(inq),
        "inquiriesNew": sum(1 for q in inq if q.get("status", "new") == "new"),
        "portfolio": len(jload("portfolio", [])),
        "columns": len(jload("columns", [])),
        "recent": [row(q) for q in recent],
    })

# ---------- 포트폴리오 (완전 동작 + 굽기) ----------
@app.get("/api/portfolio")
@require
def pf_list():
    items = sorted(jload("portfolio", []), key=lambda x: x.get("order", 0))
    return jsonify(items)

@app.post("/api/portfolio")
@require
def pf_save():
    """FormData(title/category/image파일) 단건 추가 [dfirst UI] 또는 JSON {items} 전체 저장."""
    if request.files.get("image"):         # dfirst UI: 파일 업로드 + 생성
        f = request.files["image"]
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            ext = ".jpg"
        MEDIA.mkdir(parents=True, exist_ok=True)
        name = "pf_" + hashlib.md5((f.filename + str(time.time())).encode()).hexdigest()[:14] + ext
        f.save(MEDIA / name)
        try:
            from PIL import Image
            im = Image.open(MEDIA / name)
            if max(im.size) > 1400:
                im.thumbnail((1400, 1400), Image.LANCZOS); im.save(MEDIA / name)
        except Exception:
            pass
        items = jload("portfolio", [])
        nid = max([x["id"] for x in items], default=0) + 1
        title = request.form.get("title", "").strip()
        cat = request.form.get("category", "책자")
        # 제목에서 종류 추출("브랜드 · 종류" 또는 마지막 단어)
        typ = ""
        if " · " in title:
            title, _, typ = title.partition(" · ")
        items.insert(0, {"id": nid, "image": "theme/assets/first/pf2/" + name,
                         "title": title.strip(), "type": typ.strip(), "category": cat, "order": -1})
        for i, it in enumerate(items):
            it["order"] = i
        jsave("portfolio", items)
    else:                                  # JSON 전체 저장
        d = request.json or {}
        items = d.get("items", [])
        for i, it in enumerate(items):
            it["order"] = i
        jsave("portfolio", items)
    n = bake.bake_portfolio()
    return jsonify({"ok": True, "count": n})

@app.delete("/api/portfolio/<int:pid>")
@require
def pf_del(pid):
    items = [x for x in jload("portfolio", []) if x["id"] != pid]
    for i, it in enumerate(items):
        it["order"] = i
    jsave("portfolio", items)
    bake.bake_portfolio()
    return jsonify({"ok": True})

# ---------- 업로드 ----------
@app.post("/api/upload")
@require
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400
    ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        return jsonify({"error": "이미지 파일만"}), 400
    MEDIA.mkdir(parents=True, exist_ok=True)
    name = "up_" + hashlib.md5((f.filename + str(time.time())).encode()).hexdigest()[:14] + ext
    dst = MEDIA / name
    f.save(dst)
    # 큰 이미지 최적화
    try:
        from PIL import Image
        im = Image.open(dst)
        if max(im.size) > 1400:
            im.thumbnail((1400, 1400), Image.LANCZOS)
            im.save(dst)
    except Exception:
        pass
    rel = "theme/assets/first/pf2/" + name
    return jsonify({"ok": True, "path": rel, "url": rel})   # dfirst UI는 r.url 사용

# ---------- 페이지별 이미지 교체 (목록·교체·되돌리기) ----------
def _page_file(page):
    return ROOT / (page if page.endswith(".html") else f"{page}.html")

@app.get("/api/images/<page>")
@require
def images_page(page):
    p = _page_file(page)
    if not p.exists():
        return jsonify([])
    s = p.read_text(encoding="utf-8")
    ov = jload("image_overrides", {}).get(page, {})   # {원본src: 교체src}
    rev = {v: k for k, v in ov.items()}               # 교체src → 원본src
    seen, out = set(), []
    for m in re.finditer(r'(?:<img[^>]+src="|background-image:url\(\')(theme/assets/first/[^"\')]+\.(?:jpg|jpeg|png|webp))', s):
        cur = m.group(1)
        if cur in seen or "/svc/" in cur or "favicon" in cur:
            continue
        seen.add(cur)
        original = rev.get(cur, cur)
        out.append({"id": len(out), "original": original, "src": cur, "overridden": cur in rev})
    return jsonify(out[:60])

@app.post("/api/images/<page>")
@require
def images_replace(page):
    p = _page_file(page)
    f = request.files.get("image")
    original = request.form.get("src", "")
    if not (p.exists() and f and original):
        return jsonify({"error": "잘못된 요청"}), 400
    ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    MEDIA.mkdir(parents=True, exist_ok=True)
    name = "rp_" + hashlib.md5((f.filename + str(time.time())).encode()).hexdigest()[:14] + ext
    f.save(MEDIA / name)
    try:
        from PIL import Image
        im = Image.open(MEDIA / name)
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600), Image.LANCZOS); im.save(MEDIA / name)
    except Exception:
        pass
    newsrc = "theme/assets/first/pf2/" + name
    ovall = jload("image_overrides", {})
    ov = ovall.get(page, {})
    cur = ov.get(original, original)   # 현재 파일에 있는 src
    s = p.read_text(encoding="utf-8").replace(cur, newsrc)
    p.write_text(s, encoding="utf-8")
    ov[original] = newsrc
    ovall[page] = ov
    jsave("image_overrides", ovall)
    return jsonify({"ok": True, "src": newsrc})

@app.delete("/api/images/<page>")
@require
def images_revert(page):
    p = _page_file(page)
    original = request.args.get("src", "")
    ovall = jload("image_overrides", {})
    ov = ovall.get(page, {})
    if original in ov:
        s = p.read_text(encoding="utf-8").replace(ov[original], original)
        p.write_text(s, encoding="utf-8")
        del ov[original]
        ovall[page] = ov
        jsave("image_overrides", ovall)
    return jsonify({"ok": True})

# ---------- 이미지 라이브러리 ----------
@app.get("/api/images/")
@require
def images():
    files = []
    for p in sorted(MEDIA.glob("*"), key=lambda x: -x.stat().st_mtime):
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            files.append({"path": "theme/assets/first/pf2/" + p.name,
                          "size": p.stat().st_size, "name": p.name})
    return jsonify(files[:400])

# ---------- 범용 JSON 탭 (hero/faq/content/seo/columns/inquiries/settings/admins) ----------
def json_tab(name, default):
    @app.get(f"/api/{name}", endpoint=f"get_{name}")
    @require
    def _get():
        return jsonify(jload(name, default))
    @app.route(f"/api/{name}", methods=["PUT", "POST"], endpoint=f"put_{name}")
    @require
    def _put():
        jsave(name, request.json)
        return jsonify({"ok": True})

# ---------- 사이트 설정 (SEO 설정: 도메인·Head코드·파비콘·대표이미지·메일) ----------
@app.get("/api/settings")
@require
def settings_get():
    st = jload("settings", {"domain": "https://incheondesign.co.kr"})
    out = dict(st)
    out.pop("mailPass", None)
    out["mailPassSet"] = bool(st.get("mailPass"))
    return jsonify(out)

@app.route("/api/settings", methods=["PATCH", "PUT"])
@require
def settings_save():
    st = jload("settings", {})
    d = request.json or {}
    for k in ("domain", "headCode", "siteName", "keywords", "mailEnabled", "mailUser", "mailTo"):
        if k in d:
            st[k] = d[k]
    for k in ("snsKakao", "snsInstagram", "snsBlog", "snsPhone"):   # 플로팅 SNS 링크
        if k in d:
            st[k] = d[k]
    if d.get("mailPass"):
        st["mailPass"] = d["mailPass"]
    jsave("settings", st)
    bake.bake_settings()
    bake.bake_sns()
    return jsonify({"ok": True})

@app.post("/api/settings/favicon")
@require
def settings_favicon():
    f = request.files.get("favicon")
    if not f:
        return jsonify({"error": "no file"}), 400
    ext = os.path.splitext(f.filename)[1].lower() or ".png"
    name = "favicon" + ext
    dst = ROOT / "theme" / "assets" / "first" / name
    f.save(dst)
    st = jload("settings", {}); st["favicon"] = "theme/assets/first/" + name; jsave("settings", st)
    bake.bake_settings()
    return jsonify({"ok": True, "favicon": st["favicon"]})

@app.post("/api/settings/ogimage")
@require
def settings_ogimage():
    f = request.files.get("image")
    if not f:
        return jsonify({"error": "no file"}), 400
    MEDIA.mkdir(parents=True, exist_ok=True)
    name = "og_" + hashlib.md5((f.filename + str(time.time())).encode()).hexdigest()[:12] + os.path.splitext(f.filename)[1].lower()
    f.save(MEDIA / name)
    st = jload("settings", {}); st["ogImage"] = "theme/assets/first/pf2/" + name; jsave("settings", st)
    bake.bake_settings()
    return jsonify({"ok": True, "ogImage": st["ogImage"]})

@app.post("/api/settings/test-mail")
@require
def settings_testmail():
    return jsonify({"ok": False, "error": "메일 발송은 배포 서버에서 설정됩니다(로컬 관리자 미지원)."})

# ---------- 관리자 계정 ----------
def _admins():
    a = jload("admins", None)
    if a is None:
        cfg = auth_cfg()
        a = [{"user": cfg["user"], "hash": cfg["hash"], "createdAt": "2026-07-24"}]
        jsave("admins", a)
    return a

@app.get("/api/admins")
@require
def admins_list():
    return jsonify([{"username": a["user"], "createdAt": a.get("createdAt", ""),
                     "me": a["user"] == session.get("uid")} for a in _admins()])

@app.post("/api/admins")
@require
def admins_add():
    d = request.json or {}
    u, pw = d.get("username", "").strip(), d.get("password", "")
    if not u or len(pw) < 4:
        return jsonify({"error": "아이디·비밀번호(4자+)를 확인하세요"}), 400
    a = _admins()
    if any(x["user"] == u for x in a):
        return jsonify({"error": "이미 있는 아이디"}), 400
    a.append({"user": u, "hash": hashlib.sha256(pw.encode()).hexdigest(),
              "createdAt": __import__("datetime").date.today().isoformat()})
    jsave("admins", a)
    return jsonify({"ok": True})

@app.delete("/api/admins/<user>")
@require
def admins_del(user):
    if user == session.get("uid"):
        return jsonify({"error": "본인 계정은 삭제 불가"}), 400
    jsave("admins", [x for x in _admins() if x["user"] != user])
    return jsonify({"ok": True})

# ---------- 카피(문구) — 페이지 목록 (편집모드는 추후) ----------
COPY_PAGES = [("index", "홈"), ("about", "회사소개"),
              ("portfolio", "포트폴리오"), ("contact", "문의"),
              ("catalog", "카탈로그"), ("leaflet", "리플렛"), ("pamphlet", "팜플렛"),
              ("brochure", "브로슈어"), ("poster", "포스터"),
              ("svc-brand", "브랜딩·로고"), ("svc-ppt", "PPT·제안서"),
              ("svc-web", "홈페이지·웹"), ("svc-studio", "촬영·스튜디오"),
              ("svc-mkt", "마케팅·광고")]

def _cpkey(page):
    return page[:-5] if page.endswith(".html") else page

@app.get("/api/content")
@require
def content_list():
    ov = jload("content", {})
    return jsonify([{"page": pg + ".html", "label": label,
                     "edited": bool(ov.get(pg)), "count": len(ov.get(pg, []))}
                    for pg, label in COPY_PAGES])

@app.post("/api/content/<page>")
@require
def content_save(page):
    """편집모드에서 온 텍스트 치환 목록 [{orig,new}] → 페이지 HTML에 직접 반영(정적, AI읽기)."""
    key = _cpkey(page)
    edits = (request.json or {}).get("edits", [])
    p = _page_file(page)
    if not p.exists():
        return jsonify({"error": "페이지 없음"}), 400
    s = p.read_text(encoding="utf-8")
    ovall = jload("content", {})
    ov = ovall.get(key, [])
    applied = 0

    def _clean(h):
        """편집기 표식 제거 + contenteditable이 넣는 <div>줄바꿈을 <br>로 정규화.
        (표식이 정적 파일에 구워지고 <p> 안에 <div>가 들어가 마크업이 깨지던 문제 방지)"""
        h = re.sub(r'\s*data-ce="1"', "", h)
        h = re.sub(r'\s*data-orig="[^"]*"', "", h)
        h = re.sub(r'\s*contenteditable="(?:true|false)"', "", h)
        h = re.sub(r"<div[^>]*>", "<br>", h).replace("</div>", "")
        return h

    def _pattern(o):
        """브라우저 innerHTML과 파일 원문의 사소한 표기 차이를 흡수하는 매칭 패턴.
        (&↔&amp;, <br/>↔<br>, 따옴표 " ↔ ', 공백·줄바꿈 차이로 저장이 실패하던 문제)"""
        out = []
        for part in re.split(r"(\s+)", o):
            if not part:
                continue
            if not part.strip():
                out.append(r"\s+"); continue
            q = re.escape(part)
            q = q.replace(r"\&amp;", "\x00").replace(r"\&", "&").replace("\x00", "&(?:amp;)?")
            q = q.replace('"', "[\"']").replace(">", r"\s*/?>")
            out.append(q)
        return "".join(out)

    skipped = []
    for e in edits:
        orig, new = _clean(e.get("orig", "")), _clean(e.get("new", ""))
        if not orig or orig == new:
            continue
        # 태그 포함(outerHTML) 우선 매칭 — 같은 문구가 alt 속성 등 앞쪽에 있어도 정확한 위치에만 적용
        oo, no = _clean(e.get("origOuter", "")), _clean(e.get("newOuter", ""))
        done = False
        for a, b in ((oo, no), (orig, new)):
            if not a:
                continue
            if a in s:
                s = s.replace(a, b, 1); done = True; break
            m = re.search(_pattern(a), s)
            if m:
                s = s[:m.start()] + b + s[m.end():]; done = True; break
        if not done:
            # 예전엔 조용히 건너뛰어 "저장됐다"고 착각하게 됐음 → 사용자에게 알림
            skipped.append(re.sub(r"<[^>]+>", " ", orig).strip()[:40])
            continue
        # 기존 오버라이드 중 new==orig(재편집)면 갱신, 아니면 추가 (원본 보존)
        merged = False
        for o in ov:
            if o["new"] == orig:
                o["new"] = new; merged = True; break
        if not merged:
            ov.append({"orig": orig, "new": new})
        applied += 1
    p.write_text(s, encoding="utf-8")
    ovall[key] = ov
    jsave("content", ovall)
    return jsonify({"ok": True, "count": applied, "skipped": skipped})

@app.delete("/api/content/<page>")
@require
def content_reset(page):
    key = _cpkey(page)
    p = _page_file(page)
    ovall = jload("content", {})
    ov = ovall.get(key, [])
    if p.exists() and ov:
        s = p.read_text(encoding="utf-8")
        for o in reversed(ov):   # new → orig 복원
            s = s.replace(o["new"], o["orig"], 1)
        p.write_text(s, encoding="utf-8")
    ovall.pop(key, None)
    jsave("content", ovall)
    return jsonify({"ok": True})

# ---------- 칼럼(블로그) CRUD + 굽기(Article 구조화데이터) ----------
@app.get("/api/columns")
@require
def col_list():
    return jsonify(sorted(jload("columns", []), key=lambda c: c.get("date", ""), reverse=True))

@app.post("/api/columns")
@require
def col_add():
    d = request.json or {}
    cols = jload("columns", [])
    nid = max([c["id"] for c in cols], default=0) + 1
    cols.append({"id": nid, "title": d.get("title", ""), "category": d.get("category", "Column"),
                 "excerpt": d.get("excerpt", ""), "body": d.get("body", ""),
                 "thumbnail": d.get("thumbnail", ""), "status": d.get("status", "published"),
                 "date": __import__("datetime").date.today().isoformat()})
    jsave("columns", cols)
    bake.bake_columns()
    return jsonify({"ok": True, "id": nid})

@app.patch("/api/columns/<int:cid>")
@require
def col_edit(cid):
    d = request.json or {}
    cols = jload("columns", [])
    for c in cols:
        if c["id"] == cid:
            for k in ("title", "category", "excerpt", "body", "thumbnail", "status"):
                if k in d:
                    c[k] = d[k]
    jsave("columns", cols)
    bake.bake_columns()
    return jsonify({"ok": True})

@app.delete("/api/columns/<int:cid>")
@require
def col_del(cid):
    cols = [c for c in jload("columns", []) if c["id"] != cid]
    jsave("columns", cols)
    # 삭제된 글 파일 제거
    f = ROOT / f"col-{cid}.html"
    if f.exists():
        f.unlink()
    bake.bake_columns()
    return jsonify({"ok": True})

# ---------- 히어로 (홈 bw-slide 굽기) ----------
@app.get("/api/hero")
@require
def hero_get():
    bake.seed_hero()
    return jsonify(jload("hero", []))

@app.route("/api/hero", methods=["PUT", "POST"])
@require
def hero_put():
    slides = (request.json or {}).get("slides", [])
    jsave("hero", slides)
    bake.bake_hero()
    return jsonify({"ok": True, "count": len(slides)})

# ---------- SEO (페이지별 head 메타 굽기) ----------
@app.get("/api/seo")
@require
def seo_list():
    ov = jload("seo_overrides", {})
    out = []
    for pg, label in bake.SEO_PAGES:
        cur = bake.read_meta(pg)
        if cur is None:
            continue
        o = ov.get(pg, {})
        out.append({"page": pg, "label": label,
                    "title": o.get("title", cur["title"]),
                    "description": o.get("description", cur["description"]),
                    "keywords": o.get("keywords", cur["keywords"]),
                    "overridden": pg in ov})
    return jsonify(out)

@app.route("/api/seo/<page>", methods=["PATCH", "PUT"])
@require
def seo_save(page):
    if page not in dict(bake.SEO_PAGES):
        return jsonify({"error": "알 수 없는 페이지"}), 400
    d = request.json or {}
    meta = {k: d.get(k, "") for k in ("title", "description", "keywords")}
    ov = jload("seo_overrides", {})
    ov[page] = meta
    jsave("seo_overrides", ov)
    bake.bake_seo(page, meta)
    return jsonify({"ok": True})
json_tab("settings", {"phone": "1600-9487", "email": "work@firstmkt.co.kr"})

# ---------- FAQ (완전 동작 + 굽기 + FAQPage 구조화데이터) ----------
@app.get("/api/faq")
@require
def faq_pages():
    extra = jload("faq_extra", {})
    return jsonify([{"page": pg, "label": label, "count": len(extra.get(pg, []))}
                    for pg, label in bake.FAQ_PAGES])

@app.get("/api/faq/<page>")
@require
def faq_get(page):
    store = jload("faq_extra", {})
    if page in store:                       # 관리자가 이미 편집·저장한 전체 목록
        return jsonify(store[page])
    # 처음 열 때: 페이지의 기존 기본 FAQ를 불러와 보여줌(편집 가능)
    p = _page_file(page)
    if p.exists():
        defaults = bake._extract_default_faq(p.read_text(encoding="utf-8"))
        return jsonify([{"q": q, "a": a} for q, a in defaults])
    return jsonify([])

@app.put("/api/faq/<page>")
@require
def faq_put(page):
    if page not in bake.FAQ_LABELS:
        return jsonify({"error": "알 수 없는 페이지"}), 400
    items = [{"q": x.get("q", "").strip(), "a": x.get("a", "").strip()}
             for x in (request.json or {}).get("items", []) if x.get("q") and x.get("a")]
    extra = jload("faq_extra", {})
    extra[page] = items
    jsave("faq_extra", extra)
    n, total = bake.bake_faq(page)
    return jsonify({"ok": True, "count": n, "total": total})

@app.get("/api/inquiries")
@require
def inq_list():
    return jsonify(sorted(jload("inquiries", []), key=lambda x: -x.get("ts", 0)))

@app.delete("/api/inquiries/<int:iid>")
@require
def inq_del(iid):
    jsave("inquiries", [x for x in jload("inquiries", []) if x.get("id") != iid])
    return jsonify({"ok": True})

@app.post("/api/inquiries")   # 공개: 문의폼에서 저장 (인증 불필요)
def inq_add():
    d = request.json or {}
    items = jload("inquiries", [])
    d["id"] = int(time.time() * 1000) % 2000000000
    d["ts"] = time.time()
    d["status"] = "new"
    items.append(d)
    jsave("inquiries", items)
    return jsonify({"ok": True})

# ---------- 정적: 관리자 UI + 사이트 프리뷰(썸네일용) ----------
@app.get("/admin")
@app.get("/admin/")
def admin_home():
    return send_from_directory(UI, "index.html")

@app.get("/admin/<path:f>")
def admin_asset(f):
    return send_from_directory(UI, f)

@app.get("/")
def root():
    return redirect("/admin")

EDIT_JS = """
<style>
#__cebar{position:fixed;left:0;right:0;bottom:0;background:#0f1f1c;color:#fff;padding:12px 20px;
 display:flex;gap:12px;align-items:center;z-index:99999;font-family:Pretendard,sans-serif;box-shadow:0 -6px 24px rgba(0,0,0,.3)}
#__cebar b{color:#2fd0bd}
#__cebar .sp{flex:1}
#__cebar button{font:inherit;font-weight:700;border:none;border-radius:8px;padding:9px 18px;cursor:pointer}
#__cesave{background:#0C9384;color:#fff}#__ceclose{background:#2a2c26;color:#cfd3c8}
[data-ce]:hover{outline:2px dashed #0C9384;outline-offset:2px;cursor:text}
[data-ce]:focus{outline:2px solid #0C9384;outline-offset:2px;background:#eefaf7}
</style>
<script>
(function(){
  // 자식이 전부 인라인(span/b/br 등)인 '텍스트 잎사귀'를 편집 대상으로 — 강점카드·타이틀·CTA 등 전부 포함
  var INLINE={SPAN:1,B:1,STRONG:1,EM:1,I:1,A:1,BR:1,SUB:1,SUP:1,MARK:1,SMALL:1,U:1,TIME:1,DEL:1,INS:1};
  var SKIP={SCRIPT:1,STYLE:1,SVG:1,BUTTON:1,NAV:1,IMG:1,INPUT:1,SELECT:1,TEXTAREA:1};
  function isLeaf(el){
    if(!el.textContent.trim())return false;
    for(var i=0;i<el.children.length;i++){if(!INLINE[el.children[i].tagName])return false;}
    return true;
  }
  // 사이트 JS가 실시간으로 값을 바꾸는 요소(슬라이더 카운터 등)는 제외 —
  // 편집 당시 화면 상태가 그대로 저장돼 첫 화면이 02/03부터 시작하던 문제 방지
  var LIVE='.bw-count, .bw-count *, .counter, [data-count], .swiper-pagination, .swiper-pagination *';
  var roots=[].slice.call(document.querySelectorAll('main, .cta-section, .cta2, .ct-faq'));
  var set=[];
  roots.forEach(function(root){
    [].slice.call(root.querySelectorAll('*')).forEach(function(el){
      if(SKIP[el.tagName]||el.closest('#__cebar')||el.closest('nav')||el.closest('svg'))return;
      if(el.matches&&el.matches(LIVE))return;
      // svg 아이콘을 품은 요소는 제외 — 브라우저 직렬화가 파일 원문과 달라 저장이 실패하고,
      // 편집 중 아이콘이 깨질 수 있음(버튼 문구 등)
      if(el.querySelector&&el.querySelector('svg'))return;
      if(el.isContentEditable&&el.getAttribute('data-ce'))return;
      // 부모가 이미 텍스트 잎사귀면(=인라인 자식) 제외 → 중첩 편집 방지, 줄 전체만 편집
      if(el.parentElement&&isLeaf(el.parentElement))return;
      if(isLeaf(el)&&set.indexOf(el)<0)set.push(el);
    });
  });
  var els=set;
  els.forEach(function(el){el.setAttribute('data-ce','1');el.setAttribute('data-orig',el.innerHTML);el.setAttribute('contenteditable','true');});
  var bar=document.createElement('div');bar.id='__cebar';
  bar.innerHTML='<b>편집 모드</b> — 글자를 클릭해 수정하세요 <span class="sp"></span>'+
    '<button id="__cesave">저장 · 사이트 반영</button><button id="__ceclose">닫기</button>';
  document.body.appendChild(bar);
  document.getElementById('__ceclose').onclick=function(){location.href=location.pathname;};
  // 사이트 JS(드래그 스크롤 등)가 mousedown에 preventDefault를 걸면 캐럿이 아예 안 잡힘
  // → 편집 대상 위에서는 그 핸들러에 이벤트가 닿기 전에 차단 (강점카드가 편집 안 되던 실제 원인)
  document.addEventListener('mousedown',function(e){
    if(e.target.closest&&e.target.closest('[data-ce]'))e.stopPropagation();
  },true);
  // 링크로 감싼 문구(강점카드 등)는 클릭 시 이동해버려 편집이 안 됨 → 편집모드에선 이동 차단
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a');
    if(a&&!a.closest('#__cebar')){e.preventDefault();
      var ce=e.target.closest('[data-ce]'); if(ce)ce.focus();}
  },true);
  document.getElementById('__cesave').onclick=function(){
    var edits=[];
    // 편집기 표식(data-ce/data-orig/contenteditable)이 자식에 붙어 저장본에 구워지던 문제 → 비교·전송 전 제거
    function clean(h){return h.replace(/\\s*data-ce="1"/g,'').replace(/\\s*data-orig="[^"]*"/g,'')
                             .replace(/\\s*contenteditable="(?:true|false)"/g,'');}
    els.forEach(function(el){
      var o=clean(el.getAttribute('data-orig')),n=clean(el.innerHTML);
      if(o===n)return;
      // 문구만 보내면 같은 문자열이 이미지 alt 등 앞쪽에 있을 때 엉뚱한 곳이 바뀜
      // → 태그까지 포함한 outerHTML을 함께 보내 위치를 특정
      var newOuter=clean(el.outerHTML), origOuter=newOuter.replace(n,o);
      edits.push({orig:o,new:n,origOuter:origOuter,newOuter:newOuter});
    });
    if(!edits.length){alert('변경된 문구가 없습니다.');return;}
    var page=location.pathname.replace(/^\\//,'')||'index.html';
    fetch('/api/content/'+encodeURIComponent(page),{method:'POST',credentials:'same-origin',
      headers:{'Content-Type':'application/json'},body:JSON.stringify({edits:edits})})
      .then(function(r){
        if(r.status===401){throw new Error('로그인이 풀렸습니다. 관리자에 다시 로그인한 뒤 저장하세요.');}
        return r.json();}).then(function(r){
        if(!r.ok){alert(r.error||'저장 실패');return;}
        if(r.skipped&&r.skipped.length){
          // 실패분이 있으면 페이지를 새로고침하지 않음 → 수정 내용이 화면에 남아 다시 저장 가능
          alert(r.count+'곳 저장됨.\\n\\n⚠️ 아래 '+r.skipped.length+'곳은 반영되지 않았습니다:\\n· '
                +r.skipped.join('\\n· ')+'\\n\\n화면의 수정 내용은 유지됩니다. 다시 [저장]을 눌러보시고,'
                +' 계속 실패하면 담당자에게 알려주세요.');
          return;
        }
        alert(r.count+'곳 저장·반영되었습니다.');location.reload();})
      .catch(function(err){
        // 예전엔 서버가 꺼져 있으면 아무 반응 없이 조용히 실패했음
        alert('저장하지 못했습니다: '+(err&&err.message||err)+'\\n\\n수정 내용은 화면에 그대로 있으니'
              +' 창을 닫지 마시고, 문제 해결 후 다시 [저장]을 눌러주세요.');});
  };
})();
</script>
"""

@app.get("/<path:f>")
def site_asset(f):
    # 사이트 파일 서빙. ?edit=1 이면 카피 편집모드 스크립트 주입.
    if not (ROOT / f).exists():
        return ("not found", 404)
    if request.args.get("edit") == "1" and f.endswith(".html") and session.get("uid"):
        html = (ROOT / f).read_text(encoding="utf-8")
        html = html.replace("</body>", EDIT_JS + "</body>", 1)
        return html
    return send_from_directory(ROOT, f)

if __name__ == "__main__":
    auth_cfg()
    print("관리자: http://localhost:5701/admin  (초기 비번 admin1234)")
    app.run(host="127.0.0.1", port=5701, debug=False)
