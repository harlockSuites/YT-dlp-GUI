"""README-LINUX (français et anglais) : liens, ancres, structure, commandes identiques à celles du logiciel."""
import importlib.util
import os
import re
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()

LINUX_DOCS = {"fr": os.path.join(ROOT, "README-LINUX.md"), "en": os.path.join(ROOT, "docs", "README-LINUX.en.md")}
ALL_READMES = {"fr": os.path.join(ROOT, "README.md"),
               **{c: os.path.join(ROOT, "docs", f"README.{c}.md")
                  for c in ("en", "es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko", "fil")}}
# Mots qui changent d'une langue à l'autre dans les blocs de code (le reste doit être identique)
PLACEHOLDERS = (("IDENTIFIANT", "IDENTIFIER"), ("chemin/du/profil", "path/to/profile"),
                ("nouveau-fichier.deb", "new-file.deb"), ("keyrings-sauvegarde", "keyrings-backup"))


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")   # une copie Windows du dépôt a des fins de ligne CRLF


def _slug(heading):
    """Ancre GitHub d'un titre : minuscules, ponctuation retirée, espaces remplacés par des tirets."""
    text = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return text.replace(" ", "-")


def _code_blocks(text, lang):
    blocks = re.findall(r"```[a-z]*\n(.*?)```", text, re.S)
    if lang == "en":
        return blocks
    out = []
    for block in blocks:
        for fr, en in PLACEHOLDERS:
            block = block.replace(fr, en)
        out.append(block)
    return out


def _local_links(text):
    return [u for u in re.findall(r"\]\(([^)\s]+)\)", text) if not re.match(r"[a-z]+://|mailto:", u)]


def _load_build_deb():
    spec = importlib.util.spec_from_file_location("build_deb", os.path.join(ROOT, "packaging", "build_deb.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LinuxReadmeTests(unittest.TestCase):
    def test_both_files_exist_and_are_cross_linked(self):
        for lang, path in LINUX_DOCS.items():
            with self.subTest(lang=lang):
                text = _read(path)
                self.assertTrue(text.startswith("# yt-dlp GUI"))
                self.assertIn("README-LINUX.md", text)
                self.assertIn("README-LINUX.en.md", text)

    def test_every_local_link_points_to_an_existing_file(self):
        for lang, path in LINUX_DOCS.items():
            for target in _local_links(_read(path)):
                if target.startswith("#"):
                    continue
                with self.subTest(lang=lang, target=target):
                    full = os.path.normpath(os.path.join(os.path.dirname(path), target.split("#")[0]))
                    self.assertTrue(os.path.exists(full), full)

    def test_every_anchor_matches_a_heading(self):
        for lang, path in LINUX_DOCS.items():
            text = _read(path)
            slugs = {_slug(h) for h in re.findall(r"^#{2,3} (.+)$", text, re.M)}
            anchors = re.findall(r"\]\(#([^)]+)\)", text)
            self.assertGreater(len(anchors), 8)
            for anchor in anchors:
                with self.subTest(lang=lang, anchor=anchor):
                    self.assertIn(anchor, slugs)

    def test_french_and_english_have_the_same_structure_and_the_same_commands(self):
        fr, en = _read(LINUX_DOCS["fr"]), _read(LINUX_DOCS["en"])

        def shape(t):
            return (len(re.findall(r"^## ", t, re.M)), len(re.findall(r"^### ", t, re.M)),
                    len(re.findall(r"^\|---", t, re.M)), len(re.findall(r"^- ", t, re.M)),
                    len(re.findall(r"^\d+\. ", t, re.M)), t.count("```"))
        self.assertEqual(shape(fr), shape(en))
        self.assertEqual(_code_blocks(fr, "fr"), _code_blocks(en, "en"), "les commandes doivent être identiques")
        self.assertGreater(len(_code_blocks(fr, "fr")), 25)

    def test_no_windows_content_is_left_in_it(self):
        for lang, path in LINUX_DOCS.items():
            text = _read(path)
            for word in ("SmartScreen", "Chocolatey", "Defender", "PowerShell", "VirusTotal", "SignPath"):
                with self.subTest(lang=lang, word=word):
                    self.assertNotIn(word, text)

    def test_the_commands_in_it_are_the_ones_the_software_shows(self):
        for lang, path in LINUX_DOCS.items():
            text = _read(path)
            for manager in ("apt", "dnf", "pacman", "zypper"):
                with self.subTest(lang=lang, manager=manager):
                    self.assertIn(m.linux_install_command(["AtomicParsley", "MKVToolNix", "aria2"], manager), text)
                    self.assertIn(m.linux_keyring_install_command(manager), text)
            self.assertIn(m.LINUX_KEYRING_CHECK_COMMAND, text)
            for name in (os.path.basename(m.CONFIG_FILE), os.path.basename(m.QUEUE_FILE),
                         os.path.basename(m.CUSTOM_BLOCKS_FILE)):
                self.assertIn(name, text)

    def test_the_browser_table_matches_the_catalog(self):
        natives = ("firefox", "chrome", "chromium", "brave", "vivaldi", "opera", "edge")
        for lang, path in LINUX_DOCS.items():
            text = _read(path)
            for key, label, ytdlp, dirs in m.LINUX_BROWSER_CATALOG:
                with self.subTest(lang=lang, browser=key):
                    self.assertIn(label, text)
                    if key in natives:
                        self.assertIn(dirs[0].replace("{cfg}", "~/.config"), text)

    def test_the_package_facts_match_the_build_script(self):
        bd = _load_build_deb()
        control = bd.control_text("1.2.3", "amd64", 1)
        for lang, path in LINUX_DOCS.items():
            text = _read(path)
            with self.subTest(lang=lang):
                for fact in ("libc6 (>= 2.35)", "libx11-6"):
                    self.assertIn(fact, text)
                    self.assertIn(fact, control)
                self.assertIn("/opt/yt-dlp-gui", text)
                self.assertIn(bd.deb_name("X.Y.Z", "amd64"), text)

    def test_the_menu_labels_quoted_are_the_real_ones(self):
        import json
        for lang, path in LINUX_DOCS.items():
            with open(os.path.join(ROOT, "lang", f"{lang}.json"), encoding="utf-8") as f:
                data = json.load(f)
            text = _read(path)
            with self.subTest(lang=lang):
                self.assertIn(data["menu_install.title"], text)
                self.assertIn(data["browsers.title"], text)
                self.assertIn(data["bug.window_title"], text)
                for key in ("toolbar.menu_deps", "toolbar.menu_update", "toolbar.menu_browsers"):
                    self.assertIn(data[key].split("  ")[-1].rstrip("…"), text, key)

    def test_all_fifteen_readmes_point_to_it(self):
        for code, path in ALL_READMES.items():
            with self.subTest(lang=code):
                self.assertRegex(_read(path), r"README-LINUX \(français\)\]\((\.\./)?README-LINUX\.md\)")
                self.assertRegex(_read(path), r"README-LINUX \(English\)\]\((docs/)?README-LINUX\.en\.md\)")


if __name__ == "__main__":
    unittest.main()
