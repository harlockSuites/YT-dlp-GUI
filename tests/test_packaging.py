import importlib.util
import os
import re
import tempfile
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()


def _load_build():
    spec = importlib.util.spec_from_file_location("ytgui_build", os.path.join(ROOT, "packaging", "build.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class ResolveDirsTests(unittest.TestCase):
    def test_from_sources_everything_stays_next_to_the_script(self):
        res, data = m._resolve_dirs(False, r"C:\Python\python.exe", r"C:\src\app", None, {})
        self.assertEqual((res, data), (r"C:\src\app", r"C:\src\app"))

    def test_installed_exe_uses_local_app_data(self):
        d = tempfile.mkdtemp()
        res, data = m._resolve_dirs(True, os.path.join(d, "yt-dlp-gui.exe"), "ignoré", os.path.join(d, "_internal"),
                                    {"LOCALAPPDATA": r"C:\Users\x\AppData\Local"})
        self.assertEqual(res, os.path.join(d, "_internal"))
        self.assertEqual(data, os.path.join(r"C:\Users\x\AppData\Local", "yt-dlp-GUI"))

    def test_portable_flag_keeps_data_next_to_the_exe(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "portable.flag"), "w") as f:
            f.write("x")
        res, data = m._resolve_dirs(True, os.path.join(d, "yt-dlp-gui.exe"), "ignoré", None,
                                    {"LOCALAPPDATA": r"C:\Users\x\AppData\Local"})
        self.assertEqual(data, d)
        self.assertEqual(res, d, "sans _MEIPASS, les ressources sont à côté de l'exécutable")

    def test_missing_local_app_data_falls_back_to_home(self):
        d = tempfile.mkdtemp()
        _, data = m._resolve_dirs(True, os.path.join(d, "x.exe"), "", None, {})
        self.assertTrue(data.endswith(os.path.join("AppData", "Local", "yt-dlp-GUI")))

    def test_current_constants_are_consistent(self):
        self.assertEqual(m.RESOURCE_DIR, ROOT)
        self.assertEqual(m.DATA_DIR, ROOT)
        self.assertEqual(os.path.dirname(m.YTDLP), m.DATA_DIR)
        self.assertEqual(os.path.dirname(m.LOCAL_BIN), m.DATA_DIR)
        self.assertTrue(os.path.isdir(os.path.join(m.RESOURCE_DIR, "lang")))
        self.assertTrue(os.path.isfile(m.ICON_FILE))
        self.assertTrue(os.path.isdir(m.ASSETS_DIR))


class BuildScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = _load_build()

    def test_version_matches_application(self):
        self.assertEqual(self.build.read_version(), m.__version__)

    def test_version_resource_contains_version(self):
        text = self.build.version_file_text("1.2.3")
        self.assertIn("filevers=(1, 2, 3, 0)", text)
        self.assertIn("StringStruct('FileVersion', '1.2.3')", text)
        compile(text.replace("VSVersionInfo", "dict").replace("FixedFileInfo", "dict")
                .replace("StringFileInfo", "list").replace("StringTable", "list")
                .replace("StringStruct", "tuple").replace("VarFileInfo", "list").replace("VarStruct", "tuple"),
                "version", "eval")

    def test_inno_script_references_existing_files(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        for rel in re.findall(r"(?:SetupIconFile|LicenseFile)=\.\.\\(\S+)", iss):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), rel)
        self.assertIn("{#AppVersion}", iss)
        self.assertIn("PrivilegesRequired=lowest", iss)

    def test_build_outputs_are_ignored_by_git(self):
        ignore = _read(os.path.join(ROOT, ".gitignore"))
        for entry in ("build/", "dist/", "bin/"):
            self.assertIn(entry, ignore.splitlines())


if __name__ == "__main__":
    unittest.main()
