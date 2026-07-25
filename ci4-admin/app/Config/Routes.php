<?php
/**
 * 퍼스트디자인 인천지사 관리자 — 라우트 (CodeIgniter 4)
 * Flask 관리자의 /api/* 를 그대로 CI4로 이관. admin.js 무수정 재사용.
 * ▶ 기존 CI4 프로젝트 app/Config/Routes.php 의 $routes 정의부에 아래 블록 병합.
 */
use CodeIgniter\Router\RouteCollection;
/** @var RouteCollection $routes */

// ── 인증 ──────────────────────────────────────────
$routes->post('api/login',  'Api::login');
$routes->post('api/logout', 'Api::logout');
$routes->get ('api/me',     'Api::me');
$routes->post('api/account/password', 'Api::password');

// ── 대시보드 ──────────────────────────────────────
$routes->get('api/stats', 'Api::stats');

// ── 포트폴리오 ────────────────────────────────────
$routes->get   ('api/portfolio',       'Api::pfList');
$routes->post  ('api/portfolio',       'Api::pfSave');
$routes->delete('api/portfolio/(:num)','Api::pfDelete/$1');

// ── 히어로 ────────────────────────────────────────
$routes->get('api/hero', 'Api::heroGet');
$routes->put('api/hero', 'Api::heroSave');

// ── FAQ ───────────────────────────────────────────
$routes->get('api/faq',            'Api::faqPages');
$routes->get('api/faq/(:segment)', 'Api::faqGet/$1');
$routes->put('api/faq/(:segment)', 'Api::faqSave/$1');

// ── 칼럼(블로그) ──────────────────────────────────
$routes->get   ('api/columns',       'Api::colList');
$routes->post  ('api/columns',       'Api::colAdd');
$routes->patch ('api/columns/(:num)','Api::colEdit/$1');
$routes->delete('api/columns/(:num)','Api::colDelete/$1');

// ── 카피(문구) ────────────────────────────────────
$routes->get   ('api/content',            'Api::contentList');
$routes->post  ('api/content/(:segment)', 'Api::contentSave/$1');
$routes->delete('api/content/(:segment)', 'Api::contentReset/$1');

// ── SEO ───────────────────────────────────────────
$routes->get  ('api/seo',            'Api::seoList');
$routes->patch('api/seo/(:segment)', 'Api::seoSave/$1');
$routes->put  ('api/seo/(:segment)', 'Api::seoSave/$1');

// ── 설정(도메인·Head코드·파비콘·대표이미지·메일) ──
$routes->get  ('api/settings',          'Api::settingsGet');
$routes->patch('api/settings',          'Api::settingsSave');
$routes->put  ('api/settings',          'Api::settingsSave');
$routes->post ('api/settings/favicon',  'Api::settingsFavicon');
$routes->post ('api/settings/ogimage',  'Api::settingsOgimage');
$routes->post ('api/settings/test-mail','Api::settingsTestMail');

// ── 이미지 (라이브러리·페이지별 교체) ──────────────
$routes->post  ('api/upload',            'Api::upload');
$routes->get   ('api/images',            'Api::imageLibrary');
$routes->get   ('api/images/(:segment)', 'Api::imagesPage/$1');
$routes->post  ('api/images/(:segment)', 'Api::imagesReplace/$1');
$routes->delete('api/images/(:segment)', 'Api::imagesRevert/$1');

// ── 계정 ──────────────────────────────────────────
$routes->get   ('api/admins',            'Api::adminsList');
$routes->post  ('api/admins',            'Api::adminsAdd');
$routes->delete('api/admins/(:segment)', 'Api::adminsDelete/$1');

// ── 문의(공개 접수 + 관리자 조회/삭제) ─────────────
$routes->post  ('api/inquiries',         'Api::inqAdd');   // 공개(문의폼)
$routes->get   ('api/inquiries',         'Api::inqList');
$routes->delete('api/inquiries/(:num)',  'Api::inqDelete/$1');

// ── 관리자 UI ─────────────────────────────────────
$routes->get('admin', 'Api::adminUi');
$routes->get('admin/(:segment)', 'Api::adminAsset/$1');

// ── 카피 편집모드 (사이트 페이지 + 편집 스크립트 주입) ──
// admin.js "편집하기"는 /<page>?edit=1 을 열지만, 정적 HTML은 웹서버가 직접 서빙하므로
// 편집모드는 이 라우트로 처리. (README: admin.js window.open 을 '/editmode/'+page 로 1줄 변경)
$routes->get('editmode/(:segment)', 'Api::editMode/$1');
