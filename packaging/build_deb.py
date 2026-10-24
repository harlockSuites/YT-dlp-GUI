"""Construit le paquet Debian (.deb) de la version Linux à partir du dossier PyInstaller de build_linux.py.

Usage (depuis la racine du dépôt, sous Linux, après `python3 packaging/build_linux.py`) :
    python3 packaging/build_deb.py

Résultat dans dist/ :
    yt-dlp-gui_<version>_<amd64|arm64>.deb

Contenu du paquet :
    /opt/yt-dlp-gui/               le programme (dossier PyInstaller)
    /usr/bin/yt-dlp-gui            lien vers le programme
    /usr/share/applications/       lanceur du menu des applications
    /usr/share/icons/hicolor/256x256/apps/   icône
    /usr/share/doc/yt-dlp-gui/     licence (copyright) et journal des modifications
Les données de chaque utilisateur (réglages, yt-dlp, ffmpeg…) restent dans ~/.local/share/yt-dlp-GUI : le paquet n'y
touche ni à l'installation ni à la désinstallation. Aucun script de maintenance : les « triggers » de dpkg actualisent
le menu et les icônes tout seuls.
"""
import argparse
import gzip
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SCRIPT = os.path.join(ROOT, "yt-dlp-gui.pyw")
LINUX_FILES = os.path.join(ROOT, "packaging", "linux")
ICON_PNG = os.path.join(ROOT, "assets", "yt-dlp-gui.png")
CHANGELOG = os.path.join(ROOT, "CHANGELOG-linux.md")
LICENSE = os.path.join(ROOT, "LICENSE")
PACKAGE = "yt-dlp-gui"
INSTALL_DIR = "opt/yt-dlp-gui"
DEB_ARCHES = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
# Fichiers que build_linux.py ajoute au dossier du programme : dans le paquet, ils vont sous /usr/share/doc.
DOC_FILES = ("LICENSE", "README.md", "CHANGELOG-linux.md")
MAINTAINER = "harlockSuites <harlockSuites@users.noreply.github.com>"
HOMEPAGE = "https://github.com/harlockSuites/YT-dlp-GUI"


def read_version():
    with open(SCRIPT, encoding="utf-8") as f:
        m = re.search(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', f.read(), re.M)
    if not m:
        raise SystemExit("__version__ introuvable dans yt-dlp-gui.pyw")
    return m.group(1)


def deb_arch(machine=None):
    import platform
    name = DEB_ARCHES.get((machine or platform.machine()).lower())
    if not name:
        raise SystemExit(f"architecture non prise en charge : {machine or platform.machine()}")
    return name


def deb_name(version, arch):
    return f"{PACKAGE}_{version}_{arch}.deb"


def control_text(version, arch, installed_size_kib):
    """Fichier DEBIAN/control."""
    return "\n".join([
        f"Package: {PACKAGE}",
        f"Version: {version}",
        f"Architecture: {arch}",
        f"Maintainer: {MAINTAINER}",
        f"Installed-Size: {installed_size_kib}",
        "Depends: libc6 (>= 2.35), libx11-6",
        "Recommends: xdg-utils",
        "Suggests: ffmpeg",
        "Section: video",
        "Priority: optional",
        f"Homepage: {HOMEPAGE}",
        "Description: Graphical interface for yt-dlp",
        " yt-dlp GUI is a desktop window to download videos and audio with yt-dlp:",
        " download queue, playlist inspector, cookies read from your browser and a",
        " setup assistant. The interface is available in 15 languages.",
        " .",
        " The program is bundled (PyInstaller). yt-dlp, ffmpeg and Deno are downloaded",
        " by its setup assistant into ~/.local/share/yt-dlp-GUI, so the package needs",
        " no other dependency. This is a preview release of the Linux version.",
        ""])


def _dir_size_kib(root):
    total = 0
    for folder, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(folder, name)
            if not os.path.islink(path):
                total += os.path.getsize(path)
    return (total + 1023) // 1024


def _normalize_modes(root):
    """Dossiers 755 ; fichiers 755 s'ils sont exécutables dans le dossier PyInstaller, sinon 644."""
    for folder, dirs, files in os.walk(root):
        os.chmod(folder, 0o755)
        for name in files:
            path = os.path.join(folder, name)
            if os.path.islink(path):
                continue
            os.chmod(path, 0o755 if os.stat(path).st_mode & stat.S_IXUSR else 0o644)


def _write_md5sums(root):
    lines = []
    for folder, dirs, files in os.walk(root):
        dirs.sort()
        if os.path.relpath(folder, root) == "DEBIAN":
            continue
        for name in sorted(files):
            path = os.path.join(folder, name)
            if os.path.islink(path):
                continue
            h = hashlib.md5()   # format imposé par dpkg (md5sums), sans rôle de sécurité
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            lines.append(f"{h.hexdigest()}  {os.path.relpath(path, root).replace(os.sep, '/')}")
    with open(os.path.join(root, "DEBIAN", "md5sums"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def stage_tree(app_dir, root, version, arch):
    """Prépare l'arborescence du paquet dans `root` (dossier vide ou inexistant)."""
    if os.path.exists(root):
        shutil.rmtree(root)
    opt = os.path.join(root, *INSTALL_DIR.split("/"))
    shutil.copytree(app_dir, opt, symlinks=True)
    for name in DOC_FILES:
        extra = os.path.join(opt, name)
        if os.path.exists(extra):
            os.remove(extra)
    bin_dir = os.path.join(root, "usr", "bin")
    os.makedirs(bin_dir)
    os.symlink("../../" + INSTALL_DIR + "/yt-dlp-gui", os.path.join(bin_dir, "yt-dlp-gui"))
    apps = os.path.join(root, "usr", "share", "applications")
    os.makedirs(apps)
    shutil.copy2(os.path.join(LINUX_FILES, "yt-dlp-gui.desktop"), os.path.join(apps, "yt-dlp-gui.desktop"))
    icons = os.path.join(root, "usr", "share", "icons", "hicolor", "256x256", "apps")
    os.makedirs(icons)
    shutil.copy2(ICON_PNG, os.path.join(icons, "yt-dlp-gui.png"))
    doc = os.path.join(root, "usr", "share", "doc", PACKAGE)
    os.makedirs(doc)
    shutil.copy2(LICENSE, os.path.join(doc, "copyright"))
    with open(CHANGELOG, "rb") as src, open(os.path.join(doc, "changelog.gz"), "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            gz.write(src.read())
    _normalize_modes(root)
    debian = os.path.join(root, "DEBIAN")
    os.makedirs(debian)
    with open(os.path.join(debian, "control"), "w", encoding="utf-8", newline="\n") as f:
        f.write(control_text(version, arch, _dir_size_kib(root)))
    _write_md5sums(root)
    os.chmod(debian, 0o755)
    return root


def build_deb(app_dir, out_dir, work_dir):
    version, arch = read_version(), deb_arch()
    if not os.path.isfile(os.path.join(app_dir, "yt-dlp-gui")):
        raise SystemExit(f"{app_dir} ne contient pas le programme : lancez d'abord packaging/build_linux.py")
    if not shutil.which("dpkg-deb"):
        raise SystemExit("dpkg-deb introuvable (paquet dpkg) : à construire sous Debian ou Ubuntu.")
    root = stage_tree(app_dir, os.path.join(work_dir, "deb-root"), version, arch)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, deb_name(version, arch))
    if os.path.exists(out):
        os.remove(out)
    cmd = ["dpkg-deb", "--root-owner-group", "-Zxz", "--build", root, out]
    print("->", " ".join(cmd))
    subprocess.run(cmd, check=True)
    if not os.path.isfile(out):
        raise SystemExit("paquet .deb absent après la construction")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app-dir", default=os.path.join(DIST, "yt-dlp-gui"), help="dossier PyInstaller du programme")
    ap.add_argument("--out-dir", default=DIST)
    ap.add_argument("--work-dir", default=os.path.join(ROOT, "build"))
    args = ap.parse_args(argv)
    if not sys.platform.startswith("linux"):
        raise SystemExit("Ce script construit le paquet .deb : à lancer sous Linux.")
    out = build_deb(args.app_dir, args.out_dir, args.work_dir)
    print("->", out)
    print("Terminé.")


if __name__ == "__main__":
    main()
