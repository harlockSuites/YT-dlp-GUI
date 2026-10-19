import os
import shlex
import shutil
import tempfile
import time
import unittest
from unittest import mock

from tests._loader import load_gui

m = load_gui()

LONG_FORMAT = ("bestvideo[vcodec^=avc1][height<=360]+bestaudio[language^=fr]+bestaudio[language^=en]"
               "+bestaudio[language^=es]+bestaudio[language^=ja]/bestvideo[height<=360]+bestaudio/best")
OUT = r"C:/Users/José Müller/Téléchargements/TEST GUI/File attente\%(title)s.%(ext)s"
ARGS = [r"C:\Users\Utilisateur\AppData\Local\yt-dlp-GUI\yt-dlp.exe", "-f", LONG_FORMAT, "--audio-multistreams",
        "--sub-lang", "fr,en,es", "-o", OUT, "--progress", "--newline", "--", "https://www.youtube.com/watch?v=abc"]


class CommandFileTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="cmd-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        patcher = mock.patch.object(m, "COMMAND_DIR", os.path.join(self.d, "cmd"))
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _read_like_yt_dlp(path):
        """Relecture du fichier comme le fait yt-dlp : shlex ligne par ligne, commentaires ignorés."""
        out = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                out += shlex.split(line, comments=True)
        return out

    def test_command_line_becomes_short_and_stable(self):
        run_args, path = m.command_file_args(ARGS)
        self.addCleanup(m.remove_command_file, path)
        self.assertEqual(run_args[0], ARGS[0])
        self.assertEqual(run_args[1], "--config-locations")
        self.assertEqual(run_args[2], path)
        self.assertEqual(run_args[3:], ["--", "https://www.youtube.com/watch?v=abc"])
        self.assertNotIn("^=", " ".join(run_args), "plus de sélecteur de format sur la ligne de commande")

    def test_file_gives_back_exactly_the_original_options(self):
        run_args, path = m.command_file_args(ARGS)
        self.addCleanup(m.remove_command_file, path)
        self.assertEqual(self._read_like_yt_dlp(path), ARGS[1:-2])

    def test_special_characters_survive(self):
        args = [ARGS[0], "-o", r"C:\Dossier test\100% 'quoté' #1\%(title)s.%(ext)s", "--", "u"]
        run_args, path = m.command_file_args(args)
        self.addCleanup(m.remove_command_file, path)
        self.assertEqual(self._read_like_yt_dlp(path), args[1:-2])

    def test_file_declares_utf8(self):
        _run, path = m.command_file_args(ARGS)
        self.addCleanup(m.remove_command_file, path)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.readline().strip(), "# coding: utf-8")

    def test_commands_without_url_separator_are_left_alone(self):
        args = [ARGS[0], "-F", "https://x"]
        self.assertEqual(m.command_file_args(args), (args, None))

    def test_falls_back_to_the_full_command_when_the_file_cannot_be_written(self):
        with mock.patch.object(m.os, "makedirs", side_effect=OSError("disque plein")):
            run_args, path = m.command_file_args(ARGS)
        self.assertEqual((run_args, path), (ARGS, None))

    def test_remove_and_cleanup(self):
        _run, path = m.command_file_args(ARGS)
        m.remove_command_file(path)
        self.assertFalse(os.path.exists(path))
        m.remove_command_file(path)          # déjà supprimé : sans erreur
        m.remove_command_file(None)
        _run, old = m.command_file_args(ARGS)
        _run, fresh = m.command_file_args(ARGS)
        past = time.time() - 3 * 24 * 3600
        os.utime(old, (past, past))
        m.cleanup_command_files()
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(fresh))
        m.remove_command_file(fresh)

    def test_download_launchers_use_it(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertEqual(source.count("= command_file_args(args)"), 2)
        self.assertEqual(source.count("remove_command_file(conf_file)"), 2)


if __name__ == "__main__":
    unittest.main()
