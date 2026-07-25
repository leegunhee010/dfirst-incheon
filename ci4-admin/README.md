# 퍼스트디자인 인천지사 — 관리자 백엔드 (CodeIgniter 4 + MySQL 5.6)

정적 사이트(`incheondesign.co.kr`)의 관리자를 **PHP 8.2 / CI4 / MySQL 5.6** 서버에서 돌리는 패키지입니다.
기존 Flask(Python) 관리자를 **화면·기능 그대로** PHP로 이관 → 파이썬 없이 사장님 서버에서 동작하고,
**편집·저장하면 정적 HTML에 직접 반영**되어 검색·AI가 그대로 읽습니다(JS 렌더 0).

---

## 0. 구조

```
서버 웹루트(public/)
├─ index.html, about.html, catalog.html ... (정적 사이트 — 웹서버가 직접 서빙)
├─ col-*.html (관리자가 발행한 블로그 글)
├─ sitemap.xml / robots.txt / rss.xml
├─ theme/assets/... (CSS·이미지)
└─ admin/  (관리자 UI: index.html, admin.js, admin.css)

CI4 앱(app/)
├─ Controllers/Api.php     ← /api/* 전부 처리 + /admin, /editmode
├─ Libraries/Bake.php      ← 저장 시 정적 HTML 굽기(핵심)
└─ Config/Routes.php       ← 라우트

MySQL
└─ 11개 테이블 (sql/schema.sql)
```

- **사이트 화면** = public/ 정적 HTML (웹서버 직접 서빙, 서버부하 0)
- **관리자** = CI4가 `/admin` + `/api/*` 처리
- **저장** = CI4 Api → Bake가 public/ 의 해당 HTML을 직접 수정 → 즉시 라이브 반영

---

## 1. 설치 (개발자용, 30분)

### ① DB
```sql
CREATE DATABASE firstd_incheon DEFAULT CHARSET utf8mb4;
```
```bash
mysql firstd_incheon < sql/schema.sql   # 테이블 11개
mysql firstd_incheon < sql/seed.sql      # 현재 데이터(포폴 450·히어로 3·설정 등) + 관리자 계정
```
기본 관리자: **admin / admin1234** — 로그인 후 계정 탭에서 반드시 변경.

### ② CI4 앱 병합
- `app/Controllers/Api.php`, `app/Libraries/Bake.php` → 기존 CI4 프로젝트에 복사
- `app/Config/Routes.php` 의 라우트 블록을 기존 Routes.php `$routes` 정의부에 **병합**
- `app/Config/Database.sample.php` 참고해 실제 `Database.php` 의 `$default` 채우기

### ③ 사이트 파일 배치
- `dfirst-incheon` 저장소의 정적 사이트(*.html, theme/, sitemap.xml 등)를 **public/** 에 복사
- 관리자 UI 3파일을 **public/admin/** 에 복사 (index.html, admin.js, admin.css)
  - ※ admin.js 는 이 패키지 버전 사용(카피 편집 URL이 `/editmode/` 로 패치됨)

### ④ 세션·권한
- CI4 세션 기본(파일 핸들러) 사용 — 별도 설정 불필요
- public/, theme/assets/, col-*.html 에 **웹서버 쓰기 권한**(www-data) 필요 (저장이 파일을 씀)

### ⑤ 도메인
- 관리자에서 **SEO → 사이트 설정 → 도메인** 을 `https://incheondesign.co.kr` 로 확인/저장
- 확인: `https://incheondesign.co.kr/admin` 접속 → 로그인 → 각 탭 동작

---

## 2. API 대응표 (Flask → CI4, 프론트 무수정)

admin.js 가 부르는 경로 그대로 CI4가 응답합니다. 프론트는 **admin.js 1줄(카피 편집 URL)만** 이 패키지 버전으로 교체됨(이미 반영).

| 기능 | 경로 |
|---|---|
| 로그인/세션 | `POST /api/login`, `GET /api/me`, `POST /api/logout` |
| 포트폴리오 | `GET/POST /api/portfolio`, `DELETE /api/portfolio/{id}` |
| 히어로 | `GET/PUT /api/hero` |
| FAQ | `GET /api/faq`, `GET/PUT /api/faq/{page}` |
| 칼럼 | `GET/POST /api/columns`, `PATCH/DELETE /api/columns/{id}` |
| 카피 | `GET /api/content`, `POST/DELETE /api/content/{page}`, `GET /editmode/{page}` |
| SEO | `GET /api/seo`, `PATCH /api/seo/{page}` |
| 설정 | `GET/PATCH /api/settings`, `POST /api/settings/favicon|ogimage` |
| 이미지 | `POST /api/upload`, `GET/POST/DELETE /api/images/{page}` |
| 계정 | `GET/POST /api/admins`, `DELETE /api/admins/{user}` |
| 문의 | `POST /api/inquiries`(공개), `GET/DELETE`(관리자) |

---

## 3. 문의 폼 연결 (중요)

정적 사이트의 문의 폼(`contact.html`)은 현재 **mailto** 입니다. 관리자 "견적 문의" 탭에 쌓이게 하려면
폼 제출을 `POST /api/inquiries` 로 보내도록 연결하세요(JSON: `{company,name,phone,email,field,message}`).
→ 연결하면 대시보드·문의 탭에 실시간으로 접수됩니다.

---

## 4. 참고

- 편집 결과는 **정적 HTML 파일에 직접** 쓰입니다(DB는 원본 데이터 보관용). 그래서 검색·AI가 소스를 그대로 읽음.
- 이미지 리사이즈는 GD(`imagecreate*`) 사용 — PHP GD 확장 필요(대개 기본 탑재).
- Flask 원본(참고용): `dfirst-incheon/admin/` (server.py = Api.php, bake*.py = Bake.php 대응).
