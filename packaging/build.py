"""Construit l'exécutable Windows (PyInstaller), la version portable (.zip) et l'installateur (Inno Setup).

Usage (depuis la racine du dépôt) :
    python packaging/build.py                    # tout
    python packaging/build.py --skip-installer   # exécutable + zip portable seulement
    python packaging/build.py --skip-zip

Résultats dans dist/ :
    yt-dlp-gui/                         exécutable (dossier)
    yt-dlp-gui-portable-<version>.zip   version portable (données à côté de l'exécutable)
    yt-dlp-gui-setup-<version>.exe      installateur (données dans %LOCALAPPDATA%\\yt-dlp-GUI)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
WORK = os.path.join(ROOT, "build")
APP_DIST = os.path.join(DIST, "yt-dlp-gui")
SCRIPT = os.path.join(ROOT, "yt-dlp-gui.pyw")
ICON = os.path.join(ROOT, "yt-dlp-gui.ico")
ISS = os.path.join(ROOT, "packaging", "yt-dlp-gui.iss")


def read_version():
    with open(SCRIPT, encoding="utf-8") as f:
        m = re.search(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', f.read(), re.M)
    if not m:
        raise SystemExit("__version__ introuvable dans yt-dlp-gui.pyw")
    return m.group(1)


def version_file_text(version):
    """Ressource « Détails » de l'exécutable (propriétés du fichier sous Windows)."""
    a, b, c = (int(x) for x in version.split("."))
    tup = f"({a}, {b}, {c}, 0)"
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={tup}, prodvers={tup}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040C04B0', [
      StringStruct('CompanyName', 'Harlock S.'),
      StringStruct('FileDescription', 'yt-dlp GUI'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'yt-dlp-gui'),
      StringStruct('LegalCopyright', 'MIT License - Harlock S.'),
      StringStruct('OriginalFilename', 'yt-dlp-gui.exe'),
      StringStruct('ProductName', 'yt-dlp GUI'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1036, 1200])])
  ]
)
"""


def build_exe(version):
    os.makedirs(WORK, exist_ok=True)
    vfile = os.path.join(WORK, "version-info.txt")
    with open(vfile, "w", encoding="utf-8") as f:
        f.write(version_file_text(version))
    sep = os.pathsep
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed",
           "--name", "yt-dlp-gui", "--icon", ICON, "--version-file", vfile,
           "--add-data", f"{os.path.join(ROOT, 'lang')}{sep}lang",
           "--add-data", f"{os.path.join(ROOT, 'assets')}{sep}assets",
           "--add-data", f"{ICON}{sep}.",
           "--distpath", DIST, "--workpath", os.path.join(WORK, "pyinstaller"), "--specpath", WORK,
           SCRIPT]
    print("→", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)
    for extra in ("LICENSE", "README.md", "CHANGELOG.md"):
        shutil.copy2(os.path.join(ROOT, extra), os.path.join(APP_DIST, extra))
    if not os.path.isfile(os.path.join(APP_DIST, "yt-dlp-gui.exe")):
        raise SystemExit("yt-dlp-gui.exe absent après la construction")


def build_portable_zip(version):
    out = os.path.join(DIST, f"yt-dlp-gui-portable-{version}.zip")
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for folder, _dirs, files in os.walk(APP_DIST):
            for name in files:
                full = os.path.join(folder, name)
                zf.write(full, os.path.join("yt-dlp-gui", os.path.relpath(full, APP_DIST)))
        zf.writestr("yt-dlp-gui/portable.flag",
                    "Ce fichier active le mode portable : les données restent dans ce dossier.\n")
    print("→", out)
    return out


def find_iscc():
    candidates = [os.environ.get("ISCC", ""), shutil.which("iscc") or "", shutil.which("ISCC") or ""]
    for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles(x86)", ""),
                 os.environ.get("ProgramFiles", "")):
        if base:
            candidates.append(os.path.join(base, "Programs", "Inno Setup 6", "ISCC.exe"))
            candidates.append(os.path.join(base, "Inno Setup 6", "ISCC.exe"))
    return next((c for c in candidates if c and os.path.isfile(c)), None)


def build_installer(version):
    iscc = find_iscc()
    if not iscc:
        raise SystemExit("Inno Setup (ISCC.exe) introuvable : installez-le (https://jrsoftware.org/isinfo.php) "
                         "ou définissez la variable d'environnement ISCC.")
    cmd = [iscc, f"/DAppVersion={version}", ISS]
    print("→", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)
    out = os.path.join(DIST, f"yt-dlp-gui-setup-{version}.exe")
    if not os.path.isfile(out):
        raise SystemExit("installateur absent après la compilation")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-zip", action="store_true")
    ap.add_argument("--skip-installer", action="store_true")
    args = ap.parse_args()
    version = read_version()
    print(f"yt-dlp GUI {version}")
    build_exe(version)
    if not args.skip_zip:
        build_portable_zip(version)
    if not args.skip_installer:
        build_installer(version)
    print("Terminé.")


if __name__ == "__main__":
    main()
