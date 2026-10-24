"""README-LINUX (15 langues) : liens, ancres, structure, commandes identiques à celles du logiciel."""
import importlib.util
import json
import os
import re
import unicodedata
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()

CODES = ["fr", "en", "es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko", "fil"]
LANGUAGE_NAMES = ["Français", "English", "Español", "Português", "Italiano", "Polski", "Magyar", "Srpski", "Русский",
                  "Tiếng Việt", "中文", "हिन्दी", "日本語", "한국어", "Filipino"]


def _linux_path(code):
    return os.path.join(ROOT, "README-LINUX.md") if code == "fr" else os.path.join(ROOT, "docs", f"README-LINUX.{code}.md")


def _readme_path(code):
    return os.path.join(ROOT, "README.md") if code == "fr" else os.path.join(ROOT, "docs", f"README.{code}.md")


LINUX_DOCS = {c: _linux_path(c) for c in CODES}
ALL_READMES = {c: _readme_path(c) for c in CODES}
# Mots qui changent d'une langue à l'autre dans les blocs de code du français (le reste doit être identique à l'anglais)
PLACEHOLDERS = (("IDENTIFIANT", "IDENTIFIER"), ("chemin/du/profil", "path/to/profile"),
                ("nouveau-fichier.deb", "new-file.deb"), ("keyrings-sauvegarde", "keyrings-backup"))
# Messages de yt-dlp : jamais traduits, car c'est ce que l'utilisateur voit à l'écran
YTDLP_MESSAGES = ("Extracted 0 cookies", "Item does not exist!", "Could not copy Chrome cookie database",
                  "database is locked", "Failed to decrypt", "Safe Storage")


# Écritures permises dans le texte de chaque langue (hors barre de langues) : repère les lettres d'une autre écriture
# glissées par erreur dans une traduction (ex. du cyrillique dans un texte serbe en alphabet latin)
SCRIPTS = {"ru": {"CYRILLIC"}, "zh": {"CJK"}, "ja": {"CJK", "HIRAGANA", "KATAKANA", "KATAKANA-HIRAGANA"}, "ko": {"HANGUL"},
           "hi": {"DEVANAGARI"}}


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")   # une copie Windows du dépôt a des fins de ligne CRLF


def _existing():
    return {c: p for c, p in LINUX_DOCS.items() if os.path.isfile(p)}


def _code_blocks(text, code):
    blocks = re.findall(r"```[a-z]*\n(.*?)```", text, re.S)
    if code != "fr":
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


def _label(data, key):
    """Libellé de l'interface sans l'émoji ni les points de suspension (comme il est cité dans le guide)."""
    return data[key].split("  ")[-1].rstrip("…").strip()


class LinuxReadmeTests(unittest.TestCase):
    def test_all_fifteen_languages_have_a_guide(self):
        self.assertEqual(sorted(_existing()), sorted(CODES))

    def test_every_guide_has_the_language_bar_with_the_fifteen_languages(self):
        for code, path in _existing().items():
            with self.subTest(lang=code):
                text = _read(path)
                self.assertTrue(text.startswith("# yt-dlp GUI"))
                bar = text.split("\n")[2]
                self.assertEqual(re.findall(r"\[([^\]]+)\]\(", bar), LANGUAGE_NAMES)
                for target in _local_links(bar):
                    self.assertTrue(os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(LINUX_DOCS[code]), target))))

    def test_every_local_link_points_to_an_existing_file(self):
        for code, path in _existing().items():
            for target in _local_links(_read(path)):
                if target.startswith("#"):
                    continue
                with self.subTest(lang=code, target=target):
                    full = os.path.normpath(os.path.join(os.path.dirname(path), target.split("#")[0]))
                    self.assertTrue(os.path.exists(full), full)

    def test_every_anchor_has_its_explicit_target_and_the_nine_sections_are_numbered(self):
        for code, path in _existing().items():
            text = _read(path)
            with self.subTest(lang=code):
                targets = re.findall(r'^<a id="(s\d)"></a>$', text, re.M)
                self.assertEqual(targets, [f"s{n}" for n in range(1, 10)])
                self.assertEqual([int(n) for n in re.findall(r"^## (\d+)\. ", text, re.M)], list(range(1, 10)))
                for anchor in re.findall(r"\]\(#([^)]+)\)", text):
                    self.assertIn(anchor, targets)
                self.assertEqual(len(re.findall(r"^\d\. \[[^\]]+\]\(#s\d\)$", text, re.M)), 9, "sommaire")

    def test_every_language_has_the_same_structure_and_the_same_commands_as_english(self):
        en = _read(LINUX_DOCS["en"])

        def shape(t):
            return (len(re.findall(r"^## ", t, re.M)), len(re.findall(r"^### ", t, re.M)),
                    len(re.findall(r"^\|---", t, re.M)), len(re.findall(r"^- ", t, re.M)),
                    len(re.findall(r"^\d+\. ", t, re.M)), t.count("```"), len(re.findall(r"^\| ", t, re.M)))
        for code, path in _existing().items():
            text = _read(path)
            with self.subTest(lang=code):
                self.assertEqual(shape(text), shape(en))
                self.assertEqual(_code_blocks(text, code), _code_blocks(en, "en"), "les commandes doivent être identiques")
        self.assertGreater(len(_code_blocks(en, "en")), 25)

    def test_ytdlp_messages_are_kept_untranslated(self):
        for code, path in _existing().items():
            text = _read(path)
            for message in YTDLP_MESSAGES:
                with self.subTest(lang=code, message=message):
                    self.assertIn(message, text)

    def test_no_windows_content_is_left_in_it(self):
        for code, path in _existing().items():
            text = _read(path)
            for word in ("SmartScreen", "Chocolatey", "Defender", "PowerShell", "VirusTotal", "SignPath"):
                with self.subTest(lang=code, word=word):
                    self.assertNotIn(word, text)

    def test_the_commands_in_it_are_the_ones_the_software_shows(self):
        for code, path in _existing().items():
            text = _read(path)
            for manager in ("apt", "dnf", "pacman", "zypper"):
                with self.subTest(lang=code, manager=manager):
                    self.assertIn(m.linux_install_command(["AtomicParsley", "MKVToolNix", "aria2"], manager), text)
                    self.assertIn(m.linux_keyring_install_command(manager), text)
            self.assertIn(m.LINUX_KEYRING_CHECK_COMMAND, text)
            for name in (os.path.basename(m.CONFIG_FILE), os.path.basename(m.QUEUE_FILE),
                         os.path.basename(m.CUSTOM_BLOCKS_FILE)):
                self.assertIn(name, text)

    def test_the_browser_table_matches_the_catalog(self):
        natives = ("firefox", "chrome", "chromium", "brave", "vivaldi", "opera", "edge")
        for code, path in _existing().items():
            text = _read(path)
            for key, label, ytdlp, dirs in m.LINUX_BROWSER_CATALOG:
                with self.subTest(lang=code, browser=key):
                    self.assertIn(label, text)
                    if key in natives:
                        self.assertIn(dirs[0].replace("{cfg}", "~/.config"), text)

    def test_the_package_facts_match_the_build_script(self):
        bd = _load_build_deb()
        control = bd.control_text("1.2.3", "amd64", 1)
        for code, path in _existing().items():
            text = _read(path)
            with self.subTest(lang=code):
                for fact in ("libc6 (>= 2.35)", "libx11-6"):
                    self.assertIn(fact, text)
                    self.assertIn(fact, control)
                self.assertIn("/opt/yt-dlp-gui", text)
                self.assertIn(bd.deb_name("X.Y.Z", "amd64"), text)

    def test_the_menu_labels_quoted_are_the_real_ones_of_the_same_language(self):
        for code, path in _existing().items():
            with open(os.path.join(ROOT, "lang", f"{code}.json"), encoding="utf-8") as f:
                data = json.load(f)
            text = _read(path)
            with self.subTest(lang=code):
                self.assertIn(data["menu_install.title"], text)
                self.assertIn(data["browsers.title"], text)
                self.assertIn(data["bug.window_title"], text)
                self.assertIn(data["menu_install.btn_update"], text)
                self.assertIn(data["menu_install.btn_remove"], text)
                for key in ("toolbar.menu_deps", "toolbar.menu_update", "toolbar.menu_browsers"):
                    self.assertIn(_label(data, key), text, key)

    def test_each_guide_links_to_the_main_readme_of_its_own_language(self):
        for code, path in _existing().items():
            with self.subTest(lang=code):
                name = "README.md" if code == "fr" else f"README.{code}.md"
                self.assertIn(f"]({name})", _read(path).split("\n## ")[0])

    def test_each_translation_keeps_to_the_script_of_its_language(self):
        for code, path in _existing().items():
            allowed = SCRIPTS.get(code, set()) | {"LATIN"}
            lines = [line for line in _read(path).split("\n") if not line.startswith("[Français]")]
            text = "\n".join(lines)
            found = {unicodedata.name(c, "?").split()[0] for c in text if ord(c) > 127 and unicodedata.category(c)[0] == "L"}
            with self.subTest(lang=code):
                self.assertEqual(found - allowed, set())

    def test_all_fifteen_readmes_point_to_the_guide_of_their_own_language(self):
        for code, path in ALL_READMES.items():
            with self.subTest(lang=code):
                text = _read(path)
                if code == "fr":
                    self.assertIn("(README-LINUX.md)", text)
                else:
                    self.assertIn(f"(README-LINUX.{code}.md)", text)
                self.assertRegex(text, r"🐧 \*\*Linux\*\* : \[README-LINUX\]")


if __name__ == "__main__":
    unittest.main()
