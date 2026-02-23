"""
hta_to_exe_gui.py
=================
Konwerter HTA → EXE z graficznym interfejsem użytkownika.
Uruchom dwuklikiem lub:  python hta_to_exe_gui.py

Wymagania:  pip install pyinstaller
Opcjonalnie: pip install pillow   ← konwersja PNG/JPG → ICO

Autor:    Sebastian Januchowski
Firma:    polsoft.ITS™ London
E-mail:   polsoft.its@fastservice.com
GitHub:   https://github.com/seb07uk
Licencja: 2026© Sebastian Januchowski. All rights reserved.
"""
import os
import sys
import re
import io
import json
import shutil
import base64
import tempfile
import threading
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image as _PILImage
    _PILLOW = True
except ImportError:
    _PILLOW = False

# ─────────────────────────────────────────────
#  Internacjonalizacja (PL / EN)
# ─────────────────────────────────────────────

TRANSLATIONS = {
    "pl": {
        "app_title":          "HTA \u2192 EXE Konwerter",
        "hdr_subtitle":       "polsoft.ITS™ dev tools",
        "lbl_hta":            "Plik/Folder HTA:",
        "lbl_out":            "Folder wyj\u015bciowy:",
        "lbl_icon":           "Ikona:",
        "lbl_upx":            "UPX:",
        "upx_chk":            "kompresuj EXE  (--best --lzma)",
        "upx_not_found":      "nie znaleziono \u2014 dodaj upx.exe obok aplikacji",
        "btn_convert":        "\u25b6  Konwertuj",
        "btn_converting":     "\u23f3  Konwertuj\u0119\u2026",
        "btn_folder":         "\U0001f4c1  Folder EXE",
        "btn_meta":           "\U0001f4cb  Metadane",
        "btn_meta_open":      "\U0001f4cb  Metadane \u25b2",
        "btn_browse":         "Przegl\u0105daj\u2026",
        "btn_file":           "Plik\u2026",
        "btn_folder_btn":     "Folder\u2026",
        "log_header":         "Dziennik",
        "status_ready":       "Gotowy.",
        "status_converting":  "Konwertowanie\u2026",
        "status_cancelled":   "Anulowano.",
        "warn_no_input_t":    "Brak wej\u015bcia",
        "warn_no_input_m":    "Wybierz plik .HTA lub folder projektu!",
        "err_no_path_t":      "B\u0142\u0105d",
        "err_no_path_m":      "Ście\u017cka nie istnieje:\n{}",
        "ask_overwrite_t":    "Plik istnieje",
        "ask_overwrite_m":    "Plik ju\u017c istnieje:\n{}\n\nNadpisa\u0107?",
        "ok_success_t":       "Sukces!",
        "ok_success_m":       "EXE wygenerowany:\n\n{}",
        "err_conv_t":         "B\u0142\u0105d konwersji",
        "info_no_folder_t":   "Folder EXE",
        "info_no_folder_m":   "Brak folderu wyj\u015bciowego do otwarcia.",
        "meta_title":         "Metadane EXE (Windows VERSIONINFO)",
        "meta_name":          "Nazwa aplikacji:",
        "meta_ver":           "Wersja (x.x.x.x):",
        "meta_company":       "Producent:",
        "meta_desc":          "Opis:",
        "meta_copy":          "Copyright:",
        "meta_def_desc":      "Aplikacja HTA skompilowana do EXE",
        "about_title":        "O programie",
        "about_author":       "\U0001f9d1\u200d\U0001f4bb Autor:",
        "about_firm":         "\U0001f3e2 Firma:",
        "about_email":        "\u2709  E-mail:",
        "about_github":       "\U0001f517 GitHub:",
        "about_version":      "\U0001f4c6 Wersja:",
        "about_close":        "Zamknij",
        "help_title":         "Pomoc",
        "help_body": (
            "HTA \u2192 EXE Konwerter \u2014 Instrukcja obs\u0142ugi\n"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n"
            "1. Plik/Folder HTA\n"
            "   Wskazuje plik .hta lub folder projektu.\n"
            "   Wszystkie zasoby (CSS, JS, obrazy) zostan\u0105\n"
            "   automatycznie do\u0142\u0105czone.\n\n"
            "2. Folder wyj\u015bciowy\n"
            "   Miejsce zapisu gotowego pliku .exe.\n\n"
            "3. Ikona\n"
            "   Obs\u0142ugiwane formaty: .ico .png .jpg .bmp\n"
            "   (wymaga biblioteki Pillow dla non-ICO)\n\n"
            "4. UPX\n"
            "   Kompresuje plik EXE. Wymaga upx.exe\n"
            "   w katalogu aplikacji lub w PATH.\n\n"
            "5. Metadane\n"
            "   Informacje wbudowane w plik EXE\n"
            "   (wersja, producent, copyright).\n\n"
            "Wymagania:\n"
            "   pip install pyinstaller\n"
            "   pip install pillow  (opcjonalne)\n"
        ),
        "help_close":         "Zamknij",
        "pin_on":             "Zawsze na wierzchu: W\u0141.",
        "pin_off":            "Zawsze na wierzchu: WY\u0141.",
        "lang_switch":        "EN",
        "log_upx_warn":       ("[WARN] UPX w\u0142\u0105czony, ale upx.exe nie znaleziony! "
                               "Umie\u015b\u0107 upx.exe obok aplikacji lub zainstaluj w PATH."),
        "log_done":           "\n\u2714  Gotowe: {}",
        "log_err":            "\n\u2718  B\u0142\u0105d: {}",
    },
    "en": {
        "app_title":          "HTA \u2192 EXE Converter",
        "hdr_subtitle":       "polsoft.ITS™ dev tools",
        "lbl_hta":            "HTA File/Folder:",
        "lbl_out":            "Output Folder:",
        "lbl_icon":           "Icon:",
        "lbl_upx":            "UPX:",
        "upx_chk":            "compress EXE  (--best --lzma)",
        "upx_not_found":      "not found \u2014 place upx.exe next to this app",
        "btn_convert":        "\u25b6  Convert",
        "btn_converting":     "\u23f3  Converting\u2026",
        "btn_folder":         "\U0001f4c1  EXE Folder",
        "btn_meta":           "\U0001f4cb  Metadata",
        "btn_meta_open":      "\U0001f4cb  Metadata \u25b2",
        "btn_browse":         "Browse\u2026",
        "btn_file":           "File\u2026",
        "btn_folder_btn":     "Folder\u2026",
        "log_header":         "Log",
        "status_ready":       "Ready.",
        "status_converting":  "Converting\u2026",
        "status_cancelled":   "Cancelled.",
        "warn_no_input_t":    "No input",
        "warn_no_input_m":    "Please select an .HTA file or project folder!",
        "err_no_path_t":      "Error",
        "err_no_path_m":      "Path does not exist:\n{}",
        "ask_overwrite_t":    "File exists",
        "ask_overwrite_m":    "File already exists:\n{}\n\nOverwrite?",
        "ok_success_t":       "Success!",
        "ok_success_m":       "EXE generated:\n\n{}",
        "err_conv_t":         "Conversion error",
        "info_no_folder_t":   "EXE Folder",
        "info_no_folder_m":   "No output folder available.",
        "meta_title":         "EXE Metadata (Windows VERSIONINFO)",
        "meta_name":          "App name:",
        "meta_ver":           "Version (x.x.x.x):",
        "meta_company":       "Company:",
        "meta_desc":          "Description:",
        "meta_copy":          "Copyright:",
        "meta_def_desc":      "HTA application compiled to EXE",
        "about_title":        "About",
        "about_author":       "\U0001f9d1\u200d\U0001f4bb Author:",
        "about_firm":         "\U0001f3e2 Company:",
        "about_email":        "\u2709  E-mail:",
        "about_github":       "\U0001f517 GitHub:",
        "about_version":      "\U0001f4c6 Version:",
        "about_close":        "Close",
        "help_title":         "Help",
        "help_body": (
            "HTA \u2192 EXE Converter \u2014 User Guide\n"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n"
            "1. HTA File/Folder\n"
            "   Select an .hta file or project folder.\n"
            "   All assets (CSS, JS, images) will be\n"
            "   bundled automatically.\n\n"
            "2. Output Folder\n"
            "   Where the final .exe will be saved.\n\n"
            "3. Icon\n"
            "   Supported: .ico .png .jpg .bmp\n"
            "   (Pillow required for non-ICO formats)\n\n"
            "4. UPX\n"
            "   Compresses the EXE. Requires upx.exe\n"
            "   next to the app or in PATH.\n\n"
            "5. Metadata\n"
            "   Information embedded in the EXE\n"
            "   (version, company, copyright).\n\n"
            "Requirements:\n"
            "   pip install pyinstaller\n"
            "   pip install pillow  (optional)\n"
        ),
        "help_close":         "Close",
        "pin_on":             "Always on top: ON",
        "pin_off":            "Always on top: OFF",
        "lang_switch":        "PL",
        "log_upx_warn":       ("[WARN] UPX enabled but upx.exe not found! "
                               "Place upx.exe next to the app or install it in PATH."),
        "log_done":           "\n\u2714  Done: {}",
        "log_err":            "\n\u2718  Error: {}",
    },
}

_current_lang = "pl"

def tr(key: str, *args) -> str:
    """Zwraca przetlumaczony tekst dla biezacego jezyka."""
    text = TRANSLATIONS.get(_current_lang, TRANSLATIONS["pl"]).get(key, key)
    return text.format(*args) if args else text

def set_lang(lang: str):
    global _current_lang
    _current_lang = lang



# ─────────────────────────────────────────────
#  Kolory / fonty  (Aero Dark Pro palette)
# ─────────────────────────────────────────────

DARK_BG    = "#0d1117"   # głęboka czerń z odcieniem granatu
PANEL_BG   = "#111827"   # panel ciemny granat
ACCENT     = "#e94560"   # czerwień akcentowa
ACCENT2    = "#0f3460"   # głęboki niebieski
ACCENT3    = "#00b4d8"   # neonowy cyan (nowy akcent 3)
META_BG    = "#0a1020"   # tło panelu metadanych
ENTRY_BG   = "#080f1e"   # tło pól wejściowych
BORDER_COL = "#1a3a6a"   # kolor ramek
TEXT_LIGHT = "#e8eeff"   # prawie biały z odcieniem błękitu
TEXT_DIM   = "#5a6a8a"   # przyciemniony tekst
TEXT_MED   = "#8899bb"   # średni tekst
NEON_GREEN = "#39d353"   # zielony neon statusu
FONT_MONO  = ("Consolas", 8)
FONT_UI    = ("Segoe UI", 9)
FONT_HEAD  = ("Segoe UI Semibold", 9)
FONT_SMALL = ("Segoe UI", 7)

PIN_ON  = "📌"
PIN_OFF = "📍"

def _styled_entry(parent, var, **kw):
    """Pole tekstowe z efektem Aero glass."""
    e = tk.Entry(parent, textvariable=var, font=FONT_UI,
                 bg=ENTRY_BG, fg=TEXT_LIGHT,
                 insertbackground=ACCENT3,
                 relief="flat", bd=0,
                 highlightbackground=BORDER_COL,
                 highlightthickness=1,
                 selectbackground=ACCENT2,
                 selectforeground=TEXT_LIGHT,
                 **kw)
    def _on_focus_in(e):  e.widget.configure(highlightbackground=ACCENT3, highlightthickness=1)
    def _on_focus_out(e): e.widget.configure(highlightbackground=BORDER_COL, highlightthickness=1)
    e.bind("<FocusIn>",  _on_focus_in)
    e.bind("<FocusOut>", _on_focus_out)
    return e

def _styled_btn(parent, text, cmd, accent=False, danger=False, small=False):
    """Przycisk z efektem hover (podświetlenie krawędzi)."""
    bg  = ACCENT if danger else (ACCENT2 if not accent else "#1a4a80")
    abg = "#c0273e" if danger else ACCENT3
    fg  = TEXT_LIGHT
    font = FONT_SMALL if small else FONT_UI
    btn = tk.Button(parent, text=text, font=font,
                    bg=bg, fg=fg,
                    activebackground=abg, activeforeground="#ffffff",
                    relief="flat", bd=0,
                    padx=10 if not small else 6,
                    pady=4 if not small else 2,
                    cursor="hand2", command=cmd,
                    highlightbackground=BORDER_COL,
                    highlightthickness=1)
    def _hover_in(e):  btn.configure(highlightbackground=ACCENT3, highlightthickness=1)
    def _hover_out(e): btn.configure(highlightbackground=BORDER_COL, highlightthickness=1)
    btn.bind("<Enter>", _hover_in)
    btn.bind("<Leave>", _hover_out)
    return btn

# ─────────────────────────────────────────────
#  Informacje o autorze
# ─────────────────────────────────────────────

APP_NAME      = "HTA → EXE Konwerter"
APP_VERSION   = "1.0.0.0"
AUTHOR_NAME   = "Sebastian Januchowski"
AUTHOR_FIRM   = "polsoft.ITS™ London"
AUTHOR_EMAIL  = "polsoft.its@fastservice.com"
AUTHOR_GITHUB = "https://github.com/seb07uk"
AUTHOR_COPY   = "2026© Sebastian Januchowski. All rights reserved."



# ─────────────────────────────────────────────
#  Obsługa ikon: ico / png / jpg / bmp
# ─────────────────────────────────────────────

def prepare_icon(src_path: str, tmp_dir: str, log_cb) -> str | None:
    if not src_path or not os.path.isfile(src_path):
        return None
    ext = Path(src_path).suffix.lower()
    if ext == ".ico":
        return src_path
    if not _PILLOW:
        log_cb("[WARN] Pillow nie jest zainstalowany — ikona pominięta. pip install pillow")
        return None
    try:
        img = _PILImage.open(src_path).convert("RGBA")
        sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
        ico_path = os.path.join(tmp_dir, "_icon.ico")
        img.save(ico_path, format="ICO", sizes=sizes)
        log_cb(f"[INFO] Ikona skonwertowana: {Path(src_path).name} → .ico")
        return ico_path
    except Exception as e:
        log_cb(f"[WARN] Błąd konwersji ikony: {e}")
        return None


def load_icon_thumbnail(path: str, size: int = 20):
    if not path or not os.path.isfile(path) or not _PILLOW:
        return None
    try:
        img = _PILImage.open(path).convert("RGBA")
        img.thumbnail((size, size), _PILImage.LANCZOS)
        from PIL import ImageTk
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# ─────────────────────────────────────────────
#  Zbieranie plików projektu HTA
# ─────────────────────────────────────────────

def _collect_files(root_path: str) -> dict:
    files = {}
    root = Path(root_path)
    EXTS = {".hta",".html",".htm",".css",".js",".json",".xml",
            ".png",".jpg",".jpeg",".gif",".ico",".svg",".bmp",
            ".woff",".woff2",".ttf",".eot",".txt",".md"}
    if root.is_file():
        files[root.name] = root.read_bytes()
    else:
        for f in sorted(root.rglob("*")):
            if f.is_file() and f.suffix.lower() in EXTS:
                rel = f.relative_to(root).as_posix()
                try:
                    files[rel] = f.read_bytes()
                except Exception:
                    pass
    return files


def _find_hta_entry(files: dict) -> str:
    for k in files:
        if k.endswith(".hta"):
            return k
    for k in files:
        if k.endswith((".html", ".htm")):
            return k
    raise ValueError("Nie znaleziono pliku .HTA w projekcie!")


def _inline_external_refs(hta_src: str, base_dir: str, log_cb) -> str:
    def replace_script(m):
        src = m.group(1)
        if src.startswith(("http://","https://","//")):
            return m.group(0)
        fpath = os.path.join(base_dir, src.replace("/", os.sep))
        if os.path.isfile(fpath):
            log_cb(f"[INFO] Inline JS: {src}")
            code = Path(fpath).read_text(encoding="utf-8", errors="replace")
            return f"<script>\n{code}\n</script>"
        return m.group(0)

    def replace_link(m):
        href = m.group(1)
        if href.startswith(("http://","https://","//")):
            return m.group(0)
        fpath = os.path.join(base_dir, href.replace("/", os.sep))
        if os.path.isfile(fpath):
            log_cb(f"[INFO] Inline CSS: {href}")
            css = Path(fpath).read_text(encoding="utf-8", errors="replace")
            return f"<style>\n{css}\n</style>"
        return m.group(0)

    hta_src = re.sub(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>\s*</script>',
                     replace_script, hta_src, flags=re.IGNORECASE)
    hta_src = re.sub(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*/?>',
                     replace_link, hta_src, flags=re.IGNORECASE)
    return hta_src


# ─────────────────────────────────────────────
#  Główna konwersja
# ─────────────────────────────────────────────

def _find_upx_auto() -> str | None:
    """
    Szuka upx.exe w następującej kolejności:
      1. Katalog glowny aplikacji (obok skryptu / obok .exe po zamrozeniu)
      2. PATH systemowy
    Zwraca bezwzgledna sciezke lub None.
    """
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).resolve().parent

    for candidate in ("upx.exe", "upx"):
        local = app_dir / candidate
        if local.is_file():
            return str(local)

    return shutil.which("upx") or None


def _run_upx(exe_path: str, upx_path: str, log_cb) -> bool:
    """
    Kompresuje plik EXE przy uzyciu UPX.
    upx_path – sciezka do upx.exe, 'upx' (PATH) lub "" (auto-detekcja).
    Zwraca True jesli kompresja sie powiodla.
    """
    if not upx_path:
        upx_path = _find_upx_auto()
        if upx_path:
            log_cb(f"[INFO] UPX wykryty automatycznie: {upx_path}")
        else:
            log_cb("[WARN] UPX nie znaleziony (katalog aplikacji ani PATH) — kompresja pominieta.")
            return False

    if not os.path.isfile(upx_path):
        resolved = shutil.which(upx_path)
        if not resolved:
            log_cb(f"[WARN] UPX nie znaleziony: '{upx_path}' — kompresja pominieta.")
            return False
        upx_path = resolved

    log_cb(f"[INFO] Uruchamiam UPX: {upx_path}")
    size_before = os.path.getsize(exe_path)

    cmd = [upx_path, "--best", "--lzma", exe_path]
    _no_window = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            creationflags=_no_window,
        )
        for line in proc.stdout:
            s = line.rstrip()
            if s:
                log_cb(s)
        proc.wait()
    except FileNotFoundError:
        log_cb(f"[WARN] Nie można uruchomić UPX ({upx_path}) — kompresja pominięta.")
        return False

    if proc.returncode not in (0, 1):   # UPX zwraca 1 gdy plik jest już spakowany
        log_cb(f"[WARN] UPX zakończył się kodem {proc.returncode} — sprawdź log.")
        return False

    size_after = os.path.getsize(exe_path)
    saved_kb   = (size_before - size_after) // 1024
    ratio      = 100 * size_after / size_before if size_before else 100
    log_cb(f"[INFO] UPX: {size_before//1024} KB → {size_after//1024} KB "
           f"(zaoszczędzono {saved_kb} KB, {ratio:.1f}% rozmiaru oryginału)")
    return True


def convert(hta_path: str, output_dir: str, icon: str | None,
            meta: dict, log_callback,
            upx_enabled: bool = False, upx_path: str = ""):
    """
    meta: {name, version, company, description, copyright}
    Metadane są wstrzykiwane do .spec jako version_info (Windows VERSIONINFO).
    upx_enabled – czy skompresować wynikowy EXE przy użyciu UPX.
    upx_path    – ścieżka do upx.exe; jeśli puste, szukany w PATH.
    """
    hta_path   = os.path.abspath(hta_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    base = Path(hta_path)
    project_name = base.stem if base.is_file() else base.name
    base_dir     = str(base.parent if base.is_file() else base)

    temp_dir = tempfile.mkdtemp(prefix="hta2exe_")
    try:
        log_callback("[INFO] Zbieram pliki projektu…")
        files_raw = _collect_files(hta_path)
        if not files_raw:
            raise ValueError("Brak plików do osadzenia!")
        log_callback(f"[INFO] Znaleziono {len(files_raw)} plików.")

        entry = _find_hta_entry(files_raw)
        log_callback(f"[INFO] Punkt wejścia: {entry}")

        hta_src = files_raw[entry].decode("utf-8", errors="replace")
        log_callback("[INFO] Inline'uję lokalne zasoby…")
        hta_src = _inline_external_refs(hta_src, base_dir, log_callback)
        files_raw[entry] = hta_src.encode("utf-8")

        files_b64 = {k: base64.b64encode(v).decode() for k, v in files_raw.items()}
        log_callback(f"[INFO] Zakodowano {len(files_b64)} plików.")

        ico_path = prepare_icon(icon, temp_dir, log_callback)

        # ── Wrapper Python ──────────────────────────────────────────
        wrapper = f'''\
import os, base64, tempfile, subprocess, shutil, atexit
FILES = {repr(files_b64)}
ENTRY = {repr(entry)}
def main():
    tmp = tempfile.mkdtemp(prefix="hta_app_")
    atexit.register(shutil.rmtree, tmp, True)
    for rel, b64 in FILES.items():
        dest = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest) or tmp, exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(base64.b64decode(b64))
    hta_file = os.path.join(tmp, ENTRY.replace("/", os.sep))
    mshta = os.path.join(os.environ.get("SystemRoot", r"C:\\Windows"),
                         "system32", "mshta.exe")
    if not os.path.isfile(mshta):
        mshta = "mshta.exe"
    _no_win = 0x08000000  # CREATE_NO_WINDOW
    subprocess.Popen([mshta, hta_file], creationflags=_no_win).wait()
if __name__ == "__main__":
    main()
'''
        py_path = os.path.join(temp_dir, f"{project_name}.py")
        Path(py_path).write_text(wrapper, encoding="utf-8")

        # ── Plik metadanych version_info ────────────────────────────
        ver_str  = meta.get("version", "1.0.0.0").strip() or "1.0.0.0"
        ver_parts = (ver_str + ".0.0.0.0").split(".")[:4]
        try:
            ver_tuple = tuple(int(x) for x in ver_parts)
        except ValueError:
            ver_tuple = (1, 0, 0, 0)

        app_name  = meta.get("name",        project_name).strip() or project_name
        company   = meta.get("company",     "").strip()
        desc      = meta.get("description", "").strip()
        copy_r    = meta.get("copyright",   "").strip()

        version_file = None
        if any([app_name, company, desc, copy_r, ver_str != "1.0.0.0"]):
            vi = f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple},
    prodvers={ver_tuple},
    mask=0x3f, flags=0x0, OS=0x40004,
    fileType=0x1, subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringStruct(u'CompanyName',      u'{company}'),
        StringStruct(u'FileDescription',  u'{desc}'),
        StringStruct(u'FileVersion',      u'{ver_str}'),
        StringStruct(u'InternalName',     u'{app_name}'),
        StringStruct(u'LegalCopyright',   u'{copy_r}'),
        StringStruct(u'OriginalFilename', u'{app_name}.exe'),
        StringStruct(u'ProductName',      u'{app_name}'),
        StringStruct(u'ProductVersion',   u'{ver_str}'),
      ])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
            version_file = os.path.join(temp_dir, "version_info.txt")
            Path(version_file).write_text(vi, encoding="utf-8")
            log_callback(f"[INFO] Metadane: {app_name} v{ver_str}")

        # ── PyInstaller ─────────────────────────────────────────────
        log_callback("[INFO] Uruchamiam PyInstaller…")

        # Gdy aplikacja działa jako zamrożony EXE (PyInstaller),
        # sys.executable wskazuje na własny .exe, a nie na python.exe.
        # Musimy znaleźć prawdziwy interpreter Pythona.
        if getattr(sys, "frozen", False):
            python_exe = shutil.which("python") or shutil.which("python3")
            if not python_exe:
                # Próbuj py.exe (Python Launcher dla Windows)
                python_exe = shutil.which("py")
            if not python_exe:
                raise RuntimeError(
                    "Nie znaleziono interpretera Python w PATH!\n"
                    "Zainstaluj Python i upewnij się, że jest dostępny w PATH."
                )
            log_callback(f"[INFO] Używam Pythona: {python_exe}")
        else:
            python_exe = sys.executable

        cmd = [
            python_exe, "-m", "PyInstaller",
            "--onefile", "--noconsole",
            f"--distpath={output_dir}",
            f"--workpath={os.path.join(temp_dir, 'build')}",
            f"--specpath={temp_dir}",
            f"--name={app_name}",
        ]
        if ico_path:
            cmd.append(f"--icon={ico_path}")
        if version_file:
            cmd.append(f"--version-file={version_file}")
        cmd.append(py_path)

        _no_window = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace",
                                creationflags=_no_window)
        log_buf = []
        for line in proc.stdout:
            s = line.rstrip()
            log_buf.append(s)
            log_callback(s)
        proc.wait()

        log_text = "\n".join(log_buf)
        if proc.returncode != 0:
            if "PermissionError" in log_text or "WinError 5" in log_text:
                raise PermissionError(f"'{app_name}.exe' jest uruchomiony — zamknij i spróbuj ponownie.")
            if "No module named 'PyInstaller'" in log_text:
                raise RuntimeError("Brak PyInstaller!\npip install pyinstaller")
            raise RuntimeError(f"PyInstaller błąd (kod {proc.returncode})")

        exe_path = os.path.join(output_dir, f"{app_name}.exe")
        if not os.path.isfile(exe_path):
            raise FileNotFoundError(f"Brak pliku: {exe_path}")

        # ── UPX – kompresja (opcjonalna) ────────────────────────────
        if upx_enabled:
            _run_upx(exe_path, upx_path.strip(), log_callback)

        return exe_path

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ─────────────────────────────────────────────
#  Persystencja ustawień
# ─────────────────────────────────────────────

_CFG_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "hta2exe_gui"
_CFG_FILE = _CFG_DIR / "settings.json"

def _load_cfg() -> dict:
    try:
        return json.loads(_CFG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_cfg(data: dict):
    try:
        _CFG_DIR.mkdir(parents=True, exist_ok=True)
        _CFG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # ── Inicjalizacja stylu ttk (musi być po Tk.__init__) ─────────
        _s = ttk.Style(self)
        _s.theme_use("clam")
        _s.configure("TProgressbar",
                     troughcolor="#080f1e",
                     background="#00b4d8",
                     bordercolor="#111827",
                     lightcolor="#80e8ff",
                     darkcolor="#007090",
                     thickness=4)
        self._cfg        = _load_cfg()
        self._topmost    = False
        self._icon_thumb = None
        self._meta_open  = False
        self._last_exe   = None   # ścieżka ostatniego wygenerowanego exe
        self._lang       = self._cfg.get("lang", "pl")
        set_lang(self._lang)

        self.title("HTA-EXE Converter 1.0 Mini by Sebastian Januchowski")
        self.minsize(460, 540)
        self.resizable(True, True)
        self.configure(bg=DARK_BG)

        # ── Ikona okna (title bar) z pliku ICO ───────────────────────
        self._app_icon_img = None   # referencja PhotoImage (nie może być GC)
        _ico_candidates = [
            Path(__file__).resolve().parent / "HTA_Compiler-ico.ico",
        ]
        if getattr(sys, "frozen", False):
            _ico_candidates.insert(0, Path(sys.executable).parent / "HTA_Compiler-ico.ico")
        for _ico in _ico_candidates:
            if _ico.is_file():
                try:
                    self.iconbitmap(str(_ico))
                except Exception:
                    pass
                # Ładuj też przez PhotoImage (dla _hdr_icon_lbl w nagłówku)
                if _PILLOW:
                    try:
                        from PIL import ImageTk as _ITk
                        _pil = _PILImage.open(str(_ico)).convert("RGBA")
                        _pil.thumbnail((24, 24), _PILImage.LANCZOS)
                        self._app_icon_img = _ITk.PhotoImage(_pil)
                    except Exception:
                        pass
                break

        self._build_ui()

        geo = self._cfg.get("geometry")
        if geo:
            try:
                self.geometry(geo)
            except Exception:
                self._center()
        else:
            self.geometry("500x560")
            self._center()

        last_out = self._cfg.get("last_output_dir", "")
        if last_out and os.path.isdir(last_out):
            self.out_var.set(last_out)

        # Przywróć UPX
        self.upx_enabled_var.set(self._cfg.get("upx_enabled", False))
        self.upx_path_var.set(self._cfg.get("upx_path", ""))
        # Odswież status i ewentualnie stan pól
        if self.upx_enabled_var.get():
            self._on_upx_toggle()
        else:
            self._upx_refresh_status()

        # Przywróć metadane
        m = self._cfg.get("meta", {})
        self.meta_name_var.set(m.get("name", APP_NAME))
        self.meta_ver_var.set(m.get("version", APP_VERSION))
        self.meta_company_var.set(m.get("company", AUTHOR_FIRM))
        self.meta_desc_var.set(m.get("description", tr("meta_def_desc")))
        self.meta_copy_var.set(m.get("copyright", AUTHOR_COPY))

        if self._cfg.get("topmost", False):
            self._toggle_topmost(force=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ════════════════════════════════════════
    #  Budowanie UI
    # ════════════════════════════════════════

    def _build_ui(self):
        # ── Nagłówek Aero Glass 3D ────────────────────────────────────
        import math, time as _time
        HDR_H = 80
        hdr_canvas = tk.Canvas(self, height=HDR_H, bd=0, highlightthickness=0)
        hdr_canvas.pack(fill="x")

        self._anim_phase   = 0.0   # faza animacji (scan-line + particles)
        self._anim_id      = None
        self._banner_W     = 500

        def _lerp(a, b, t): return int(a + (b - a) * t)
        def _hex(r, g, b):  return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

        def _draw_banner(event=None):
            W = hdr_canvas.winfo_width() or 500
            self._banner_W = W
            ph = self._anim_phase
            hdr_canvas.delete("all")

            # ── 1. Tlo: ciemny granat, trzy-strefowy gradient ──────
            #    strefa A: top (bardzo ciemny, prawie czarny niebieski)
            #    strefa B: srodek (blekitny glass)
            #    strefa C: dol (ciemny)
            for i in range(HDR_H):
                t = i / HDR_H
                if t < 0.45:
                    s = t / 0.45
                    r = _lerp(0x04, 0x10, s)
                    g = _lerp(0x0a, 0x22, s)
                    b = _lerp(0x28, 0x55, s)
                elif t < 0.55:
                    s = (t - 0.45) / 0.10
                    r = _lerp(0x10, 0x1a, s)
                    g = _lerp(0x22, 0x30, s)
                    b = _lerp(0x55, 0x70, s)
                else:
                    s = (t - 0.55) / 0.45
                    r = _lerp(0x1a, 0x06, s)
                    g = _lerp(0x30, 0x10, s)
                    b = _lerp(0x70, 0x30, s)
                hdr_canvas.create_rectangle(0, i, W, i+1,
                                            fill=_hex(r,g,b), outline=_hex(r,g,b))

            # ── 2. Aero Glass: polprzezroczysty blask od gory ──────
            for i in range(int(HDR_H * 0.42)):
                alpha = (1 - i / (HDR_H * 0.42)) * 0.55
                v = int(255 * alpha)
                c = _hex(v, v + 10, v + 30)
                hdr_canvas.create_rectangle(0, i, W, i+1,
                                            fill=c, outline=c, stipple="gray50")

            # ── 3. Eliptyczny highlight (soczewka Aero) ────────────
            cx, cy = W // 2, int(HDR_H * 0.22)
            for step in range(18, 0, -1):
                alpha_t = step / 18
                rw = int(W * 0.55 * alpha_t)
                rh = int(HDR_H * 0.28 * alpha_t)
                bri = int(60 * (1 - alpha_t))
                col = _hex(bri + 140, bri + 155, bri + 185)
                hdr_canvas.create_oval(cx - rw, cy - rh, cx + rw, cy + rh,
                                       fill=col, outline="", stipple="gray25")

            # ── 4. Animowana linia skanujaca (neon sweep) ──────────
            scan_x = int((math.sin(ph * 0.7) * 0.5 + 0.5) * W)
            for dx, alpha_str in [(-2,"gray12"),(-1,"gray25"),(0,"gray50"),(1,"gray25"),(2,"gray12")]:
                sx = scan_x + dx
                if 0 <= sx < W:
                    hdr_canvas.create_rectangle(sx, 0, sx+1, HDR_H,
                                                fill="#aabbff", outline="",
                                                stipple=alpha_str)

            # ── 5. Lewy pasek akcentowy (czerwony 3D z gradient) ───
            for i in range(HDR_H):
                t = i / HDR_H
                r = _lerp(0xff, 0xcc, t)
                g = _lerp(0x55, 0x10, t)
                b = _lerp(0x70, 0x20, t)
                hdr_canvas.create_rectangle(0, i, 5, i+1,
                                            fill=_hex(r,g,b), outline=_hex(r,g,b))
            # highlight krawedzi lewego paska
            hdr_canvas.create_rectangle(0, 0, 2, HDR_H,
                                        fill="#ffaaaa", outline="", stipple="gray25")

            # ── 6. Prawa dekoracja: szklany badge EXE ──────────────
            bx1, by1, bx2, by2 = W-98, 10, W-10, HDR_H-10
            # tlo badge (ciemne szklane)
            for i in range(by1, by2):
                t = (i - by1) / (by2 - by1)
                r = _lerp(0x08, 0x14, t)
                g = _lerp(0x1a, 0x28, t)
                b = _lerp(0x44, 0x5c, t)
                hdr_canvas.create_rectangle(bx1, i, bx2, i+1,
                                            fill=_hex(r,g,b), outline=_hex(r,g,b))
            # glass top-highlight w badge
            hdr_canvas.create_rectangle(bx1, by1, bx2, by1 + (by2-by1)//3,
                                        fill="#9ab8e8", outline="", stipple="gray25")
            # ramka 3D badge
            hdr_canvas.create_rectangle(bx1, by1, bx2, by2,
                                        outline="#4488cc", width=1)
            hdr_canvas.create_rectangle(bx1+1, by1+1, bx2-1, by2-1,
                                        outline="#1a3a60", width=1)
            # napis EXE w badge — cien + glowny
            mx, my = (bx1+bx2)//2, (by1+by2)//2
            hdr_canvas.create_text(mx+1, my+2, text="EXE",
                                   font=("Segoe UI Black", 13),
                                   fill="#000a1a", anchor="center")
            hdr_canvas.create_text(mx, my, text="EXE",
                                   font=("Segoe UI Black", 13),
                                   fill="#c8dfff", anchor="center")
            # animowana kropka statusu (pulsujaca)
            pulse = 0.5 + 0.5 * math.sin(ph * 2.5)
            pcol = _hex(int(80+175*pulse), int(200+55*pulse), int(80+80*pulse))
            hdr_canvas.create_oval(bx1+6, by2-12, bx1+13, by2-5,
                                   fill=pcol, outline="")

            # ── 7. Pionowe linie dekoracyjne (subtelne) ────────────
            for lx in [W//4, W//2, 3*W//4]:
                hdr_canvas.create_rectangle(lx, 0, lx+1, HDR_H,
                                            fill="#ffffff", outline="", stipple="gray12")

            # ── 8. Cien tytulu (3D emboss wielowarstwowy) ──────────
            title_text = tr("app_title")
            tx, ty = 14, int(HDR_H * 0.36)
            for ox, oy, col in [(3,3,"#000008"),(2,2,"#000820"),
                                 (1,1,"#001540"),(0,1,"#002060")]:
                hdr_canvas.create_text(tx+ox, ty+oy, text=title_text,
                                       font=("Segoe UI Semibold", 15),
                                       fill=col, anchor="w")
            # highlight (jaśniejszy od gory — efekt 3D light source)
            hdr_canvas.create_text(tx-1, ty-1, text=title_text,
                                   font=("Segoe UI Semibold", 15),
                                   fill="#4466aa", anchor="w")
            # glowny bialy tytul
            hdr_canvas.create_text(tx, ty, text=title_text,
                                   font=("Segoe UI Semibold", 15),
                                   fill="#f0f4ff", anchor="w")

            # ── 9. "mini" za tytulem malymi literkami ──────────────
            tmp = tk.Label(self, text=title_text, font=("Segoe UI Semibold", 15))
            tmp.update_idletasks()
            tw = tmp.winfo_reqwidth()
            tmp.destroy()
            hdr_canvas.create_text(tx + tw + 5, ty + 4,
                                   text="mini",
                                   font=("Segoe UI", 8),
                                   fill="#7799cc", anchor="w")

            # ── 10. Podtytul ze swiecacym akcentem ─────────────────
            sub_glow = 0.5 + 0.5 * math.sin(ph * 1.8 + 1.0)
            sr = int(0x44 + 0x22 * sub_glow)
            sg = int(0x66 + 0x22 * sub_glow)
            sb_c = int(0xaa + 0x33 * sub_glow)
            hdr_canvas.create_text(tx+1, ty+21, text=tr("hdr_subtitle"),
                                   font=("Segoe UI", 8), fill="#00060e", anchor="w")
            hdr_canvas.create_text(tx, ty+20, text=tr("hdr_subtitle"),
                                   font=("Segoe UI", 8),
                                   fill=_hex(sr, sg, sb_c), anchor="w")

            # ── 11. Dolna linia neonowa (czerwona z blyskiem) ──────
            glow = 0.5 + 0.5 * math.sin(ph * 3.0)
            nr = int(0xe9 + 0x10 * glow)
            ng = int(0x20 + 0x20 * glow)
            nb = int(0x40 + 0x20 * glow)
            hdr_canvas.create_rectangle(0, HDR_H-2, W, HDR_H,
                                        fill=_hex(nr,ng,nb), outline="")
            hdr_canvas.create_rectangle(0, HDR_H-2, W, HDR_H-1,
                                        fill="#ff99aa", outline="", stipple="gray50")

            # ── 12. Particles: drobne iskry ────────────────────────
            import random as _rnd
            _rnd.seed(42)
            p_max_x = max(6, W - 105)
            p_max_y = max(4, HDR_H - 5)
            for _ in range(12):
                px = _rnd.randint(5, p_max_x)
                py = _rnd.randint(3, p_max_y)
                base_phase = _rnd.random() * 6.28
                brightness = 0.3 + 0.7 * max(0, math.sin(ph * 2.0 + base_phase))
                if brightness > 0.5:
                    bv = int(brightness * 180)
                    hdr_canvas.create_oval(px-1, py-1, px+1, py+1,
                                           fill=_hex(bv, bv+20, bv+60), outline="")

        hdr_canvas.bind("<Configure>", _draw_banner)

        # ── Animacja bannera ─────────────────────────────────────────
        def _animate():
            self._anim_phase += 0.07
            _draw_banner()
            self._anim_id = self.after(55, _animate)   # ~18 fps

        self.after(20, _animate)
        self._hdr_canvas    = hdr_canvas
        self._draw_banner   = _draw_banner

        # Dummy vars dla kompatybilnosci z _rebuild_ui
        self._hdr_title_lbl = None
        self._hdr_sub_lbl2  = None





        # ── Panel opcji (formularz) ───────────────────────────────────
        opt = tk.Frame(self, bg=PANEL_BG, padx=10, pady=8)
        opt.pack(fill="x")
        # cienka górna linia akcentowa nad formularzem
        tk.Frame(self, bg=ACCENT3, height=1).pack(fill="x", before=opt)

        self._row_hta(opt)
        self._row_out(opt)
        self._row_icon(opt)
        self._row_upx(opt)
        self._row_buttons(opt)   # ← Konwertuj | Folder EXE | Metadane

        # ── Panel metadanych (początkowo ukryty) ─────────────────────
        self._meta_frame = tk.Frame(self, bg=META_BG, padx=10, pady=8)
        # nie pack() — pojawi się po kliknięciu przycisku Metadane

        self._build_meta_panel(self._meta_frame)

        # ── Separator neonowy z gradientem ────────────────────────────
        sep_c = tk.Canvas(self, height=3, bd=0, highlightthickness=0)
        sep_c.pack(fill="x")
        def _draw_sep(ev=None):
            W2 = sep_c.winfo_width() or 500
            sep_c.delete("all")
            for ix in range(W2):
                t = ix / W2
                r = int(0xe9 * (1-t) + 0x00 * t)
                g = int(0x45 * (1-t) + 0xb4 * t)
                b = int(0x60 * (1-t) + 0xd8 * t)
                col = f"#{r:02x}{g:02x}{b:02x}"
                sep_c.create_rectangle(ix, 0, ix+1, 3, fill=col, outline=col)
        sep_c.bind("<Configure>", _draw_sep)
        self.after(15, _draw_sep)

        # ── Dziennik ─────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=DARK_BG, padx=6, pady=4)
        log_frame.pack(fill="both", expand=True)

        # Nagłówek logu z ikoną
        log_hdr = tk.Frame(log_frame, bg=DARK_BG)
        log_hdr.pack(fill="x", pady=(0,3))
        tk.Label(log_hdr, text="◈", font=("Segoe UI", 9),
                 bg=DARK_BG, fg=ACCENT3).pack(side="left")
        tk.Label(log_hdr, text=f"  {tr('log_header')}",
                 font=FONT_HEAD, bg=DARK_BG, fg=TEXT_MED).pack(side="left")

        # Ramka z podwójnym obramowaniem neonowym
        outer = tk.Frame(log_frame, bg=ACCENT3, padx=1, pady=1)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=DARK_BG, padx=1, pady=1)
        inner.pack(fill="both", expand=True)
        txt_frame = tk.Frame(inner, bg="#060c18")
        txt_frame.pack(fill="both", expand=True)

        self.log = tk.Text(
            txt_frame, font=FONT_MONO,
            bg="#060c18", fg="#b8cce4",
            insertbackground=ACCENT3,
            selectbackground=ACCENT2,
            selectforeground=TEXT_LIGHT,
            relief="flat", bd=0, wrap="word", state="disabled",
        )
        self.log.tag_configure("err",  foreground="#ff6b6b")
        self.log.tag_configure("warn", foreground="#ffd166")
        self.log.tag_configure("ok",   foreground="#06d6a0")
        self.log.tag_configure("info", foreground="#00b4d8")

        sb = ttk.Scrollbar(txt_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True, padx=3, pady=3)

        # ── Pasek statusu ─────────────────────────────────────────────
        self._build_statusbar()

    # ── Panel metadanych ─────────────────────────────────────────────

    def _build_meta_panel(self, parent):
        """Buduje formularz metadanych wewnątrz przekazanego Frame."""
        hdr_f = tk.Frame(parent, bg=META_BG)
        hdr_f.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        tk.Label(hdr_f, text="◈", font=("Segoe UI", 9),
                 bg=META_BG, fg=ACCENT3).pack(side="left")
        tk.Label(hdr_f, text=f"  {tr('meta_title')}",
                 font=FONT_HEAD, bg=META_BG, fg=TEXT_MED).pack(side="left")

        fields = [
            (tr("meta_name"),    "meta_name_var"),
            (tr("meta_ver"),     "meta_ver_var"),
            (tr("meta_company"), "meta_company_var"),
            (tr("meta_desc"),    "meta_desc_var"),
            (tr("meta_copy"),    "meta_copy_var"),
        ]

        for i, (label, attr) in enumerate(fields, start=1):
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Label(parent, text=label, font=FONT_SMALL, bg=META_BG,
                     fg=TEXT_MED, anchor="e", width=18).grid(
                row=i, column=0, sticky="e", padx=(0, 6), pady=3)
            _styled_entry(parent, var).grid(
                row=i, column=1, sticky="ew", ipady=3, pady=2)

        parent.columnconfigure(1, weight=1)

    # ── Pasek statusu ─────────────────────────────────────────────────

    def _show_about(self):
        """Okno 'O programie' z danymi autora."""
        win = tk.Toplevel(self)
        win.title(tr("about_title"))
        win.configure(bg=DARK_BG)
        win.resizable(False, False)
        win.wm_attributes("-topmost", True)

        # Naglowek
        hdr = tk.Frame(win, bg=ACCENT2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📄  {tr('app_title')}",
                 font=("Segoe UI Semibold", 11), bg=ACCENT2,
                 fg=TEXT_LIGHT).pack(side="left", padx=14, pady=8)

        # Separator
        tk.Frame(win, bg=ACCENT, height=2).pack(fill="x")

        # Informacje
        body = tk.Frame(win, bg=DARK_BG, padx=20, pady=14)
        body.pack(fill="both")

        rows = [
            (tr("about_author"),   AUTHOR_NAME),
            (tr("about_firm"),    AUTHOR_FIRM),
            (tr("about_email"),   AUTHOR_EMAIL),
            (tr("about_github"),  AUTHOR_GITHUB),
            (tr("about_version"), APP_VERSION),
        ]

        for label, value in rows:
            row = tk.Frame(body, bg=DARK_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 9),
                     bg=DARK_BG, fg=TEXT_DIM, width=13, anchor="e").pack(side="left")
            lbl = tk.Label(row, text=value, font=("Segoe UI Semibold", 9),
                           bg=DARK_BG, fg=TEXT_LIGHT, anchor="w", cursor="hand2")
            lbl.pack(side="left", padx=(8, 0))
            # Klikalne linki
            if value.startswith("http") or "@" in value:
                import webbrowser
                url = value if value.startswith("http") else f"mailto:{value}"
                lbl.configure(fg="#5599ff")
                lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
                lbl.bind("<Enter>", lambda e, l=lbl: l.configure(fg="#88bbff"))
                lbl.bind("<Leave>", lambda e, l=lbl: l.configure(fg="#5599ff"))

        # Separator
        tk.Frame(win, bg=ACCENT2, height=1).pack(fill="x", padx=20)

        # Copyright
        copy_frame = tk.Frame(win, bg=DARK_BG, pady=8)
        copy_frame.pack(fill="x")
        tk.Label(copy_frame, text=AUTHOR_COPY,
                 font=("Segoe UI", 8), bg=DARK_BG,
                 fg=TEXT_DIM).pack()

        # Przycisk zamknij
        tk.Button(
            win, text=tr("about_close"), font=FONT_UI,
            bg=ACCENT2, fg=TEXT_LIGHT,
            activebackground=ACCENT, activeforeground=TEXT_LIGHT,
            relief="flat", bd=0, padx=20, pady=4,
            cursor="hand2", command=win.destroy,
        ).pack(pady=(0, 14))

        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width()  - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        win.geometry(f"+{x}+{y}")

    # ── Pasek statusu ──────────────────────────────────────────────────

    def _toggle_lang(self):
        """Przelacza jezyk PL/EN i przebudowuje UI."""
        self._lang = "en" if self._lang == "pl" else "pl"
        set_lang(self._lang)
        self._rebuild_ui()

    def _rebuild_ui(self):
        """Przebudowuje caly interfejs po zmianie jezyka."""
        # Zapisz stan przed zniszczeniem
        hta_val  = self.hta_var.get()
        out_val  = self.out_var.get()
        ico_val  = self.ico_var.get()
        upx_en   = self.upx_enabled_var.get()
        meta_n   = self.meta_name_var.get()
        meta_v   = self.meta_ver_var.get()
        meta_c   = self.meta_company_var.get()
        meta_d   = self.meta_desc_var.get()
        meta_cp  = self.meta_copy_var.get()
        was_meta = self._meta_open

        # Zatrzymaj animacje bannera przed zniszczeniem
        if getattr(self, '_anim_id', None):
            self.after_cancel(self._anim_id)
            self._anim_id = None

        # Zniszcz wszystkie widgety poza oknem
        for w in self.winfo_children():
            w.destroy()

        # Reset flag
        self._meta_open  = False
        self._icon_thumb = None
        self._pin_tip    = None
        self._timer_id   = None
        self._start_ts   = None

        # Przebuduj UI
        self._build_ui()

        # Przywroc wartosci
        self.hta_var.set(hta_val)
        self.out_var.set(out_val)
        self.ico_var.set(ico_val)
        self.upx_enabled_var.set(upx_en)
        self.meta_name_var.set(meta_n)
        self.meta_ver_var.set(meta_v)
        self.meta_company_var.set(meta_c)
        self.meta_desc_var.set(meta_d)
        self.meta_copy_var.set(meta_cp)
        self._upx_refresh_status()
        if was_meta:
            self._toggle_meta()

        self.title("HTA-EXE Converter 1.0 Mini by Sebastian Januchowski")
        if self._last_exe:
            self.btn_folder.configure(state="normal")
        self.status_var.set(tr("status_ready"))

    def _show_help(self):
        """Okno pomocy z instrukcja obslugi."""
        win = tk.Toplevel(self)
        win.title(tr("help_title"))
        win.configure(bg=DARK_BG)
        win.resizable(False, False)
        win.wm_attributes("-topmost", True)

        # Naglowek
        hdr = tk.Frame(win, bg=ACCENT2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"❓  {tr('help_title')}",
                 font=("Segoe UI Semibold", 11), bg=ACCENT2,
                 fg=TEXT_LIGHT).pack(side="left", padx=14, pady=8)

        tk.Frame(win, bg=ACCENT, height=2).pack(fill="x")

        # Tresc
        body = tk.Frame(win, bg=DARK_BG, padx=16, pady=12)
        body.pack(fill="both")

        txt = tk.Text(
            body, font=FONT_MONO,
            bg="#060c18", fg="#b8cce4",
            relief="flat", bd=0, wrap="word",
            width=52, height=24,
            state="normal",
        )
        txt.insert("end", tr("help_body"))
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)

        tk.Frame(win, bg=ACCENT2, height=1).pack(fill="x", padx=20)

        tk.Button(
            win, text=tr("help_close"), font=FONT_UI,
            bg=ACCENT2, fg=TEXT_LIGHT,
            activebackground=ACCENT, activeforeground=TEXT_LIGHT,
            relief="flat", bd=0, padx=20, pady=4,
            cursor="hand2", command=win.destroy,
        ).pack(pady=(8, 14))

        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width()  - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        win.geometry(f"+{x}+{y}")

    def _build_statusbar(self):
        SB_BG = "#080d14"
        # górna linia statusbara (gradient)
        top_line = tk.Canvas(self, height=1, bd=0, highlightthickness=0, bg=ACCENT2)
        top_line.pack(fill="x", side="bottom")
        sb = tk.Frame(self, bg=SB_BG, height=26)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        # ── Lewa: kropka statusu + tekst ──────────────────────────────
        left = tk.Frame(sb, bg=SB_BG)
        left.pack(side="left", fill="y", padx=(4,0))

        self._status_icon_var = tk.StringVar(value="●")
        self._status_icon_lbl = tk.Label(
            left, textvariable=self._status_icon_var,
            font=("Segoe UI", 8), bg=SB_BG, fg=NEON_GREEN, padx=4)
        self._status_icon_lbl.pack(side="left", fill="y")

        self.status_var = tk.StringVar(value=tr("status_ready"))
        tk.Label(left, textvariable=self.status_var,
                 font=FONT_SMALL, bg=SB_BG,
                 fg=TEXT_MED, anchor="w").pack(side="left", fill="y")

        # ── Prawa strona ───────────────────────────────────────────────
        def _sb_sep():
            tk.Frame(sb, bg=BORDER_COL, width=1).pack(side="right", fill="y", pady=5)

        # 📌 Pinezka
        self._pin_lbl = tk.Label(
            sb, text=PIN_OFF, font=("Segoe UI", 10),
            bg=SB_BG, fg=TEXT_DIM, padx=5, cursor="hand2")
        self._pin_lbl.pack(side="right", fill="y")
        self._pin_lbl.bind("<Button-1>", lambda e: self._toggle_topmost())
        self._pin_lbl.bind("<Enter>", self._pin_hover_on)
        self._pin_lbl.bind("<Leave>", self._pin_hover_off)
        self._pin_tip = None
        _sb_sep()

        # 🌐 Język  (neonowy badge)
        self._lang_btn = tk.Label(
            sb, text=tr("lang_switch"),
            font=("Segoe UI Semibold", 7),
            bg="#0a2040", fg=ACCENT3,
            padx=6, pady=0, cursor="hand2",
            relief="flat",
            highlightbackground=ACCENT3, highlightthickness=1)
        self._lang_btn.pack(side="right", fill="y", pady=5, padx=3)
        self._lang_btn.bind("<Button-1>", lambda e: self._toggle_lang())
        self._lang_btn.bind("<Enter>", lambda e: self._lang_btn.configure(bg=ACCENT3, fg="#000"))
        self._lang_btn.bind("<Leave>", lambda e: self._lang_btn.configure(bg="#0a2040", fg=ACCENT3))

        # ❓ Pomoc
        _help_lbl = tk.Label(sb, text="❓", font=("Segoe UI", 9),
                              bg=SB_BG, fg=TEXT_DIM, padx=4, cursor="hand2")
        _help_lbl.pack(side="right", fill="y")
        _help_lbl.bind("<Button-1>", lambda e: self._show_help())
        _help_lbl.bind("<Enter>", lambda e: _help_lbl.configure(fg=ACCENT3))
        _help_lbl.bind("<Leave>", lambda e: _help_lbl.configure(fg=TEXT_DIM))

        # ⓘ About
        _about_lbl = tk.Label(sb, text="ⓘ", font=("Segoe UI", 9),
                               bg=SB_BG, fg=TEXT_DIM, padx=4, cursor="hand2")
        _about_lbl.pack(side="right", fill="y")
        _about_lbl.bind("<Button-1>", lambda e: self._show_about())
        _about_lbl.bind("<Enter>", lambda e: _about_lbl.configure(fg=ACCENT3))
        _about_lbl.bind("<Leave>", lambda e: _about_lbl.configure(fg=TEXT_DIM))
        _sb_sep()

        # ⏱ Zegar
        self._elapsed_var = tk.StringVar(value="")
        tk.Label(sb, textvariable=self._elapsed_var,
                 font=("Consolas", 7), bg=SB_BG,
                 fg=TEXT_DIM, padx=5).pack(side="right", fill="y")
        _sb_sep()

        # Nazwa pliku
        self._file_var = tk.StringVar(value="")
        tk.Label(sb, textvariable=self._file_var,
                 font=FONT_SMALL, bg=SB_BG,
                 fg=ACCENT3).pack(side="right", padx=5, fill="y")

        self._timer_id = None
        self._start_ts = None

    # ════════════════════════════════════════
    #  Wiersze formularza
    # ════════════════════════════════════════

    def _lbl(self, parent, text, row):
        tk.Label(parent, text=text, font=FONT_UI, bg=PANEL_BG,
                 fg=TEXT_MED, width=14, anchor="e").grid(
            row=row, column=0, sticky="e", pady=3, padx=(0, 6))

    def _entry(self, parent, var, row):
        e = _styled_entry(parent, var)
        e.grid(row=row, column=1, sticky="ew", ipady=3)
        parent.columnconfigure(1, weight=1)
        return e

    def _mk_btn(self, parent, text, cmd, bg=None, danger=False):
        return _styled_btn(parent, text, cmd, danger=danger)

    def _row_out(self, p):
        self.out_var = tk.StringVar()
        self._lbl(p, tr("lbl_out"), 1)
        self._entry(p, self.out_var, 1)
        self._mk_btn(p, tr("btn_browse"), self._pick_out).grid(
            row=1, column=2, padx=(5,0), pady=2, sticky="ew")

    def _row_icon(self, p):
        self.ico_var = tk.StringVar()
        self.ico_var.trace_add("write", self._on_icon_changed)
        self._lbl(p, tr("lbl_icon"), 2)

        ico_frame = tk.Frame(p, bg=PANEL_BG)
        ico_frame.grid(row=2, column=1, sticky="ew")
        ico_frame.columnconfigure(1, weight=1)

        self._ico_thumb_lbl = tk.Label(ico_frame, bg=PANEL_BG, width=2, anchor="center")
        self._ico_thumb_lbl.grid(row=0, column=0, padx=(0, 3))

        _styled_entry(ico_frame, self.ico_var).grid(row=0, column=1, sticky="ew", ipady=3)

        self._mk_btn(p, tr("btn_browse"), self._pick_ico).grid(
            row=2, column=2, padx=(5,0), pady=2, sticky="ew")

    def _row_upx(self, p):
        """Wiersz UPX: tylko przelacznik ON/OFF + ikona statusu."""
        self.upx_enabled_var = tk.BooleanVar(value=False)
        self.upx_path_var    = tk.StringVar(value="")  # wewnetrzne – auto

        # Lewa kolumna: label
        tk.Label(p, text=tr("lbl_upx"), font=FONT_UI,
                 bg=PANEL_BG, fg=TEXT_MED, width=14, anchor="e").grid(
            row=3, column=0, sticky="e", pady=3, padx=(0, 6))
        # Srodkowa kolumna: checkbox + ikona statusu + info-tekst
        mid = tk.Frame(p, bg=PANEL_BG)
        mid.grid(row=3, column=1, columnspan=2, sticky="ew")

        self._upx_chk = tk.Checkbutton(
            mid, variable=self.upx_enabled_var,
            text=tr("upx_chk"),
            font=FONT_SMALL,
            bg=PANEL_BG, fg=TEXT_MED,
            activebackground=PANEL_BG, activeforeground=TEXT_LIGHT,
            selectcolor=ENTRY_BG,
            relief="flat", bd=0, cursor="hand2",
            command=self._on_upx_toggle,
        )
        self._upx_chk.pack(side="left")

        self._upx_status_lbl = tk.Label(
            mid, text="", font=("Segoe UI", 9),
            bg=PANEL_BG, width=2, anchor="center",
        )
        self._upx_status_lbl.pack(side="left", padx=(8, 0))

        self._upx_info_lbl = tk.Label(
            mid, text="", font=FONT_SMALL,
            bg=PANEL_BG, fg=TEXT_DIM, anchor="w",
        )
        self._upx_info_lbl.pack(side="left", padx=(2, 0))

        # Wykryj UPX od razu przy starcie
        self._upx_refresh_status()

    def _upx_refresh_status(self):
        """Sprawdza dostepnosc UPX i aktualizuje ikone + info-tekst."""
        detected = _find_upx_auto()
        if detected:
            self._upx_status_lbl.configure(text="✔", fg=NEON_GREEN)
            self._upx_info_lbl.configure(text=Path(detected).name, fg=NEON_GREEN)
            self.upx_path_var.set(detected)
        else:
            self._upx_status_lbl.configure(text="✘", fg="#e94560")
            self._upx_info_lbl.configure(
                text=tr("upx_not_found"), fg="#e94560")
            self.upx_path_var.set("")

    def _on_upx_toggle(self):
        """Logguje ostrzezenie jesli UPX wlaczony, ale niedostepny."""
        if self.upx_enabled_var.get() and not self.upx_path_var.get():
            self._log("[WARN] UPX wlaczony, ale upx.exe nie znaleziony! "
                      "Umiec upx.exe obok aplikacji lub zainstaluj w PATH.")

    def _row_buttons(self, p):
        """Wiersz: [▶ Konwertuj]  [📁 Folder EXE]  [📋 Metadane]"""
        bf = tk.Frame(p, bg=PANEL_BG)
        bf.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 3))

        # ▶ Konwertuj  (czerwony – akcja główna)
        self.btn = tk.Button(
            bf, text=tr("btn_convert"),
            font=("Segoe UI Semibold", 9),
            bg=ACCENT, fg="#ffffff",
            activebackground="#c0273e", activeforeground="#ffffff",
            relief="flat", bd=0, padx=14, pady=5,
            cursor="hand2", command=self._start,
            highlightbackground=ACCENT, highlightthickness=1,
        )
        self.btn.pack(side="left")
        def _btn_hi(e):  self.btn.configure(highlightbackground="#ff8099")
        def _btn_ho(e):  self.btn.configure(highlightbackground=ACCENT)
        self.btn.bind("<Enter>", _btn_hi)
        self.btn.bind("<Leave>", _btn_ho)

        # 📁 Otwórz folder EXE
        self.btn_folder = _styled_btn(bf, tr("btn_folder"),
                                      self._open_output_folder)
        self.btn_folder.configure(state="disabled", pady=5)
        self.btn_folder.pack(side="left", padx=(6, 0))

        # 📋 Metadane (toggle)
        self.btn_meta = _styled_btn(bf, tr("btn_meta"), self._toggle_meta)
        self.btn_meta.configure(pady=5)
        self.btn_meta.pack(side="left", padx=(6, 0))

        # ── Progress bar z gradientem (neon cyan) ─────────────────────
        pf = tk.Frame(p, bg=PANEL_BG)
        pf.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(4, 2))

        self.progress = ttk.Progressbar(pf, mode="indeterminate",
                                        style="TProgressbar")
        self.progress.pack(fill="x", expand=True)

    # ════════════════════════════════════════
    #  Panel metadanych – toggle
    # ════════════════════════════════════════

    def _toggle_meta(self):
        self._meta_open = not self._meta_open
        if self._meta_open:
            # Wstaw panel metadanych po opt (przed separatorem ACCENT)
            # Używamy place-based pack order trick:
            self._meta_frame.pack(fill="x", after=self._opt_ref)
            self.btn_meta.configure(text=tr("btn_meta_open"), fg=TEXT_LIGHT, bg="#1e3a5f")
        else:
            self._meta_frame.pack_forget()
            self.btn_meta.configure(text=tr("btn_meta"), bg=ACCENT2)

    # ════════════════════════════════════════
    #  Topmost / pin
    # ════════════════════════════════════════

    def _toggle_topmost(self, force=False):
        if force:
            self._topmost = True
        else:
            self._topmost = not self._topmost
        self.wm_attributes("-topmost", self._topmost)
        if self._topmost:
            self._pin_lbl.configure(text=PIN_ON,  fg="#f0a500")
        else:
            self._pin_lbl.configure(text=PIN_OFF, fg=TEXT_DIM)

    def _pin_hover_on(self, event=None):
        tip = tr("pin_on") if self._topmost else tr("pin_off")
        self._pin_tip = tk.Toplevel(self)
        self._pin_tip.wm_overrideredirect(True)
        self._pin_tip.wm_attributes("-topmost", True)
        x = self._pin_lbl.winfo_rootx()
        y = self._pin_lbl.winfo_rooty() - 22
        self._pin_tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._pin_tip, text=tip, font=("Segoe UI", 8),
                 bg="#2a2a4a", fg=TEXT_LIGHT, padx=6, pady=2).pack()

    def _pin_hover_off(self, event=None):
        if self._pin_tip:
            self._pin_tip.destroy()
            self._pin_tip = None

    # ════════════════════════════════════════
    #  Dialogi / pick
    # ════════════════════════════════════════

    def _on_close(self):
        self._cfg["geometry"] = self.geometry()
        self._cfg["topmost"]  = self._topmost
        out = self.out_var.get().strip()
        if out:
            self._cfg["last_output_dir"] = out
        self._cfg["meta"] = {
            "name":        self.meta_name_var.get(),
            "version":     self.meta_ver_var.get(),
            "company":     self.meta_company_var.get(),
            "description": self.meta_desc_var.get(),
            "copyright":   self.meta_copy_var.get(),
        }
        self._cfg["upx_enabled"] = self.upx_enabled_var.get()
        self._cfg["upx_path"]    = self.upx_path_var.get()
        self._cfg["lang"]        = self._lang
        _save_cfg(self._cfg)
        self.destroy()

    def _pick_hta_file(self):
        path = filedialog.askopenfilename(
            title=tr("lbl_hta"),
            filetypes=[("HTA / HTML", "*.hta *.html *.htm"), ("All", "*.*")])
        if path:
            self.hta_var.set(path)
            if not self.out_var.get():
                self.out_var.set(os.path.dirname(path))

    def _pick_hta_folder(self):
        path = filedialog.askdirectory(title=tr("lbl_hta"))
        if path:
            self.hta_var.set(path)
            if not self.out_var.get():
                self.out_var.set(os.path.dirname(path))

    def _pick_out(self):
        path = filedialog.askdirectory(title=tr("lbl_out"))
        if path:
            self.out_var.set(path)
            self._cfg["last_output_dir"] = path
            _save_cfg(self._cfg)

    def _pick_ico(self):
        path = filedialog.askopenfilename(
            title=tr("lbl_icon"),
            filetypes=[
                ("Images / Icons", "*.ico *.png *.jpg *.jpeg *.bmp"),
                ("ICO",  "*.ico"), ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp"),
                ("All", "*.*"),
            ])
        if path:
            self.ico_var.set(path)

    def _on_icon_changed(self, *_):
        path  = self.ico_var.get().strip()
        thumb = load_icon_thumbnail(path, size=20)
        if thumb:
            self._icon_thumb = thumb
            self._ico_thumb_lbl.configure(image=thumb, text="")
        else:
            self._icon_thumb = None
            if path and os.path.isfile(path):
                ext = Path(path).suffix.upper().lstrip(".")[:3]
                self._ico_thumb_lbl.configure(image="", text=ext,
                                              font=("Segoe UI", 6), fg=TEXT_DIM)
            else:
                self._ico_thumb_lbl.configure(image="", text="")

    def _open_output_folder(self):
        """Otwiera folder zawierający ostatnio wygenerowany .exe."""
        target = None
        if self._last_exe and os.path.isfile(self._last_exe):
            target = os.path.dirname(self._last_exe)
        else:
            target = self.out_var.get().strip()
        if target and os.path.isdir(target):
            os.startfile(target)
        else:
            messagebox.showinfo(tr("info_no_folder_t"), tr("info_no_folder_m"))

    # ════════════════════════════════════════
    #  Konwersja
    # ════════════════════════════════════════

    def _start(self):
        hta = self.hta_var.get().strip()
        out = self.out_var.get().strip()

        if not hta:
            messagebox.showwarning(tr("warn_no_input_t"), tr("warn_no_input_m"))
            return
        if not os.path.exists(hta):
            messagebox.showerror(tr("err_no_path_t"), tr("err_no_path_m", hta))
            return
        if not out:
            out = os.path.dirname(os.path.abspath(hta))
            self.out_var.set(out)

        # Ustal nazwę z metadanych lub z pliku
        app_name = self.meta_name_var.get().strip()
        if not app_name:
            base = Path(hta)
            app_name = base.stem if base.is_file() else base.name

        exe_path = os.path.join(out, f"{app_name}.exe")
        if os.path.isfile(exe_path):
            if not messagebox.askyesno(tr("ask_overwrite_t"),
                                       tr("ask_overwrite_m", exe_path),
                                       icon="warning", default="no"):
                self.status_var.set(tr("status_cancelled"))
                return

        meta = {
            "name":        self.meta_name_var.get().strip(),
            "version":     self.meta_ver_var.get().strip(),
            "company":     self.meta_company_var.get().strip(),
            "description": self.meta_desc_var.get().strip(),
            "copyright":   self.meta_copy_var.get().strip(),
        }

        self._log_clear()
        self._set_busy(True)

        def worker():
            try:
                exe = convert(
                    hta_path=hta, output_dir=out,
                    icon=self.ico_var.get().strip() or None,
                    meta=meta, log_callback=self._log,
                    upx_enabled=self.upx_enabled_var.get(),
                    upx_path=self.upx_path_var.get().strip(),
                )
                self.after(0, self._done_ok, exe)
            except Exception as e:
                self.after(0, self._done_err, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _done_ok(self, exe_path):
        self._last_exe = exe_path
        self._set_busy(False)
        self._log(tr("log_done", exe_path))
        self.status_var.set(f"✔  {os.path.basename(exe_path)}")
        self._status_icon_var.set("●")
        self._status_icon_lbl.configure(fg=NEON_GREEN)
        self._file_var.set(os.path.basename(exe_path))
        self.btn_folder.configure(state="normal")
        messagebox.showinfo(tr("ok_success_t"), tr("ok_success_m", exe_path))

    def _done_err(self, msg):
        self._set_busy(False)
        self._log(tr("log_err", msg))
        self.status_var.set(tr("err_conv_t"))
        self._status_icon_var.set("●")
        self._status_icon_lbl.configure(fg="#e94560")
        self._file_var.set("")
        messagebox.showerror(tr("err_conv_t"), msg)

    # ════════════════════════════════════════
    #  Narzędzia / log
    # ════════════════════════════════════════

    def _set_busy(self, busy: bool):
        if busy:
            self.btn.configure(state="disabled", text=tr("btn_converting"))
            self.progress.start(12)
            self.status_var.set(tr("status_converting"))
            self._status_icon_lbl.configure(fg="#f0a500")
            self._status_icon_var.set("◉")
            self._file_var.set(os.path.basename(self.hta_var.get().strip()))
            import time as _t
            self._start_ts = _t.time()
            self._tick_timer()
        else:
            self.btn.configure(state="normal", text=tr("btn_convert"))
            self.progress.stop()
            if self._timer_id:
                self.after_cancel(self._timer_id)
                self._timer_id = None

    def _tick_timer(self):
        import time as _t
        if self._start_ts is None:
            return
        e = _t.time() - self._start_ts
        m, s = divmod(int(e), 60)
        self._elapsed_var.set(f"⏱ {m:02d}:{s:02d}")
        self._timer_id = self.after(1000, self._tick_timer)

    def _log(self, msg: str):
        lo = msg.lower()
        if any(k in lo for k in ("error","błąd","✘","failed","exception","traceback")):
            tag = "err"
        elif any(k in lo for k in ("warning","warn")):
            tag = "warn"
        elif any(k in lo for k in ("✔","gotowe","sukces","completed successfully")):
            tag = "ok"
        elif any(k in lo for k in ("info","building","copying","checking")):
            tag = "info"
        else:
            tag = None
        self.after(0, self._log_insert, msg + "\n", tag)

    def _log_insert(self, msg: str, tag=None):
        self.log.configure(state="normal")
        start = self.log.index("end")
        self.log.insert("end", msg)
        if tag:
            self.log.tag_add(tag, start, "end-1c")
        lines = int(self.log.index("end-1c").split(".")[0])
        if lines > 200:
            self.log.delete("1.0", f"{lines-200}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _row_hta(self, p):
        self._opt_ref = p      # referencja potrzebna do pack(after=...) w _toggle_meta
        self.hta_var = tk.StringVar()
        self._lbl(p, tr("lbl_hta"), 0)
        self._entry(p, self.hta_var, 0)
        bf = tk.Frame(p, bg=PANEL_BG)
        bf.grid(row=0, column=2, padx=(5,0), sticky="ew")
        self._mk_btn(bf, tr("btn_file"),   self._pick_hta_file).pack(side="left")
        self._mk_btn(bf, tr("btn_folder_btn"), self._pick_hta_folder).pack(side="left", padx=(3,0))


# ─────────────────────────────────────────────
#  Start
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()