# ============================================================
#  HTA-2-EXE.spec  -  PyInstaller spec file
#  HTA-EXE Converter 1.0 mini
#  polsoft.ITS(tm) London  *  Sebastian Januchowski  *  2026
#
#  Uzycie:  pyinstaller HTA-2-EXE.spec --clean --noconfirm
# ============================================================
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['HTA-2-EXE.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'PyQt5',
        'PyQt6',
        'wx',
        'sqlite3',
        'unittest',
        'test',
        'tests',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HTA-EXE Converter 1.0 mini',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='HTA_Compiler-ico.ico',
    version='version_info.txt',
)
