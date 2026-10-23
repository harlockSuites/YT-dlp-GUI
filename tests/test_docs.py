import os
import re
import unittest

from tests._loader import ROOT

CODES = ["en", "es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko", "fil"]


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _all_docs():
    docs = {"fr": os.path.join(ROOT, "README.md")}
    for c in CODES:
        docs[c] = os.path.join(ROOT, "docs", f"README.{c}.md")
    return docs


def _local_links(text):
    return [u for u in re.findall(r"\]\(([^)\s]+)\)", text) if not re.match(r"[a-z]+://", u)]


class DocsTests(unittest.TestCase):
    def test_every_language_has_a_readme(self):
        for code, path in _all_docs().items():
            with self.subTest(lang=code):
                self.assertTrue(os.path.isfile(path), path)

    def test_same_structure_as_french_reference(self):
        ref = _read(_all_docs()["fr"])
        shape = lambda t: (len(re.findall(r"^# ", t, re.M)), len(re.findall(r"^## ", t, re.M)),
                           len(re.findall(r"^### ", t, re.M)), len(re.findall(r"^- ", t, re.M)),
                           len(re.findall(r"^\d+\. ", t, re.M)), t.count("```"), len(re.findall(r"^!\[", t, re.M)))
        for code, path in _all_docs().items():
            with self.subTest(lang=code):
                self.assertEqual(shape(_read(path)), shape(ref))

    def test_language_bar_links_all_fifteen_and_they_exist(self):
        for code, path in _all_docs().items():
            with self.subTest(lang=code):
                text = _read(path)
                bar = next(line for line in text.splitlines() if line.count("](") >= 15)
                links = re.findall(r"\]\(([^)]+)\)", bar)
                self.assertEqual(len(links), 15)
                for link in links:
                    self.assertTrue(os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(path), link))), link)

    def test_local_links_resolve_and_match_reference(self):
        norm = lambda u: re.sub(r"\.(fr|en)\.png$", ".png", os.path.basename(u))
        ref_targets = sorted(norm(u) for u in _local_links(_read(_all_docs()["fr"]))
                             if not u.startswith("docs/README"))
        for code, path in _all_docs().items():
            text = _read(path)
            with self.subTest(lang=code):
                for link in _local_links(text):
                    self.assertTrue(os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), link))), link)
                mine = sorted(norm(u) for u in _local_links(text) if "README" not in u)
                self.assertEqual(mine, [t for t in ref_targets if "README" not in t])

    def test_external_links_identical_everywhere(self):
        ext = lambda t: sorted(re.findall(r"\]\((https://[^)\s]+)\)", t))
        ref = ext(_read(_all_docs()["fr"]))
        for code, path in _all_docs().items():
            with self.subTest(lang=code):
                self.assertEqual(ext(_read(path)), ref)

    def test_privacy_bullet_mentions_the_update_check(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
            bullet = next(l for l in lines[heads[4] + 1:] if l.startswith("- "))
            with self.subTest(lang=code):
                self.assertGreaterEqual(bullet.count("GitHub"), 2)

    def test_installation_section_comes_second_and_explains_smartscreen(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
            section = "\n".join(lines[heads[1]:heads[2]])
            with self.subTest(lang=code):
                for needle in ("yt-dlp-gui-setup-X.Y.Z.exe", "yt-dlp-gui-portable-X.Y.Z.zip", "SmartScreen",
                               "SHA256SUMS.txt", "Get-FileHash", "/releases"):
                    self.assertIn(needle, section)

    def test_screenshots_exist_and_use_the_right_language(self):
        for code, path in _all_docs().items():
            text = _read(path)
            names = re.findall(r"^!\[[^\]]*\]\(([^)]+)\)", text, re.M)
            with self.subTest(lang=code):
                self.assertEqual(len(names), 3)
                for n in names:
                    self.assertTrue(os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(path), n))), n)
                    self.assertIn(".fr.png" if code == "fr" else ".en.png", n)

    def test_license_paragraph_discloses_ai_generated_assets(self):
        for code, path in _all_docs().items():
            last = [l for l in _read(path).splitlines() if l.strip()][-1]
            with self.subTest(lang=code):
                for needle in ("MIT", "yt-dlp-gui.ico", "assets/", "Harlock S."):
                    self.assertIn(needle, last)

    def test_update_bullet_names_the_menu_entries_in_the_same_language(self):
        import json
        for code, path in _all_docs().items():
            lang = json.loads(_read(os.path.join(ROOT, "lang", f"{code}.json")))
            text = _read(path)
            with self.subTest(lang=code):
                self.assertIn(lang["toolbar.menu_auto_update_check"], text)
                self.assertIn(lang["toolbar.menu_check_update"], text)

    def test_every_language_announces_the_linux_preview_in_the_banner(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            banner = next(l for l in lines if l.startswith("> **"))
            with self.subTest(lang=code):
                self.assertRegex(banner, r"Linux|Linuks")   # le polonais décline le mot
        self.assertNotIn("sera publiée à moyen terme", _read(_all_docs()["fr"]))
        self.assertNotIn("will be released in the medium term", _read(_all_docs()["en"]))

    def test_installation_lists_the_linux_files_in_every_language(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
            section = "\n".join(lines[heads[1]:heads[2]])
            with self.subTest(lang=code):
                for needle in ("yt-dlp-gui-X.Y.Z-x86_64.AppImage", "chmod +x", "libfuse2", "--appimage-extract-and-run",
                               "yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz", "tar xzf", "~/.local/share/yt-dlp-GUI",
                               "SHA256SUMS-linux.txt", "sha256sum -c SHA256SUMS-linux.txt --ignore-missing", "glibc 2.35",
                               "Linux-v", "Pre-release"):   # où trouver les fichiers : releases « Linux-v… » en préversion
                    self.assertIn(needle, section)
                self.assertEqual(sum(1 for l in section.splitlines() if l.startswith("- **Linux")), 3)

    def test_prerequisites_quick_start_and_dependencies_mention_linux(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
            prereq = "\n".join(lines[heads[3]:heads[4]])
            quick = "\n".join(lines[heads[4]:heads[5]])
            with self.subTest(lang=code):
                self.assertIn("Linux", prereq)
                self.assertIn("python3-tk", prereq)
                self.assertIn("python3 yt-dlp-gui.pyw", quick)
                text = "\n".join(lines)
                for needle in ("zypper", "AppImage", "Chromium", "Vivaldi", "GNOME Keyring"):
                    self.assertIn(needle, text)

    def test_bug_report_bullet_no_longer_says_windows_only(self):
        for code, path in _all_docs().items():
            lines = _read(path).splitlines()
            heads2 = [i for i, l in enumerate(lines) if l.startswith("## ")]
            bug = max(i for i, l in enumerate(lines) if l.startswith("### ") and i < heads2[1])
            first = next(l for l in lines[bug:] if l.startswith("- "))
            with self.subTest(lang=code):
                self.assertNotIn("Windows", first)

    def test_key_facts_present_in_every_language(self):
        for code, path in _all_docs().items():
            text = _read(path)
            with self.subTest(lang=code):
                for needle in ("yt-dlp-gui.bat", "SHA-256", ".yt-dlp-registre.json", "Ko-fi", "MIT",
                               "python -X utf8 -m unittest discover -s tests -t ."):
                    self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
