# HTA-EXE Converter `v1.0 mini`
<img width="486" height="727" alt="image" src="https://github.com/user-attachments/assets/d17ad2c6-91dc-41b9-a87a-65f3438d0b6f" />

> **Convert any HTA application into a standalone Windows `.exe` — no command line required.**

<div align="center">

![polsoft.ITS™ dev tools](https://img.shields.io/badge/polsoft.ITS™-dev%20tools-0f3460?style=for-the-badge&labelColor=0d1117)
![Version](https://img.shields.io/badge/version-1.0%20mini-e94560?style=for-the-badge&labelColor=0d1117)
![Platform](https://img.shields.io/badge/platform-Windows-00b4d8?style=for-the-badge&labelColor=0d1117)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white&labelColor=0d1117)
![License](https://img.shields.io/badge/license-Proprietary-8888aa?style=for-the-badge&labelColor=0d1117)

**Author:** Sebastian Januchowski &nbsp;|&nbsp; **Company:** polsoft.ITS™ London &nbsp;|&nbsp; **© 2026**

[✉ polsoft.its@fastservice.com](mailto:polsoft.its@fastservice.com) &nbsp;·&nbsp; [🔗 github.com/seb07uk](https://github.com/seb07uk)

</div>

---

## Table of Contents

- [What is HTA-EXE Converter?](#what-is-hta-exe-converter)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Interface — Full Reference](#user-interface--full-reference)
  - [Banner & Title Bar](#banner--title-bar)
  - [HTA File / Folder](#-hta-file--folder)
  - [Output Folder](#-output-folder)
  - [Icon](#-icon)
  - [UPX Compression](#-upx-compression)
  - [▶ Convert Button](#-convert-button)
  - [📁 EXE Folder Button](#-exe-folder-button)
  - [📋 Metadata Panel](#-metadata-panel)
  - [Log Window](#-log-window)
  - [Status Bar](#-status-bar)
- [EXE Metadata (Windows VERSIONINFO)](#exe-metadata-windows-versioninfo)
- [UPX Compression — Deep Dive](#upx-compression--deep-dive)
- [Asset Bundling & Inlining](#asset-bundling--inlining)
- [Settings Persistence](#settings-persistence)
- [Language Switching](#language-switching)
- [Always on Top](#always-on-top)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Technical Notes](#technical-notes)
- [License](#license)

---

## What is HTA-EXE Converter?

**HTA-EXE Converter** is a GUI desktop tool for Windows that wraps any `.hta` (*HTML Application*) file — or an entire HTA project folder — into a single, self-contained `.exe` executable.

The resulting `.exe`:
- Requires **no Python** installed on the target machine
- Requires **no separate files** — all assets are bundled inside
- Runs the HTA via the Windows built-in `mshta.exe` engine
- Can carry full **Windows VERSIONINFO metadata** (version, company, copyright)
- Can be optionally compressed with **UPX** to reduce file size

It is designed for developers, IT professionals, and power users who build HTA-based tools and want to distribute them as clean, professional `.exe` files.

---

## How It Works

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Your HTA project                                           │
  │  ├── app.hta        ← entry pointm                          │
  │  ├── style.css      ← auto-inlined into HTA                 │
  │  ├── logic.js       ← auto-inlined into HTA                 │
  │  └── images/        ← base64-bundled                        │
  └──────────────────────┬──────────────────────────────────────┘
                         │  Step 1: Collect & inline assets
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Python wrapper script (temp)                               │
  │  • Embeds all files as base64 strings                       │
  │  • On launch: extracts to temp dir, calls mshta.exe         │
  │  • Cleans up temp dir on exit (atexit)                      │
  └──────────────────────┬──────────────────────────────────────┘
                         │  Step 2: PyInstaller --onefile --noconsole
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Final standalone .EXE                                      │
  │  • Single file, no dependencies                             │
  │  • Optional: Windows VERSIONINFO metadata                   │
  │  • Optional: custom icon (.ico / .png / .jpg / .bmp)        │
  │  • Optional: UPX compression (--best --lzma)                │
  └─────────────────────────────────────────────────────────────┘
```

**Step-by-step internally:**

1. All project files are collected (`.hta`, `.html`, `.css`, `.js`, `.json`, `.xml`, images, fonts, etc.)
2. External `<script src="...">` and `<link href="...">` references are **automatically inlined** into the HTA source — no broken references at runtime
3. All files are **base64-encoded** and embedded into a Python wrapper script
4. `PyInstaller --onefile --noconsole` compiles the wrapper into a single `.exe`
5. Windows VERSIONINFO resource is injected via a `version_info.txt` file
6. Optionally, UPX compresses the result

---

## Requirements

| Requirement | Details |
|---|---|
| **OS** | Windows 7 / 8 / 10 / 11 (64-bit recommended) |
| **Python** | 3.10 or newer (must be in `PATH`) |
| **PyInstaller** | `pip install pyinstaller` — **required** |
| **Pillow** | `pip install pillow` — optional, needed for `.png` / `.jpg` / `.bmp` icons |
| **UPX** | Optional — place `upx.exe` next to the app or in `PATH` |
| **mshta.exe** | Built into Windows — required on the **target** machine to run the generated EXE |

> ⚠️ **Python must be installed on the machine running HTA-EXE Converter.** The *generated* `.exe` does not require Python on the target.

---

## Installation

HTA-EXE Converter does not require installation. Just run the script:

```bash
# 1. Install dependencies
pip install pyinstaller
pip install pillow        # optional

# 2. Run
python HTA-2-EXE.py
```

Or double-click `HTA-EXE Converter 1.0 Mini.exe` if you have the pre-built version.

---

## Quick Start

1. **Launch** the application
2. Click **File…** or **Folder…** next to *HTA File/Folder* and select your `.hta` file or project folder
3. Optionally set an **Output Folder** (defaults to the HTA's own directory)
4. Optionally pick an **Icon**
5. Click **▶ Convert**
6. When done, click **📁 EXE Folder** to open the output location

That's it — your `.exe` is ready.

---

## User Interface — Full Reference

### Banner & Title Bar

The animated banner at the top of the window displays:
- **Application name** — `HTA → EXE Converter mini`
- **Subtitle** — `polsoft.ITS™ dev tools`
- Aero Glass visual effect with animated neon scan line, particle sparks, and a pulsing status dot in the EXE badge

The **title bar** shows: `HTA-EXE Converter 1.0 Mini by Sebastian Januchowski`

---

### 📂 HTA File / Folder

**Label:** *HTA File/Folder*

This is the **primary input** — the source of your HTA application.

| Button | Action |
|---|---|
| **File…** | Opens a file picker filtered to `.hta`, `.html`, `.htm` files. Use this for single-file HTA apps. |
| **Folder…** | Opens a folder picker. Use this for multi-file HTA projects with separate CSS, JS, and image assets. |

**What gets collected when you select a folder:**

The converter recursively scans the folder for all files with these extensions:

```
.hta  .html  .htm  .css  .js  .json  .xml
.png  .jpg  .jpeg  .gif  .ico  .svg  .bmp
.woff  .woff2  .ttf  .eot  .txt  .md
```

The **entry point** is determined automatically: the first `.hta` file found takes priority, then `.html`, then `.htm`.

> 💡 **Tip:** If your project has a specific entry point, name it with `.hta` extension so it is picked up first.

---

### 📁 Output Folder

**Label:** *Output Folder*

The directory where the finished `.exe` will be saved.

- Click **Browse…** to select a folder
- If left empty, the output goes to the **same folder as the input HTA**
- The path is remembered between sessions

---

### 🖼 Icon

**Label:** *Icon*

Sets the icon embedded into the `.exe` file (visible in Explorer, taskbar, etc.).

| Format | Requirements |
|---|---|
| `.ico` | Works directly, no extra dependencies |
| `.png` | Requires **Pillow** (`pip install pillow`) |
| `.jpg` / `.jpeg` | Requires **Pillow** |
| `.bmp` | Requires **Pillow** |

When you pick a non-ICO image, the converter:
1. Opens it with Pillow
2. Converts to RGBA
3. Generates a multi-resolution `.ico` with sizes: 16×16, 24×24, 32×32, 48×48, 64×64, 128×128, 256×256
4. Passes the `.ico` to PyInstaller

A **thumbnail preview** of the icon is shown next to the path field after selection.

> ⚠️ If Pillow is not installed and you select a non-ICO file, the icon is **silently skipped** — the EXE will use the default Python icon. A warning appears in the Log.

---

### 📦 UPX Compression

**Label:** *UPX*

UPX (*Ultimate Packer for eXecutables*) is an open-source executable compressor that can significantly reduce the size of the generated `.exe`.

**Checkbox:** `compress EXE (--best --lzma)`

When checked, after PyInstaller finishes, UPX runs on the output `.exe` with maximum compression:

```
upx --best --lzma YourApp.exe
```

**How UPX is located (auto-detection order):**

1. `upx.exe` in the **same folder as HTA-EXE Converter**
2. `upx` / `upx.exe` anywhere in the system **PATH**

The status indicator next to the checkbox shows:
- ✔ green — UPX found, path displayed
- ✘ red — UPX not found, compression will be skipped even if checked

**Typical compression results:** 40–70% size reduction depending on content.

> 💡 Download UPX from [upx.github.io](https://upx.github.io/) and place `upx.exe` next to the converter.

---

### ▶ Convert Button

The main action button. Starts the conversion process.

**What happens when you click Convert:**

1. Input path is validated (must exist)
2. If output `.exe` already exists → confirmation dialog ("Overwrite?")
3. Log is cleared
4. A background thread starts the conversion (UI stays responsive)
5. Progress bar animates (neon cyan indeterminate)
6. Elapsed time counter starts in the status bar
7. On success → success dialog + **📁 EXE Folder** button activates
8. On error → error dialog with details in the Log

While converting, the button shows `⏳ Converting…` and is disabled.

---

### 📁 EXE Folder Button

Opens the output folder in **Windows Explorer**, directly to the folder containing the generated `.exe`.

- Disabled until a successful conversion has been completed in the current session
- If the last EXE file still exists on disk, it navigates to its exact parent folder
- Falls back to the Output Folder path if the file is no longer there

---

### 📋 Metadata Panel

Click **📋 Metadata** to expand the metadata form. Click again (shows **▲**) to collapse it.

The metadata is embedded into the `.exe` as a standard **Windows VERSIONINFO** resource, visible in *File → Properties → Details* in Explorer.

| Field | Description | Example |
|---|---|---|
| **App name** | Internal name and product name of the EXE | `MyTool` |
| **Version (x.x.x.x)** | Four-part version number | `1.2.0.0` |
| **Company** | Company or author name | `polsoft.ITS™ London` |
| **Description** | Short description shown in file properties | `HTA application compiled to EXE` |
| **Copyright** | Copyright string | `© 2026 Sebastian Januchowski` |

All fields are **optional**. If left blank, the VERSIONINFO block is omitted entirely.

The metadata settings are **saved between sessions** automatically.

---

### Log Window

The log panel shows real-time output from the conversion process.

**Color-coded messages:**

| Color | Tag | Meaning |
|---|---|---|
| 🔵 Cyan | `[INFO]` | Informational steps (collecting files, inlining, PyInstaller progress) |
| 🟡 Yellow | `[WARN]` | Non-fatal warnings (UPX not found, icon skipped, etc.) |
| 🔴 Red | `[ERROR]` / `✘` | Errors that stopped the conversion |
| 🟢 Green | `✔` | Success confirmation |

The log automatically scrolls to the latest message and keeps the last 200 lines.

---

### Status Bar

The bottom bar shows application state at a glance:

| Element | Description |
|---|---|
| **● dot** | Green = ready, orange/pulsing = converting, red = error |
| **Status text** | Current state: *Ready*, *Converting…*, *Cancelled*, or the EXE filename |
| **Filename** | Name of the file being processed or last generated EXE |
| **⏱ Timer** | Elapsed time during conversion (`MM:SS`) |
| **ⓘ** | Opens the *About* dialog |
| **❓** | Opens the *Help* dialog |
| **`EN` / `PL` badge** | Switches interface language |
| **📍 / 📌 pin** | Toggles *Always on Top* mode |

---

## EXE Metadata (Windows VERSIONINFO)

The metadata panel generates a `VSVersionInfo` block compatible with PyInstaller's `--version-file` option. It creates a proper Windows PE resource with both `StringFileInfo` and `VarFileInfo` sections.

**Fields embedded:**

```
CompanyName       → Company field
FileDescription   → Description field
FileVersion       → Version field (string)
InternalName      → App name field
LegalCopyright    → Copyright field
OriginalFilename  → App name + .exe
ProductName       → App name field
ProductVersion    → Version field (string)
filevers          → Version as tuple (major, minor, patch, build)
prodvers          → Same as filevers
```

**Version format:** Must be `major.minor.patch.build` (e.g., `1.0.0.0`). If fewer parts are given, zeros are appended. If the format is invalid, it falls back to `(1, 0, 0, 0)`.

---

## UPX Compression — Deep Dive

UPX compression happens **after** PyInstaller builds the EXE. The converter runs:

```
upx --best --lzma output.exe
```

`--best` selects the highest compression level. `--lzma` uses the LZMA algorithm which typically achieves better ratios than the default.

After compression, the Log reports:

```
[INFO] UPX: 8420 KB → 3210 KB (saved 5210 KB, 38.1% of original)
```

**Notes:**
- UPX return code `1` is treated as success (already-compressed files)
- If UPX fails, the EXE is still delivered — just uncompressed
- Some antivirus software may flag UPX-compressed executables as suspicious (false positive). This is a known UPX limitation.

---

## Asset Bundling & Inlining

### CSS & JavaScript Inlining

Before bundling, the converter scans the HTA source for external references and **inlines them directly**:

```html
<!-- Before inlining -->
<script src="logic.js"></script>
<link rel="stylesheet" href="style.css">

<!-- After inlining -->
<script>
  /* contents of logic.js */
</script>
<style>
  /* contents of style.css */
</style>
```

This ensures the HTA runs correctly from a temporary directory without any path issues. External URLs (`http://`, `https://`, `//`) are left untouched.

### Binary Assets

Images, fonts, and other binary files are **base64-encoded** and embedded as string literals inside the Python wrapper. At runtime, they are decoded and written to a temporary directory before `mshta.exe` is called.

### Temp Directory Lifecycle

```
App launches → Creates temp dir (hta_app_XXXX) → Extracts all files
                                                         ↓
                                              mshta.exe runs the HTA
                                                         ↓
                                    App exits → atexit cleans up temp dir
```

---

## Settings Persistence

The converter saves your settings automatically to:

```
%APPDATA%\hta2exe_gui\settings.json
```

**Saved settings include:**
- Last used output folder
- UPX enabled/disabled state and path
- Metadata fields (name, version, company, description, copyright)
- Window geometry (size and position)
- Interface language (PL / EN)
- Always on Top state

Settings are restored on next launch.

---

## Language Switching

The interface supports **Polish** and **English**. Click the `EN` or `PL` badge in the bottom-right of the status bar to switch.

The entire UI rebuilds instantly — all labels, buttons, dialogs, and log messages switch language. Your form data is preserved during the rebuild.

The selected language is saved to settings and restored on next launch.

---

## Always on Top

Click the **📍** pin icon in the status bar to toggle *Always on Top* mode.

- **📍** (unpinned) — normal window behaviour
- **📌** (pinned) — the converter window stays above all other windows

State is saved and restored between sessions.

---

## Troubleshooting

### `Layout Horizontal.Neon.TProgressbar not found`
Your Python/Tkinter version requires ttk styles to be initialized differently. Make sure you are running the latest version of HTA-EXE Converter which initializes the style in `App.__init__()` using the built-in `TProgressbar` name.

### `No module named 'PyInstaller'`
PyInstaller is not installed. Run:
```bash
pip install pyinstaller
```

### `Permission Error` / `WinError 5`
The output `.exe` is currently running. Close it before trying to overwrite with a new build.

### `mshta.exe not found` (on target machine)
The generated EXE calls `mshta.exe` which is part of Windows. It is present on all standard Windows installations. On Windows Server Core or stripped-down images it may be missing or disabled by Group Policy.

### Icon is ignored / default Python icon used
Either Pillow is not installed (for non-ICO formats) or the icon file path is invalid. Check the Log for `[WARN]` messages about the icon.

### UPX not found
Place `upx.exe` in the same folder as `HTA-2-EXE.py` (or the converter EXE), or add its directory to the system `PATH`. The status bar shows ✔ when UPX is detected.

### Conversion succeeds but the EXE crashes on target machine
- Make sure the target machine has `mshta.exe` available
- If your HTA uses ActiveX or COM objects, they must be registered on the target machine
- Check that your HTA does not reference external files by absolute path — all assets must be in the project folder so they get bundled

### `ValueError: empty range in randrange` (animation crash)
Resize the application window to be wider — this was a bug in earlier builds where particles would crash on very narrow windows. Fixed in current version with `max()` guards.

---

## FAQ

**Q: Does the generated EXE require Python on the target machine?**
A: No. PyInstaller packages everything needed. Only `mshta.exe` (built into Windows) is required.

**Q: Can I convert a multi-file HTA project (with CSS, JS, images)?**
A: Yes. Select the project **folder** instead of a single file. All supported assets are collected and bundled automatically.

**Q: Will my HTA's JavaScript and CSS work correctly?**
A: Yes. External script and stylesheet references are inlined before bundling, so relative paths work as expected.

**Q: Can I use a PNG or JPG as the EXE icon?**
A: Yes, if Pillow is installed (`pip install pillow`). The image is auto-converted to a multi-resolution `.ico`.

**Q: How much does UPX compress the EXE?**
A: Typically 40–70%, depending on content. A 10 MB EXE may compress to 3–5 MB.

**Q: Can I run the converter itself as an EXE (frozen)?**
A: Yes. When running frozen, the converter detects this and searches `PATH` for a real Python interpreter to run PyInstaller, since `sys.executable` would otherwise point to itself.

**Q: Where are settings saved?**
A: `%APPDATA%\hta2exe_gui\settings.json`

**Q: Can I use this on non-Windows systems?**
A: The converter's UI will run on any OS with Python + Tkinter. However, the generated EXE targets Windows only (relies on `mshta.exe`).

**Q: My antivirus flags the generated EXE. Is it a virus?**
A: No. PyInstaller-generated executables are commonly flagged as false positives, especially when UPX-compressed. This is a known industry issue. Submit the file to your AV vendor as a false positive.

---

## Technical Notes

- **Conversion runs in a background thread** — the GUI remains fully responsive during long builds
- **Temp directory** is created via `tempfile.mkdtemp()` and always cleaned up via `atexit`, even on crash
- **PyInstaller flags used:** `--onefile` (single EXE), `--noconsole` (no terminal window), `--distpath` (output location), `--workpath` (build artifacts in temp)
- **CSS/JS inlining** uses regex matching on `<script src="...">` and `<link href="...">` patterns; only local references are inlined
- **Base64 overhead:** Binary assets increase ~33% in the wrapper source; PyInstaller then compresses the bundle further
- **Python discovery when frozen:** Searches `python`, `python3`, then `py` (Windows Launcher) in PATH
- **UPX return code 1** is treated as success — UPX exits 1 when the file is already compressed or compression is not beneficial
- **Log retention:** The log widget keeps a maximum of 200 lines to avoid memory growth during very verbose builds

---

## License

```
© 2026 Sebastian Januchowski. All rights reserved.
polsoft.ITS™ London

This software is proprietary. Redistribution, modification,
or commercial use without explicit written permission is prohibited.

Contact: polsoft.its@fastservice.com
```

---

<div align="center">

**HTA-EXE Converter** `v1.0 mini` &nbsp;·&nbsp; polsoft.ITS™ dev tools &nbsp;·&nbsp; London 2026

*Built with Python · Tkinter · PyInstaller*

</div>
