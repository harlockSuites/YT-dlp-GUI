import json
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

SHOW_URL = "https://www.youtube.com/show/VLPLHovnlOusNLgvAbnxluXCVB3KLj8e4QB-?sbp=KgtId0FQTGtfc1Ezd0AB"

# `yt-dlp -J --flat-playlist` sur l'adresse brute d'une série : titre « show », 9 éléments
SHOW = {
    "_type": "playlist", "id": "show", "title": "show", "playlist_count": 1,
    "entries": [{"id": f"vid{n}", "title": f"THE AMAZING DIGITAL CIRCUS {n}"} for n in range(9)],
}


class ShowUrlTests(unittest.TestCase):
    def test_raw_show_address_is_a_playlist_address(self):
        self.assertTrue(m.is_playlist_url(SHOW_URL))
        self.assertTrue(m.is_playlist_url("https://youtube.com/show/VLPLabc"))

    def test_official_and_video_addresses_are_unchanged(self):
        self.assertTrue(m.is_playlist_url("https://youtube.com/playlist?list=PLabc&si=xyz"))
        self.assertFalse(m.is_playlist_url("https://www.youtube.com/watch?v=abc&list=PLabc"))
        self.assertFalse(m.is_playlist_url("https://www.youtube.com/watch?v=rZgDl8zMCNY"))
        self.assertFalse(m.is_playlist_url("https://www.youtube.com/@Vinesauce"))

    def test_generic_show_title_is_dropped_and_all_entries_are_counted(self):
        self.assertEqual(m.playlist_summary(SHOW), {"title": "", "count": 9, "bad": 0})

    def test_a_real_title_that_happens_to_be_show_is_kept(self):
        info = dict(SHOW, id="PLabc")
        self.assertEqual(m.playlist_summary(info)["title"], "show")


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class ShowUrlMessageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_message_for_an_untitled_series(self):
        shown = []
        done = types.SimpleNamespace(returncode=0, stdout=json.dumps(SHOW), stderr="")
        with mock.patch.object(m.subprocess, "run", return_value=done), \
                mock.patch.object(self.app, "after", side_effect=lambda ms, fn=None, *a: fn(*a)), \
                mock.patch.object(self.app, "_show_inspect_box", side_effect=lambda *a: shown.append(a)), \
                mock.patch.object(self.app, "_log"):
            self.app._inspect_playlist(SHOW_URL, [], "firefox")
        text = shown[0][0]
        self.assertIn(m.t("inspect.playlist_untitled"), text)
        self.assertIn("9 vidéo(s)", text)
        self.assertNotIn("show", text.lower().replace("sans titre", ""))


if __name__ == "__main__":
    unittest.main()
