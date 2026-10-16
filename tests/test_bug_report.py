import os
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse

from tests._loader import load_gui, tk_available

m = load_gui()
HOME = os.path.expanduser("~")


class RedactTests(unittest.TestCase):
    def test_masks_home_private_folders_and_emails(self):
        text = (f"Fichier {HOME}\\Videos\\a.mp4 et D:/Exemple/Dossier Prive/b.mp3 "
                "contact: jean.dupont@example.com")
        out = m._redact(text, private=["D:/Exemple/Dossier Prive"])
        self.assertNotIn(HOME, out)
        self.assertNotIn("Dossier Prive", out)
        self.assertNotIn("example.com", out)
        self.assertIn("<folder>", out)
        self.assertIn("<email>", out)

    def test_masks_username(self):
        import getpass
        user = getpass.getuser()
        if len(user) < 3:
            self.skipTest("nom d'utilisateur trop court")
        self.assertNotIn(user.lower(), m._redact(f"salut {user}!").lower())

    def test_backslash_and_slash_variants(self):
        out = m._redact(r"C:\Users\Quelquun\Dossier\x et C:/Users/Quelquun/Dossier/y",
                        private=[r"C:\Users\Quelquun\Dossier"])
        self.assertNotIn("Quelquun", out)


class DiagnosticsTests(unittest.TestCase):
    def test_contains_environment_and_is_redacted(self):
        with mock.patch.object(m, "_ytdlp_version", return_value="2099.01.01"):
            report = m.collect_diagnostics(
                log_tail=f"erreur dans {HOME}\\x\nautre ligne",
                last_error="Traceback (most recent call last):\n  ValueError: boom",
                private=["E:/Mes videos"])
        for expected in (f"GUI version: {m.__version__}", "yt-dlp: 2099.01.01", "Python:", "OS:",
                         "--- Last internal error ---", "ValueError: boom", "--- Log (last lines) ---"):
            self.assertIn(expected, report)
        self.assertNotIn(HOME, report)

    def test_no_error_section_when_empty(self):
        with mock.patch.object(m, "_ytdlp_version", return_value="x"):
            report = m.collect_diagnostics()
        self.assertNotIn("Last internal error", report)
        self.assertNotIn("Log (last lines)", report)

    def test_config_exposes_only_safe_keys(self):
        m.save_config({"lang": "en", "outdir": "E:/prive", "browser": "firefox", "secret": "x"})
        try:
            with mock.patch.object(m, "_ytdlp_version", return_value="x"):
                report = m.collect_diagnostics()
        finally:
            m.save_config({})
        self.assertIn("lang=en", report)
        self.assertIn("browser=firefox", report)
        self.assertNotIn("prive", report)
        self.assertNotIn("secret", report)


class IssueUrlTests(unittest.TestCase):
    def test_prefilled_url(self):
        url, truncated = m._issue_url("Plantage au démarrage", "Description ici", "ligne1\nligne2")
        self.assertFalse(truncated)
        parsed = urlparse(url)
        self.assertEqual(f"{parsed.scheme}://{parsed.netloc}{parsed.path}", m.REPO_URL + "/issues/new")
        qs = parse_qs(parsed.query)
        self.assertEqual(qs["title"], ["Plantage au démarrage"])
        self.assertIn("Description ici", qs["body"][0])
        self.assertIn("ligne1\nligne2", qs["body"][0])

    def test_long_report_is_truncated_under_limit(self):
        url, truncated = m._issue_url("t", "d", "x" * 50000, limit=6500)
        self.assertTrue(truncated)
        self.assertLessEqual(len(url), 6500)
        self.assertIn("%5Btruncated%5D", url)


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

    def _window(self, report="rapport"):
        win = m.BugReportWindow(self.app, report)
        win.withdraw()
        self.addCleanup(win.destroy)
        return win

    def test_open_requires_summary(self):
        win = self._window()
        with mock.patch.object(m.messagebox, "showwarning") as warn, \
                mock.patch.object(m.webbrowser, "open") as opened:
            win._open()
        warn.assert_called_once()
        opened.assert_not_called()

    def test_open_launches_prefilled_issue(self):
        win = self._window("REPORT-TEXT")
        win.var_summary.set("Mon problème")
        win.txt_desc.insert("1.0", "Il plante")
        with mock.patch.object(m.webbrowser, "open") as opened:
            win._open()
        url = opened.call_args[0][0]
        self.assertTrue(url.startswith(m.REPO_URL + "/issues/new?"))
        body = parse_qs(urlparse(url).query)["body"][0]
        self.assertIn("Il plante", body)
        self.assertIn("REPORT-TEXT", body)

    def test_copy_puts_full_text_in_clipboard(self):
        win = self._window("REPORT-TEXT")
        win.txt_desc.insert("1.0", "desc")
        win._copy()
        clip = self.app.clipboard_get()
        self.assertIn("desc", clip)
        self.assertIn("REPORT-TEXT", clip)

    def test_toolbar_report_collects_log_and_hides_paths(self):
        app = self.app
        app.var_outdir.set("E:/Mes videos privees")
        app.log_text.configure(state="normal")
        app.log_text.insert("end", "Destination: E:/Mes videos privees/a.mp4\n")
        app.log_text.configure(state="disabled")
        captured = {}
        with mock.patch.object(m, "BugReportWindow", side_effect=lambda parent, rep: captured.update(r=rep)), \
                mock.patch.object(m, "_ytdlp_version", return_value="x"):
            app._open_bug_report()
        self.assertIn("Destination:", captured["r"])
        self.assertNotIn("privees", captured["r"])


if __name__ == "__main__":
    unittest.main()
