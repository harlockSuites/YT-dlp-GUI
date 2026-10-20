import os
import time
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _all_labels(widget):
    texts = []
    for child in widget.winfo_children():
        try:
            texts.append(str(child.cget("text")))
        except Exception:
            pass
        texts.extend(_all_labels(child))
    return texts


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class ReportAndDepsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _report(self, statuses):
        rows = [{"title": f"Vidéo {i}", "status": s, "dropped": [], "rc": 0} for i, s in enumerate(statuses)]
        win = m.DownloadReportWindow(self.app, rows)
        win.withdraw()
        self.addCleanup(win.destroy)
        return win

    def test_report_accepts_skipped_videos(self):
        """Une vidéo sautée plantait le bilan de fin de file (KeyError 'sauté')."""
        win = self._report(["ok", "sauté", "erreur", "ajusté", "sauté"])
        texts = _all_labels(win)
        self.assertEqual(sum(1 for x in texts if x == m.t("report.status_skipped")), 2)
        self.assertTrue(any(m.t("report.summary_skipped", n=2) in x for x in texts), texts)

    def test_report_without_skips_keeps_the_original_summary(self):
        win = self._report(["ok", "ok"])
        self.assertFalse(any("sauté" in x.lower() for x in _all_labels(win)))

    def test_every_report_status_has_a_colour_and_a_label(self):
        win = self._report(["ok"])
        for status in ("ok", "ajusté", "erreur", "sauté"):
            self.assertIn(status, win._STATUS_COLOR)
            self.assertIn(status, win._STATUS_LABEL)

    def test_deps_window_explains_the_disabled_install_all_button(self):
        with mock.patch.object(m, "choco_available", return_value=False), \
                mock.patch.object(m, "dep_installed", return_value=False), \
                mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.DepsWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        self.assertIn(m.t("deps.install_all_disabled"), _all_labels(win))

    def test_deps_window_with_chocolatey_has_no_such_message(self):
        with mock.patch.object(m, "choco_available", return_value=True), \
                mock.patch.object(m, "dep_installed", return_value=False), \
                mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.DepsWindow(self.app)
        win.withdraw()
        self.addCleanup(win.destroy)
        self.assertNotIn(m.t("deps.install_all_disabled"), _all_labels(win))


class SourceRuleTests(unittest.TestCase):
    def setUp(self):
        with open(m.__file__, encoding="utf-8") as f:
            self.source = f.read()

    def test_pause_button_is_reset_whenever_a_new_video_starts(self):
        # _kill_and_cleanup baisse déjà _paused : le libellé doit être remis quoi qu'il arrive
        self.assertIn('''            self._paused = False
            self.after(0, lambda: self.btn_pause.configure(text=t("dlq.btn_pause")))''', self.source)

    def test_old_command_files_are_removed_at_startup(self):
        d = m.COMMAND_DIR
        os.makedirs(d, exist_ok=True)
        old = os.path.join(d, "cmd-test-old.conf")
        fresh = os.path.join(d, "cmd-test-fresh.conf")
        for p in (old, fresh):
            with open(p, "w") as f:
                f.write("# coding: utf-8\n")
        self.addCleanup(m.remove_command_file, old)
        self.addCleanup(m.remove_command_file, fresh)
        past = time.time() - 3600           # une heure : l'arrêt brutal d'une session précédente
        os.utime(old, (past, past))
        m.cleanup_command_files()
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(fresh), "le fichier d'un téléchargement qui démarre doit rester")


if __name__ == "__main__":
    unittest.main()
