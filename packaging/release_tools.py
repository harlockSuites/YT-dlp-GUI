"""Outils de publication, appelés par .github/workflows/release.yml (et testables en local).

    python packaging/release_tools.py check-tag v0.1.0
    python packaging/release_tools.py notes --out dist/release-notes.md
    python packaging/release_tools.py checksums --dir dist --out dist/SHA256SUMS.txt
"""
import argparse
import fnmatch
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATTERNS = ("yt-dlp-gui-setup-*.exe", "yt-dlp-gui-portable-*.zip")
LINUX_ARTIFACT_PATTERNS = ("yt-dlp-gui-*-*.AppImage", "yt-dlp-gui-linux-*.tar.gz")


def read_version(root=ROOT):
    with open(os.path.join(root, "yt-dlp-gui.pyw"), encoding="utf-8") as f:
        m = re.search(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', f.read(), re.M)
    if not m:
        raise SystemExit("__version__ introuvable dans yt-dlp-gui.pyw")
    return m.group(1)


def tag_matches_version(tag, version, prefix="v"):
    """L'étiquette de publication doit être exactement le préfixe (« v » pour Windows, « Linux-v » pour Linux)
    suivi de __version__."""
    return tag == f"{prefix}{version}"


def release_notes(changelog_text, version):
    """Section du journal des modifications correspondant à `version` (sans son titre)."""
    lines = changelog_text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(rf"^##\s*\[{re.escape(version)}\]", l)), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:end]).strip() + "\n"


def artifact_files(folder, patterns=ARTIFACT_PATTERNS):
    names = sorted(os.listdir(folder))
    return [n for n in names if any(fnmatch.fnmatch(n, p) for p in patterns)]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checksums(folder, out_path, patterns=ARTIFACT_PATTERNS):
    """Écrit « hash  nom » (format sha256sum) pour chaque fichier publié."""
    names = artifact_files(folder, patterns)
    if not names:
        raise SystemExit(f"aucun fichier à publier dans {folder}")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for n in names:
            f.write(f"{sha256_of(os.path.join(folder, n))}  {n}\n")
    return names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check-tag")
    p.add_argument("tag")
    p.add_argument("--prefix", default="v", help="préfixe de l'étiquette (« Linux-v » pour la version Linux)")
    p = sub.add_parser("notes")
    p.add_argument("--out", required=True)
    p.add_argument("--changelog", default="CHANGELOG.md", help="journal des modifications à lire (dans le dépôt)")
    p = sub.add_parser("checksums")
    p.add_argument("--dir", default=os.path.join(ROOT, "dist"))
    p.add_argument("--out", required=True)
    p.add_argument("--platform", choices=("windows", "linux"), default="windows")
    args = ap.parse_args(argv)

    version = read_version()
    if args.cmd == "check-tag":
        if not tag_matches_version(args.tag, version, args.prefix):
            print(f"Étiquette « {args.tag} » différente de la version du code ({args.prefix}{version}) : "
                  f"corrigez __version__ ou l'étiquette.", file=sys.stderr)
            return 1
        print(f"Étiquette {args.tag} : OK")
    elif args.cmd == "notes":
        with open(os.path.join(ROOT, args.changelog), encoding="utf-8") as f:
            notes = release_notes(f.read(), version)
        if not notes.strip():
            notes = f"yt-dlp GUI {version}\n"
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(notes)
        print(f"Notes de la version {version} : {args.out}")
    elif args.cmd == "checksums":
        names = write_checksums(args.dir, args.out,
                                LINUX_ARTIFACT_PATTERNS if args.platform == "linux" else ARTIFACT_PATTERNS)
        print("Sommes SHA-256 :", ", ".join(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
