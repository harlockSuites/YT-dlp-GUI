import hashlib
import importlib.util
import io
import os
import tarfile
import tempfile
import time
import unittest

from tests._loader import ROOT

spec = importlib.util.spec_from_file_location("build_bootloader", os.path.join(ROOT, "packaging", "build_bootloader.py"))
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)


def _write(path, data=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


class SdistInfoTests(unittest.TestCase):
    def test_picks_the_sdist_entry(self):
        data = {"urls": [{"packagetype": "bdist_wheel", "url": "https://x/w.whl", "digests": {"sha256": "aa"}},
                         {"packagetype": "sdist", "url": "https://x/s.tar.gz", "digests": {"sha256": "bb"}}]}
        self.assertEqual(bb.sdist_info(data), ("https://x/s.tar.gz", "bb"))

    def test_no_sdist_is_an_error(self):
        with self.assertRaises(SystemExit):
            bb.sdist_info({"urls": [{"packagetype": "bdist_wheel", "url": "u", "digests": {"sha256": "a"}}]})
        with self.assertRaises(SystemExit):
            bb.sdist_info({})


class DownloadTests(unittest.TestCase):
    def test_matching_hash_is_accepted_and_wrong_hash_is_refused_and_removed(self):
        with tempfile.TemporaryDirectory() as d:
            source = os.path.join(d, "source.bin")
            _write(source, b"contenu")
            url = "file:///" + source.replace("\\", "/")
            good = hashlib.sha256(b"contenu").hexdigest()
            dest = os.path.join(d, "copie.bin")
            self.assertEqual(bb.download_verified(url, good, dest), dest)
            self.assertTrue(os.path.isfile(dest))
            bad = os.path.join(d, "mauvaise.bin")
            with self.assertRaises(SystemExit):
                bb.download_verified(url, "0" * 64, bad)
            self.assertFalse(os.path.exists(bad), "un fichier à la somme inattendue ne reste pas sur le disque")


class ExtractTests(unittest.TestCase):
    def _archive(self, d, name):
        path = os.path.join(d, "a.tar.gz")
        with tarfile.open(path, "w:gz") as tar:
            info = tarfile.TarInfo(name)
            payload = b"data"
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
        return path

    def test_normal_archive_is_extracted(self):
        with tempfile.TemporaryDirectory() as d:
            bb.extract(self._archive(d, "dossier/fichier.txt"), os.path.join(d, "out"))
            self.assertTrue(os.path.isfile(os.path.join(d, "out", "dossier", "fichier.txt")))

    def test_path_leaving_the_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out")
            os.makedirs(out)
            with self.assertRaises((SystemExit, tarfile.TarError)):
                bb.extract(self._archive(d, "../evade.txt"), out)
            self.assertFalse(os.path.exists(os.path.join(d, "evade.txt")))


class CopyCompiledTests(unittest.TestCase):
    def test_only_files_written_by_the_compilation_are_copied(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "src")
            target = os.path.join(d, "installed")
            folder = os.path.join(src, "PyInstaller", "bootloader", "Windows-64bit-intel")
            _write(os.path.join(folder, "runw.exe"), b"nouveau")
            _write(os.path.join(folder, "old.exe"), b"ancien")
            os.utime(os.path.join(folder, "old.exe"), (1, 1))                     # pas touché par la compilation
            _write(os.path.join(src, "PyInstaller", "bootloader", "Linux-64bit", "run"), b"linux")
            _write(os.path.join(target, "Windows-64bit-intel", "runw.exe"), b"officiel")
            changed = bb.copy_compiled(src, time.time() - 5, target)
            self.assertEqual([c[0] for c in changed], ["Windows-64bit-intel/runw.exe"])
            name, old, new = changed[0]
            self.assertEqual(old, hashlib.sha256(b"officiel").hexdigest())
            self.assertEqual(new, hashlib.sha256(b"nouveau").hexdigest())
            self.assertNotEqual(old, new)
            with open(os.path.join(target, "Windows-64bit-intel", "runw.exe"), "rb") as f:
                self.assertEqual(f.read(), b"nouveau")
            self.assertFalse(os.path.exists(os.path.join(target, "Windows-64bit-intel", "old.exe")))
            self.assertFalse(os.path.exists(os.path.join(target, "Linux-64bit")))

    def test_installed_pyinstaller_version_is_read(self):
        self.assertRegex(bb.installed_version(), r"^\d+\.\d+")


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, ".github", "workflows", "bootloader-test.yml"), encoding="utf-8") as f:
            self.text = f.read()

    def test_the_trial_workflow_never_publishes(self):
        self.assertIn("workflow_dispatch", self.text)
        self.assertNotIn("push:", self.text)
        self.assertNotIn("tags:", self.text)
        self.assertNotIn("action-gh-release", self.text)
        self.assertIn("contents: read", self.text, "lecture seule : aucune écriture dans le dépôt")

    def test_it_compiles_the_bootloader_before_building(self):
        compile_at = self.text.index("build_bootloader.py")
        build_at = self.text.index("packaging/build.py")
        self.assertLess(compile_at, build_at)

    def test_the_artifact_has_its_own_name(self):
        self.assertIn("yt-dlp-gui-windows-lanceur-compile", self.text)


if __name__ == "__main__":
    unittest.main()
