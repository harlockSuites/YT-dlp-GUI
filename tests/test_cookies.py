import os
import shutil
import tempfile
import time
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()
REAL_PROCESS_COUNT = m.browser_process_count   # les tests de conseils le remplacent par un faux

CHROME_LOCKED = ("ERROR: Could not copy Chrome cookie database. "
                 "See https://github.com/yt-dlp/yt-dlp/issues/7271  for more info")


class CookieHintTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")
        patcher = mock.patch.object(m, "browser_process_count", return_value=0)   # indépendant des navigateurs ouverts
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_locked_database_gets_a_clear_localized_hint(self):
        hint = m._cookie_hint(CHROME_LOCKED, "brave")
        self.assertIn("Brave", hint)
        self.assertIn("Fermez-le complètement", hint)
        self.assertIn("Firefox", hint)

    def test_locked_database_with_the_browser_still_running_says_so(self):
        with mock.patch.object(m, "browser_process_count", return_value=7):
            hint = m._cookie_hint(CHROME_LOCKED, "edge")
        self.assertIn("Edge", hint)
        self.assertIn("7 processus", hint)
        self.assertIn("Gestionnaire des tâches", hint)
        self.assertIn("arrière-plan", hint)

    def test_process_count_matches_the_browser_programs(self):
        edge, firefox = m._BROWSER_EXES["edge"][0], m._BROWSER_EXES["firefox"][0]   # propres au système
        procs = [(1, 0, edge), (2, 1, edge), (3, 0, firefox), (4, 0, "notepad.exe")]
        with mock.patch.object(m, "_iter_processes", return_value=iter(procs)):
            self.assertEqual(REAL_PROCESS_COUNT("edge"), 2)
        with mock.patch.object(m, "_iter_processes", return_value=iter(procs)):
            self.assertEqual(REAL_PROCESS_COUNT("firefox"), 1)
        self.assertEqual(REAL_PROCESS_COUNT("inconnu"), 0)
        self.assertEqual(REAL_PROCESS_COUNT(""), 0)

    def test_process_count_never_raises(self):
        with mock.patch.object(m, "_iter_processes", side_effect=OSError("accès refusé")):
            self.assertEqual(REAL_PROCESS_COUNT("chrome"), 0)

    def test_real_process_listing_finds_this_python(self):
        names = {name for _pid, _parent, name in m._iter_processes()}
        self.assertTrue(any(n.startswith("python") for n in names), sorted(names)[:10])

    def test_other_cookie_errors(self):
        self.assertIn("Edge", m._cookie_hint("Failed to decrypt with DPAPI", "edge"))
        self.assertIn("Chrome", m._cookie_hint("ERROR: could not find chrome cookies database in ...", "chrome"))
        self.assertTrue(m._cookie_hint("sqlite3.OperationalError: database is locked", "chrome"))

    def test_rotated_session_asks_to_sign_in_again(self):
        text = "WARNING: [youtube] The provided YouTube account cookies are no longer valid. They have likely been rotated"
        hint = m._cookie_hint(text, "firefox")
        self.assertIn("Firefox", hint)
        self.assertIn("connecté", hint)

    def test_age_restriction_hint_depends_on_the_cookie_choice(self):
        text = "ERROR: [youtube] abc: Sign in to confirm your age. This video may be inappropriate for some users."
        on = m._cookie_hint(text, "firefox")
        off = m._cookie_hint(text, m.BROWSER_OFF)
        self.assertIn("Firefox", on)
        self.assertIn("voyant", on)
        self.assertIn("Cookies", off)
        self.assertNotEqual(on, off)
        self.assertEqual(m._cookie_hint(text, ""), off)

    def test_bot_check_hint(self):
        text = "ERROR: [youtube] abc: Sign in to confirm you’re not a bot. Use --cookies-from-browser"
        self.assertIn("robot", m._cookie_hint(text, "firefox"))

    def test_unrelated_errors_give_no_hint(self):
        for text in ("", None, "ERROR: Video unavailable", "HTTP Error 429: Too Many Requests"):
            self.assertEqual(m._cookie_hint(text, "firefox"), "")

    def test_hint_is_translated(self):
        m.load_lang("en")
        try:
            self.assertIn("Close it completely", m._cookie_hint(CHROME_LOCKED, "brave"))
        finally:
            m.load_lang("fr")


class PathRefreshTests(unittest.TestCase):
    def test_merge_adds_only_existing_new_directories(self):
        d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d1, ignore_errors=True)
        self.addCleanup(shutil.rmtree, d2, ignore_errors=True)
        first = os.path.join(os.sep, "existant")   # ni testé ni modifié : `current` est repris tel quel
        merged = m._merge_path(os.pathsep.join([first, d1]), [d1.upper(), d2, os.path.join(d2, "absent"), ""])
        parts = merged.split(os.pathsep)
        self.assertEqual(parts.count(d1), 1, "pas de doublon (casse ignorée)")
        self.assertIn(d2, parts)
        self.assertNotIn(os.path.join(d2, "absent"), parts, "dossier inexistant ignoré")
        self.assertEqual(parts[0], first)

    def test_tool_installed_after_launch_is_detected(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        exe_name = "outil-fictif-zz" + (".exe" if os.name == "nt" else "")
        path = os.path.join(d, exe_name)
        with open(path, "w") as f:
            f.write("x")
        os.chmod(path, 0o755)
        with mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", "")}), \
                mock.patch.object(m, "_registry_path_dirs", return_value=[d]):
            self.assertIsNone(shutil.which("outil-fictif-zz"), "absent du PATH du processus")
            self.assertTrue(m.dep_installed("outil-fictif-zz"), "trouvé grâce au PATH lu dans le registre")
            self.assertIn(d, os.environ["PATH"].split(os.pathsep))

    def test_tool_in_the_chocolatey_package_folder_is_found_without_path(self):
        """Paquet installé par un autre compte administrateur : son dossier n'est pas dans le PATH
        de la session courante (cas réel de Deno : lib\\deno\\deno.exe)."""
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        pkg = os.path.join(root, "lib", "outil-fictif-choco")
        os.makedirs(pkg)
        with open(os.path.join(pkg, "outil-fictif-choco.exe"), "w") as f:
            f.write("x")
        dep = {"name": "fictif", "exe": "outil-fictif-choco", "choco": "outil-fictif-choco"}
        m.DEPS.append(dep)
        self.addCleanup(m.DEPS.remove, dep)
        with mock.patch.dict(os.environ, {"ChocolateyInstall": root}), \
                mock.patch.object(m, "_refresh_process_path"):
            self.assertFalse(m.dep_installed("outil-absent-zz"))
            self.assertTrue(m.dep_installed("outil-fictif-choco"))
            self.assertIn(pkg, os.environ["PATH"].split(os.pathsep), "dossier ajouté pour yt-dlp")

    def test_deno_looks_in_the_usual_places(self):
        dep = next(d for d in m.DEPS if d["exe"] == "deno")
        paths = [p.lower() for p in m._known_exe_paths(dep)]
        self.assertTrue(any(p.endswith(os.path.join("lib", "deno", "deno.exe")) for p in paths))
        self.assertTrue(any(".deno" in p for p in paths))

    def test_registry_reader_is_safe_without_winreg_values(self):
        self.assertIsInstance(m._registry_path_dirs(), list)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class CookieFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls._no_browser = mock.patch.object(m, "browser_process_count", return_value=0)
        cls._no_browser.start()
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()
        cls._no_browser.stop()

    def _pump(self, until, timeout=5):
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)
        self.app.after(20, tick)
        self.app.mainloop()

    def test_main_window_has_the_same_cookie_frame_as_the_inspector(self):
        frame = self.app._cookie_frame
        self.assertIsInstance(frame, m.CookieFrame)
        self.assertEqual(frame.cget("text"), m.t("opts.label_cookies").rstrip(" :："))
        self.assertTrue(frame.dot.winfo_exists() and frame.button.winfo_exists())
        insp = m.PlaylistInspectorWindow(self.app)
        insp.withdraw()
        self.addCleanup(insp.destroy)
        self.assertIsInstance(insp._cookie_frame, m.CookieFrame)

    def test_states_follow_the_browser_choice(self):
        frame = self.app._cookie_frame
        self.app.var_browser.set(m.BROWSER_OFF)
        self.assertEqual(frame.state, "off")
        self.assertTrue(frame.warn.winfo_manager())
        self.app.var_browser.set("firefox")
        self.assertEqual(frame.state, "untested")
        self.assertFalse(frame.warn.winfo_manager(), "avertissement masqué quand un navigateur est choisi")
        self.app.var_browser.set(m.BROWSER_OFF)

    def test_known_browser_limits_are_shown_under_the_menu(self):
        frame = self.app._cookie_frame
        for browser in ("chrome", "edge", "brave"):
            self.app.var_browser.set(browser)
            self.assertTrue(frame.note.winfo_manager(), browser)
            self.assertEqual(frame.note.cget("text"), m.t("cookie.note_blocked"))
        self.assertIn("Firefox", m.t("cookie.note_blocked"))
        self.app.var_browser.set("opera")
        self.assertTrue(frame.note.winfo_manager())
        self.assertEqual(frame.note.cget("text"), m.t("cookie.note_closed"))
        for browser in ("firefox", m.BROWSER_OFF):
            self.app.var_browser.set(browser)
            self.assertFalse(frame.note.winfo_manager(), browser)
        self.app.var_browser.set(m.BROWSER_OFF)

    def test_check_success_turns_green(self):
        frame = self.app._cookie_frame
        self.app.var_browser.set("firefox")
        ok = types.SimpleNamespace(returncode=0, stderr=b"", stdout=b"")
        with mock.patch.object(m.subprocess, "run", return_value=ok):
            self.app.after(10, frame.check)
            self._pump(lambda: frame.state == "ok")
        self.assertEqual(frame.state, "ok")
        self.app.var_browser.set(m.BROWSER_OFF)

    def test_locked_chromium_database_shows_the_hint_in_the_tooltip(self):
        frame = self.app._cookie_frame
        self.app.var_browser.set("brave")
        bad = types.SimpleNamespace(returncode=1, stderr=CHROME_LOCKED.encode(), stdout=b"")
        with mock.patch.object(m.subprocess, "run", return_value=bad):
            self.app.after(10, frame.check)
            self._pump(lambda: frame.state == "fail")
        self.assertEqual(frame.state, "fail")
        tip = frame._tip_text()
        self.assertIn("Brave", tip)
        self.assertIn("Fermez-le complètement", tip)
        self.app.var_browser.set(m.BROWSER_OFF)

    def test_only_one_test_runs_at_a_time(self):
        frame = self.app._cookie_frame
        self.app.var_browser.set("firefox")
        frame.set_state("testing")
        with mock.patch.object(m.subprocess, "run") as run:
            frame.check()
        run.assert_not_called()
        self.app.var_browser.set(m.BROWSER_OFF)

    def test_download_log_shows_the_hint_once(self):
        app = self.app
        app.var_browser.set("brave")
        app._cookie_hint_shown = False
        app._on_output_line(CHROME_LOCKED)
        app._on_output_line(CHROME_LOCKED)
        text = app.log_text.get("1.0", "end")
        self.assertEqual(text.count("Fermez-le complètement"), 1)
        app.var_browser.set(m.BROWSER_OFF)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WindowSizeTests(unittest.TestCase):
    def test_default_size_is_comfortable_and_the_last_size_is_remembered(self):
        m.save_config({})
        app = m.YtDlpGui()   # fenêtre visible : Tk n'applique pas la géométrie d'une fenêtre masquée
        try:
            app.update()
            self.assertGreaterEqual(app.winfo_height(), 600, "plus la hauteur minimale de 420 px")
            # taille choisie compatible avec l'écran (celui d'un exécuteur CI est petit)
            w = min(1100, app.winfo_screenwidth() - 120)
            h = min(700, app.winfo_screenheight() - 220)
            size = f"{w}x{h}"
            app.geometry(size)
            app.update()
            app._on_close()
        except Exception:
            app.destroy()
            raise
        self.assertEqual(m.load_config()["window_size"], size)
        app2 = m.YtDlpGui()
        try:
            app2.update()
            self.assertEqual((app2.winfo_width(), app2.winfo_height()), (w, h))
        finally:
            app2.destroy()
            m.save_config({})

    def test_absurd_saved_size_is_ignored_or_clamped(self):
        m.save_config({"window_size": "9x9"})
        app = m.YtDlpGui()
        try:
            app.update()
            self.assertGreaterEqual(app.winfo_height(), 600)
        finally:
            app.destroy()
            m.save_config({})


if __name__ == "__main__":
    unittest.main()
