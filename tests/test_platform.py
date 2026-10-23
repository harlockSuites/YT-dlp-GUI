"""Couche de plateforme (Windows / Linux) : processus, pause, ouverture de fichier, liste des processus."""
import os
import subprocess
import sys
import time
import unittest
from unittest import mock

from tests._loader import load_gui

m = load_gui()

# Un processus Python qui lance un petit-enfant, puis attend : un arbre de trois processus.
_TREE = ("import subprocess, sys, time\n"
         "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
         "time.sleep(60)\n")


def _alive(pid):
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                             **m.NO_WINDOW).stdout
        return str(pid) in out
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            return f.read().decode("utf-8", "replace").rsplit(")", 1)[1].split()[0] != "Z"   # zombie = mort
    except OSError:
        return False


def _wait_until(condition, seconds=10.0):
    end = time.time() + seconds
    while time.time() < end:
        if condition():
            return True
        time.sleep(0.1)
    return False


class SubprocessArgumentsTests(unittest.TestCase):
    def test_arguments_match_the_system(self):
        if m.IS_WINDOWS:
            self.assertEqual(m.NO_WINDOW, {"creationflags": subprocess.CREATE_NO_WINDOW})
            self.assertEqual(m.PROCESS_GROUP, m.NO_WINDOW)
        else:
            self.assertEqual(m.NO_WINDOW, {})
            self.assertEqual(m.PROCESS_GROUP, {"start_new_session": True})

    def test_arguments_are_accepted_by_subprocess(self):
        r = subprocess.run([sys.executable, "-c", "pass"], timeout=30, **m.NO_WINDOW)
        self.assertEqual(r.returncode, 0)


class ProcessListingTests(unittest.TestCase):
    def test_this_process_is_listed_with_its_parent(self):
        found = {pid: (parent, name) for pid, parent, name in m._iter_processes()}
        self.assertIn(os.getpid(), found)
        self.assertEqual(found[os.getpid()][0], os.getppid())
        self.assertTrue(found[os.getpid()][1].startswith("python"), found[os.getpid()])

    @unittest.skipIf(os.name == "nt", "lecture de /proc")
    def test_names_with_spaces_and_parentheses_are_read_whole(self):
        stat = "4242 (Web Content (x)) S 77 4242 4242 0 -1 4194560 1 0 0 0 0 0 0 0 20 0 1 0 1 1 1 1"
        with mock.patch.object(m.os, "listdir", return_value=["4242", "self", "cpuinfo"]), \
                mock.patch("builtins.open", mock.mock_open(read_data=stat.encode())):
            self.assertEqual(list(m._iter_processes_posix()), [(4242, 77, "web content (x)")])

    @unittest.skipIf(os.name == "nt", "lecture de /proc")
    def test_a_process_that_ends_during_the_listing_is_ignored(self):
        with mock.patch.object(m.os, "listdir", return_value=["4242"]), \
                mock.patch("builtins.open", side_effect=FileNotFoundError):
            self.assertEqual(list(m._iter_processes_posix()), [])

    def test_browser_programs_are_defined_for_each_menu_entry(self):
        for browser in ("chrome", "edge", "brave", "opera", "firefox"):
            self.assertTrue(m._BROWSER_EXES[browser], browser)
        if not m.IS_WINDOWS:
            self.assertTrue(all("." not in n for names in m._BROWSER_EXES.values() for n in names))


class ProcessTreeTests(unittest.TestCase):
    def _start(self):
        p = subprocess.Popen([sys.executable, "-c", _TREE], **m.PROCESS_GROUP)
        self.addCleanup(lambda: (m.kill_process_tree(p), p.wait()))
        self.assertTrue(_wait_until(lambda: m._child_pids(p.pid)), "le petit-enfant n'a pas démarré")
        return p, m._child_pids(p.pid)

    def test_kill_process_tree_stops_the_children_too(self):
        p, children = self._start()
        m.kill_process_tree(p)
        p.wait(timeout=10)
        for pid in children:
            self.assertTrue(_wait_until(lambda pid=pid: not _alive(pid)), f"l'enfant {pid} vit encore")

    @unittest.skipIf(os.name == "nt", "groupes de processus POSIX")
    def test_kill_never_touches_the_group_of_the_program(self):
        """Un processus lancé sans PROCESS_GROUP partage notre groupe : seul lui est arrêté."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(p.wait)
        self.assertEqual(os.getpgid(p.pid), os.getpgrp())
        m.kill_process_tree(p)
        p.wait(timeout=10)
        self.assertTrue(_alive(os.getpid()))

    @unittest.skipIf(os.name == "nt", "signaux POSIX")
    def test_suspend_then_resume_stops_and_restarts_the_whole_tree(self):
        def state(pid):
            with open(f"/proc/{pid}/stat", "rb") as f:
                return f.read().decode().rsplit(")", 1)[1].split()[0]

        p, children = self._start()
        m.suspend_process_tree(p.pid)
        self.assertTrue(_wait_until(lambda: state(p.pid) == "T"), "parent non suspendu")
        for pid in children:
            self.assertTrue(_wait_until(lambda pid=pid: state(pid) == "T"), f"enfant {pid} non suspendu")
        m.resume_process_tree(p.pid)
        self.assertTrue(_wait_until(lambda: state(p.pid) != "T"), "parent non repris")
        for pid in children:
            self.assertTrue(_wait_until(lambda pid=pid: state(pid) != "T"), f"enfant {pid} non repris")

    def test_suspend_and_resume_never_raise_for_a_missing_process(self):
        m.suspend_process_tree(99999999)
        m.resume_process_tree(99999999)


class OpenPathTests(unittest.TestCase):
    def test_uses_the_system_opener(self):
        if m.IS_WINDOWS:
            with mock.patch.object(m.os, "startfile", create=True) as opener:
                m.open_path(r"C:\x\a.mp4")
            opener.assert_called_once_with(r"C:\x\a.mp4")
        else:
            with mock.patch.object(m.subprocess, "Popen") as popen:
                m.open_path("/x/a.mp4")
            self.assertEqual(popen.call_args[0][0], ["xdg-open", "/x/a.mp4"])
            self.assertTrue(popen.call_args[1]["start_new_session"])

    @unittest.skipIf(os.name == "nt", "xdg-open")
    def test_missing_opener_is_an_oserror(self):
        with mock.patch.object(m.subprocess, "Popen", side_effect=FileNotFoundError("xdg-open")):
            with self.assertRaises(OSError):
                m.open_path("/x/a.mp4")


class PlatformConstantsTests(unittest.TestCase):
    def test_program_name_follows_the_system(self):
        self.assertEqual(os.path.basename(m.YTDLP), "yt-dlp.exe" if m.IS_WINDOWS else "yt-dlp")


if __name__ == "__main__":
    unittest.main()
