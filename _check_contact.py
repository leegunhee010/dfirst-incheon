# -*- coding: utf-8 -*-
"""연락처·회사정보 일관성 점검 (2026-07-28 사용자 "이메일도 다르잖아 다 체크해야지 전화번호 이런거").
전 페이지에서 이메일·전화·주소·운영시간·상호·대표자·사업자번호를 뽑아
기준값과 다르거나 페이지마다 다른 곳을 찾아낸다."""
import re, pathlib, io, sys
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

R = pathlib.Path(__file__).parent
EXPECT = {
    "이메일":   "work@firstmkt.co.kr",
    "전화":     "1600-9487",
    "주소":     "인천광역시 남동구 미래로 16 3층",
    "상호":     "퍼스트디자인 인천지사(㈜퍼스트마케팅컴퍼니)",
    "대표자":   "김우석",
    "사업자번호": "884-88-01123",
    "운영시간": "평일 09:00 ~ 18:00",
}
PAT = {
    "이메일":   r"[\w.\-]+@[\w.\-]+\.\w+",
    "전화":     r"1[56]00[-\s]?\d{4}|0\d{1,2}-\d{3,4}-\d{4}",
    "주소":     r"소재지\s*:\s*([^|<]+)",
    "상호":     r"상호\s*:\s*([^|<]+)",
    "대표자":   r"대표자\s*:\s*([^|<]+)",
    "사업자번호": r"사업자\s*번호\s*:\s*([^|<]+)",
    "운영시간": r"상담 가능 시간\s*:\s*([^<]+)",
}
found = defaultdict(lambda: defaultdict(set))   # 항목 → 값 → {페이지}
for f in sorted(R.glob("*.html")):
    t = f.read_text(encoding="utf-8")
    body = re.sub(r"<script.*?</script>", "", t, flags=re.S)   # 스키마 제외(별도 확인)
    for key, pat in PAT.items():
        for m in re.finditer(pat, body):
            val = (m.group(1) if m.groups() else m.group(0)).strip()
            val = re.sub(r"\s+", " ", val).replace("&nbsp;", "").strip()
            if val:
                found[key][val].add(f.name)

bad = 0
for key, expect in EXPECT.items():
    vals = found.get(key, {})
    if not vals:
        print(f"⚠️ {key}: 어느 페이지에서도 찾지 못함"); bad += 1; continue
    for val, pages in sorted(vals.items(), key=lambda x: -len(x[1])):
        ok = (val == expect)
        mark = "OK " if ok else "❌ "
        if not ok: bad += 1
        print(f"{mark}{key:6s} [{len(pages):2d}p] {val[:58]}")
        if not ok:
            print(f"        기대값: {expect}")
            print(f"        해당: {', '.join(sorted(pages)[:6])}{' …' if len(pages) > 6 else ''}")

# 구조화 데이터(LocalBusiness)도 확인
print("\n--- 구조화 데이터 ---")
import json
sch = defaultdict(set)
for f in sorted(R.glob("*.html")):
    t = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: d = json.loads(m.group(1))
        except Exception: continue
        if isinstance(d, dict) and d.get("@type") == "LocalBusiness":
            hrs = d.get("openingHoursSpecification", [{}])[0]
            sch[(d.get("telephone"), d.get("email"),
                 hrs.get("opens"), hrs.get("closes"))].add(f.name)
for (tel, mail, op, cl), pages in sch.items():
    print(f"   전화 {tel} / 이메일 {mail} / {op}~{cl}  ({len(pages)}p)")

print(f"\n{'문제 없음' if bad == 0 else f'불일치 {bad}건'}")
