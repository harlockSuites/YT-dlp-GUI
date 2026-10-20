import os
import shutil
import tempfile
import unittest

from tests._loader import load_gui, tk_available

m = load_gui()


class SubtitleTrackingTests(unittest.TestCase):
    """Le .srt que yt-dlp vient d'annoncer doit être suivi avant même sa ligne « Destination »."""

    LINE = r"[info] Writing video subtitles to: C:\Dl\THE AMAZING DIGITAL CIRCUS PILOT.ja.srt"

    def test_both_download_windows_recognise_the_announcement(self):
        for cls in (m.DownloadQueueWindow, m.YtDlpGui):
            found = cls._RE_SUBS.search(self.LINE)
            self.assertIsNotNone(found, cls.__name__)
            self.assertEqual(found.group(1), r"C:\Dl\THE AMAZING DIGITAL CIRCUS PILOT.ja.srt")
            auto = cls._RE_SUBS.search("[info] Writing video automatic captions to: C:\\Dl\\x.fr.vtt")
            self.assertIsNotNone(auto)
            self.assertIsNone(cls._RE_SUBS.search("[info] Writing video thumbnail 0 to: C:\\Dl\\x.jpg"))

    @unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
    def test_main_window_tracks_the_announced_file(self):
        m.load_lang("fr")
        app = m.YtDlpGui()
        app.withdraw()
        try:
            app._current_dl_files = []
            app._on_output_line(self.LINE)
            app._on_output_line(self.LINE)
            self.assertEqual(app._current_dl_files, [r"C:\Dl\THE AMAZING DIGITAL CIRCUS PILOT.ja.srt"])
        finally:
            app.destroy()


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class PreferencesTests(unittest.TestCase):
    def setUp(self):
        m.save_config({})
        m.load_lang("fr")
        self.d1, self.d2 = tempfile.mkdtemp(prefix="dl1-"), tempfile.mkdtemp(prefix="dl2-")
        for d in (self.d1, self.d2):
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.addCleanup(m.save_config, {})

    def _app(self):
        app = m.YtDlpGui()
        app.withdraw()
        def _close():
            try:
                app.destroy()
            except Exception:   # déjà détruite par le test
                pass
        self.addCleanup(_close)
        return app

    def test_main_window_choices_are_saved_immediately(self):
        app = self._app()
        app.var_outdir.set(self.d1)
        app.var_browser.set("firefox")
        cfg = m.load_config()        # sans attendre la fermeture de la fenêtre
        self.assertEqual(cfg["outdir"], self.d1)
        self.assertEqual(cfg["browser"], "firefox")

    def test_choices_survive_a_restart(self):
        app = self._app()
        app.var_outdir.set(self.d1)
        app.var_browser.set("opera")
        app.destroy()
        again = m.YtDlpGui()
        self.addCleanup(again.destroy)
        again.withdraw()
        self.assertEqual(again.var_outdir.get(), self.d1)
        self.assertEqual(again.var_browser.get(), "opera")

    def test_inspector_remembers_its_own_folder_and_browser(self):
        app = self._app()
        app.var_outdir.set(self.d1)
        insp = m.PlaylistInspectorWindow(app, outdir=app.var_outdir.get())
        insp.withdraw()
        self.assertEqual(insp.var_g_outdir.get(), self.d1)        # première ouverture : dossier de la fenêtre principale
        insp.var_g_outdir.set(self.d2)
        insp.var_g_browser.set("firefox")
        cfg = m.load_config()
        self.assertEqual(cfg["insp_outdir"], self.d2)
        self.assertEqual(cfg["browser"], "firefox")
        insp.destroy()
        insp2 = m.PlaylistInspectorWindow(app, outdir=app.var_outdir.get())
        insp2.withdraw()
        self.addCleanup(insp2.destroy)
        self.assertEqual(insp2.var_g_outdir.get(), self.d2, "dernier dossier de l'inspecteur retrouvé")

    def test_a_missing_remembered_folder_falls_back_to_the_main_one(self):
        m.save_config({"insp_outdir": os.path.join(self.d1, "supprimé")})
        app = self._app()
        insp = m.PlaylistInspectorWindow(app, outdir=self.d1)
        insp.withdraw()
        self.addCleanup(insp.destroy)
        self.assertEqual(insp.var_g_outdir.get(), self.d1)


if __name__ == "__main__":
    unittest.main()
