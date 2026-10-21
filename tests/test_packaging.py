import importlib.util
import os
import re
import sys
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

    def test_installer_offers_fourteen_languages_and_local_translations_exist(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        entries = re.findall(r'^Name: "(\w+)"; MessagesFile: "([^"]+)"', iss, re.M)
        self.assertEqual(len(entries), 14)
        local = [rel for _name, rel in entries if not rel.startswith("compiler:")]
        self.assertEqual(sorted(os.path.basename(r) for r in local),
                         ["ChineseSimplified.isl", "Hindi.islu", "SerbianLatin.isl", "Vietnamese.isl"])
        for rel in local:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "packaging", rel.replace("\\", os.sep))), rel)
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "packaging", "languages", "README.md")))

    def test_installer_shows_the_filipino_note_on_the_welcome_page(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        self.assertIn("DisableWelcomePage=no", iss)
        self.assertIn("FilipinoNote=Nag-aalok ang programang ito ng salin sa Filipino sa loob ng software.", iss)
        self.assertIn("CustomMessage('FilipinoNote')", iss)
        self.assertIn("WizardForm.WelcomePage", iss)

    def test_uninstaller_offers_to_delete_the_data_in_every_language(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        langs = [n for n, _rel in re.findall(r'^Name: "(\w+)"; MessagesFile: "([^"]+)"', iss, re.M)]
        self.assertEqual(len(langs), 14)
        for lang in ["", *[f"{n}." for n in langs if n != "english"]]:
            line = next((l for l in iss.splitlines() if l.startswith(f"{lang}DeleteDataPrompt=")), None)
            self.assertIsNotNone(line, f"message manquant : {lang or 'english'}")
            self.assertIn("%1", line, "chemin du dossier")
            self.assertGreater(len(line), 40)
        self.assertIn("procedure CurUninstallStepChanged", iss)
        self.assertIn("usPostUninstall", iss)
        self.assertIn("MB_DEFBUTTON2", iss, "« Non » est le choix par défaut")
        self.assertIn("{param:DELETEDATA|0}", iss, "désinstallation silencieuse : données conservées par défaut")
        self.assertTrue(iss.startswith("﻿"), "BOM UTF-8 : les messages contiennent des caractères non ASCII")

    def test_data_folder_matches_the_application(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        self.assertIn('#define DataDirName "yt-dlp-GUI"', iss)
        source = _read(m.__file__)
        self.assertIn('"yt-dlp-GUI"', source, "dossier des données dans %LOCALAPPDATA% (_resolve_dirs)")

    def test_installer_detects_the_running_application(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        self.assertIn(f"AppMutex={m.RUN_MUTEX_NAME}", iss)
        self.assertIn("UninstallDisplayName={#AppName}", iss)

    def test_installer_offers_to_force_close_the_running_application(self):
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        langs = [n for n, _rel in re.findall(r'^Name: "(\w+)"; MessagesFile: "([^"]+)"', iss, re.M)]
        for lang in ["", *[f"{n}." for n in langs if n != "english"]]:
            for key in ("AppRunningTitle", "AppRunningText", "AppRunningForce", "AppRunningRetry", "AppRunningCancel"):
                line = next((l for l in iss.splitlines() if l.startswith(f"{lang}{key}=")), None)
                self.assertIsNotNone(line, f"message manquant : {lang or 'english'} {key}")
                self.assertGreaterEqual(len(line.split("=", 1)[1]), 2)
        self.assertIn("function InitializeSetup", iss)
        self.assertIn("function InitializeUninstall", iss)
        self.assertIn("TaskDialogMsgBox", iss, "boutons personnalisés : « Forcer la fermeture »")
        self.assertIn("/F /IM {#AppExe} /T", iss, "fermeture forcée avec les processus enfants (téléchargements)")
        self.assertIn("{param:FORCECLOSE|0}", iss, "installation silencieuse : fermeture seulement avec /FORCECLOSE=1")
        self.assertIn(f"RunMutexName = '{m.RUN_MUTEX_NAME}'", iss, "même mutex que le logiciel")

    def test_no_pascal_line_starts_with_an_opening_bracket(self):
        """Inno Setup lit « [ » en début de ligne comme une balise de section : « Invalid section tag »."""
        iss = _read(os.path.join(ROOT, "packaging", "yt-dlp-gui.iss"))
        code = iss.split("\n[Code]", 1)[1]
        for number, line in enumerate(code.splitlines(), 1):
            self.assertFalse(line.lstrip().startswith("["), f"[Code] ligne {number} : {line.strip()[:60]}")

    @unittest.skipUnless(os.path.isfile(os.path.join(ROOT, "dist", "yt-dlp-gui", "yt-dlp-gui.exe")), "pas de build PyInstaller local")
    def test_installer_script_compiles(self):
        import subprocess
        import tempfile
        sys.path.insert(0, os.path.join(ROOT, "packaging"))
        import build
        iscc = build.find_iscc()
        if not iscc:
            self.skipTest("Inno Setup introuvable")
        with tempfile.TemporaryDirectory() as out:
            result = subprocess.run([iscc, "/Q", f"/O{out}", "/DAppVersion=9.9.9", "/DDataDirName=yt-dlp-GUI-test",
                                     os.path.join(ROOT, "packaging", "yt-dlp-gui.iss")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(os.name == "nt", "mutex nommé Windows")
    def test_application_holds_the_named_mutex(self):
        import ctypes
        handle = m._acquire_run_mutex()
        self.assertTrue(handle)
        opened = ctypes.windll.kernel32.OpenMutexW(0x00100000, False, m.RUN_MUTEX_NAME)   # SYNCHRONIZE
        self.assertTrue(opened, "visible par un autre processus (l'installateur)")
        ctypes.windll.kernel32.CloseHandle(opened)

    def test_build_outputs_are_ignored_by_git(self):
        ignore = _read(os.path.join(ROOT, ".gitignore"))
        for entry in ("build/", "dist/", "bin/"):
            self.assertIn(entry, ignore.splitlines())


if __name__ == "__main__":
    unittest.main()
