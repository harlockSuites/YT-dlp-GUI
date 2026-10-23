"""Construit les paquets Linux (PyInstaller) : archive .tar.gz et AppImage.

Usage (depuis la racine du dépôt, sous Linux) :
    python3 packaging/build_linux.py                   # tout
    python3 packaging/build_linux.py --skip-appimage   # dossier PyInstaller + archive seulement
    python3 packaging/build_linux.py --skip-tarball

Résultats dans dist/ :
    yt-dlp-gui-linux-<version>-<arch>.tar.gz   archive à extraire ; lancer ./yt-dlp-gui/yt-dlp-gui
    yt-dlp-gui-<version>-<arch>.AppImage       fichier unique à rendre exécutable

Les données (réglages, yt-dlp, ffmpeg…) vont dans $XDG_DATA_HOME/yt-dlp-GUI (par défaut ~/.local/share/yt-dlp-GUI),
sauf si un fichier « portable.flag » est placé à côté de l'exécutable de l'archive.
Pour la meilleure compatibilité, construire sur la plus ancienne distribution prise en charge (la glibc de la
machine de construction est le minimum exigé des machines qui l'exécutent).
"""
import argparse
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
WORK = os.path.join(ROOT, "build")
APP_DIST = os.path.join(DIST, "yt-dlp-gui")
SCRIPT = os.path.join(ROOT, "yt-dlp-gui.pyw")
ICON_PNG = os.path.join(ROOT, "assets", "yt-dlp-gui.png")
LINUX_FILES = os.path.join(ROOT, "packaging", "linux")
ARCHES = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}


def read_version():
    with open(SCRIPT, encoding="utf-8") as f:
        m = re.search(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', f.read(), re.M)
    if not m:
        raise SystemExit("__version__ introuvable dans yt-dlp-gui.pyw")
    return m.group(1)


def arch_name(machine=None):
    """« x86_64 » ou « aarch64 » (les seules architectures pour lesquelles ffmpeg et Deno ont des téléchargements)."""
    name = ARCHES.get((machine or platform.machine()).lower())
    if not name:
        raise SystemExit(f"architecture non prise en charge : {machine or platform.machine()}")
    return name


def tarball_name(version, arch):
    return f"yt-dlp-gui-linux-{version}-{arch}.tar.gz"


def appimage_name(version, arch):
    return f"yt-dlp-gui-{version}-{arch}.AppImage"


def build_app():
    os.makedirs(WORK, exist_ok=True)
    sep = os.pathsep
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
           "--name", "yt-dlp-gui", "--hidden-import", "lzma",   # archive ffmpeg .tar.xz de l'assistant d'installation
           "--add-data", f"{os.path.join(ROOT, 'lang')}{sep}lang",
           "--add-data", f"{os.path.join(ROOT, 'assets')}{sep}assets",
           "--distpath", DIST, "--workpath", os.path.join(WORK, "pyinstaller-linux"), "--specpath", WORK,
           SCRIPT]
    print("->", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)
    for extra in ("LICENSE", "README.md", "CHANGELOG.md"):
        shutil.copy2(os.path.join(ROOT, extra), os.path.join(APP_DIST, extra))
    if not os.path.isfile(os.path.join(APP_DIST, "yt-dlp-gui")):
        raise SystemExit("yt-dlp-gui absent après la construction")


def build_tarball(version, arch):
    out = os.path.join(DIST, tarball_name(version, arch))
    if os.path.exists(out):
        os.remove(out)

    def clean_owner(info):
        info.uid = info.gid = 0
        info.uname = info.gname = "root"
        return info

    with tarfile.open(out, "w:gz", compresslevel=9) as tf:
        tf.add(APP_DIST, arcname="yt-dlp-gui", filter=clean_owner)
    print("->", out)
    return out


def find_appimagetool():
    for candidate in (os.environ.get("APPIMAGETOOL", ""), shutil.which("appimagetool") or ""):
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def prepare_appdir(appdir):
    """AppDir : AppRun, lanceur .desktop, icône et programme (usr/lib/yt-dlp-gui)."""
    if os.path.exists(appdir):
        shutil.rmtree(appdir)
    os.makedirs(os.path.join(appdir, "usr", "lib"))
    shutil.copytree(APP_DIST, os.path.join(appdir, "usr", "lib", "yt-dlp-gui"), symlinks=True)
    apprun = os.path.join(appdir, "AppRun")
    shutil.copy2(os.path.join(LINUX_FILES, "AppRun"), apprun)
    os.chmod(apprun, os.stat(apprun).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    shutil.copy2(os.path.join(LINUX_FILES, "yt-dlp-gui.desktop"), os.path.join(appdir, "yt-dlp-gui.desktop"))
    shutil.copy2(ICON_PNG, os.path.join(appdir, "yt-dlp-gui.png"))
    os.symlink("yt-dlp-gui.png", os.path.join(appdir, ".DirIcon"))


def build_appimage(version, arch):
    tool = find_appimagetool()
    if not tool:
        raise SystemExit("appimagetool introuvable : installez-le (https://github.com/AppImage/appimagetool) "
                         "ou définissez la variable d'environnement APPIMAGETOOL.")
    appdir = os.path.join(WORK, "AppDir")
    prepare_appdir(appdir)
    out = os.path.join(DIST, appimage_name(version, arch))
    if os.path.exists(out):
        os.remove(out)
    env = dict(os.environ, ARCH=arch, APPIMAGE_EXTRACT_AND_RUN="1")   # l'outil est lui-même un AppImage : pas de FUSE
    cmd = [tool, appdir, out]
    print("->", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)
    if not os.path.isfile(out):
        raise SystemExit("AppImage absent après la construction")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-tarball", action="store_true")
    ap.add_argument("--skip-appimage", action="store_true")
    args = ap.parse_args()
    if not sys.platform.startswith("linux"):
        raise SystemExit("Ce script construit les paquets Linux : à lancer sous Linux.")
    version, arch = read_version(), arch_name()
    print(f"yt-dlp GUI {version} ({arch})")
    build_app()
    if not args.skip_tarball:
        build_tarball(version, arch)
    if not args.skip_appimage:
        build_appimage(version, arch)
    print("Terminé.")


if __name__ == "__main__":
    main()
