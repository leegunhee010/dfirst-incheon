-- 2026-07-28 마이그레이션 (이미 schema.sql로 설치한 경우에만 실행)
-- MySQL 5.6 호환: JSON·생성컬럼 미사용
ALTER TABLE `columns`
  ADD COLUMN `file` VARCHAR(64) DEFAULT NULL,
  ADD COLUMN `builtin` TINYINT(1) NOT NULL DEFAULT 0;
