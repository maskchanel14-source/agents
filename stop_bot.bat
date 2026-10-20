@echo off
setlocal EnableExtensions
rem ============================================================
rem  stop_bot.bat - aktifkan kill switch (aman) lalu matikan bot
rem ============================================================
cd /d "%~dp0"

echo Mengaktifkan kill switch (file KILL_SWITCH)...
echo stop > KILL_SWITCH

rem Beri waktu bot menyadar lalu shutdown bersih (cancel-all order)
timeout /t 8 >nul

rem Matikan proses python bot yang tersisa (jika masih hidup)
tasklist /fi "imagename eq pythonw.exe" 2>nul | find /i "pythonw.exe" >nul && (
    echo Menghentikan proses background...
    taskkill /im pythonw.exe /f >nul 2>nul
)
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul && (
    taskkill /im python.exe /f >nul 2>nul
)

echo Selesai. Kill switch tetap aktif (file KILL_SWITCH ada).
echo Jalankan start_bot.bat lagi untuk menghapus kill switch otomatis
echo atau hapus manual file KILL_SWITCH sebelum trading berikutnya.
pause
endlocal
exit /b 0
