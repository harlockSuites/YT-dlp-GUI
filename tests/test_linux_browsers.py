"""Navigateurs pour les cookies sous Linux : cinq par défaut, choix parmi onze dans une fenêtre des options."""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

KEYS = ["firefox", "chrome", "chromium", "brave", "vivaldi", "opera", "edge", "librewolf", "waterfox", "floorp", "zen"]
DEFAULT5 = ["firefox", "chrome", "chromium", "brave", "vivaldi"]


class CatalogTests(unittest.TestCase):
    def test_eleven_browsers_in_a_fixed_order_with_five_by_default(self):
        self.assertEqual(list(m.LINUX_BROWSER_KEYS), KEYS)
        self.assertEqual(list(m.LINUX_DEFAULT_BROWSERS), DEFAULT5)
        self.assertEqual(len(set(m.LINUX_BROWSER_KEYS)), 11)

    def test_yt_dlp_names_are_the_ones_it_accepts(self):
        """Noms de navigateur acceptés par --cookies-from-browser (yt_dlp/cookies.py : SUPPORTED_BROWSERS)."""
        accepted = {"brave", "chrome", "chromium", "edge", "opera", "vivaldi", "whale", "firefox", "safari"}
        for _key, _label, ytdlp, dirs in m.LINUX_BROWSER_CATALOG:
            self.assertIn(ytdlp, accepted)
            self.assertTrue(dirs)

    def test_natives_use_their_own_name_and_forks_are_firefox_by_path(self):
        for key, _label, ytdlp, _dirs in m.LINUX_BROWSER_CATALOG:
            if key in ("librewolf", "waterfox", "floorp", "zen"):
                self.assertEqual(ytdlp, "firefox", key)
            else:
                self.assertEqual(ytdlp, key)

    def test_chromium_family_is_the_keyring_family(self):
        self.assertEqual(set(m._LINUX_KEYRING_BROWSERS), {"chrome", "chromium", "brave", "vivaldi", "opera", "edge"})


class SelectionTests(unittest.TestCase):
    def test_default_is_the_five_most_used(self):
        self.assertEqual(m.selected_linux_browsers({}), DEFAULT5)

    def test_the_user_choice_is_kept_in_catalog_order_and_unknown_names_dropped(self):
        self.assertEqual(m.selected_linux_browsers({"linux_browsers": ["zen", "edge", "firefox", "netscape"]}),
                         ["firefox", "edge", "zen"])

    def test_an_empty_choice_is_respected_but_a_bad_value_falls_back_to_the_default(self):
        self.assertEqual(m.selected_linux_browsers({"linux_browsers": []}), [])
        for bad in ("firefox", 3, None, {"a": 1}):
            self.assertEqual(m.selected_linux_browsers({"linux_browsers": bad}), DEFAULT5, bad)

    def test_lists_follow_the_selection_and_never_drop_the_current_choice(self):
        with mock.patch.object(m, "IS_WINDOWS", False), \
                mock.patch.object(m, "load_config", return_value={"linux_browsers": ["firefox", "opera"]}):
            self.assertEqual(m.visible_browsers(False), ["firefox", "opera"])
            self.assertEqual(m.visible_browsers(True, current="brave"), ["firefox", "opera", "brave"])
            self.assertEqual(m.visible_browsers(True, current="opera"), ["firefox", "opera"])
            self.assertEqual(m.visible_browsers(True, current=m.BROWSER_OFF), ["firefox", "opera"])

    def test_default_lists_without_any_setting(self):
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "load_config", return_value={}):
            self.assertEqual(m.visible_browsers(False), DEFAULT5)


class ProfileFoldersTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="home-")
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        self.env = {"XDG_CONFIG_HOME": ""}
        patcher = mock.patch.dict(os.environ, {"HOME": self.home, "USERPROFILE": self.home})
        patcher.start()
        self.addCleanup(patcher.stop)

    def _mk(self, *parts):
        path = os.path.join(self.home, *parts)
        os.makedirs(path)
        return path

    def test_native_browsers_are_found_by_the_folders_yt_dlp_reads(self):
        self.assertFalse(m.linux_browser_found("chromium", self.env))
        self._mk(".config", "chromium")
        self._mk(".config", "BraveSoftware", "Brave-Browser")
        self._mk(".config", "microsoft-edge")
        for key in ("chromium", "brave", "edge"):
            self.assertTrue(m.linux_browser_found(key, self.env), key)
        self.assertFalse(m.linux_browser_found("vivaldi", self.env))

    def test_firefox_is_found_in_every_layout_yt_dlp_knows(self):
        for parts in ((".mozilla", "firefox"), (".config", "mozilla", "firefox"),
                      ("snap", "firefox", "common", ".mozilla", "firefox"),
                      (".var", "app", "org.mozilla.firefox", ".mozilla", "firefox")):
            shutil.rmtree(self.home, ignore_errors=True)
            os.makedirs(self.home)
            self._mk(*parts)
            self.assertTrue(m.linux_browser_found("firefox", self.env), parts)

    def test_xdg_config_home_is_followed_only_when_absolute(self):
        custom = os.path.join(self.home, "cfg")
        self.assertEqual(m.linux_browser_dirs("chromium", {"XDG_CONFIG_HOME": custom}), [os.path.join(custom, "chromium")])
        self.assertEqual(m.linux_browser_dirs("chromium", {"XDG_CONFIG_HOME": "relatif"}),
                         [os.path.join(self.home, ".config", "chromium")])
        self.assertEqual(m.linux_browser_dirs("inconnu", self.env), [])


class CookieArgumentTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="home-")
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"HOME": self.home, "USERPROFILE": self.home, "XDG_CONFIG_HOME": ""})
        patcher.start()
        self.addCleanup(patcher.stop)
        p = mock.patch.object(m, "IS_WINDOWS", False)
        p.start()
        self.addCleanup(p.stop)

    def test_natives_and_unknown_names_are_passed_as_they_are(self):
        for browser in ("firefox", "chrome", "chromium", "brave", "vivaldi", "opera", "edge", "whale"):
            self.assertEqual(m.cookie_browser_arg(browser), browser)

    def _profile(self, *parts, age=0):
        """Crée <maison>/<parts>/cookies.sqlite (plus ancien de `age` secondes) et renvoie le dossier du profil."""
        folder = os.path.join(self.home, *parts)
        os.makedirs(folder, exist_ok=True)
        db = os.path.join(folder, "cookies.sqlite")
        with open(db, "wb") as f:
            f.write(b"")
        if age:
            past = os.path.getmtime(db) - age
            os.utime(db, (past, past))
        return folder

    def test_a_firefox_fork_is_read_by_the_folder_of_its_profile(self):
        folder = self._profile(".librewolf", "abc123.default")
        self.assertEqual(m.cookie_browser_arg("librewolf"), f"firefox:{folder}")

    def test_the_real_layout_of_librewolf_flatpak_is_found(self):
        """Relevé dans la VM le 2026-10-23 : le profil est sous config/librewolf/librewolf, et ~/.librewolf est vide."""
        os.makedirs(os.path.join(self.home, ".var", "app", "io.gitlab.librewolf-community", ".librewolf"))
        folder = self._profile(".var", "app", "io.gitlab.librewolf-community", "config", "librewolf", "librewolf",
                               "ysn3qqrm.default-release")
        self.assertEqual(m.cookie_browser_arg("librewolf"), f"firefox:{folder}")
        self.assertTrue(m.linux_browser_found("librewolf", {"XDG_CONFIG_HOME": ""}))

    def test_the_xdg_layout_of_a_normal_installation_is_found(self):
        folder = self._profile(".config", "waterfox", "waterfox", "x.default-release")
        self.assertEqual(m.cookie_browser_arg("waterfox"), f"firefox:{folder}")

    def test_another_flatpak_fork_is_found_when_the_usual_folder_is_missing(self):
        folder = self._profile(".var", "app", "app.zen_browser.zen", ".zen", "p1.Default (release)")
        self.assertEqual(m.cookie_browser_arg("zen"), f"firefox:{folder}")

    def test_the_most_recently_used_profile_wins(self):
        self._profile(".floorp", "old.default", age=5000)
        newer = self._profile(".var", "app", "one.ablaze.floorp", "config", "floorp", "floorp", "new.default", age=10)
        self.assertEqual(m.cookie_browser_arg("floorp"), f"firefox:{newer}")

    def test_a_database_buried_too_deep_is_ignored(self):
        self._profile(".zen", "a", "b", "c", "d")
        self.assertEqual(m.cookie_browser_arg("zen"), "firefox:" + os.path.join(self.home, ".zen"))

    def test_a_fork_without_profile_yet_points_to_its_first_existing_folder(self):
        folder = os.path.join(self.home, ".var", "app", "net.waterfox.waterfox", ".waterfox")
        os.makedirs(folder)
        self.assertEqual(m.cookie_browser_arg("waterfox"), f"firefox:{folder}")

    def test_a_missing_fork_still_gets_a_path_so_yt_dlp_can_explain(self):
        self.assertEqual(m.cookie_browser_arg("waterfox"), "firefox:" + os.path.join(self.home, ".waterfox"))

    def test_windows_never_changes_the_value(self):
        with mock.patch.object(m, "IS_WINDOWS", True):
            for browser in ("firefox", "librewolf", "zen", "edge"):
                self.assertEqual(m.cookie_browser_arg(browser), browser)

    def test_the_labels_name_the_browser_properly_and_windows_keeps_its_capitalisation(self):
        self.assertEqual(m.browser_label("zen"), "Zen Browser")
        self.assertEqual(m.browser_label("chrome"), "Google Chrome")
        self.assertEqual(m.browser_label("whale"), "Whale")
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertEqual(m.browser_label("chrome"), "Chrome")

    def test_every_yt_dlp_call_goes_through_the_helper(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn('"--cookies-from-browser", browser]', source)
        self.assertNotIn('"--cookies-from-browser", browser,', source)
        self.assertGreaterEqual(source.count('"--cookies-from-browser", cookie_browser_arg(browser)'), 9)

    def test_the_failing_hint_names_the_fork_properly(self):
        m.load_lang("fr")
        hint = m._cookie_hint("ERROR: could not find firefox cookies database in '/x'", "zen")
        self.assertIn("Zen Browser", hint)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        m.save_config({})
        self.addCleanup(m.save_config, {})
        p = mock.patch.object(m, "IS_WINDOWS", False)
        p.start()
        self.addCleanup(p.stop)
        self.var = m.tk.StringVar(master=self.app, value=m.BROWSER_OFF)
        self.combo = m._browser_combo(self.app, self.var)
        self.addCleanup(self.combo.destroy)

    def _window(self, found=()):
        with mock.patch.object(m, "linux_browser_found", side_effect=lambda key, env=None: key in found):
            win = m.LinuxBrowsersWindow(self.app)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def _values(self):
        return list(self.combo.cget("values"))

    def test_the_combobox_starts_with_the_five_defaults(self):
        self.assertEqual(self._values(), [m.t("opts.cookies_disabled")] + DEFAULT5)

    def test_the_window_shows_eleven_browsers_with_the_defaults_ticked(self):
        win = self._window()
        self.assertEqual(list(win._vars), KEYS)
        self.assertEqual([k for k, v in win._vars.items() if v.get()], DEFAULT5)

    def test_ticking_a_browser_updates_the_open_lists_and_the_saved_setting(self):
        win = self._window()
        win._vars["zen"].set(True)
        win._vars["brave"].set(False)
        win._save()
        self.assertEqual(self._values(), [m.t("opts.cookies_disabled"), "firefox", "chrome", "chromium", "vivaldi", "zen"])
        self.assertEqual(m.load_config()["linux_browsers"], ["firefox", "chrome", "chromium", "vivaldi", "zen"])

    def test_the_browser_in_use_stays_in_the_list_when_unticked(self):
        self.var.set("brave")
        win = self._window()
        win._vars["brave"].set(False)
        win._save()
        self.assertIn("brave", self._values())

    def test_reset_restores_the_five_defaults(self):
        win = self._window()
        for var in win._vars.values():
            var.set(True)
        win._save()
        self.assertEqual(len(self._values()), 12)
        win._reset()
        self.assertEqual(self._values(), [m.t("opts.cookies_disabled")] + DEFAULT5)
        self.assertEqual(m.load_config()["linux_browsers"], DEFAULT5)

    def test_found_browsers_are_marked(self):
        win = self._window(found={"firefox", "zen"})

        def texts(widget):
            for child in widget.winfo_children():
                try:
                    yield str(child.cget("text"))
                except Exception:
                    pass
                yield from texts(child)
        marked = [t for t in texts(win) if m.t("browsers.linux_found") in t]
        self.assertEqual(sorted(x.split()[0] for x in marked), ["Firefox", "Zen"])

    def test_the_options_menu_opens_this_window_on_linux_and_the_windows_one_on_windows(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn("(BrowserOptionsWindow if IS_WINDOWS else LinuxBrowsersWindow)(self)", source)


class TranslationsTests(unittest.TestCase):
    def test_the_new_texts_exist_in_every_language_and_name_the_five_defaults(self):
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lang")
        for name in sorted(os.listdir(base)):
            with open(os.path.join(base, name), encoding="utf-8") as f:
                data = json.load(f)
            for key in ("browsers.linux_explain", "browsers.linux_reset", "browsers.linux_found"):
                self.assertTrue(data[key].strip(), (name, key))
            for browser in ("Firefox", "Google Chrome", "Chromium", "Brave", "Vivaldi", "LibreWolf", "Zen Browser"):
                self.assertIn(browser, data["browsers.linux_explain"], (name, browser))


if __name__ == "__main__":
    unittest.main()
