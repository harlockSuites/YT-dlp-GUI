import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

URL = "https://www.youtube.com/playlist?list=PLn0gNfHzKO0QhlQ8XO02Xr5dIyQHIH2_-&si=0aeIMAR17OlcLl-8"
PASTED = (f"Inspection : {URL}\nERROR: Could not copy Chrome cookie database. See  "
          "https://github.com/yt-dlp/yt-dlp/issues/7271  for more info\nEdge est encore en cours d'exécution")


class ExtractUrlTests(unittest.TestCase):
    def test_a_clean_url_is_unchanged(self):
        self.assertEqual(m.extract_url(URL), URL)
        self.assertEqual(m.extract_url("  " + URL + "  "), URL)

    def test_first_url_is_taken_from_pasted_text(self):
        self.assertEqual(m.extract_url(PASTED), URL)

    def test_trailing_punctuation_of_a_sentence_is_dropped(self):
        self.assertEqual(m.extract_url("regarde https://youtu.be/abc123, merci"), "https://youtu.be/abc123")
        self.assertEqual(m.extract_url("(voir https://youtu.be/abc123)"), "https://youtu.be/abc123")

    def test_text_without_url_and_empty_values_are_left_alone(self):
        self.assertEqual(m.extract_url("pas d'adresse ici"), "pas d'adresse ici")
        self.assertEqual(m.extract_url(""), "")
        self.assertEqual(m.extract_url(None), "")
        self.assertEqual(m.extract_url("abc123"), "abc123")


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class MainWindowUrlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def tearDown(self):
        self.app.var_url.set("")

    def test_reading_does_not_touch_the_field_but_returns_the_clean_url(self):
        self.app.var_url.set(PASTED)
        self.assertEqual(self.app._url(), URL)
        self.assertEqual(self.app.var_url.get(), PASTED)

    def test_actions_correct_the_field_on_screen(self):
        self.app.var_url.set(PASTED)
        self.assertEqual(self.app._url(fix=True), URL)
        self.assertEqual(self.app.var_url.get(), URL)

    def test_generated_command_uses_the_clean_url(self):
        self.app.var_url.set(PASTED)
        self.assertEqual(self.app._build_args()[-1], URL)

    def test_inspect_starts_with_the_clean_url(self):
        self.app.var_url.set(PASTED)
        with mock.patch.object(m.subprocess, "run") as run, mock.patch.object(m.threading, "Thread") as thread:
            self.app._inspect()
        self.assertEqual(self.app.var_url.get(), URL)
        thread.assert_called_once()


if __name__ == "__main__":
    unittest.main()
