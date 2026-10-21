import json
import os
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


class VisibleBrowsersTests(unittest.TestCase):
    def setUp(self):
        m.save_config({})
        self.addCleanup(m.save_config, {})

    def test_blocked_browsers_are_hidden_by_default_on_windows(self):
        with mock.patch.object(m.sys, "platform", "win32"):
            self.assertFalse(m.show_blocked_browsers())

    def test_blocked_browsers_are_shown_by_default_elsewhere(self):
        for platform in ("linux", "darwin"):
            with mock.patch.object(m.sys, "platform", platform):
                self.assertTrue(m.show_blocked_browsers(), platform)

    def test_the_saved_choice_wins_over_the_platform_default(self):
        with mock.patch.object(m.sys, "platform", "win32"):
            m.save_config({"show_blocked_browsers": True})
            self.assertTrue(m.show_blocked_browsers())
        with mock.patch.object(m.sys, "platform", "linux"):
            m.save_config({"show_blocked_browsers": False})
            self.assertFalse(m.show_blocked_browsers())

    def test_hidden_list_keeps_firefox_and_opera(self):
        self.assertEqual(m.visible_browsers(False), ["firefox", "opera"])

    def test_shown_list_has_every_browser(self):
        self.assertEqual(set(m.visible_browsers(True)), {"firefox", "opera", "chrome", "edge", "brave"})

    def test_the_current_choice_never_disappears(self):
        self.assertIn("chrome", m.visible_browsers(False, current="chrome"))
        self.assertNotIn("edge", m.visible_browsers(False, current="chrome"))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class BrowserComboTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        m.save_config({"show_blocked_browsers": False})
        self.addCleanup(m.save_config, {})
        self.var = m.tk.StringVar(master=self.app, value=m.BROWSER_OFF)
        self.combo = m._browser_combo(self.app, self.var)
        self.addCleanup(self.combo.destroy)

    def _values(self):
        return list(self.combo.cget("values"))

    def test_list_without_blocked_browsers(self):
        self.assertEqual(self._values(), [m.t("opts.cookies_disabled"), "firefox", "opera"])

    def test_toggling_the_option_updates_open_lists(self):
        win = m.BrowserOptionsWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        win.var.set(True)
        win._toggle()
        self.assertEqual(set(self._values()), {m.t("opts.cookies_disabled"), "firefox", "opera", "chrome", "edge", "brave"})
        self.assertTrue(m.load_config()["show_blocked_browsers"])
        win.var.set(False)
        win._toggle()
        self.assertEqual(self._values(), [m.t("opts.cookies_disabled"), "firefox", "opera"])

    def test_a_saved_blocked_browser_stays_selectable_and_then_leaves_the_list(self):
        self.var.set("chrome")
        self.assertIn("chrome", self._values())
        self.var.set("firefox")
        self.assertNotIn("chrome", self._values())

    def test_destroyed_combos_are_forgotten(self):
        extra = m._browser_combo(self.app, m.tk.StringVar(master=self.app))
        extra.destroy()
        m.refresh_browser_combos()                             # ne doit pas lever d'erreur
        self.assertNotIn(extra, [cb for cb, _ in m._BROWSER_COMBOS])

    def test_window_explains_the_choice(self):
        win = m.BrowserOptionsWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        texts = []

        def walk(w):
            for child in w.winfo_children():
                try:
                    texts.append(str(child.cget("text")))
                except Exception:
                    pass
                walk(child)
        walk(win)
        self.assertIn(m.t("browsers.explain"), texts)
        self.assertIn(m.t("browsers.chk"), texts)

    def test_options_menu_has_the_entry(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn('label=t("toolbar.menu_browsers")', source)


class TranslationsTests(unittest.TestCase):
    def test_explanation_names_the_browsers_in_every_language(self):
        lang_dir = os.path.join(os.path.dirname(m.__file__), "lang")
        for name in sorted(os.listdir(lang_dir)):
            with self.subTest(lang=name):
                with open(os.path.join(lang_dir, name), encoding="utf-8") as f:
                    texts = json.load(f)
                for key in ("toolbar.menu_browsers", "browsers.title", "browsers.chk", "browsers.explain", "browsers.close"):
                    self.assertTrue(texts[key].strip(), key)
                for browser in ("Edge", "Chrome", "Brave", "Firefox", "Opera"):
                    self.assertIn(browser, texts["browsers.explain"])


if __name__ == "__main__":
    unittest.main()
