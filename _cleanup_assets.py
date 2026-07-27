# -*- coding: utf-8 -*-
"""미사용 이미지 정리 (2026-07-28 전체 점검 — 미러링 잔재 등 안 쓰는 이미지가 65MB 쌓여 있었음).
보수적으로: 경로 참조 + 파일명 참조 둘 다 살펴 하나라도 걸리면 보존.
사용법:  python _cleanup_assets.py          → 목록만 출력(삭제 안 함)
         python _cleanup_assets.py --delete → 실제 삭제"""
import re, sys, json, pathlib
from collections import Counter

R = pathlib.Path(__file__).parent
EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.ico')
PATH_RE = re.compile(r"theme/assets/[^\s\"')\\]+\.(?:jpg|jpeg|png|webp|gif|svg|ico)", re.I)
NAME_RE = re.compile(r"([\w.\-]+\.(?:jpg|jpeg|png|webp|gif|svg|ico))", re.I)

targets = (list(R.glob('*.html')) + list((R / 'theme').rglob('*.js')) + list((R / 'theme').rglob('*.css'))
           + list((R / 'admin').rglob('*.py')) + list((R / 'admin').rglob('*.js'))
           + list((R / 'admin').rglob('*.json')) + list((R / 'admin').rglob('*.html'))
           + list(R.glob('_*.py')) + list(R.glob('*.json')) + list(R.glob('*.xml')))
# 자기 자신(이 스크립트가 만든 미사용 목록)을 읽으면 전부 "사용 중"으로 잘못 판정됨
targets = [f for f in targets if f.name != '_unused.json']
used = set()
for f in targets:
    try:
        t = f.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    used.update(m.group(0) for m in PATH_RE.finditer(t))
    used.update(m.group(1) for m in NAME_RE.finditer(t))   # 파일명만 쓰는 참조도 보존

allimg = [p for p in (R / 'theme' / 'assets').rglob('*') if p.suffix.lower() in EXTS]
unused = [p for p in allimg
          if p.relative_to(R).as_posix() not in used and p.name not in used]

size = sum(p.stat().st_size for p in unused)
print(f"전체 {len(allimg)}개 / 미사용 {len(unused)}개 / {size / 1048576:.0f}MB")
print("폴더별:", dict(Counter(p.parent.relative_to(R).as_posix() for p in unused)))
print("상위 5:")
for p in sorted(unused, key=lambda x: -x.stat().st_size)[:5]:
    print(f"  {p.stat().st_size / 1048576:5.1f}MB  {p.relative_to(R).as_posix()}")

if '--delete' in sys.argv:
    for p in unused:
        p.unlink()
    print(f"\n삭제 완료: {len(unused)}개 / {size / 1048576:.0f}MB 확보")
else:
    json.dump([p.relative_to(R).as_posix() for p in unused],
              open(R / '_unused.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("\n(목록만 출력, 삭제하려면 --delete)")
