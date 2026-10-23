"""Dépendances et cookies sous Linux : testés sur tous les systèmes en simulant IS_WINDOWS = False."""
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


class LinuxInstallCommandTests(unittest.TestCase):
    ALL = ["AtomicParsley", "MKVToolNix", "aria2"]

    def test_command_per_package_manager(self):
        self.assertEqual(m.linux_install_command(self.ALL, "apt"), "sudo apt install aria2 atomicparsley mkvtoolnix")
        self.assertEqual(m.linux_install_command(self.ALL, "dnf"), "sudo dnf install AtomicParsley aria2 mkvtoolnix")
        self.assertEqual(m.linux_install_command(self.ALL, "pacman"),
                         "sudo pacman -S aria2 atomicparsley mkvtoolnix-cli")
        self.assertEqual(m.linux_install_command(self.ALL, "zypper"),
                         "sudo zypper install AtomicParsley aria2 mkvtoolnix")

    def test_only_the_missing_tools_are_listed(self):
        self.assertEqual(m.linux_install_command(["aria2"], "apt"), "sudo apt install aria2")

    def test_ffmpeg_and_deno_are_never_in_the_command(self):
        """Ces deux-là sont téléchargés par l'assistant : la commande ne les cite pas."""
        self.assertIsNone(m.linux_install_command(["ffmpeg", "ffprobe", "deno"], "apt"))

    def test_unknown_manager_or_nothing_to_install_gives_none(self):
        with mock.patch.object(m, "linux_package_manager", return_value=None):
            self.assertIsNone(m.linux_install_command(self.ALL))
        self.assertIsNone(m.linux_install_command([], "apt"))
        self.assertIsNone(m.linux_install_command(self.ALL, "emerge"))

    def test_the_manager_is_detected_from_the_path(self):
        found = {"dnf"}
        with mock.patch.object(m.shutil, "which", lambda name: "/usr/bin/" + name if name in found else None):
            self.assertEqual(m.linux_package_manager(), "dnf")
        with mock.patch.object(m.shutil, "which", return_value=None):
            self.assertIsNone(m.linux_package_manager())

    def test_the_command_is_displayed_never_run(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        for forbidden in ("pkexec", "sudo -S", "os.system("):
            self.assertNotIn(forbidden, source)


class DirectInstallTests(unittest.TestCase):
    def _dep(self, name):
        return next(d for d in m.DEPS if d["name"] == name)

    def test_deno_is_direct_everywhere(self):
        for windows in (True, False):
            with mock.patch.object(m, "IS_WINDOWS", windows):
                self.assertTrue(m.dep_direct(self._dep("deno")))

    def test_ffmpeg_is_direct_only_on_linux(self):
        for name in ("ffmpeg", "ffprobe"):
            with mock.patch.object(m, "IS_WINDOWS", True):
                self.assertFalse(m.dep_direct(self._dep(name)), "Windows : Chocolatey")
            with mock.patch.object(m, "IS_WINDOWS", False):
                self.assertTrue(m.dep_direct(self._dep(name)))
            with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "FFMPEG_URL", None):
                self.assertFalse(m.dep_direct(self._dep(name)), "architecture sans téléchargement officiel")

    def test_optional_tools_are_never_direct(self):
        for name in ("AtomicParsley", "MKVToolNix", "aria2"):
            with mock.patch.object(m, "IS_WINDOWS", False):
                self.assertFalse(m.dep_direct(self._dep(name)))


class LinuxBrowsersTests(unittest.TestCase):
    """La liste des navigateurs Linux (cinq par défaut, choix de l'utilisateur) est testée dans test_linux_browsers.py ;
    ici, ce qui doit rester vrai pour Windows et pour un réglage ancien."""

    def test_a_saved_browser_outside_the_list_is_kept(self):
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "load_config", return_value={}):
            self.assertIn("whale", m.visible_browsers(False, current="whale"))
            self.assertNotIn(m.BROWSER_OFF, m.visible_browsers(False, current=m.BROWSER_OFF))

    def test_windows_list_is_unchanged(self):
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertEqual(m.visible_browsers(False), ["firefox", "opera"])
            self.assertEqual(m.visible_browsers(True), ["firefox", "opera", "chrome", "edge", "brave"])

    def test_process_names_exist_for_every_linux_browser(self):
        if not m.IS_WINDOWS:
            for browser in m.LINUX_BROWSER_KEYS:
                self.assertIn(browser, m._BROWSER_EXES)


class LinuxCookieHintsTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")

    def test_locked_database_with_the_browser_running_names_the_system_monitor(self):
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "browser_process_count", return_value=7):
            hint = m._cookie_hint("sqlite3.OperationalError: database is locked", "chromium")
        self.assertIn("Chromium", hint)
        self.assertIn("7 processus", hint)
        self.assertIn("moniteur système", hint)
        self.assertNotIn("Gestionnaire des tâches", hint)

    def test_windows_hint_is_unchanged(self):
        with mock.patch.object(m, "IS_WINDOWS", True), mock.patch.object(m, "browser_process_count", return_value=7):
            hint = m._cookie_hint("sqlite3.OperationalError: database is locked", "edge")
        self.assertIn("Gestionnaire des tâches", hint)

    def test_keyring_failure_explains_the_desktop_keyring(self):
        with mock.patch.object(m, "IS_WINDOWS", False):
            for text in ("WARNING: cannot decrypt v11 cookies: no key found", "ERROR: Failed to decrypt with x"):
                hint = m._cookie_hint(text, "chrome")
                self.assertIn("GNOME Keyring", hint, text)
                self.assertIn("Firefox", hint)

    def test_cannot_decrypt_on_windows_keeps_its_old_behaviour(self):
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertEqual(m._cookie_hint("cannot decrypt v10 cookies: no key found", "chrome"), "")

    def test_hints_are_translated(self):
        m.load_lang("en")
        try:
            with mock.patch.object(m, "IS_WINDOWS", False):
                self.assertIn("key ring", m._cookie_hint("cannot decrypt v11 cookies: no key found", "brave"))
        finally:
            m.load_lang("fr")


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class LinuxWindowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _deps_window(self, installed=(), manager="apt"):
        with mock.patch.object(m, "IS_WINDOWS", False), \
                mock.patch.object(m, "dep_installed", side_effect=lambda exe: exe in installed), \
                mock.patch.object(m, "linux_package_manager", return_value=manager), \
                mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.DepsWindow(self.app)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def _row(self, win, name):
        return next(r for r in win._rows if r["dep"]["name"] == name)

    def test_ffmpeg_and_deno_are_installed_by_the_assistant(self):
        win = self._deps_window()
        for name in ("ffmpeg", "ffprobe", "deno"):
            btn = self._row(win, name)["btn"]
            self.assertEqual(btn.cget("text"), m.t("deps.btn_install"), name)
            self.assertEqual(str(btn.cget("state")), "normal", name)

    def test_optional_tools_point_to_their_official_site(self):
        win = self._deps_window()
        for name in ("AtomicParsley", "MKVToolNix", "aria2"):
            self.assertEqual(self._row(win, name)["btn"].cget("text"), m.t("deps.btn_open_site"), name)

    def test_there_is_no_chocolatey_nor_install_all_on_linux(self):
        win = self._deps_window()
        texts = []

        def walk(widget):
            for child in widget.winfo_children():
                try:
                    texts.append(str(child.cget("text")))
                except Exception:
                    pass
                walk(child)
        walk(win)
        joined = "\n".join(texts)
        self.assertNotIn("Chocolatey", joined)
        self.assertNotIn(m.t("deps.btn_install_all"), joined)
        self.assertIn(m.t("deps.linux_note"), joined)
        self.assertIn(m.t("deps.footnote_linux"), joined)

    def test_the_command_for_the_missing_optional_tools_is_shown_and_copied(self):
        win = self._deps_window(installed={"aria2c"})
        self.assertTrue(win._cmd_frame.winfo_manager())
        self.assertEqual(win._cmd_var.get(), "sudo apt install atomicparsley mkvtoolnix")
        win._copy_command()
        self.assertEqual(win.clipboard_get(), "sudo apt install atomicparsley mkvtoolnix")
        self.assertIn(m.t("deps.linux_command_copied"), win.log.get("1.0", "end"))

    def test_no_command_when_the_optional_tools_are_installed(self):
        win = self._deps_window(installed={"AtomicParsley", "mkvpropedit", "aria2c"})
        self.assertFalse(win._cmd_frame.winfo_manager())

    def test_unknown_package_manager_says_so_and_disables_the_copy(self):
        win = self._deps_window(manager=None)
        self.assertEqual(win._cmd_var.get(), m.t("deps.linux_no_manager"))
        self.assertEqual(str(win._btn_copy.cget("state")), "disabled")

    def test_windows_explorer_warning_is_shown_only_on_windows(self):
        app = self.app
        app._secondary_sel.set_options([("alang_fr", "FR")])
        app._secondary_sel.set_selected(["alang_fr"])
        app.var_embed_thumb.set(True)
        try:
            for windows in (True, False):
                with mock.patch.object(m, "IS_WINDOWS", windows):
                    app._update_cmd()
                self.assertEqual(bool(app._lbl_mkv_warn_main.winfo_manager()), windows, windows)
        finally:
            app.var_embed_thumb.set(False)
            app._secondary_sel.set_selected([])
            app._update_cmd()

    def _update_window(self):
        with mock.patch.object(m.UpdateWindow, "_show_version"), mock.patch.object(m.tk.Toplevel, "grab_set",
                                                                                  lambda self: None):
            win = m.UpdateWindow(self.app)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def test_replace_dialog_asks_for_exe_files_on_windows_and_any_file_elsewhere(self):
        win = self._update_window()
        for windows in (True, False):
            with mock.patch.object(m, "IS_WINDOWS", windows), \
                    mock.patch.object(m.filedialog, "askopenfilename", return_value="") as ask, \
                    mock.patch.object(win, "_show_version"):
                win._replace_exe()
            kw = ask.call_args.kwargs
            if windows:
                self.assertEqual(kw["title"], m.t("upd.replace_title_dialog"))
                self.assertIn(("*.exe"), [pattern for _label, pattern in kw["filetypes"]])
            else:
                self.assertEqual(kw["title"], m.t("upd.replace_title_dialog_linux"))
                self.assertNotIn(".exe", kw["title"])
                self.assertEqual([pattern for _label, pattern in kw["filetypes"]], ["*"])

    @unittest.skipIf(m.os.name == "nt", "droits d'exécution POSIX")
    def test_replaced_yt_dlp_becomes_executable_on_linux(self):
        import tempfile
        d = tempfile.mkdtemp()
        self.addCleanup(m.shutil.rmtree, d, ignore_errors=True)
        src, target = m.os.path.join(d, "yt-dlp_linux"), m.os.path.join(d, "yt-dlp")
        with open(src, "wb") as f:
            f.write(b"#!/bin/sh\n")
        m.os.chmod(src, 0o644)
        win = self._update_window()
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "YTDLP", target), \
                mock.patch.object(m.filedialog, "askopenfilename", return_value=src), \
                mock.patch.object(win, "_show_version"):
            win._replace_exe()
        self.assertEqual(m.os.stat(target).st_mode & 0o777, 0o755)

    def test_wizard_marks_unavailable_downloads(self):
        with mock.patch.object(m, "dep_installed", return_value=False), \
                mock.patch.object(m, "FFMPEG_URL", None), mock.patch.object(m, "DENO_URL", None), \
                mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.SetupWizardWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        self.assertFalse(win._items["ffmpeg"].get())
        self.assertFalse(win._items["deno"].get())
        self.assertEqual(win._items["ytdlp"].get(), not m.os.path.isfile(m.YTDLP))


class KeyringNoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not tk_available():
            raise unittest.SkipTest("pas d'affichage Tk disponible")
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_chromium_family_gets_the_keyring_note_and_firefox_none(self):
        frame = self.app._cookie_frame
        with mock.patch.object(m, "IS_WINDOWS", False):
            for browser in m._LINUX_KEYRING_BROWSERS:
                self.app.var_browser.set(browser)
                self.assertEqual(frame.note.cget("text"), m.t("cookie.note_keyring"), browser)
            for browser in ("firefox", m.BROWSER_OFF):
                self.app.var_browser.set(browser)
                self.assertFalse(frame.note.winfo_manager(), browser)
        self.app.var_browser.set(m.BROWSER_OFF)


if __name__ == "__main__":
    unittest.main()
