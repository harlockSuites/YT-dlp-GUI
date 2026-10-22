"""Compile le lanceur (« bootloader ») de PyInstaller depuis ses sources et remplace celui de l'installation.

Pourquoi : le lanceur fourni par PyInstaller est le même pour des milliers de programmes, dont des logiciels
malveillants ; des antivirus (Microsoft Defender : « Trojan:Win32/Wacatac…!ml », CrowdStrike, Zillya…) le
signalent par apprentissage automatique. Le recompiler avec le compilateur Visual C++ produit un fichier
différent (même code, autre empreinte). Cet essai ne garantit pas la fin des détections : il se juge en
soumettant le résultat à VirusTotal.

Usage (Windows, Visual Studio Build Tools avec « Développement Desktop en C++ » installé) :
    python packaging/build_bootloader.py            # compile et installe le lanceur compilé
    python packaging/build_bootloader.py --dry-run  # télécharge et vérifie seulement
Les sources viennent de PyPI (archive « sdist » de la version installée, somme SHA-256 vérifiée).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

PYPI_JSON = "https://pypi.org/pypi/pyinstaller/{version}/json"


def installed_version():
    from importlib.metadata import version
    return version("pyinstaller")


def sdist_info(data):
    """(url, sha256) de l'archive source dans la réponse JSON de PyPI."""
    for item in data.get("urls", []):
        if item.get("packagetype") == "sdist":
            return item["url"], item["digests"]["sha256"]
    raise SystemExit("archive source de PyInstaller introuvable sur PyPI")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_verified(url, expected_sha256, dest):
    """Télécharge `url` vers `dest` ; refuse un fichier dont la somme SHA-256 diffère."""
    with urllib.request.urlopen(url, timeout=60) as response, open(dest, "wb") as out:
        shutil.copyfileobj(response, out)
    actual = sha256_file(dest)
    if actual != expected_sha256:
        os.remove(dest)
        raise SystemExit(f"somme SHA-256 inattendue : {actual} au lieu de {expected_sha256}")
    return dest


def extract(archive, dest):
    with tarfile.open(archive) as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter="data")                 # refuse les chemins sortant du dossier
        else:                                                     # Python sans filtre : contrôle à la main
            root = os.path.realpath(dest)
            for member in tar.getmembers():
                if not os.path.realpath(os.path.join(dest, member.name)).startswith(root + os.sep):
                    raise SystemExit(f"chemin suspect dans l'archive : {member.name}")
            tar.extractall(dest)


def installed_bootloader_dir():
    import PyInstaller
    return os.path.join(os.path.dirname(PyInstaller.__file__), "bootloader")


def copy_compiled(source_root, started, target_dir):
    """Copie les lanceurs que la compilation vient d'écrire ; renvoie [(nom, ancienne somme, nouvelle somme)]."""
    changed = []
    base = os.path.join(source_root, "PyInstaller", "bootloader")
    for platform_dir in sorted(os.listdir(base)):
        folder = os.path.join(base, platform_dir)
        if not (platform_dir.startswith("Windows-") and os.path.isdir(folder)):
            continue
        for name in sorted(os.listdir(folder)):
            source = os.path.join(folder, name)
            if not name.endswith(".exe") or os.path.getmtime(source) < started - 1:
                continue
            target = os.path.join(target_dir, platform_dir, name)
            old = sha256_file(target) if os.path.isfile(target) else ""
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            changed.append((f"{platform_dir}/{name}", old, sha256_file(target)))
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="télécharger et vérifier seulement")
    args = parser.parse_args()
    version = installed_version()
    with urllib.request.urlopen(PYPI_JSON.format(version=version), timeout=60) as response:
        url, expected = sdist_info(json.load(response))
    print(f"PyInstaller {version} : sources {url}")
    with tempfile.TemporaryDirectory() as work:
        archive = download_verified(url, expected, os.path.join(work, "pyinstaller-sdist.tar.gz"))
        print(f"archive vérifiée (SHA-256 {expected})")
        extract(archive, work)
        source_root = os.path.join(work, f"pyinstaller-{version}")
        if not os.path.isdir(os.path.join(source_root, "bootloader")):
            raise SystemExit("dossier « bootloader » absent de l'archive")
        if args.dry_run:
            print("--dry-run : rien n'est compilé")
            return
        started = time.time()
        subprocess.run([sys.executable, "./waf", "all"], cwd=os.path.join(source_root, "bootloader"), check=True)
        changed = copy_compiled(source_root, started, installed_bootloader_dir())
        if not changed:
            raise SystemExit("aucun lanceur compilé : la compilation n'a rien produit")
        for name, old, new in changed:
            print(f"{name}\n  avant : {old or '(absent)'}\n  après : {new}")


if __name__ == "__main__":
    main()
