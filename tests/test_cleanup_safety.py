import os
import shutil
import tempfile
import time
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

    def test_skipping_after_the_merge_deletes_the_merged_video_too(self):
        merged = os.path.join(self.d, "Ma vidéo.mkv")
        with open(merged, "w") as f:
            f.write("x")
        win = self._window(running=True, files=[merged, self.video])      # fichier final + sous-titre déjà écrit
        self._run_cleanup(win)
        self.assertFalse(os.path.exists(merged), "règle « tout supprimer » : le MKV fusionné aussi")
        self.assertFalse(os.path.exists(self.video))

    def test_final_file_announcements_are_recognised(self):
        cases = {
            r'[Merger] Merging formats into "C:\Dl\Ep 2.mkv"': r"C:\Dl\Ep 2.mkv",
            r"[ExtractAudio] Destination: C:\Dl\chanson.mp3": r"C:\Dl\chanson.mp3",
            r'[VideoRemuxer] Remuxing video from webm to mp4; Destination: "C:\Dl\v.mp4"': r"C:\Dl\v.mp4",
        }
        for cls in (m.DownloadQueueWindow, m.YtDlpGui):
            for line, expected in cases.items():
                found = cls._RE_FINAL.search(line)
                self.assertIsNotNone(found, (cls.__name__, line))
                self.assertEqual(next(g for g in found.groups() if g).strip(), expected)
            self.assertIsNone(cls._RE_FINAL.search(r'[Metadata] Adding metadata to "C:\Dl\x.mkv"'))

    # ── les replis de nettoyage ne touchent jamais les fichiers des autres vidéos ─────────────────
    def _old(self, name, content="x"):
        path = os.path.join(self.d, name)
        with open(path, "w") as f:
            f.write(content)
        past = time.time() - 3600
        os.utime(path, (past, past))
        return path

    def test_fallbacks_spare_files_of_other_videos(self):
        others = [self._old("Autre.fr.srt"), self._old("Autre.f251.webm.part"), self._old("Show S02.E02.mkv"),
                  self._old("Reprise.mp4.ytdl")]
        win = self._window(running=True, files=[os.path.join(self.d, "Cette vidéo.fr.srt"),      # annoncé, pas encore écrit
                                                os.path.join(self.d, "Show S01.E02.mkv")])        # fusion interrompue
        win._dl_started = time.time() - 5
        self._run_cleanup(win)
        for path in others:
            self.assertTrue(os.path.exists(path), os.path.basename(path))

    def test_fallback_still_removes_what_the_interrupted_video_wrote(self):
        mismatch = os.path.join(self.d, "Cette vidéo.f251.webm.part")       # titre assaini autrement par yt-dlp
        with open(mismatch, "w") as f:
            f.write("x")
        win = self._window(running=True, files=[os.path.join(self.d, "Cette video.f251.webm")])
        win._dl_started = time.time() - 5
        self._run_cleanup(win)
        self.assertFalse(os.path.exists(mismatch))

    def test_without_a_start_time_the_fallbacks_delete_nothing(self):
        other = self._old("Autre.fr.srt")
        win = self._window(running=True, files=[os.path.join(self.d, "Cette vidéo.fr.srt")])
        win._dl_started = None
        self._run_cleanup(win)
        self.assertTrue(os.path.exists(other))

    def test_modified_since(self):
        old = self._old("vieux.txt")
        self.assertFalse(m.modified_since(old, time.time()))
        self.assertTrue(m.modified_since(self.video, time.time() - 5))
        self.assertFalse(m.modified_since(self.video, None))
        self.assertFalse(m.modified_since(os.path.join(self.d, "absent"), time.time()))

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

    def test_main_window_cleanup_spares_other_files(self):
        other = os.path.join(self.d, "Autre.fr.srt")
        with open(other, "w") as f:
            f.write("x")
        past = time.time() - 3600
        os.utime(other, (past, past))
        self.app._current_dl_files = [os.path.join(self.d, "Cette vidéo.fr.srt")]
        self.app._dl_started = time.time() - 5
        with mock.patch("time.sleep"), mock.patch.object(m.threading, "Thread") as thread:
            self.app._cleanup_partial_files()
            thread.call_args.kwargs["target"](*thread.call_args.kwargs["args"])
        self.assertTrue(os.path.exists(other))


if __name__ == "__main__":
    unittest.main()
