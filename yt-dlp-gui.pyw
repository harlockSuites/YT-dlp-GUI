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

YTDLP              = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt-dlp.exe")
CONFIG_FILE        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui-config.json")
QUEUE_FILE         = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download-queue.json")
CUSTOM_BLOCKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom-blocks.json")

SUBTITLE_LANGS = [
    ("Désactivés", ""),
    ("Français (fr)", "fr"),
    ("Anglais (en)", "en"),
    ("Espagnol (es)", "es"),
    ("Allemand (de)", "de"),
    ("Japonais (ja)", "ja"),
    ("Coréen (ko)", "ko"),
    ("Tous disponibles", "all"),
]

SUBTITLE_FORMATS = ["vtt", "srt", "ass", "best"]

VIDEO_FORMATS = [
    # ── Flux DASH (vidéo seule + audio EN séparé) ──────────────────────────────
    ("Meilleure qualité (EN)", "bestvideo+bestaudio/best"),
    ("1080p H.264 (EN)", "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]"),
    ("720p H.264 (EN)", "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]"),
    # ── Flux HLS multi-langue (vidéo+audio intégrés, protocole m3u8) ───────────
    # Sélectionne le meilleur flux HLS pour la langue choisie ;
    # ffmpeg peut y ajouter une 2e piste audio DASH (ex. EN) via --audio-multistreams
    ("1080p FR (HLS)", "best[language=fr][height<=1080]"),
    # Flux HLS FR (vidéo+audio FR) + audio DASH EN séparé (audio-only).
    # ffmpeg garde la vidéo+audio FR du flux HLS et ajoute l'audio EN comme 2e piste → MKV bi-audio.
    # Fallback : flux FR seul si l'audio EN DASH n'est pas disponible.
    ("1080p FR + EN (MKV)", "best[language=fr][height<=1080]+bestaudio[language=en]/best[language=fr][height<=1080]"),
    ("720p FR (HLS)", "best[language=fr][height<=720]"),
    ("720p FR + EN (MKV)", "best[language=fr][height<=720]+best[language=en][height<=720]/best[language=fr][height<=720]"),
    ("1080p EN original (HLS)", "best[language=en][height<=1080]"),
    # ── Résolutions basses ──────────────────────────────────────────────────────
    ("480p", "bestvideo[height<=480]+bestaudio/best[height<=480]"),
    # ── Audio seul ─────────────────────────────────────────────────────────────
    ("Audio seulement (MP3)", "bestaudio"),
    ("Audio seulement (M4A)", "bestaudio[ext=m4a]/bestaudio"),
    ("Personnalisé…", "custom"),
]

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
    ("Audio",           "audio_multistream",  "Multi-pistes audio (MKV)",         ["--audio-multistreams"]),
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
# Options à plat pour les widgets sans onglets
SCRIPT_BLOCKS_OPTIONS = [(code, lbl) for _, code, lbl, _ in SCRIPT_BLOCKS]
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

_LANG_DIR = _pathlib.Path(__file__).parent / "lang"
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


def _save_custom_blocks():
    """Sauvegarde CUSTOM_BLOCKS dans custom-blocks.json."""
    data = [{"cat": c, "code": co, "label": l, "args": a}
            for c, co, l, a in CUSTOM_BLOCKS]
    try:
        with open(CUSTOM_BLOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


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
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def choco_available():
    return shutil.which("choco") is not None


def dep_installed(exe):
    if shutil.which(exe) is not None:
        return True
    # Fallback : vérifier les chemins connus et injecter dans PATH si trouvé
    dep = next((d for d in DEPS if d["exe"] == exe), None)
    if dep:
        for path in dep.get("known_paths", []):
            if os.path.isfile(path):
                folder = os.path.dirname(path)
                if folder not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
                return True
    return False


def run_elevated(cmd_str):
    """Lance une commande PowerShell avec élévation UAC (Start-Process -Verb RunAs)."""
    ps = (
        f'Start-Process powershell -Verb RunAs '
        f'-ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command "{cmd_str}"\''
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden",
         "-ExecutionPolicy", "Bypass", "-Command", ps],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


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
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", **pad)

        # Avertissement si Chocolatey absent
        if not choco_available():
            frm_warn = ttk.Frame(self, relief="solid", borderwidth=1)
            frm_warn.pack(fill="x", padx=12, pady=(0, 6))
            ttk.Label(
                frm_warn,
                text=t("deps.choco_warn"),
                foreground="#c0392b",
                justify="left",
                padding=8,
            ).pack(anchor="w")

        # Tableau des dépendances
        frm_table = ttk.Frame(self)
        frm_table.pack(fill="x", padx=12)

        has_choco = choco_available()
        headers = [t("deps.col_tool"), t("deps.col_status"), t("deps.col_role"), t("deps.col_action")]
        widths   = [14,       8,        46,      14]
        for col, (h, w) in enumerate(zip(headers, widths)):
            ttk.Label(frm_table, text=h, font=("Segoe UI", 9, "bold"),
                      width=w, anchor="w").grid(row=0, column=col, padx=4, pady=(0, 4))

        self._rows = []
        for i, dep in enumerate(DEPS):
            row = i + 1
            req_tag = " *" if dep["required"] else ""
            lbl_name = ttk.Label(frm_table, text=dep["name"] + req_tag,
                                 font=("Consolas", 9), width=14, anchor="w")
            lbl_name.grid(row=row, column=0, padx=4, pady=2, sticky="w")

            lbl_status = ttk.Label(frm_table, text="…", width=8, anchor="w")
            lbl_status.grid(row=row, column=1, padx=4, pady=2, sticky="w")

            lbl_desc = ttk.Label(frm_table, text=dep["desc"], width=46,
                                 anchor="w", wraplength=340, justify="left")
            lbl_desc.grid(row=row, column=2, padx=4, pady=2, sticky="w")

            url = dep.get("url", "")
            if has_choco:
                btn = ttk.Button(frm_table, text=t("deps.btn_install"),
                                 command=lambda d=dep: self._install(d))
            else:
                btn = ttk.Button(frm_table, text=t("deps.btn_open_site"),
                                 command=lambda u=url: self._open_url(u),
                                 state="normal" if url else "disabled")
            btn.grid(row=row, column=3, padx=4, pady=2)

            self._rows.append({"dep": dep, "lbl_status": lbl_status, "btn": btn})

        ttk.Label(self, text=t("deps.footnote"), font=("Segoe UI", 8), foreground="#666",
                  wraplength=560, justify="left").pack(anchor="w", padx=12)

        # Boutons du bas
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x", padx=12, pady=10)

        ttk.Button(frm_btn, text=t("deps.btn_install_all"),
                   command=self._install_all).pack(side="left", ipadx=6)
        ttk.Button(frm_btn, text=t("deps.btn_refresh"),
                   command=self._refresh).pack(side="left", padx=(8, 0), ipadx=6)
        ttk.Button(frm_btn, text=t("deps.btn_close"),
                   command=self.destroy).pack(side="right", ipadx=6)

        # Journal d'installation
        frm_log = ttk.LabelFrame(self, text=t("deps.log_frame"), padding=6)
        frm_log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log = tk.Text(frm_log, height=8, width=70,
                           font=("Consolas", 9), state="disabled",
                           bg="#1e1e1e", fg="#d4d4d4")
        sb = ttk.Scrollbar(frm_log, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

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
        has_choco = choco_available()
        for row in self._rows:
            dep = row["dep"]
            installed = dep_installed(dep["exe"])
            if installed:
                row["lbl_status"].configure(text=t("deps.status_ok"), foreground="#27ae60")
                row["btn"].configure(state="disabled")
            else:
                row["lbl_status"].configure(text=t("deps.status_absent"), foreground="#c0392b")
                if has_choco:
                    row["btn"].configure(state="normal")
                else:
                    url = dep.get("url", "")
                    row["btn"].configure(state="normal" if url else "disabled")

    def _install(self, dep):
        # ffprobe est installé via le paquet ffmpeg — on évite de le lancer deux fois
        if dep["name"] == "ffprobe":
            ffmpeg_dep = next(d for d in DEPS if d["name"] == "ffmpeg")
            dep = ffmpeg_dep
        self._choco_install([dep["choco"]])

    def _install_all(self):
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
        pkg_str = " ".join(packages)
        cmd = f"choco install {pkg_str} -y; pause"
        self._log(t("deps.log_installing", pkgs=pkg_str), "#9cdcfe")
        self._log(t("deps.log_uac_warning"), "#dcdcaa")
        run_elevated(cmd)

        # Actualiser après un délai (laisse le temps à l'UAC + choco)
        self.after(3000, self._refresh)


# Flags critiques que le GUI utilise — chacun doit être présent dans --help
_GUI_FLAGS = [
    ("--audio-multistreams",   "Multi-pistes audio (FR+EN)"),
    ("--embed-thumbnail",      "Miniature embarquée"),
    ("--embed-subs",           "Sous-titres intégrés"),
    ("--merge-output-format",  "Format de fusion (MKV/MP4)"),
    ("--flat-playlist",        "Inspection rapide de playlist"),
    ("--fragment-retries",     "Retries sur fragments HLS"),
    ("--sleep-interval",       "Délai anti-rate-limit"),
    ("--sub-format",           "Format de sous-titres"),
    ("--write-subs",           "Export sous-titres externe"),
    ("--no-playlist",          "Vidéo seule (ignore playlist)"),
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
                  font=("Consolas", 10)).pack(anchor="w")

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

        self.log = tk.Text(frm_log, height=12, font=("Consolas", 9),
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
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                ver = r.stdout.strip() or "inconnue"
            except Exception:
                ver = "erreur — exe introuvable"
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
                    creationflags=subprocess.CREATE_NO_WINDOW,
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
                self.after(0, lambda: self._log(f"Erreur : {e}", "#f66"))
            self.after(0, lambda: self.btn_auto.configure(state="normal"))
            self.after(0, self._show_version)

        threading.Thread(target=_run, daemon=True).start()

    # ── Remplacement manuel ──────────────────────────────────────
    def _replace_exe(self):
        src = filedialog.askopenfilename(
            title=t("upd.replace_title_dialog"),
            filetypes=[(t("upd.replace_filetypes_exe"), "*.exe"), (t("upd.replace_filetypes_all"), "*.*")],
            parent=self,
        )
        if not src:
            return
        try:
            import shutil as _sh
            # Sauvegarde de l'ancien exe
            backup = YTDLP + ".bak"
            if os.path.exists(YTDLP):
                _sh.copy2(YTDLP, backup)
                self._log(f"Sauvegarde : {backup}", "#888")
            _sh.copy2(src, YTDLP)
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
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                ver = r.stdout.strip()
                self.after(0, lambda v=ver: self._log(t("upd.log_diag_version_ok", v=v), "#4ec94e"))
            except Exception as e:
                self.after(0, lambda: self._log(f"✘ Impossible de lire la version : {e}", "#f66"))
                self.after(0, lambda: self.btn_diag.configure(state="normal"))
                return

            # 3. Flags requis (parse --help)
            try:
                h = subprocess.run([YTDLP, "--help"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace",
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                help_text = h.stdout + h.stderr
            except Exception as e:
                self.after(0, lambda: self._log(f"✘ Impossible de lire --help : {e}", "#f66"))
                self.after(0, lambda: self.btn_diag.configure(state="normal"))
                return

            self.after(0, lambda: self._log(t("upd.log_diag_flags_header"), "#888"))
            all_ok = True
            for flag, desc in _GUI_FLAGS:
                present = flag in help_text
                if present:
                    self.after(0, lambda f=flag, d=desc:
                               self._log(f"  ✔ {f:<28}  {d}", "#4ec94e"))
                else:
                    all_ok = False
                    self.after(0, lambda f=flag, d=desc:
                               self._log(t("upd.log_diag_flag_missing", flag=f, desc=d), "#f66"))

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
                  font=("Segoe UI", 9)).pack(fill="x", padx=8, pady=(8, 2))

        self.var_progress = tk.DoubleVar(value=0)
        ttk.Progressbar(self, variable=self.var_progress, maximum=100,
                        mode="determinate").pack(fill="x", padx=8, pady=(0, 4))

        frm_log = ttk.LabelFrame(self, text=t("dlq.log_frame_label"), padding=6)
        frm_log.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.log = tk.Text(frm_log, wrap="word", font=("Consolas", 9),
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
        """Tue le processus yt-dlp en cours et supprime les fichiers partiels."""
        if self._paused and self._process:
            self._resume_process(self._process.pid)
            self._paused = False
        if self._process:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self._process.pid)],
                    creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            except Exception:
                try:
                    self._process.terminate()
                except Exception:
                    pass
        files = list(self._current_dl_files)
        self._current_dl_files = []

        # Répertoire de sortie connu via l'inspecteur (filet de sécurité si files est vide)
        insp_outdir = ""
        if self._inspector is not None:
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
                            _try_remove(os.path.join(d, fname))
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
                        _try_remove(os.path.join(d, fname))
                    elif fext.lower() == ext_lower + ".part" and _norm(fstem) == stem_norm:
                        _try_remove(os.path.join(d, fname))
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
                        _try_remove(f)

        t = threading.Thread(target=_cleanup, args=(files, insp_outdir), daemon=True)
        self._cleanup_thread = t
        t.start()

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
            t = getattr(self, "_cleanup_thread", None)
            if t:
                t.join()
            try:
                self.after(0, self.destroy)
            except Exception:
                pass
        threading.Thread(target=_wait_and_destroy, daemon=True).start()

    def _suspend_process(self, pid):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            result = subprocess.run(
                ["wmic", "process", "where", f"(ParentProcessId={pid})", "get", "ProcessId"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=3,
            )
            child_pids = [int(x.strip()) for x in result.stdout.split() if x.strip().isdigit()]
            for cpid in child_pids:
                h = kernel32.OpenProcess(0x1F0FFF, False, cpid)
                if h:
                    ntdll.NtSuspendProcess(h)
                    kernel32.CloseHandle(h)
            h = kernel32.OpenProcess(0x1F0FFF, False, pid)
            if h:
                ntdll.NtSuspendProcess(h)
                kernel32.CloseHandle(h)
        except Exception:
            pass

    def _resume_process(self, pid):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            h = kernel32.OpenProcess(0x1F0FFF, False, pid)
            if h:
                ntdll.NtResumeProcess(h)
                kernel32.CloseHandle(h)
            result = subprocess.run(
                ["wmic", "process", "where", f"(ParentProcessId={pid})", "get", "ProcessId"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=3,
            )
            child_pids = [int(x.strip()) for x in result.stdout.split() if x.strip().isdigit()]
            for cpid in child_pids:
                h = kernel32.OpenProcess(0x1F0FFF, False, cpid)
                if h:
                    ntdll.NtResumeProcess(h)
                    kernel32.CloseHandle(h)
        except Exception:
            pass

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    _RE_DEST   = re.compile(r"\[download\] Destination:\s+(.+)")
    _RE_THUMB  = re.compile(r"\[info\] (?:Writing|Downloading) video thumbnail \S+ to:\s+(.+)")
    _RE_THUMB2 = re.compile(r'\[ThumbnailsConvertor\] Converting thumbnail "(.+?)" to ')

    def _run_one(self, args):
        """Lance yt-dlp pour une commande, retourne (returncode, output_lines)."""
        lines = []
        try:
            self._process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
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
            return self._process.returncode, lines
        except Exception as e:
            self.after(0, lambda e=e: self._log(f"Erreur : {e}", "#f66"))
            return -1, lines

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

        browser = self.var_g_browser.get() if hasattr(self, "var_g_browser") else "Désactivé"
        cookie_args = ["--cookies-from-browser", browser] if browser != "Désactivé" else []

        def probe_one(lang):
            try:
                r = subprocess.run(
                    [YTDLP, "-f", f"bestaudio[language^={lang}]",
                     "--simulate", "--no-warnings", "--no-playlist"]
                    + cookie_args + ["--", vid_url],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW, timeout=20,
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
            if self._paused:
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
                self.after(0, lambda s=cmd_str: self._log("[relance ST] $ " + s, "#666"))
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
                    self.after(0, lambda s=cmd_str2: self._log("[relance] $ " + s, "#666"))
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
                    self.after(0, lambda s=cmd_sub: self._log("[ST] $ " + s, "#666"))
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

            # Attendre la fin du nettoyage avant de lancer la vidéo suivante
            if self._skip_flag.is_set():
                self.after(0, lambda: self.var_status.set(t("dlq.status_cleanup")))
                t = getattr(self, "_cleanup_thread", None)
                if t:
                    t.join()

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
    }
    @property
    def _STATUS_LABEL(self):
        return {
            "ok":     t("report.status_ok"),
            "ajusté": t("report.status_adjusted"),
            "erreur": t("report.status_error"),
        }

    def __init__(self, parent, report):
        super().__init__(parent)
        self.title(t("report.window_title"))
        self.resizable(True, True)
        self.minsize(560, 260)

        n_ok  = sum(1 for r in report if r["status"] == "ok")
        n_adj = sum(1 for r in report if r["status"] == "ajusté")
        n_err = sum(1 for r in report if r["status"] == "erreur")
        total = len(report)

        h = max(280, min(700, 100 + total * 36))
        self.geometry(f"680x{h}")

        # ── Résumé en haut ─────────────────────────────────────────
        frm_sum = ttk.Frame(self, padding=(12, 10, 12, 6))
        frm_sum.pack(fill="x")
        ttk.Label(frm_sum,
                  text=t("report.summary", total=total, n_ok=n_ok, n_adj=n_adj, n_err=n_err),
                  font=("Segoe UI", 10, "bold")).pack(side="left")

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
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

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
                     font=("Consolas", 9, "bold")).grid(row=0, column=0, padx=(8, 4), pady=4, sticky="w")

            title_text = r["title"][:72] + "…" if len(r["title"]) > 72 else r["title"]
            tk.Label(frm_row, text=title_text, fg="#d4d4d4", bg=bg,
                     anchor="w", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="ew", pady=4)

            if r["dropped"]:
                detail = t("report.tracks_ignored", liste=", ".join(r["dropped"]))
                tk.Label(frm_row, text=detail, fg="#888", bg=bg,
                         anchor="w", font=("Segoe UI", 8, "italic")).grid(
                    row=1, column=1, columnspan=2, sticky="w", padx=(0, 8), pady=(0, 4))

        # ── Bouton fermer ───────────────────────────────────────────
        frm_btn = ttk.Frame(self, padding=(8, 6))
        frm_btn.pack(fill="x")
        ttk.Button(frm_btn, text=t("report.btn_close"), command=self.destroy).pack(side="right", ipadx=10)


# ══════════════════════════════════════════════════════════════════
#  Widget multi-sélection avec popup modale
# ══════════════════════════════════════════════════════════════════
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
            pop.geometry(f"460x{h}+{x}+{y}")
            pop.minsize(280, 160)
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
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

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
        pop.geometry(f"520x480+{x}+{y}")
        pop.minsize(400, 300)

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
            canvas.bind("<MouseWheel>", lambda e, cv=canvas: cv.yview_scroll(-1*(e.delta//120), "units"))

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
                      foreground="#888", font=("Segoe UI", 8)
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
                               foreground="#888", font=("Segoe UI", 8))
        lbl_legend.pack(side="right", padx=4)


# ══════════════════════════════════════════════════════════════════
#  Inspecteur de playlist
# ══════════════════════════════════════════════════════════════════
class PlaylistInspectorWindow(tk.Toplevel):

    # Noms d'affichage des codes de langue
    # Couleurs de ligne selon disponibilité des langues choisies
    _BG_OK_EVEN  = "#2d2d2d"
    _BG_OK_ODD   = "#222222"
    _BG_WARN     = "#3a3010"   # langue secondaire/ST manquante
    _BG_ERROR    = "#4a1c1c"   # langue principale manquante

    def __init__(self, parent, url="", outdir=""):
        super().__init__(parent)
        self.title(t("insp.window_title"))
        self.geometry("1180x720")
        self.minsize(960, 520)
        self._stop_flag = threading.Event()
        self._rows = []
        self._log_visible = False
        self._dl_window = None   # fenêtre de téléchargement active
        self._build()
        # Charger le dernier navigateur depuis la config partagée
        cfg = load_config()
        if "browser" in cfg:
            self.var_g_browser.set(cfg["browser"])
        self._update_cookie_warn_insp()
        self.protocol("WM_DELETE_WINDOW", self._on_inspector_close)
        if url:
            self.var_url.set(url)
        if outdir:
            self.var_g_outdir.set(outdir)

    def _on_inspector_close(self):
        cfg = load_config()
        cfg["browser"] = self.var_g_browser.get()
        save_config(cfg)
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
        txt = tk.Text(frm, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
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
                  font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True, padx=(0, 6))
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

        # ── Règles globales ────────────────────────────────────────
        frm_g = ttk.LabelFrame(
            self, text=t("insp.rules_frame_label"),
            padding=8)
        frm_g.pack(fill="x", padx=8, pady=6)

        # Ligne 0 : qualité / audio / sous-titres / miniature / cookies
        ttk.Label(frm_g, text=t("insp.label_quality")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.var_g_quality = tk.StringVar(value="1080p")
        self._g_quality_combo = ttk.Combobox(
            frm_g, textvariable=self.var_g_quality,
            values=[t("opts.quality_best"), "2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"],
            state="readonly", width=12)
        self._g_quality_combo.grid(row=0, column=1, sticky="w", padx=(0, 8))

        self.var_g_audio_only = tk.BooleanVar(value=False)
        def _on_audio_only(*_):
            state = "disabled" if self.var_g_audio_only.get() else "readonly"
            self._g_quality_combo.configure(state=state)
        self.var_g_audio_only.trace_add("write", _on_audio_only)
        ttk.Checkbutton(frm_g, text=t("insp.chk_audio_only"),
                        variable=self.var_g_audio_only).grid(row=0, column=2, padx=(0, 12))

        ttk.Label(frm_g, text=t("insp.label_sub_fmt")).grid(row=0, column=3, sticky="w", padx=(0, 4))
        self.var_g_sub_fmt = tk.StringVar(value="srt")
        ttk.Combobox(frm_g, textvariable=self.var_g_sub_fmt, values=SUBTITLE_FORMATS,
                     state="readonly", width=6).grid(row=0, column=4, sticky="w", padx=(0, 10))

        self.var_g_embed_subs = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_g, text=t("insp.chk_embed_subs"),
                        variable=self.var_g_embed_subs).grid(row=0, column=5, padx=(0, 8))
        self.var_g_embed_thumb = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_g, text=t("insp.chk_embed_thumb"),
                        variable=self.var_g_embed_thumb).grid(row=0, column=6, padx=(0, 8))

        self.var_g_numbering = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_g, text=t("insp.chk_numbering"),
                        variable=self.var_g_numbering).grid(row=0, column=7, padx=(0, 8))

        self.var_g_smart_dir = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_g, text=t("insp.chk_smart_dir"),
                        variable=self.var_g_smart_dir).grid(row=0, column=8, padx=(0, 8))

        ttk.Label(frm_g, text=t("insp.label_cookies")).grid(row=0, column=9, sticky="w", padx=(8, 4))
        self.var_g_browser = tk.StringVar(value="Désactivé")
        ttk.Combobox(frm_g, textvariable=self.var_g_browser,
                     values=["Désactivé", "chrome", "firefox", "edge", "brave", "opera"],
                     state="readonly", width=10).grid(row=0, column=10, sticky="w")
        self.var_g_browser.trace_add("write", lambda *_: (
            self._on_browser_change(), self._update_cookie_warn_insp()))
        self._lbl_cookie_warn_insp = tk.Label(
            frm_g, text=t("insp.cookie_warn"),
            fg="#e74c3c", font=("Segoe UI", 8))
        self._lbl_cookie_warn_insp.grid(row=0, column=11, columnspan=2, sticky="w", padx=(10, 0))

        # Ligne 1 : sélection des langues
        ttk.Label(frm_g, text=t("insp.label_primary_lang")).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=(8, 0))
        _g_opt_default  = t("insp.primary_default")
        _g_opt_no_audio = t("insp.primary_no_audio")
        _g_opt_manual   = t("insp.primary_manual")
        self.var_g_primary_lbl = tk.StringVar(value=_g_opt_default)
        self._g_primary_combo = ttk.Combobox(
            frm_g, textvariable=self.var_g_primary_lbl,
            values=[_g_opt_default, _g_opt_no_audio, _g_opt_manual],
            state="readonly", width=26)
        self._g_primary_combo.grid(row=1, column=1, columnspan=2, sticky="w",
                                   pady=(8, 0), padx=(0, 14))
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

        ttk.Label(frm_g, text=t("insp.label_secondary_audio")).grid(
            row=1, column=3, sticky="w", padx=(0, 4), pady=(8, 0))
        self._g_secondary = MultiCheckSelect(
            frm_g, placeholder=t("opts.placeholder_disabled"), width=28,
            on_change=self._refresh_colors)
        self._g_secondary.grid(row=1, column=4, columnspan=2, sticky="w",
                               pady=(8, 0), padx=(0, 12))

        ttk.Label(frm_g, text=t("insp.label_subs")).grid(
            row=1, column=6, sticky="w", padx=(0, 4), pady=(8, 0))
        self._g_subs = MultiCheckSelect(
            frm_g, placeholder=t("opts.placeholder_disabled"), width=26,
            on_change=self._refresh_colors)
        self._g_subs.grid(row=1, column=7, columnspan=2, sticky="w", pady=(8, 0))

        # Ligne 2 : blocs de script
        ttk.Label(frm_g, text=t("insp.label_blocks")).grid(
            row=2, column=0, sticky="w", padx=(0, 4), pady=(8, 0))
        self._g_blocks = MultiCheckSelect(
            frm_g, placeholder=t("opts.placeholder_disabled"), width=32,
            tabs=_translated_blocks_tabs())
        self._g_blocks.grid(row=2, column=1, columnspan=4, sticky="w", pady=(8, 0))

        # Avertissement miniature MKV (visible seulement si secondary + embed_thumb)
        self._lbl_mkv_warn = ttk.Label(
            frm_g, text=t("insp.mkv_warn"),
            foreground="#e67e22", font=("Segoe UI", 8), wraplength=600)
        self._lbl_mkv_warn.grid(row=2, column=5, columnspan=4, sticky="w", pady=(8, 0))
        self._lbl_mkv_warn.grid_remove()

        # Ligne 3 : dossier
        ttk.Label(frm_g, text=t("insp.label_outdir")).grid(
            row=3, column=0, sticky="w", padx=(0, 4), pady=(6, 0))
        self.var_g_outdir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Entry(frm_g, textvariable=self.var_g_outdir, width=54).grid(
            row=3, column=1, columnspan=7, sticky="ew", pady=(6, 0))
        ttk.Button(frm_g, text=t("insp.btn_browse"), width=3,
                   command=self._browse_out).grid(row=3, column=8, pady=(6, 0))

        # Légende couleurs
        frm_legend = ttk.Frame(self)
        frm_legend.pack(fill="x", padx=8, pady=(0, 2))
        for bg, txt in [(self._BG_ERROR, t("insp.legend_primary_missing")),
                        (self._BG_WARN,  t("insp.legend_secondary_missing")),
                        (self._BG_OK_EVEN, t("insp.legend_ok"))]:
            tk.Label(frm_legend, text=f"  {txt}  ", bg=bg, fg="#d4d4d4",
                     font=("Segoe UI", 8), relief="flat").pack(side="left", padx=(0, 6))

        # ── En-tête grille ─────────────────────────────────────────
        frm_head = tk.Frame(self, bg="#333")
        frm_head.pack(fill="x", padx=8)
        for text, w in [("", 3), (t("insp.grid_col_num"), 3), (t("insp.grid_col_title"), 36), (t("insp.grid_col_audio"), 20),
                        (t("insp.grid_col_subs"), 16), (t("insp.grid_col_primary"), 16),
                        (t("insp.grid_col_secondary"), 22), (t("insp.grid_col_subs_override"), 20)]:
            tk.Label(frm_head, text=text, bg="#333", fg="#aaa",
                     font=("Segoe UI", 8, "bold"),
                     width=w, anchor="w").pack(side="left", padx=3, pady=3)

        # ── Zone scrollable ────────────────────────────────────────
        frm_cv = ttk.Frame(self)
        frm_cv.pack(fill="both", expand=True, padx=8)
        self._canvas = tk.Canvas(frm_cv, bg="#252525", highlightthickness=0)
        vsb = ttk.Scrollbar(frm_cv, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._inner = tk.Frame(self._canvas, bg="#252525")
        self._cwin = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>",
                         lambda _: self._canvas.configure(
                             scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._cwin, width=e.width))
        self._canvas.bind("<MouseWheel>",
                          lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

        # ── Panneau de log (caché par défaut) ─────────────────────
        self._log_frame = ttk.LabelFrame(self, text=" Journal de debug ", padding=4)
        # Pas de pack() ici — _toggle_log le gère
        self._log_text = tk.Text(self._log_frame, height=6, state="disabled",
                                 font=("Consolas", 8), bg="#1e1e1e", fg="#d4d4d4",
                                 wrap="word", relief="flat")
        log_vsb = ttk.Scrollbar(self._log_frame, orient="vertical",
                                command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=log_vsb.set)
        log_vsb.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)

        # ── Barre d'état + pied ────────────────────────────────────
        self.var_status = tk.StringVar(value=t("insp.status_initial"))
        ttk.Label(self, textvariable=self.var_status, anchor="w",
                  font=("Segoe UI", 9)).pack(fill="x", padx=8, pady=(4, 0))

        frm_foot = ttk.Frame(self, padding=(8, 4, 8, 8))
        frm_foot.pack(fill="x")
        ttk.Button(frm_foot, text=t("insp.btn_select_all"),
                   command=lambda: self._select_all(True)).pack(side="left", ipadx=6)
        ttk.Button(frm_foot, text=t("insp.btn_deselect_all"),
                   command=lambda: self._select_all(False)).pack(
            side="left", padx=(6, 0), ipadx=6)
        self.var_dl_lbl = tk.StringVar(value=t("insp.btn_download_sel"))
        self.btn_dl = ttk.Button(frm_foot, textvariable=self.var_dl_lbl,
                                 command=self._download_selection, state="disabled")
        self.btn_dl.pack(side="right", ipadx=10, ipady=4)

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
        lb = tk.Listbox(lb_frame, font=("Segoe UI", 9), activestyle="dotbox",
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
        if has_secondary and embed_thumb:
            self._lbl_mkv_warn.grid()
        else:
            self._lbl_mkv_warn.grid_remove()

    # ── Analyse ────────────────────────────────────────────────────
    def _analyze(self):
        url = self.var_url.get().strip()
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
            self.after(0, lambda m=msg: self.var_status.set(
                f"Erreur inattendue — voir console : {e}"))
            print(msg)
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            self.after(0, lambda: self.btn_stop_an.configure(state="disabled"))

    def _run_analyze_impl(self, url):
        # Étape 1 : liste plate
        try:
            result = subprocess.run(
                [YTDLP, "--flat-playlist", "-j", "--no-warnings", "--", url],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=120,
            )
            lines = [l for l in result.stdout.splitlines() if l.strip()]
        except Exception as e:
            self.after(0, lambda: self.var_status.set(f"Erreur liste plate : {e}"))
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            return

        videos = []
        for line in lines:
            try:
                info = json.loads(line)
                videos.append({"id": info.get("id", ""),
                               "title": info.get("title", info.get("id", "?"))})
            except Exception:
                continue

        if not videos:
            self.after(0, lambda: self.var_status.set(t("insp.status_no_videos")))
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))
            return

        n = len(videos)
        # Étape 2 : inspection de chaque vidéo
        for i, vid in enumerate(videos):
            if self._stop_flag.is_set():
                break
            self.after(0, lambda ix=i, tot=n:
                       self.var_status.set(t("insp.status_inspecting", ix=ix+1, tot=tot)))

            audio_langs, sub_langs, auto_only_subs = set(), set(), set()
            vid_url = f"https://www.youtube.com/watch?v={vid['id']}"

            # Cookies optionnels pour accéder aux pistes doublées
            browser = self.var_g_browser.get()
            cookie_args = ["--cookies-from-browser", browser] \
                          if browser != "Désactivé" else []

            # Appel yt-dlp -j avec le client par défaut (yt-dlp choisit ios/tv_embedded)
            try:
                r = subprocess.run(
                    [YTDLP, "-j", "--no-warnings", "--no-playlist"] + cookie_args + ["--", vid_url],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW, timeout=45,
                )
                rc = r.returncode
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
                        creationflags=subprocess.CREATE_NO_WINDOW, timeout=30,
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
                    self.var_status.set(f"Erreur ligne {ix+1} : {e}")
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
        return self.var_g_browser.get() not in ("", "Désactivé")

    def _update_cookie_warn_insp(self):
        if self.var_g_browser.get() == "Désactivé":
            self._lbl_cookie_warn_insp.grid()
        else:
            self._lbl_cookie_warn_insp.grid_remove()

    def _on_browser_change(self):
        """Rafraîchit les widgets de langue/audio quand le navigateur (cookie) change."""
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
                 fg="#888", font=("Consolas", 9)).pack(side="left", padx=3)

        # Titre (tronqué)
        title = vid["title"]
        disp = (title[:38] + "…") if len(title) > 38 else title
        tk.Label(frm, text=disp, width=38, anchor="w", bg=bg,
                 fg="#d4d4d4", font=("Segoe UI", 9)).pack(side="left", padx=4)

        # Audio dispo (résumé)
        audio_str = " ".join(l.upper() for l in vid["audio_langs"][:8]) or "?"
        tk.Label(frm, text=audio_str, width=20, anchor="w", bg=bg,
                 fg="#9cdcfe", font=("Consolas", 8)).pack(side="left", padx=2)

        # ST dispo (résumé)
        _ao = set(vid.get("auto_only_subs", []))
        sub_str = " ".join(
            f"[{l.upper()}]" if l in _ao else l.upper()
            for l in vid["sub_langs"][:8]
        ) or "—"
        tk.Label(frm, text=sub_str, width=16, anchor="w", bg=bg,
                 fg="#ce9178", font=("Consolas", 8)).pack(side="left", padx=2)

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
                args += ["--embed-subs"]
            else:
                args += ["--write-subs"]
            if has_auto:
                args += ["--write-auto-subs", "--sleep-requests", "4"]
            args += ["--retries", "10", "--fragment-retries", "10",
                     "--sleep-interval", "3", "--max-sleep-interval", "8"]
            browser = self.var_g_browser.get()
            if browser != "Désactivé":
                args += ["--cookies-from-browser", browser]
            out = self.var_g_outdir.get().strip()
            if out:
                args += ["-o", os.path.join(out, "%(title)s.%(ext)s")]
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
                        "--audio-multistreams", "--merge-output-format", "mkv"]
            else:
                # Piste unique → MP3
                if primary_audio:
                    fmt = f"bestaudio[language^={primary_audio}]/bestaudio/best"
                else:
                    fmt = "bestaudio/best"
                args = [YTDLP, "-f", fmt,
                        "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
        else:
            # ── Construction du format selon les langues ────────────
            prim_lbl = row["var_primary"].get()
            if prim_lbl == self._g_opt_row_default:
                primary = self._global_primary()
            elif prim_lbl == self._g_opt_no_audio:
                primary = "__video_only__"
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
                args += ["--audio-multistreams", "--merge-output-format", "mkv"]
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
                args += ["--embed-subs"]
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
        if browser != "Désactivé":
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
            args += ["-o", unique_path]
        elif outdir:
            args += ["-o", os.path.join(outdir, f"{prefix}%(title)s.%(ext)s")]
        elif prefix:
            args += ["-o", f"{prefix}%(title)s.%(ext)s"]

        if self.var_g_smart_dir.get() and outdir:
            archive_path = os.path.join(outdir, ".yt-dlp-archive.txt")
            args += ["--download-archive", archive_path]

        args += ["--progress", "--newline", "--", vid_url]
        return args

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
        self.btn_dl.configure(state="disabled")
        win = DownloadQueueWindow(self, selected, self._build_video_args, inspector=self)
        self._dl_window = win

        def _on_dl_closed(event=None):
            if event is not None and event.widget is not win:
                return
            self._dl_window = None
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
class YtDlpGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("app.window_title"))
        self.resizable(True, True)
        self.minsize(680, 620)
        self._process = None
        self._paused = False
        self._queue_running = False
        self._queue_index = -1
        self._queue_end_index = -1
        self._queue_skip = False
        self._config = load_config()
        self._queue = load_queue()
        self._build_ui()
        self._restore_config()
        self._refresh_queue_tv()
        # Résoudre les titres manquants des entrées chargées depuis le disque
        for i, e in enumerate(self._queue):
            if not e.get("title") and e.get("status") == "pending":
                threading.Thread(target=self._queue_fetch_title, args=(i,), daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Rend visibles les exceptions silencieuses dans les callbacks tkinter
        self.report_callback_exception = self._on_tk_error

    def _on_tk_error(self, exc, val, tb):
        import traceback
        msg = "".join(traceback.format_exception(exc, val, tb))
        print(msg)  # console si lancé en python (pas pythonw)
        messagebox.showerror(t("app.error_internal_title"), t("app.error_internal_msg", exc_name=exc.__name__, val=val), parent=self)

    # ──────────────────────────────────────────────
    #  Construction de l'interface
    # ──────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=10, pady=5)

        # ── Barre d'outils (haut) ──────────────────
        frm_toolbar = ttk.Frame(self)
        frm_toolbar.pack(fill="x", padx=10, pady=(8, 0))

        # Indicateur de dépendances manquantes
        self.var_dep_warn = tk.StringVar()
        self._lbl_dep_warn = ttk.Label(
            frm_toolbar, textvariable=self.var_dep_warn,
            foreground="#e67e22", font=("Segoe UI", 9)
        )
        self._lbl_dep_warn.pack(side="left")

        ttk.Button(
            frm_toolbar, text=t("toolbar.btn_donate"),
            command=lambda: __import__("webbrowser").open(
                "https://ko-fi.com/harlocksuites")
        ).pack(side="right")
        ttk.Button(
            frm_toolbar, text=t("toolbar.btn_options"),
            command=self._open_options_menu
        ).pack(side="right", padx=(0, 6))

        self._check_deps_quick()

        # ── URL ────────────────────────────────────
        frm_url = ttk.LabelFrame(self, text=t("url.frame_label"), padding=8)
        frm_url.pack(fill="x", **pad)

        self.var_url = tk.StringVar()
        ent_url = ttk.Entry(frm_url, textvariable=self.var_url, font=("Segoe UI", 10))
        ent_url.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frm_url, text=t("url.btn_paste"), command=self._paste_url).pack(side="left")
        ttk.Button(frm_url, text=t("url.btn_inspect"), command=self._inspect).pack(side="left", padx=(4, 0))
        ttk.Button(frm_url, text=t("url.btn_playlist_advanced"),
                   command=self._open_playlist_inspector).pack(side="left", padx=(4, 0))

        # ── Dossier de destination ──────────────────
        frm_out = ttk.LabelFrame(self, text=t("opts.outdir_frame_label"), padding=8)
        frm_out.pack(fill="x", **pad)

        self.var_outdir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ent_out = ttk.Entry(frm_out, textvariable=self.var_outdir, font=("Segoe UI", 10))
        ent_out.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frm_out, text=t("opts.outdir_browse"), command=self._browse_dir).pack(side="left")

        # ── Options de téléchargement ───────────────
        frm_opts = ttk.LabelFrame(self, text=t("opts.frame_label"), padding=8)
        frm_opts.pack(fill="x", **pad)

        # Ligne 0 : qualité / audio seulement / ST / miniature / cookies
        ttk.Label(frm_opts, text=t("opts.label_quality")).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.var_quality = tk.StringVar(value="1080p")
        self._quality_combo = ttk.Combobox(
            frm_opts, textvariable=self.var_quality,
            values=[t("opts.quality_best"), "2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"],
            state="readonly", width=12)
        self._quality_combo.grid(row=0, column=1, sticky="w", padx=(0, 8))

        self.var_audio_only = tk.BooleanVar(value=False)
        def _on_audio_only_main(*_):
            self._quality_combo.configure(
                state="disabled" if self.var_audio_only.get() else "readonly")
            self._update_cmd()
        self.var_audio_only.trace_add("write", _on_audio_only_main)
        ttk.Checkbutton(frm_opts, text=t("opts.chk_audio_only"),
                        variable=self.var_audio_only).grid(row=0, column=2, padx=(0, 12))

        ttk.Label(frm_opts, text=t("opts.label_sub_fmt")).grid(row=0, column=3, sticky="w", padx=(0, 4))
        self.var_sub_fmt = tk.StringVar(value="srt")
        ttk.Combobox(frm_opts, textvariable=self.var_sub_fmt, values=SUBTITLE_FORMATS,
                     state="readonly", width=6).grid(row=0, column=4, sticky="w", padx=(0, 10))

        self.var_embed_subs = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_opts, text=t("opts.chk_embed_subs"),
                        variable=self.var_embed_subs).grid(row=0, column=5, padx=(0, 8))

        self.var_embed_thumb = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_opts, text=t("opts.chk_embed_thumb"),
                        variable=self.var_embed_thumb).grid(row=0, column=6, padx=(0, 8))

        ttk.Label(frm_opts, text=t("opts.label_cookies")).grid(row=0, column=7, sticky="w", padx=(6, 4))
        self.var_browser = tk.StringVar(value="Désactivé")
        ttk.Combobox(frm_opts, textvariable=self.var_browser,
                     values=["Désactivé", "chrome", "firefox", "edge", "brave", "opera"],
                     state="readonly", width=10).grid(row=0, column=8, sticky="w")
        self._lbl_cookie_warn_main = tk.Label(
            frm_opts,
            text=t("opts.cookie_warn"),
            fg="#e74c3c", font=("Segoe UI", 8))
        self._lbl_cookie_warn_main.grid(row=0, column=9, columnspan=2, sticky="w", padx=(10, 0))
        self.var_browser.trace_add("write", lambda *_: (
            self._update_cookie_warn_main(), self._update_cmd()))

        # Ligne 1 : langues
        ttk.Label(frm_opts, text=t("opts.label_primary_lang")).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=(8, 0))
        self._opt_primary_default  = t("opts.primary_lang_default")
        self._opt_primary_no_audio = t("opts.primary_lang_no_audio")
        self._opt_primary_manual   = t("opts.primary_lang_manual")
        self.var_primary_lbl = tk.StringVar(value=self._opt_primary_default)
        self._primary_combo = ttk.Combobox(
            frm_opts, textvariable=self.var_primary_lbl,
            values=[self._opt_primary_default, self._opt_primary_no_audio, self._opt_primary_manual],
            state="readonly", width=26)
        self._primary_combo.grid(row=1, column=1, columnspan=2, sticky="w",
                                 pady=(8, 0), padx=(0, 14))
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

        ttk.Label(frm_opts, text=t("opts.label_secondary_audio")).grid(
            row=1, column=3, sticky="w", padx=(0, 4), pady=(8, 0))
        self._secondary_sel = MultiCheckSelect(
            frm_opts, placeholder=t("opts.placeholder_disabled"), width=28,
            on_change=self._update_cmd)
        self._secondary_sel.set_options(
            [(_c, _tblklbl(_c, _l)) for _c, _l in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])])
        self._secondary_sel.grid(row=1, column=4, columnspan=2, sticky="w",
                                 pady=(8, 0), padx=(0, 12))

        ttk.Label(frm_opts, text=t("opts.label_subs")).grid(
            row=1, column=6, sticky="w", padx=(0, 4), pady=(8, 0))
        self._subs_sel = MultiCheckSelect(
            frm_opts, placeholder=t("opts.placeholder_disabled"), width=22,
            on_change=self._update_cmd)
        self._subs_sel.set_options(
            [(_c, _tblklbl(_c, _l)) for _c, _l in SCRIPT_BLOCKS_BY_TAB.get("Langue", [])])
        self._subs_sel.grid(row=1, column=7, columnspan=3, sticky="w", pady=(8, 0))

        # Avertissement miniature MKV
        self._lbl_mkv_warn_main = ttk.Label(
            frm_opts, text=t("opts.mkv_warn"),
            foreground="#e67e22", font=("Segoe UI", 8), wraplength=500)
        self._lbl_mkv_warn_main.grid(row=1, column=9, columnspan=2, sticky="w", pady=(8, 0))
        self._lbl_mkv_warn_main.grid_remove()

        # Ligne 2 : blocs de script
        ttk.Label(frm_opts, text=t("opts.label_blocks")).grid(
            row=2, column=0, sticky="w", padx=(0, 4), pady=(8, 0))
        self._blocks_sel = MultiCheckSelect(
            frm_opts, placeholder=t("opts.placeholder_disabled"), width=32,
            tabs=_translated_blocks_tabs(), on_change=self._update_cmd)
        self._blocks_sel.grid(row=2, column=1, columnspan=5, sticky="w", pady=(8, 0))

        # Trace mise à jour commande
        for _v in (self.var_quality, self.var_sub_fmt, self.var_embed_subs,
                   self.var_embed_thumb, self.var_audio_only):
            _v.trace_add("write", lambda *_: self._update_cmd())

        # ── Commande générée ───────────────────────
        frm_cmd = ttk.LabelFrame(self, text=t("opts.cmd_frame_label"), padding=8)
        frm_cmd.pack(fill="x", **pad)

        self.var_cmd = tk.StringVar()
        ttk.Entry(frm_cmd, textvariable=self.var_cmd, font=("Consolas", 9),
                  state="readonly").pack(fill="x")

        for _v in (self.var_url, self.var_outdir):
            _v.trace_add("write", lambda *_: self._update_cmd())

        # ── Boutons ────────────────────────────────
        frm_btn = ttk.Frame(self)
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
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        frm_queue = ttk.LabelFrame(paned, text=t("queue.frame_label"), padding=6)
        paned.add(frm_queue, weight=1)

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
        self._tv_queue.tag_configure("pending", foreground="#d4d4d4")
        self._tv_queue.tag_configure("running", foreground="#3498db")
        self._tv_queue.tag_configure("error",   foreground="#e74c3c")
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

        # ── Progression ────────────────────────────
        self.var_progress = tk.DoubleVar(value=0)
        ttk.Progressbar(self, variable=self.var_progress,
                        maximum=100, mode="determinate").pack(fill="x", padx=10, pady=(0, 4))

        self.var_status = tk.StringVar(value=t("app.status_ready"))
        ttk.Label(self, textvariable=self.var_status, anchor="w",
                  font=("Segoe UI", 9)).pack(fill="x", padx=10)

        # ── Journal ────────────────────────────────
        frm_log = ttk.LabelFrame(paned, text=" Journal ", padding=6)
        paned.add(frm_log, weight=2)

        self.log_text = tk.Text(frm_log, wrap="word", height=10,
                                font=("Consolas", 9), state="disabled",
                                bg="#1e1e1e", fg="#d4d4d4",
                                insertbackground="white")
        sb = ttk.Scrollbar(frm_log, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        self._update_cmd()

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
                    t("app.dep_warn_required", liste=', '.join(missing))
                )
            else:
                self.var_dep_warn.set(
                    t("app.dep_warn_optional", liste=', '.join(missing))
                )
        else:
            self.var_dep_warn.set(t("app.dep_ok"))
            self._lbl_dep_warn.configure(foreground="#27ae60")

    def _open_options_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=t("toolbar.menu_update"), command=self._open_update)
        menu.add_command(label=t("toolbar.menu_deps"),   command=self._open_deps)
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

        tk.Label(dlg, text="Langue / Language", font=("Segoe UI", 11, "bold")).pack(pady=(14, 6), padx=20)

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
        _new_path = _pathlib.Path(__file__).parent / "lang" / f"{new_code}.json"
        if _new_path.exists():
            with open(_new_path, encoding="utf-8") as _f:
                _new_strings = _json.load(_f)
        _en_path = _pathlib.Path(__file__).parent / "lang" / "en.json"
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

        tk.Label(dlg, text=new_name, font=("Segoe UI", 12, "bold")).pack(pady=(14, 2), padx=24)
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
            subprocess.Popen([sys.executable] + sys.argv)
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

    def _open_playlist_inspector(self):
        url = self.var_url.get().strip()
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
                return os.path.normpath(os.path.join(outdir, f"{candidate}.%(ext)s"))
            n += 1

    def _build_args(self):
        url = self.var_url.get().strip()
        secondary = []
        force_mp4 = False

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
                        "--audio-multistreams", "--merge-output-format", "mkv"]
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

            embed_thumb = self.var_embed_thumb.get()
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
                args += ["--audio-multistreams", "--merge-output-format", "mkv"]
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
                args += ["--embed-subs"]
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
        if browser and browser != "Désactivé":
            args += ["--cookies-from-browser", browser]

        out = self.var_outdir.get().strip()
        if out:
            cur_url = self.var_url.get().strip()
            insp_url = getattr(self, "_inspected_url", "")
            known_title = getattr(self, "_inspected_title", "") if cur_url == insp_url else ""
            unique = self._unique_output_path(out, known_title) if known_title else None
            args += ["-o", unique if unique else os.path.join(out, "%(title)s.%(ext)s")]

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
        if has_secondary and embed_thumb:
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
    def _inspect(self):
        url = self.var_url.get().strip()
        if not url:
            messagebox.showwarning(t("url.warn_missing_title"), t("url.warn_missing_msg"))
            return
        self._clear_log()
        self._log(f"Inspection : {url}", "info")

        browser = self.var_browser.get()
        cookie_args = ["--cookies-from-browser", browser] if browser != "Désactivé" else []

        def run():
            try:
                result = subprocess.run(
                    [YTDLP, "-j", "--no-playlist"] + cookie_args + ["--", url],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=os.path.dirname(YTDLP),
                )
                if result.returncode != 0:
                    for line in result.stderr.splitlines():
                        self.after(0, self._log, line)
                    return
                try:
                    info = json.loads(result.stdout)
                except Exception:
                    self.after(0, self._log, "Erreur : réponse JSON invalide", "error")
                    return

                title = info.get("title", "?")
                self._inspected_title = title   # mémorisé pour la déduplication
                self._inspected_url   = url
                duration = info.get("duration_string", "")
                uploader = info.get("uploader", "")
                self.after(0, self._log, f"Titre    : {title}", "info")
                self.after(0, self._log, f"Durée    : {duration}   Chaîne : {uploader}", "info")

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
                            creationflags=subprocess.CREATE_NO_WINDOW,
                            cwd=os.path.dirname(YTDLP),
                        )
                        for line in r2.stdout.splitlines():
                            for m in re.findall(r'\[([a-z]{2,4})\]', line):
                                if m != "und":
                                    audio_langs.add(m)
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
                    self._log(f"Pistes audio : {', '.join(audio_langs) or 'aucune'}", "info")
                    sub_info = ', '.join(all_sub_langs) or 'aucune'
                    auto_info = f" (auto : {', '.join(sorted(auto_only))})" if auto_only else ""
                    self._log(f"Sous-titres : {sub_info}{auto_info}", "info")

                self.after(0, _populate)

                self.after(0, self._log, "", None)
                # Afficher aussi les formats (-F) pour info
                proc2 = subprocess.Popen(
                    [YTDLP, "-F", "--no-playlist"] + cookie_args + ["--", url],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=os.path.dirname(YTDLP),
                )
                for line in proc2.stdout:
                    self.after(0, self._log, line.rstrip())
                proc2.wait()

            except Exception as e:
                self.after(0, self._log, f"Erreur : {e}", "error")

        threading.Thread(target=run, daemon=True).start()

    # ──────────────────────────────────────────────
    #  Téléchargement
    # ──────────────────────────────────────────────
    def _download(self):
        url = self.var_url.get().strip()
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
        self.var_progress.set(0)
        self.var_status.set(t("app.status_starting"))
        self._clear_log()
        self._log("$ " + " ".join(f'"{a}"' if " " in a else a for a in args), "cmd")

        def run():
            try:
                self._process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=os.path.dirname(YTDLP),
                )
                for line in self._process.stdout:
                    self.after(0, self._on_output_line, line.rstrip())
                self._process.wait()
                self.after(0, self._on_done, self._process.returncode == 0)
            except Exception as e:
                self.after(0, self._log, f"Erreur : {e}")
                self.after(0, self._on_done, False)
            finally:
                self._process = None

        threading.Thread(target=run, daemon=True).start()

    _RE_PROGRESS = re.compile(r"\[download\]\s+([\d.]+)%")
    _RE_DEST     = re.compile(r"\[download\] Destination:\s+(.+)")
    _RE_THUMB    = re.compile(r"\[info\] (?:Writing|Downloading) video thumbnail \S+ to:\s+(.+)")
    _RE_THUMB2   = re.compile(r'\[ThumbnailsConvertor\] Converting thumbnail "(.+?)" to ')

    def _on_output_line(self, line):
        self._log(line)
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

    def _on_done(self, success):
        self.btn_dl.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_pause.configure(state="disabled", text=t("dl.btn_pause"))
        self._paused = False
        if success:
            self.var_progress.set(100)
            self.var_status.set(t("app.status_done_ok"))
            self._log(t("app.log_done"), "ok")
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

    def _stop(self):
        if self._queue_running:
            self._queue_running = False
            self._queue_skip = False
            self._queue_set_running_ui(False)
        if self._process:
            if self._paused:
                self._resume_process(self._process.pid)
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self._process.pid)],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=5,
                )
            except Exception:
                self._process.terminate()
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
        if browser and browser != "Désactivé":
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
        cookie_args = ["--cookies-from-browser", browser] if browser != "Désactivé" else []
        try:
            r = subprocess.run(
                [YTDLP, "--get-title", "--no-playlist"] + cookie_args + ["--", url],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
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
        url = self.var_url.get().strip()
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
                    outdir = os.path.dirname(args[i + 1])
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
        self._queue_skip = True


        if self._process:
            if self._paused:
                self._resume_process(self._process.pid)
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self._process.pid)],
                    creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            except Exception:
                self._process.terminate()
        else:
            # Pas de processus actif (cas rare), avancer manuellement
            self._queue_skip = False
            self._queue_index += 1
            self._queue_run_next()

        self._cleanup_partial_files()

    def _queue_stop(self):
        if not self._queue_running:
            return
        self._queue_running = False
        self._queue_skip = False
        self._queue_set_running_ui(False)
        if self._process:
            if self._paused:
                self._resume_process(self._process.pid)
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self._process.pid)],
                    creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            except Exception:
                self._process.terminate()
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
                            _try_remove(os.path.join(d, fname))
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
                        _try_remove(os.path.join(d, fname))
                    elif fext.lower() == ext_lower + ".part" and _norm(fstem) == stem_norm:
                        _try_remove(os.path.join(d, fname))
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
                        _try_remove(f)

        threading.Thread(target=_do_cleanup, args=(files,), daemon=True).start()

    def _update_cookie_warn_main(self):
        if self.var_browser.get() == "Désactivé":
            self._lbl_cookie_warn_main.grid()
        else:
            self._lbl_cookie_warn_main.grid_remove()

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
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            # Suspendre les processus enfants (ex. ffmpeg, aria2c) puis le parent
            result = subprocess.run(
                ["wmic", "process", "where", f"(ParentProcessId={pid})", "get", "ProcessId"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=3,
            )
            child_pids = [int(x.strip()) for x in result.stdout.split() if x.strip().isdigit()]
            for cpid in child_pids:
                h = kernel32.OpenProcess(0x1F0FFF, False, cpid)
                if h:
                    ntdll.NtSuspendProcess(h)
                    kernel32.CloseHandle(h)
            h = kernel32.OpenProcess(0x1F0FFF, False, pid)
            if h:
                ntdll.NtSuspendProcess(h)
                kernel32.CloseHandle(h)
        except Exception:
            pass

    def _resume_process(self, pid):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            # Reprendre le parent en premier, puis les enfants
            h = kernel32.OpenProcess(0x1F0FFF, False, pid)
            if h:
                ntdll.NtResumeProcess(h)
                kernel32.CloseHandle(h)
            result = subprocess.run(
                ["wmic", "process", "where", f"(ParentProcessId={pid})", "get", "ProcessId"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=3,
            )
            child_pids = [int(x.strip()) for x in result.stdout.split() if x.strip().isdigit()]
            for cpid in child_pids:
                h = kernel32.OpenProcess(0x1F0FFF, False, cpid)
                if h:
                    ntdll.NtResumeProcess(h)
                    kernel32.CloseHandle(h)
        except Exception:
            pass

    # ──────────────────────────────────────────────
    #  Persistance
    # ──────────────────────────────────────────────
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

    def _on_close(self):
        save_config({
            "outdir":      self.var_outdir.get(),
            "quality":     self.var_quality.get(),
            "audio_only":  self.var_audio_only.get(),
            "sub_fmt":     self.var_sub_fmt.get(),
            "embed_subs":  self.var_embed_subs.get(),
            "embed_thumb": self.var_embed_thumb.get(),
            "browser":     self.var_browser.get(),
        })
        self.destroy()


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
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
        ttk.Style().theme_use("vista")
    except Exception:
        pass

    app.mainloop()
