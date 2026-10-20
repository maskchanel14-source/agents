@echo off
setlocal EnableExtensions
rem ============================================================
rem  start_bot_background.bat - jalan tanpa jendela (pythonw)
rem  Untuk Task Scheduler / background. Log di logs\bot.log
rem  Hentikan dengan stop_bot.bat (kill switch aman).
rem ============================================================
cd /d "%~dp0"

if not exist "venv\Scripts\pythonw.exe" (
    echo [ERROR] venv belum ada. Jalankan start_bot.bat dulu untuk setup.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] .env belum ada. Jalankan start_bot.bat dulu.
    pause
    exit /b 1
)

rem Mode default paper; ganti dengan --mode live HANYA jika sudah siap.
start "ARC-TERMINAL background" /min "" venv\Scripts\pythonw.exe -m bot --mode paper --no-open-browser
echo Bot berjalan di background. Cek dashboard http://127.0.0.1:8788/
echo Hentikan dengan stop_bot.bat
timeout /t 5 >nul
endlocal
exit /b 0
