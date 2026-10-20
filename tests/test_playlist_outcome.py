import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

# journal réel (abrégé) : 6 éléments, les n°2 et n°6 supprimés par YouTube, les autres téléchargés
REAL = [
    "[download] Downloading playlist: MUSIC",
    "[youtube:tab] Playlist MUSIC: Downloading 6 items of 6",
    "[download] Downloading item 1 of 6",
    "[download] 100% of   49.73MiB in 00:00:15 at 3.20MiB/s",
    "[download] Downloading item 2 of 6",
    "ERROR: [youtube] Ani_6IRV20A: This video has been removed for violating YouTube's policy on nudity or sexual content",
    "[download] Downloading item 3 of 6",
    "[download] Downloading item 4 of 6",
    "[download] Downloading item 5 of 6",
    "[download] Downloading item 6 of 6",
    "ERROR: [youtube] 2dbR2JZmlWo: This video has been removed for violating YouTube's policy on nudity or sexual content",
    "[download] Finished downloading playlist: MUSIC",
]


class PlaylistOutcomeTests(unittest.TestCase):
    def test_real_log_two_unavailable_of_six(self):
        self.assertEqual(m.playlist_outcome(REAL), (4, 2))

    def test_stopped_before_the_end_is_not_a_partial_success(self):
        self.assertIsNone(m.playlist_outcome(REAL[:-1]))                  # pas de « Finished downloading playlist »

    def test_every_video_failed_stays_a_failure(self):
        lines = ["[download] Downloading item 1 of 2", "ERROR: [youtube] a: boom",
                 "[download] Downloading item 2 of 2", "ERROR: [youtube] b: boom",
                 "[download] Finished downloading playlist: X"]
        self.assertIsNone(m.playlist_outcome(lines))

    def test_no_error_or_single_video_gives_nothing(self):
        self.assertIsNone(m.playlist_outcome([l for l in REAL if not l.startswith("ERROR")]))
        self.assertIsNone(m.playlist_outcome(["ERROR: [youtube] a: boom"]))
        self.assertIsNone(m.playlist_outcome([]))

    def test_the_same_error_repeated_is_counted_once(self):
        lines = REAL[:6] + [REAL[5]] + REAL[6:]
        self.assertEqual(m.playlist_outcome(lines), (4, 2))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class MainWindowPartialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app._queue_running = False
        self.app._current_dl_files = ["C:/Dl/RICE BALLS.mp4"]

    def test_partial_playlist_is_reported_as_finished(self):
        self.app._on_done(False, (4, 2))
        self.assertEqual(self.app.var_status.get(), m.t("app.status_done_partial", ok=4, failed=2))
        self.assertNotIn("Échec", self.app.var_status.get())
        self.assertEqual(self.app._current_dl_files, [], "les vidéos téléchargées sont définitives")

    def test_plain_failure_is_unchanged(self):
        self.app._on_done(False)
        self.assertEqual(self.app.var_status.get(), m.t("app.status_done_fail"))

    def test_partial_playlist_keeps_a_queue_entry_in_error(self):
        self.app._queue = [{"url": "https://www.youtube.com/playlist?list=X", "status": "pending"}]
        self.app._queue_running, self.app._queue_index, self.app._queue_skip = True, 0, False
        with mock.patch.object(m, "save_queue"), mock.patch.object(self.app, "_queue_run_next"), \
                mock.patch.object(self.app, "_refresh_queue_tv"):
            self.app._on_done(False, (4, 2))
        self.assertEqual(len(self.app._queue), 1, "l'entrée n'est pas supprimée : l'utilisateur décide")
        self.assertEqual(self.app._queue[0]["status"], "error")


class AgeHintTests(unittest.TestCase):
    def test_hint_no_longer_says_only_retry(self):
        m.load_lang("fr")
        text = m._cookie_hint("This video is age-restricted and YouTube is requiring account age-verification", "firefox")
        self.assertIn("qualité réduite", text)
        self.assertIn("Firefox", text)
        self.assertIn("s'il échoue", text)


if __name__ == "__main__":
    unittest.main()
