import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _labels(widget):
    texts = []
    for child in widget.winfo_children():
        try:
            texts.append(str(child.cget("text")))
        except Exception:
            pass
        texts.extend(_labels(child))
    return texts


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class DepsLevelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _window(self, installed=()):
        with mock.patch.object(m, "choco_available", return_value=False), \
                mock.patch.object(m, "dep_installed", side_effect=lambda exe: exe in installed), \
                mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.DepsWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        return win

    def _status(self, win, name):
        row = next(r for r in win._rows if r["dep"]["name"] == name)
        return str(row["lbl_status"].cget("text")), str(row["lbl_status"].cget("foreground"))

    def test_only_ffmpeg_and_ffprobe_are_shown_as_missing_in_red(self):
        win = self._window()
        for name in ("ffmpeg", "ffprobe"):
            self.assertEqual(self._status(win, name), (m.t("deps.status_absent"), "#c0392b"))

    def test_optional_tools_do_not_look_like_errors(self):
        win = self._window()
        for name in ("AtomicParsley", "MKVToolNix", "aria2"):
            text, color = self._status(win, name)
            self.assertEqual(text, m.t("deps.status_optional"), name)
            self.assertNotEqual(color, "#c0392b", name)
            self.assertNotIn("✘", text)

    def test_deno_is_recommended_not_required(self):
        win = self._window()
        self.assertEqual(self._status(win, "deno")[0], m.t("deps.status_recommended"))

    def test_installed_tools_are_ok(self):
        win = self._window(installed=("AtomicParsley",))
        self.assertEqual(self._status(win, "AtomicParsley")[0], m.t("deps.status_ok"))

    def test_the_window_says_that_only_ffmpeg_is_essential(self):
        win = self._window()
        self.assertIn(m.t("deps.optional_note"), _labels(win))

    @mock.patch.object(m, "IS_WINDOWS", True)
    def test_missing_chocolatey_is_not_presented_as_a_warning(self):
        win = self._window()
        shown = [x for x in _labels(win) if x == m.t("deps.choco_warn")]
        self.assertEqual(len(shown), 1)
        self.assertNotIn("⚠", shown[0])

    def test_note_names_the_optional_tools_in_every_language(self):
        import json
        import os
        lang_dir = os.path.join(os.path.dirname(m.__file__), "lang")
        for name in sorted(os.listdir(lang_dir)):
            with self.subTest(lang=name):
                with open(os.path.join(lang_dir, name), encoding="utf-8") as f:
                    note = json.load(f)["deps.optional_note"]
                for tool in ("ffmpeg", "ffprobe", "Deno", "AtomicParsley", "MKVToolNix", "aria2"):
                    self.assertIn(tool, note)


if __name__ == "__main__":
    unittest.main()
