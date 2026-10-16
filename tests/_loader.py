"""Charge yt-dlp-gui.pyw comme module, avec une config isolée (jamais celle de l'utilisateur)."""
import importlib.util
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SESSION_DIR = tempfile.mkdtemp(prefix="ytgui-tests-")


def load_gui():
    if "ytgui" in sys.modules:
        return sys.modules["ytgui"]
    spec = importlib.util.spec_from_file_location("ytgui", os.path.join(ROOT, "yt-dlp-gui.pyw"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["ytgui"] = m
    spec.loader.exec_module(m)
    m.CONFIG_FILE = os.path.join(_SESSION_DIR, "gui-config.json")
    m.QUEUE_FILE = os.path.join(_SESSION_DIR, "download-queue.json")
    m.CUSTOM_BLOCKS_FILE = os.path.join(_SESSION_DIR, "custom-blocks.json")
    m.load_lang("fr")
    m.YtDlpGui.AUTO_SETUP = False
    m.YtDlpGui.AUTO_UPDATE_CHECK = False
    return m


def tk_available():
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        return False
