@echo off
setlocal EnableExtensions
rem ============================================================
rem  start_bot.bat - launcher bot arbitrase Polymarket (Windows)
rem  Line endings: CRLF. ASCII-safe. Klik dua kali dari mana saja.
rem ============================================================
cd /d "%~dp0"
title ARC-TERMINAL - Polymarket Arb Bot
color 0B

:MENU
cls
echo ============================================================
echo   ARC-TERMINAL - POLYMARKET ARBITRAGE BOT
echo   Mode default: PAPER (simulasi, TANPA order asli)
echo ============================================================
echo.
echo   [1] PAPER        - live data, eksekusi simulasi
echo   [2] BACKTEST     - replay fixture/rekaman
echo   [3] LIVE         - TERKUNCI, butuh konfirmasi ketik LIVE
echo   [4] Edit .env
echo   [5] Jalankan test suite
echo   [6] Rekam data orderbook live (recorder)
echo   [0] Keluar
echo.
set "CHOICE="
set /p CHOICE="Pilih menu [0-6]: "

if "%CHOICE%"=="1" goto RUN_PAPER
if "%CHOICE%"=="2" goto RUN_BACKTEST
if "%CHOICE%"=="3" goto RUN_LIVE
if "%CHOICE%"=="4" goto EDIT_ENV
if "%CHOICE%"=="5" goto RUN_TESTS
if "%CHOICE%"=="6" goto RUN_RECORD
if "%CHOICE%"=="0" goto EXIT
echo Pilihan tidak dikenal. Tekan ENTER untuk ulang...
pause >nul
goto MENU

rem ------------------------------------------------------------
:PREP
rem Cek Python 3.11+ dan siapkan venv + dependency (sekali jalan).
set "PYLAUNCH="
where py >nul 2>nul && set "PYLAUNCH=py -3"
if defined PYLAUNCH goto HAVE_PY
where python >nul 2>nul && set "PYLAUNCH=python"
if defined PYLAUNCH goto HAVE_PY
echo [ERROR] Python tidak ditemukan di PATH.
echo Instal Python 3.11+ dari https://www.python.org/downloads/
echo Centang "Add python.exe to PATH" saat instalasi.
pause
exit /b 1

:HAVE_PY
%PYLAUNCH% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Butuh Python 3.11 atau lebih baru. Versi terdeteksi:
    %PYLAUNCH% --version
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [SETUP] Membuat virtual environment...
    %PYLAUNCH% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Gagal membuat venv.
        pause
        exit /b 1
    )
)
set "PY=venv\Scripts\python.exe"

rem Install dependency hanya jika requirements berubah (marker file)
set "NEED_INSTALL=1"
if exist "venv\.install_marker" (
    fc /b "venv\.install_marker" "requirements.txt" >nul 2>nul && set "NEED_INSTALL=0"
)
if "%NEED_INSTALL%"=="1" (
    echo [SETUP] Install dependencies...
    "%PY%" -m pip install --upgrade pip
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Gagal install dependencies.
        pause
        exit /b 1
    )
    copy /y "requirements.txt" "venv\.install_marker" >nul
)

if not exist ".env" (
    echo [SETUP] .env belum ada - membuat dari .env.example ...
    copy /y ".env.example" ".env" >nul
    echo [SETUP] Membuka .env di Notepad - isi sesuai kebutuhan lalu SIMPAN.
    notepad ".env"
)
exit /b 0

rem ------------------------------------------------------------
:RUN_PAPER
call :PREP
if errorlevel 1 goto MENU
echo.
echo [RUN] Memulai bot mode PAPER (dashboard terbuka otomatis di browser)...
echo Tekan Ctrl+C untuk berhenti dengan bersih.
"%PY%" -m bot --mode paper
echo.
echo [EXIT] Bot berhenti dengan exit code %ERRORLEVEL%.
pause
goto MENU

rem ------------------------------------------------------------
:RUN_BACKTEST
call :PREP
if errorlevel 1 goto MENU
echo.
echo [RUN] Backtest replay + parameter sweep...
"%PY%" -m bot.backtest.run --sweep
echo.
echo [EXIT] Backtest selesai dengan exit code %ERRORLEVEL%.
pause
goto MENU

rem ------------------------------------------------------------
:RUN_LIVE
call :PREP
if errorlevel 1 goto MENU
echo.
echo ============================================================
echo   PERINGATAN: MODE LIVE MEMAKAI UANG ASLI
echo ============================================================
echo Bot tetap mensyaratkan LIVE_TRADING=true di .env DAN file
echo live_trading.confirmed. Tanpa keduanya, bot jatuh ke PAPER.
echo.
set "CONFIRM="
set /p CONFIRM="Ketik LIVE (huruf besar) untuk melanjutkan: "
if /I not "%CONFIRM%"=="LIVE" (
    echo [BATAL] Konfirmasi tidak cocok - kembali ke menu.
    pause
    goto MENU
)
echo.
echo [RUN] Memulai bot mode LIVE...
"%PY%" -m bot --mode live
echo.
echo [EXIT] Bot berhenti dengan exit code %ERRORLEVEL%.
pause
goto MENU

rem ------------------------------------------------------------
:EDIT_ENV
if not exist ".env" copy /y ".env.example" ".env" >nul
notepad ".env"
goto MENU

rem ------------------------------------------------------------
:RUN_TESTS
call :PREP
if errorlevel 1 goto MENU
echo.
echo [TEST] Menjalankan test suite...
"%PY%" -m pip install -r requirements-dev.txt
"%PY%" -m pytest tests/ -q
echo.
echo [EXIT] Test selesai dengan exit code %ERRORLEVEL%.
pause
goto MENU

rem ------------------------------------------------------------
:RUN_RECORD
call :PREP
if errorlevel 1 goto MENU
set "MINUTES="
set /p MINUTES="Durasi rekam dalam menit (mis. 120): "
if "%MINUTES%"=="" set "MINUTES=60"
echo.
echo [REC] Merekam orderbook live ke data\recordings ...
"%PY%" -m bot.record --minutes %MINUTES% --out data\recordings
echo.
echo [EXIT] Recorder selesai dengan exit code %ERRORLEVEL%.
pause
goto MENU

rem ------------------------------------------------------------
:EXIT
echo Sampai jumpa.
endlocal
exit /b 0
