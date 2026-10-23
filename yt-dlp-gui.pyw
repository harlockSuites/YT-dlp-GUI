"""
yt-dlp GUI — Interface graphique pour yt-dlp
Répertoire de travail : C:\\Tools\\yt-dlp
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import threading
import shutil
import os
import json
import re
import sys
import time
import platform
import getpass
import signal
import webbrowser
from urllib.parse import quote

__version__ = "0.1.0"   # version Linux (étiquette Linux-v0.1.0) ; la version Windows 0.1.7 est figée sur la branche main
REPO_URL = "https://github.com/harlockSuites/YT-dlp-GUI"

# ══════════════════════════════════════════════════════════════════
#  Couche de plateforme : tout ce qui diffère entre Windows et Linux passe par ici.
#  Sous Windows, chaque fonction fait exactement ce que le code faisait avant (taskkill, NtSuspendProcess,
#  os.startfile, CREATE_NO_WINDOW) ; le reste du fichier n'a plus à connaître le système.
# ══════════════════════════════════════════════════════════════════
IS_WINDOWS = sys.platform == "win32"

# Arguments de subprocess : pas de fenêtre de console sous Windows ; rien à ajouter ailleurs.
NO_WINDOW = {"creationflags": subprocess.CREATE_NO_WINDOW} if IS_WINDOWS else {}
# Idem pour un processus que le logiciel devra arrêter avec ses enfants : hors Windows, il devient chef de son
# propre groupe de processus, ce qui permet de tuer le groupe entier sans toucher au logiciel.
PROCESS_GROUP = NO_WINDOW if IS_WINDOWS else {"start_new_session": True}


def kill_process_tree(proc, timeout=5):
    """Arrête de force le processus `proc` (subprocess.Popen) et tous ses descendants."""
    if IS_WINDOWS:
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], **NO_WINDOW, timeout=timeout)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass
        return
    try:
        pgid = os.getpgid(proc.pid)
        # Le groupe n'est visé que s'il a été créé pour ce processus (PROCESS_GROUP) : jamais le nôtre.
        if pgid == proc.pid and pgid != os.getpgrp():
            os.killpg(pgid, signal.SIGKILL)
            return
    except OSError:
        pass
    try:
        proc.kill()
    except Exception:
        pass


def _signal_processes(pids, resume):
    """Suspend (ou reprend si `resume`) chacun des processus de `pids`, dans l'ordre."""
    if IS_WINDOWS:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        ntdll = ctypes.windll.ntdll
        action = ntdll.NtResumeProcess if resume else ntdll.NtSuspendProcess
        for pid in pids:
            h = kernel32.OpenProcess(0x1F0FFF, False, pid)
            if h:
                action(h)
                kernel32.CloseHandle(h)
        return
    sig = signal.SIGCONT if resume else signal.SIGSTOP
    for pid in pids:
        try:
            os.kill(pid, sig)
        except OSError:
            pass


def suspend_process_tree(pid):
    """Met en pause le processus et ses enfants (ex. ffmpeg, aria2c) : les enfants d'abord, puis le parent."""
    try:
        _signal_processes(_child_pids(pid) + [pid], resume=False)
    except Exception:
        pass


def resume_process_tree(pid):
    """Reprend le processus et ses enfants : le parent en premier, puis les enfants."""
    try:
        _signal_processes([pid], resume=True)
        _signal_processes(_child_pids(pid), resume=True)
    except Exception:
        pass


def open_path(path):
    """Ouvre un fichier avec le programme associé du système. Lève OSError s'il n'y en a pas."""
    if IS_WINDOWS:
        os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)


# Polices de l'interface. Windows : Segoe UI et Consolas. Ailleurs ces polices n'existent pas et Tk en prendrait une
# autre au hasard : use_system_fonts() choisit la police système de Tk (interface et chasse fixe) quand la
# fenêtre existe, avant que le moindre contrôle ne soit créé.
UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"


def use_system_fonts():
    global UI_FONT, MONO_FONT
    if IS_WINDOWS:
        return
    import tkinter.font as tkfont
    UI_FONT = tkfont.nametofont("TkDefaultFont").actual("family")
    MONO_FONT = tkfont.nametofont("TkFixedFont").actual("family")


def _resolve_dirs(frozen, executable, script_dir, meipass, env, windows=None):
    """Retourne (RESOURCE_DIR, DATA_DIR).
    - RESOURCE_DIR : fichiers du programme en lecture seule (traductions, images, icône).
    - DATA_DIR : fichiers modifiables (config, file d'attente, yt-dlp, ffmpeg).
    Depuis les sources, tout reste à côté du script. Dans l'exécutable : à côté de l'exécutable si
    le fichier « portable.flag » s'y trouve (version portable), sinon dans %LOCALAPPDATA%\\yt-dlp-GUI
    (le dossier d'installation, ex. Program Files, n'est pas modifiable sans droits administrateur) ;
    sous Linux, dans $XDG_DATA_HOME/yt-dlp-GUI (par défaut ~/.local/share/yt-dlp-GUI).
    `windows` force le système (tests) ; par défaut, celui qui exécute le logiciel."""
    if windows is None:
        windows = IS_WINDOWS
    if not frozen:
        return script_dir, script_dir
    exe_dir = os.path.dirname(os.path.abspath(executable))
    resources = meipass or exe_dir
    if os.path.isfile(os.path.join(exe_dir, "portable.flag")):
        return resources, exe_dir
    if windows:
        base = env.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    else:
        xdg = env.get("XDG_DATA_HOME")
        base = xdg if xdg and os.path.isabs(xdg) else os.path.join(os.path.expanduser("~"), ".local", "share")
    return resources, os.path.join(base, "yt-dlp-GUI")


RESOURCE_DIR, DATA_DIR = _resolve_dirs(
    getattr(sys, "frozen", False), sys.executable, os.path.dirname(os.path.abspath(__file__)),
    getattr(sys, "_MEIPASS", None), os.environ)
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except OSError:
    pass

YTDLP              = os.path.join(DATA_DIR, "yt-dlp.exe" if IS_WINDOWS else "yt-dlp")
CONFIG_FILE        = os.path.join(DATA_DIR, "gui-config.json")
QUEUE_FILE         = os.path.join(DATA_DIR, "download-queue.json")
CUSTOM_BLOCKS_FILE = os.path.join(DATA_DIR, "custom-blocks.json")
LOCAL_BIN          = os.path.join(DATA_DIR, "bin")   # ffmpeg/ffprobe installés par l'assistant
COMMAND_DIR        = os.path.join(DATA_DIR, "cmd")   # fichiers de configuration éphémères de yt-dlp
ICON_FILE          = os.path.join(RESOURCE_DIR, "yt-dlp-gui.ico")
ICON_PNG           = os.path.join(RESOURCE_DIR, "assets", "yt-dlp-gui.png")   # icône des fenêtres hors Windows
ASSETS_DIR         = os.path.join(RESOURCE_DIR, "assets")
DONATE_URL         = "https://ko-fi.com/harlocksuites"
if LOCAL_BIN not in os.environ.get("PATH", "").split(os.pathsep):
    os.environ["PATH"] = LOCAL_BIN + os.pathsep + os.environ.get("PATH", "")


def _registry_path_dirs():
    """Dossiers du PATH utilisateur et système lus dans le registre : un processus déjà lancé
    ne voit pas les outils installés après son démarrage (Deno, ffmpeg…)."""
    try:
        import winreg
    except ImportError:
        return []
    dirs = []
    for root, sub in ((winreg.HKEY_CURRENT_USER, "Environment"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
        try:
            with winreg.OpenKey(root, sub) as key:
                value, _kind = winreg.QueryValueEx(key, "Path")
        except OSError:
            continue
        dirs += [os.path.expandvars(x.strip().strip('"')) for x in str(value).split(";") if x.strip()]
    return dirs


def _merge_path(current, extra):
    """Ajoute à `current` les dossiers existants de `extra` qui n'y figurent pas encore."""
    parts = [x for x in current.split(os.pathsep) if x]
    seen = {os.path.normcase(os.path.normpath(x)) for x in parts}
    for d in extra:
        key = os.path.normcase(os.path.normpath(d)) if d else ""
        if d and key not in seen and os.path.isdir(d):
            parts.append(d)
            seen.add(key)
    return os.pathsep.join(parts)


def _refresh_process_path():
    home = os.path.expanduser("~")
    extra = _registry_path_dirs() + [os.path.join(home, ".deno", "bin")]
    if IS_WINDOWS:
        extra += [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Links"),
            os.path.join(os.environ.get("ProgramData", ""), "chocolatey", "bin"),
        ]
    os.environ["PATH"] = _merge_path(os.environ.get("PATH", ""), extra)


_refresh_process_path()

SUBTITLE_FORMATS = ["vtt", "srt", "ass", "best"]

# Plusieurs pistes audio : fusion en MKV. --embed-metadata fait écrire par yt-dlp la langue de chaque
# piste (étiquette « language » du flux) ; sans lui, le lecteur n'affiche que « Piste 1 », « Piste 2 »…
MULTI_AUDIO_ARGS = ["--audio-multistreams", "--embed-metadata", "--merge-output-format", "mkv"]

# Sous-titres intégrés. Avec « --write-auto-subs », yt-dlp n'ajoute plus « --write-subs » de lui-même quand on
# demande « --embed-subs » : seuls les sous-titres automatiques sont alors cherchés et ceux rédigés par
# l'auteur sont ignorés (« There are no subtitles for the requested languages »). On demande donc les deux, et
# « no-keep-subs » supprime les fichiers .srt une fois intégrés, comme avec « --embed-subs » seul.
EMBED_SUBS_ARGS = ["--write-subs", "--embed-subs", "--compat-options", "no-keep-subs"]

# Bibliothèque de blocs yt-dlp sélectionnables dans les Règles globales
# (code, label_affiché, [args yt-dlp correspondants])
SCRIPT_BLOCKS = [
    # Post-traitement
    ("Post-traitement", "embed_chapters",     "Chapitres intégrés",               ["--embed-chapters"]),
    ("Post-traitement", "sponsorblock",       "Retirer segments SponsorBlock",    ["--sponsorblock-remove", "all"]),
    ("Post-traitement", "sponsorblock_mark",  "Marquer segments SponsorBlock",    ["--sponsorblock-mark", "all"]),
    ("Post-traitement", "add_metadata",       "Métadonnées ID3/MP4",              ["--add-metadata"]),
    ("Post-traitement", "xattrs",             "Attributs étendus (xattrs)",       ["--xattrs"]),
    ("Post-traitement", "keep_video",         "Garder la vidéo source",           ["--keep-video"]),
    ("Post-traitement", "trim_silence",       "Couper silence audio (ffmpeg)",    ["--postprocessor-args", "ffmpeg:-af silenceremove=1:0:-50dB"]),
    ("Post-traitement", "normalize_audio",    "Normaliser le volume (loudnorm)",  ["--postprocessor-args", "ffmpeg:-af loudnorm"]),
    # Export
    ("Export",          "write_desc",         "Fichier description (.txt)",       ["--write-description"]),
    ("Export",          "write_info",         "Fichier info JSON",                ["--write-info-json"]),
    ("Export",          "write_thumb",        "Miniature (fichier externe)",      ["--write-thumbnail"]),
    ("Export",          "write_comments",     "Commentaires JSON",                ["--write-comments"]),
    ("Export",          "compat_titles",      "Noms compatibles Windows",         ["--windows-filenames"]),
    ("Export",          "restrict_names",     "Noms ASCII (sans accents)",        ["--restrict-filenames"]),
    ("Export",          "no_overwrites",      "Ne pas écraser les fichiers",      ["--no-overwrites"]),
    ("Export",          "no_part",            "Pas de fichiers .part temporaires",["--no-part"]),
    # Audio
    ("Audio",           "audio_quality_0",    "Qualité maximale",                 ["--audio-quality", "0"]),
    ("Audio",           "audio_multistream",  "Multi-pistes audio (MKV)",         ["--audio-multistreams", "--embed-metadata"]),
    ("Audio",           "extract_audio_mp3",  "Extraire en MP3",                  ["--extract-audio", "--audio-format", "mp3"]),
    ("Audio",           "extract_audio_m4a",  "Extraire en M4A",                  ["--extract-audio", "--audio-format", "m4a"]),
    ("Audio",           "extract_audio_flac", "Extraire en FLAC",                 ["--extract-audio", "--audio-format", "flac"]),
    ("Audio",           "extract_audio_opus", "Extraire en Opus",                 ["--extract-audio", "--audio-format", "opus"]),
    # Réseau
    ("Réseau",          "rate_limit_2m",      "Limite débit : 2 Mo/s",            ["--rate-limit", "2M"]),
    ("Réseau",          "rate_limit_5m",      "Limite débit : 5 Mo/s",            ["--rate-limit", "5M"]),
    ("Réseau",          "rate_limit_10m",     "Limite débit : 10 Mo/s",           ["--rate-limit", "10M"]),
    ("Réseau",          "concurrent_2",       "2 fragments en parallèle",         ["--concurrent-fragments", "2"]),
    ("Réseau",          "concurrent_4",       "4 fragments en parallèle",         ["--concurrent-fragments", "4"]),
    ("Réseau",          "concurrent_8",       "8 fragments en parallèle",         ["--concurrent-fragments", "8"]),
    ("Réseau",          "sleep_2_5",          "Pause 2–5 s entre vidéos",         ["--sleep-interval", "2", "--max-sleep-interval", "5"]),
    ("Réseau",          "retries_20",         "20 tentatives sur erreur réseau",  ["--retries", "20", "--fragment-retries", "20"]),
    # Comportement
    ("Comportement",    "no_playlist",        "Ignorer les playlists",            ["--no-playlist"]),
    ("Comportement",    "yes_playlist",       "Forcer le mode playlist",          ["--yes-playlist"]),
    ("Comportement",    "ignore_errors",      "Ignorer les erreurs (-i)",         ["--ignore-errors"]),
    ("Comportement",    "abort_on_error",     "Arrêter sur la première erreur",   ["--abort-on-error"]),
    ("Comportement",    "continue_dl",        "Reprendre les téléchargements",    ["--continue"]),
    ("Comportement",    "verbose",            "Mode verbeux (debug)",             ["--verbose"]),
    ("Comportement",    "simulate",           "Simulation (sans téléchargement)", ["--simulate"]),
    # Langue — pistes audio secondaires (50 langues les plus parlées au monde)
    # Les codes préfixés "_alang_" sont traités spécialement dans _build_video_args :
    # ils s'ajoutent à la liste des pistes audio secondaires (format bestaudio[language=XX])
    ("Langue",  "alang_en",  "Anglais (en)",              ["_alang_", "en"]),
    ("Langue",  "alang_zh",  "Chinois mandarin (zh)",     ["_alang_", "zh"]),
    ("Langue",  "alang_hi",  "Hindi (hi)",                ["_alang_", "hi"]),
    ("Langue",  "alang_es",  "Espagnol (es)",             ["_alang_", "es"]),
    ("Langue",  "alang_fr",  "Français (fr)",             ["_alang_", "fr"]),
    ("Langue",  "alang_ar",  "Arabe (ar)",                ["_alang_", "ar"]),
    ("Langue",  "alang_bn",  "Bengali (bn)",              ["_alang_", "bn"]),
    ("Langue",  "alang_ru",  "Russe (ru)",                ["_alang_", "ru"]),
    ("Langue",  "alang_pt",  "Portugais (pt)",            ["_alang_", "pt"]),
    ("Langue",  "alang_ur",  "Ourdou (ur)",               ["_alang_", "ur"]),
    ("Langue",  "alang_id",  "Indonésien (id)",           ["_alang_", "id"]),
    ("Langue",  "alang_de",  "Allemand (de)",             ["_alang_", "de"]),
    ("Langue",  "alang_ja",  "Japonais (ja)",             ["_alang_", "ja"]),
    ("Langue",  "alang_sw",  "Swahili (sw)",              ["_alang_", "sw"]),
    ("Langue",  "alang_mr",  "Marathi (mr)",              ["_alang_", "mr"]),
    ("Langue",  "alang_te",  "Télougou (te)",             ["_alang_", "te"]),
    ("Langue",  "alang_tr",  "Turc (tr)",                 ["_alang_", "tr"]),
    ("Langue",  "alang_ta",  "Tamoul (ta)",               ["_alang_", "ta"]),
    ("Langue",  "alang_vi",  "Vietnamien (vi)",           ["_alang_", "vi"]),
    ("Langue",  "alang_ko",  "Coréen (ko)",               ["_alang_", "ko"]),
    ("Langue",  "alang_fa",  "Persan (fa)",               ["_alang_", "fa"]),
    ("Langue",  "alang_ha",  "Haoussa (ha)",              ["_alang_", "ha"]),
    ("Langue",  "alang_tl",  "Tagalog / Filipino (tl)",   ["_alang_", "tl"]),
    ("Langue",  "alang_it",  "Italien (it)",              ["_alang_", "it"]),
    ("Langue",  "alang_pa",  "Pendjabi (pa)",             ["_alang_", "pa"]),
    ("Langue",  "alang_gu",  "Gujarati (gu)",             ["_alang_", "gu"]),
    ("Langue",  "alang_th",  "Thaï (th)",                 ["_alang_", "th"]),
    ("Langue",  "alang_kn",  "Kannada (kn)",              ["_alang_", "kn"]),
    ("Langue",  "alang_am",  "Amharique (am)",            ["_alang_", "am"]),
    ("Langue",  "alang_yo",  "Yoruba (yo)",               ["_alang_", "yo"]),
    ("Langue",  "alang_ms",  "Malais (ms)",               ["_alang_", "ms"]),
    ("Langue",  "alang_my",  "Birman (my)",               ["_alang_", "my"]),
    ("Langue",  "alang_pl",  "Polonais (pl)",             ["_alang_", "pl"]),
    ("Langue",  "alang_uk",  "Ukrainien (uk)",            ["_alang_", "uk"]),
    ("Langue",  "alang_ml",  "Malayalam (ml)",            ["_alang_", "ml"]),
    ("Langue",  "alang_nl",  "Néerlandais (nl)",          ["_alang_", "nl"]),
    ("Langue",  "alang_ro",  "Roumain (ro)",              ["_alang_", "ro"]),
    ("Langue",  "alang_or",  "Odia (or)",                 ["_alang_", "or"]),
    ("Langue",  "alang_ig",  "Igbo (ig)",                 ["_alang_", "ig"]),
    ("Langue",  "alang_uz",  "Ouzbek (uz)",               ["_alang_", "uz"]),
    ("Langue",  "alang_ne",  "Népalais (ne)",             ["_alang_", "ne"]),
    ("Langue",  "alang_sd",  "Sindhi (sd)",               ["_alang_", "sd"]),
    ("Langue",  "alang_jv",  "Javanais (jv)",             ["_alang_", "jv"]),
    ("Langue",  "alang_az",  "Azerbaïdjanais (az)",       ["_alang_", "az"]),
    ("Langue",  "alang_si",  "Cingalais (si)",            ["_alang_", "si"]),
    ("Langue",  "alang_km",  "Khmer (km)",                ["_alang_", "km"]),
    ("Langue",  "alang_cs",  "Tchèque (cs)",              ["_alang_", "cs"]),
    ("Langue",  "alang_hu",  "Hongrois (hu)",             ["_alang_", "hu"]),
    ("Langue",  "alang_el",  "Grec (el)",                 ["_alang_", "el"]),
    ("Langue",  "alang_sv",  "Suédois (sv)",              ["_alang_", "sv"]),
]

# Index rapide code → args
SCRIPT_BLOCKS_MAP = {code: args for _, code, _, args in SCRIPT_BLOCKS}
# Options groupées par catégorie : {"Post-traitement": [(code, lbl), ...], ...}
SCRIPT_BLOCKS_BY_TAB = {}
for _cat, _code, _lbl, _ in SCRIPT_BLOCKS:
    SCRIPT_BLOCKS_BY_TAB.setdefault(_cat, []).append((_code, _lbl))

# Codes des blocs built-in (non supprimables)
_BUILTIN_BLOCK_CODES = {code for _, code, _, _ in SCRIPT_BLOCKS}

# Blocs personnalisés — chargés depuis custom-blocks.json au démarrage
CUSTOM_BLOCKS = []   # list of (cat, code, label, args_list)

# ── Internationalisation ──────────────────────────────────────────────────────
import pathlib as _pathlib

_LANG_DIR = _pathlib.Path(RESOURCE_DIR) / "lang"
_STRINGS: dict = {}
_STRINGS_EN: dict = {}
_CURRENT_LANG: str = "fr"

def load_lang(code: str = "fr") -> None:
    global _STRINGS, _STRINGS_EN, _CURRENT_LANG
    _CURRENT_LANG = code
    en_path = _LANG_DIR / "en.json"
    if en_path.exists():
        import json as _json
        with open(en_path, encoding="utf-8") as _f:
            _STRINGS_EN = _json.load(_f)
    lang_path = _LANG_DIR / f"{code}.json"
    if lang_path.exists():
        import json as _json
        with open(lang_path, encoding="utf-8") as _f:
            _STRINGS = _json.load(_f)
    else:
        _STRINGS = dict(_STRINGS_EN)

def t(key: str, **kwargs) -> str:
    val = _STRINGS.get(key) or _STRINGS_EN.get(key) or key
    if kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, ValueError):
            return val
    return val
# ─────────────────────────────────────────────────────────────────────────────

_LANG_NAMES = {
    "en": "Anglais", "zh": "Chinois", "hi": "Hindi", "es": "Espagnol",
    "fr": "Français", "ar": "Arabe", "bn": "Bengali", "pt": "Portugais",
    "ru": "Russe", "ur": "Ourdou", "id": "Indonésien", "de": "Allemand",
    "ja": "Japonais", "sw": "Swahili", "mr": "Marathi", "te": "Télougou",
    "tr": "Turc", "ta": "Tamoul", "vi": "Vietnamien", "ko": "Coréen",
    "it": "Italien", "fa": "Persan", "pl": "Polonais", "uk": "Ukrainien",
    "nl": "Néerlandais", "th": "Thaï", "ro": "Roumain", "el": "Grec",
    "hu": "Hongrois", "cs": "Tchèque", "sv": "Suédois", "no": "Norvégien",
    "fi": "Finnois", "da": "Danois", "he": "Hébreu", "sk": "Slovaque",
    "hr": "Croate", "bg": "Bulgare", "sr": "Serbe", "ca": "Catalan",
    "lt": "Lituanien", "lv": "Letton", "sl": "Slovène", "et": "Estonien",
    "ms": "Malais", "tl": "Filipino", "af": "Afrikaans", "sq": "Albanais",
    "be": "Biélorusse", "mk": "Macédonien",
}

_BLKCAT_KEYS = {
    "Post-traitement": "blk.cat.post",
    "Export": "blk.cat.export",
    "Audio": "blk.cat.audio",
    "Réseau": "blk.cat.reseau",
    "Comportement": "blk.cat.comportement",
    "Langue": "blk.cat.langue",
}


def _t_lang_name(code: str) -> str:
    """Return translated language name for a BCP-47 code, falling back to _LANG_NAMES."""
    val = _STRINGS.get(f"sub.{code}") or _STRINGS_EN.get(f"sub.{code}")
    return val if val else _LANG_NAMES.get(code, code)


def _tblkcat(fr_cat: str) -> str:
    """Translate a builtin block category name."""
    key = _BLKCAT_KEYS.get(fr_cat)
    return t(key) if key else fr_cat


def _can_scroll_y(canvas, delta):
    """Le canevas peut-il défiler dans le sens de la molette (delta > 0 : vers le haut) ?"""
    try:
        lo, hi = canvas.yview()
    except tk.TclError:
        return False
    return lo > 0.0 if delta > 0 else hi < 1.0


def modified_since(path, since):
    """Le fichier a-t-il été écrit depuis `since` (horloge time.time(), 2 s de tolérance) ?

    Garde-fou du nettoyage : les recherches « par suffixe » ou par motif (*.part, .fr.srt…) ne touchent que les
    fichiers que le téléchargement interrompu vient de produire, jamais ceux des autres vidéos du dossier.
    Sans heure de départ connue, rien n'est considéré comme récent."""
    if since is None:
        return False
    try:
        return os.path.getmtime(path) >= since - 2
    except OSError:
        return False


def wheel_target(widget, delta):
    """Zone défilante à faire bouger pour une molette tournée au-dessus de `widget`, ou None.

    On remonte les parents : un tableau, une zone de texte ou une liste défilent déjà seuls (liaison de
    classe de Tk, on ne s'en mêle pas) ; sinon le premier canevas à barre de défilement qui peut encore
    bouger dans ce sens est retenu, y compris quand le pointeur est sur une étiquette, un cadre ou un bouton."""
    w = widget
    while w is not None:
        if isinstance(w, (tk.Text, tk.Listbox, ttk.Treeview)):
            return None
        if isinstance(w, tk.Canvas):
            scrollable = bool(str(w.cget("yscrollcommand"))) or bool(str(w.cget("scrollregion")).strip())
            if scrollable and _can_scroll_y(w, delta):
                return w
        w = getattr(w, "master", None)
    return None


def install_wheel_scrolling(root):
    """Molette de la souris : fait défiler la zone défilante sous le pointeur, où qu'il soit dans la fenêtre
    (étiquettes, cadres, boutons…), au lieu de ne fonctionner que sur quelques contrôles. Une liste déroulante
    survolée fait défiler la page au lieu de changer sa valeur."""
    def scroll(event, delta):
        try:
            pointer = root.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return None
        canvas = wheel_target(pointer, delta)
        if canvas is None:
            return None
        step = max(1, abs(delta) // 120)
        canvas.yview_scroll(-step if delta > 0 else step, "units")
        return "break"

    root.bind_all("<MouseWheel>", lambda e: scroll(e, e.delta), add="+")
    root.bind_all("<Button-4>", lambda e: scroll(e, 120), add="+")      # X11 : la molette est le bouton 4 / 5
    root.bind_all("<Button-5>", lambda e: scroll(e, -120), add="+")
    root.bind_class("TCombobox", "<MouseWheel>", lambda e: scroll(e, e.delta) or "break")
    # X11 : sans ces deux liaisons, Tk change la valeur de la liste au passage de la molette
    root.bind_class("TCombobox", "<Button-4>", lambda e: scroll(e, 120) or "break")
    root.bind_class("TCombobox", "<Button-5>", lambda e: scroll(e, -120) or "break")


_UNAVAILABLE_TITLES = ("[Private video]", "[Deleted video]")


def is_playlist_url(url):
    """Adresse de playlist seule, pas une vidéo qui appartient à une playlist (« watch?v=…&list=… »).

    Deux écritures existent : « …/playlist?list=ID » (adresse officielle) et « …/show/VLID » (adresse brute d'une
    série, où l'identifiant de la playlist est précédé de « VL » et ne figure pas dans la requête)."""
    from urllib.parse import urlparse, parse_qs
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
    except ValueError:
        return False
    if "list" in query and "v" not in query:
        return True
    return parsed.path.startswith("/show/")


def playlist_summary(info):
    """{titre, nombre de vidéos, nombre d'indisponibles} d'après `yt-dlp -J --flat-playlist`, ou None.

    Les vidéos privées, supprimées ou masquées reviennent sans titre (ou « [Private video] »)."""
    if not isinstance(info, dict) or not isinstance(info.get("entries"), list):
        return None
    entries = [e for e in info["entries"] if isinstance(e, dict)]
    bad = sum(1 for e in entries if not e.get("title") or e.get("title") in _UNAVAILABLE_TITLES)
    count = len(entries) or int(info.get("playlist_count") or 0)
    title = info.get("title") or ""
    if title == "show" and info.get("id") == "show":          # adresse « /show/… » : yt-dlp n'y trouve pas de titre
        title = ""
    return {"title": title, "count": count, "bad": bad}


_RE_PLAYLIST_ITEM = re.compile(r"\[download\] Downloading item \d+ of (\d+)")


def playlist_outcome(lines):
    """(téléchargées, en erreur) quand une playlist est allée au bout avec quelques échecs, sinon None.

    yt-dlp renvoie un code d'erreur dès qu'une vidéo de la playlist est indisponible (supprimée, privée…)
    alors que les autres sont téléchargées. Sans la ligne finale « Finished downloading playlist », rien
    n'est conclu : un arrêt demandé en cours de route ne doit pas passer pour un succès partiel."""
    total, errors, finished = 0, set(), False
    for line in lines:
        item = _RE_PLAYLIST_ITEM.search(line)
        if item:
            total = int(item.group(1))
        elif line.startswith("ERROR:"):
            errors.add(line)
        elif line.startswith("[download] Finished downloading playlist"):
            finished = True
    if not finished or total < 2 or not errors:
        return None
    failed = min(len(errors), total)
    return (total - failed, failed) if total - failed > 0 else None


def format_table_languages(text):
    """Langues audio lues dans la table des formats de `yt-dlp -F` (colonne « MORE INFO », « [en] »).

    Seules les lignes du tableau comptent : une ligne d'information comme « [info] Available formats for … »
    ressemblait à un code de langue et faisait afficher « Pistes audio : info »."""
    found = set()
    for line in text.splitlines():
        if line.lstrip().startswith("[") or line.count("|") < 2:
            continue
        for code in re.findall(r"\[([a-z]{2,4})\]", line.rsplit("|", 1)[-1]):
            if code != "und":
                found.add(code)
    return found


def extract_url(text):
    """Adresse à utiliser quand le champ URL contient du texte collé autour (« Inspection : https://… » suivi
    d'un journal, par exemple) : la première adresse http(s) du texte ; sinon le texte nettoyé."""
    text = (text or "").strip()
    if not text or not re.search(r"\s", text):
        return text
    found = re.search(r"https?://[^\s\"'<>]+", text)
    return found.group(0).rstrip(".,;:!?)]}»") if found else text


def _screen_fit_geometry(screen_w, screen_h, w, h, x, y, margin=10, bottom=60):
    """Taille et position (w, h, x, y) d'une fenêtre ouverte près d'un contrôle, ramenées dans l'écran.

    La position demandée est gardée tant que la fenêtre tient ; sinon elle est décalée vers le haut
    ou la gauche. Si elle est plus grande que l'écran, sa hauteur est limitée (la liste défile et les
    boutons restent visibles). `bottom` réserve la place de la barre des tâches."""
    w = max(1, min(w, screen_w - 2 * margin))
    h = max(1, min(h, screen_h - bottom - margin))
    x = max(margin, min(x, screen_w - w - margin))
    y = max(margin, min(y, screen_h - bottom - h))
    return w, h, x, y


def _tblklbl(code: str, fr_label: str) -> str:
    """Translate a builtin block label; for alang_* entries uses sub.* keys."""
    val = _STRINGS.get(f"blk.{code}") or _STRINGS_EN.get(f"blk.{code}")
    if val:
        return val
    if code.startswith("alang_"):
        lang_code = code[6:]
        lang_name = _t_lang_name(lang_code)
        return f"{lang_name} ({lang_code})"
    return fr_label


def _lang_label(code):
    name = _t_lang_name(code)
    return f"{code.upper()} — {name}"


def _translated_blocks_tabs(filter_fn=None) -> dict:
    """Return SCRIPT_BLOCKS_BY_TAB with translated category names and block labels.
    filter_fn(fr_cat) → bool is applied on the original French category key."""
    result = {}
    for fr_cat, entries in SCRIPT_BLOCKS_BY_TAB.items():
        if filter_fn is not None and not filter_fn(fr_cat):
            continue
        tr_cat = _tblkcat(fr_cat)
        result[tr_cat] = [(_code, _tblklbl(_code, _lbl)) for _code, _lbl in entries]
    return result


def _load_custom_blocks():
    """Charge les blocs custom et les fusionne dans les structures globales."""
    global CUSTOM_BLOCKS
    if not os.path.exists(CUSTOM_BLOCKS_FILE):
        return
    try:
        with open(CUSTOM_BLOCKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        CUSTOM_BLOCKS = []
        for item in data:
            cat, code, lbl, args = item["cat"], item["code"], item["label"], item["args"]
            CUSTOM_BLOCKS.append((cat, code, lbl, args))
            SCRIPT_BLOCKS_MAP[code] = args
            SCRIPT_BLOCKS_BY_TAB.setdefault(cat, []).append((code, lbl))
    except Exception:
        pass


_JSON_WRITE_LOCK = threading.Lock()


def _write_json_atomic(path, data):
    """Écrit `data` en JSON via un fichier temporaire puis os.replace : une coupure
    en pleine écriture ne laisse jamais un fichier tronqué."""
    tmp = path + ".tmp"
    with _JSON_WRITE_LOCK:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)


def _save_custom_blocks():
    """Sauvegarde CUSTOM_BLOCKS dans custom-blocks.json."""
    data = [{"cat": c, "code": co, "label": l, "args": a}
            for c, co, l, a in CUSTOM_BLOCKS]
    try:
        _write_json_atomic(CUSTOM_BLOCKS_FILE, data)
    except Exception:
        pass


def _add_custom_block(cat, code, label, args):
    """Ajoute un bloc custom aux structures globales et sauvegarde."""
    CUSTOM_BLOCKS.append((cat, code, label, args))
    SCRIPT_BLOCKS_MAP[code] = args
    SCRIPT_BLOCKS_BY_TAB.setdefault(cat, []).append((code, label))
    _save_custom_blocks()


def _delete_custom_block(code):
    """Supprime un bloc custom des structures globales et sauvegarde."""
    global CUSTOM_BLOCKS
    cat_of = None
    for c, co, l, a in CUSTOM_BLOCKS:
        if co == code:
            cat_of = c
            break
    CUSTOM_BLOCKS = [(c, co, l, a) for c, co, l, a in CUSTOM_BLOCKS if co != code]
    SCRIPT_BLOCKS_MAP.pop(code, None)
    if cat_of and cat_of in SCRIPT_BLOCKS_BY_TAB:
        SCRIPT_BLOCKS_BY_TAB[cat_of] = [
            (co, l) for co, l in SCRIPT_BLOCKS_BY_TAB[cat_of] if co != code]
        if not SCRIPT_BLOCKS_BY_TAB[cat_of]:
            del SCRIPT_BLOCKS_BY_TAB[cat_of]
    _save_custom_blocks()


def _edit_custom_block(old_code, new_cat, new_code, new_label, new_args):
    """Modifie un bloc custom existant."""
    _delete_custom_block(old_code)
    _add_custom_block(new_cat, new_code, new_label, new_args)


# Dépendances yt-dlp avec leur paquet Chocolatey
DEPS = [
    {
        "name": "ffmpeg",
        "exe": "ffmpeg",
        "choco": "ffmpeg",
        "url": "https://ffmpeg.org/download.html",
        "desc": "Fusion vidéo+audio, conversion de formats, sous-titres",
        "required": True,
    },
    {
        "name": "ffprobe",
        "exe": "ffprobe",
        "choco": "ffmpeg",   # ffprobe est inclus dans le paquet ffmpeg
        "url": "https://ffmpeg.org/download.html",
        "desc": "Analyse des flux média (inclus avec ffmpeg)",
        "required": True,
    },
    {
        "name": "AtomicParsley",
        "exe": "AtomicParsley",
        "choco": "atomicparsley",
        "url": "https://github.com/wez/atomicparsley/releases",
        "desc": "Intégration des miniatures dans les fichiers MP4/M4A",
        "required": False,
    },
    {
        "name": "MKVToolNix",
        "exe": "mkvpropedit",
        "choco": "mkvtoolnix",
        "url": "https://mkvtoolnix.download/downloads.html#windows",
        "desc": "Intégration optimale des miniatures dans les MKV (utilisé par yt-dlp en priorité sur ffmpeg)",
        "required": False,
        "known_paths": [
            r"C:\Program Files\MKVToolNix\mkvpropedit.exe",
            r"C:\Program Files (x86)\MKVToolNix\mkvpropedit.exe",
        ],
    },
    {
        "name": "aria2",
        "exe": "aria2c",
        "choco": "aria2",
        "url": "https://github.com/aria2/aria2/releases",
        "desc": "Téléchargement multi-connexions (vitesse accrue)",
        "required": False,
    },
    {
        "name": "deno",
        "exe": "deno",
        "choco": "deno",
        "url": "https://deno.com",
        "desc": "Runtime JS — requis pour voir les pistes audio secondaires (FR, ES…) et certains formats récents",
        "required": False,
        "level": "recommended",
        "direct": True,   # installable par l'assistant (téléchargement vérifié), sans Chocolatey
        "known_paths": [
            r"%USERPROFILE%\.deno\bin\deno.exe",
            r"%LOCALAPPDATA%\Microsoft\WinGet\Links\deno.exe",
            r"%USERPROFILE%\scoop\shims\deno.exe",
            r"%ProgramData%\scoop\shims\deno.exe",
            r"%ProgramFiles%\deno\deno.exe",
        ],
    },
]


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(data):
    try:
        _write_json_atomic(CONFIG_FILE, data)
    except Exception:
        pass


def update_config(key, value, attempts=3, delay=0.2):
    """Modifie un seul réglage sans jamais écraser les autres : si le fichier existe mais reste illisible
    (verrouillé un instant par un antivirus, par exemple), rien n'est écrit. Renvoie True si le réglage est
    enregistré (ou l'était déjà)."""
    for i in range(attempts):
        if not os.path.exists(CONFIG_FILE):
            cfg = {}
            break
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if isinstance(cfg, dict):
                break
        except Exception:
            pass
        cfg = None
        if i < attempts - 1:
            time.sleep(delay)
    if cfg is None:
        return False
    if cfg.get(key) == value:
        return True
    cfg[key] = value
    save_config(cfg)
    return True


def load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for e in data:
                if e.get("status") not in ("pending", "error"):
                    e["status"] = "pending"
            return data
        except Exception:
            pass
    return []


def save_queue(queue):
    try:
        _write_json_atomic(QUEUE_FILE, queue)
    except Exception:
        pass


def command_file_args(args):
    """Ligne de commande courte pour yt-dlp : (args_à_lancer, fichier_temporaire ou None).

    Les options sont écrites dans un fichier de configuration (--config-locations) ; seule la fin de la
    commande (« -- URL ») reste sur la ligne de commande. Un antivirus de comportement peut bloquer un
    processus à cause de ses *arguments* (RAV : « Suspicious.Argument ») quand le sélecteur de format est
    long, avec plusieurs pistes audio ; une ligne courte et stable lui laisse moins de prise."""
    if len(args) < 4 or "--" not in args:
        return args, None
    import shlex
    import tempfile
    cut = len(args) - 1 - args[::-1].index("--")          # dernier « -- » : début de la zone des URL
    options, tail = args[1:cut], args[cut:]
    try:
        os.makedirs(COMMAND_DIR, exist_ok=True)
        fd, path = tempfile.mkstemp(prefix=f"cmd-{os.getpid()}-", suffix=".conf", dir=COMMAND_DIR)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write("# coding: utf-8\n")
            for a in options:
                f.write(shlex.quote(a) + "\n")            # guillemets simples : les « \ » de Windows restent tels quels
    except OSError:
        return args, None                                     # repli : ligne de commande complète
    return [args[0], "--config-locations", path] + tail, path


def remove_command_file(path):
    if path:
        try:
            os.remove(path)
        except OSError:
            pass


def command_file_owner(name):
    """PID du logiciel qui a créé le fichier de commande (« cmd-1234-xxxx.conf »), None pour l'ancien format."""
    found = re.match(r"cmd-(\d+)-", name)
    return int(found.group(1)) if found else None


def cleanup_command_files(max_age=24 * 3600, grace=60):
    """Supprime les fichiers de commande orphelins, sans toucher à ceux d'une autre fenêtre du logiciel.

    Un fichier appartient à un processus (PID dans son nom) : s'il ne tourne plus, le fichier est orphelin et
    part tout de suite, même tout frais (arrêt brutal puis relancement immédiat). Sans PID connu, ou si la
    liste des processus est illisible, on se rabat sur l'âge (`grace` secondes ; `max_age` dans tous les cas)."""
    try:
        alive = {pid for pid, _parent, _name in _iter_processes()}
    except Exception:
        alive = None
    try:
        names = os.listdir(COMMAND_DIR)
    except OSError:
        return
    for name in names:
        full = os.path.join(COMMAND_DIR, name)
        if not name.endswith(".conf"):
            continue
        try:
            age = time.time() - os.path.getmtime(full)
        except OSError:
            continue
        owner = command_file_owner(name)
        if owner is not None and alive:
            orphan = owner not in alive
        else:
            orphan = age > grace
        if orphan or age > max_age:
            remove_command_file(full)


def is_antivirus_block(exc):
    """Windows refuse d'ouvrir un fichier que l'antivirus a bloqué (WinError 225 ou 226)."""
    return isinstance(exc, OSError) and getattr(exc, "winerror", None) in (225, 226)


def av_advice(exc):
    """Explication à afficher quand `exc` vient d'un blocage par l'antivirus (sinon chaîne vide)."""
    return t("av.hint", folder=DATA_DIR) if is_antivirus_block(exc) else ""


def _replace_with_retry(src, dst, attempts=8, delay=0.5):
    """os.replace qui réessaie quand un antivirus analyse encore le fichier (WinError 32 ou 5)."""
    for i in range(attempts):
        try:
            os.replace(src, dst)
            return
        except OSError as exc:
            if getattr(exc, "winerror", None) not in (5, 32) or i == attempts - 1:
                raise
            time.sleep(delay * (i + 1))


def choco_available():
    return shutil.which("choco") is not None


# Linux : les outils facultatifs viennent du gestionnaire de paquets de la distribution (le logiciel affiche la
# commande, sans jamais la lancer lui-même). Nom du paquet de chaque outil, par gestionnaire.
LINUX_PACKAGES = {
    "AtomicParsley": {"apt": "atomicparsley", "dnf": "AtomicParsley", "pacman": "atomicparsley",
                      "zypper": "AtomicParsley"},
    "MKVToolNix": {"apt": "mkvtoolnix", "dnf": "mkvtoolnix", "pacman": "mkvtoolnix-cli", "zypper": "mkvtoolnix"},
    "aria2": {"apt": "aria2", "dnf": "aria2", "pacman": "aria2", "zypper": "aria2"},
}
_LINUX_INSTALL_COMMANDS = {"apt": "sudo apt install", "dnf": "sudo dnf install", "pacman": "sudo pacman -S",
                           "zypper": "sudo zypper install"}


def linux_package_manager():
    """Gestionnaire de paquets de la distribution (apt, dnf, pacman, zypper), ou None s'il n'est pas reconnu."""
    return next((name for name in _LINUX_INSTALL_COMMANDS if shutil.which(name)), None)


def linux_install_command(tool_names, manager=None):
    """Commande à copier dans un terminal pour installer ces outils facultatifs, ou None si le gestionnaire de
    paquets est inconnu ou si aucun outil ne s'installe ainsi."""
    manager = manager or linux_package_manager()
    packages = sorted({LINUX_PACKAGES[n][manager] for n in tool_names if n in LINUX_PACKAGES and manager in
                       LINUX_PACKAGES[n]})
    if not manager or not packages:
        return None
    return f"{_LINUX_INSTALL_COMMANDS[manager]} {' '.join(packages)}"


def dep_direct(dep):
    """L'assistant sait-il installer cet outil lui-même (téléchargement vérifié, sans droits administrateur) ?
    Deno partout ; ffmpeg et ffprobe sous Linux (sous Windows ils passent par Chocolatey)."""
    if dep.get("direct"):
        return True
    return not IS_WINDOWS and dep["name"] in ("ffmpeg", "ffprobe") and bool(FFMPEG_URL)


def dep_installed(exe):
    if shutil.which(exe) is not None:
        return True
    _refresh_process_path()   # outil installé depuis le lancement du logiciel
    if shutil.which(exe) is not None:
        return True
    # Fallback : vérifier les chemins connus et injecter dans PATH si trouvé
    dep = next((d for d in DEPS if d["exe"] == exe), None)
    if dep:
        for path in _known_exe_paths(dep):
            if os.path.isfile(path):
                folder = os.path.dirname(path)
                if folder not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
                return True
    return False


def _known_exe_paths(dep):
    """Emplacements où l'outil peut se trouver sans figurer dans le PATH de cet utilisateur : chemins
    déclarés, puis dossier du paquet Chocolatey (installé par un autre compte administrateur, dont
    le PATH utilisateur n'est pas celui de la session courante)."""
    paths = [os.path.expandvars(p) for p in dep.get("known_paths", [])]
    pkg = dep.get("choco")
    if pkg and IS_WINDOWS:
        root = os.environ.get("ChocolateyInstall") or os.path.join(os.environ.get("ProgramData", ""), "chocolatey")
        base = os.path.join(root, "lib", pkg)
        paths += [os.path.join(d, dep["exe"] + ".exe") for d in (base, os.path.join(base, "tools"))]
    return paths


def _iter_processes():
    """(pid, pid_parent, nom_du_programme_en_minuscules) de tous les processus."""
    return _iter_processes_windows() if IS_WINDOWS else _iter_processes_posix()


def _iter_processes_posix():
    """Lit /proc/<pid>/stat (« pid (nom) état pid_parent … » ; le nom peut contenir espaces et parenthèses)."""
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat", "rb") as f:
                data = f.read().decode("utf-8", "replace")
        except OSError:
            continue   # le processus s'est terminé entre-temps
        start, end = data.find("("), data.rfind(")")
        if start < 0 or end < start:
            continue
        fields = data[end + 2:].split()
        try:
            yield int(entry), int(fields[1]), data[start + 1:end].lower()
        except (IndexError, ValueError):
            continue


def _iter_processes_windows():
    """Toolhelp32 (wmic a disparu des Windows récents)."""
    import ctypes
    from ctypes import wintypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

    k32 = ctypes.windll.kernel32
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)   # TH32CS_SNAPPROCESS
    if not snap or snap == ctypes.c_void_p(-1).value:
        return
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = k32.Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            yield entry.th32ProcessID, entry.th32ParentProcessID, entry.szExeFile.lower()
            ok = k32.Process32NextW(snap, ctypes.byref(entry))
    finally:
        k32.CloseHandle(snap)


def _child_pids(pid):
    """PID des processus enfants directs."""
    return [p for p, parent, _name in _iter_processes() if parent == pid]


# Programmes de chaque navigateur (noms de menu de cookies de yt-dlp)
if IS_WINDOWS:
    _BROWSER_EXES = {"chrome": ("chrome.exe",), "edge": ("msedge.exe",), "brave": ("brave.exe",),
                     "opera": ("opera.exe",), "firefox": ("firefox.exe",)}
else:
    _BROWSER_EXES = {"chrome": ("chrome", "google-chrome"), "edge": ("msedge", "microsoft-edge"),
                     "brave": ("brave", "brave-browser"), "opera": ("opera",),
                     "firefox": ("firefox", "firefox-esr", "firefox-bin"),
                     "chromium": ("chromium", "chromium-browse"),   # le nom d'un processus est coupé à 15 lettres
                     "vivaldi": ("vivaldi", "vivaldi-bin")}


def browser_process_count(browser):
    """Nombre de processus du navigateur encore en cours d'exécution, y compris en arrière-plan
    (Edge et Chrome restent actifs après la fermeture de leur fenêtre) ; 0 si inconnu."""
    names = _BROWSER_EXES.get((browser or "").lower())
    if not names:
        return 0
    try:
        return sum(1 for _pid, _parent, exe in _iter_processes() if exe in names)
    except Exception:
        return 0


def run_elevated(cmd_str):
    """Lance une commande dans une fenêtre visible avec élévation UAC (ShellExecute « runas »).

    Pas de PowerShell masqué ni de contournement de la politique d'exécution des scripts : ce montage
    est celui des logiciels malveillants et les antivirus de comportement le bloquent. Renvoie False si Windows n'a pas
    lancé la commande (élévation refusée ou annulée)."""
    try:
        import ctypes
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {cmd_str}", None, 1)
    except Exception:
        return False
    return result > 32


# ══════════════════════════════════════════════════════════════════
#  Fenêtre Dépendances
# ══════════════════════════════════════════════════════════════════
class DepsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("deps.window_title"))
        self.resizable(False, False)
        self.grab_set()
        self._rows = []
        self._build()
        self._refresh()

    def _build(self):
        pad = dict(padx=12, pady=6)

        ttk.Label(
            self,
            text=t("deps.header"),
            font=(UI_FONT, 10, "bold"),
        ).pack(anchor="w", **pad)
        ttk.Label(self, text=t("deps.optional_note"), wraplength=560, justify="left",
                  foreground="#2e7d32").pack(anchor="w", padx=12, pady=(0, 6))

        # Information si Chocolatey est absent (facultatif : il ne sert qu'aux installations automatiques)
        if not IS_WINDOWS:
            ttk.Label(self, text=t("deps.linux_note"), wraplength=560, justify="left",
                      foreground="#555555").pack(anchor="w", padx=12, pady=(0, 6))
        elif not choco_available():
            frm_warn = ttk.Frame(self, relief="solid", borderwidth=1)
            frm_warn.pack(fill="x", padx=12, pady=(0, 6))
            ttk.Label(
                frm_warn,
                text=t("deps.choco_warn"),
                foreground="#555555",
                justify="left",
                padding=8,
            ).pack(anchor="w")
            ttk.Label(
                frm_warn,
                text=t("deps.install_all_disabled"),
                wraplength=560,
                justify="left",
                padding=(8, 0, 8, 8),
            ).pack(anchor="w")

        # Tableau des dépendances
        frm_table = ttk.Frame(self)
        frm_table.pack(fill="x", padx=12)

        has_choco = IS_WINDOWS and choco_available()
        headers =[t("deps.col_tool"), t("deps.col_status"), t("deps.col_role"), t("deps.col_action")]
        widths   = [14,       16,       54,      14]
        for col, (h, w) in enumerate(zip(headers, widths)):
            ttk.Label(frm_table, text=h, font=(UI_FONT, 9, "bold"),
                      width=w, anchor="w").grid(row=0, column=col, padx=4, pady=(0, 4))

        self._rows = []
        for i, dep in enumerate(DEPS):
            row = i + 1
            req_tag = " *" if dep["required"] else ""
            lbl_name = ttk.Label(frm_table, text=dep["name"] + req_tag,
                                 font=(MONO_FONT, 9), width=14, anchor="w")
            lbl_name.grid(row=row, column=0, padx=4, pady=2, sticky="w")

            lbl_status = ttk.Label(frm_table, text="…", width=16, anchor="w")
            lbl_status.grid(row=row, column=1, padx=4, pady=2, sticky="w")

            lbl_desc = ttk.Label(frm_table, text=dep["desc"], width=54,
                                 anchor="w", wraplength=320, justify="left")
            lbl_desc.grid(row=row, column=2, padx=4, pady=2, sticky="w")

            url = dep.get("url", "")
            if dep_direct(dep):
                btn = ttk.Button(frm_table, text=t("deps.btn_install"), command=self._install_direct)
            elif has_choco:
                btn = ttk.Button(frm_table, text=t("deps.btn_install"),
                                 command=lambda d=dep: self._install(d))
            else:
                btn = ttk.Button(frm_table, text=t("deps.btn_open_site"),
                                 command=lambda u=url: self._open_url(u),
                                 state="normal" if url else "disabled")
            btn.grid(row=row, column=3, padx=4, pady=2)

            self._rows.append({"dep": dep, "lbl_status": lbl_status, "btn": btn})

        ttk.Label(self, text=t("deps.footnote" if IS_WINDOWS else "deps.footnote_linux"), font=(UI_FONT, 8),
                  foreground="#666", wraplength=560, justify="left").pack(anchor="w", padx=12)

        # Boutons du bas
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x", padx=12, pady=10)
        self._frm_btn = frm_btn

        if IS_WINDOWS:
            ttk.Button(frm_btn, text=t("deps.btn_install_all"), command=self._install_all,
                       state="normal" if choco_available() else "disabled").pack(side="left", ipadx=6)
        else:
            self._build_command_frame()
        ttk.Button(frm_btn, text=t("deps.btn_refresh"),
                   command=self._refresh).pack(side="left", padx=(8, 0), ipadx=6)
        ttk.Button(frm_btn, text=t("deps.btn_close"),
                   command=self.destroy).pack(side="right", ipadx=6)

        # Journal d'installation
        frm_log = ttk.LabelFrame(self, text=t("deps.log_frame"), padding=6)
        frm_log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log = tk.Text(frm_log, height=8, width=70,
                           font=(MONO_FONT, 9), state="disabled",
                           bg="#1e1e1e", fg="#d4d4d4")
        sb = ttk.Scrollbar(frm_log, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

    def _build_command_frame(self):
        """Linux : commande du gestionnaire de paquets pour les outils facultatifs absents (à copier, jamais lancée)."""
        self._cmd_frame = ttk.LabelFrame(self, text=t("deps.linux_command_label"), padding=6)
        self._cmd_var = tk.StringVar()
        ttk.Entry(self._cmd_frame, textvariable=self._cmd_var, state="readonly",
                  font=(MONO_FONT, 9)).pack(side="left", fill="x", expand=True)
        self._btn_copy = ttk.Button(self._cmd_frame, text=t("deps.btn_copy_command"), command=self._copy_command)
        self._btn_copy.pack(side="left", padx=(6, 0))

    def _update_command_frame(self):
        missing = [d["name"] for d in DEPS if d["name"] in LINUX_PACKAGES and not dep_installed(d["exe"])]
        if not missing:
            self._cmd_frame.pack_forget()
            return
        command = linux_install_command(missing)
        self._cmd_var.set(command or t("deps.linux_no_manager"))
        self._btn_copy.configure(state="normal" if command else "disabled")
        self._cmd_frame.pack(fill="x", padx=12, pady=(0, 4), before=self._frm_btn)

    def _copy_command(self):
        self.clipboard_clear()
        self.clipboard_append(self._cmd_var.get())
        self._log(t("deps.linux_command_copied"), "#27ae60")

    def _log(self, text, color=None):
        self.log.configure(state="normal")
        tag = None
        if color:
            tag = color
            self.log.tag_configure(tag, foreground=color)
        self.log.insert("end", text + "\n", tag or "")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _open_url(self, url):
        if url:
            import webbrowser
            webbrowser.open(url)

    def _refresh(self):
        has_choco = IS_WINDOWS and choco_available()
        for row in self._rows:
            dep = row["dep"]
            installed = dep_installed(dep["exe"])
            if installed:
                row["lbl_status"].configure(text=t("deps.status_ok"), foreground="#27ae60")
                row["btn"].configure(state="disabled")
            else:
                level = "required" if dep["required"] else dep.get("level", "optional")
                text, color = {"required": ("deps.status_absent", "#c0392b"),
                               "recommended": ("deps.status_recommended", "#b9770e"),
                               "optional": ("deps.status_optional", "#7f8c8d")}[level]
                row["lbl_status"].configure(text=t(text), foreground=color)
                if dep_direct(dep) or has_choco:
                    row["btn"].configure(state="normal")
                else:
                    url = dep.get("url", "")
                    row["btn"].configure(state="normal" if url else "disabled")
        if not IS_WINDOWS:
            self._update_command_frame()

    def _install(self, dep):
        # ffprobe est installé via le paquet ffmpeg — on évite de le lancer deux fois
        if dep["name"] == "ffprobe":
            ffmpeg_dep = next(d for d in DEPS if d["name"] == "ffmpeg")
            dep = ffmpeg_dep
        self._choco_install([dep["choco"]])

    def _install_direct(self):
        """Outils que l'assistant sait télécharger lui-même (Deno) : pas de Chocolatey ni d'administrateur."""
        SetupWizardWindow(self, on_done=self._refresh)

    def _install_all(self):
        if not choco_available():
            self._log(t("deps.log_no_choco"), "#f5a623")
            return
        pkgs_seen = set()
        pkgs = []
        for dep in DEPS:
            if dep["choco"] not in pkgs_seen and not dep_installed(dep["exe"]):
                pkgs.append(dep["choco"])
                pkgs_seen.add(dep["choco"])
        if not pkgs:
            self._log(t("deps.log_all_installed"), "#27ae60")
            return
        self._choco_install(pkgs)

    def _choco_install(self, packages):
        if not choco_available():
            self._log(t("deps.log_no_choco"), "#f5a623")
            return
        pkg_str = " ".join(packages)
        cmd = f"choco install {pkg_str} -y & pause"
        self._log(t("deps.log_installing", pkgs=pkg_str), "#9cdcfe")
        self._log(t("deps.log_uac_warning"), "#dcdcaa")
        if not run_elevated(cmd):
            self._log(t("deps.log_elevation_cancelled"), "#f5a623")
            return

        # Actualiser après un délai (laisse le temps à l'UAC + choco)
        self.after(3000, self._refresh)


# Flags critiques que le GUI utilise — chacun doit être présent dans --help
_GUI_FLAGS = [
    "--audio-multistreams", "--embed-metadata", "--embed-thumbnail", "--embed-subs", "--merge-output-format",
    "--flat-playlist", "--fragment-retries", "--sleep-interval", "--sub-format",
    "--write-subs", "--compat-options", "--no-playlist",
]


# ══════════════════════════════════════════════════════════════════
#  Mise à jour & Diagnostic
# ══════════════════════════════════════════════════════════════════
class UpdateWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("upd.window_title"))
        self.resizable(True, False)
        self.minsize(580, 420)
        self.grab_set()
        self._build()
        self._show_version()

    def _build(self):
        pad = dict(padx=12, pady=6)

        # Version courante
        frm_ver = ttk.LabelFrame(self, text=t("upd.version_frame"), padding=8)
        frm_ver.pack(fill="x", **pad)
        self.var_ver = tk.StringVar(value=t("upd.version_reading"))
        ttk.Label(frm_ver, textvariable=self.var_ver,
                  font=(MONO_FONT, 10)).pack(anchor="w")

        # ── Mise à jour ──────────────────────────────────────────
        frm_upd = ttk.LabelFrame(self, text=t("upd.update_frame"), padding=8)
        frm_upd.pack(fill="x", **pad)

        ttk.Label(frm_upd,
                  text=t("upd.update_desc"),
                  justify="left", wraplength=520).pack(anchor="w", pady=(0, 8))

        frm_upd_btns = ttk.Frame(frm_upd)
        frm_upd_btns.pack(anchor="w")
        self.btn_auto = ttk.Button(frm_upd_btns, text=t("upd.btn_auto_update"),
                                   command=self._auto_update)
        self.btn_auto.pack(side="left", ipadx=6)
        ttk.Button(frm_upd_btns, text=t("upd.btn_replace_exe"),
                   command=self._replace_exe).pack(side="left", padx=(10, 0), ipadx=6)

        # ── Diagnostic ──────────────────────────────────────────
        frm_diag = ttk.LabelFrame(self, text=t("upd.diag_frame"), padding=8)
        frm_diag.pack(fill="x", **pad)

        ttk.Label(frm_diag,
                  text=t("upd.diag_desc"),
                  justify="left", wraplength=520).pack(anchor="w", pady=(0, 8))

        self.btn_diag = ttk.Button(frm_diag, text=t("upd.btn_run_diag"),
                                   command=self._run_diag)
        self.btn_diag.pack(anchor="w", ipadx=6)

        # Journal (update + diagnostic)
        frm_log = ttk.LabelFrame(self, text=t("upd.log_frame"), padding=6)
        frm_log.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.log = tk.Text(frm_log, height=12, font=(MONO_FONT, 9),
                           state="disabled", bg="#1e1e1e", fg="#d4d4d4",
                           wrap="word")
        sb = ttk.Scrollbar(frm_log, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

        ttk.Button(self, text=t("upd.btn_close"), command=self.destroy).pack(
            anchor="e", padx=12, pady=(0, 10), ipadx=8)

    # ── Helpers journal ─────────────────────────────────────────
    def _log(self, text, color=None):
        self.log.configure(state="normal")
        if color:
            tag = f"c{color.replace('#','')}"
            self.log.tag_configure(tag, foreground=color)
            self.log.insert("end", text + "\n", tag)
        else:
            self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    # ── Version ─────────────────────────────────────────────────
    def _show_version(self):
        def _get():
            try:
                r = subprocess.run([YTDLP, "--version"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   **NO_WINDOW)
                ver = r.stdout.strip() or t("upd.ver_unknown")
            except Exception:
                ver = t("upd.ver_error")
            self.after(0, lambda: self.var_ver.set(
                f"yt-dlp  {ver}   ({YTDLP})"))
        threading.Thread(target=_get, daemon=True).start()

    # ── Mise à jour auto ─────────────────────────────────────────
    def _auto_update(self):
        self._log_clear()
        self.btn_auto.configure(state="disabled")
        self._log(t("upd.log_launching_update"), "#9cdcfe")

        def _run():
            try:
                proc = subprocess.Popen(
                    [YTDLP, "-U"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    **NO_WINDOW,
                )
                for line in proc.stdout:
                    line = line.rstrip()
                    if line:
                        color = ("#f66" if "error" in line.lower() else
                                 "#4ec94e" if "up to date" in line.lower() or
                                              "updated" in line.lower() else None)
                        self.after(0, lambda l=line, c=color: self._log(l, c))
                proc.wait()
            except Exception as e:
                self.after(0, lambda e=e: self._log(t("common.log_error", error=e), "#f66"))
            self.after(0, lambda: self.btn_auto.configure(state="normal"))
            self.after(0, self._show_version)

        threading.Thread(target=_run, daemon=True).start()

    # ── Remplacement manuel ──────────────────────────────────────
    def _replace_exe(self):
        if IS_WINDOWS:
            title = t("upd.replace_title_dialog")
            filetypes = [(t("upd.replace_filetypes_exe"), "*.exe"), (t("upd.replace_filetypes_all"), "*.*")]
        else:   # pas d'extension .exe : tous les fichiers
            title = t("upd.replace_title_dialog_linux")
            filetypes = [(t("upd.replace_filetypes_all"), "*")]
        src = filedialog.askopenfilename(title=title, filetypes=filetypes, parent=self)
        if not src:
            return
        try:
            import shutil as _sh
            # Sauvegarde de l'ancien exe
            backup = YTDLP + ".bak"
            if os.path.exists(YTDLP):
                _sh.copy2(YTDLP, backup)
                self._log(t("upd.log_backup", path=backup), "#888")
            _sh.copy2(src, YTDLP)
            if not IS_WINDOWS:
                os.chmod(YTDLP, 0o755)   # un fichier téléchargé n'est pas exécutable
            self._log(t("upd.log_replace_ok", src=src), "#4ec94e")
            self._log(t("upd.log_replace_check"), "#dcdcaa")
        except Exception as e:
            self._log(t("upd.log_replace_fail", error=e), "#f66")
        self._show_version()

    # ── Diagnostic ───────────────────────────────────────────────
    def _run_diag(self):
        self._log_clear()
        self.btn_diag.configure(state="disabled")
        self._log(t("upd.log_diag_header"), "#888")

        def _diag():
            # 1. Exe présent ?
            if os.path.exists(YTDLP):
                self.after(0, lambda: self._log(t("upd.log_diag_exe_ok", path=YTDLP), "#4ec94e"))
            else:
                self.after(0, lambda: self._log(t("upd.log_diag_exe_missing", path=YTDLP), "#f66"))
                self.after(0, lambda: self.btn_diag.configure(state="normal"))
                return

            # 2. Version
            try:
                r = subprocess.run([YTDLP, "--version"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   **NO_WINDOW)
                ver = r.stdout.strip()
                self.after(0, lambda v=ver: self._log(t("upd.log_diag_version_ok", v=v), "#4ec94e"))
            except Exception as e:
                self.after(0, lambda e=e: self._log(t("upd.log_diag_version_fail", error=e), "#f66"))
                self.after(0, lambda: self.btn_diag.configure(state="normal"))
                return

            # 3. Flags requis (parse --help)
            try:
                h = subprocess.run([YTDLP, "--help"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace",
                                   **NO_WINDOW)
                help_text = h.stdout + h.stderr
            except Exception as e:
                self.after(0, lambda e=e: self._log(t("upd.log_diag_help_fail", error=e), "#f66"))
                self.after(0, lambda: self.btn_diag.configure(state="normal"))
                return

            self.after(0, lambda: self._log(t("upd.log_diag_flags_header"), "#888"))
            all_ok = True
            for flag in _GUI_FLAGS:
                present = flag in help_text
                if present:
                    self.after(0, lambda f=flag:
                               self._log(f"  ✔ {f}", "#4ec94e"))
                else:
                    all_ok = False
                    self.after(0, lambda f=flag:
                               self._log(t("upd.log_diag_flag_missing", flag=f, desc=""), "#f66"))

            # 4. ffmpeg
            import shutil as _sh
            ffmpeg_ok = _sh.which("ffmpeg") is not None
            self.after(0, lambda ok=ffmpeg_ok: self._log(
                t("upd.log_diag_ffmpeg_ok") if ok else t("upd.log_diag_ffmpeg_missing"),
                "#4ec94e" if ok else "#f66"))

            # 5. Verdict
            verdict_ok = all_ok and ffmpeg_ok
            self.after(0, lambda ok=verdict_ok: self._log(
                t("upd.log_diag_verdict_ok") if ok else t("upd.log_diag_verdict_warn"),
                "#4ec94e" if ok else "#e67e22"))

            self.after(0, lambda: self.btn_diag.configure(state="normal"))

        threading.Thread(target=_diag, daemon=True).start()


# ══════════════════════════════════════════════════════════════════
#  File de téléchargement (utilisée par l'inspecteur de playlist)
# ══════════════════════════════════════════════════════════════════
class DownloadQueueWindow(tk.Toplevel):
    def __init__(self, parent, rows, build_args_fn, inspector=None):
        super().__init__(parent)
        self.title(t("dlq.window_title"))
        self.geometry("860x520")
        self.minsize(640, 400)
        self._rows = rows
        self._build_args = build_args_fn
        self._inspector = inspector  # PlaylistInspectorWindow, pour lire les variables globales
        self._stop_flag = threading.Event()
        self._skip_flag = threading.Event()
        self._process = None
        self._current_dl_files = []
        self._paused = False
        self._downloading = False
        self._build()

    def _build(self):
        self.var_status = tk.StringVar(value=t("dlq.status_starting"))
        ttk.Label(self, textvariable=self.var_status, anchor="w",
                  font=(UI_FONT, 9)).pack(fill="x", padx=8, pady=(8, 2))

        self.var_progress = tk.DoubleVar(value=0)
        ttk.Progressbar(self, variable=self.var_progress, maximum=100,
                        mode="determinate").pack(fill="x", padx=8, pady=(0, 4))

        frm_log = ttk.LabelFrame(self, text=t("dlq.log_frame_label"), padding=6)
        frm_log.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.log = tk.Text(frm_log, wrap="word", font=(MONO_FONT, 9),
                           state="disabled", bg="#1e1e1e", fg="#d4d4d4")
        sb = ttk.Scrollbar(frm_log, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

        frm_btn = ttk.Frame(self, padding=(8, 0, 8, 8))
        frm_btn.pack(fill="x")
        self.btn_pause = ttk.Button(frm_btn, text=t("dlq.btn_pause"), command=self._toggle_pause)
        self.btn_pause.pack(side="left", ipadx=6)
        self.btn_skip = ttk.Button(frm_btn, text=t("dlq.btn_skip"), command=self._skip)
        self.btn_skip.pack(side="left", padx=(6, 0), ipadx=6)
        self.btn_close = ttk.Button(frm_btn, text=t("dlq.btn_close"),
                                    command=self._close)
        self.btn_close.pack(side="right", ipadx=6)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _log(self, text, color=None):
        try:
            self.log.configure(state="normal")
            if color:
                tag = f"c{color.replace('#','')}"
                self.log.tag_configure(tag, foreground=color)
                self.log.insert("end", text + "\n", tag)
            else:
                self.log.insert("end", text + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        except tk.TclError:
            pass

    def _kill_and_cleanup(self):
        """Tue le processus yt-dlp en cours et supprime les fichiers partiels.

        Les fichiers de la liste ne sont supprimés que si yt-dlp tournait encore : fermer la fenêtre après
        un téléchargement terminé ne doit jamais effacer ce qui vient d'être téléchargé."""
        was_running = self._process is not None and self._process.poll() is None
        if self._paused and self._process:
            self._resume_process(self._process.pid)
            self._paused = False
        if self._process:
            kill_process_tree(self._process)
        files = list(self._current_dl_files) if was_running else []
        self._current_dl_files = []
        since = getattr(self, "_dl_started", None)

        # Répertoire de sortie connu via l'inspecteur (filet de sécurité si files est vide)
        insp_outdir = ""
        if was_running and self._inspector is not None:
            try:
                insp_outdir = self._inspector.var_g_outdir.get().strip()
            except Exception:
                pass

        self.after(0, lambda n=len(files): self._log(
            t("dlq.cleanup_n_files", n=n), "#888"))

        def _try_remove(path):
            import time
            for attempt in range(5):
                try:
                    if not os.path.exists(path):
                        return True
                    os.remove(path)
                    self.after(0, lambda p=path: self._log(
                        t("dlq.cleanup_ok", name=os.path.basename(p)), "#6ec26e"))
                    return True
                except Exception as e:
                    if attempt == 4:
                        self.after(0, lambda p=path, err=e: self._log(
                            t("dlq.cleanup_fail", name=os.path.basename(p), error=err), "#f66"))
                    time.sleep(1.5)
            return False

        def _try_remove_recent(path):
            """Repli : ne supprime que ce que la vidéo interrompue vient d'écrire (voir modified_since)."""
            if modified_since(path, since):
                _try_remove(path)

        def _remove_by_suffix(path, d):
            """Fallback : si le chemin exact n'existe pas, cherche par suffixe ou tige normalisée."""
            import re as _re
            name = os.path.basename(path)

            def _norm(s):
                """Normalise : retire les chars de sanitisation yt-dlp pour comparer."""
                s = s.replace('：', '').replace(':', '').replace('＊', '').replace('？', '')
                s = s.replace('＂', '').replace('＜', '').replace('＞', '').replace('｜', '')
                return _re.sub(r'\s+', ' ', s).strip().lower()

            # Cas 1 : double extension spécifique au flux (.f160.mp4, .f140-20.m4a, .en.srt…)
            m = _re.search(r'(\.[a-zA-Z0-9][a-zA-Z0-9\-]*\.[a-zA-Z0-9]{2,4}'
                           r'(?:\.part|\.ytdl)?)$', name)
            if m:
                suffix = m.group(1)
                try:
                    for fname in os.listdir(d):
                        if (fname.endswith(suffix) or fname.endswith(suffix + ".part")
                                or fname.endswith(suffix + ".ytdl")):
                            _try_remove_recent(os.path.join(d, fname))
                except OSError:
                    pass
                return

            # Cas 2 : extension simple (miniature .jpg/.webp, .png…)
            # Correspondance par tige normalisée + même extension
            stem, ext = os.path.splitext(name)
            if not ext or len(stem) < 4:
                return
            stem_norm = _norm(stem)
            ext_lower = ext.lower()
            try:
                for fname in os.listdir(d):
                    fstem, fext = os.path.splitext(fname)
                    if fext.lower() == ext_lower and _norm(fstem) == stem_norm:
                        _try_remove_recent(os.path.join(d, fname))
                    elif fext.lower() == ext_lower + ".part" and _norm(fstem) == stem_norm:
                        _try_remove_recent(os.path.join(d, fname))
            except OSError:
                pass

        def _cleanup(flist, outdir):
            import time, glob as _gl
            time.sleep(2)
            dirs = set()
            for path in flist:
                d = os.path.dirname(path)
                if d:
                    dirs.add(d)
                if os.path.exists(path) or os.path.exists(path + ".part"):
                    for c in (path, path + ".part", path + ".ytdl"):
                        _try_remove(c)
                else:
                    # Mismatch de sanitisation titre → cherche par suffixe
                    _remove_by_suffix(path, d)
            if outdir and os.path.isdir(outdir):
                dirs.add(outdir)
            for d in dirs:
                for pat in ("*.part", "*.ytdl"):
                    for f in _gl.glob(os.path.join(d, pat)):
                        _try_remove_recent(f)

        _thread = threading.Thread(target=_cleanup, args=(files, insp_outdir), daemon=True)
        self._cleanup_thread = _thread
        _thread.start()

    def _toggle_pause(self):
        if not self._downloading or not self._process:
            return
        if self._paused:
            self._resume_process(self._process.pid)
            self._paused = False
            self.after(0, lambda: self.btn_pause.configure(text=t("dlq.btn_pause")))
            self.after(0, lambda: self._log(t("dlq.log_resumed"), "#9cdcfe"))
        else:
            self._suspend_process(self._process.pid)
            self._paused = True
            self.after(0, lambda: self.btn_pause.configure(text=t("dlq.btn_resume")))
            self.after(0, lambda: self._log(t("dlq.log_paused"), "#f5a623"))

    def _skip(self):
        if not self._downloading:
            return
        self._skip_flag.set()
        self._kill_and_cleanup()
        self.after(0, lambda: self._log(t("dlq.log_skipped"), "#f5a623"))

    def _stop(self):
        self._stop_flag.set()
        self._kill_and_cleanup()

    def _close(self):
        """Arrête le téléchargement, attend la fin du nettoyage, puis ferme."""
        self._stop()
        def _wait_and_destroy():
            _thread = getattr(self, "_cleanup_thread", None)
            if _thread:
                _thread.join()
            try:
                self.after(0, self.destroy)
            except Exception:
                pass
        threading.Thread(target=_wait_and_destroy, daemon=True).start()

    def _suspend_process(self, pid):
        suspend_process_tree(pid)

    def _resume_process(self, pid):
        resume_process_tree(pid)

    def start(self):
        threading.Thread(target=self._run_guarded, daemon=True).start()

    def _run_guarded(self):
        try:
            self._run()
        except Exception as exc:
            self._downloading = False

            def _fail(e=exc):
                try:
                    self._log(t("dlq.log_internal_error", error=e), "#f66")
                    self.var_status.set(t("dlq.status_interrupted"))
                    self.btn_pause.configure(state="disabled")
                    self.btn_skip.configure(state="disabled")
                    self.btn_close.configure(text=t("dlq.btn_close_done"))
                except tk.TclError:
                    pass
            try:
                self.after(0, _fail)
            except (tk.TclError, RuntimeError):
                pass

    _RE_DEST   = re.compile(r"\[download\] Destination:\s+(.+)")
    _RE_SUBS   = re.compile(r"\[info\] Writing video (?:subtitles|automatic captions) to:\s+(.+)")
    _RE_FINAL  = re.compile(r'\[Merger\] Merging formats into "(.+)"|\[ExtractAudio\] Destination:\s+(.+)'
                            r'|\[Video(?:Remuxer|Convertor)\].*?Destination:\s+"?(.+?)"?\s*$')
    _RE_THUMB  = re.compile(r"\[info\] (?:Writing|Downloading) video thumbnail \S+ to:\s+(.+)")
    _RE_THUMB2 = re.compile(r'\[ThumbnailsConvertor\] Converting thumbnail "(.+?)" to ')

    def _run_one(self, args):
        """Lance yt-dlp pour une commande, retourne (returncode, output_lines)."""
        lines = []
        run_args, conf_file = command_file_args(args)
        try:
            self._process = subprocess.Popen(
                run_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                **PROCESS_GROUP,
            )
            for line in self._process.stdout:
                if self._skip_flag.is_set() or self._stop_flag.is_set():
                    break
                line = line.rstrip()
                if not line:
                    continue
                lines.append(line)
                m = self._RE_DEST.search(line)
                if m:
                    path = m.group(1).strip()
                    if path not in self._current_dl_files:
                        self._current_dl_files.append(path)
                mt = self._RE_THUMB.search(line)
                if mt:
                    thumb = mt.group(1).strip()
                    base = os.path.splitext(thumb)[0]
                    for ext in (os.path.splitext(thumb)[1], ".jpg", ".png", ".webp"):
                        p = base + ext
                        if p not in self._current_dl_files:
                            self._current_dl_files.append(p)
                msub = self._RE_SUBS.search(line)
                if msub:
                    sub_path = msub.group(1).strip()
                    if sub_path not in self._current_dl_files:
                        self._current_dl_files.append(sub_path)
                mfin = self._RE_FINAL.search(line)
                if mfin:
                    # fichier final : sauter ou arrêter la vidéo en cours le supprime aussi (« tout supprimer »)
                    final = next(g for g in mfin.groups() if g).strip()
                    if final not in self._current_dl_files:
                        self._current_dl_files.append(final)
                mt2 = self._RE_THUMB2.search(line)
                if mt2:
                    thumb2 = mt2.group(1).strip()
                    if thumb2 not in self._current_dl_files:
                        self._current_dl_files.append(thumb2)
                    base2 = os.path.splitext(thumb2)[0]
                    for ext in (".jpg", ".png", ".webp"):
                        p = base2 + ext
                        if p not in self._current_dl_files:
                            self._current_dl_files.append(p)
                color = ("#f66" if line.startswith("ERROR") else
                         "#9cdcfe" if line.startswith("[download]") else
                         "#dcdcaa" if line.startswith(("[ffmpeg]", "[Merger]")) else None)
                self.after(0, lambda l=line, c=color: self._log(l, c))
            self._process.wait()
            src = self._inspector
            browser = src.var_g_browser.get() if src is not None and hasattr(src, "var_g_browser") else ""
            hint = _cookie_hint("\n".join(lines), browser)
            if hint:
                self.after(0, lambda h=hint: self._log(h, "#f5a623"))
            return self._process.returncode, lines
        except Exception as e:
            self.after(0, lambda e=e: self._log(t("common.log_error", error=e), "#f66"))
            advice = av_advice(e)
            if advice:
                self.after(0, lambda a=advice: self._log(a, "#f5a623"))
            return -1, lines
        finally:
            remove_command_file(conf_file)

    @staticmethod
    def _format_not_available(lines):
        return any(
            "Requested format is not available" in l or "format is not available" in l.lower()
            for l in lines
        )

    @staticmethod
    def _subtitle_error(lines):
        return any(
            "Unable to download video subtitles" in l or
            ("subtitles" in l.lower() and ("429" in l or "403" in l or "error" in l.lower()))
            for l in lines
        )

    def _probe_secondary(self, vid_url, lang_codes):
        """
        Pour chaque code langue, vérifie via --simulate si la piste audio existe.
        Retourne (available: list, absent: list).
        Exécuté dans le thread de téléchargement (pas le thread UI).
        """
        import concurrent.futures

        src = self._inspector if self._inspector is not None else self
        browser = src.var_g_browser.get() if hasattr(src, "var_g_browser") else BROWSER_OFF
        cookie_args = ["--cookies-from-browser", browser] if browser != BROWSER_OFF else []

        def probe_one(lang):
            try:
                r = subprocess.run(
                    [YTDLP, "-f", f"bestaudio[language^={lang}]",
                     "--simulate", "--no-warnings", "--no-playlist"]
                    + cookie_args + ["--", vid_url],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    **NO_WINDOW, timeout=20,
                )
                ok = r.returncode == 0 and not self._format_not_available(
                    r.stdout.splitlines() + r.stderr.splitlines()
                )
                return lang, ok
            except Exception:
                return lang, False

        available, absent = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(probe_one, lang): lang for lang in lang_codes}
            for fut in concurrent.futures.as_completed(futures):
                lang, ok = fut.result()
                (available if ok else absent).append(lang)

        # Préserver l'ordre original
        available = [l for l in lang_codes if l in available]
        absent    = [l for l in lang_codes if l in absent]
        return available, absent

    def _run(self):
        total = len(self._rows)
        report = []  # [{title, status, dropped, error}]
        self._downloading = True

        for i, row in enumerate(self._rows):
            if self._stop_flag.is_set():
                break
            self._skip_flag.clear()
            self._current_dl_files = []
            self._dl_started = time.time()
            # toujours remettre le bouton : _kill_and_cleanup a déjà repris le processus en pause et baissé _paused
            self._paused = False
            self.after(0, lambda: self.btn_pause.configure(text=t("dlq.btn_pause")))
            title = row["vid"]["title"]
            vid_url = f"https://www.youtube.com/watch?v={row['vid']['id']}"
            self.after(0, lambda t=title, ix=i, tot=total:
                       self.var_status.set(f"[{ix+1}/{tot}]  {t}"))
            self.after(0, lambda ix=i, tot=total:
                       self.var_progress.set(ix / tot * 100))

            insp = self._inspector
            dropped = []
            sub_dropped = False
            rc = -1
            out_lines = []

            # Mode intégration ST : les subs sont inclus dans Phase 1.
            # Mode écriture ST : Phase 1 sans subs, Phase 2 écrit les .srt séparément.
            embed_subs = (insp.var_g_embed_subs.get() if insp is not None else False)

            # ── Phase 1 : vidéo (+ subs intégrés si embed_subs) ──────
            args_vid = self._build_args(row, skip_subs=not embed_subs)
            cmd_str = " ".join(f'"{a}"' if " " in a else a for a in args_vid)
            self.after(0, lambda s=cmd_str: self._log("$ " + s, "#666"))
            rc, out_lines = self._run_one(args_vid)

            # Embed mode : si l'échec vient des subs, relancer sans subs
            if rc != 0 and embed_subs and self._subtitle_error(out_lines):
                self.after(0, lambda:
                           self._log(t("dlq.log_sub_fail_retry"), "#f5a623"))
                args_vid = self._build_args(row, skip_subs=True)
                cmd_str = " ".join(f'"{a}"' if " " in a else a for a in args_vid)
                self.after(0, lambda s=cmd_str: self._log("[retry-subs] $ " + s, "#666"))
                rc, out_lines = self._run_one(args_vid)
                sub_dropped = True

            # ── Probe + relance si format audio indisponible ───────
            # Calculer initial_secondary uniquement pour le probe (union global+vidéo+blocs)
            initial_secondary = []
            if rc != 0 and self._format_not_available(out_lines):
                if insp is not None:
                    g_sec = list(insp._global_secondary())
                    v_sec = list(row["secondary_widget"].get_selected())
                    blk = [SCRIPT_BLOCKS_MAP[c][1]
                           for c in insp._g_blocks.get_selected()
                           if SCRIPT_BLOCKS_MAP.get(c, [""])[0] == "_alang_"]
                    seen = set(g_sec)
                    initial_secondary = list(g_sec)
                    for lang in v_sec + blk:
                        if lang not in seen:
                            initial_secondary.append(lang)
                            seen.add(lang)
                else:
                    initial_secondary = []

            if (rc != 0 and initial_secondary
                    and self._format_not_available(out_lines)):

                self.after(0, lambda n=len(initial_secondary):
                           self._log(t("dlq.log_probe_secondary", n=n), "#f5a623"))

                available, absent = self._probe_secondary(vid_url, initial_secondary)

                if absent:
                    self.after(0, lambda ab=absent, av=available:
                               self._log(t("dlq.log_probe_result",
                                           ab=', '.join(ab),
                                           av=', '.join(av) or t("dlq.log_probe_none")), "#f5a623"))
                    dropped = absent
                    # Le retry audio est toujours skip_subs=True ; en embed mode, les subs
                    # ne seront pas intégrés dans cette relance
                    if embed_subs and not sub_dropped:
                        sub_dropped = True
                    args2 = self._build_args(row, secondary_override=available, skip_subs=True)
                    cmd_str2 = " ".join(f'"{a}"' if " " in a else a for a in args2)
                    self.after(0, lambda s=cmd_str2: self._log("[retry] $ " + s, "#666"))
                    rc, out_lines = self._run_one(args2)
                else:
                    self.after(0, lambda:
                               self._log(t("dlq.log_probe_all_ok"), "#f5a623"))

            # ── Phase 2 : sous-titres séparément (mode écriture uniquement) ──
            # En mode embed, les subs étaient dans Phase 1. Si sub_dropped, ils ont échoué.
            if rc == 0 and not embed_subs:
                args_subs = self._build_args(row, subs_only=True)
                if args_subs:
                    cmd_sub = " ".join(f'"{a}"' if " " in a else a for a in args_subs)
                    self.after(0, lambda s=cmd_sub: self._log("[subs] $ " + s, "#666"))
                    rc_sub, sub_lines = self._run_one(args_subs)
                    if rc_sub != 0:
                        sub_dropped = True
                        self.after(0, lambda:
                                   self._log(t("dlq.log_subs_ignored"), "#f5a623"))

            # ── Consigner le résultat ──────────────────────────────
            if self._stop_flag.is_set():
                break  # interrompu — ne pas consigner d'erreur, _finish affiche le message
            if self._skip_flag.is_set():
                status = "sauté"
                self.after(0, lambda _title=title:
                           self._log(t("dlq.log_skipped_title", title=_title), "#f5a623"))
            elif rc == 0:
                if dropped or sub_dropped:
                    status = "ajusté"
                    details = []
                    if dropped:
                        details.append(t("dlq.log_adjusted_tracks", liste=', '.join(dropped)))
                    if sub_dropped:
                        details.append(t("dlq.log_adjusted_subs"))
                    self.after(0, lambda _title=title, d=details:
                               self._log(t("dlq.log_adjusted_title", title=_title, details='; '.join(d)), "#9cdcfe"))
                else:
                    status = "ok"
                    self.after(0, lambda _title=title:
                               self._log(t("dlq.log_ok_title", title=_title), "#6ec26e"))
            else:
                status = "erreur"
                self.after(0, lambda _title=title, c=rc:
                           self._log(t("dlq.log_fail_title", title=_title, rc=c), "#f66"))

            report.append({
                "title": title,
                "status": status,
                "dropped": list(dropped),
                "rc": rc,
            })
            if status != "erreur" and not self._skip_flag.is_set() and not self._stop_flag.is_set():
                self._current_dl_files = []   # fichiers définitifs : plus rien à nettoyer

            # Attendre la fin du nettoyage avant de lancer la vidéo suivante
            if self._skip_flag.is_set():
                self.after(0, lambda: self.var_status.set(t("dlq.status_cleanup")))
                _thread = getattr(self, "_cleanup_thread", None)
                if _thread:
                    _thread.join()

        stopped = self._stop_flag.is_set()
        self._downloading = False

        def _finish():
            try:
                self.var_progress.set(100)
                self.var_status.set(
                    t("dlq.status_interrupted") if stopped else
                    t("dlq.status_finished", total=total))
                self.btn_pause.configure(state="disabled")
                self.btn_skip.configure(state="disabled")
                self.btn_close.configure(text=t("dlq.btn_close_done"))
                if not stopped and report:
                    self.after(200, lambda: DownloadReportWindow(self, report))
            except tk.TclError:
                pass

        self.after(0, _finish)


# ══════════════════════════════════════════════════════════════════
#  Rapport de fin de téléchargement
# ══════════════════════════════════════════════════════════════════
class DownloadReportWindow(tk.Toplevel):
    """Fenêtre de bilan affichée après la fin d'une file de téléchargement."""

    _STATUS_COLOR = {
        "ok":     "#6ec26e",
        "ajusté": "#f5a623",
        "erreur": "#f66666",
        "sauté":  "#9cdcfe",
    }
    @property
    def _STATUS_LABEL(self):
        return {
            "ok":     t("report.status_ok"),
            "ajusté": t("report.status_adjusted"),
            "erreur": t("report.status_error"),
            "sauté":  t("report.status_skipped"),
        }

    def __init__(self, parent, report):
        super().__init__(parent)
        self.title(t("report.window_title"))
        self.resizable(True, True)
        self.minsize(560, 260)

        n_ok  = sum(1 for r in report if r["status"] == "ok")
        n_adj = sum(1 for r in report if r["status"] == "ajusté")
        n_err = sum(1 for r in report if r["status"] == "erreur")
        n_skip = sum(1 for r in report if r["status"] == "sauté")
        total = len(report)

        h = max(280, min(700, 100 + total * 36))
        self.geometry(f"680x{h}")

        # ── Résumé en haut ─────────────────────────────────────────
        frm_sum = ttk.Frame(self, padding=(12, 10, 12, 6))
        frm_sum.pack(fill="x")
        ttk.Label(frm_sum,
                  text=t("report.summary", total=total, n_ok=n_ok, n_adj=n_adj, n_err=n_err)
                       + (t("report.summary_skipped", n=n_skip) if n_skip else ""),
                  font=(UI_FONT, 10, "bold")).pack(side="left")

        # ── Liste scrollable ────────────────────────────────────────
        frm_cv = ttk.Frame(self, padding=(8, 0, 8, 0))
        frm_cv.pack(fill="both", expand=True)

        canvas = tk.Canvas(frm_cv, highlightthickness=0)
        vsb = ttk.Scrollbar(frm_cv, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        cwin = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cwin, width=e.width))
        inner.columnconfigure(1, weight=1)

        for idx, r in enumerate(report):
            bg = "#1e1e1e" if idx % 2 == 0 else "#252525"
            color = self._STATUS_COLOR[r["status"]]
            lbl_status = r["status"]

            frm_row = tk.Frame(inner, bg=bg)
            frm_row.grid(row=idx, column=0, columnspan=3, sticky="ew", pady=0)
            frm_row.columnconfigure(1, weight=1)

            tk.Label(frm_row, text=self._STATUS_LABEL[lbl_status],
                     fg=color, bg=bg, width=12, anchor="w",
                     font=(MONO_FONT, 9, "bold")).grid(row=0, column=0, padx=(8, 4), pady=4, sticky="w")

            title_text = r["title"][:72] + "…" if len(r["title"]) > 72 else r["title"]
            tk.Label(frm_row, text=title_text, fg="#d4d4d4", bg=bg,
                     anchor="w", font=(UI_FONT, 9)).grid(row=0, column=1, sticky="ew", pady=4)

            if r["dropped"]:
                detail = t("report.tracks_ignored", liste=", ".join(r["dropped"]))
                tk.Label(frm_row, text=detail, fg="#888", bg=bg,
                         anchor="w", font=(UI_FONT, 8, "italic")).grid(
                    row=1, column=1, columnspan=2, sticky="w", padx=(0, 8), pady=(0, 4))

        # ── Bouton fermer ───────────────────────────────────────────
        frm_btn = ttk.Frame(self, padding=(8, 6))
        frm_btn.pack(fill="x")
        ttk.Button(frm_btn, text=t("report.btn_close"), command=self.destroy).pack(side="right", ipadx=10)


# ══════════════════════════════════════════════════════════════════
#  Widget multi-sélection avec popup modale
# ══════════════════════════════════════════════════════════════════
class BrowserOptionsWindow(tk.Toplevel):
    """Option : afficher ou masquer Edge, Chrome et Brave dans les listes de navigateurs (cookies)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("browsers.title"))
        self.resizable(False, False)
        self.transient(parent)
        frm = ttk.Frame(self, padding=14)
        frm.pack(fill="both", expand=True)
        self.var = tk.BooleanVar(value=show_blocked_browsers())
        ttk.Checkbutton(frm, text=t("browsers.chk"), variable=self.var, command=self._toggle).pack(anchor="w")
        ttk.Label(frm, text=t("browsers.explain"), wraplength=460, justify="left",
                  foreground="#555555").pack(anchor="w", pady=(10, 12))
        ttk.Button(frm, text=t("browsers.close"), command=self.destroy).pack(anchor="e", ipadx=8)

    def _toggle(self):
        update_config("show_blocked_browsers", bool(self.var.get()))
        refresh_browser_combos()


class MultiCheckSelect(ttk.Frame):
    """Bouton qui ouvre une popup modale avec cases à cocher (multi-sélection)."""

    def __init__(self, master, placeholder="Désactivés", width=22, on_change=None,
                 tabs=None, **kw):
        """
        tabs : dict {tab_name: [(code, lbl), ...]} — si fourni, la popup affiche
               un ttk.Notebook avec un onglet par catégorie au lieu d'une liste plate.
        """
        super().__init__(master, **kw)
        self._placeholder = placeholder
        self._width = width
        self._on_change = on_change
        self._tabs = tabs          # None = liste plate, dict = onglets
        self._choices = []         # list of (code, display_label) — liste plate
        if tabs:
            for entries in tabs.values():
                self._choices.extend(entries)
        self._selected = set()
        self._btn = ttk.Button(self, text=placeholder, width=width,
                               command=self._open_popup)
        self._btn.pack(fill="x")

    def set_options(self, options):
        """options : list of (code, display_label). Préserve la sélection existante."""
        self._choices = list(options)
        codes = {c for c, _ in options}
        self._selected &= codes
        self._refresh_btn()

    def set_placeholder(self, text):
        self._placeholder = text
        self._refresh_btn()

    def set_enabled(self, enabled: bool):
        self._btn.configure(state="normal" if enabled else "disabled")

    def set_tabs(self, tabs: dict):
        """Remplace les onglets (tabs) et reconstruit _choices. Préserve la sélection valide."""
        self._tabs = tabs
        self._choices = []
        for entries in tabs.values():
            self._choices.extend(entries)
        codes = {c for c, _ in self._choices}
        self._selected &= codes
        self._refresh_btn()

    def get_selected(self):
        order = [c for c, _ in self._choices]
        return [c for c in order if c in self._selected]

    def set_selected(self, codes):
        self._selected = set(codes)
        self._refresh_btn()

    def _refresh_btn(self):
        labels = [lbl for c, lbl in self._choices if c in self._selected]
        text = ", ".join(labels) if labels else self._placeholder
        if len(text) > self._width - 1:
            text = text[:self._width - 2] + "…"
        self._btn.configure(text=text)

    def _open_popup(self):
        pop = tk.Toplevel(self.winfo_toplevel())
        pop.resizable(True, True)
        pop.transient(self.winfo_toplevel())
        pop.title("")
        self._btn.update_idletasks()
        x = self._btn.winfo_rootx()
        y = self._btn.winfo_rooty() + self._btn.winfo_height()
        pop.grab_set()

        check_vars = {}   # code → BooleanVar (tous onglets confondus)

        # ── Boutons communs (packés EN PREMIER → toujours visibles) ──
        frm_btns = ttk.Frame(pop)
        frm_btns.pack(side="bottom", pady=6, fill="x", padx=10)

        def _apply():
            self._selected = {c for c, v in check_vars.items() if v.get()}
            self._refresh_btn()
            pop.destroy()
            if self._on_change:
                self.after(10, self._on_change)

        ttk.Button(frm_btns, text=t("mcs.btn_apply"), command=_apply).pack(
            side="left", ipadx=6)
        ttk.Button(frm_btns, text=t("mcs.btn_close"),
                   command=pop.destroy).pack(side="left", padx=(6, 0), ipadx=6)

        if self._tabs:
            self._open_popup_tabs(pop, check_vars, x, y)
        else:
            n = len(self._choices)
            h = max(220, min(560, 100 + n * 28))
            w, h, x, y = _screen_fit_geometry(pop.winfo_screenwidth(), pop.winfo_screenheight(), 460, h, x, y)
            pop.geometry(f"{w}x{h}+{x}+{y}")
            pop.minsize(min(280, w), min(160, h))
            self._open_popup_flat(pop, check_vars, self._choices)

        pop.wait_window()

    # ── Popup liste plate (Audio secondaire, Sous-titres) ──────────
    def _open_popup_flat(self, pop, check_vars, choices):
        row_widgets = []   # (code, lbl_lower, widget)

        # Barre de recherche — top
        frm_search = ttk.Frame(pop)
        frm_search.pack(side="top", fill="x", padx=6, pady=(6, 2))
        ttk.Label(frm_search, text="🔍").pack(side="left", padx=(2, 4))
        var_search = tk.StringVar()
        ent_search = ttk.Entry(frm_search, textvariable=var_search)
        ent_search.pack(side="left", fill="x", expand=True)
        ent_search.focus_set()

        # Aucun / Tout — bottom, packés AVANT le canvas pour rester visibles
        frm_extra = ttk.Frame(pop)
        frm_extra.pack(side="bottom", fill="x", padx=10, pady=(0, 2))

        # Canvas scrollable — remplit l'espace restant
        frm_cv = ttk.Frame(pop)
        frm_cv.pack(side="top", fill="both", expand=True, padx=4, pady=(2, 0))
        canvas = tk.Canvas(frm_cv, highlightthickness=0)
        vsb = ttk.Scrollbar(frm_cv, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        cwin = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cwin, width=e.width))
        if not choices:
            ttk.Label(inner, text=t("mcs.no_option")).pack(padx=12, pady=8)
        else:
            for code, lbl in choices:
                var = tk.BooleanVar(value=code in self._selected)
                check_vars[code] = var
                cb = ttk.Checkbutton(inner, text=lbl, variable=var)
                cb.pack(fill="x", padx=10, pady=1)
                row_widgets.append((code, lbl.lower(), cb))

        def _on_search(*_):
            q = var_search.get().lower().strip()
            for code, lbl_low, w in row_widgets:
                if not q or q in lbl_low or q in code.lower():
                    w.pack(fill="x", padx=10, pady=1)
                else:
                    w.pack_forget()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(0)

        var_search.trace_add("write", _on_search)

        def _visible_codes():
            q = var_search.get().lower().strip()
            return [c for c, lbl_low, _ in row_widgets
                    if not q or q in lbl_low or q in c.lower()]

        ttk.Button(frm_extra, text=t("mcs.btn_all"),
                   command=lambda: [check_vars[c].set(True) for c in _visible_codes()]
                   ).pack(side="right", padx=(4, 0), ipadx=4)
        ttk.Button(frm_extra, text=t("mcs.btn_none"),
                   command=lambda: [check_vars[c].set(False) for c in _visible_codes()]
                   ).pack(side="right", ipadx=4)

    # ── Popup avec onglets (Bibliothèque de blocs) ─────────────────
    def _open_popup_tabs(self, pop, check_vars, x, y):
        w, h, x, y = _screen_fit_geometry(pop.winfo_screenwidth(), pop.winfo_screenheight(), 520, 480, x, y)
        pop.geometry(f"{w}x{h}+{x}+{y}")
        pop.minsize(min(400, w), min(300, h))

        # Barre de recherche globale (filtre tous les onglets)
        frm_search = ttk.Frame(pop)
        frm_search.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Label(frm_search, text="🔍").pack(side="left", padx=(2, 4))
        var_search = tk.StringVar()
        ent_search = ttk.Entry(frm_search, textvariable=var_search)
        ent_search.pack(side="left", fill="x", expand=True)
        ent_search.focus_set()

        nb = ttk.Notebook(pop)
        nb.pack(fill="both", expand=True, padx=4, pady=(2, 0))

        # tab_rows : {tab_name: [(code, lbl_lower, widget), ...]}
        tab_rows = {}
        tab_canvases = {}

        for tab_name, choices in self._tabs.items():
            frm_tab = ttk.Frame(nb)
            nb.add(frm_tab, text=f"  {tab_name}  ")

            canvas = tk.Canvas(frm_tab, highlightthickness=0)
            vsb = ttk.Scrollbar(frm_tab, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            inner = ttk.Frame(canvas)
            cwin = canvas.create_window((0, 0), window=inner, anchor="nw")
            inner.bind("<Configure>", lambda _, cv=canvas: cv.configure(scrollregion=cv.bbox("all")))
            canvas.bind("<Configure>", lambda e, cv=canvas, cw=cwin: cv.itemconfig(cw, width=e.width))
            rows = []
            for code, lbl in choices:
                var = tk.BooleanVar(value=code in self._selected)
                check_vars[code] = var
                cb = ttk.Checkbutton(inner, text=lbl, variable=var)
                cb.pack(fill="x", padx=10, pady=2)
                rows.append((code, lbl.lower(), cb))

            tab_rows[tab_name] = rows
            tab_canvases[tab_name] = canvas

            # Tout / Aucun par onglet
            frm_tab_btn = ttk.Frame(frm_tab)
            frm_tab_btn.pack(side="bottom", fill="x", padx=6, pady=3)
            ttk.Button(frm_tab_btn, text=t("mcs.btn_all"),
                       command=lambda r=rows: [check_vars[c].set(True) for c, _, _ in r]
                       ).pack(side="right", padx=(4, 0), ipadx=4)
            ttk.Button(frm_tab_btn, text=t("mcs.btn_none"),
                       command=lambda r=rows: [check_vars[c].set(False) for c, _, _ in r]
                       ).pack(side="right", ipadx=4)

        def _on_search(*_):
            q = var_search.get().lower().strip()
            for tab_name, rows in tab_rows.items():
                cv = tab_canvases[tab_name]
                for code, lbl_low, w in rows:
                    if not q or q in lbl_low or q in code.lower():
                        w.pack(fill="x", padx=10, pady=2)
                    else:
                        w.pack_forget()
                cv.configure(scrollregion=cv.bbox("all"))
                cv.yview_moveto(0)

        var_search.trace_add("write", _on_search)

        # ── Onglet Options (gestion des blocs) ────────────────────
        frm_opts_tab = ttk.Frame(nb)
        nb.add(frm_opts_tab, text="  ⚙ Options  ")
        self._build_blocks_options_tab(frm_opts_tab, pop, nb, tab_rows, tab_canvases, check_vars)

    def _build_blocks_options_tab(self, frm, pop, nb, tab_rows, tab_canvases, check_vars):
        """Construit l'onglet de gestion des blocs de script."""
        # ── Treeview ──────────────────────────────────────────────
        cols = ("type", "cat", "label", "args")
        tv = ttk.Treeview(frm, columns=cols, show="headings", selectmode="browse", height=12)
        tv.heading("type",  text=t("blocks.tv_col_type"),  anchor="w")
        tv.heading("cat",   text=t("blocks.tv_col_cat"),   anchor="w")
        tv.heading("label", text=t("blocks.tv_col_label"), anchor="w")
        tv.heading("args",  text=t("blocks.tv_col_args"),  anchor="w")
        tv.column("type",  width=70,  stretch=False)
        tv.column("cat",   width=110, stretch=False)
        tv.column("label", width=180, stretch=True)
        tv.column("args",  width=200, stretch=True)

        vsb_tv = ttk.Scrollbar(frm, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=vsb_tv.set)
        vsb_tv.pack(side="right", fill="y", padx=(0, 2), pady=4)
        tv.pack(fill="both", expand=True, padx=(4, 0), pady=4)

        tv.tag_configure("builtin", foreground="#888888")
        tv.tag_configure("custom",  foreground="#9cdcfe")

        def _refresh_tv():
            tv.delete(*tv.get_children())
            for cat, code, lbl, args in SCRIPT_BLOCKS:
                tv.insert("", "end", iid=code,
                          values=("built-in", cat, lbl, " ".join(args)),
                          tags=("builtin",))
            for cat, code, lbl, args in CUSTOM_BLOCKS:
                tv.insert("", "end", iid=f"custom_{code}",
                          values=("custom", cat, lbl, " ".join(args)),
                          tags=("custom",))

        _refresh_tv()

        # ── Boutons d'action ───────────────────────────────────────
        frm_btns = ttk.Frame(frm)
        frm_btns.pack(fill="x", padx=4, pady=(0, 4))

        def _get_selected_info():
            sel = tv.focus()
            if not sel:
                return None
            vals = tv.item(sel, "values")
            is_custom = vals[0] == "custom"
            code = sel[len("custom_"):] if sel.startswith("custom_") else sel
            return {"iid": sel, "is_custom": is_custom, "type": vals[0],
                    "cat": vals[1], "label": vals[2], "args": vals[3], "code": code}

        def _open_editor(prefill=None):
            """Ouvre la fenêtre d'ajout/modification d'un bloc."""
            edit_win = tk.Toplevel(pop)
            edit_win.title(t("blocks.editor_title_edit") if prefill else t("blocks.editor_title_add"))
            edit_win.resizable(False, False)
            edit_win.transient(pop)
            edit_win.grab_set()
            edit_win.geometry("480x230")

            frm_f = ttk.Frame(edit_win, padding=12)
            frm_f.pack(fill="both", expand=True)
            frm_f.columnconfigure(1, weight=1)

            all_cats = list(SCRIPT_BLOCKS_BY_TAB.keys())

            ttk.Label(frm_f, text=t("blocks.editor_label_cat")).grid(row=0, column=0, sticky="w", pady=4, padx=(0,8))
            var_cat = tk.StringVar(value=prefill["cat"] if prefill else all_cats[0])
            frm_cat_row = ttk.Frame(frm_f)
            frm_cat_row.grid(row=0, column=1, sticky="ew", pady=4)
            frm_cat_row.columnconfigure(0, weight=1)
            cb_cat = ttk.Combobox(frm_cat_row, textvariable=var_cat,
                                  values=all_cats, state="readonly", width=20)
            cb_cat.grid(row=0, column=0, sticky="ew")

            def _new_category():
                name = simpledialog.askstring(
                    t("blocks.new_cat_title"), t("blocks.new_cat_prompt"),
                    parent=edit_win)
                if not name:
                    return
                name = name.strip()
                if not name:
                    return
                cur_vals = list(cb_cat["values"])
                if name not in cur_vals:
                    cur_vals.append(name)
                    cb_cat["values"] = cur_vals
                var_cat.set(name)

            ttk.Button(frm_cat_row, text="＋", width=3,
                       command=_new_category).grid(row=0, column=1, padx=(4, 0))

            ttk.Label(frm_f, text=t("blocks.editor_label_name")).grid(row=1, column=0, sticky="w", pady=4, padx=(0,8))
            var_lbl = tk.StringVar(value=prefill["label"] if prefill else "")
            ttk.Entry(frm_f, textvariable=var_lbl).grid(row=1, column=1, sticky="ew", pady=4)

            ttk.Label(frm_f, text=t("blocks.editor_label_args")).grid(row=2, column=0, sticky="w", pady=4, padx=(0,8))
            var_args = tk.StringVar(value=prefill["args"] if prefill else "")
            ttk.Entry(frm_f, textvariable=var_args).grid(row=2, column=1, sticky="ew", pady=4)
            ttk.Label(frm_f, text=t("blocks.editor_args_hint"),
                      foreground="#888", font=(UI_FONT, 8)
                      ).grid(row=3, column=1, sticky="w")

            def _save():
                import shlex as _shlex
                cat   = var_cat.get().strip()
                label = var_lbl.get().strip()
                args_str = var_args.get().strip()
                if not cat or not label or not args_str:
                    messagebox.showwarning(t("blocks.warn_fields_title"),
                                           t("blocks.warn_fields_msg"),
                                           parent=edit_win)
                    return
                try:
                    args_list = _shlex.split(args_str)
                except ValueError:
                    args_list = args_str.split()

                # Générer un code unique
                import re as _re
                base_code = _re.sub(r"[^a-z0-9]", "_", label.lower())[:24]
                code = base_code
                i = 2
                while code in SCRIPT_BLOCKS_MAP and (not prefill or code != prefill.get("code", "")):
                    code = f"{base_code}_{i}"; i += 1

                if prefill and prefill["is_custom"]:
                    _edit_custom_block(prefill["code"], cat, code, label, args_list)
                else:
                    _add_custom_block(cat, code, label, args_list)

                _refresh_tv()
                edit_win.destroy()

            frm_eb = ttk.Frame(edit_win, padding=(12, 0, 12, 10))
            frm_eb.pack(fill="x")
            ttk.Button(frm_eb, text=t("blocks.editor_btn_save"), command=_save).pack(side="left", ipadx=8)
            ttk.Button(frm_eb, text=t("blocks.editor_btn_cancel"), command=edit_win.destroy).pack(side="left", padx=(6,0))

        def _on_add():
            _open_editor()

        def _on_edit():
            info = _get_selected_info()
            if not info:
                return
            if not info["is_custom"]:
                messagebox.showinfo(t("blocks.info_builtin_no_edit_title"),
                                    t("blocks.info_builtin_no_edit_msg"),
                                    parent=pop)
                return
            _open_editor(prefill=info)

        def _on_delete():
            info = _get_selected_info()
            if not info:
                return
            if not info["is_custom"]:
                messagebox.showinfo(t("blocks.info_builtin_no_del_title"),
                                    t("blocks.info_builtin_no_del_msg"),
                                    parent=pop)
                return
            if messagebox.askyesno(t("blocks.confirm_del_title"),
                                   t("blocks.confirm_del_msg", label=info['label']),
                                   parent=pop):
                _delete_custom_block(info["code"])
                _refresh_tv()

        ttk.Button(frm_btns, text=t("blocks.btn_add"),    command=_on_add).pack(side="left", ipadx=6)
        ttk.Button(frm_btns, text=t("blocks.btn_edit"),   command=_on_edit).pack(side="left", padx=(6,0), ipadx=6)
        ttk.Button(frm_btns, text=t("blocks.btn_delete"), command=_on_delete).pack(side="left", padx=(6,0), ipadx=6)

        lbl_legend = ttk.Label(frm_btns,
                               text=t("blocks.legend"),
                               foreground="#888", font=(UI_FONT, 8))
        lbl_legend.pack(side="right", padx=4)


# ══════════════════════════════════════════════════════════════════
#  Inspecteur de playlist
# ══════════════════════════════════════════════════════════════════
REGISTRY_NAME = ".yt-dlp-registre.json"       # registre maître : id → url, titre, durée, fichier, date
ARCHIVE_NAME  = ".yt-dlp-archive.txt"         # dérivé du registre, lu par yt-dlp (--download-archive)
TITLES_NAME   = ".yt-dlp-archive.titles.tsv"  # boîte de réception écrite par yt-dlp (--print-to-file)
_MEDIA_EXTS   = {".mp4", ".mkv", ".webm", ".m4a", ".mp3", ".opus", ".mov", ".flv",
                 ".avi", ".ogg", ".wav", ".aac", ".flac", ".m4v"}


def _norm_title(s):
    return re.sub(r"[\W_]+", "", (s or "").casefold())


def _tmpl_esc(s):
    """Échappe % pour un modèle de sortie yt-dlp (-o) construit à partir d'un chemin ou d'un titre."""
    return s.replace("%", "%%")


def _watch_url(vid_id):
    return f"https://www.youtube.com/watch?v={vid_id}"


def _sync_registry(outdir):
    """Fusionne registre JSON + ids du .txt + boîte de réception TSV, réécrit le JSON
    et régénère le .txt. Retourne {id: {url, title, duration, file, date}}."""
    path = os.path.join(outdir, REGISTRY_NAME)
    videos = {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("videos"), dict):
            videos = data["videos"]
    except (OSError, ValueError):
        pass
    before = json.dumps(videos, sort_keys=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")

    inbox = os.path.join(outdir, TITLES_NAME)
    inbox_read = False
    try:
        with open(inbox, encoding="utf-8", errors="replace") as f:
            for line in f:
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) < 4 or not cols[0]:
                    continue
                try:
                    dur = int(float(cols[2]))
                except ValueError:
                    dur = None
                e = videos.setdefault(cols[0], {})
                e.update(url=_watch_url(cols[0]), title=cols[1], duration=dur,
                         file=os.path.basename(cols[3]))
                e.setdefault("date", now)
        inbox_read = True
    except OSError:
        pass

    try:
        with open(os.path.join(outdir, ARCHIVE_NAME), encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[-1] not in videos:
                    videos[parts[-1]] = {"url": _watch_url(parts[-1]), "title": "",
                                         "duration": None, "file": "", "date": ""}
    except OSError:
        pass

    if json.dumps(videos, sort_keys=True) != before or not os.path.isfile(path):
        _write_text_atomic(path, json.dumps({"version": 1, "videos": videos},
                                            ensure_ascii=False, indent=1))
    archive = "".join(f"youtube {i}\n" for i in sorted(videos))
    try:
        with open(os.path.join(outdir, ARCHIVE_NAME), encoding="utf-8") as f:
            same = f.read() == archive
    except OSError:
        same = False
    if not same and (videos or os.path.isfile(os.path.join(outdir, ARCHIVE_NAME))):
        _write_text_atomic(os.path.join(outdir, ARCHIVE_NAME), archive)
    if inbox_read:
        try:
            os.remove(inbox)
        except OSError:
            pass
    return videos


def _write_text_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _find_existing_matches(rows, outdir):
    """Lignes dont la vidéo semble déjà présente dans outdir mais absente du registre.
    Retourne [(row, nom_fichier, "title")]."""
    registry = _sync_registry(outdir)
    by_title = {}
    try:
        names = os.listdir(outdir)
    except OSError:
        return []
    for fn in names:
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in _MEDIA_EXTS:
            continue
        stem = re.sub(r"\s\(\d+\)$", "", stem)
        for variant in (stem, re.sub(r"^\d+\s-\s", "", stem)):
            key = _norm_title(variant)
            if key:
                by_title.setdefault(key, fn)
    found = []
    for row in rows:
        vid = row["vid"]
        if vid["id"] in registry:
            continue
        fn = by_title.get(_norm_title(vid.get("title")))
        if fn:
            found.append((row, fn, "title"))
    return found


def _register_in_archive(outdir, entries):
    """entries : [(id, titre, nom_fichier[, durée])] — inscrit au registre (et régénère le .txt)."""
    registry = _sync_registry(outdir)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for vid_id, title, fn, *rest in entries:
        if not re.fullmatch(r"[\w-]{11}", str(vid_id)):
            continue
        e = registry.setdefault(vid_id, {})
        e.update(url=_watch_url(vid_id), title=title, file=fn)
        if rest and rest[0]:
            e["duration"] = int(rest[0])
        e.setdefault("duration", None)
        e.setdefault("date", now)
    _write_text_atomic(os.path.join(outdir, REGISTRY_NAME),
                       json.dumps({"version": 1, "videos": registry},
                                  ensure_ascii=False, indent=1))
    _sync_registry(outdir)


def _clean_stem(fn):
    stem = re.sub(r"\s\(\d+\)$", "", os.path.splitext(fn)[0])
    return re.sub(r"^\d+\s-\s", "", stem)


def _scan_registry_folder(outdir):
    """Retourne (registre, fichiers_média, fichiers_absents_du_registre, nb_entrées_sans_titre)."""
    registry = _sync_registry(outdir)
    known_files = {e.get("file") for e in registry.values() if e.get("file")}
    known_titles = {_norm_title(e.get("title")) for e in registry.values() if e.get("title")}
    media, missing = [], []
    for fn in sorted(os.listdir(outdir)):
        if os.path.splitext(fn)[1].lower() not in _MEDIA_EXTS:
            continue
        media.append(fn)
        stem = re.sub(r"\s\(\d+\)$", "", os.path.splitext(fn)[0])
        if (fn in known_files or _norm_title(stem) in known_titles
                or _norm_title(_clean_stem(fn)) in known_titles):
            continue
        missing.append(fn)
    incomplete = sum(1 for e in registry.values() if not e.get("title"))
    return registry, media, missing, incomplete


def _local_duration(path):
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", path], capture_output=True, text=True,
                           timeout=20, **NO_WINDOW)
        return float(r.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _search_video(title, local_dur):
    """Cherche `title` sur YouTube via yt-dlp. Retourne (cand|None, tag) ;
    tag dans {"sure", "title", "check", "none"}."""
    try:
        r = subprocess.run([YTDLP, "--flat-playlist", "-j", "--no-warnings", "--",
                            f"ytsearch5:{title}"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=60, **NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return None, "none"
    cands = []
    for line in r.stdout.splitlines():
        try:
            c = json.loads(line)
        except ValueError:
            continue
        if (isinstance(c, dict) and c.get("title")
                and re.fullmatch(r"[\w-]{11}", str(c.get("id") or ""))):
            cands.append(c)
    if not cands:
        return None, "none"
    want = _norm_title(title)

    def same_title(c):
        got = _norm_title(c["title"])
        return bool(want) and (got == want or want in got or got in want)

    for c in cands:
        dur_ok = (local_dur is not None and c.get("duration") is not None
                  and abs(float(c["duration"]) - local_dur) <= 3)
        if dur_ok and same_title(c):
            return c, "sure"
    if local_dur is None:
        for c in cands:
            if _norm_title(c["title"]) == want:
                return c, "title"
    return cands[0], "check"


class _Tip:
    """Infobulle minimale ; `text` peut être une str ou un callable renvoyant une str."""
    def __init__(self, widget, text):
        self._w, self._text, self._tw = widget, text, None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _e=None):
        txt = self._text() if callable(self._text) else self._text
        if not txt or self._tw:
            return
        self._tw = tw = tk.Toplevel(self._w)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{self._w.winfo_rootx() + 12}+{self._w.winfo_rooty() + self._w.winfo_height() + 4}")
        tk.Label(tw, text=txt, bg="#ffffe0", fg="#000000", relief="solid",
                 borderwidth=1, font=(UI_FONT, 9), padx=4, pady=2).pack()

    def _hide(self, _e=None):
        if self._tw:
            self._tw.destroy()
            self._tw = None


BROWSER_OFF = "Désactivé"   # valeur interne (config) : l'affichage est traduit par _browser_combo


def show_blocked_browsers():
    """Edge, Chrome et Brave figurent-ils dans les listes de navigateurs ? Sous Windows ils chiffrent leurs
    cookies d'une façon que yt-dlp ne lit pas : masqués par défaut ; visibles par défaut ailleurs."""
    cfg = load_config()
    if "show_blocked_browsers" in cfg:
        return bool(cfg["show_blocked_browsers"])
    return sys.platform != "win32"


def visible_browsers(show_blocked, current=""):
    """Navigateurs proposés dans les listes. Le navigateur déjà choisi reste toujours dans la liste, pour qu'un
    réglage existant ne disparaisse pas sans que l'utilisateur l'ait changé. Sous Linux, yt-dlp lit tous les
    navigateurs (Chromium et dérivés via le trousseau de clés du bureau) : aucun n'est masqué."""
    if not IS_WINDOWS:
        extra = [current] if current and current != BROWSER_OFF and current not in _LINUX_BROWSERS else []
        return list(_LINUX_BROWSERS) + extra
    return ["firefox", "opera"] + [b for b in _COOKIE_ENCRYPTED_BROWSERS if show_blocked or b == current]


_BROWSER_COMBOS = []      # (combobox, fonction de mise à jour de ses valeurs)


def refresh_browser_combos():
    """Remet à jour toutes les listes de navigateurs ouvertes (après un changement de l'option)."""
    for entry in list(_BROWSER_COMBOS):
        cb, refresh = entry
        try:
            alive = cb.winfo_exists()
        except tk.TclError:
            alive = False
        if alive:
            refresh()
        else:
            _BROWSER_COMBOS.remove(entry)


def _browser_combo(parent, var):
    """Combobox des navigateurs : `var` garde la valeur interne (BROWSER_OFF ou nom du
    navigateur) tandis que l'affichage de « désactivé » est traduit."""
    off_lbl = t("opts.cookies_disabled")
    disp = tk.StringVar()

    def to_disp(*_):
        disp.set(off_lbl if var.get() in ("", BROWSER_OFF) else var.get())

    def to_var(_e=None):
        v = disp.get()
        var.set(BROWSER_OFF if v == off_lbl else v)

    def values():
        return [off_lbl] + visible_browsers(show_blocked_browsers(), var.get())

    cb = ttk.Combobox(parent, textvariable=disp, state="readonly", width=12, values=values())

    def refresh(*_):
        try:
            cb.configure(values=values())
        except tk.TclError:
            pass

    cb.bind("<<ComboboxSelected>>", to_var)
    var.trace_add("write", lambda *_: (to_disp(), refresh()))
    to_disp()
    _BROWSER_COMBOS.append((cb, refresh))
    return cb


def _cookie_hint(text, browser=""):
    """Explication claire d'une erreur de lecture des cookies (sinon chaîne vide)."""
    low = (text or "").lower()
    name = (browser or "").capitalize()
    if "database is locked" in low or ("could not copy" in low and "cookie" in low):
        running = browser_process_count(browser)
        if running:
            return t("cookie.hint_locked_running" if IS_WINDOWS else "cookie.hint_locked_running_linux",
                     browser=name, n=running)
        return t("cookie.hint_locked", browser=name)
    if "failed to decrypt" in low or "dpapi" in low or ("cannot decrypt" in low and not IS_WINDOWS):
        return t("cookie.hint_decrypt" if IS_WINDOWS else "cookie.hint_decrypt_linux", browser=name)
    if "could not find" in low and "cookies database" in low:
        return t("cookie.hint_notfound", browser=name)
    cookies_on = bool(browser) and browser != BROWSER_OFF
    if "cookies are no longer valid" in low:
        return t("cookie.hint_rotated", browser=name or "")
    if "private video" in low:
        return t("cookie.hint_private", browser=name) if cookies_on else t("cookie.hint_private_off")
    if "confirm your age" in low or "age-restricted" in low:
        return t("cookie.hint_age", browser=name) if cookies_on else t("cookie.hint_age_off")
    if "not a bot" in low:
        return t("cookie.hint_bot")
    return ""


# Résultats d'essais (Windows 11, 2026-10) : ces navigateurs chiffrent leurs cookies d'une façon que
# yt-dlp ne lit pas toujours, même fermés ; Opera n'est lisible que fermé ; Firefox toujours.
_COOKIE_ENCRYPTED_BROWSERS = ("chrome", "edge", "brave")
_COOKIE_CLOSED_BROWSERS = ("opera",)
# Linux : Firefox d'abord, puis les navigateurs Chromium, dont les cookies sont protégés par le trousseau de clés
# du bureau (GNOME Keyring, KWallet) : il doit être déverrouillé, donc une session graphique ouverte.
_LINUX_BROWSERS = ("firefox", "chromium", "chrome", "brave", "edge", "opera", "vivaldi")
_LINUX_KEYRING_BROWSERS = _LINUX_BROWSERS[1:]
_COOKIE_COLORS = {"off": "#e74c3c", "untested": "#f5a623", "testing": "#f5a623",
                  "ok": "#4ec94e", "fail": "#e74c3c"}


class CookieFrame(ttk.LabelFrame):
    """Cadre « Cookies » : navigateur, voyant d'état (●), bouton de test (↻) et avertissement."""

    def __init__(self, parent, var, label_key, warn_key, warn_wrap=210):
        super().__init__(parent, text=t(label_key).rstrip(" :："), padding=6)
        self._var = var
        self.state = "off"
        self.detail = ""
        _browser_combo(self, var).grid(row=0, column=0, sticky="w")
        self.dot = tk.Label(self, text="●", fg=_COOKIE_COLORS["off"], font=(UI_FONT, 13), cursor="hand2")
        self.dot.grid(row=0, column=1, padx=(6, 0))
        self.dot.bind("<Button-1>", lambda _e: self.check())
        self.button = ttk.Button(self, text="↻", width=2, command=self.check)
        self.button.grid(row=0, column=2, padx=(2, 0))
        _Tip(self.button, lambda: t("insp.cookie_tip_refresh"))
        _Tip(self.dot, self._tip_text)
        self.warn = tk.Label(self, text=t(warn_key), justify="left", anchor="w",
                             fg="#e74c3c", font=(UI_FONT, 8), wraplength=warn_wrap)
        self.warn.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.note = tk.Label(self, text="", justify="left", anchor="w",
                             fg="#f5a623", font=(UI_FONT, 8), wraplength=warn_wrap)
        self.note.grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))
        var.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def _note_key(self):
        """Limite connue du navigateur choisi (clé de traduction) ou chaîne vide."""
        browser = self._var.get()
        if not IS_WINDOWS:
            return "cookie.note_keyring" if browser in _LINUX_KEYRING_BROWSERS else ""
        if browser in _COOKIE_ENCRYPTED_BROWSERS:
            return "cookie.note_blocked"
        if browser in _COOKIE_CLOSED_BROWSERS:
            return "cookie.note_closed"
        return ""

    def _tip_text(self):
        text = t(f"insp.cookie_dot_{self.state}")
        if self.state == "fail" and self.detail:
            text += "\n" + self.detail
        return text

    def active(self):
        return self._var.get() not in ("", BROWSER_OFF)

    def refresh(self):
        """Avertissement visible si les cookies sont désactivés ; voyant remis à « non testé »."""
        key = self._note_key()
        if key:
            self.note.configure(text=t(key))
            self.note.grid()
        else:
            self.note.grid_remove()
        if self.active():
            self.warn.grid_remove()
            self.set_state("untested")
        else:
            self.warn.grid()
            self.set_state("off")

    def set_state(self, state):
        self.state = state
        self.dot.configure(fg=_COOKIE_COLORS[state])

    def check(self):
        """Lance un test rapide yt-dlp pour vérifier que les cookies sont lisibles."""
        browser = self._var.get()
        if not browser or browser == BROWSER_OFF:
            self.set_state("off")
            return
        if self.state == "testing":
            return
        self.detail = ""
        self.set_state("testing")

        def _test():
            detail = ""
            try:
                r = subprocess.run(
                    [YTDLP, "--cookies-from-browser", browser, "--simulate", "--no-playlist", "--quiet",
                     "https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                    capture_output=True, timeout=20, **NO_WINDOW)
                ok = r.returncode == 0
                if not ok:
                    text = (r.stderr or b"").decode("utf-8", "replace").strip()
                    lines = text.splitlines()
                    detail = _cookie_hint(text, browser) or (lines[-1][:160] if lines else "")
            except Exception as exc:
                ok, detail = False, av_advice(exc) or str(exc)[:160]

            def _done():
                if self._var.get() != browser:   # le choix a changé pendant le test
                    return
                self.detail = detail
                self.set_state("ok" if ok else "fail")
            try:
                self.after(0, _done)
            except (tk.TclError, RuntimeError):
                pass

        threading.Thread(target=_test, daemon=True).start()


class _FlowFrame(ttk.Frame):
    """Conteneur qui replie ses enfants sur plusieurs lignes selon la largeur disponible
    (placement absolu : chaque ligne a ses propres largeurs, sans colonnes partagées)."""
    GAP_X, GAP_Y = 12, 6

    def __init__(self, parent):
        super().__init__(parent)
        self._items = []   # (widget, pleine_largeur)
        self._sig = None
        self._pending = None
        self.bind("<Configure>", lambda e: self._layout())
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _on_destroy(self, event):
        if event.widget is self and self._pending is not None:
            try:
                self.after_cancel(self._pending)
            except tk.TclError:
                pass
            self._pending = None

    def _schedule(self):
        if self._pending is None:
            self._pending = self.after_idle(self._run_pending)

    def _run_pending(self):
        self._pending = None
        self._layout()

    def add(self, widget, wide=False):
        self._items.append((widget, wide))
        widget.bind("<Configure>", lambda e: self._schedule(), add="+")
        self._schedule()

    def _layout(self):
        avail = self.winfo_width()
        if avail <= 1:
            return
        rows, cur, x = [], [], 0
        for w, wide in self._items:
            if wide:
                if cur:
                    rows.append(cur)
                    cur, x = [], 0
                rows.append([(w, True)])
                continue
            need = w.winfo_reqwidth()
            if cur and x + need > avail:
                rows.append(cur)
                cur, x = [], 0
            cur.append((w, False))
            x += need + self.GAP_X
        if cur:
            rows.append(cur)
        plan, y = [], 0
        for row in rows:
            h = max(w.winfo_reqheight() for w, _ in row)
            x = 0
            for w, wide in row:
                if wide:
                    plan.append((w, 0, y, avail, h))
                else:
                    rw = w.winfo_reqwidth()
                    plan.append((w, x, y, rw, h))
                    x += rw + self.GAP_X
            y += h + self.GAP_Y
        total = max(y - self.GAP_Y, 1)
        sig = (tuple((id(w), x, y0, ww, hh) for w, x, y0, ww, hh in plan), total)
        if sig == self._sig:
            return
        self._sig = sig
        for w, x, y0, ww, hh in plan:
            w.place(x=x, y=y0, width=ww, height=hh)
        self.configure(height=total)


class PlaylistInspectorWindow(tk.Toplevel):

    # Noms d'affichage des codes de langue
    # Couleurs de ligne selon disponibilité des langues choisies
    _BG_OK_EVEN  = "#2d2d2d"
    _BG_OK_ODD   = "#222222"
    _BG_WARN     = "#3a3010"   # langue secondaire/ST manquante
    _BG_ERROR    = "#4a1c1c"   # langue principale manquante

    _closed = False

    def after(self, ms, func=None, *args):
        """Comme Toplevel.after, mais une action planifiée par le thread d'analyse est ignorée si la fenêtre a été
        fermée entre-temps (elle ouvrait sinon une « Erreur interne » par action restante)."""
        if func is None:
            return super().after(ms)

        def guarded(*a):
            if not self._closed:
                return func(*a)
        try:
            return super().after(ms, guarded, *args)
        except (tk.TclError, RuntimeError):      # fenêtre déjà détruite
            return None

    def __init__(self, parent, url="", outdir=""):
        super().__init__(parent)
        self.bind("<Destroy>", lambda e: setattr(self, "_closed", True) if e.widget is self else None)
        self.title(t("insp.window_title"))
        self.geometry("1180x720")
        self.minsize(560, 420)
        self._stop_flag = threading.Event()
        self._rows = []
        self._log_visible = False
        self._dl_window = None   # fenêtre de téléchargement active
        self._build()
        # Charger le dernier navigateur depuis la config partagée
        cfg = load_config()
        parent_browser = getattr(parent, "var_browser", None)
        if parent_browser is not None:
            self.var_g_browser.set(parent_browser.get())
        elif "browser" in cfg:
            self.var_g_browser.set(cfg["browser"])
        self._update_cookie_warn_insp()
        self.protocol("WM_DELETE_WINDOW", self._on_inspector_close)
        if url:
            self.var_url.set(url)
        # dossier : celui que l'inspecteur utilisait la dernière fois, sinon celui de la fenêtre principale
        last = cfg.get("insp_outdir", "")
        if last and os.path.isdir(last):
            self.var_g_outdir.set(last)
        elif outdir:
            self.var_g_outdir.set(outdir)
        self.var_g_outdir.trace_add("write", lambda *_: YtDlpGui.remember("insp_outdir", self.var_g_outdir.get()))
        self.var_g_browser.trace_add("write", lambda *_: YtDlpGui.remember("browser", self.var_g_browser.get()))

    def _on_inspector_close(self):
        self._stop_flag.set()
        cfg = load_config()
        cfg["browser"] = self.var_g_browser.get()
        save_config(cfg)
        parent_browser = getattr(self.master, "var_browser", None)
        if parent_browser is not None:
            parent_browser.set(self.var_g_browser.get())
        self.destroy()

    # ── Journal de debug (fenêtre séparée) ────────────────────────
    def _log(self, msg):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        if hasattr(self, "_log_text") and self._log_text.winfo_exists():
            self._log_text.configure(state="normal")
            self._log_text.insert("end", line)
            self._log_text.see("end")
            self._log_text.configure(state="disabled")

    def _toggle_log(self):
        if hasattr(self, "_log_win") and self._log_win.winfo_exists():
            self._log_win.lift()
            self._log_win.focus_set()
            return
        win = tk.Toplevel(self)
        win.title(t("insp.debug_log_title"))
        win.geometry("780x400")
        win.minsize(400, 200)
        self._log_win = win
        frm = ttk.Frame(win, padding=6)
        frm.pack(fill="both", expand=True)
        txt = tk.Text(frm, font=(MONO_FONT, 9), bg="#1e1e1e", fg="#d4d4d4",
                      wrap="word", relief="flat", state="disabled")
        vsb = ttk.Scrollbar(frm, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)
        self._log_text = txt
        frm_btn = ttk.Frame(win, padding=(6, 0, 6, 6))
        frm_btn.pack(fill="x")
        ttk.Button(frm_btn, text=t("insp.debug_log_btn_clear"),
                   command=lambda: (txt.configure(state="normal"),
                                    txt.delete("1.0", "end"),
                                    txt.configure(state="disabled"))
                   ).pack(side="left", ipadx=6)
        ttk.Button(frm_btn, text=t("insp.debug_log_btn_close"),
                   command=win.destroy).pack(side="right", ipadx=6)
        win.protocol("WM_DELETE_WINDOW", win.destroy)

    # ── Nom d'affichage d'un code langue ──────────────────────────
    def _lang_label(self, code, count=None, total=None):
        name = _t_lang_name(code)
        base = f"{code.upper()} — {name}"
        if count is not None and total is not None:
            return f"{base} ({count}/{total})"
        return base

    # ── Construction UI ────────────────────────────────────────────
    def _build(self):
        # ── URL ───────────────────────────────────────────────────
        frm_top = ttk.Frame(self, padding=(8, 8, 8, 0))
        frm_top.pack(fill="x")
        ttk.Label(frm_top, text=t("insp.label_url")).pack(side="left", padx=(0, 6))
        self.var_url = tk.StringVar()
        ttk.Entry(frm_top, textvariable=self.var_url,
                  font=(UI_FONT, 10)).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frm_top, text=t("insp.btn_paste"),
                   command=lambda: self.var_url.set(self.clipboard_get())).pack(side="left", padx=(0, 4))
        self.btn_analyze = ttk.Button(frm_top, text=t("insp.btn_analyze"),
                                      command=self._analyze)
        self.btn_analyze.pack(side="left")
        self.btn_stop_an = ttk.Button(frm_top, text=t("insp.btn_stop"), command=self._stop_analyze,
                                      state="disabled", width=3)
        self.btn_stop_an.pack(side="left", padx=(4, 0))
        self._btn_log = ttk.Button(frm_top, text=t("insp.btn_log"),
                                   command=self._toggle_log, width=10)
        self._btn_log.pack(side="right")

        # ── Pied : packé en premier pour rester toujours visible ──
        frm_foot = ttk.Frame(self, padding=(8, 4, 8, 8))
        frm_foot.pack(side="bottom", fill="x")
        ttk.Button(frm_foot, text=t("insp.btn_select_all"),
                   command=lambda: self._select_all(True)).pack(side="left", ipadx=6)
        ttk.Button(frm_foot, text=t("insp.btn_deselect_all"),
                   command=lambda: self._select_all(False)).pack(
            side="left", padx=(6, 0), ipadx=6)
        self.var_dl_lbl = tk.StringVar(value=t("insp.btn_download_sel"))
        self.btn_dl = ttk.Button(frm_foot, textvariable=self.var_dl_lbl,
                                 command=self._download_selection, state="disabled")
        self.btn_dl.pack(side="right", ipadx=10, ipady=4)
        self.var_status = tk.StringVar(value=t("insp.status_initial"))
        ttk.Label(self, textvariable=self.var_status, anchor="w",
                  font=(UI_FONT, 9)).pack(side="bottom", fill="x", padx=8, pady=(4, 0))

        # ── Page défilante verticalement (règles + légende + tableau) ──
        frm_page = ttk.Frame(self)
        frm_page.pack(fill="both", expand=True)
        self._page_cv = tk.Canvas(frm_page, highlightthickness=0)
        self._page_vsb = ttk.Scrollbar(frm_page, orient="vertical", command=self._page_cv.yview)
        self._page_cv.configure(yscrollcommand=self._page_vsb.set)
        self._page_cv.pack(side="left", fill="both", expand=True)
        page = ttk.Frame(self._page_cv)
        page_win = self._page_cv.create_window((0, 0), window=page, anchor="nw")
        page_state = {"vsb": False}

        def _fit_page(_e=None):
            cw, ch = self._page_cv.winfo_width(), self._page_cv.winfo_height()
            need = page.winfo_reqheight()
            h = max(ch, need)
            self._page_cv.itemconfigure(page_win, width=cw, height=h)
            self._page_cv.configure(scrollregion=(0, 0, cw, h))
            want_vsb = need > ch + 1
            if want_vsb != page_state["vsb"]:
                page_state["vsb"] = want_vsb
                if want_vsb:
                    self._page_vsb.pack(side="right", fill="y")
                else:
                    self._page_vsb.pack_forget()
                    self._page_cv.yview_moveto(0)

        self._page_cv.bind("<Configure>", _fit_page)
        page.bind("<Configure>", _fit_page)

        # ── Règles globales (reflux automatique selon la largeur) ──
        frm_g_outer = ttk.LabelFrame(page, text=t("insp.rules_frame_label"), padding=8)
        frm_g_outer.pack(fill="x", padx=8, pady=6)
        frm_g = _FlowFrame(frm_g_outer)
        frm_g.pack(fill="x")

        # Qualité
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_quality")).pack(side="left", padx=(0, 4))
        self.var_g_quality = tk.StringVar(value="1080p")
        self._g_quality_combo = ttk.Combobox(
            g, textvariable=self.var_g_quality,
            values=[t("opts.quality_best"), "2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"],
            state="readonly", width=12)
        self._g_quality_combo.pack(side="left")
        frm_g.add(g)

        # Audio seulement
        self.var_g_audio_only = tk.BooleanVar(value=False)

        def _on_audio_only(*_):
            state = "disabled" if self.var_g_audio_only.get() else "readonly"
            self._g_quality_combo.configure(state=state)
        self.var_g_audio_only.trace_add("write", _on_audio_only)
        g = ttk.Frame(frm_g)
        ttk.Checkbutton(g, text=t("insp.chk_audio_only"),
                        variable=self.var_g_audio_only).pack(side="left")
        frm_g.add(g)

        # Format ST
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_sub_fmt")).pack(side="left", padx=(0, 4))
        self.var_g_sub_fmt = tk.StringVar(value="srt")
        ttk.Combobox(g, textvariable=self.var_g_sub_fmt, values=SUBTITLE_FORMATS,
                     state="readonly", width=6).pack(side="left")
        frm_g.add(g)

        # Cases à cocher
        self.var_g_embed_subs = tk.BooleanVar(value=True)
        self.var_g_embed_thumb = tk.BooleanVar(value=True)
        self.var_g_numbering = tk.BooleanVar(value=False)
        g = ttk.Frame(frm_g)
        ttk.Checkbutton(g, text=t("insp.chk_embed_subs"),
                        variable=self.var_g_embed_subs).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(g, text=t("insp.chk_embed_thumb"),
                        variable=self.var_g_embed_thumb).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(g, text=t("insp.chk_numbering"),
                        variable=self.var_g_numbering).pack(side="left")
        frm_g.add(g)

        # Cookies : menu + voyant + bouton test
        self.var_g_browser = tk.StringVar(value=BROWSER_OFF)
        self._cookie_frame = CookieFrame(frm_g, self.var_g_browser, "insp.label_cookies", "insp.cookie_warn")
        self.var_g_browser.trace_add("write", lambda *_: self._on_browser_change())
        frm_g.add(self._cookie_frame)

        # Répertoire intelligent
        frm_smart = ttk.LabelFrame(frm_g, text=t("insp.chk_smart_dir"), padding=6)
        self.var_g_smart_dir = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_smart, text=t("insp.smart_dir_enable"),
                        variable=self.var_g_smart_dir).pack(anchor="w")
        ttk.Button(frm_smart, text=t("insp.btn_registry_tool"),
                   command=self._open_registry_tool).pack(fill="x", pady=(6, 0))
        frm_g.add(frm_smart)

        # Langue principale
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_primary_lang")).pack(side="left", padx=(0, 4))
        _g_opt_default  = t("insp.primary_default")
        _g_opt_no_audio = t("insp.primary_no_audio")
        _g_opt_manual   = t("insp.primary_manual")
        self.var_g_primary_lbl = tk.StringVar(value=_g_opt_default)
        self._g_primary_combo = ttk.Combobox(
            g, textvariable=self.var_g_primary_lbl,
            values=[_g_opt_default, _g_opt_no_audio, _g_opt_manual],
            state="readonly", width=26)
        self._g_primary_combo.pack(side="left")
        frm_g.add(g)
        self._g_primary_map = {_g_opt_default: "", _g_opt_no_audio: "__video_only__",
                               _g_opt_manual: "__manual__"}
        self._g_opt_manual       = _g_opt_manual
        self._g_opt_default      = _g_opt_default
        self._g_opt_no_audio     = _g_opt_no_audio
        self._g_opt_row_default  = t("insp.row_default_global")
        self._g_manual_primary_code = ""   # code choisi manuellement

        def _on_primary_select(evt=None):
            if self.var_g_primary_lbl.get() == self._g_opt_manual:
                self._pick_primary_language()
            self._refresh_colors()

        self._g_primary_combo.bind("<<ComboboxSelected>>", _on_primary_select)
        self.var_g_primary_lbl.trace_add(
            "write", lambda *_: self.after(20, self._refresh_colors))

        # Audio secondaire(s)
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_secondary_audio")).pack(side="left", padx=(0, 4))
        self._g_secondary = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=28,
            on_change=self._refresh_colors)
        self._g_secondary.pack(side="left")
        frm_g.add(g)

        # Sous-titres
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_subs")).pack(side="left", padx=(0, 4))
        self._g_subs = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=26,
            on_change=self._refresh_colors)
        self._g_subs.pack(side="left")
        frm_g.add(g)

        # Blocs de script (+ avertissement miniature MKV)
        g = ttk.Frame(frm_g)
        ttk.Label(g, text=t("insp.label_blocks")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self._g_blocks = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=32,
            tabs=_translated_blocks_tabs())
        self._g_blocks.grid(row=0, column=1, sticky="w")
        self._lbl_mkv_warn = ttk.Label(
            g, text=t("insp.mkv_warn"),
            foreground="#e67e22", font=(UI_FONT, 8), wraplength=360)
        self._lbl_mkv_warn.grid(row=0, column=2, sticky="w", padx=(10, 0))
        self._lbl_mkv_warn.grid_remove()
        frm_g.add(g)

        # Dossier (pleine largeur)
        g = ttk.Frame(frm_g)
        g.columnconfigure(1, weight=1)
        ttk.Label(g, text=t("insp.label_outdir")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.var_g_outdir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Entry(g, textvariable=self.var_g_outdir, width=54).grid(row=0, column=1, sticky="ew")
        ttk.Button(g, text=t("insp.btn_browse"), width=3,
                   command=self._browse_out).grid(row=0, column=2, padx=(4, 0))
        frm_g.add(g, wide=True)

        # Légende couleurs
        frm_legend = ttk.Frame(page)
        frm_legend.pack(fill="x", padx=8, pady=(0, 2))
        for bg, txt in [(self._BG_ERROR, t("insp.legend_primary_missing")),
                        (self._BG_WARN,  t("insp.legend_secondary_missing")),
                        (self._BG_OK_EVEN, t("insp.legend_ok"))]:
            tk.Label(frm_legend, text=f"  {txt}  ", bg=bg, fg="#d4d4d4",
                     font=(UI_FONT, 8), relief="flat").pack(side="left", padx=(0, 6))

        # ── Tableau : en-tête + zone défilante (verticale ET horizontale) ──
        frm_table = ttk.Frame(page)
        frm_table.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        frm_table.columnconfigure(0, weight=1)
        frm_table.rowconfigure(1, weight=1)

        self._head_cv = tk.Canvas(frm_table, bg="#333", highlightthickness=0, height=26)
        self._head_cv.grid(row=0, column=0, sticky="ew")
        frm_head = tk.Frame(self._head_cv, bg="#333")
        head_win = self._head_cv.create_window((0, 0), window=frm_head, anchor="nw")
        for text, w in [("", 3), (t("insp.grid_col_num"), 3), (t("insp.grid_col_title"), 36), (t("insp.grid_col_audio"), 20),
                        (t("insp.grid_col_subs"), 16), (t("insp.grid_col_primary"), 16),
                        (t("insp.grid_col_secondary"), 22), (t("insp.grid_col_subs_override"), 20)]:
            tk.Label(frm_head, text=text, bg="#333", fg="#aaa",
                     font=(UI_FONT, 8, "bold"),
                     width=w, anchor="w").pack(side="left", padx=3, pady=3)

        self._canvas = tk.Canvas(frm_table, bg="#252525", highlightthickness=0, height=240)
        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self._canvas.yview)
        hsb = ttk.Scrollbar(frm_table, orient="horizontal", command=self._canvas.xview)

        def _xscroll(first, last):
            hsb.set(first, last)
            self._head_cv.xview_moveto(first)

        self._canvas.configure(yscrollcommand=vsb.set, xscrollcommand=_xscroll)
        self._canvas.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")
        self._inner = tk.Frame(self._canvas, bg="#252525")
        self._cwin = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        def _fit_table(_e=None):
            cw = self._canvas.winfo_width()
            wid = max(cw, self._inner.winfo_reqwidth(), frm_head.winfo_reqwidth())
            self._canvas.itemconfigure(self._cwin, width=wid)
            self._canvas.configure(scrollregion=(0, 0, wid, self._inner.winfo_reqheight()))
            self._head_cv.itemconfigure(head_win, width=wid)
            self._head_cv.configure(scrollregion=(0, 0, wid, frm_head.winfo_reqheight()),
                                    height=frm_head.winfo_reqheight())

        self._inner.bind("<Configure>", _fit_table)
        frm_head.bind("<Configure>", _fit_table)
        self._canvas.bind("<Configure>", _fit_table)
        self._canvas.bind("<Shift-MouseWheel>",
                          lambda e: self._canvas.xview_scroll(-1 * (e.delta // 120), "units"))
        self._canvas.bind("<Shift-Button-4>", lambda e: self._canvas.xview_scroll(-1, "units"))   # X11
        self._canvas.bind("<Shift-Button-5>", lambda e: self._canvas.xview_scroll(1, "units"))

        # ── Panneau de log (caché par défaut) ─────────────────────
        self._log_frame = ttk.LabelFrame(self, text=" Journal de debug ", padding=4)
        # Pas de pack() ici — _toggle_log le gère
        self._log_text = tk.Text(self._log_frame, height=6, state="disabled",
                                 font=(MONO_FONT, 8), bg="#1e1e1e", fg="#d4d4d4",
                                 wrap="word", relief="flat")
        log_vsb = ttk.Scrollbar(self._log_frame, orient="vertical",
                                command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=log_vsb.set)
        log_vsb.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)

    # ── Popup générique de sélection de langue principale ──────────
    def _open_lang_picker(self, on_confirm):
        """Ouvre un popup de sélection parmi les 50 langues. on_confirm(code, label)."""
        lang_choices = [(code[len("alang_"):], _tblklbl(code, lbl))
                        for code, lbl in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])
                        if code.startswith("alang_")]

        pop = tk.Toplevel(self)
        pop.title(t("insp.lang_picker_title"))
        pop.resizable(False, True)
        pop.minsize(300, 300)
        pop.geometry("340x420")
        pop.transient(self)
        pop.grab_set()

        frm_s = ttk.Frame(pop)
        frm_s.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(frm_s, text="🔍").pack(side="left", padx=(2, 4))
        var_q = tk.StringVar()
        ttk.Entry(frm_s, textvariable=var_q).pack(side="left", fill="x", expand=True)

        lb_frame = ttk.Frame(pop)
        lb_frame.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        lb = tk.Listbox(lb_frame, font=(UI_FONT, 9), activestyle="dotbox",
                        selectmode="single", bg="#252525", fg="#d4d4d4",
                        selectbackground="#264f78", highlightthickness=0)
        vsb = ttk.Scrollbar(lb_frame, command=lb.yview)
        lb.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        lb.pack(fill="both", expand=True)

        def _populate(q=""):
            lb.delete(0, "end")
            for code, lbl in lang_choices:
                if not q or q in lbl.lower() or q in code.lower():
                    lb.insert("end", lbl)

        _populate()
        var_q.trace_add("write", lambda *_: _populate(var_q.get().lower().strip()))

        def _apply():
            sel = lb.curselection()
            if not sel:
                pop.destroy()
                return
            chosen_lbl = lb.get(sel[0])
            chosen_code = next((c for c, l in lang_choices if l == chosen_lbl), "")
            pop.destroy()
            on_confirm(chosen_code, chosen_lbl)

        frm_b = ttk.Frame(pop)
        frm_b.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(frm_b, text=t("insp.lang_picker_btn_select"), command=_apply).pack(side="left", ipadx=8)
        ttk.Button(frm_b, text=t("insp.lang_picker_btn_cancel"), command=pop.destroy).pack(side="left", padx=(6, 0))
        lb.bind("<Double-Button-1>", lambda _: _apply())

    def _pick_primary_language(self):
        """Popup pour la règle globale."""
        def _on_confirm(code, lbl):
            self._g_manual_primary_code = code
            self._g_primary_map[lbl] = code
            self._g_primary_map[self._g_opt_manual] = code
            self.var_g_primary_lbl.set(lbl)
            vals = list(self._g_primary_combo["values"])
            if lbl not in vals:
                vals.insert(1, lbl)
                self._g_primary_combo.configure(values=vals)
            self._refresh_colors()
        self._open_lang_picker(_on_confirm)

    def _pick_primary_lang_manual(self, var, combo, base_opts):
        """Popup pour une ligne per-vidéo."""
        def _on_confirm(code, lbl):
            var.set(lbl)
            vals = list(combo["values"])
            if lbl not in vals:
                vals.insert(1, lbl)
                combo.configure(values=vals)
            self._refresh_colors()
        self._open_lang_picker(_on_confirm)

    # ── Helpers généraux ───────────────────────────────────────────
    def _browse_out(self):
        d = filedialog.askdirectory(initialdir=self.var_g_outdir.get())
        if d:
            self.var_g_outdir.set(d)

    def _select_all(self, state):
        for r in self._rows:
            r["var_en"].set(state)
        self._refresh_dl_btn()

    def _refresh_dl_btn(self):
        n = sum(1 for r in self._rows if r["var_en"].get())
        self.var_dl_lbl.set(t("insp.btn_download_n", n=n) if n else t("insp.btn_download_sel"))
        self.btn_dl.configure(state="normal" if n else "disabled")

    def _clear_rows(self):
        for w in self._inner.winfo_children():
            w.destroy()
        self._rows.clear()

    def _global_primary(self):
        """Retourne le code langue ('' si désactivé, '__video_only__' si sans audio)."""
        code = self._g_primary_map.get(self.var_g_primary_lbl.get(), "")
        return "" if code == "__manual__" else code

    def _global_secondary(self):
        return self._g_secondary.get_selected()

    def _global_subs(self):
        return self._g_subs.get_selected()

    # ── Couleurs de ligne ──────────────────────────────────────────
    @staticmethod
    def _set_bg_recursive(widget, bg):
        try:
            widget.configure(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            PlaylistInspectorWindow._set_bg_recursive(child, bg)

    def _refresh_colors(self, *_):
        g_primary   = self._global_primary()
        g_secondary = set(self._global_secondary())
        g_subs      = set(self._global_subs())

        self._log(f"_refresh_colors | lignes={len(self._rows)} "
                  f"| g_primary='{g_primary}' "
                  f"| g_secondary={sorted(g_secondary)} "
                  f"| g_subs={sorted(g_subs)}")

        for i, row in enumerate(self._rows):
            audio = set(row["vid"].get("audio_langs", []))
            st    = set(row["vid"].get("sub_langs", []))

            # Paramètre effectif = override par ligne si défini, sinon règle globale
            prim_lbl = row["var_primary"].get()
            if prim_lbl == self._g_opt_row_default:
                primary = g_primary
            else:
                primary = prim_lbl.split(" — ")[0].lower() if " — " in prim_lbl else ""

            sec_sel   = row["secondary_widget"].get_selected()
            secondary = set(sec_sel) if sec_sel else g_secondary

            sub_sel = row["subs_widget"].get_selected()
            subs    = set(sub_sel) if sub_sel else g_subs

            if primary and primary not in audio:
                bg = self._BG_ERROR
            elif (secondary and not secondary.issubset(audio)) or \
                 (subs and not subs.issubset(st)):
                bg = self._BG_WARN
            else:
                bg = self._BG_OK_EVEN if i % 2 == 0 else self._BG_OK_ODD

            if row.get("bg") != bg:
                row["bg"] = bg
                self._set_bg_recursive(row["frame"], bg)

        self._inner.update_idletasks()

        # Avertissement miniature MKV
        has_secondary = bool(g_secondary) or any(
            row["secondary_widget"].get_selected() for row in self._rows)
        embed_thumb = self.var_g_embed_thumb.get()
        if IS_WINDOWS and has_secondary and embed_thumb:   # l'avertissement parle de l'Explorateur Windows
            self._lbl_mkv_warn.grid()
        else:
            self._lbl_mkv_warn.grid_remove()

    # ── Analyse ────────────────────────────────────────────────────
    def _analyze(self):
        url = extract_url(self.var_url.get())
        if url != self.var_url.get().strip():
            self.var_url.set(url)
        if not url:
            messagebox.showwarning(t("insp.warn_url_missing_title"), t("insp.warn_url_missing_msg"), parent=self)
            return
        self._clear_rows()
        self._stop_flag.clear()
        self.btn_analyze.configure(state="disabled")
        self.btn_stop_an.configure(state="normal")
        self.btn_dl.configure(state="disabled")
        self.var_status.set(t("insp.status_fetching"))
        threading.Thread(target=self._run_analyze, args=(url,), daemon=True).start()

    def _stop_analyze(self):
        self._stop_flag.set()
        self.btn_stop_an.configure(state="disabled")

    def _run_analyze(self, url):
        try:
            self._run_analyze_impl(url)
        except Exception as e:
            import traceback
            msg = traceback.format_exc()
            self.after(0, lambda m=msg, e=e: self.var_status.set(
                t("insp.status_err_unexpected", error=e)))
            print(msg)
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            self.after(0, lambda: self.btn_stop_an.configure(state="disabled"))

    def _run_analyze_impl(self, url):
        # Étape 1 : liste plate. Les cookies du navigateur choisi servent dès cette étape : sans eux, une vidéo privée
        # qui appartient au compte connecté n'a pas de titre et serait ignorée comme « masquée ».
        browser = self.var_g_browser.get()
        list_cookie_args = ["--cookies-from-browser", browser] if browser != BROWSER_OFF else []
        try:
            result = subprocess.run(
                [YTDLP, "--flat-playlist", "-j", "--no-warnings"] + list_cookie_args + ["--", url],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                **NO_WINDOW,
                timeout=120,
            )
            lines = [l for l in result.stdout.splitlines() if l.strip()]
        except Exception as e:
            self.after(0, lambda e=e: self.var_status.set(t("insp.status_err_list", error=e)))
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            return

        videos = []
        skipped = 0
        for line in lines:
            try:
                info = json.loads(line)
            except Exception:
                continue
            if not isinstance(info, dict):
                continue
            vid_id = info.get("id") or ""
            title = info.get("title") or ""
            # « private » n'est pas retenu ici : une vidéo privée inaccessible n'a pas de titre (ou « [Private video] »),
            # et pour une adresse de vidéo seule, `availability` vaut « private » quand c'est le propriétaire qui la voit.
            hidden = (not vid_id or not title
                      or title.startswith(("[Private video]", "[Deleted video]"))
                      or info.get("availability") in ("premium_only", "subscriber_only"))
            if hidden:
                skipped += 1
                continue
            videos.append({"id": vid_id, "title": title})
        if skipped:
            self.after(0, lambda s=skipped: self._log(
                f"  [liste] {s} élément(s) masqué(s)/privé(s)/supprimé(s) ignoré(s)"))

        if not videos:
            if result.returncode != 0:                        # raison de l'échec (cookies verrouillés, vidéo indisponible…)
                for line in dict.fromkeys(l for l in result.stderr.splitlines() if l.strip()):    # sans les doublons
                    self.after(0, lambda l=line: self._log(f"  [liste] {l}"))
                hint = _cookie_hint(result.stderr, browser)
                if hint:
                    self.after(0, lambda h=hint: self._log(h))
            self.after(0, lambda: self.var_status.set(t("insp.status_no_videos")))
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            return

        n = len(videos)
        # Étape 2 : inspection de chaque vidéo
        for i, vid in enumerate(videos):
            if self._stop_flag.is_set():
                break
            vid["title"] = vid.get("title") or vid.get("id") or "?"
            self.after(0, lambda ix=i, tot=n:
                       self.var_status.set(t("insp.status_inspecting", ix=ix+1, tot=tot)))

            audio_langs, sub_langs, auto_only_subs = set(), set(), set()
            vid_url = f"https://www.youtube.com/watch?v={vid['id']}"

            # Cookies optionnels pour accéder aux pistes doublées
            browser = self.var_g_browser.get()
            cookie_args = ["--cookies-from-browser", browser] \
                          if browser != BROWSER_OFF else []

            # Appel yt-dlp -j avec le client par défaut (yt-dlp choisit ios/tv_embedded)
            try:
                r = subprocess.run(
                    [YTDLP, "-j", "--no-warnings", "--no-playlist"] + cookie_args + ["--", vid_url],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    **NO_WINDOW, timeout=45,
                )
                rc = r.returncode
                if rc != 0:
                    hint = _cookie_hint(r.stderr, browser)
                    if hint:
                        self.after(0, lambda h=hint: (self.var_status.set(h), self._log(h)))
                stdout_len = len(r.stdout.strip())
                self.after(0, lambda t=vid["title"][:25], c=rc, l=stdout_len:
                           self._log(f"  [json] returncode={c} stdout={l}o → '{t}'"))
                if r.returncode == 0 and r.stdout.strip():
                    info = json.loads(r.stdout.strip())
                    all_fmts = info.get("formats", [])
                    audio_fmts = [f for f in all_fmts
                                  if (f.get("acodec") or "none") != "none"]
                    lang_fmts  = [f for f in audio_fmts if f.get("language")]
                    lang_vals  = sorted({f["language"] for f in lang_fmts})
                    # Chercher aussi dans audio_track (nouveau champ yt-dlp)
                    track_fmts = [f for f in all_fmts if f.get("audio_track")]
                    self.after(0, lambda t=vid["title"][:20],
                               na=len(all_fmts), naf=len(audio_fmts),
                               nlf=len(lang_fmts), lv=lang_vals, ntf=len(track_fmts):
                               self._log(f"  [détail] '{t}' "
                                         f"total_fmts={na} "
                                         f"avec_audio={naf} "
                                         f"avec_lang={nlf} "
                                         f"langs={lv} "
                                         f"audio_track={ntf}"))
                    for fmt in all_fmts:
                        # Uniquement le champ 'language' de premier niveau — seules les
                        # pistes réellement accessibles via le sélecteur -f [language=X].
                        # audio_track.lang est exclu : il décrit des pistes potentiellement
                        # derrière auth (Premium/région) non téléchargeables sans cookies.
                        lang = fmt.get("language")
                        if lang and (fmt.get("acodec") or "none") != "none":
                            audio_langs.add(lang.split("-")[0].lower())
                    _known_langs = set(_LANG_NAMES.keys())
                    _manual_subs = set()
                    _auto_subs = set()
                    for lang in info.get("subtitles", {}):
                        base = lang.split("-")[0].lower()
                        if base and base != "und" and 2 <= len(base) <= 4:
                            _manual_subs.add(base)
                    for lang in info.get("automatic_captions", {}):
                        base = lang.split("-")[0].lower()
                        # Filtrer les langues obscures : garder seulement celles dans
                        # notre liste des 50 langues connues, ou qui ont aussi une version manuelle
                        if base and base != "und" and 2 <= len(base) <= 4:
                            if base in _known_langs or base in _manual_subs:
                                _auto_subs.add(base)
                    sub_langs.update(_manual_subs | _auto_subs)
                    auto_only_subs = _auto_subs - _manual_subs
                    audio_langs.discard("und")
            except Exception as exc:
                self.after(0, lambda e=str(exc):
                           self._log(f"  [json] Exception: {e}"))

            # Repli sur -F si moins de 2 langues audio détectées
            if len(audio_langs) <= 1:
                langs_before_F = set(audio_langs)
                try:
                    r2 = subprocess.run(
                        [YTDLP, "-F", "--no-warnings", "--no-playlist"] + cookie_args + ["--", vid_url],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        **NO_WINDOW, timeout=30,
                    )
                    for line in r2.stdout.splitlines():
                        if line.startswith("["):
                            continue
                        if any(x in line for x in ("mhtml", "storyboard", "images",
                                                    "video only")):
                            continue
                        for m in re.findall(r'\[([a-z]{2,4})\]', line):
                            if m != "und":
                                audio_langs.add(m)
                    new_langs = audio_langs - langs_before_F
                    self.after(0, lambda t=vid["title"][:25], n=len(audio_langs),
                               nl=sorted(new_langs):
                               self._log(f"  [-F]  total={n} pistes, ajout={nl} → '{t}'"))
                except Exception as exc:
                    self.after(0, lambda e=str(exc):
                               self._log(f"  [-F]  Exception: {e}"))

            vid_data = dict(vid,
                            audio_langs=sorted(audio_langs),
                            sub_langs=sorted(sub_langs),
                            auto_only_subs=sorted(auto_only_subs))

            a_str = ", ".join(sorted(audio_langs)) or "(aucune)"
            s_str = ", ".join(sorted(sub_langs))[:60] or "(aucune)"
            self.after(0, lambda t=vid["title"][:30], a=a_str, s=s_str:
                       self._log(f"Vidéo '{t}' | audio=[{a}] | subs=[{s}]"))

            # Pause anti-rate-limit aléatoire entre chaque vidéo
            if not self._stop_flag.is_set():
                import random
                time.sleep(random.uniform(2.0, 5.0))

            def _safe_add(v=vid_data, ix=i):
                try:
                    self._add_row(ix + 1, v)
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    self.var_status.set(t("insp.status_err_row", n=ix + 1, error=e))
            self.after(0, _safe_add)

        stopped = self._stop_flag.is_set()
        self.after(0, lambda: self.var_status.set(
            t("insp.status_stopped", n=len(self._rows)) if stopped else
            t("insp.status_done", n=len(self._rows))))
        self.after(0, lambda: self.btn_analyze.configure(state="normal"))
        self.after(0, lambda: self.btn_stop_an.configure(state="disabled"))
        self.after(0, self._update_global_suggestions)

    # ── Mise à jour des suggestions globales après analyse ─────────
    def _update_global_suggestions(self):
        total = len(self._rows)
        if not total:
            return

        audio_cnt, sub_cnt, auto_only_global = {}, {}, set()
        for row in self._rows:
            for l in row["vid"].get("audio_langs", []):
                audio_cnt[l] = audio_cnt.get(l, 0) + 1
            for l in row["vid"].get("sub_langs", []):
                sub_cnt[l] = sub_cnt.get(l, 0) + 1
            auto_only_global.update(row["vid"].get("auto_only_subs", []))

        # Trier par fréquence décroissante
        sorted_audio = sorted(audio_cnt.items(), key=lambda x: (-x[1], x[0]))
        sorted_subs  = sorted(sub_cnt.items(),  key=lambda x: (-x[1], x[0]))

        # Langue principale (Combobox mono-sélection)
        # Options spéciales toujours présentes + langues détectées + choisir manuellement
        primary_labels = ([self._g_opt_default, self._g_opt_no_audio]
                          + [self._lang_label(c, n, total) for c, n in sorted_audio]
                          + [self._g_opt_manual])
        self._g_primary_map = {self._g_opt_default: "", self._g_opt_no_audio: "__video_only__",
                               self._g_opt_manual: "__manual__"}
        self._g_primary_map.update({
            self._lang_label(c, n, total): c for c, n in sorted_audio})
        # Préserver une sélection manuelle précédente si encore valide
        cur = self.var_g_primary_lbl.get()
        if cur not in primary_labels and cur not in self._g_primary_map:
            self.var_g_primary_lbl.set(self._g_opt_default)
        self._g_primary_combo.configure(values=primary_labels)

        # Cookies requis pour les pistes audio secondaires et le bloc Langue
        cookies_ok = self._cookies_active()

        # Audio secondaire (multi-sélection) — verrouillé sans cookies
        self._g_secondary.set_options([
            (c, self._lang_label(c, n, total)) for c, n in sorted_audio])
        self._g_secondary.set_enabled(cookies_ok)
        self._g_secondary.set_placeholder(
            t("opts.placeholder_disabled") if cookies_ok else t("insp.placeholder_cookies_required"))

        # Blocs de script — onglet Langue masqué sans cookies
        self._g_blocks.set_tabs(
            _translated_blocks_tabs(filter_fn=lambda k: k != "Langue" or cookies_ok))

        # Sous-titres (multi-sélection)
        # Les langues auto-only sont masquées si aucun cookie n'est configuré
        self._g_subs.set_options([
            (c, ("[Auto] " if c in auto_only_global else "") + self._lang_label(c, n, total))
            for c, n in sorted_subs
            if c not in auto_only_global or cookies_ok])
        self._g_subs.set_placeholder(
            t("opts.placeholder_disabled") if cookies_ok else
            t("insp.subs_placeholder_no_cookies"))

        # Mettre à jour les widgets par-ligne avec les options disponibles
        for row in self._rows:
            self._update_row_lang_widgets(row)

        self._refresh_colors()

    def _cookies_active(self):
        return self.var_g_browser.get() not in ("", BROWSER_OFF)

    def _update_cookie_warn_insp(self):
        self._cookie_frame.refresh()

    def _set_cookie_state(self, state):
        self._cookie_frame.set_state(state)

    def _check_cookie(self):
        self._cookie_frame.check()

    @property
    def _cookie_state(self):
        return self._cookie_frame.state

    def _on_browser_change(self):
        """Rafraîchit les widgets de langue/audio quand le navigateur (cookie) change."""
        self._update_cookie_warn_insp()
        cookies_ok = self._cookies_active()
        # Verrouillage global toujours mis à jour, même sans lignes analysées
        self._g_secondary.set_enabled(cookies_ok)
        self._g_secondary.set_placeholder(
            t("opts.placeholder_disabled") if cookies_ok else t("insp.placeholder_cookies_required"))
        self._g_blocks.set_tabs(
            _translated_blocks_tabs(filter_fn=lambda k: k != "Langue" or cookies_ok))
        if self._rows:
            self._update_global_suggestions()

    def _sub_label(self, code, auto_only_set):
        base = self._lang_label(code)
        return f"[Auto] {base}" if code in auto_only_set else base

    def _update_row_lang_widgets(self, row):
        """Met à jour les options des widgets de langue d'une ligne selon ses langues détectées."""
        audio = row["vid"].get("audio_langs", [])
        subs  = row["vid"].get("sub_langs", [])
        auto_only = set(row["vid"].get("auto_only_subs", []))
        cookies_ok = self._cookies_active()

        audio_opts = [(c, self._lang_label(c)) for c in audio]
        sub_opts   = [(c, self._sub_label(c, auto_only))
                      for c in subs
                      if c not in auto_only or cookies_ok]

        # Combobox principale
        primary_opts = ([self._g_opt_row_default, self._g_opt_no_audio]
                        + [self._lang_label(c) for c in audio]
                        + [self._g_opt_manual])
        row["primary_combo"].configure(values=primary_opts)
        if row["var_primary"].get() not in primary_opts:
            row["var_primary"].set(primary_opts[0])

        # Multi-sélections — audio secondaire verrouillé sans cookies
        row["secondary_widget"].set_options(audio_opts)
        row["secondary_widget"].set_enabled(cookies_ok)
        row["secondary_widget"].set_placeholder(
            t("insp.placeholder_secondary_default") if cookies_ok else t("insp.placeholder_cookies_required"))
        row["subs_widget"].set_options(sub_opts)

    # ── Ajout d'une ligne ──────────────────────────────────────────
    def _add_row(self, idx, vid):
        row_idx = len(self._rows)
        bg = self._BG_OK_EVEN if row_idx % 2 == 0 else self._BG_OK_ODD
        frm = tk.Frame(self._inner, bg=bg)
        frm.pack(fill="x", pady=1)

        # Checkbox
        var_en = tk.BooleanVar(value=True)
        var_en.trace_add("write", lambda *_: self._refresh_dl_btn())
        tk.Checkbutton(frm, variable=var_en, bg=bg, activebackground=bg,
                       fg="#d4d4d4", selectcolor="#444").pack(side="left", padx=(6, 0))

        # Numéro
        tk.Label(frm, text=str(idx), width=3, anchor="e", bg=bg,
                 fg="#888", font=(MONO_FONT, 9)).pack(side="left", padx=3)

        # Titre (tronqué)
        title = vid["title"]
        disp = (title[:38] + "…") if len(title) > 38 else title
        tk.Label(frm, text=disp, width=38, anchor="w", bg=bg,
                 fg="#d4d4d4", font=(UI_FONT, 9)).pack(side="left", padx=4)

        # Audio dispo (résumé)
        audio_str = " ".join(l.upper() for l in vid["audio_langs"][:8]) or "?"
        tk.Label(frm, text=audio_str, width=20, anchor="w", bg=bg,
                 fg="#9cdcfe", font=(MONO_FONT, 8)).pack(side="left", padx=2)

        # ST dispo (résumé)
        _ao = set(vid.get("auto_only_subs", []))
        sub_str = " ".join(
            f"[{l.upper()}]" if l in _ao else l.upper()
            for l in vid["sub_langs"][:8]
        ) or "—"
        tk.Label(frm, text=sub_str, width=16, anchor="w", bg=bg,
                 fg="#ce9178", font=(MONO_FONT, 8)).pack(side="left", padx=2)

        # ── Override : langue principale ──
        var_primary = tk.StringVar(value=self._g_opt_row_default)
        audio_opts = ([self._g_opt_row_default, self._g_opt_no_audio]
                      + [self._lang_label(c) for c in vid["audio_langs"]]
                      + [self._g_opt_manual])
        primary_combo = ttk.Combobox(frm, textvariable=var_primary,
                                     values=audio_opts, state="readonly", width=16)
        primary_combo.pack(side="left", padx=4)

        def _on_primary_row(evt, _combo=primary_combo, _var=var_primary):
            if _var.get() == self._g_opt_manual:
                self._pick_primary_lang_manual(_var, _combo, audio_opts)
            else:
                self._refresh_colors()

        primary_combo.bind("<<ComboboxSelected>>", _on_primary_row)

        # ── Override : audio secondaire (multi) ──
        secondary_widget = MultiCheckSelect(frm, placeholder=self._g_opt_row_default, width=22,
                                            on_change=self._refresh_colors)
        secondary_widget.set_options([(c, self._lang_label(c)) for c in vid["audio_langs"]])
        secondary_widget.pack(side="left", padx=4)

        # ── Override : sous-titres (multi) ──
        subs_widget = MultiCheckSelect(frm, placeholder=self._g_opt_row_default, width=20,
                                       on_change=self._refresh_colors)
        auto_only = set(vid.get("auto_only_subs", []))
        cookies_ok = self._cookies_active()
        subs_widget.set_options([
            (c, self._sub_label(c, auto_only))
            for c in vid["sub_langs"]
            if c not in auto_only or cookies_ok])
        subs_widget.pack(side="left", padx=4)

        row_data = {
            "vid": vid, "var_en": var_en, "frame": frm, "bg": bg,
            "var_primary": var_primary, "primary_combo": primary_combo,
            "secondary_widget": secondary_widget, "subs_widget": subs_widget,
        }
        self._rows.append(row_data)
        self._refresh_dl_btn()

    # ── Construction des args yt-dlp par vidéo ─────────────────────
    def _build_video_args(self, row, secondary_override=None, skip_subs=False, subs_only=False):
        """
        secondary_override : liste de codes langue ['fr','it',...] ou None.
        Utilisé par le système de sondage/relance lors des échecs de format.
        """
        vid = row["vid"]
        vid_url = f"https://www.youtube.com/watch?v={vid['id']}"

        # ── Mode subs-only : commande dédiée au téléchargement des sous-titres ──
        if subs_only:
            g_subs = list(self._global_subs())
            v_subs = row["subs_widget"].get_selected()
            seen_s = set(g_subs)
            subs = list(g_subs)
            for s in v_subs:
                if s not in seen_s:
                    subs.append(s)
                    seen_s.add(s)
            if not subs:
                return []   # Rien à faire → pas de commande
            auto_only = set(row["vid"].get("auto_only_subs", []))
            has_auto = any(s in auto_only for s in subs)
            args = [YTDLP,
                    "--skip-download",          # ne re-télécharge pas la vidéo
                    "--sub-lang", ",".join(subs),
                    "--sub-format", self.var_g_sub_fmt.get()]
            if self.var_g_embed_subs.get():
                args += EMBED_SUBS_ARGS
            else:
                args += ["--write-subs"]
            if has_auto:
                args += ["--write-auto-subs", "--sleep-requests", "4"]
            args += ["--retries", "10", "--fragment-retries", "10",
                     "--sleep-interval", "3", "--max-sleep-interval", "8"]
            browser = self.var_g_browser.get()
            if browser != BROWSER_OFF:
                args += ["--cookies-from-browser", browser]
            out = self.var_g_outdir.get().strip()
            if row.get("_out_template"):
                args += ["-o", row["_out_template"]]
            elif out:
                args += ["-o", os.path.join(_tmpl_esc(out), "%(title)s.%(ext)s")]
            args += ["--no-playlist", "--", vid_url]
            return args

        # ── Langues audio de la bibliothèque de blocs (onglet Langue) ──
        block_audio_langs = [
            SCRIPT_BLOCKS_MAP[code][1]
            for code in self._g_blocks.get_selected()
            if SCRIPT_BLOCKS_MAP.get(code, [""])[0] == "_alang_"
        ]

        force_mp4 = False  # sera recalculé en mode vidéo si applicable

        # ── Mode audio seulement ────────────────────────────────────
        if self.var_g_audio_only.get():
            prim_lbl = self.var_g_primary_lbl.get()
            primary_audio = self._g_primary_map.get(prim_lbl, "")
            if primary_audio in ("__video_only__", "__manual__"):
                primary_audio = ""

            # Secondaires : union global + per-vidéo
            g_sec = list(self._global_secondary())
            v_sec = row["secondary_widget"].get_selected()
            seen_sec = set(g_sec)
            secondary_audio = list(g_sec)
            for lang in (list(v_sec) + block_audio_langs):
                if lang not in seen_sec:
                    secondary_audio.append(lang)
                    seen_sec.add(lang)

            if secondary_audio:
                # Plusieurs pistes → MKV multi-stream
                prim_fmt = (f"bestaudio[language^={primary_audio}]"
                            if primary_audio else "bestaudio")
                sec_str = "+".join(f"bestaudio[language^={l}]" for l in secondary_audio)
                fmt = f"{prim_fmt}+{sec_str}/{prim_fmt}/bestaudio/best"
                args = [YTDLP, "-f", fmt,
                        *MULTI_AUDIO_ARGS]
            else:
                # Piste unique → MP3
                if primary_audio:
                    fmt = f"bestaudio[language^={primary_audio}]/bestaudio/best"
                else:
                    fmt = "bestaudio/best"
                args = [YTDLP, "-f", fmt,
                        "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
            primary, secondary = primary_audio, secondary_audio
            embed_thumb = self.var_g_embed_thumb.get()
        else:
            # ── Construction du format selon les langues ────────────
            prim_lbl = row["var_primary"].get()
            if prim_lbl == self._g_opt_row_default:
                primary = self._global_primary()
            elif prim_lbl == self._g_opt_no_audio:
                primary = "__video_only__"
            elif prim_lbl == self._g_opt_manual:
                primary = self._global_primary()
            else:
                # L'étiquette est "XX — Nom" ou parfois juste "XX" (saisie manuelle)
                primary = prim_lbl.split(" — ")[0].strip().lower()

            if secondary_override is not None:
                secondary = secondary_override
            else:
                # Union : global + per-vidéo (sans doublons, ordre : global d'abord)
                g_sec = list(self._global_secondary())
                v_sec = row["secondary_widget"].get_selected()
                seen = set(g_sec)
                secondary = list(g_sec)
                for lang in (list(v_sec) + block_audio_langs):
                    if lang not in seen:
                        secondary.append(lang)
                        seen.add(lang)

            quality = self.var_g_quality.get()
            h = {"2160p (4K)": 2160, "1440p": 1440, "1080p": 1080, "720p": 720,
                 "480p": 480, "360p": 360, "240p": 240, "144p": 144}.get(quality)
            hf = f"[height<={h}]" if h else ""

            embed_thumb = self.var_g_embed_thumb.get()
            embed_subs  = self.var_g_embed_subs.get()
            vsel = f"bestvideo{hf}"
            vsel_h264 = f"bestvideo[vcodec^=avc1]{hf}" if embed_thumb else None
            # Forcer mp4 quand : miniature + pas de secondaires + pas de langue spécifique
            # (les pistes doublées sont Opus → incompatibles avec le conteneur mp4)
            # Les ST sont convertis mov_text automatiquement par ffmpeg dans le mp4
            force_mp4 = (embed_thumb and not secondary and not primary)

            if primary == "__video_only__":
                # Piste vidéo seule, sans audio
                fmt = f"{vsel_h264}/{vsel}" if vsel_h264 else vsel
            elif primary and secondary:
                sec_str = "+".join(f"bestaudio[language^={s}]" for s in secondary)
                if vsel_h264:
                    fmt = (f"{vsel_h264}+bestaudio[language^={primary}]+{sec_str}"
                           f"/{vsel}+bestaudio[language^={primary}]+{sec_str}"
                           f"/{vsel_h264}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = (f"{vsel}+bestaudio[language^={primary}]+{sec_str}"
                           f"/{vsel}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio/best")
            elif primary:
                if vsel_h264:
                    # Préférer m4a pour la piste doublée → H.264+m4a = MP4 viable
                    fmt = (f"{vsel_h264}+bestaudio[language^={primary}][ext=m4a]"
                           f"/{vsel_h264}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = (f"{vsel}+bestaudio[language^={primary}]"
                           f"/{vsel}+bestaudio/best")
            elif secondary:
                # primary vide = piste par défaut (bestaudio) + secondaires explicites
                sec_str = "+".join(f"bestaudio[language^={s}]" for s in secondary)
                if vsel_h264:
                    fmt = (f"{vsel_h264}+bestaudio+{sec_str}"
                           f"/{vsel_h264}+bestaudio"
                           f"/{vsel}+bestaudio+{sec_str}"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = f"{vsel}+bestaudio+{sec_str}/{vsel}+bestaudio/best"
            else:
                if force_mp4:
                    # H.264 (mp4) + AAC (m4a) → merge propre en .mp4
                    # Fallback best[ext=mp4] = format pré-mergé YouTube (H.264+AAC)
                    # évite bestaudio Opus qui force yt-dlp à passer en MKV
                    fmt = (f"{vsel_h264}[ext=mp4]+bestaudio[ext=m4a]"
                           f"/{vsel_h264}+bestaudio[ext=m4a]"
                           f"/best[ext=mp4]/best")
                elif vsel_h264:
                    fmt = f"{vsel_h264}+bestaudio/{vsel}+bestaudio/best"
                else:
                    fmt = f"{vsel}+bestaudio/best"

            args = [YTDLP, "-f", fmt]

            if secondary:
                args += MULTI_AUDIO_ARGS
            elif force_mp4:
                args += ["--merge-output-format", "mp4"]
            elif embed_thumb and primary and not secondary:
                # m4a préféré dans le sélecteur → H.264+m4a → MP4 ; MKV si m4a indisponible
                args += ["--merge-output-format", "mp4/mkv"]

        # ── Options communes ────────────────────────────────────────
        if self.var_g_embed_thumb.get():
            args += ["--embed-thumbnail", "--convert-thumbnails", "jpg"]

        # Union : subs global + per-vidéo
        if skip_subs:
            subs = []
        else:
            g_subs = list(self._global_subs())
            v_subs = row["subs_widget"].get_selected()
            seen_subs = set(g_subs)
            subs = list(g_subs)
            for s in v_subs:
                if s not in seen_subs:
                    subs.append(s)
                    seen_subs.add(s)
        if subs:
            auto_only = set(row["vid"].get("auto_only_subs", []))
            has_auto = any(s in auto_only for s in subs)
            args += ["--sub-lang", ",".join(subs), "--sub-format", self.var_g_sub_fmt.get()]
            if self.var_g_embed_subs.get():
                args += EMBED_SUBS_ARGS
                if has_auto:
                    args += ["--write-auto-subs"]
                if not secondary and not force_mp4 and not (embed_thumb and primary):
                    args += ["--merge-output-format", "mkv"]
            else:
                args += ["--write-subs"]
                if has_auto:
                    args += ["--write-auto-subs"]

        args += ["--retries", "10", "--fragment-retries", "10",
                 "--sleep-interval", "3", "--max-sleep-interval", "8",
                 "--no-playlist"]
        browser = self.var_g_browser.get()
        if browser != BROWSER_OFF:
            args += ["--cookies-from-browser", browser]

        # Blocs de script de la bibliothèque globale
        # Les blocs "_alang_" sont des pistes audio — traitement séparé ci-dessous
        for code in self._g_blocks.get_selected():
            block_args = SCRIPT_BLOCKS_MAP.get(code, [])
            if block_args and block_args[0] != "_alang_":
                args += block_args

        outdir = self.var_g_outdir.get().strip()
        prefix = ""
        if self.var_g_numbering.get():
            try:
                num = self._rows.index(row) + 1
            except ValueError:
                num = 0
            prefix = f"{num:02d} - " if num > 0 else ""

        vid_title = row["vid"].get("title", "")
        base_title = f"{prefix}{vid_title}" if vid_title else ""
        unique_path = YtDlpGui._unique_output_path(outdir, base_title) if outdir and base_title else None

        if unique_path:
            out_template = unique_path
        elif outdir:
            out_template = os.path.join(_tmpl_esc(outdir), f"{prefix}%(title)s.%(ext)s")
        elif prefix:
            out_template = f"{prefix}%(title)s.%(ext)s"
        else:
            out_template = None
        if out_template:
            args += ["-o", out_template]
        # Mémorisé pour la passe « sous-titres seuls » : les .srt doivent porter exactement le nom de la
        # vidéo (préfixe de numérotation, suffixe _2, _3…), qui n'est plus calculable une fois la vidéo écrite.
        row["_out_template"] = out_template

        if self.var_g_smart_dir.get() and outdir:
            args += ["--download-archive", os.path.join(outdir, ARCHIVE_NAME),
                     "--print-to-file",
                     "after_move:%(id)s\t%(title)s\t%(duration)s\t%(filepath)s",
                     os.path.join(outdir, TITLES_NAME)]

        args += ["--progress", "--newline", "--", vid_url]
        return args

    # ── Outil « Mettre à jour le registre » ────────────────────────
    def _open_registry_tool(self):
        outdir = self.var_g_outdir.get().strip()
        if not (outdir and os.path.isdir(outdir)):
            messagebox.showwarning(t("insp.registry_title"), t("insp.registry_empty_dir"), parent=self)
            return
        dlg = tk.Toplevel(self)
        dlg.title(t("insp.registry_title"))
        dlg.geometry("780x500")
        dlg.transient(self)
        state = {"closed": False, "missing": [], "props": []}
        var_summary = tk.StringVar()
        var_info = tk.StringVar()
        ttk.Label(dlg, textvariable=var_summary, justify="left").pack(
            anchor="w", padx=10, pady=(10, 4))
        btns = ttk.Frame(dlg)
        btns.pack(side="bottom", fill="x", padx=10, pady=10)
        ttk.Label(dlg, textvariable=var_info, foreground="gray").pack(anchor="w", padx=10)
        body = ttk.Frame(dlg)
        body.pack(fill="both", expand=True, padx=10, pady=(4, 0))
        canvas = tk.Canvas(body, highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        inner_win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(inner_win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btn_search = ttk.Button(btns, text=t("insp.registry_btn_search"))
        btn_apply = ttk.Button(btns, text=t("insp.registry_btn_apply"), state="disabled")
        btn_search.pack(side="left")
        btn_apply.pack(side="left", padx=(8, 0))
        ttk.Button(btns, text=t("insp.registry_btn_close"), command=dlg.destroy).pack(side="right")

        def _clear():
            for w in inner.winfo_children():
                w.destroy()

        def _refresh():
            _clear()
            reg, media, missing, incomplete = _scan_registry_folder(outdir)
            state["missing"] = missing
            var_summary.set(t("insp.registry_summary", media=len(media), reg=len(reg),
                              incomplete=incomplete, missing=len(missing)))
            if missing:
                for fn in missing:
                    ttk.Label(inner, text=fn).pack(anchor="w")
            else:
                ttk.Label(inner, text=t("insp.registry_all_ok"), foreground="gray").pack(anchor="w")
            btn_search.configure(state="normal" if missing else "disabled")
            btn_apply.configure(state="disabled")

        def _open_local(fn):
            try:
                open_path(os.path.join(outdir, fn))
            except OSError as e:
                var_info.set(str(e))

        def _open_web(vid_id):
            import webbrowser
            webbrowser.open(_watch_url(vid_id))

        def _show_proposals(props):
            if state["closed"]:
                return
            _clear()
            state["props"] = []
            tag_txt = {"sure": t("insp.registry_tag_sure"), "title": t("insp.registry_tag_title"),
                       "check": t("insp.registry_tag_check"), "none": t("insp.registry_none")}
            for i, (fn, cand, tag) in enumerate(props):
                v = tk.BooleanVar(value=tag in ("sure", "title"))
                state["props"].append((fn, cand, v))
                ttk.Checkbutton(inner, text=fn, variable=v,
                                state="normal" if cand else "disabled").grid(
                    row=i * 2, column=0, sticky="w", pady=(4, 0))
                if cand:
                    dur = cand.get("duration")
                    d_txt = f" · {int(dur) // 60}:{int(dur) % 60:02d}" if dur else ""
                    line = f"→ {cand['title']}{d_txt}  ·  {tag_txt[tag]}"
                    frm_b = ttk.Frame(inner)
                    frm_b.grid(row=i * 2, column=1, rowspan=2, sticky="e", padx=(8, 4))
                    ttk.Button(frm_b, text=t("insp.registry_btn_open_file"),
                               command=lambda f=fn: _open_local(f)).pack(side="left")
                    ttk.Button(frm_b, text=t("insp.registry_btn_open_web"),
                               command=lambda c=cand: _open_web(c["id"])).pack(
                        side="left", padx=(4, 0))
                else:
                    line = tag_txt["none"]
                ttk.Label(inner, text=line, foreground="gray", wraplength=430,
                          justify="left").grid(
                    row=i * 2 + 1, column=0, sticky="w", padx=(24, 0))
            var_info.set("")
            btn_apply.configure(state="normal")

        def _search():
            btn_search.configure(state="disabled")
            missing = list(state["missing"])

            def _progress(k):
                if not state["closed"]:
                    var_info.set(t("insp.registry_progress", i=k, n=len(missing)))

            def _worker():
                props = []
                for i, fn in enumerate(missing):
                    if state["closed"]:
                        return
                    ldur = _local_duration(os.path.join(outdir, fn))
                    cand, tag = _search_video(_clean_stem(fn), ldur)
                    props.append((fn, cand, tag))
                    self.after(0, lambda k=i + 1: _progress(k))
                    time.sleep(1.0)
                self.after(0, lambda: _show_proposals(props))

            threading.Thread(target=_worker, daemon=True).start()

        def _apply():
            entries = [(c["id"], c["title"], fn, c.get("duration"))
                       for fn, c, v in state["props"] if c and v.get()]
            if entries:
                try:
                    _register_in_archive(outdir, entries)
                except OSError as e:
                    var_info.set(str(e))
                    return
            _refresh()
            var_info.set(t("insp.registry_applied", n=len(entries)))

        def _on_destroy(e):
            if e.widget is dlg:
                state["closed"] = True

        btn_search.configure(command=_search)
        btn_apply.configure(command=_apply)
        dlg.bind("<Destroy>", _on_destroy)
        _refresh()

    # ── Rétroaction « Répertoire intelligent » ─────────────────────
    def _reconcile_smart_dir(self, selected):
        """Détecte les vidéos déjà présentes dans le dossier mais absentes du registre,
        laisse l'utilisateur confirmer, puis les inscrit au registre et les décoche.
        Retourne les lignes à télécharger ([] = rien à faire / abandon)."""
        outdir = self.var_g_outdir.get().strip()
        if not (self.var_g_smart_dir.get() and outdir and os.path.isdir(outdir)):
            return selected
        matches = _find_existing_matches(selected, outdir)
        if not matches:
            return selected
        chosen = self._ask_reconcile(matches)
        if chosen is None:
            return []
        if chosen:
            try:
                _register_in_archive(outdir, [(r["vid"]["id"], r["vid"]["title"], fn)
                                              for r, fn, _src in chosen])
            except OSError as e:
                self.var_status.set(t("insp.status_err_registry", error=e))
                return []
            for r, _fn, _src in chosen:
                r["var_en"].set(False)
            self.var_status.set(t("insp.reconcile_status_skipped", n=len(chosen)))
        return [r for r in selected if r["var_en"].get()]

    def _ask_reconcile(self, matches):
        """Fenêtre de confirmation. Retourne les correspondances cochées,
        [] pour « télécharger quand même », None si la fenêtre est fermée."""
        dlg = tk.Toplevel(self)
        dlg.title(t("insp.reconcile_title"))
        dlg.geometry("760x440")
        dlg.transient(self)
        result = {"chosen": None}
        ttk.Label(dlg, text=t("insp.reconcile_intro", n=len(matches)),
                  wraplength=720, justify="left").pack(anchor="w", padx=10, pady=(10, 6))

        btns = ttk.Frame(dlg)
        btns.pack(side="bottom", fill="x", padx=10, pady=10)
        body = ttk.Frame(dlg)
        body.pack(fill="both", expand=True, padx=10)
        canvas = tk.Canvas(body, highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        src_title = t("insp.reconcile_src_title")
        vars_ = []
        for i, (row, fn, _src) in enumerate(matches):
            v = tk.BooleanVar(value=True)
            vars_.append(v)
            ttk.Checkbutton(inner, text=row["vid"]["title"], variable=v).grid(
                row=i * 2, column=0, sticky="w", pady=(4, 0))
            ttk.Label(inner, text=f"{fn}  ·  {src_title}", foreground="gray").grid(
                row=i * 2 + 1, column=0, sticky="w", padx=(24, 0))

        def _skip():
            result["chosen"] = [m for m, v in zip(matches, vars_) if v.get()]
            dlg.destroy()

        def _ignore():
            result["chosen"] = []
            dlg.destroy()

        ttk.Button(btns, text=t("insp.reconcile_btn_skip"), command=_skip).pack(side="left")
        ttk.Button(btns, text=t("insp.reconcile_btn_ignore"), command=_ignore).pack(side="right")
        dlg.grab_set()
        self.wait_window(dlg)
        return result["chosen"]

    # ── Lancement du téléchargement ────────────────────────────────
    def _download_selection(self):
        # Bloquer si une fenêtre de téléchargement est déjà ouverte
        if self._dl_window is not None and self._dl_window.winfo_exists():
            self._dl_window.lift()
            self._dl_window.focus_force()
            return
        selected = [r for r in self._rows if r["var_en"].get()]
        if not selected:
            return
        selected = self._reconcile_smart_dir(selected)
        if not selected:
            return
        self.btn_dl.configure(state="disabled")
        win = DownloadQueueWindow(self, selected, self._build_video_args, inspector=self)
        self._dl_window = win

        def _on_dl_closed(event=None):
            if event is not None and event.widget is not win:
                return
            self._dl_window = None
            out_now = self.var_g_outdir.get().strip()
            if self.var_g_smart_dir.get() and out_now and os.path.isdir(out_now):
                try:
                    _sync_registry(out_now)
                except OSError:
                    pass
            try:
                self.btn_dl.configure(
                    state="normal" if any(r["var_en"].get() for r in self._rows) else "disabled")
            except tk.TclError:
                pass

        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())
        win.bind("<Destroy>", _on_dl_closed)
        win.start()


# ══════════════════════════════════════════════════════════════════
#  Fenêtre principale
# ══════════════════════════════════════════════════════════════════
_SAFE_CONFIG_KEYS = ("lang", "quality", "audio_only", "sub_fmt", "embed_subs", "embed_thumb", "browser")


def _redact(text, private=()):
    """Masque les dossiers personnels, le nom d'utilisateur et les adresses e-mail."""
    for p in sorted({x for x in private if x and len(x) > 3}, key=len, reverse=True):
        for variant in {p, p.replace("\\", "/"), p.replace("/", "\\")}:
            text = text.replace(variant, "<folder>")
    home = os.path.expanduser("~")
    if home and len(home) > 3:
        for variant in {home, home.replace("\\", "/")}:
            text = text.replace(variant, "~")
    try:
        user = getpass.getuser()
    except Exception:
        user = ""
    if user and len(user) >= 3:
        text = re.sub(re.escape(user), "<user>", text, flags=re.I)
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "<email>", text)


def _ytdlp_version():
    try:
        r = subprocess.run([YTDLP, "--version"], capture_output=True, text=True, timeout=8,
                           **NO_WINDOW)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "not found"


def collect_diagnostics(log_tail="", last_error="", private=()):
    """Texte technique joint à un rapport de bogue : aucune donnée personnelle (masquage inclus)."""
    cfg = load_config()
    lines = [
        f"GUI version: {__version__}",
        f"Python: {platform.python_version()}",
        f"OS: {platform.platform()}",
        f"yt-dlp: {_ytdlp_version()}",
        f"ffmpeg: {'found' if shutil.which('ffmpeg') else 'missing'}",
        f"ffprobe: {'found' if shutil.which('ffprobe') else 'missing'}",
        f"UI language: {_CURRENT_LANG}",
    ]
    settings = [f"{k}={cfg[k]}" for k in _SAFE_CONFIG_KEYS if k in cfg]
    if settings:
        lines.append("Settings: " + ", ".join(settings))
    if last_error.strip():
        lines += ["", "--- Last internal error ---", last_error.strip()]
    if log_tail.strip():
        lines += ["", "--- Log (last lines) ---", log_tail.strip()]
    return _redact("\n".join(lines), private)


def _issue_url(title, description, report, limit=6500):
    """URL de nouveau ticket GitHub préremplie. Retourne (url, tronqué)."""
    def build(rep):
        body = f"## Description\n{description or '-'}\n\n## Report\n```\n{rep}\n```\n"
        return f"{REPO_URL}/issues/new?title={quote(title, safe='')}&body={quote(body, safe='')}"
    url, truncated = build(report), False
    while len(url) > limit and len(report) > 200:
        report = report[:int(len(report) * 0.8)].rstrip() + "\n[truncated]"
        url, truncated = build(report), True
    return url, truncated


class BugReportWindow(tk.Toplevel):
    """Rapport de bogue : rien n'est envoyé automatiquement, l'utilisateur relit puis ouvre GitHub."""
    def __init__(self, parent, report):
        super().__init__(parent)
        self.title(t("bug.window_title"))
        self.geometry("640x640")
        self.minsize(520, 480)
        self.transient(parent)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=t("bug.intro"), wraplength=580, justify="left").pack(anchor="w")
        ttk.Label(frm, text=t("bug.label_summary")).pack(anchor="w", pady=(10, 2))
        self.var_summary = tk.StringVar()
        ttk.Entry(frm, textvariable=self.var_summary).pack(fill="x")
        ttk.Label(frm, text=t("bug.label_description")).pack(anchor="w", pady=(10, 2))
        self.txt_desc = tk.Text(frm, height=6, wrap="word", font=(UI_FONT, 10))
        self.txt_desc.pack(fill="x")

        ttk.Label(frm, text=t("bug.label_report")).pack(anchor="w", pady=(10, 2))
        frm_btn = ttk.Frame(frm)
        frm_btn.pack(side="bottom", fill="x", pady=(10, 0))
        self.var_info = tk.StringVar()
        ttk.Label(frm, textvariable=self.var_info, foreground="gray",
                  wraplength=580, justify="left").pack(side="bottom", anchor="w")
        frm_rep = ttk.Frame(frm)
        frm_rep.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(frm_rep, orient="vertical")
        self.txt_report = tk.Text(frm_rep, wrap="word", font=(MONO_FONT, 9), yscrollcommand=sb.set)
        sb.configure(command=self.txt_report.yview)
        sb.pack(side="right", fill="y")
        self.txt_report.pack(side="left", fill="both", expand=True)
        self.txt_report.insert("1.0", report)

        ttk.Button(frm_btn, text=t("bug.btn_open"), command=self._open).pack(side="left", ipadx=6)
        ttk.Button(frm_btn, text=t("bug.btn_copy"), command=self._copy).pack(side="left", padx=(6, 0), ipadx=6)
        ttk.Button(frm_btn, text=t("bug.btn_close"), command=self.destroy).pack(side="right", ipadx=6)

    def _full_text(self):
        desc = self.txt_desc.get("1.0", "end").strip()
        report = self.txt_report.get("1.0", "end").strip()
        return f"## Description\n{desc or '-'}\n\n## Report\n```\n{report}\n```\n"

    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self._full_text())
        self.var_info.set(t("bug.copied"))

    def _open(self):
        summary = self.var_summary.get().strip()
        if not summary:
            messagebox.showwarning(t("bug.window_title"), t("bug.warn_summary"), parent=self)
            return
        url, truncated = _issue_url(summary, self.txt_desc.get("1.0", "end").strip(),
                                    self.txt_report.get("1.0", "end").strip())
        if truncated:
            self._copy()
            self.var_info.set(t("bug.truncated"))
        webbrowser.open(url)


# ══════════════════════════════════════════════════════════════════
#  Assistant d'installation (yt-dlp + ffmpeg), téléchargements vérifiés
# ══════════════════════════════════════════════════════════════════
def _release_assets(system, machine):
    """Fichiers officiels à télécharger selon le système (« windows » ou « linux ») et l'architecture :
    binaire yt-dlp de ses versions GitHub, archives ffmpeg et Deno (None si le projet n'en publie pas pour
    cette architecture : l'outil vient alors du gestionnaire de paquets du système), suffixe des exécutables."""
    machine = (machine or "").lower()
    if system == "windows":
        return {"ytdlp": "yt-dlp.exe", "ffmpeg": "ffmpeg-master-latest-win64-gpl.zip",
                "deno": "deno-x86_64-pc-windows-msvc.zip", "exe": ".exe"}
    if machine in ("x86_64", "amd64"):
        return {"ytdlp": "yt-dlp_linux", "ffmpeg": "ffmpeg-master-latest-linux64-gpl.tar.xz",
                "deno": "deno-x86_64-unknown-linux-gnu.zip", "exe": ""}
    if machine in ("aarch64", "arm64"):
        return {"ytdlp": "yt-dlp_linux_aarch64", "ffmpeg": "ffmpeg-master-latest-linuxarm64-gpl.tar.xz",
                "deno": "deno-aarch64-unknown-linux-gnu.zip", "exe": ""}
    # Autre architecture : yt-dlp en script (il demande python3 sur le système), ni ffmpeg ni Deno à télécharger.
    return {"ytdlp": "yt-dlp", "ffmpeg": None, "deno": None, "exe": ""}


_ASSETS = _release_assets("windows" if IS_WINDOWS else "linux", platform.machine())
EXE_SUFFIX          = _ASSETS["exe"]
YTDLP_ASSET         = _ASSETS["ytdlp"]
YTDLP_URL           = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/" + YTDLP_ASSET
YTDLP_SUMS_URL      = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-256SUMS"
FFMPEG_ARCHIVE_NAME = _ASSETS["ffmpeg"]
FFMPEG_URL          = ("https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/" + FFMPEG_ARCHIVE_NAME
                       if FFMPEG_ARCHIVE_NAME else None)
FFMPEG_SUMS_URL     = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/checksums.sha256"
DENO_ARCHIVE_NAME   = _ASSETS["deno"]
DENO_URL            = ("https://github.com/denoland/deno/releases/latest/download/" + DENO_ARCHIVE_NAME
                       if DENO_ARCHIVE_NAME else None)
DENO_SUMS_URL       = DENO_URL + ".sha256sum" if DENO_URL else None


class SetupError(Exception):
    pass


def _open_url(url, timeout=30, headers=None):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": f"yt-dlp-GUI/{__version__}", **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def _fetch_text(url, timeout=30, opener=_open_url):
    with opener(url, timeout) as r:
        return r.read().decode("utf-8", "replace")


def _download_file(url, dest, progress=None, stop=None, timeout=30, opener=_open_url):
    """Télécharge url vers dest via un fichier .part ; rien ne reste en cas d'échec ou d'annulation."""
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    tmp = dest + ".part"
    try:
        with opener(url, timeout) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            done = 0
            while True:
                if stop is not None and stop.is_set():
                    raise SetupError(t("setup.err_cancelled"))
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
        _replace_with_retry(tmp, dest)
    except BaseException as exc:
        close = getattr(exc, "close", None)   # HTTPError garde un fichier ouvert
        if close:
            close()
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    return dest


def _sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_checksums(text):
    """Fichier de sommes « hash  nom » (ou « hash *nom ») -> {nom: hash}."""
    out = {}
    for line in text.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            out[parts[1].lstrip("*").strip()] = parts[0].lower()
    # Format publié par Deno (Get-FileHash en liste) : « Hash : <sha256> » puis « Path : <chemin> »
    for m in re.finditer(r"Hash\s*:\s*([0-9A-Fa-f]{64})\s+Path\s*:\s*(\S.*)", text):
        out[re.split(r"[\\/]", m.group(2).strip())[-1]] = m.group(1).lower()
    return out


def _verified_download(url, sums_url, name, dest, progress=None, stop=None, log=None):
    """Télécharge puis vérifie le SHA-256 publié ; supprime le fichier si la somme ne correspond pas."""
    expected = _parse_checksums(_fetch_text(sums_url)).get(name)
    if not expected:
        raise SetupError(t("setup.err_no_checksum", name=name))
    if log:
        log(t("setup.log_downloading", name=name))
    _download_file(url, dest, progress, stop)
    if log:
        log(t("setup.log_verifying", name=name))
    if _sha256_file(dest) != expected:
        os.remove(dest)
        raise SetupError(t("setup.err_checksum", name=name))
    return dest


def _tool_names(*names):
    """Noms de fichiers des outils pour ce système (« ffmpeg » -> « ffmpeg.exe » sous Windows)."""
    return tuple(n + EXE_SUFFIX for n in names)


def _archive_files(path):
    """(nom de fichier en minuscules, fonction d'ouverture) de chaque fichier ordinaire d'une archive .zip ou
    .tar.xz. Les chemins de l'archive sont ignorés ; liens, dossiers et fichiers spéciaux ne sont pas listés."""
    import posixpath
    if path.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    yield posixpath.basename(info.filename.replace("\\", "/")).lower(), lambda i=info: zf.open(i)
    else:
        import tarfile
        with tarfile.open(path, "r:*") as tf:
            for member in tf:
                if member.isfile():
                    yield posixpath.basename(member.name).lower(), lambda mb=member: tf.extractfile(mb)


def _extract_tools(archive_path, dest_dir, names=None):
    """Extrait d'une archive .zip ou .tar.xz uniquement les outils demandés (ffmpeg/ffprobe par défaut),
    par nom de fichier, jamais par chemin de l'archive. Hors Windows, ils reçoivent le droit d'exécution."""
    names = names or _tool_names("ffmpeg", "ffprobe")
    os.makedirs(dest_dir, exist_ok=True)
    done = []
    for base, opener in _archive_files(archive_path):
        if base not in names or base in done:
            continue
        target = os.path.join(dest_dir, base)
        with opener() as src, open(target + ".new", "wb") as dst:
            shutil.copyfileobj(src, dst)
        if not IS_WINDOWS:
            os.chmod(target + ".new", 0o755)
        _replace_with_retry(target + ".new", target)
        done.append(base)
        if len(done) == len(names):
            break   # inutile de lire le reste d'une archive de plusieurs centaines de Mo
    if not done:
        raise SetupError(t("setup.err_no_tools_found", tools=", ".join(names)))
    return done


def install_ytdlp(progress=None, stop=None, log=None):
    tmp = YTDLP + ".new"
    _verified_download(YTDLP_URL, YTDLP_SUMS_URL, YTDLP_ASSET, tmp, progress, stop, log)
    if not IS_WINDOWS:
        os.chmod(tmp, 0o755)
    if os.path.exists(YTDLP):
        shutil.copy2(YTDLP, YTDLP + ".bak")
    _replace_with_retry(tmp, YTDLP)


def _require_download(name, url):
    if not url:
        raise SetupError(t("setup.err_unsupported", name=name, system=f"{platform.system()} {platform.machine()}"))


def install_ffmpeg(progress=None, stop=None, log=None):
    import tempfile
    _require_download("ffmpeg", FFMPEG_URL)
    work = tempfile.mkdtemp(prefix="ytgui-ffmpeg-")
    try:
        archive = os.path.join(work, FFMPEG_ARCHIVE_NAME)
        _verified_download(FFMPEG_URL, FFMPEG_SUMS_URL, FFMPEG_ARCHIVE_NAME, archive, progress, stop, log)
        _extract_tools(archive, LOCAL_BIN)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def install_deno(progress=None, stop=None, log=None):
    """Deno : moteur JavaScript que yt-dlp utilise pour YouTube, installé dans le dossier de données."""
    import tempfile
    _require_download("deno", DENO_URL)
    work = tempfile.mkdtemp(prefix="ytgui-deno-")
    try:
        archive = os.path.join(work, DENO_ARCHIVE_NAME)
        _verified_download(DENO_URL, DENO_SUMS_URL, DENO_ARCHIVE_NAME, archive, progress, stop, log)
        _extract_tools(archive, LOCAL_BIN, names=_tool_names("deno"))
    finally:
        shutil.rmtree(work, ignore_errors=True)


class SetupWizardWindow(tk.Toplevel):
    """Télécharge et installe yt-dlp, ffmpeg et Deno depuis leurs dépôts officiels."""
    def __init__(self, parent, on_done=None):
        super().__init__(parent)
        self.title(t("setup.window_title"))
        self.resizable(False, False)
        self.transient(parent)
        self._on_done = on_done
        self._stop = threading.Event()
        self._busy = False

        frm = ttk.Frame(self, padding=14)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=t("setup.intro"), wraplength=520, justify="left").pack(anchor="w")

        frm_items = ttk.Frame(frm)
        frm_items.pack(fill="x", pady=(12, 4))
        self._items = {}
        for key, label, installed, downloadable in (
                ("ytdlp", t("setup.item_ytdlp"), os.path.isfile(YTDLP), True),
                ("ffmpeg", t("setup.item_ffmpeg"), dep_installed("ffmpeg") and dep_installed("ffprobe"),
                 bool(FFMPEG_URL)),
                ("deno", t("setup.item_deno"), dep_installed("deno"), bool(DENO_URL))):
            todo = not installed and downloadable   # pas de téléchargement officiel pour cette architecture
            var = tk.BooleanVar(value=todo)
            row = ttk.Frame(frm_items)
            row.pack(fill="x", pady=2)
            cb = ttk.Checkbutton(row, text=label, variable=var,
                                 state="normal" if todo else "disabled")
            cb.pack(side="left")
            if installed:
                status, color = t("setup.status_ok"), "#27ae60"
            elif not downloadable:
                status, color = t("setup.status_unavailable"), "#7f8c8d"
            else:
                status, color = t("setup.status_missing"), "#c0392b"
            ttk.Label(row, text=status, foreground=color).pack(side="right")
            self._items[key] = var

        self.var_progress = tk.DoubleVar(value=0)
        ttk.Progressbar(frm, variable=self.var_progress, maximum=100).pack(fill="x", pady=(10, 2))
        self.var_info = tk.StringVar()
        ttk.Label(frm, textvariable=self.var_info, foreground="gray").pack(anchor="w")
        self.txt = tk.Text(frm, height=7, width=64, font=(MONO_FONT, 9), state="disabled",
                           bg="#1e1e1e", fg="#d4d4d4")
        self.txt.pack(fill="x", pady=(6, 0))

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(10, 0))
        self.btn_install = ttk.Button(btns, text=t("setup.btn_install"), command=self._install)
        self.btn_install.pack(side="left", ipadx=8)
        self.btn_close = ttk.Button(btns, text=t("setup.btn_later"), command=self._close)
        self.btn_close.pack(side="right", ipadx=8)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _ui(self, fn):
        try:
            self.after(0, fn)
        except (tk.TclError, RuntimeError):
            pass

    def _log(self, text):
        try:
            self.txt.configure(state="normal")
            self.txt.insert("end", text + "\n")
            self.txt.see("end")
            self.txt.configure(state="disabled")
        except tk.TclError:
            pass

    def _set_progress(self, done, total):
        if total:
            self.var_progress.set(done * 100 / total)
            self.var_info.set(t("setup.progress", done=f"{done / 1048576:.0f}", total=f"{total / 1048576:.0f}"))

    def _install(self):
        todo = [k for k, v in self._items.items() if v.get()]
        if not todo or self._busy:
            if not todo:
                self._log(t("setup.nothing_selected"))
            return
        self._busy = True
        self.btn_install.configure(state="disabled")
        self.btn_close.configure(text=t("setup.btn_cancel"))
        threading.Thread(target=self._run, args=(todo,), daemon=True).start()

    def _run(self, todo):
        names = {"ytdlp": ("yt-dlp", install_ytdlp), "ffmpeg": ("ffmpeg", install_ffmpeg),
                 "deno": ("deno", install_deno)}
        ok = True
        for key in todo:
            label, fn = names[key]
            try:
                fn(progress=lambda d, tot: self._ui(lambda: self._set_progress(d, tot)),
                   stop=self._stop, log=lambda msg: self._ui(lambda: self._log(msg)))
                self._ui(lambda n=label: self._log(t("setup.log_installed", name=n)))
            except Exception as exc:
                ok = False
                self._ui(lambda e=exc: self._log(t("setup.log_error", error=describe_network_error(e) or e)))
                advice = av_advice(exc)
                if advice:
                    self._ui(lambda a=advice: self._log(a))
                break
        self._ui(lambda: self._finished(ok))

    def _finished(self, ok):
        self._busy = False
        self.btn_close.configure(text=t("setup.btn_close"))
        if ok:
            self.var_progress.set(100)
            self._log(t("setup.log_all_done"))
        else:
            self.btn_install.configure(state="normal")
        if self._on_done:
            self._on_done()

    def _close(self):
        self._stop.set()
        self.destroy()


# ══════════════════════════════════════════════════════════════════
#  Notification de mise à jour du logiciel (dernière release GitHub)
# ══════════════════════════════════════════════════════════════════
RELEASES_API_URL = "https://api.github.com/repos/harlockSuites/YT-dlp-GUI/releases/latest"   # Windows : la dernière
# Linux : les versions Linux sont des préversions GitHub (étiquette « Linux-vX.Y.Z ») : « latest » les ignore et reste
# la version Windows, que cette liste ne doit jamais proposer. On liste donc les releases et on filtre l'étiquette.
RELEASES_LIST_URL = "https://api.github.com/repos/harlockSuites/YT-dlp-GUI/releases?per_page=30"
LINUX_TAG_PREFIX = "Linux-v"
UPDATE_CHECK_INTERVAL = 24 * 3600
def linux_arch_name(machine=None):
    """Nom d'architecture des fichiers Linux de la release (« x86_64 » ou « aarch64 »), ou None si le projet
    n'en publie pas pour cette architecture."""
    machine = (machine if machine is not None else platform.machine()).lower()
    return {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}.get(machine)


def release_asset_patterns(windows, machine=None):
    """Motifs des fichiers à proposer selon le type d'installation. Windows : installateur et version portable ;
    Linux : AppImage et archive .tar.gz, pour l'architecture de cette machine."""
    if windows:
        return {"installer": "yt-dlp-gui-setup-*.exe", "portable": "yt-dlp-gui-portable-*.zip"}
    arch = linux_arch_name(machine)
    if not arch:
        return {}
    return {"appimage": f"yt-dlp-gui-*-{arch}.AppImage", "portable": f"yt-dlp-gui-linux-*-{arch}.tar.gz"}


_ASSET_PATTERNS = release_asset_patterns(IS_WINDOWS)


def describe_network_error(exc):
    """Message clair pour une erreur réseau (pas de connexion, délai dépassé, serveur injoignable), ou None si
    `exc` n'en est pas une. L'explication technique de Windows suit entre parenthèses."""
    import socket
    import ssl
    reason = getattr(exc, "reason", exc)
    detail = str(reason)
    if isinstance(reason, socket.gaierror) or "getaddrinfo" in detail:
        return t("net.offline", detail=detail)
    if isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in detail.lower():
        return t("net.timeout", detail=detail)
    if isinstance(reason, (ConnectionError, ssl.SSLError)):
        return t("net.unreachable", detail=detail)
    return None


class UpdateError(Exception):
    def __init__(self, message, not_found=False):
        super().__init__(message)
        self.not_found = not_found


def _parse_version(text):
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", (text or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def _is_newer(latest, current):
    a, b = _parse_version(latest), _parse_version(current)
    return a is not None and b is not None and a > b


def _is_github_url(url):
    from urllib.parse import urlparse
    u = urlparse(url or "")
    host = (u.hostname or "").lower()
    return u.scheme == "https" and (host == "github.com" or host.endswith(".github.com")
                                    or host.endswith(".githubusercontent.com"))


def _install_kind(frozen=None, executable=None, env=None):
    """« source », « portable », « installer » (Windows) ou « appimage » (Linux) : détermine quel fichier proposer."""
    frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    if not frozen:
        return "source"
    if not IS_WINDOWS and (os.environ if env is None else env).get("APPIMAGE"):
        return "appimage"   # lancé depuis un AppImage : le chemin de l'exécutable est dans son montage temporaire
    if not IS_WINDOWS:
        return "portable"   # archive .tar.gz extraite : il n'y a pas d'installateur sous Linux
    exe_dir = os.path.dirname(os.path.abspath(executable or sys.executable))
    return "portable" if os.path.isfile(os.path.join(exe_dir, "portable.flag")) else "installer"


def should_check_updates(cfg, now):
    return bool(cfg.get("update_check", True)) and now - float(cfg.get("update_last_check", 0) or 0) >= UPDATE_CHECK_INTERVAL


def pick_asset(info, kind):
    import fnmatch
    pattern = _ASSET_PATTERNS.get(kind)
    if not pattern:
        return None
    return next((a for a in info["assets"] if fnmatch.fnmatch(a["name"], pattern)), None)


def select_linux_release(releases):
    """La plus récente des releases dont l'étiquette est exactement « Linux-vX.Y.Z » (préversions comprises, brouillons
    exclus), ou None. Les étiquettes de la version Windows (« vX.Y.Z ») ne sont jamais retenues."""
    best = None
    for rel in releases if isinstance(releases, list) else []:
        if not isinstance(rel, dict) or rel.get("draft"):
            continue
        tag = rel.get("tag_name") or ""
        rest = tag[len(LINUX_TAG_PREFIX):] if tag.startswith(LINUX_TAG_PREFIX) else ""
        if not re.fullmatch(r"\d+\.\d+\.\d+", rest):
            continue
        version = _parse_version(rest)
        if best is None or version > best[0]:
            best = (version, rel)
    return best[1] if best else None


def fetch_latest_release(opener=_open_url):
    """Dernière release publiée sur GitHub (sous Linux : la dernière « Linux-vX.Y.Z »), ou UpdateError. Seuls les
    liens github.com sont conservés."""
    import urllib.error
    try:
        with opener(RELEASES_API_URL if IS_WINDOWS else RELEASES_LIST_URL, 15,
                    {"Accept": "application/vnd.github+json"}) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        e.close()
        if e.code == 404:
            raise UpdateError(t("app_update.error_not_found"), not_found=True)
        raise UpdateError(f"HTTP {e.code}")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise UpdateError(describe_network_error(e) or str(getattr(e, "reason", e)))
    if IS_WINDOWS:
        version = (data.get("tag_name") or "").lstrip("v")
    else:
        data = select_linux_release(data)
        if data is None:
            raise UpdateError(t("app_update.error_not_found"), not_found=True)
        version = data["tag_name"][len(LINUX_TAG_PREFIX):]
    if _parse_version(version) is None:
        raise UpdateError(t("app_update.error_bad_release"))
    page = data.get("html_url") or ""
    assets = [{"name": a.get("name", ""), "url": a.get("browser_download_url", ""), "size": a.get("size", 0)}
              for a in data.get("assets", []) if _is_github_url(a.get("browser_download_url"))]
    return {"version": version, "tag": data.get("tag_name"), "name": data.get("name") or "",
            "notes": data.get("body") or "", "url": page if _is_github_url(page) else REPO_URL + "/releases",
            "assets": assets}


def check_for_update(current=None, opener=_open_url):
    """Retourne les informations de la release si elle est plus récente que `current`, sinon None."""
    info = fetch_latest_release(opener)
    return info if _is_newer(info["version"], current or __version__) else None


class AppUpdateWindow(tk.Toplevel):
    """Recherche de mise à jour du logiciel : informe et ouvre le navigateur, n'installe rien tout seul."""
    def __init__(self, parent, info=None):
        super().__init__(parent)
        self.title(t("app_update.window_title"))
        self.geometry("560x430")
        self.minsize(460, 340)
        self.transient(parent)
        self._parent = parent
        self._info = None
        self._closed = False
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=t("app_update.current", version=__version__)).pack(anchor="w")
        self.var_status = tk.StringVar(value=t("app_update.checking"))
        self.lbl_status = ttk.Label(frm, textvariable=self.var_status, font=(UI_FONT, 10, "bold"))
        self.lbl_status.pack(anchor="w", pady=(6, 4))
        self.lbl_hint = ttk.Label(frm, text="", foreground="gray", wraplength=520, justify="left")
        self.lbl_hint.pack(anchor="w")
        frm.bind("<Configure>", self._wrap_messages)

        frm_notes = ttk.LabelFrame(frm, text=t("app_update.notes"), padding=6)
        frm_notes.pack(fill="both", expand=True, pady=(8, 6))
        sb = ttk.Scrollbar(frm_notes, orient="vertical")
        self.txt = tk.Text(frm_notes, wrap="word", height=8, state="disabled", font=(UI_FONT, 9),
                           yscrollcommand=sb.set)
        sb.configure(command=self.txt.yview)
        sb.pack(side="right", fill="y")
        self.txt.pack(side="left", fill="both", expand=True)

        cfg = load_config()
        self.var_auto = tk.BooleanVar(value=bool(cfg.get("update_check", True)))
        self.var_auto.trace_add("write", self._save_auto)
        ttk.Checkbutton(frm, text=t("app_update.chk_auto"), variable=self.var_auto).pack(anchor="w")

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(8, 0))
        self.btn_page = ttk.Button(btns, text=t("app_update.btn_page"), command=self._open_page, state="disabled")
        self.btn_dl = ttk.Button(btns, text=t("app_update.btn_download"), command=self._download, state="disabled")
        self.btn_ignore = ttk.Button(btns, text=t("app_update.btn_ignore"), command=self._ignore, state="disabled")
        self.btn_page.pack(side="left")
        self.btn_dl.pack(side="left", padx=(6, 0))
        self.btn_ignore.pack(side="left", padx=(6, 0))
        ttk.Button(btns, text=t("app_update.btn_close"), command=self.destroy).pack(side="right")
        self.bind("<Destroy>", lambda e: setattr(self, "_closed", True) if e.widget is self else None)

        if info is not None:
            self._show(info, None)
        else:
            threading.Thread(target=self._work, daemon=True).start()

    def _wrap_messages(self, event):
        """Les messages d'état (une erreur réseau est longue) passent à la ligne au lieu de déborder."""
        width = max(200, event.width - 30)
        self.lbl_status.configure(wraplength=width, justify="left")
        self.lbl_hint.configure(wraplength=width)

    def _work(self):
        try:
            info, err = check_for_update(), None
        except UpdateError as e:
            info, err = None, e
        except Exception as e:
            info, err = None, UpdateError(str(e))
        try:
            self.after(0, lambda: self._show(info, err))
        except (tk.TclError, RuntimeError):
            pass

    def _show(self, info, err):
        if self._closed:
            return
        self._info = info
        if err is not None:
            self.var_status.set(t("app_update.error", error=err))
            return
        self._parent._record_update_check(info)
        if info is None:
            self.var_status.set(t("app_update.up_to_date", version=__version__))
            return
        self.var_status.set(t("app_update.available", version=info["version"]))
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", info["notes"].strip() or info["name"] or info["tag"])
        self.txt.configure(state="disabled")
        self.btn_page.configure(state="normal")
        self.btn_ignore.configure(state="normal")
        if _install_kind() == "source":
            self.lbl_hint.configure(text=t("app_update.hint_source"))
        elif pick_asset(info, _install_kind()):
            self.btn_dl.configure(state="normal")

    def _save_auto(self, *_):
        cfg = load_config()
        cfg["update_check"] = bool(self.var_auto.get())
        save_config(cfg)

    def _open_page(self):
        if self._info and _is_github_url(self._info["url"]):
            webbrowser.open(self._info["url"])

    def _download(self):
        asset = pick_asset(self._info, _install_kind()) if self._info else None
        if asset and _is_github_url(asset["url"]):
            webbrowser.open(asset["url"])

    def _ignore(self):
        if not self._info:
            return
        cfg = load_config()
        cfg["update_ignored"] = self._info["version"]
        save_config(cfg)
        self.btn_ignore.configure(state="disabled")
        self._parent._record_update_check(self._info)


class DonateWindow(tk.Toplevel):
    """Fenêtre de remerciement avec logo, bannière et lien vers le don."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("donate.window_title"))
        self.transient(parent)
        self.resizable(False, False)
        self._images = []   # références : sinon Tk libère les images

        frm_head = ttk.Frame(self, padding=(16, 14, 16, 4))
        frm_head.pack()
        for name in ("logo.png", "banner.png"):
            try:
                img = tk.PhotoImage(file=os.path.join(ASSETS_DIR, name))
            except tk.TclError:
                continue
            self._images.append(img)
            ttk.Label(frm_head, image=img).pack(side="left", padx=(0, 12) if name == "logo.png" else 0)

        ttk.Label(self, text=t("donate.text"), justify="left", wraplength=500,
                  font=(UI_FONT, 10)).pack(padx=24, pady=(10, 14), anchor="w")

        ttk.Button(self, text=t("donate.btn_kofi"),
                   command=lambda: __import__("webbrowser").open(DONATE_URL)
                   ).pack(pady=(0, 18), ipadx=14, ipady=5)


class YtDlpGui(tk.Tk):
    AUTO_SETUP = True   # ouvre l'assistant au démarrage si yt-dlp.exe est absent
    AUTO_UPDATE_CHECK = True   # vérifie en arrière-plan la présence d'une nouvelle version

    def __init__(self):
        # Hors Windows, la classe de fenêtre (WM_CLASS) relie la fenêtre à son lanceur « yt-dlp-gui.desktop »
        super().__init__(**({} if IS_WINDOWS else {"className": "yt-dlp-gui"}))
        use_system_fonts()
        try:
            if IS_WINDOWS:
                self.iconbitmap(default=ICON_FILE)   # icône de toutes les fenêtres
            else:
                self._icon = tk.PhotoImage(file=ICON_PNG)   # référence gardée : sinon Tk libère l'image
                self.iconphoto(True, self._icon)
        except tk.TclError:
            pass
        self.title(f"{t('app.window_title')}  v{__version__}")
        self.resizable(True, True)
        self.minsize(560, 420)
        self._process = None
        self._paused = False
        self._queue_running = False
        self._queue_index = -1
        self._queue_end_index = -1
        self._queue_skip = False
        self._cookie_hint_shown = False
        self._config = load_config()
        self._queue = load_queue()
        self._build_ui()
        self._restore_config()
        self._apply_initial_geometry()
        install_wheel_scrolling(self)
        cleanup_command_files()
        if self.AUTO_SETUP:
            self.after(400, self._maybe_first_run)
        if self.AUTO_UPDATE_CHECK:
            self.after(3000, self._maybe_check_updates)
        self._refresh_queue_tv()
        # Résoudre les titres manquants des entrées chargées depuis le disque
        for i, e in enumerate(self._queue):
            if not e.get("title") and e.get("status") == "pending":
                threading.Thread(target=self._queue_fetch_title, args=(i,), daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Rend visibles les exceptions silencieuses dans les callbacks tkinter
        self.report_callback_exception = self._on_tk_error

    def _apply_initial_geometry(self):
        """Taille de départ : celle de la dernière session, sinon 980 x 930, ramenée à l'écran."""
        m_size = re.fullmatch(r"(\d{3,4})x(\d{3,4})", str(load_config().get("window_size", "")))
        w, h = (int(m_size[1]), int(m_size[2])) if m_size else (980, 930)
        w = max(560, min(w, self.winfo_screenwidth() - 40))
        h = max(420, min(h, self.winfo_screenheight() - 100))
        self.geometry(f"{w}x{h}")

    def _on_tk_error(self, exc, val, tb):
        import traceback
        msg = "".join(traceback.format_exception(exc, val, tb))
        print(msg)  # console si lancé en python (pas pythonw)
        self._last_error = msg
        if is_antivirus_block(val):
            messagebox.showwarning(t("av.title"), av_advice(val), parent=self)
            return
        if messagebox.askyesno(
                t("app.error_internal_title"),
                t("app.error_internal_msg", exc_name=exc.__name__, val=val)
                + "\n\n" + t("bug.ask_report"), parent=self):
            self._open_bug_report()

    def _open_bug_report(self):
        try:
            log_tail = "\n".join(self.log_text.get("1.0", "end").splitlines()[-60:])
        except tk.TclError:
            log_tail = ""
        private = [self.var_outdir.get().strip(), DATA_DIR, RESOURCE_DIR, os.getcwd()]
        report = collect_diagnostics(log_tail, getattr(self, "_last_error", ""), private)
        BugReportWindow(self, report)

    # ──────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=10, pady=5)

        # ── Page défilante verticalement (tout sauf progression/état) ──
        frm_page = ttk.Frame(self)
        self._page_cv = tk.Canvas(frm_page, highlightthickness=0)
        self._page_vsb = ttk.Scrollbar(frm_page, orient="vertical", command=self._page_cv.yview)
        self._page_cv.configure(yscrollcommand=self._page_vsb.set)
        self._page_cv.pack(side="left", fill="both", expand=True)
        page = ttk.Frame(self._page_cv)
        page_win = self._page_cv.create_window((0, 0), window=page, anchor="nw")
        page_state = {"vsb": False}

        def _fit_page(_e=None):
            cw, ch = self._page_cv.winfo_width(), self._page_cv.winfo_height()
            need = page.winfo_reqheight()
            h = max(ch, need)
            self._page_cv.itemconfigure(page_win, width=cw, height=h)
            self._page_cv.configure(scrollregion=(0, 0, cw, h))
            want_vsb = need > ch + 1
            if want_vsb != page_state["vsb"]:
                page_state["vsb"] = want_vsb
                if want_vsb:
                    self._page_vsb.pack(side="right", fill="y")
                else:
                    self._page_vsb.pack_forget()
                    self._page_cv.yview_moveto(0)

        self._fit_page = _fit_page
        self._page_cv.bind("<Configure>", _fit_page)
        page.bind("<Configure>", _fit_page)

        # ── Barre d'outils (haut) ──────────────────
        frm_toolbar = ttk.Frame(page)
        frm_toolbar.pack(fill="x", padx=10, pady=(8, 0))

        # Indicateur de dépendances manquantes
        self.var_dep_warn = tk.StringVar()
        self._lbl_dep_warn = ttk.Label(
            frm_toolbar, textvariable=self.var_dep_warn,
            foreground="#e67e22", font=(UI_FONT, 9)
        )
        self._lbl_dep_warn.pack(side="left")
        self._update_info = None
        self._frm_toolbar = frm_toolbar
        self._frm_update = ttk.Frame(page)   # ligne affichée sous la barre d'outils quand une version est disponible
        self._lbl_update = tk.Label(self._frm_update, text="", fg="#2980b9", cursor="hand2",
                                    font=(UI_FONT, 9, "underline"), justify="left", wraplength=700)
        self._lbl_update.pack(anchor="w")
        self._lbl_update.bind("<Button-1>", lambda _e: self._open_app_update())

        ttk.Button(
            frm_toolbar, text=t("toolbar.btn_donate"),
            command=lambda: DonateWindow(self)
        ).pack(side="right")
        ttk.Button(
            frm_toolbar, text=t("toolbar.btn_options"),
            command=self._open_options_menu
        ).pack(side="right", padx=(0, 6))
        ttk.Button(
            frm_toolbar, text=t("toolbar.btn_bug"),
            command=self._open_bug_report
        ).pack(side="right", padx=(0, 6))

        self._check_deps_quick()

        # ── URL ────────────────────────────────────
        frm_url = ttk.LabelFrame(page, text=t("url.frame_label"), padding=8)
        frm_url.pack(fill="x", **pad)
        self._frm_url = frm_url

        self.var_url = tk.StringVar()
        ent_url = ttk.Entry(frm_url, textvariable=self.var_url, font=(UI_FONT, 10))
        ent_url.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frm_url, text=t("url.btn_paste"), command=self._paste_url).pack(side="left")
        ttk.Button(frm_url, text=t("url.btn_inspect"), command=self._inspect).pack(side="left", padx=(4, 0))
        ttk.Button(frm_url, text=t("url.btn_playlist_advanced"),
                   command=self._open_playlist_inspector).pack(side="left", padx=(4, 0))

        # Résultat de l'analyse (titre, durée, chaîne, langues), sous le champ URL ; masqué si l'URL change
        self._inspect_box_url = None
        self._lbl_inspect = tk.Label(page, text="", justify="left", anchor="w", wraplength=760,
                                     font=(UI_FONT, 9))
        self.var_url.trace_add("write", lambda *_: self._on_url_changed_for_box())

        # ── Dossier de destination ──────────────────
        frm_out = ttk.LabelFrame(page, text=t("opts.outdir_frame_label"), padding=8)
        frm_out.pack(fill="x", **pad)

        self.var_outdir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ent_out = ttk.Entry(frm_out, textvariable=self.var_outdir, font=(UI_FONT, 10))
        ent_out.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frm_out, text=t("opts.outdir_browse"), command=self._browse_dir).pack(side="left")

        # ── Options de téléchargement (reflux automatique selon la largeur) ──
        frm_opts_box = ttk.LabelFrame(page, text=t("opts.frame_label"), padding=8)
        frm_opts_box.pack(fill="x", **pad)
        frm_opts = _FlowFrame(frm_opts_box)
        frm_opts.pack(fill="x")

        # Qualité
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_quality")).pack(side="left", padx=(0, 4))
        self.var_quality = tk.StringVar(value="1080p")
        self._quality_combo = ttk.Combobox(
            g, textvariable=self.var_quality,
            values=[t("opts.quality_best"), "2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"],
            state="readonly", width=12)
        self._quality_combo.pack(side="left")
        frm_opts.add(g)

        # Audio seulement
        self.var_audio_only = tk.BooleanVar(value=False)

        def _on_audio_only_main(*_):
            self._quality_combo.configure(
                state="disabled" if self.var_audio_only.get() else "readonly")
            self._update_cmd()
        self.var_audio_only.trace_add("write", _on_audio_only_main)
        g = ttk.Frame(frm_opts)
        ttk.Checkbutton(g, text=t("opts.chk_audio_only"),
                        variable=self.var_audio_only).pack(side="left")
        frm_opts.add(g)

        # Format ST
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_sub_fmt")).pack(side="left", padx=(0, 4))
        self.var_sub_fmt = tk.StringVar(value="srt")
        ttk.Combobox(g, textvariable=self.var_sub_fmt, values=SUBTITLE_FORMATS,
                     state="readonly", width=6).pack(side="left")
        frm_opts.add(g)

        # Intégrer ST / Miniature
        self.var_embed_subs = tk.BooleanVar(value=False)
        self.var_embed_thumb = tk.BooleanVar(value=False)
        g = ttk.Frame(frm_opts)
        ttk.Checkbutton(g, text=t("opts.chk_embed_subs"),
                        variable=self.var_embed_subs).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(g, text=t("opts.chk_embed_thumb"),
                        variable=self.var_embed_thumb).pack(side="left")
        frm_opts.add(g)

        # Cookies : menu + voyant + bouton test (comme dans l'inspecteur)
        self.var_browser = tk.StringVar(value=BROWSER_OFF)
        self._cookie_frame = CookieFrame(frm_opts, self.var_browser, "opts.label_cookies", "opts.cookie_warn",
                                         warn_wrap=280)
        self.var_browser.trace_add("write", lambda *_: self._update_cmd())
        frm_opts.add(self._cookie_frame)

        # Langue principale
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_primary_lang")).pack(side="left", padx=(0, 4))
        self._opt_primary_default  = t("opts.primary_lang_default")
        self._opt_primary_no_audio = t("opts.primary_lang_no_audio")
        self._opt_primary_manual   = t("opts.primary_lang_manual")
        self.var_primary_lbl = tk.StringVar(value=self._opt_primary_default)
        self._primary_combo = ttk.Combobox(
            g, textvariable=self.var_primary_lbl,
            values=[self._opt_primary_default, self._opt_primary_no_audio, self._opt_primary_manual],
            state="readonly", width=26)
        self._primary_combo.pack(side="left")
        frm_opts.add(g)
        self._primary_map = {self._opt_primary_default: "",
                             self._opt_primary_no_audio: "__video_only__",
                             self._opt_primary_manual: "__manual__"}
        self._manual_primary_code = ""

        def _on_primary_main(evt=None):
            if self.var_primary_lbl.get() == self._opt_primary_manual:
                self._pick_primary_language_main()
            self._update_cmd()

        self._primary_combo.bind("<<ComboboxSelected>>", _on_primary_main)
        self.var_primary_lbl.trace_add("write", lambda *_: self.after(20, self._update_cmd))

        # Audio secondaire(s)
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_secondary_audio")).pack(side="left", padx=(0, 4))
        self._secondary_sel = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=28,
            on_change=self._update_cmd)
        self._secondary_sel.set_options(
            [(_c, _tblklbl(_c, _l)) for _c, _l in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])])
        self._secondary_sel.pack(side="left")
        frm_opts.add(g)

        # Sous-titres
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_subs")).pack(side="left", padx=(0, 4))
        self._subs_sel = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=22,
            on_change=self._update_cmd)
        self._subs_sel.set_options(
            [(_c, _tblklbl(_c, _l)) for _c, _l in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])])
        self._subs_sel.pack(side="left")
        frm_opts.add(g)

        # Blocs de script (+ avertissement miniature MKV)
        g = ttk.Frame(frm_opts)
        ttk.Label(g, text=t("opts.label_blocks")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self._blocks_sel = MultiCheckSelect(
            g, placeholder=t("opts.placeholder_disabled"), width=32,
            tabs=_translated_blocks_tabs(), on_change=self._update_cmd)
        self._blocks_sel.grid(row=0, column=1, sticky="w")
        self._lbl_mkv_warn_main = ttk.Label(
            g, text=t("opts.mkv_warn"),
            foreground="#e67e22", font=(UI_FONT, 8), wraplength=420)
        self._lbl_mkv_warn_main.grid(row=0, column=2, sticky="w", padx=(10, 0))
        self._lbl_mkv_warn_main.grid_remove()
        frm_opts.add(g)

        # Trace mise à jour commande
        for _v in (self.var_quality, self.var_sub_fmt, self.var_embed_subs,
                   self.var_embed_thumb, self.var_audio_only):
            _v.trace_add("write", lambda *_: self._update_cmd())

        # ── Commande générée ───────────────────────
        frm_cmd = ttk.LabelFrame(page, text=t("opts.cmd_frame_label"), padding=8)
        frm_cmd.pack(fill="x", **pad)

        self.var_cmd = tk.StringVar()
        ttk.Entry(frm_cmd, textvariable=self.var_cmd, font=(MONO_FONT, 9),
                  state="readonly").pack(fill="x")

        for _v in (self.var_url, self.var_outdir):
            _v.trace_add("write", lambda *_: self._update_cmd())

        # ── Boutons ────────────────────────────────
        frm_btn = ttk.Frame(page)
        frm_btn.pack(fill="x", padx=10, pady=(0, 6))

        self.btn_dl = ttk.Button(frm_btn, text=t("dl.btn_download"),
                                 command=self._download)
        self.btn_dl.pack(side="left", ipadx=10, ipady=4)

        self.btn_stop = ttk.Button(frm_btn, text=t("dl.btn_stop"),
                                   command=self._stop, state="disabled")
        self.btn_stop.pack(side="left", padx=(6, 0), ipadx=6, ipady=4)

        self.btn_pause = ttk.Button(frm_btn, text=t("dl.btn_pause"),
                                    command=self._toggle_pause, state="disabled")
        self.btn_pause.pack(side="left", padx=(6, 0), ipadx=6, ipady=4)

        ttk.Button(frm_btn, text=t("dl.btn_clear_log"),
                   command=self._clear_log).pack(side="right")

        # ── File d'attente ─────────────────────────
        # tk.PanedWindow (et non ttk) : sa hauteur demandée est la somme de celle de ses volets et chaque
        # volet a une hauteur minimale (« minsize »). Quand la fenêtre est basse, c'est la page qui
        # s'allonge et se parcourt avec la barre de défilement : seuls les tableaux peuvent être réduits
        # à la souris, jamais les boutons.
        paned = tk.PanedWindow(page, orient="vertical", sashwidth=6, sashrelief="flat", bd=0,
                               bg=ttk.Style().lookup("TFrame", "background") or "#f0f0f0")
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._paned = paned
        # la hauteur demandée par la page change sans que sa taille change (premier affichage, contenu
        # des volets) : on recalcule la page et sa barre de défilement à chaque changement du conteneur
        paned.bind("<Configure>", lambda _e: self.after_idle(self._fit_page))

        frm_queue = ttk.LabelFrame(paned, text=t("queue.frame_label"), padding=6)
        paned.add(frm_queue, stretch="always")
        self._frm_queue = frm_queue

        frm_qhead = ttk.Frame(frm_queue)
        frm_qhead.pack(fill="x", pady=(0, 4))
        self._lbl_queue_count = ttk.Label(frm_qhead, text=t("queue.count_empty"))
        self._lbl_queue_count.pack(side="left")
        ttk.Button(frm_qhead, text=t("queue.btn_add_url"),
                   command=self._queue_add).pack(side="right")

        frm_qtv = ttk.Frame(frm_queue)
        frm_qtv.pack(fill="both", expand=True)

        cols = ("num", "status", "url", "title", "summary")
        self._tv_queue = ttk.Treeview(frm_qtv, columns=cols, show="headings",
                                      selectmode="browse")
        self._tv_queue.heading("num",     text=t("queue.col_num"))
        self._tv_queue.heading("status",  text=t("queue.col_status"))
        self._tv_queue.heading("url",     text=t("queue.col_url"))
        self._tv_queue.heading("title",   text=t("queue.col_title"))
        self._tv_queue.heading("summary", text=t("queue.col_summary"))
        self._tv_queue.column("num",     width=36,  minwidth=36,  stretch=False, anchor="center")
        self._tv_queue.column("status",  width=110, minwidth=80,  stretch=False)
        self._tv_queue.column("url",     width=200, minwidth=80)
        self._tv_queue.column("title",   width=220, minwidth=80)
        self._tv_queue.column("summary", width=180, minwidth=80)
        self._tv_queue.tag_configure("pending", foreground="#222222")
        self._tv_queue.tag_configure("running", foreground="#1a5fa0")
        self._tv_queue.tag_configure("error",   foreground="#c0392b")
        self._tv_queue.bind("<Delete>", lambda e: self._queue_remove_selected())

        sb_q = ttk.Scrollbar(frm_qtv, command=self._tv_queue.yview)
        self._tv_queue.configure(yscrollcommand=sb_q.set)
        sb_q.pack(side="right", fill="y")
        self._tv_queue.pack(fill="both", expand=True)

        # Lancement
        frm_ql1 = ttk.Frame(frm_queue)
        frm_ql1.pack(fill="x", pady=(6, 2))
        ttk.Button(frm_ql1, text=t("queue.btn_run_all"),
                   command=lambda: self._queue_run(0)).pack(side="left", padx=(0, 4))
        ttk.Button(frm_ql1, text=t("queue.btn_run_from"),
                   command=self._queue_run_from_selection).pack(side="left", padx=(0, 4))
        ttk.Button(frm_ql1, text=t("queue.btn_run_one"),
                   command=self._queue_run_one).pack(side="left", padx=(0, 14))
        ttk.Label(frm_ql1, text=t("queue.label_from")).pack(side="left", padx=(0, 2))
        self._spin_from = ttk.Spinbox(frm_ql1, from_=1, to=999, width=4)
        self._spin_from.pack(side="left")
        ttk.Label(frm_ql1, text=t("queue.label_to")).pack(side="left", padx=(4, 2))
        self._spin_to = ttk.Spinbox(frm_ql1, from_=1, to=999, width=4)
        self._spin_to.pack(side="left")
        ttk.Button(frm_ql1, text=t("queue.btn_run_range"),
                   command=self._queue_run_range).pack(side="left", padx=(6, 0))

        # Contrôles
        frm_ql2 = ttk.Frame(frm_queue)
        frm_ql2.pack(fill="x", pady=(2, 0))
        self.btn_q_skip = ttk.Button(frm_ql2, text=t("queue.btn_skip"),
                                     command=self._queue_skip_current, state="disabled")
        self.btn_q_skip.pack(side="left", padx=(0, 4))
        self.btn_q_stop = ttk.Button(frm_ql2, text=t("queue.btn_stop_queue"),
                                     command=self._queue_stop, state="disabled")
        self.btn_q_stop.pack(side="left", padx=(0, 4))
        self.btn_q_pause = ttk.Button(frm_ql2, text=t("queue.btn_pause_queue"),
                                      command=self._toggle_pause, state="disabled")
        self.btn_q_pause.pack(side="left", padx=(0, 14))
        ttk.Button(frm_ql2, text=t("queue.btn_remove_sel"),
                   command=self._queue_remove_selected).pack(side="left", padx=(0, 4))
        ttk.Button(frm_ql2, text=t("queue.btn_clear_errors"),
                   command=self._queue_clear_errors).pack(side="right")
        ttk.Button(frm_ql2, text=t("queue.btn_retry_errors"),
                   command=self._queue_retry_errors).pack(side="right", padx=(0, 6))

        # Les rangées de boutons sont placées en bas du volet AVANT le tableau : quand le volet est réduit,
        # c'est le tableau qui rétrécit, jamais les boutons.
        for f in (frm_qtv, frm_ql1, frm_ql2):
            f.pack_forget()
        frm_ql2.pack(side="bottom", fill="x", pady=(2, 0))
        frm_ql1.pack(side="bottom", fill="x", pady=(6, 2))
        frm_qtv.pack(side="top", fill="both", expand=True)

        # ── Progression ────────────────────────────
        self.var_progress = tk.DoubleVar(value=0)
        self.var_status = tk.StringVar(value=t("app.status_ready"))
        ttk.Label(self, textvariable=self.var_status, anchor="w",
                  font=(UI_FONT, 9)).pack(side="bottom", fill="x", padx=10)
        ttk.Progressbar(self, variable=self.var_progress,
                        maximum=100, mode="determinate").pack(
            side="bottom", fill="x", padx=10, pady=(0, 4))
        frm_page.pack(fill="both", expand=True)

        # ── Journal ────────────────────────────────
        frm_log = ttk.LabelFrame(paned, text=" Journal ", padding=6)
        paned.add(frm_log, stretch="always")
        self._frm_log = frm_log

        self.log_text = tk.Text(frm_log, wrap="word", height=10,
                                font=(MONO_FONT, 9), state="disabled",
                                bg="#1e1e1e", fg="#d4d4d4",
                                insertbackground="white")
        sb = ttk.Scrollbar(frm_log, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        self._update_cmd()
        self.after(50, self._set_pane_minsizes)

    def _set_pane_minsizes(self):
        """Hauteur minimale des volets : tout ce qui n'est pas un tableau (titres, boutons) doit rester visible."""
        try:
            self.update_idletasks()
            rows = 3
            row_h = 20
            table_extra = max(0, self._tv_queue.winfo_reqheight() - rows * row_h)
            self._paned.paneconfigure(self._frm_queue, minsize=max(120, self._frm_queue.winfo_reqheight() - table_extra))
            self._paned.paneconfigure(self._frm_log, minsize=90)
            self._fit_page()
        except tk.TclError:
            pass

    # ──────────────────────────────────────────────
    #  Vérification rapide des dépendances
    # ──────────────────────────────────────────────
    def _check_deps_quick(self):
        missing = [d["name"] for d in DEPS if not dep_installed(d["exe"])]
        if missing:
            required_missing = [d["name"] for d in DEPS
                                if d["required"] and not dep_installed(d["exe"])]
            if required_missing:
                self.var_dep_warn.set(
                    t("app.dep_warn_required", liste=', '.join(required_missing))
                )
                self._lbl_dep_warn.configure(foreground="#e67e22")
            else:
                self.var_dep_warn.set(
                    t("app.dep_warn_optional", liste=', '.join(missing))
                )
                self._lbl_dep_warn.configure(foreground="#7f8c8d")      # simple information, pas une alerte
        else:
            self.var_dep_warn.set(t("app.dep_ok"))
            self._lbl_dep_warn.configure(foreground="#27ae60")

    def _open_options_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=t("toolbar.menu_update"), command=self._open_update)
        menu.add_command(label=t("toolbar.menu_check_update"), command=self._open_app_update)
        self._var_auto_update = tk.BooleanVar(value=bool(load_config().get("update_check", True)))
        menu.add_checkbutton(label=t("toolbar.menu_auto_update_check"), variable=self._var_auto_update,
                             command=self._toggle_auto_update)
        menu.add_command(label=t("toolbar.menu_deps"),   command=self._open_deps)
        menu.add_command(label=t("toolbar.menu_setup"),  command=self._open_setup)
        if IS_WINDOWS:   # ailleurs, tous les navigateurs sont proposés : rien à masquer
            menu.add_command(label=t("toolbar.menu_browsers"), command=lambda: BrowserOptionsWindow(self))
        menu.add_separator()
        menu.add_command(label="🌐  Langue / Language…", command=self._open_lang_dialog)
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def _open_lang_dialog(self):
        _LANGUAGES = [
            ("fr", "Français"),
            ("en", "English"),
            ("es", "Español"),
            ("pt", "Português (Brasil)"),
            ("it", "Italiano"),
            ("pl", "Polski"),
            ("hu", "Magyar"),
            ("sr", "Srpski"),
            ("ru", "Русский"),
            ("vi", "Tiếng Việt"),
            ("zh", "中文（简体）"),
            ("hi", "हिन्दी"),
            ("ja", "日本語"),
            ("ko", "한국어"),
            ("fil", "Filipino"),
        ]
        # Build selection dialog
        dlg = tk.Toplevel(self)
        dlg.title("Langue / Language")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg, text="Langue / Language", font=(UI_FONT, 11, "bold")).pack(pady=(14, 6), padx=20)

        var_lang = tk.StringVar(value=_CURRENT_LANG)
        frm_list = tk.Frame(dlg)
        frm_list.pack(padx=20, pady=4)
        for code, name in _LANGUAGES:
            tk.Radiobutton(frm_list, text=name, variable=var_lang, value=code,
                           anchor="w", width=26).pack(anchor="w")

        def _confirm():
            new_code = var_lang.get()
            if new_code == _CURRENT_LANG:
                dlg.destroy()
                return
            # Find display name
            new_name = next((n for c, n in _LANGUAGES if c == new_code), new_code)
            dlg.destroy()
            self._show_lang_change_dialog(new_code, new_name)

        tk.Button(dlg, text="OK", command=_confirm, width=10).pack(pady=(8, 14))
        dlg.wait_window()

    def _show_lang_change_dialog(self, new_code: str, new_name: str):
        # Load the NEW language strings for the dialog body
        import json as _json
        import pathlib as _pathlib
        _new_strings: dict = {}
        _new_path = _LANG_DIR / f"{new_code}.json"
        if _new_path.exists():
            with open(_new_path, encoding="utf-8") as _f:
                _new_strings = _json.load(_f)
        _en_path = _LANG_DIR / "en.json"
        _en_strings: dict = {}
        if _en_path.exists():
            with open(_en_path, encoding="utf-8") as _f:
                _en_strings = _json.load(_f)

        def _nt(key: str) -> str:
            return _new_strings.get(key) or _en_strings.get(key) or key

        dlg = tk.Toplevel(self)
        dlg.title(_nt("lang.dialog_title"))
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg, text=new_name, font=(UI_FONT, 12, "bold")).pack(pady=(14, 2), padx=24)
        tk.Label(dlg, text=_nt("lang.dialog_body"), wraplength=320).pack(pady=(2, 10), padx=24)

        def _schedule():
            cfg = load_config()
            cfg["lang"] = new_code
            save_config(cfg)
            dlg.destroy()

        def _restart_now():
            cfg = load_config()
            cfg["lang"] = new_code
            save_config(cfg)
            dlg.destroy()
            import subprocess, sys
            subprocess.Popen([sys.executable] if getattr(sys, "frozen", False) else [sys.executable] + sys.argv)
            self.destroy()

        def _cancel():
            dlg.destroy()

        frm_btn = tk.Frame(dlg)
        frm_btn.pack(pady=(4, 14), padx=24)
        tk.Button(frm_btn, text=_nt("lang.btn_schedule"), command=_schedule, width=28).pack(pady=2)
        tk.Button(frm_btn, text=_nt("lang.btn_restart"), command=_restart_now, width=28).pack(pady=2)
        # Cancel button always in CURRENT language
        tk.Button(frm_btn, text=t("lang.btn_cancel"), command=_cancel, width=28).pack(pady=2)

        dlg.wait_window()

    def _open_update(self):
        UpdateWindow(self)

    def _open_app_update(self):
        AppUpdateWindow(self, self._update_info)

    def _toggle_auto_update(self):
        cfg = load_config()
        cfg["update_check"] = bool(self._var_auto_update.get())
        save_config(cfg)

    def _maybe_check_updates(self):
        if not should_check_updates(load_config(), time.time()):
            return

        def work():
            try:
                info = check_for_update()
            except Exception:
                return   # vérification silencieuse : aucune erreur affichée au démarrage
            try:
                self.after(0, lambda: self._record_update_check(info))
            except (tk.TclError, RuntimeError):
                pass
        threading.Thread(target=work, daemon=True).start()

    def _record_update_check(self, info):
        """Mémorise l'heure de la vérification et affiche (ou masque) le bandeau de nouvelle version."""
        cfg = load_config()
        cfg["update_last_check"] = time.time()
        save_config(cfg)
        self._update_info = info
        if info and info["version"] != cfg.get("update_ignored"):
            self._lbl_update.configure(text=t("app_update.banner", version=info["version"]))
            self._frm_update.pack(fill="x", padx=10, pady=(4, 0), after=self._frm_toolbar)
        else:
            self._frm_update.pack_forget()

    def _maybe_first_run(self):
        if not os.path.isfile(YTDLP):
            self._open_setup()

    def _open_setup(self):
        SetupWizardWindow(self, on_done=self._check_deps_quick)

    def _open_playlist_inspector(self):
        url = self._url(fix=True)
        outdir = self.var_outdir.get().strip()
        PlaylistInspectorWindow(self, url=url, outdir=outdir)

    def _open_deps(self):
        win = DepsWindow(self)
        # Actualiser l'indicateur quand la fenêtre se ferme
        win.bind("<Destroy>", lambda _: self.after(200, self._check_deps_quick))

    # ──────────────────────────────────────────────
    #  Logique des options
    # ──────────────────────────────────────────────
    def _pick_primary_language_main(self):
        top = tk.Toplevel(self)
        top.title(t("langpick.window_title"))
        top.geometry("340x420")
        top.resizable(False, True)
        top.grab_set()

        ttk.Label(top, text=t("langpick.label_search")).pack(anchor="w", padx=8, pady=(8, 0))
        var_search = tk.StringVar()
        ttk.Entry(top, textvariable=var_search).pack(fill="x", padx=8)

        lb_frame = ttk.Frame(top)
        lb_frame.pack(fill="both", expand=True, padx=8, pady=4)
        lb = tk.Listbox(lb_frame, activestyle="none", selectmode="single")
        vsb = ttk.Scrollbar(lb_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        lb.pack(side="left", fill="both", expand=True)

        lang_entries = [(_tblklbl(code, lbl), code.replace("alang_", ""))
                        for code, lbl in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])
                        if code.startswith("alang_")]
        _all = lang_entries[:]

        def _refresh(*_):
            q = var_search.get().lower()
            lb.delete(0, "end")
            for lbl, _ in _all:
                if not q or q in lbl.lower():
                    lb.insert("end", lbl)

        var_search.trace_add("write", _refresh)
        _refresh()

        def _confirm():
            sel = lb.curselection()
            if not sel:
                return
            chosen_lbl = lb.get(sel[0])
            chosen_code = next((c for l, c in _all if l == chosen_lbl), "")
            self._manual_primary_code = chosen_code
            self._primary_map[self._opt_primary_manual] = "__manual__"
            self.var_primary_lbl.set(chosen_lbl)
            self._primary_map[chosen_lbl] = chosen_code
            top.destroy()

        btn_fr = ttk.Frame(top)
        btn_fr.pack(fill="x", padx=8, pady=6)
        ttk.Button(btn_fr, text=t("langpick.btn_confirm"), command=_confirm).pack(side="right", padx=(4, 0))
        ttk.Button(btn_fr, text=t("langpick.btn_cancel"), command=top.destroy).pack(side="right")

    def _paste_url(self):
        try:
            self.var_url.set(self.clipboard_get())
        except tk.TclError:
            pass

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.var_outdir.get())
        if d:
            self.var_outdir.set(d)

    @staticmethod
    def _sanitize_title(title):
        """
        Reproduit la sanitisation yt-dlp sur Windows :
        les caractères interdits sont remplacés par leurs équivalents pleine chasse Unicode.
        """
        # Table de remplacement identique à yt-dlp (sanitize_filename, Windows)
        _WIN_REPL = {
            ':':  '：',   # U+FF1A FULLWIDTH COLON
            '*':  '＊',   # U+FF0A FULLWIDTH ASTERISK
            '?':  '？',   # U+FF1F FULLWIDTH QUESTION MARK
            '"':  '＂',   # U+FF02 FULLWIDTH QUOTATION MARK
            '<':  '＜',   # U+FF1C FULLWIDTH LESS-THAN SIGN
            '>':  '＞',   # U+FF1E FULLWIDTH GREATER-THAN SIGN
            '|':  '｜',   # U+FF5C FULLWIDTH VERTICAL LINE
        }
        for ch, repl in _WIN_REPL.items():
            title = title.replace(ch, repl)
        return title.strip()

    @staticmethod
    def _unique_output_path(outdir, title):
        """
        Retourne un chemin -o avec suffixe _2, _3… si outdir/title.* existe déjà.
        Retourne None si pas de conflit (utiliser le template %(title)s.%(ext)s).
        Le titre est sanitisé (caractères Windows interdits retirés) avant le glob.
        """
        import glob as _glob, re as _re
        if not outdir or not title:
            return None
        if not os.path.isdir(outdir):
            return None
        # Sanitiser comme yt-dlp pour correspondre au nom réel sur disque
        safe = YtDlpGui._sanitize_title(title)
        if not safe:
            return None
        def _exists(t):
            pat = os.path.normpath(os.path.join(outdir, _glob.escape(t) + ".*"))
            return bool(_glob.glob(pat))
        if not _exists(safe):
            return None
        n = 2
        while True:
            candidate = f"{safe}_{n}"
            if not _exists(candidate):
                return os.path.normpath(os.path.join(_tmpl_esc(outdir), _tmpl_esc(candidate) + ".%(ext)s"))
            n += 1

    def _build_args(self):
        url = self._url()
        secondary = []
        force_mp4 = False
        embed_thumb = self.var_embed_thumb.get()

        if self.var_audio_only.get():
            primary_code = self._primary_map.get(self.var_primary_lbl.get(), "")
            if primary_code == "__manual__":
                primary_code = getattr(self, "_manual_primary_code", "")
            secondary = [c.replace("alang_", "") for c in self._secondary_sel.get_selected()]

            if secondary:
                # Plusieurs pistes audio → MKV multi-stream
                prim_fmt = (f"bestaudio[language^={primary_code}]"
                            if primary_code and primary_code not in ("__video_only__",)
                            else "bestaudio")
                sec_str = "+".join(f"bestaudio[language^={l}]" for l in secondary)
                fmt = f"{prim_fmt}+{sec_str}/{prim_fmt}/bestaudio/best"
                args = [YTDLP, "-f", fmt,
                        *MULTI_AUDIO_ARGS]
            else:
                # Piste unique → MP3
                if primary_code and primary_code not in ("__video_only__",):
                    fmt = f"bestaudio[language^={primary_code}]/bestaudio/best"
                else:
                    fmt = "bestaudio/best"
                args = [YTDLP, "-f", fmt,
                        "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
        else:
            quality = self.var_quality.get()
            q_map = {t("opts.quality_best"): None, "2160p (4K)": "2160", "1440p": "1440", "1080p": "1080",
                     "720p": "720", "480p": "480", "360p": "360", "240p": "240", "144p": "144"}
            h = q_map.get(quality)

            primary_code = self._primary_map.get(self.var_primary_lbl.get(), "")
            if primary_code == "__manual__":
                primary_code = self._manual_primary_code

            block_audio = [SCRIPT_BLOCKS_MAP[c][1] for c in self._blocks_sel.get_selected()
                           if SCRIPT_BLOCKS_MAP.get(c, [""])[0] == "_alang_"]
            secondary = list(dict.fromkeys(
                [c.replace("alang_", "") for c in self._secondary_sel.get_selected()] + block_audio
            ))

            hf = f"[height<={h}]" if h else ""
            vsel = f"bestvideo{hf}"
            vsel_h264 = f"bestvideo[vcodec^=avc1]{hf}" if embed_thumb else None
            force_mp4 = (embed_thumb and not secondary and not primary_code)

            if primary_code == "__video_only__":
                fmt = f"{vsel_h264}/{vsel}" if vsel_h264 else vsel
            elif primary_code and secondary:
                sec_str = "+".join(f"bestaudio[language^={l}]" for l in secondary)
                if vsel_h264:
                    fmt = (f"{vsel_h264}+bestaudio[language^={primary_code}]+{sec_str}"
                           f"/{vsel}+bestaudio[language^={primary_code}]+{sec_str}"
                           f"/{vsel_h264}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = (f"{vsel}+bestaudio[language^={primary_code}]+{sec_str}"
                           f"/{vsel}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio/best")
            elif primary_code:
                if vsel_h264:
                    fmt = (f"{vsel_h264}+bestaudio[language^={primary_code}][ext=m4a]"
                           f"/{vsel_h264}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = (f"{vsel}+bestaudio[language^={primary_code}]"
                           f"/{vsel}+bestaudio/best")
            elif secondary:
                # primary vide = piste par défaut (bestaudio) + secondaires explicites
                sec_str = "+".join(f"bestaudio[language^={l}]" for l in secondary)
                if vsel_h264:
                    fmt = (f"{vsel_h264}+bestaudio+{sec_str}"
                           f"/{vsel_h264}+bestaudio"
                           f"/{vsel}+bestaudio+{sec_str}"
                           f"/{vsel}+bestaudio/best")
                else:
                    fmt = f"{vsel}+bestaudio+{sec_str}/{vsel}+bestaudio/best"
            else:
                if force_mp4:
                    fmt = (f"{vsel_h264}[ext=mp4]+bestaudio[ext=m4a]"
                           f"/{vsel_h264}+bestaudio[ext=m4a]"
                           f"/best[ext=mp4]/best")
                elif vsel_h264:
                    fmt = f"{vsel_h264}+bestaudio/{vsel}+bestaudio/best"
                else:
                    fmt = f"{vsel}+bestaudio/best"

            args = [YTDLP, "-f", fmt]
            if secondary:
                args += MULTI_AUDIO_ARGS
            elif force_mp4:
                args += ["--merge-output-format", "mp4"]
            elif embed_thumb and primary_code and not secondary:
                args += ["--merge-output-format", "mp4/mkv"]

        # Sous-titres
        sub_codes = [c.replace("alang_", "") for c in self._subs_sel.get_selected()]
        if sub_codes:
            args += ["--sub-lang", ",".join(sub_codes),
                     "--sub-format", self.var_sub_fmt.get(),
                     "--write-auto-subs"]
            if self.var_embed_subs.get():
                args += EMBED_SUBS_ARGS
                if not secondary and not force_mp4 and not (embed_thumb and primary_code):
                    args += ["--merge-output-format", "mkv"]
            else:
                args += ["--write-subs"]

        if self.var_embed_thumb.get():
            args += ["--embed-thumbnail", "--convert-thumbnails", "jpg"]

        args += ["--no-playlist"]

        # Blocs de script (non-langue)
        for code in self._blocks_sel.get_selected():
            block_args = SCRIPT_BLOCKS_MAP.get(code, [])
            if not block_args or block_args[0] == "_alang_":
                continue
            args += block_args

        # Cookies
        browser = self.var_browser.get()
        if browser and browser != BROWSER_OFF:
            args += ["--cookies-from-browser", browser]

        out = self.var_outdir.get().strip()
        if out:
            cur_url = self._url()
            insp_url = getattr(self, "_inspected_url", "")
            known_title = getattr(self, "_inspected_title", "") if cur_url == insp_url else ""
            unique = self._unique_output_path(out, known_title) if known_title else None
            args += ["-o", unique if unique else os.path.join(_tmpl_esc(out), "%(title)s.%(ext)s")]

        args += ["--retries", "10", "--fragment-retries", "10",
                 "--sleep-interval", "3", "--max-sleep-interval", "8"]
        args += ["--progress", "--newline"]

        if url:
            args += ["--", url]

        return args

    def _update_cmd(self):
        args = self._build_args()
        display = " ".join(f'"{a}"' if " " in a else a for a in args)
        self.var_cmd.set(display)
        has_secondary = bool(self._secondary_sel.get_selected())
        embed_thumb = self.var_embed_thumb.get()
        if IS_WINDOWS and has_secondary and embed_thumb:   # l'avertissement parle de l'Explorateur Windows
            self._lbl_mkv_warn_main.grid()
        else:
            self._lbl_mkv_warn_main.grid_remove()

    # ──────────────────────────────────────────────
    #  Journal
    # ──────────────────────────────────────────────
    def _log(self, text, tag=None):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n", tag or "")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ──────────────────────────────────────────────
    #  Inspection
    # ──────────────────────────────────────────────
    def _url(self, fix=False):
        """URL du champ, débarrassée du texte collé autour ; avec fix=True le champ est corrigé à l'écran."""
        raw = self.var_url.get().strip()
        url = extract_url(raw)
        if fix and url != raw:
            self.var_url.set(url)
        return url

    def _show_inspect_box(self, text, color, url):
        """Affiche (ou met à jour) l'encadré de résultat sous le champ URL."""
        self._inspect_box_url = url
        self._lbl_inspect.configure(text=text, fg=color)
        if not self._lbl_inspect.winfo_ismapped():
            self._lbl_inspect.pack(fill="x", padx=12, pady=(0, 2), after=self._frm_url)

    def _inspect_playlist(self, url, cookie_args, browser):
        """Résumé d'une adresse de playlist (thread d'analyse) : titre, nombre de vidéos, vidéos indisponibles."""
        result = subprocess.run(
            [YTDLP, "-J", "--flat-playlist", "--no-warnings"] + cookie_args + ["--", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
            **NO_WINDOW, cwd=os.path.dirname(YTDLP))
        summary = None
        if result.returncode == 0:
            try:
                summary = playlist_summary(json.loads(result.stdout))
            except ValueError:
                summary = None
        if summary is None:
            for line in result.stderr.splitlines():
                self.after(0, self._log, line)
            hint = _cookie_hint(result.stderr, browser)
            if hint:
                self.after(0, self._log, hint, "info")
            if result.returncode == 0:
                self.after(0, self._log, t("inspect.log_bad_json"), "error")
            self.after(0, self._show_inspect_box, t("inspect.box_failed"), "#c0392b", url)
            return
        key = "inspect.playlist_bad" if summary["bad"] else "inspect.playlist"
        summary["title"] = summary["title"] or t("inspect.playlist_untitled")
        text = t(key, **summary)
        self._inspected_title, self._inspected_url = summary["title"], url
        self.after(0, self._log, text, "info")
        self.after(0, self._show_inspect_box, text, "#f5a623" if summary["bad"] else "#27ae60", url)

    def _on_url_changed_for_box(self):
        if self._inspect_box_url is not None and self._url() != self._inspect_box_url:
            self._inspect_box_url = None
            self._lbl_inspect.pack_forget()

    def _inspect(self):
        url = self._url(fix=True)
        if not url:
            messagebox.showwarning(t("url.warn_missing_title"), t("url.warn_missing_msg"))
            return
        self._clear_log()
        self._log(t("inspect.log_start", url=url), "info")
        self._show_inspect_box(t("inspect.box_running"), "gray", url)

        browser = self.var_browser.get()
        cookie_args = ["--cookies-from-browser", browser] if browser != BROWSER_OFF else []

        def run():
            try:
                if is_playlist_url(url):
                    self._inspect_playlist(url, cookie_args, browser)
                    return
                result = subprocess.run(
                    [YTDLP, "-j", "--no-playlist"] + cookie_args + ["--", url],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="replace",
                    **NO_WINDOW,
                    cwd=os.path.dirname(YTDLP),
                )
                if result.returncode != 0:
                    for line in result.stderr.splitlines():
                        self.after(0, self._log, line)
                    hint = _cookie_hint(result.stderr, browser)
                    if hint:
                        self.after(0, self._log, hint, "info")
                    self.after(0, self._show_inspect_box, t("inspect.box_failed"), "#c0392b", url)
                    return
                try:
                    info = json.loads(result.stdout)
                except Exception:
                    self.after(0, self._log, t("inspect.log_bad_json"), "error")
                    self.after(0, self._show_inspect_box, t("inspect.box_failed"), "#c0392b", url)
                    return

                title = info.get("title", "?")
                self._inspected_title = title   # mémorisé pour la déduplication
                self._inspected_url   = url
                duration = info.get("duration_string", "")
                uploader = info.get("uploader", "")
                self.after(0, self._log, t("inspect.log_title", title=title), "info")
                self.after(0, self._log, t("inspect.log_duration", duration=duration, uploader=uploader), "info")

                # Pistes audio
                formats = info.get("formats", [])
                audio_langs = set()
                for f in formats:
                    lang = f.get("language")
                    if lang and lang != "und" and (f.get("acodec") or "none") != "none":
                        audio_langs.add(lang.split("-")[0].lower())

                # Repli sur -F si aucune langue détectée via JSON
                if not audio_langs:
                    try:
                        r2 = subprocess.run(
                            [YTDLP, "-F", "--no-playlist"] + cookie_args + ["--", url],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace",
                            **NO_WINDOW,
                            cwd=os.path.dirname(YTDLP),
                        )
                        audio_langs.update(format_table_languages(r2.stdout))
                    except Exception:
                        pass

                audio_langs.discard("und")
                audio_langs = sorted(audio_langs)

                # Sous-titres manuels + automatiques
                _known_langs = set(_LANG_NAMES.keys())
                manual_subs = set()
                auto_subs = set()
                for lang in info.get("subtitles", {}):
                    base = lang.split("-")[0].lower()
                    if base and base != "und" and 2 <= len(base) <= 4:
                        manual_subs.add(base)
                for lang in info.get("automatic_captions", {}):
                    base = lang.split("-")[0].lower()
                    if base and base != "und" and 2 <= len(base) <= 4:
                        if base in _known_langs or base in manual_subs:
                            auto_subs.add(base)
                all_sub_langs = sorted(manual_subs | auto_subs)
                auto_only = auto_subs - manual_subs

                def _populate():
                    audio_options = [(f"alang_{l}", _lang_label(l)) for l in audio_langs]
                    self._secondary_sel.set_options(audio_options)
                    # Sous-titres : union pistes audio + langues ST détectées
                    sub_options = [(f"alang_{l}", ("[Auto] " if l in auto_only else "") + _lang_label(l))
                                   for l in all_sub_langs]
                    self._subs_sel.set_options(sub_options)
                    # Combobox langue principale
                    choices = ([self._opt_primary_default, self._opt_primary_no_audio, self._opt_primary_manual]
                               + [_lang_label(l) for l in audio_langs])
                    self._primary_combo.configure(values=choices)
                    for l in audio_langs:
                        self._primary_map[_lang_label(l)] = l
                    none = t("inspect.none")
                    self._log(t("inspect.log_audio", langs=', '.join(audio_langs) or none), "info")
                    sub_info = ', '.join(all_sub_langs) or none
                    auto_info = (t("inspect.auto_part", langs=', '.join(sorted(auto_only)))
                                 if auto_only else "")
                    self._log(t("inspect.log_subs", langs=sub_info, auto=auto_info), "info")
                    head = title + (f" ({duration})" if duration else "") + (f" — {uploader}" if uploader else "")
                    self._show_inspect_box(
                        head + "\n" + t("inspect.box_langs", audio=', '.join(a.upper() for a in audio_langs) or none,
                                        subs=', '.join(a.upper() for a in all_sub_langs) or none),
                        "#27ae60", url)

                self.after(0, _populate)

                self.after(0, self._log, "", None)
                # Afficher aussi les formats (-F) pour info
                proc2 = subprocess.Popen(
                    [YTDLP, "-F", "--no-playlist"] + cookie_args + ["--", url],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    **NO_WINDOW,
                    cwd=os.path.dirname(YTDLP),
                )
                for line in proc2.stdout:
                    self.after(0, self._log, line.rstrip())
                proc2.wait()

            except Exception as e:
                self.after(0, self._log, t("common.log_error", error=e), "error")
                self.after(0, self._show_inspect_box, t("inspect.box_failed"), "#c0392b", url)
                advice = av_advice(e)
                if advice:
                    self.after(0, self._log, advice, "info")

        threading.Thread(target=run, daemon=True).start()

    # ──────────────────────────────────────────────
    #  Téléchargement
    # ──────────────────────────────────────────────
    def _download(self):
        url = self._url(fix=True)
        if not url:
            messagebox.showwarning(t("url.warn_missing_title"), t("url.warn_missing_msg"))
            return
        self._start_download(self._build_args())

    def _start_download(self, args):
        self.btn_dl.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_pause.configure(state="normal")
        self._paused = False
        self._current_dl_files = []   # fichiers en cours pour nettoyage si skip
        self._finished_items_files = []   # éléments déjà terminés d'une playlist
        self._dl_started = time.time()
        self._cookie_hint_shown = False
        self.var_progress.set(0)
        self.var_status.set(t("app.status_starting"))
        self._clear_log()
        self._log("$ " + " ".join(f'"{a}"' if " " in a else a for a in args), "cmd")

        def run():
            run_args, conf_file = command_file_args(args)
            output = []
            try:
                self._process = subprocess.Popen(
                    run_args,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    **PROCESS_GROUP,
                    cwd=os.path.dirname(YTDLP),
                )
                for line in self._process.stdout:
                    output.append(line.rstrip())
                    self.after(0, self._on_output_line, line.rstrip())
                self._process.wait()
                ok = self._process.returncode == 0
                self.after(0, self._on_done, ok, None if ok else playlist_outcome(output))
            except Exception as e:
                self.after(0, self._log, t("common.log_error", error=e))
                advice = av_advice(e)
                if advice:
                    self.after(0, self._log, advice, "info")
                self.after(0, self._on_done, False)
            finally:
                self._process = None
                remove_command_file(conf_file)

        threading.Thread(target=run, daemon=True).start()

    _RE_PROGRESS = re.compile(r"\[download\]\s+([\d.]+)%")
    _RE_DEST     = re.compile(r"\[download\] Destination:\s+(.+)")
    _RE_SUBS     = re.compile(r"\[info\] Writing video (?:subtitles|automatic captions) to:\s+(.+)")
    _RE_FINAL    = re.compile(r'\[Merger\] Merging formats into "(.+)"|\[ExtractAudio\] Destination:\s+(.+)'
                              r'|\[Video(?:Remuxer|Convertor)\].*?Destination:\s+"?(.+?)"?\s*$')
    _RE_THUMB    = re.compile(r"\[info\] (?:Writing|Downloading) video thumbnail \S+ to:\s+(.+)")
    _RE_THUMB2   = re.compile(r'\[ThumbnailsConvertor\] Converting thumbnail "(.+?)" to ')

    def _on_output_line(self, line):
        self._log(line)
        if _RE_PLAYLIST_ITEM.search(line):
            # nouvel élément de playlist : les fichiers de l'élément précédent sont terminés
            self._finished_items_files = list(getattr(self, "_finished_items_files", [])) \
                + list(getattr(self, "_current_dl_files", []))
            self._current_dl_files = []
        if not self._cookie_hint_shown:
            hint = _cookie_hint(line, self.var_browser.get())
            if hint:
                self._cookie_hint_shown = True
                self._log(hint, "info")
        m = self._RE_PROGRESS.search(line)
        if m:
            pct = float(m.group(1))
            self.var_progress.set(pct)
            self.var_status.set(t("app.status_downloading_pct", pct=pct))
        m2 = self._RE_DEST.search(line)
        if m2:
            path = m2.group(1).strip()
            self.var_status.set(f"↓ {os.path.basename(path)}")
            if hasattr(self, "_current_dl_files") and path not in self._current_dl_files:
                self._current_dl_files.append(path)
        msub = self._RE_SUBS.search(line)
        if msub and hasattr(self, "_current_dl_files"):
            sub_path = msub.group(1).strip()
            if sub_path not in self._current_dl_files:
                self._current_dl_files.append(sub_path)
        mfin = self._RE_FINAL.search(line)
        if mfin and hasattr(self, "_current_dl_files"):
            final = next(g for g in mfin.groups() if g).strip()
            if final not in self._current_dl_files:
                self._current_dl_files.append(final)
        m3 = self._RE_THUMB.search(line)
        if m3:
            thumb = m3.group(1).strip()
            base = os.path.splitext(thumb)[0]
            for ext in (os.path.splitext(thumb)[1], ".jpg", ".png", ".webp"):
                p = base + ext
                if hasattr(self, "_current_dl_files") and p not in self._current_dl_files:
                    self._current_dl_files.append(p)
        m4 = self._RE_THUMB2.search(line)
        if m4:
            thumb2 = m4.group(1).strip()
            if hasattr(self, "_current_dl_files") and thumb2 not in self._current_dl_files:
                self._current_dl_files.append(thumb2)
            base2 = os.path.splitext(thumb2)[0]
            for ext in (".jpg", ".png", ".webp"):
                p = base2 + ext
                if hasattr(self, "_current_dl_files") and p not in self._current_dl_files:
                    self._current_dl_files.append(p)

    def _on_done(self, success, partial=None):
        self._finished_items_files = []
        self.btn_dl.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_pause.configure(state="disabled", text=t("dl.btn_pause"))
        self._paused = False
        if success:
            self._current_dl_files = []   # téléchargement terminé : ses fichiers sont définitifs
            self.var_progress.set(100)
            self.var_status.set(t("app.status_done_ok"))
            self._log(t("app.log_done"), "ok")
        elif partial:
            # playlist allée au bout : les vidéos téléchargées sont définitives ; une entrée de la file reste
            # en erreur (branche ci-dessous), pour que l'utilisateur décide de la relancer
            ok, failed = partial
            self._current_dl_files = []
            self.var_progress.set(100)
            self.var_status.set(t("app.status_done_partial", ok=ok, failed=failed))
            self._log(t("app.status_done_partial", ok=ok, failed=failed), "info")
        else:
            self.var_status.set(t("app.status_done_fail"))
            self._log(t("app.status_done_fail"), "err")

        if not self._queue_running:
            self._refresh_queue_tv()
            return

        idx = self._queue_index
        if self._queue_skip:
            # Sauter : l'entrée reste "pending", on passe à la suivante
            self._queue_skip = False
            self._queue_index += 1
            self._refresh_queue_tv()
            self._queue_run_next()
        elif success:
            # Succès : suppression automatique + avancement
            if 0 <= idx < len(self._queue):
                del self._queue[idx]
                save_queue(self._queue)
                self._queue_end_index = max(-1, self._queue_end_index - 1)
            self._refresh_queue_tv()
            self._queue_run_next()
        else:
            # Erreur : marquer et avancer
            if 0 <= idx < len(self._queue):
                self._queue[idx]["status"] = "error"
                save_queue(self._queue)
            self._queue_index += 1
            self._refresh_queue_tv()
            self._queue_run_next()

    def _kill_current_process(self):
        """Tue le processus yt-dlp en cours (et ses enfants). Retourne False s'il n'y en a pas."""
        proc = self._process
        if not proc:
            return False
        if self._paused:
            self._resume_process(proc.pid)
        kill_process_tree(proc)
        return True

    def _confirm_stop_scope(self):
        """Avant d'arrêter une playlist déjà en partie téléchargée : que faut-il supprimer ?

        Renvoie False si l'utilisateur annule (le téléchargement continue). « Oui » ajoute les vidéos déjà
        terminées aux fichiers à supprimer ; « Non » ne supprime que la vidéo en cours."""
        proc = self._process
        if not getattr(self, "_finished_items_files", []) or proc is None or proc.poll() is not None:
            return True
        # Le téléchargement est mis en pause pendant la question : rien ne doit être téléchargé de plus, ni
        # échapper à la suppression globale ; il reprend seulement si l'utilisateur annule.
        suspended = not self._paused
        if suspended:
            self._suspend_process(proc.pid)
        try:
            answer = messagebox.askyesnocancel(
                t("dl.stop_playlist_title"),
                t("dl.stop_playlist_msg", n=len(self._finished_items_files)), parent=self)
        except BaseException:
            if suspended:
                self._resume_process(proc.pid)
            raise
        if answer is None:
            if suspended:
                self._resume_process(proc.pid)
            return False
        if answer:
            # la liste est relue après la réponse : elle contient tout ce qui existe à cet instant
            self._current_dl_files = list(self._finished_items_files) + list(self._current_dl_files)
        self._finished_items_files = []
        return True

    def _stop(self):
        if not self._confirm_stop_scope():
            return
        if self._queue_running:
            self._queue_running = False
            self._queue_skip = False
            self._queue_set_running_ui(False)
        if self._kill_current_process():      # rien à nettoyer si aucun téléchargement n'était en cours
            self._cleanup_partial_files()

    # ──────────────────────────────────────────────
    #  File d'attente
    # ──────────────────────────────────────────────
    def _build_summary(self):
        parts = []
        if self.var_audio_only.get():
            parts.append(t("queue.summary_audio_only"))
        else:
            parts.append(self.var_quality.get())
        prim = self.var_primary_lbl.get()
        prim_code = self._primary_map.get(prim, "")
        if prim_code and prim_code not in ("", "__video_only__", "__manual__"):
            parts.append(prim_code.upper())
        elif prim_code == "__video_only__":
            parts.append(t("queue.summary_video_only"))
        sec = self._secondary_sel.get_selected()
        if sec:
            parts.append("+" + "+".join(s.upper() for s in sec))
        subs = self._subs_sel.get_selected()
        if subs:
            parts.append(t("queue.summary_subs_embedded") if self.var_embed_subs.get() else t("queue.summary_subs"))
        if self.var_embed_thumb.get():
            parts.append(t("queue.summary_thumb"))
        browser = self.var_browser.get()
        if browser and browser != BROWSER_OFF:
            parts.append(f"🍪{browser}")
        return " · ".join(parts) if parts else t("queue.summary_default")

    def _refresh_queue_tv(self):
        self._tv_queue.delete(*self._tv_queue.get_children())
        for i, entry in enumerate(self._queue):
            num = i + 1
            status = entry.get("status", "pending")
            if status == "error":
                status_lbl, tag = t("queue.status_error"), "error"
            else:
                status_lbl, tag = t("queue.status_pending"), "pending"
            url = entry.get("url", "")
            url_short = url if len(url) <= 40 else url[:37] + "…"
            title = entry.get("title", "")
            title_lbl = title if title else t("queue.title_resolving") if entry.get("status") == "pending" else ""
            self._tv_queue.insert("", "end", iid=str(i),
                                  values=(num, status_lbl, url_short, title_lbl, entry.get("summary", "")),
                                  tags=(tag,))
        count = len(self._queue)
        pending = sum(1 for e in self._queue if e.get("status") == "pending")
        if count == 0:
            self._lbl_queue_count.configure(text=t("queue.count_empty"))
        else:
            self._lbl_queue_count.configure(
                text=t("queue.count_label", n=count, pending=pending))
        n = max(count, 1)
        self._spin_from.configure(to=n)
        self._spin_to.configure(to=n)

    def _queue_fetch_title(self, idx):
        entry = self._queue[idx]
        url = entry.get("url", "")
        browser = self.var_browser.get()
        cookie_args = ["--cookies-from-browser", browser] if browser != BROWSER_OFF else []
        try:
            r = subprocess.run(
                [YTDLP, "--get-title", "--no-playlist"] + cookie_args + ["--", url],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, encoding="utf-8", errors="replace",
                **NO_WINDOW,
                cwd=os.path.dirname(YTDLP), timeout=30,
            )
            title = r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else ""
        except Exception:
            title = ""
        if idx < len(self._queue) and self._queue[idx].get("url") == url:
            self._queue[idx]["title"] = title
            save_queue(self._queue)
            self.after(0, self._refresh_queue_tv)

    def _queue_add(self):
        url = self._url(fix=True)
        if not url:
            messagebox.showwarning(t("queue.warn_url_missing_title"), t("queue.warn_url_missing_msg"), parent=self)
            return
        entry = {
            "url":     url,
            "args":    self._build_args(),
            "summary": self._build_summary(),
            "status":  "pending",
            "title":   "",
        }
        self._queue.append(entry)
        idx = len(self._queue) - 1
        save_queue(self._queue)
        self._refresh_queue_tv()
        threading.Thread(target=self._queue_fetch_title, args=(idx,), daemon=True).start()
        # Sélectionner la ligne ajoutée
        iid = str(len(self._queue) - 1)
        self._tv_queue.selection_set(iid)
        self._tv_queue.see(iid)

    def _queue_remove(self, idx):
        if 0 <= idx < len(self._queue):
            del self._queue[idx]
            save_queue(self._queue)
            self._refresh_queue_tv()

    def _queue_remove_selected(self):
        sel = self._tv_queue.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self._queue_running and idx == self._queue_index:
            return  # ne pas supprimer l'entrée en cours de téléchargement
        self._queue_remove(idx)

    def _queue_retry_errors(self):
        """Remet en attente tous les éléments en erreur puis relance la file (les autres sont ignorés)."""
        if self._queue_running:
            return
        failed = [e for e in self._queue if e.get("status") == "error"]
        if not failed:
            messagebox.showinfo(t("queue.warn_empty_title"), t("queue.msg_no_errors"), parent=self)
            return
        for e in failed:
            e["status"] = "pending"
        save_queue(self._queue)
        self._refresh_queue_tv()
        self._queue_run(0)

    def _queue_clear_errors(self):
        self._queue = [e for e in self._queue if e.get("status") != "error"]
        save_queue(self._queue)
        self._refresh_queue_tv()

    def _queue_set_running_ui(self, running):
        state = "normal" if running else "disabled"
        self.btn_q_skip.configure(state=state)
        self.btn_q_stop.configure(state=state)
        self.btn_q_pause.configure(state=state)
        self.btn_pause.configure(state=state)

    def _queue_run(self, start_idx, end_idx=None):
        if self._queue_running:
            return
        if not self._queue:
            messagebox.showinfo(t("queue.warn_empty_title"), t("queue.warn_empty_msg"), parent=self)
            return
        self._queue_running = True
        self._queue_index = start_idx
        self._queue_end_index = end_idx if end_idx is not None else len(self._queue) - 1
        self._queue_skip = False
        self._queue_set_running_ui(True)
        self._queue_run_next()

    def _queue_run_next(self):
        while self._queue_index <= self._queue_end_index:
            if self._queue_index >= len(self._queue):
                break
            if self._queue[self._queue_index].get("status") == "pending":
                self._queue_run_entry(self._queue_index)
                return
            self._queue_index += 1
        # Plus rien à faire dans la plage
        self._queue_running = False
        self._queue_set_running_ui(False)
        self._refresh_queue_tv()
        self.var_status.set(t("app.status_queue_done"))

    def _queue_run_entry(self, idx):
        entry = self._queue[idx]
        iid = str(idx)
        url_short = entry.get("url", "")
        if len(url_short) > 55:
            url_short = url_short[:52] + "…"
        self._tv_queue.item(iid,
                            values=(idx + 1, t("queue.status_running"), url_short,
                                    entry.get("title", ""), entry.get("summary", "")),
                            tags=("running",))
        self._tv_queue.see(iid)

        # Déduplication : patcher le -o si le titre est connu et le fichier existe déjà
        args = list(entry["args"])
        title = entry.get("title", "")
        if title:
            outdir = ""
            for i, a in enumerate(args):
                if a == "-o" and i + 1 < len(args):
                    outdir = os.path.dirname(args[i + 1]).replace("%%", "%")
                    break
            if outdir:
                unique = self._unique_output_path(outdir, title)
                if unique:
                    for i, a in enumerate(args):
                        if a == "-o" and i + 1 < len(args):
                            args[i + 1] = unique
                            break

        self._start_download(args)

    def _queue_skip_current(self):
        if not self._queue_running:
            return
        if not self._confirm_stop_scope():
            return
        self._queue_skip = True

        if not self._kill_current_process():
            # Pas de processus actif (cas rare), avancer manuellement
            self._queue_skip = False
            self._queue_index += 1
            self._queue_run_next()
        else:
            self._cleanup_partial_files()

    def _queue_stop(self):
        if not self._queue_running:
            return
        if not self._confirm_stop_scope():
            return
        self._queue_running = False
        self._queue_skip = False
        self._queue_set_running_ui(False)
        if self._kill_current_process():
            self._cleanup_partial_files()
        self.var_status.set(t("app.status_queue_stopped"))
        self._refresh_queue_tv()

    def _queue_run_from_selection(self):
        sel = self._tv_queue.selection()
        if not sel:
            messagebox.showwarning(t("queue.warn_no_sel_title"),
                                   t("queue.warn_no_sel_msg"), parent=self)
            return
        self._queue_run(int(sel[0]))

    def _queue_run_one(self):
        sel = self._tv_queue.selection()
        if not sel:
            messagebox.showwarning(t("queue.warn_no_sel_title"),
                                   t("queue.warn_no_sel_msg"), parent=self)
            return
        idx = int(sel[0])
        self._queue_run(idx, end_idx=idx)

    def _queue_run_range(self):
        try:
            a = int(self._spin_from.get()) - 1
            b = int(self._spin_to.get()) - 1
        except ValueError:
            return
        if a < 0 or b < a or a >= len(self._queue):
            messagebox.showwarning(t("queue.warn_bad_range_title"),
                                   t("queue.warn_bad_range_msg"), parent=self)
            return
        b = min(b, len(self._queue) - 1)
        self._queue_run(a, end_idx=b)

    def _cleanup_partial_files(self):
        """Supprime les fichiers partiels du téléchargement interrompu."""
        files = list(getattr(self, "_current_dl_files", []))
        self._current_dl_files = []
        since = getattr(self, "_dl_started", None)
        def _try_remove(path):
            """Tente de supprimer un fichier avec réessais."""
            import time
            for attempt in range(5):
                try:
                    if not os.path.exists(path):
                        return True   # déjà absent
                    os.remove(path)
                    self.after(0, self._log, f"[cleanup] ✓ {os.path.basename(path)}", "ok")
                    return True
                except Exception as e:
                    if attempt == 4:
                        self.after(0, self._log,
                                   f"[cleanup] ✗ {os.path.basename(path)} : {e}", "err")
                    time.sleep(1.5)
            return False

        def _try_remove_recent(path):
            """Repli : ne supprime que ce que la vidéo interrompue vient d'écrire (voir modified_since)."""
            if modified_since(path, since):
                _try_remove(path)

        def _remove_by_suffix(path, d):
            import re as _re
            name = os.path.basename(path)

            def _norm(s):
                s = s.replace('：', '').replace(':', '').replace('＊', '').replace('？', '')
                s = s.replace('＂', '').replace('＜', '').replace('＞', '').replace('｜', '')
                return _re.sub(r'\s+', ' ', s).strip().lower()

            # Cas 1 : double extension (.f160.mp4, .f140-20.m4a, .en.srt…)
            m = _re.search(r'(\.[a-zA-Z0-9][a-zA-Z0-9\-]*\.[a-zA-Z0-9]{2,4}'
                           r'(?:\.part|\.ytdl)?)$', name)
            if m:
                suffix = m.group(1)
                try:
                    for fname in os.listdir(d):
                        if (fname.endswith(suffix) or fname.endswith(suffix + ".part")
                                or fname.endswith(suffix + ".ytdl")):
                            _try_remove_recent(os.path.join(d, fname))
                except OSError:
                    pass
                return

            # Cas 2 : extension simple (miniature .jpg/.webp/.png…)
            stem, ext = os.path.splitext(name)
            if not ext or len(stem) < 4:
                return
            stem_norm = _norm(stem)
            ext_lower = ext.lower()
            try:
                for fname in os.listdir(d):
                    fstem, fext = os.path.splitext(fname)
                    if fext.lower() == ext_lower and _norm(fstem) == stem_norm:
                        _try_remove_recent(os.path.join(d, fname))
                    elif fext.lower() == ext_lower + ".part" and _norm(fstem) == stem_norm:
                        _try_remove_recent(os.path.join(d, fname))
            except OSError:
                pass

        def _do_cleanup(flist):
            import time, glob as _gl
            time.sleep(2)
            dirs = set()
            for path in flist:
                d = os.path.dirname(path)
                if d:
                    dirs.add(d)
                if os.path.exists(path) or os.path.exists(path + ".part"):
                    for c in (path, path + ".part", path + ".ytdl"):
                        _try_remove(c)
                else:
                    _remove_by_suffix(path, d)
            for d in dirs:
                if not d:
                    continue
                for pat in ("*.part", "*.ytdl"):
                    for f in _gl.glob(os.path.join(d, pat)):
                        _try_remove_recent(f)

        threading.Thread(target=_do_cleanup, args=(files,), daemon=True).start()

    def _update_cookie_warn_main(self):
        self._cookie_frame.refresh()

    def _toggle_pause(self):
        if not self._process:
            return
        if not self._paused:
            self._suspend_process(self._process.pid)
            self._paused = True
            self.btn_pause.configure(text=t("dl.btn_resume"))
            self.var_status.set(t("app.status_paused"))
        else:
            self._resume_process(self._process.pid)
            self._paused = False
            self.btn_pause.configure(text=t("dl.btn_pause"))
            self.var_status.set(t("app.status_resumed"))

    def _suspend_process(self, pid):
        suspend_process_tree(pid)

    def _resume_process(self, pid):
        resume_process_tree(pid)

    # ──────────────────────────────────────────────
    #  Persistance
    # ──────────────────────────────────────────────
    @staticmethod
    def remember(key, value):
        """Écrit un réglage dans la configuration tout de suite : un arrêt brutal ou un redémarrage de
        l'ordinateur ne fait plus perdre le dernier dossier ni le dernier navigateur choisis."""
        update_config(key, value)

    def _restore_config(self):
        c = self._config
        if "outdir" in c:
            self.var_outdir.set(c["outdir"])
        if "quality" in c:
            self.var_quality.set(c["quality"])
        if "audio_only" in c:
            self.var_audio_only.set(c["audio_only"])
        if "sub_fmt" in c:
            self.var_sub_fmt.set(c["sub_fmt"])
        if "embed_subs" in c:
            self.var_embed_subs.set(c["embed_subs"])
        if "embed_thumb" in c:
            self.var_embed_thumb.set(c["embed_thumb"])
        if "browser" in c:
            self.var_browser.set(c["browser"])
        self._update_cookie_warn_main()
        self._update_cmd()
        self.var_outdir.trace_add("write", lambda *_: self.remember("outdir", self.var_outdir.get()))
        self.var_browser.trace_add("write", lambda *_: self.remember("browser", self.var_browser.get()))

    def _on_close(self):
        cfg = load_config()
        cfg.update({
            "outdir":      self.var_outdir.get(),
            "quality":     self.var_quality.get(),
            "audio_only":  self.var_audio_only.get(),
            "sub_fmt":     self.var_sub_fmt.get(),
            "embed_subs":  self.var_embed_subs.get(),
            "embed_thumb": self.var_embed_thumb.get(),
            "browser":     self.var_browser.get(),
        })
        if self.state() not in ("zoomed", "iconic"):
            cfg["window_size"] = re.split(r"[+-]", self.geometry())[0]
        save_config(cfg)
        self.destroy()


RUN_MUTEX_NAME = "yt-dlp-GUI-Running"   # identique à AppMutex dans packaging/yt-dlp-gui.iss
_run_mutex = None


def _acquire_run_mutex():
    """Mutex nommé : l'installateur et le désinstalleur détectent le logiciel en cours d'exécution et
    demandent de le fermer, au lieu d'échouer sur un fichier verrouillé. Sans effet hors Windows."""
    global _run_mutex
    try:
        import ctypes
        _run_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, RUN_MUTEX_NAME)
    except Exception:
        _run_mutex = None
    return _run_mutex


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    _acquire_run_mutex()
    _load_custom_blocks()
    _boot_cfg = load_config()
    load_lang(_boot_cfg.get("lang", "fr"))

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = YtDlpGui()

    app.log_text.tag_configure("cmd", foreground="#9cdcfe")
    app.log_text.tag_configure("ok",  foreground="#4ec9b0")
    app.log_text.tag_configure("err", foreground="#f48771")
    app.log_text.tag_configure("info", foreground="#dcdcaa")

    try:
        ttk.Style().theme_use("vista" if IS_WINDOWS else "clam")
    except Exception:
        pass

    app.mainloop()
