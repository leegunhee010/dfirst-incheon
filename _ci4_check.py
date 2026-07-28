# -*- coding: utf-8 -*-
"""CI4 패키지 SQL 검증 — MySQL 5.6 호환성·인덱스 길이·따옴표 균형."""
import re, pathlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SQLDIR = pathlib.Path(__file__).parent / 'ci4-admin' / 'sql'
STR_LIT = re.compile(r"'(?:[^'\\]|\\.)*'")
BAD = [
    (re.compile(r"`\w+`\s+JSON\b", re.I), "JSON 컬럼 타입(5.7+)"),
    (re.compile(r"GENERATED\s+ALWAYS", re.I), "생성 컬럼(5.7+)"),
    (re.compile(r"utf8mb4_0900", re.I), "MySQL 8.0 콜레이션"),
    (re.compile(r"DEFAULT\s*\(", re.I), "표현식 DEFAULT(8.0+)"),
    (re.compile(r"\bROW_NUMBER\s*\(|\bWITH\s+\w+\s+AS\s*\(", re.I), "윈도우 함수·CTE(8.0+)"),
]

problems = []
for p in sorted(SQLDIR.glob('*.sql')):
    t = p.read_text(encoding='utf-8')
    code = STR_LIT.sub("''", re.sub(r"--[^\n]*", "", t))   # 주석·문자열 제외
    for rx, why in BAD:
        if rx.search(code):
            problems.append(f"{p.name}: {why}")
    # 따옴표 균형 — 문자열 안에 줄바꿈이 들어갈 수 있어 '줄'이 아니라 '구문' 단위로 검사
    for stmt in re.split(r";\s*\n", t):
        s = stmt.strip()
        if not s.upper().startswith(('INSERT', 'ALTER', 'CREATE', 'TRUNCATE')):
            continue
        if s.replace("\\'", '').count("'") % 2:
            problems.append(f"{p.name}: 따옴표 불균형 → {s[:60]}")
    stmts = len([s for s in code.split(';') if s.strip()])
    print(f"{p.name:32s} 구문 {stmts:4d}개  {p.stat().st_size/1024:6.0f}KB")

# utf8mb4에서 인덱스 키 길이 767byte 초과 여부 (5.6 기본 설정)
schema = (SQLDIR / 'schema.sql').read_text(encoding='utf-8')
sizes = {m.group(1): int(m.group(2)) for m in re.finditer(r"`(\w+)`\s+VARCHAR\((\d+)\)", schema)}
keycols = set()
for k in re.findall(r"(?:UNIQUE KEY|PRIMARY KEY|KEY)[^(]*\(([^)]+)\)", schema):
    for c in k.split(','):
        keycols.add(c.strip().strip('`'))
over = {c: n for c, n in sizes.items() if c in keycols and n * 4 > 767}
print()
print("MySQL 5.6 비호환 문법 :", "없음" if not problems else "")
for x in dict.fromkeys(problems):
    print("   ·", x)
print("인덱스 길이 초과      :", "없음" if not over else over)
print("\n결과:", "PHP 8.2 / MySQL 5.6 환경에서 사용 가능" if not problems and not over else "수정 필요")
