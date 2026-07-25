-- 퍼스트디자인 인천지사 관리자 — MySQL 5.6 스키마
-- (Flask+JSON 관리자를 CI4+MySQL로 이관. utf8mb4 / InnoDB)
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 관리자 계정
CREATE TABLE IF NOT EXISTS `admins` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(60) NOT NULL,
  `password_hash` CHAR(64) NOT NULL,           -- sha256
  `created_at` DATE NOT NULL DEFAULT '2026-07-24',
  PRIMARY KEY (`id`), UNIQUE KEY `uq_user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 포트폴리오 카드
CREATE TABLE IF NOT EXISTS `portfolio` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `image` VARCHAR(255) NOT NULL,
  `title` VARCHAR(200) NOT NULL DEFAULT '',
  `type` VARCHAR(120) NOT NULL DEFAULT '',
  `category` VARCHAR(30) NOT NULL DEFAULT '책자',   -- 책자/리플릿/로고/촬영/기타
  `sort_order` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`), KEY `idx_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 히어로 슬라이드(홈 bw-slide)
CREATE TABLE IF NOT EXISTS `hero` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `sort_order` INT NOT NULL DEFAULT 0,
  `title` TEXT,            -- *강조* / 줄바꿈 마커
  `eyebrow` VARCHAR(120) DEFAULT '',
  `subtitle` TEXT,
  `image` VARCHAR(255) DEFAULT '',
  `btn1_link` VARCHAR(255) DEFAULT 'portfolio.html',
  `text_color` VARCHAR(10) DEFAULT 'light',
  PRIMARY KEY (`id`), KEY `idx_order` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- FAQ (서비스 페이지별 전체 문항)
CREATE TABLE IF NOT EXISTS `faq` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `page` VARCHAR(40) NOT NULL,       -- svc-brand, catalog ...
  `q` TEXT NOT NULL,
  `a` TEXT NOT NULL,
  `sort_order` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`), KEY `idx_page` (`page`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 칼럼(블로그) 글
CREATE TABLE IF NOT EXISTS `columns` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `category` VARCHAR(80) NOT NULL DEFAULT 'Column',
  `excerpt` VARCHAR(500) DEFAULT '',
  `body` MEDIUMTEXT,                 -- 본문 HTML
  `thumbnail` VARCHAR(255) DEFAULT '',
  `status` VARCHAR(16) NOT NULL DEFAULT 'published',  -- published/draft
  `date` DATE NOT NULL,
  PRIMARY KEY (`id`), KEY `idx_status_date` (`status`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 카피(문구) 오버라이드 — 원문→새문 치환쌍
CREATE TABLE IF NOT EXISTS `content_overrides` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `page` VARCHAR(40) NOT NULL,
  `orig` TEXT NOT NULL,
  `new` TEXT NOT NULL,
  PRIMARY KEY (`id`), KEY `idx_page` (`page`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SEO 페이지별 메타 오버라이드
CREATE TABLE IF NOT EXISTS `seo_overrides` (
  `page` VARCHAR(40) NOT NULL,
  `title` VARCHAR(255) DEFAULT '',
  `description` TEXT,
  `keywords` TEXT,
  PRIMARY KEY (`page`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 이미지 교체 오버라이드
CREATE TABLE IF NOT EXISTS `image_overrides` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `page` VARCHAR(40) NOT NULL,
  `original_src` VARCHAR(255) NOT NULL,
  `new_src` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`), KEY `idx_page` (`page`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 사이트 설정 (key-value)
CREATE TABLE IF NOT EXISTS `settings` (
  `k` VARCHAR(40) NOT NULL,
  `v` TEXT,
  PRIMARY KEY (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 견적 문의 (홈/문의 폼 접수)
CREATE TABLE IF NOT EXISTS `inquiries` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `company` VARCHAR(120) DEFAULT '',
  `name` VARCHAR(80) DEFAULT '',
  `phone` VARCHAR(40) DEFAULT '',
  `email` VARCHAR(120) DEFAULT '',
  `field` VARCHAR(120) DEFAULT '',
  `message` TEXT,
  `status` VARCHAR(16) NOT NULL DEFAULT 'new',   -- new/inprogress/done
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`), KEY `idx_status` (`status`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
