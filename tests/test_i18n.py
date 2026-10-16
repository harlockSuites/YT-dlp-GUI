import glob
import json
import os
import re
import string
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()
LANG_DIR = os.path.join(ROOT, "lang")
def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


LANGS = {os.path.basename(f)[:-5]: json.loads(_read(f))
         for f in sorted(glob.glob(os.path.join(LANG_DIR, "*.json")))}
SRC = _read(os.path.join(ROOT, "yt-dlp-gui.pyw"))


def _placeholders(text):
    return sorted(f for _, f, _, _ in string.Formatter().parse(text) if f)


class I18nTests(unittest.TestCase):
    def test_fifteen_languages(self):
        expected = {"fr", "en", "es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko", "fil"}
        self.assertEqual(set(LANGS), expected)

    def test_same_keys_in_every_language(self):
        base = set(LANGS["fr"])
        for code, strings in LANGS.items():
            with self.subTest(lang=code):
                self.assertEqual(base - set(strings), set(), "clés manquantes")
                self.assertEqual(set(strings) - base, set(), "clés en trop")

    def test_same_placeholders_in_every_language(self):
        for key, ref in LANGS["fr"].items():
            for code, strings in LANGS.items():
                with self.subTest(key=key, lang=code):
                    self.assertEqual(_placeholders(strings[key]), _placeholders(ref))

    def test_no_empty_translation(self):
        for code, strings in LANGS.items():
            for key, value in strings.items():
                with self.subTest(lang=code, key=key):
                    self.assertTrue(str(value).strip())

    def test_keys_used_in_code_exist(self):
        used = set(re.findall(r'\b(?:t|_nt)\(\s*"([a-z0-9_.]+)"', SRC))
        used |= {f"insp.cookie_dot_{s}" for s in ("off", "untested", "testing", "ok", "fail")}
        self.assertEqual(sorted(k for k in used if k not in LANGS["fr"]), [])

    def test_t_falls_back_to_key_and_formats(self):
        self.assertEqual(m.t("cle.inexistante"), "cle.inexistante")
        self.assertIn("3", m.t("insp.status_done", n=3))


if __name__ == "__main__":
    unittest.main()
