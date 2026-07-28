# -*- coding: utf-8 -*-
"""CI4 패키지 데이터 동기화 (2026-07-28 사용자 "php 8.2 (CI4) / mysql 5.6 이걸로 적용해줘").

로컬 Flask 관리자의 JSON 데이터를 서버용 SQL(seed)로 변환한다.
MySQL 5.6 기준: JSON 타입·생성컬럼 미사용, utf8mb4, 문자열은 이스케이프 처리.
대상: columns(칼럼 4글) / settings(연락처·파비콘 등) / content_overrides(카피 수정분)
      / seo_overrides(페이지별 메타) / faq_extra(있으면)"""
import json, pathlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

R = pathlib.Path(__file__).parent
D = R / 'admin' / 'data'
OUT = R / 'ci4-admin' / 'sql' / 'seed_data_2026-07-28.sql'

def esc(v):
    """MySQL 문자열 이스케이프 (5.6 기본 모드 기준)"""
    if v is None:
        return 'NULL'
    s = str(v)
    s = s.replace('\\', '\\\\').replace("'", "\\'").replace('\r', '').replace('\n', '\\n')
    return "'" + s + "'"

def jload(name, default):
    p = D / f'{name}.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default

lines = ["-- 2026-07-28 데이터 시드 (로컬 관리자 JSON → MySQL 5.6)",
         "-- 주의: 재실행 시 중복 방지를 위해 해당 테이블을 먼저 비웁니다.",
         "SET NAMES utf8mb4;", ""]

# ① 칼럼 4글
cols = jload('columns', [])
if cols:
    lines.append("TRUNCATE TABLE `columns`;")
    for c in cols:
        lines.append(
            "INSERT INTO `columns` (`id`,`title`,`category`,`excerpt`,`body`,`thumbnail`,"
            "`status`,`date`,`file`,`builtin`) VALUES ("
            f"{int(c['id'])},{esc(c['title'])},{esc(c.get('category','Column'))},"
            f"{esc(c.get('excerpt',''))},{esc(c.get('body',''))},{esc(c.get('thumbnail',''))},"
            f"{esc(c.get('status','published'))},{esc(c.get('date','2026-07-20'))},"
            f"{esc(c.get('file'))},{1 if c.get('builtin') else 0});")
    lines.append("")

# ② 사이트 설정
st = jload('settings', {})
if st:
    lines.append("-- 사이트 설정 (연락처·파비콘·대표이미지 등)")
    for k, v in st.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        lines.append("INSERT INTO `settings` (`k`,`v`) VALUES "
                     f"({esc(k)},{esc(v)}) ON DUPLICATE KEY UPDATE `v`=VALUES(`v`);")
    lines.append("")

# ③ 카피 수정분
ov = jload('content', {})
if ov:
    lines.append("-- 카피(문구) 수정분")
    lines.append("TRUNCATE TABLE `content_overrides`;")
    for page, edits in ov.items():
        for e in edits:
            lines.append("INSERT INTO `content_overrides` (`page`,`orig`,`new`) VALUES ("
                         f"{esc(page)},{esc(e.get('orig',''))},{esc(e.get('new',''))});")
    lines.append("")

# ④ 페이지별 SEO
seo = jload('seo_overrides', {})
if seo:
    lines.append("-- 페이지별 SEO 메타")
    lines.append("TRUNCATE TABLE `seo_overrides`;")
    for page, m in seo.items():
        lines.append("INSERT INTO `seo_overrides` (`page`,`title`,`description`,`keywords`) VALUES ("
                     f"{esc(page)},{esc(m.get('title',''))},{esc(m.get('description',''))},"
                     f"{esc(m.get('keywords',''))});")
    lines.append("")

# ⑤ FAQ 편집분
fq = jload('faq_extra', {})
if fq:
    lines.append("-- FAQ 편집분")
    lines.append("TRUNCATE TABLE `faq`;")
    for page, items in fq.items():
        for i, it in enumerate(items):
            lines.append("INSERT INTO `faq` (`page`,`q`,`a`,`sort_order`) VALUES ("
                         f"{esc(page)},{esc(it.get('q',''))},{esc(it.get('a',''))},{i});")
    lines.append("")

OUT.write_text("\n".join(lines) + "\n", encoding='utf-8')
print(f"생성: {OUT.relative_to(R).as_posix()}")
print(f"  칼럼 {len(cols)}건 / 설정 {len(st)}건 / 카피 {sum(len(v) for v in ov.values())}건"
      f" / SEO {len(seo)}건 / FAQ {sum(len(v) for v in fq.values())}건")
print(f"  용량 {OUT.stat().st_size/1024:.0f}KB")
