import json
import threading
import time
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

# `yt-dlp -J --flat-playlist` sur la playlist « MUSIC » (6 éléments, les n°2 et n°6 supprimés par YouTube)
MUSIC = {
    "_type": "playlist", "title": "MUSIC", "playlist_count": 6, "uploader": "TVFilthyFrank",
    "entries": [
        {"id": "LeMVDuIO3J0", "title": "RICE BALLS"},
        {"id": "Ani_6IRV20A", "title": None},
        {"id": "b9Wlei7ZV1Y", "title": "PINK LIFE"},
        {"id": "9HFDW0x10-Q", "title": "TERIYAKI GOD"},
        {"id": "OLpeX4RRo28", "title": "PINK GUY - STFU"},
        {"id": "2dbR2JZmlWo", "title": None},
    ],
}


class PlaylistSummaryTests(unittest.TestCase):
    def test_playlist_urls_are_recognised(self):
        self.assertTrue(m.is_playlist_url("https://youtube.com/playlist?list=PLabc&si=xyz"))
        self.assertTrue(m.is_playlist_url("https://www.youtube.com/playlist?list=PLabc"))
        self.assertFalse(m.is_playlist_url("https://www.youtube.com/watch?v=abc&list=PLabc&index=4"))
        self.assertFalse(m.is_playlist_url("https://www.youtube.com/watch?v=abc"))
        self.assertFalse(m.is_playlist_url("https://youtu.be/abc"))
        self.assertFalse(m.is_playlist_url(""))

    def test_summary_counts_unavailable_videos(self):
        self.assertEqual(m.playlist_summary(MUSIC), {"title": "MUSIC", "count": 6, "bad": 2})

    def test_private_and_deleted_titles_count_as_unavailable(self):
        info = {"title": "X", "entries": [{"title": "[Private video]"}, {"title": "[Deleted video]"},
                                           {"title": "[MV] Un vrai titre"}]}
        self.assertEqual(m.playlist_summary(info), {"title": "X", "count": 3, "bad": 2})

    def test_not_a_playlist_gives_none(self):
        self.assertIsNone(m.playlist_summary({"title": "Une vidéo"}))
        self.assertIsNone(m.playlist_summary([]))
        self.assertIsNone(m.playlist_summary(None))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class InspectPlaylistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _run(self, stdout="", stderr="", returncode=0):
        shown, logged = [], []
        done = types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)
        with mock.patch.object(m.subprocess, "run", return_value=done) as run, \
                mock.patch.object(self.app, "after", side_effect=lambda ms, fn=None, *a: fn(*a)), \
                mock.patch.object(self.app, "_show_inspect_box", side_effect=lambda *a: shown.append(a)), \
                mock.patch.object(self.app, "_log", side_effect=lambda *a: logged.append(a)):
            self.app._inspect_playlist("https://youtube.com/playlist?list=PLabc", [], "firefox")
        return run, shown, logged

    def test_summary_is_shown_with_unavailable_videos(self):
        run, shown, logged = self._run(stdout=json.dumps(MUSIC))
        command = run.call_args.args[0]
        self.assertIn("--flat-playlist", command)               # une seule requête rapide, pas une analyse par vidéo
        text, color, _url = shown[0]
        self.assertIn("MUSIC", text)
        self.assertIn("6 vidéo(s)", text)
        self.assertIn("2 indisponible(s)", text)
        self.assertEqual(color, "#f5a623")
        self.assertEqual(logged[0][0], text)

    def test_playlist_without_unavailable_video_is_green(self):
        info = dict(MUSIC, entries=[e for e in MUSIC["entries"] if e["title"]])
        _run, shown, _logged = self._run(stdout=json.dumps(info))
        self.assertEqual(shown[0][1], "#27ae60")
        self.assertNotIn("indisponible", shown[0][0])

    def test_failure_reports_yt_dlp_errors(self):
        _run, shown, logged = self._run(stderr="ERROR: [youtube:tab] Playlist does not exist", returncode=1)
        self.assertEqual(shown[0][0], m.t("inspect.box_failed"))
        self.assertTrue(any("Playlist does not exist" in str(x[0]) for x in logged))

    def test_unreadable_output_is_reported(self):
        _run, shown, logged = self._run(stdout="pas du json")
        self.assertEqual(shown[0][0], m.t("inspect.box_failed"))
        self.assertTrue(any(x[0] == m.t("inspect.log_bad_json") for x in logged))

    def test_inspect_routes_a_playlist_url_to_the_summary(self):
        self.app.var_url.set("https://youtube.com/playlist?list=PLabc&si=xyz")
        with mock.patch.object(self.app, "_inspect_playlist") as playlist, \
                mock.patch.object(m.subprocess, "run") as run, \
                mock.patch.object(m.threading, "Thread", side_effect=lambda target, **k: types.SimpleNamespace(
                    start=target)):
            self.app._inspect()
        playlist.assert_called_once()
        run.assert_not_called()                                 # plus d'« -j » sur une playlist : c'était l'erreur JSON invalide


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class InspectorCloseTests(unittest.TestCase):
    """Fermer l'inspecteur pendant une analyse ne doit plus ouvrir de « Erreur interne »."""

    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.errors = []
        self.app.report_callback_exception = lambda *exc: self.errors.append(exc)
        self.insp = m.PlaylistInspectorWindow(self.app, outdir="")
        self.insp.withdraw()
        self.addCleanup(lambda: self.insp.winfo_exists() and self.insp.destroy())

    def _pump(self, seconds=0.2):
        end = time.time() + seconds
        while time.time() < end:
            self.app.update()
            time.sleep(0.01)

    def test_actions_scheduled_before_the_close_are_dropped(self):
        ran = []
        for n in range(3):                                       # les trois actions de fin d'analyse
            self.insp.after(80, lambda n=n: (ran.append(n), self.insp.btn_analyze.configure(state="normal")))
        self.insp.destroy()
        self._pump(0.3)
        self.assertEqual(ran, [])
        self.assertEqual(self.errors, [])

    def test_actions_scheduled_after_the_close_are_dropped(self):
        self.insp.destroy()
        self.insp.after(0, lambda: self.insp.btn_analyze.configure(state="normal"))
        self._pump(0.1)
        self.assertEqual(self.errors, [])

    def test_the_analysis_thread_can_schedule_after_the_close(self):
        self.insp.destroy()
        problems = []

        def worker():
            try:
                self.insp.after(0, lambda: None)
            except BaseException as exc:                        # noqa: BLE001
                problems.append(exc)
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(5)
        self.assertEqual(problems, [])

    def test_open_window_still_runs_its_actions(self):
        ran = []
        self.insp.after(0, lambda: ran.append("ok"))
        self._pump(0.1)
        self.assertEqual(ran, ["ok"])
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
