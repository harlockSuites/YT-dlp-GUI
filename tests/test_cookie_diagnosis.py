"""Diagnostic des cookies (0 cookie lu, trousseau de clés absent), couleur des avertissements, boutons des fenêtres."""
import time
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _luminance(hex_color):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class WarningColorTests(unittest.TestCase):
    def test_warning_text_is_readable_on_the_grey_of_the_windows_and_on_white(self):
        for background in ("#dcdad5", "#d9d9d9", "#f0f0f0", "#ffffff"):
            self.assertGreaterEqual(_contrast(m.WARN_TEXT, background), 4.5, background)

    def test_bright_orange_is_no_longer_used_as_text_on_light_backgrounds(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        for line in source.splitlines():
            if "foreground=" in line or "fg=" in line:
                self.assertNotIn("#f5a623", line)
                self.assertNotIn("#e67e22", line)
                self.assertNotIn("#b9770e", line)

    def test_the_log_windows_keep_their_bright_colours_on_dark_background(self):
        self.assertEqual(m._COOKIE_COLORS["untested"], "#f5a623")


class HintTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")
        self.addCleanup(m.load_lang, "fr")

    def test_zero_cookies_gets_its_own_explanation_even_with_a_robot_error(self):
        text = "Extracting cookies from firefox\nExtracted 0 cookies from firefox\nERROR: Sign in to confirm you're not a bot"
        hint = m._cookie_hint(text, "librewolf")
        self.assertIn("Extracted 0 cookies", hint)
        self.assertIn("LibreWolf", hint)
        self.assertIn("supprime", hint)
        self.assertNotEqual(hint, m.t("cookie.hint_bot"))

    def test_a_normal_extraction_is_not_flagged(self):
        self.assertEqual(m._cookie_hint("Extracted 49 cookies from firefox", "firefox"), "")
        self.assertEqual(m._cookie_hint("Extracted 10 cookies from firefox", "firefox"), "")

    def test_the_missing_desktop_keyring_is_explained_on_linux(self):
        with mock.patch.object(m, "IS_WINDOWS", False):
            for text in ("Extracting cookies from chromium\nERROR: Item does not exist!",
                         "ERROR: failed to read from keyring", "secretstorage not available"):
                hint = m._cookie_hint(text, "chromium")
                self.assertIn("Chromium", hint, text)
                self.assertIn("trousseau", hint, text)
                self.assertIn("Navigateurs pour les cookies", hint, text)

    def test_the_keyring_hint_does_not_claim_the_keyring_is_missing_or_locked(self):
        # Constaté dans la VM : le trousseau existait, déverrouillé ; la clé du navigateur n'existait pas encore
        # parce qu'il n'avait jamais été lancé. Le conseil dit donc d'abord de lancer le navigateur.
        hint = m.t("cookie.hint_keyring", browser="Chromium")
        self.assertNotIn("introuvable", hint)
        self.assertNotIn("verrouillé", hint)
        self.assertIn("jamais été lancé", hint)

    def test_librewolf_gets_its_own_note_on_linux_only(self):
        frame = types.SimpleNamespace(_var=types.SimpleNamespace(get=lambda: "librewolf"))
        with mock.patch.object(m, "IS_WINDOWS", False):
            self.assertEqual(m.CookieFrame._note_key(frame), "cookie.note_librewolf")
            frame._var = types.SimpleNamespace(get=lambda: "firefox")
            self.assertEqual(m.CookieFrame._note_key(frame), "")
            frame._var = types.SimpleNamespace(get=lambda: "chromium")
            self.assertEqual(m.CookieFrame._note_key(frame), "cookie.note_keyring")
        self.assertIn("LibreWolf", m.t("cookie.note_librewolf"))

    def test_windows_does_not_get_the_keyring_hint(self):
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertEqual(m._cookie_hint("ERROR: Item does not exist!", "chrome"), "")

    def test_the_hints_exist_in_every_language_with_the_same_placeholders(self):
        import json
        import os
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lang")
        for name in sorted(os.listdir(base)):
            with open(os.path.join(base, name), encoding="utf-8") as f:
                data = json.load(f)
            for key in ("cookie.hint_zero", "cookie.hint_keyring"):
                self.assertIn("{browser}", data[key], (name, key))
                self.assertIn("Item does not exist" if key.endswith("keyring") else "Extracted 0 cookies", data[key], (name, key))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _check(self, browser, **result):
        frame = self.app._cookie_frame
        self.app.var_browser.set(browser)
        done = types.SimpleNamespace(returncode=0, stderr=b"", stdout=b"")
        for key, value in result.items():
            setattr(done, key, value)
        with mock.patch.object(m.subprocess, "run", return_value=done) as run:
            self.app.after(10, frame.check)
            self._pump(lambda: frame.state in ("ok", "fail"))
        self.addCleanup(self.app.var_browser.set, m.BROWSER_OFF)
        return frame, run

    def _pump(self, until, timeout=5):
        """Boucle d'évènements réelle : le test de cookies répond depuis un autre thread (comme dans les autres tests)."""
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)
        self.app.after(20, tick)
        self.app.mainloop()

    def test_a_browser_that_gave_zero_cookies_is_not_green(self):
        frame, run = self._check("firefox", stdout=b"Extracting cookies from firefox\nExtracted 0 cookies from firefox\n")
        self.assertEqual(frame.state, "fail")
        self.assertIn("Extracted 0 cookies", frame.detail)
        self.assertNotIn("--quiet", run.call_args.args[0], "sans --quiet, yt-dlp annonce le nombre de cookies")

    def test_a_browser_that_gave_cookies_is_green(self):
        frame, _ = self._check("firefox", stdout=b"Extracted 49 cookies from firefox\n")
        self.assertEqual(frame.state, "ok")

    def test_the_keyring_failure_shows_the_explanation_in_the_tooltip(self):
        with mock.patch.object(m, "IS_WINDOWS", False):
            frame, _ = self._check("chromium", returncode=1,
                                   stderr=b"Extracting cookies from chromium\nERROR: Item does not exist!\n")
        self.assertEqual(frame.state, "fail")
        self.assertIn("trousseau", frame.detail)
        self.assertIn("jamais été lancé", frame.detail)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WindowButtonsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _buttons_inside(self, win, buttons):
        for _ in range(30):
            self.app.update()
        bottom = win.winfo_rooty() + win.winfo_height()
        for b in buttons:
            self.assertTrue(b.winfo_viewable(), b)
            self.assertLessEqual(b.winfo_rooty() + b.winfo_height(), bottom, f"{b} dépasse la fenêtre")

    def test_the_queue_window_always_shows_its_buttons(self):
        for geometry in ("860x520", "640x400", "640x300"):
            win = m.DownloadQueueWindow(self.app, [], lambda: [])
            self.addCleanup(lambda w=win: w.winfo_exists() and w.destroy())
            win.minsize(1, 1)
            win.geometry(geometry)
            self._buttons_inside(win, (win.btn_pause, win.btn_skip, win.btn_close))

    def test_the_debug_log_window_always_shows_its_buttons(self):
        insp = m.PlaylistInspectorWindow(self.app, outdir="")
        self.addCleanup(insp.destroy)
        insp._toggle_log()
        win = insp._log_win
        buttons = [w for frame in win.winfo_children() for w in frame.winfo_children()
                   if w.winfo_class() == "TButton"]
        self.assertEqual(len(buttons), 2)
        for geometry in ("780x400", "400x200", "420x150"):
            win.minsize(1, 1)
            win.geometry(geometry)
            self._buttons_inside(win, buttons)


if __name__ == "__main__":
    unittest.main()
