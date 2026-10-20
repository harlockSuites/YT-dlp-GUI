import os
import time
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()
RUNNING = types.SimpleNamespace(pid=4242, poll=lambda: None)
FINISHED = types.SimpleNamespace(pid=4242, poll=lambda: 0)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class StopScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app._process = RUNNING
        self.app._queue_running = False
        self.app._current_dl_files = []
        self.app._finished_items_files = []
        self.addCleanup(setattr, self.app, "_process", None)
        self.app._paused = False
        for name in ("_suspend_process", "_resume_process"):       # jamais de vrai processus : PID fictif
            patcher = mock.patch.object(self.app, name)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _feed(self, *lines):
        for line in lines:
            self.app._on_output_line(line)

    def _two_items(self):
        self._feed("[download] Downloading item 1 of 4",
                   r"[download] Destination: C:\Dl\Un.f133.mp4",
                   r'[Merger] Merging formats into "C:\Dl\Un.mp4"',
                   "[download] Downloading item 2 of 4",
                   r"[download] Destination: C:\Dl\Deux.f133.mp4")

    def _stop_with(self, answer):
        seen = {}
        with mock.patch.object(m.messagebox, "askyesnocancel", return_value=answer) as ask, \
                mock.patch.object(self.app, "_kill_current_process", return_value=True) as kill, \
                mock.patch.object(self.app, "_cleanup_partial_files",
                                  side_effect=lambda: seen.update(files=list(self.app._current_dl_files))):
            self.app._stop()
        return seen.get("files"), ask, kill

    def test_each_playlist_item_closes_the_previous_one(self):
        self._two_items()
        self.assertEqual(self.app._finished_items_files, [r"C:\Dl\Un.f133.mp4", r"C:\Dl\Un.mp4"])
        self.assertEqual(self.app._current_dl_files, [r"C:\Dl\Deux.f133.mp4"])

    def test_no_question_for_a_single_video(self):
        self._feed(r"[download] Destination: C:\Dl\Seule.f133.mp4")
        files, ask, kill = self._stop_with(True)
        ask.assert_not_called()
        self.assertEqual(files, [r"C:\Dl\Seule.f133.mp4"])

    def test_no_the_current_video_only_is_deleted(self):
        self._two_items()
        files, ask, _kill = self._stop_with(False)
        ask.assert_called_once()
        self.assertEqual(files, [r"C:\Dl\Deux.f133.mp4"])

    def test_yes_everything_is_deleted_including_finished_videos(self):
        self._two_items()
        files, _ask, _kill = self._stop_with(True)
        self.assertEqual(files, [r"C:\Dl\Un.f133.mp4", r"C:\Dl\Un.mp4", r"C:\Dl\Deux.f133.mp4"])

    def test_cancel_keeps_downloading_and_deletes_nothing(self):
        self._two_items()
        files, _ask, kill = self._stop_with(None)
        kill.assert_not_called()
        self.assertIsNone(files)
        self.assertEqual(self.app._finished_items_files, [r"C:\Dl\Un.f133.mp4", r"C:\Dl\Un.mp4"])

    def test_nothing_is_asked_when_no_download_is_running(self):
        self._two_items()
        self.app._process = FINISHED
        with mock.patch.object(m.messagebox, "askyesnocancel") as ask:
            self.assertTrue(self.app._confirm_stop_scope())
        ask.assert_not_called()

    def test_queue_stop_and_skip_use_the_same_question(self):
        for method in ("_queue_stop", "_queue_skip_current"):
            with self.subTest(method=method):
                self._two_items()
                self.app._queue_running = True
                with mock.patch.object(m.messagebox, "askyesnocancel", return_value=None), \
                        mock.patch.object(self.app, "_kill_current_process") as kill:
                    getattr(self.app, method)()
                kill.assert_not_called()
                self.assertTrue(self.app._queue_running, "annuler ne doit pas arrêter la file")
                self.app._finished_items_files, self.app._current_dl_files = [], []

    def test_finished_items_are_forgotten_when_the_download_ends(self):
        self._two_items()
        self.app._queue_running = False
        self.app._on_done(False)
        self.assertEqual(self.app._finished_items_files, [])


class CommandFileOwnerTests(unittest.TestCase):
    def setUp(self):
        os.makedirs(m.COMMAND_DIR, exist_ok=True)
        self.paths = []

    def tearDown(self):
        for p in self.paths:
            m.remove_command_file(p)

    def _file(self, name, age=0):
        path = os.path.join(m.COMMAND_DIR, name)
        with open(path, "w") as f:
            f.write("# coding: utf-8\n")
        if age:
            past = time.time() - age
            os.utime(path, (past, past))
        self.paths.append(path)
        return path

    def test_new_files_carry_the_pid_of_their_owner(self):
        _run, path = m.command_file_args(["yt-dlp", "-f", "best", "-o", "x", "--", "https://example.com"])
        self.paths.append(path)
        self.assertEqual(m.command_file_owner(os.path.basename(path)), os.getpid())
        self.assertIsNone(m.command_file_owner("cmd-abc.conf"))

    def test_a_fresh_file_of_a_dead_process_is_removed_at_startup(self):
        orphan = self._file("cmd-2147483000-aaaa.conf")             # ce PID n'existe pas : arrêt brutal
        m.cleanup_command_files()
        self.assertFalse(os.path.exists(orphan))

    def test_a_file_of_a_running_process_is_kept(self):
        mine = self._file(f"cmd-{os.getpid()}-bbbb.conf", age=3600)   # une autre fenêtre du logiciel pourrait en être l'auteur
        m.cleanup_command_files()
        self.assertTrue(os.path.exists(mine))

    def test_old_format_falls_back_on_age(self):
        old = self._file("cmd-oldname.conf", age=3600)
        fresh = self._file("cmd-freshname.conf")
        m.cleanup_command_files()
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(fresh))

    def test_every_file_older_than_a_day_goes_even_for_a_live_pid(self):
        stale = self._file(f"cmd-{os.getpid()}-cccc.conf", age=3 * 24 * 3600)
        m.cleanup_command_files()
        self.assertFalse(os.path.exists(stale))

    def test_unreadable_process_list_falls_back_on_age(self):
        orphan = self._file("cmd-2147483000-dddd.conf", age=3600)
        young = self._file("cmd-2147483000-eeee.conf")
        with mock.patch.object(m, "_iter_processes", side_effect=OSError):
            m.cleanup_command_files()
        self.assertFalse(os.path.exists(orphan))
        self.assertTrue(os.path.exists(young))


if __name__ == "__main__":
    unittest.main()
