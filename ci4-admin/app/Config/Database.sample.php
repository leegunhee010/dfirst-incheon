<?php
/**
 * DB 접속 설정 예시 — 실제 서버의 app/Config/Database.php 의 $default 배열에 반영하세요.
 * (CI4 기본 Database.php 에서 아래 값만 서버 정보로 채우면 됩니다.)
 */
public array $default = [
    'DSN'      => '',
    'hostname' => 'localhost',
    'username' => 'firstd_user',      // ← 서버 MySQL 계정
    'password' => 'CHANGE_ME',        // ← 비밀번호
    'database' => 'firstd_incheon',   // ← 스키마명
    'DBDriver' => 'MySQLi',
    'DBPrefix' => '',
    'pConnect' => false,
    'DBDebug'  => false,
    'charset'  => 'utf8mb4',
    'DBCollat' => 'utf8mb4_general_ci',
    'port'     => 3306,
];
