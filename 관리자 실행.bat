@echo off
chcp 65001 >nul
title 퍼스트디자인 인천지사 - 관리자
cd /d "%~dp0"

echo ============================================
echo   퍼스트디자인 인천지사 관리자
echo ============================================
echo.

rem 이미 실행 중인지 확인
netstat -ano | findstr ":5701" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [i] 관리자 서버가 이미 실행 중입니다.
) else (
    echo [1/2] 관리자 서버 시작...
    start "관리자 서버" /min cmd /c "cd /d "%~dp0admin" && python server.py"
    timeout /t 3 /nobreak >nul
)

echo [2/2] 브라우저 열기...
start http://localhost:5701/admin

echo.
echo ============================================
echo   주소   : http://localhost:5701/admin
echo   아이디 : admin
echo ============================================
echo.
echo 이 창을 닫아도 관리자 서버는 계속 실행됩니다.
echo 서버를 끄려면 최소화된 "관리자 서버" 창을 닫으세요.
echo.
pause
