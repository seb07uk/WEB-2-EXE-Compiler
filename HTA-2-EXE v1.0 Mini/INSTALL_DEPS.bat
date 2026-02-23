@echo off
REM ============================================================
REM  INSTALL_DEPS.bat - Instalacja zaleznosci
REM  Uruchom raz przed pierwszym buildem.
REM  polsoft.ITS(tm) London  -  Sebastian Januchowski  -  2026
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
chcp 65001 >nul 2>&1
title Instalacja zaleznosci - HTA-EXE Converter

echo.
echo  =====================================================
echo   Instalacja zaleznosci dla HTA-EXE Converter Build
echo   polsoft.ITS(tm) London - Sebastian Januchowski
echo  =====================================================
echo.

REM -- sprawdz Pythona ------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo  [BLAD] Python nie znaleziony!
    echo         Pobierz Python 3.10+ z https://python.org
    echo         Zaznacz "Add Python to PATH" podczas instalacji.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [OK] !PY_VER!
echo.

REM -- 1/3 pip --------------------------------------------------
echo  [1/3] Aktualizuje pip...
python -m pip install --upgrade pip --quiet
echo        OK

REM -- 2/3 PyInstaller ------------------------------------------
echo  [2/3] Instaluje PyInstaller...
python -m pip install --upgrade pyinstaller --quiet
if errorlevel 1 (
    echo  [BLAD] Nie mozna zainstalowac PyInstaller!
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python -m PyInstaller --version 2^>^&1') do set PI_VER=%%v
echo        OK - PyInstaller !PI_VER!

REM -- 3/3 Pillow -----------------------------------------------
echo  [3/3] Instaluje Pillow (ikony PNG/JPG)...
python -m pip install --upgrade pillow --quiet
if errorlevel 1 (
    echo        [WARN] Pillow niedostepny (opcjonalne - tylko dla ikon PNG/JPG)
) else (
    echo        OK
)

echo.
echo  =====================================================
echo   Wszystkie zaleznosci zainstalowane.
echo   Mozesz teraz uruchomic BUILD.bat
echo  =====================================================
echo.
pause
endlocal
