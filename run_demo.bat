@echo off
echo ===================================================
echo   Cleaning up old processes...
taskkill /F /IM ngrok.exe /T >nul 2>&1
echo   Starting Phish Guard Local Demo
echo ===================================================

echo [1/2] Launching Flask Server...
start "Phish Guard Server" cmd /k "py run.py || pause"

echo Waiting 5 seconds for server to start...
timeout /t 5 >nul

echo [2/2] Launching Ngrok Tunnel...
start "Phish Guard Tunnel" cmd /k "py start_tunnel.py || pause"

echo.
echo ===================================================
echo   DONE! 
echo.
echo   1. Check the "Phish Guard Tunnel" window.
echo   2. Copy the "NGROK_URL" (e.g., https://xyz.ngrok-free.app).
echo   3. Share that link!
echo ===================================================
pause
