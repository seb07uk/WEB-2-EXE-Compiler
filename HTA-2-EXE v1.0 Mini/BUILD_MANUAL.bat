@echo off
REM ============================================================
REM  BUILD_MANUAL.bat - Kompilacja bez pliku .spec
REM  Alternatywa gdy .spec nie dziala.
REM  polsoft.ITS(tm) London  -  Sebastian Januchowski  -  2026
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
chcp 65001 >nul 2>&1
title HTA-EXE Converter - Manual Build

echo.
echo  =====================================================
echo   HTA-EXE Converter 1.0 mini - Manual Build
echo   polsoft.ITS(tm) London - Sebastian Januchowski
echo  =====================================================
echo.

REM -- sprawdz Pythona ------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo  [BLAD] Python nie znaleziony w PATH!
    pause
    exit /b 1
)

REM -- wykryj ikone ---------------------------------------------
set ICO_FLAG=
if exist "HTA_Compiler-ico.ico" (
    set ICO_FLAG=--icon "HTA_Compiler-ico.ico"
    echo  [OK] Ikona: HTA_Compiler-ico.ico
) else (
    echo  [INFO] Brak ikony - kompilacja bez ikony
)

REM -- wykryj version_info --------------------------------------
set VI_FLAG=
if exist "version_info.txt" (
    set VI_FLAG=--version-file "version_info.txt"
    echo  [OK] Version info: version_info.txt
) else (
    echo  [INFO] Brak version_info.txt
)

REM -- wykryj UPX -----------------------------------------------
set UPX_FLAG=
if exist "upx.exe" (
    set UPX_FLAG=--upx-dir "."
    echo  [OK] UPX: upx.exe znaleziony
) else (
    echo  [INFO] Brak upx.exe - kompilacja bez UPX
)

echo.
echo  [INFO] Kompilowanie...
echo.

python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --clean ^
    --noconfirm ^
    --name "HTA-EXE Converter 1.0 mini" ^
    --optimize 2 ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    --exclude-module sqlite3 ^
    !ICO_FLAG! ^
    !VI_FLAG! ^
    !UPX_FLAG! ^
    "HTA-2-EXE.py"

echo.
if exist "dist\HTA-EXE Converter 1.0 mini.exe" (
    for %%f in ("dist\HTA-EXE Converter 1.0 mini.exe") do set SIZE=%%~zf
    set /a SIZE_MB=!SIZE! / 1048576
    echo  =====================================================
    echo   [SUKCES] dist\HTA-EXE Converter 1.0 mini.exe
    echo   Rozmiar : !SIZE_MB! MB  (!SIZE! bajtow)
    echo  =====================================================
    explorer "dist"
) else (
    echo  [BLAD] Kompilacja nie powiodla sie. Sprawdz log powyzej.
)
echo.
pause
endlocal
