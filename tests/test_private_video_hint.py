import unittest
from unittest import mock

from tests._loader import load_gui

m = load_gui()

PRIVATE = "ERROR: [youtube] J7Nb13oYwjc: Private video"
PRIVATE_SIGN_IN = "ERROR: [youtube] J7Nb13oYwjc: Private video. Sign in if you've been granted access to this video"


class PrivateVideoHintTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")
        patcher = mock.patch.object(m, "browser_process_count", return_value=0)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_private_video_with_cookies_asks_for_the_right_account(self):
        for text in (PRIVATE, PRIVATE_SIGN_IN):
            hint = m._cookie_hint(text, "firefox")
            self.assertIn("privée", hint)
            self.assertIn("Firefox", hint)                    # nom du navigateur choisi
            self.assertIn("bon compte", hint)
            self.assertIn("vous appartient", hint)

    def test_private_video_without_cookies_asks_to_pick_a_browser(self):
        hint = m._cookie_hint(PRIVATE, m.BROWSER_OFF)
        self.assertIn("privée", hint)
        self.assertIn("cadre Cookies", hint)
        self.assertEqual(hint, m.t("cookie.hint_private_off"))

    def test_a_plain_unavailable_video_is_not_called_private(self):
        self.assertEqual(m._cookie_hint("ERROR: [youtube] J7Nb13oYwjc: Video unavailable", "firefox"), "")

    def test_the_other_hints_are_unchanged(self):
        self.assertIn("restriction d'âge", m._cookie_hint("This video is age-restricted", "firefox"))
        self.assertIn("robot", m._cookie_hint("Sign in to confirm you're not a bot", "firefox").lower())

    def test_every_language_has_both_texts(self):
        import json
        import os
        lang_dir = os.path.join(os.path.dirname(m.__file__), "lang")
        for name in sorted(os.listdir(lang_dir)):
            with self.subTest(lang=name):
                with open(os.path.join(lang_dir, name), encoding="utf-8") as f:
                    texts = json.load(f)
                self.assertIn("{browser}", texts["cookie.hint_private"])
                self.assertNotIn("{browser}", texts["cookie.hint_private_off"])


if __name__ == "__main__":
    unittest.main()
