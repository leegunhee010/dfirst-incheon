# -*- coding: utf-8 -*-
"""SEO / GEO / AEO 점수 산출 + 항목별 진단.
SEO = 검색엔진 기본기(메타·구조·인덱싱)  GEO = 지역 검색(로컬 비즈니스)
AEO = 답변엔진(AI·음성 검색이 인용하기 좋은 구조)
사용: python _score_seo.py [페이지명]   (인자 없으면 전 페이지)"""
import re, json, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

R = pathlib.Path(__file__).parent
SITEMAP = (R / 'sitemap.xml').read_text(encoding='utf-8') if (R / 'sitemap.xml').exists() else ''

def lds(t):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: out.append(json.loads(m.group(1)))
        except Exception: out.append(None)
    return out

def evaluate(f):
    t = f.read_text(encoding='utf-8')
    bm = re.search(r'<main class="site-main">(.*?)</main>', t, re.S)
    body = bm.group(1) if bm else t
    text = re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>', '', body, flags=re.S))
    chars = len(re.sub(r'\s+', '', text))
    ld = lds(t)
    types = str([d.get('@type') for d in ld if isinstance(d, dict)])
    lb = next((d for d in ld if isinstance(d, dict) and d.get('@type') == 'LocalBusiness'), None)
    ti = re.search(r'<title>(.*?)</title>', t, re.S)
    de = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = ti.group(1).strip() if ti else ''
    desc = de.group(1).strip() if de else ''
    h1 = len(re.findall(r'<h1[\s>]', t))
    h2 = len(re.findall(r'<h2[\s>]', body)); h3 = len(re.findall(r'<h3[\s>]', body))
    imgs = re.findall(r'<img [^>]*>', body)
    noalt = [i for i in imgs if 'alt=' not in i]
    faq = len(re.findall(r'<details', body)) + len(re.findall(r'faq-item', body))
    inmap = f.name in SITEMAP or (f.name == 'index.html' and 'incheondesign.co.kr/<' in SITEMAP.replace('</loc>', '<'))

    seo = [
        ('타이틀 길이(10~70자)', 10 if 10 <= len(title) <= 70 else 0, f'{len(title)}자'),
        ('설명문 길이(40~170자)', 10 if 40 <= len(desc) <= 170 else (5 if desc else 0), f'{len(desc)}자'),
        ('canonical', 10 if 'rel="canonical"' in t else 0, ''),
        ('OG 제목·설명', 10 if 'og:title' in t and 'og:description' in t else 0, ''),
        ('OG 대표이미지', 10 if 'og:image' in t else 0, ''),
        ('keywords', 10 if 'name="keywords"' in t else 0, ''),
        ('H1 정확히 1개', 10 if h1 == 1 else (5 if h1 > 1 else 0), f'{h1}개'),
        ('이미지 alt', 10 if not imgs or not noalt else (7 if len(noalt) / len(imgs) < .2 else 0),
         f'{len(imgs)}장 중 누락 {len(noalt)}'),
        ('사이트맵 등록', 10 if inmap else 0, ''),
        ('본문 분량(500자+)', 10 if chars > 500 else 5, f'{chars}자'),
    ]
    geo = [
        ('LocalBusiness 스키마', 20 if lb else 0, ''),
        ('주소·좌표·영업시간', 20 if lb and lb.get('address') and lb.get('geo')
         and lb.get('openingHoursSpecification') else 0, ''),
        ('제목·설명에 지역명', 20 if '인천' in title + desc else 0, ''),
        ('본문 지역명 2회+', 20 if text.count('인천') >= 2 else (10 if '인천' in text else 0),
         f"{text.count('인천')}회"),
        ('상세주소 노출', 20 if '미래로 16' in t else 0, ''),
    ]
    aeo = [
        ('FAQ 구조화데이터', 20 if 'FAQPage' in types else 0, ''),
        ('브레드크럼', 20 if 'BreadcrumbList' in types else 0, ''),
        ('질문·답변 블록', 20 if faq >= 4 else (10 if faq else 0), f'{faq}개'),
        ('소제목 위계(H2·H3)', 20 if h2 >= 2 and h3 >= 2 else (10 if h2 or h3 else 0), f'H2 {h2} · H3 {h3}'),
        ('콘텐츠 유형 명시', 20 if 'BlogPosting' in types or ('FAQPage' in types and faq)
         else (10 if lb else 0), ''),
    ]
    return seo, geo, aeo, dict(title=title, desc=desc, chars=chars)

def show(f, detail=True):
    seo, geo, aeo, meta = evaluate(f)
    s, g, a = sum(x[1] for x in seo), sum(x[1] for x in geo), sum(x[1] for x in aeo)
    print(f"\n{'='*58}\n {f.name}   SEO {s} / GEO {g} / AEO {a}\n{'='*58}")
    if detail:
        for label, items in (('SEO', seo), ('GEO', geo), ('AEO', aeo)):
            print(f"[{label}]")
            for name, sc, note in items:
                full = 10 if label == 'SEO' else 20
                mark = '○' if sc == full else ('△' if sc else '✕')
                print(f"  {mark} {name:22s} {sc:2d}/{full}  {note}")
    return s, g, a

if __name__ == '__main__':
    if len(sys.argv) > 1:
        show(R / sys.argv[1])
    else:
        order = ['index.html'] + sorted(p.name for p in R.glob('*.html') if p.name != 'index.html')
        rows = []
        for n in order:
            seo, geo, aeo, _ = evaluate(R / n)
            rows.append((n, sum(x[1] for x in seo), sum(x[1] for x in geo), sum(x[1] for x in aeo)))
        print(f"{'페이지':24s} SEO GEO AEO")
        for n, s, g, a in rows:
            print(f"{n:26s} {s:3d} {g:3d} {a:3d}")
        print(f"\n평균  SEO {round(sum(r[1] for r in rows)/len(rows))}"
              f" / GEO {round(sum(r[2] for r in rows)/len(rows))}"
              f" / AEO {round(sum(r[3] for r in rows)/len(rows))}")
