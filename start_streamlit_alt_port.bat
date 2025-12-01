@echo off
echo ========================================
echo NexSupply Streamlit 서버 시작 (대체 포트)
echo ========================================
echo.

echo 🚀 Streamlit 서버를 시작합니다...
echo 포트: 8502 (대체 포트)
echo 브라우저에서 http://localhost:8502 로 접속하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

REM Streamlit 실행 (대체 포트, IPv4만 사용)
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502

pause

