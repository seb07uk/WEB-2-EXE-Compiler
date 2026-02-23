# Build — HTA-EXE Converter v1.0 mini

> Instrukcja kompilacji do portable `.exe` dla Windows

---

## Zawartość paczki build

```
📁 build_package\
├── HTA-2-EXE.py              ← główny skrypt aplikacji
├── HTA-2-EXE.spec            ← spec PyInstaller (zalecane)
├── HTA_Compiler-ico.ico      ← ikona EXE
├── version_info.txt          ← metadane Windows VERSIONINFO
├── upx.exe                   ← kompresor (opcjonalne)
│
├── INSTALL_DEPS.bat          ← krok 1: instaluj zależności
├── BUILD.bat                 ← krok 2: kompiluj (używa .spec)
└── BUILD_MANUAL.bat          ← alternatywa: bez pliku .spec
```

---

## Szybki start

### Krok 1 — Zainstaluj zależności (tylko raz)

```
Dwuklik: INSTALL_DEPS.bat
```

Instaluje: `pyinstaller` + `pillow`

### Krok 2 — Skompiluj

```
Dwuklik: BUILD.bat
```

Gotowy plik: `dist\HTA-EXE Converter 1.0 mini.exe`

---

## Wymagania

| Co | Wersja |
|---|---|
| Windows | 7 / 10 / 11 (64-bit) |
| Python | 3.10+ (musi być w PATH) |
| PyInstaller | najnowszy (`pip install pyinstaller`) |
| Pillow | opcjonalne (`pip install pillow`) |

---

## Ręczna kompilacja (bez .bat)

```bat
python -m PyInstaller HTA-2-EXE.spec --clean --noconfirm
```

lub bez pliku spec:

```bat
python -m PyInstaller ^
    --onefile --noconsole --clean ^
    --name "HTA-EXE Converter 1.0 mini" ^
    --icon "HTA_Compiler-ico.ico" ^
    --version-file "version_info.txt" ^
    --upx-dir "." ^
    HTA-2-EXE.py
```

---

## Wynik

```
dist\
└── HTA-EXE Converter 1.0 mini.exe   ← portable, standalone EXE
```

- Jeden plik, zero zależności na maszynie docelowej
- Ikona z `HTA_Compiler-ico.ico`
- Metadane z `version_info.txt` (widoczne w Właściwościach pliku)
- Skompresowany przez UPX jeśli `upx.exe` obecny

---

## Troubleshooting

**`Python nie znaleziony`** — zainstaluj Python 3.10+ z [python.org](https://python.org) zaznaczając *Add Python to PATH*

**`No module named PyInstaller`** — uruchom `INSTALL_DEPS.bat`

**`icon file not found`** — upewnij się że `HTA_Compiler-ico.ico` jest w tym samym folderze

**`version file not found`** — upewnij się że `version_info.txt` jest w tym samym folderze

**AV flaguje EXE** — znany false-positive PyInstaller+UPX, pomiń UPX lub dodaj do wyjątków AV

---

*polsoft.ITS™ London · 2026© Sebastian Januchowski*
