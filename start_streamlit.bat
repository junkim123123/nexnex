@echo off
echo ========================================
echo NexSupply Streamlit 서버 시작
echo ========================================
echo.

REM 포트가 사용 중인지 확인
netstat -ano | findstr ":8501" >nul
if %errorlevel% == 0 (
    echo ⚠️  포트 8501이 이미 사용 중입니다.
    echo 기존 프로세스를 종료하고 다시 시도합니다...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo.
echo 🚀 Streamlit 서버를 시작합니다...
echo 포트: 8501
echo 브라우저에서 자동으로 열립니다.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

REM Streamlit 실행 (IPv4만 사용)
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501

pause

