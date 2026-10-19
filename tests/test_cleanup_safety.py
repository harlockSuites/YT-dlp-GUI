import os
import shutil
import tempfile
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _fake_process(running):
    return types.SimpleNamespace(pid=4242, poll=lambda: None if running else 0)


class QueueWindowCleanupTests(unittest.TestCase):
    """Fermer la fenêtre de téléchargement ne doit jamais effacer un téléchargement terminé."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="clean-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.video = os.path.join(self.d, "Ma vidéo.fr.srt")
        self.part = os.path.join(self.d, "Ma vidéo.f251.webm.part")
        for p in (self.video, self.part):
            with open(p, "w") as f:
                f.write("x")

    def _window(self, running, files):
        win = m.DownloadQueueWindow.__new__(m.DownloadQueueWindow)
        win._paused = False
        win._process = _fake_process(running)
        win._current_dl_files = list(files)
        win._inspector = None
        win.after = lambda _ms, fn=None, *a: fn(*a) if fn else None
        win._log = lambda *a, **k: None
        return win

    def _run_cleanup(self, win):
        with mock.patch.object(m.subprocess, "run"), mock.patch("time.sleep"):
            win._kill_and_cleanup()
            thread = getattr(win, "_cleanup_thread", None)
            if thread:
                thread.join(timeout=10)

    def test_finished_download_keeps_its_files_when_the_window_is_closed(self):
        win = self._window(running=False, files=[self.video])
        self._run_cleanup(win)
        self.assertTrue(os.path.exists(self.video), "les sous-titres terminés ne doivent pas être supprimés")

    def test_interrupted_download_still_loses_its_partial_files(self):
        win = self._window(running=True, files=[self.part])
        self._run_cleanup(win)
        self.assertFalse(os.path.exists(self.part))

    def test_without_any_process_nothing_is_deleted(self):
        win = self._window(running=False, files=[self.video])
        win._process = None
        self._run_cleanup(win)
        self.assertTrue(os.path.exists(self.video))

    def test_source_clears_the_list_when_a_video_succeeds(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn('self._current_dl_files = []   # fichiers définitifs', source)
        self.assertIn('self._current_dl_files = []   # téléchargement terminé', source)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class MainWindowCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="clean-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.srt = os.path.join(self.d, "video.fr.srt")
        with open(self.srt, "w") as f:
            f.write("x")
        self.app._process = None
        self.app._queue_running = False

    def test_stop_without_a_running_download_deletes_nothing(self):
        self.app._current_dl_files = [self.srt]
        self.app._stop()
        self.assertTrue(os.path.exists(self.srt))

    def test_success_empties_the_list(self):
        self.app._current_dl_files = [self.srt]
        self.app._on_done(True)
        self.assertEqual(self.app._current_dl_files, [])
        self.assertTrue(os.path.exists(self.srt))


if __name__ == "__main__":
    unittest.main()
