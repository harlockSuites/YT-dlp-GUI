"""Aucun texte visible en dur dans l'interface : tout passe par les fichiers de langue (15 langues)."""
import json
import os
import re
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()
LANG_DIR = os.path.join(ROOT, "lang")
KEYS = ("ui.tab_options", "ui.log_frame", "ui.debug_log_frame")
ALLOWED_LITERALS = {"Langue / Language"}   # sélecteur de langue : volontairement bilingue


def _langs():
    out = {}
    for name in sorted(os.listdir(LANG_DIR)):
        if name.endswith(".json"):
            with open(os.path.join(LANG_DIR, name), encoding="utf-8") as f:
                out[name[:-5]] = json.load(f)
    return out


class UiTextsTests(unittest.TestCase):
    def test_the_three_labels_exist_in_every_language(self):
        langs = _langs()
        self.assertEqual(len(langs), 15)
        for code, data in langs.items():
            for key in KEYS:
                self.assertTrue(data[key].strip(), (code, key))

    def test_french_keeps_exactly_the_old_wording(self):
        data = _langs()["fr"]
        self.assertEqual((data["ui.tab_options"], data["ui.log_frame"], data["ui.debug_log_frame"]),
                         ("Options", "Journal", "Journal de debug"))

    def test_other_languages_are_really_translated(self):
        langs = _langs()
        english_or_french = {langs["fr"][k] for k in KEYS} | {langs["en"][k] for k in KEYS}
        for code in ("es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko"):
            for key in KEYS:
                self.assertNotIn(langs[code][key], {"Journal de debug"}, (code, key))
        self.assertEqual(langs["ru"]["ui.log_frame"], "Журнал")
        self.assertEqual(langs["ja"]["ui.tab_options"], "オプション")
        self.assertNotEqual(langs["es"]["ui.tab_options"], langs["fr"]["ui.tab_options"])
        self.assertTrue(english_or_french)

    def test_the_log_labels_follow_the_other_log_texts_of_the_same_language(self):
        for code, data in _langs().items():
            self.assertEqual(data["ui.log_frame"], data["dlq.log_frame_label"], code)
            self.assertTrue(data["insp.debug_log_title"].startswith(data["ui.debug_log_frame"]), code)

    def test_no_visible_text_is_written_in_the_source(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        literals = set(re.findall(r'\btext="([^"{}]*[A-Za-zÀ-ÿ]{3,}[^"{}]*)"', source))
        self.assertEqual(literals - ALLOWED_LITERALS, set(), "texte visible en dur : passer par t('…')")


if __name__ == "__main__":
    unittest.main()
