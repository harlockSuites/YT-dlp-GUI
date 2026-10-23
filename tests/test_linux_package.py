"""Paquets Linux (AppImage, .tar.gz), mise à jour, polices, icône et workflows : testés sur tous les systèmes."""
import importlib.util
import os
import re
import stat
import struct
import tarfile
import tempfile
import shutil
import unittest
from unittest import mock

from tests._loader import ROOT, load_gui, tk_available

m = load_gui()


def _read(*parts, raw=False):
    """Contenu d'un fichier du dépôt. Les fins de ligne sont normalisées (une copie Windows du dépôt les a en CRLF,
    comme sur le serveur d'intégration), sauf avec `raw=True` pour les fichiers Linux qui doivent rester en LF."""
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="" if raw else None) as f:
        return f.read()


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "packaging", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bl = _load_script("build_linux")
rt = _load_script("release_tools")


class ReleaseAssetsForUpdateTests(unittest.TestCase):
    def test_windows_patterns_are_unchanged(self):
        self.assertEqual(m.release_asset_patterns(True),
                         {"installer": "yt-dlp-gui-setup-*.exe", "portable": "yt-dlp-gui-portable-*.zip"})

    def test_linux_patterns_follow_the_architecture(self):
        self.assertEqual(m.release_asset_patterns(False, "x86_64"),
                         {"appimage": "yt-dlp-gui-*-x86_64.AppImage", "portable": "yt-dlp-gui-linux-*-x86_64.tar.gz"})
        self.assertEqual(m.release_asset_patterns(False, "arm64")["appimage"], "yt-dlp-gui-*-aarch64.AppImage")
        self.assertEqual(m.release_asset_patterns(False, "riscv64"), {})

    def test_published_names_match_the_patterns_the_program_looks_for(self):
        import fnmatch
        patterns = m.release_asset_patterns(False, "x86_64")
        self.assertTrue(fnmatch.fnmatch(bl.appimage_name("0.2.0", "x86_64"), patterns["appimage"]))
        self.assertTrue(fnmatch.fnmatch(bl.tarball_name("0.2.0", "x86_64"), patterns["portable"]))
        self.assertFalse(fnmatch.fnmatch(bl.tarball_name("0.2.0", "x86_64"), patterns["appimage"]))
        self.assertFalse(fnmatch.fnmatch(bl.appimage_name("0.2.0", "aarch64"), patterns["appimage"]),
                         "pas le fichier d'une autre architecture")

    def test_release_tools_know_the_same_names(self):
        import fnmatch
        for name in (bl.appimage_name("0.2.0", "x86_64"), bl.tarball_name("0.2.0", "aarch64")):
            self.assertTrue(any(fnmatch.fnmatch(name, p) for p in rt.LINUX_ARTIFACT_PATTERNS), name)
            self.assertFalse(any(fnmatch.fnmatch(name, p) for p in rt.ARTIFACT_PATTERNS), name)

    def test_asset_choice_for_linux_install_kinds(self):
        info = {"assets": [{"name": n, "url": "https://github.com/x/" + n, "size": 1} for n in (
            "yt-dlp-gui-setup-9.0.0.exe", "yt-dlp-gui-portable-9.0.0.zip", "yt-dlp-gui-9.0.0-x86_64.AppImage",
            "yt-dlp-gui-linux-9.0.0-x86_64.tar.gz", "yt-dlp-gui-9.0.0-aarch64.AppImage")]}
        with mock.patch.object(m, "_ASSET_PATTERNS", m.release_asset_patterns(False, "x86_64")):
            self.assertEqual(m.pick_asset(info, "appimage")["name"], "yt-dlp-gui-9.0.0-x86_64.AppImage")
            self.assertEqual(m.pick_asset(info, "portable")["name"], "yt-dlp-gui-linux-9.0.0-x86_64.tar.gz")
            self.assertIsNone(m.pick_asset(info, "installer"))
            self.assertIsNone(m.pick_asset(info, "source"))

    def test_checksums_for_the_linux_files_only(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for name in ("yt-dlp-gui-9.0.0-x86_64.AppImage", "yt-dlp-gui-linux-9.0.0-x86_64.tar.gz",
                     "yt-dlp-gui-setup-9.0.0.exe", "SHA256SUMS.txt"):
            with open(os.path.join(d, name), "wb") as f:
                f.write(b"x")
        out = os.path.join(d, "SHA256SUMS-linux.txt")
        names = rt.write_checksums(d, out, rt.LINUX_ARTIFACT_PATTERNS)
        self.assertEqual(names, ["yt-dlp-gui-9.0.0-x86_64.AppImage", "yt-dlp-gui-linux-9.0.0-x86_64.tar.gz"])
        self.assertEqual(rt.main(["checksums", "--platform", "windows", "--dir", d, "--out", out + "w"]), 0)
        self.assertEqual(rt.artifact_files(d), ["yt-dlp-gui-setup-9.0.0.exe"], "Windows : liste inchangée")


class InstallKindTests(unittest.TestCase):
    def test_linux_kinds(self):
        exe = "/opt/yt-dlp-gui/yt-dlp-gui"
        with mock.patch.object(m, "IS_WINDOWS", False):
            self.assertEqual(m._install_kind(frozen=False), "source")
            self.assertEqual(m._install_kind(True, exe, env={}), "portable")
            self.assertEqual(m._install_kind(True, exe, env={"APPIMAGE": "/home/u/yt-dlp-gui.AppImage"}), "appimage")
            self.assertEqual(m._install_kind(True, exe, env={"APPIMAGE": ""}), "portable")

    def test_windows_ignores_the_appimage_variable(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        exe = os.path.join(d, "yt-dlp-gui.exe")
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertEqual(m._install_kind(True, exe, env={"APPIMAGE": "x"}), "installer")


class FontTests(unittest.TestCase):
    def test_windows_keeps_its_fonts(self):
        with mock.patch.object(m, "IS_WINDOWS", True), mock.patch.object(m, "UI_FONT", "Segoe UI"), \
                mock.patch.object(m, "MONO_FONT", "Consolas"):
            m.use_system_fonts()
            self.assertEqual((m.UI_FONT, m.MONO_FONT), ("Segoe UI", "Consolas"))

    @unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
    def test_elsewhere_the_system_fonts_of_tk_are_used(self):
        import tkinter as tk
        import tkinter.font as tkfont
        root = tk.Tk()
        self.addCleanup(root.destroy)
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "UI_FONT", "Segoe UI"), \
                mock.patch.object(m, "MONO_FONT", "Consolas"):
            m.use_system_fonts()
            self.assertEqual(m.UI_FONT, tkfont.nametofont("TkDefaultFont").actual("family"))
            self.assertEqual(m.MONO_FONT, tkfont.nametofont("TkFixedFont").actual("family"))

    def test_no_font_name_is_hard_coded_outside_the_two_constants(self):
        source = _read("yt-dlp-gui.pyw")
        self.assertEqual(source.count('"Segoe UI"'), 1)
        self.assertEqual(source.count('"Consolas"'), 1)


class IconTests(unittest.TestCase):
    def test_png_icon_is_a_256_pixel_png_with_the_ico_picture(self):
        with open(m.ICON_PNG, "rb") as f:
            png = f.read()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png[16:24]), (256, 256))
        with open(m.ICON_FILE, "rb") as f:
            ico = f.read()
        size, offset = struct.unpack("<II", ico[6 + 8:6 + 16])
        self.assertEqual(ico[offset:offset + size], png, "le PNG est l'image du .ico (une seule source)")

    @unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
    @unittest.skipIf(os.name == "nt", "icône .ico sous Windows")
    def test_window_gets_the_png_icon_and_a_class_for_the_launcher(self):
        m.load_lang("fr")
        app = m.YtDlpGui()
        self.addCleanup(app.destroy)
        app.withdraw()
        self.assertEqual(app._icon.width(), 256)
        self.assertEqual(app.winfo_class().lower(), "yt-dlp-gui")


class LinuxPackageFilesTests(unittest.TestCase):
    def test_apprun_is_a_posix_script_with_lf_endings_that_starts_the_program(self):
        text = _read("packaging", "linux", "AppRun", raw=True)   # .gitattributes : LF même après une copie sous Windows
        self.assertTrue(text.startswith("#!/bin/sh\n"))
        self.assertNotIn("\r", text)
        self.assertIn('exec "$HERE/usr/lib/yt-dlp-gui/yt-dlp-gui" "$@"', text)

    def test_desktop_file_matches_the_icon_and_the_window_class(self):
        text = _read("packaging", "linux", "yt-dlp-gui.desktop", raw=True)
        self.assertNotIn("\r", text)
        entries = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)
        self.assertEqual(entries["Type"], "Application")
        self.assertEqual(entries["Exec"], "yt-dlp-gui")
        self.assertEqual(entries["Icon"], "yt-dlp-gui")
        self.assertEqual(entries["StartupWMClass"], "yt-dlp-gui")
        self.assertTrue(entries["Categories"].endswith(";"))
        self.assertEqual(entries["Terminal"], "false")

    def test_gitattributes_keeps_lf_for_the_linux_files(self):
        attrs = _read(".gitattributes")
        self.assertIn("packaging/linux/AppRun text eol=lf", attrs)
        self.assertIn("packaging/linux/*.desktop text eol=lf", attrs)

    def test_names_and_architectures(self):
        self.assertEqual(bl.read_version(), m.__version__)
        self.assertEqual(bl.tarball_name("0.2.0", "x86_64"), "yt-dlp-gui-linux-0.2.0-x86_64.tar.gz")
        self.assertEqual(bl.appimage_name("0.2.0", "aarch64"), "yt-dlp-gui-0.2.0-aarch64.AppImage")
        self.assertEqual(bl.arch_name("AMD64"), "x86_64")
        self.assertEqual(bl.arch_name("arm64"), "aarch64")
        with self.assertRaises(SystemExit):
            bl.arch_name("riscv64")

    def test_tarball_has_one_top_folder_and_neutral_owner(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        app = os.path.join(d, "yt-dlp-gui")
        os.makedirs(os.path.join(app, "_internal"))
        with open(os.path.join(app, "yt-dlp-gui"), "wb") as f:
            f.write(b"\x7fELF")
        os.chmod(os.path.join(app, "yt-dlp-gui"), 0o755)
        with open(os.path.join(app, "_internal", "x.so"), "wb") as f:
            f.write(b"x")
        with mock.patch.object(bl, "APP_DIST", app), mock.patch.object(bl, "DIST", d):
            out = bl.build_tarball("9.9.9", "x86_64")
        self.assertEqual(os.path.basename(out), "yt-dlp-gui-linux-9.9.9-x86_64.tar.gz")
        with tarfile.open(out) as tf:
            names = tf.getnames()
            self.assertEqual({n.split("/")[0] for n in names}, {"yt-dlp-gui"})
            self.assertIn("yt-dlp-gui/yt-dlp-gui", names)
            member = tf.getmember("yt-dlp-gui/yt-dlp-gui")
            self.assertEqual((member.uid, member.gid, member.uname), (0, 0, "root"))
            if os.name != "nt":
                self.assertTrue(member.mode & stat.S_IXUSR, "l'exécutable reste exécutable")

    @unittest.skipIf(os.name == "nt", "liens symboliques et droits POSIX")
    def test_appdir_layout_expected_by_appimagetool(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        app = os.path.join(d, "yt-dlp-gui")
        os.makedirs(app)
        with open(os.path.join(app, "yt-dlp-gui"), "wb") as f:
            f.write(b"x")
        appdir = os.path.join(d, "AppDir")
        with mock.patch.object(bl, "APP_DIST", app):
            bl.prepare_appdir(appdir)
        self.assertTrue(os.access(os.path.join(appdir, "AppRun"), os.X_OK))
        for name in ("yt-dlp-gui.desktop", "yt-dlp-gui.png", os.path.join("usr", "lib", "yt-dlp-gui", "yt-dlp-gui")):
            self.assertTrue(os.path.isfile(os.path.join(appdir, name)), name)
        self.assertEqual(os.readlink(os.path.join(appdir, ".DirIcon")), "yt-dlp-gui.png")

    def test_missing_appimagetool_is_explained(self):
        with mock.patch.object(bl.shutil, "which", return_value=None), \
                mock.patch.dict(os.environ, {"APPIMAGETOOL": ""}):
            with self.assertRaises(SystemExit) as ctx:
                bl.build_appimage("9.9.9", "x86_64")
        self.assertIn("appimagetool", str(ctx.exception))

    def test_the_ffmpeg_archive_format_is_bundled(self):
        """L'assistant lit une archive .tar.xz : PyInstaller doit embarquer lzma."""
        with open(os.path.join(ROOT, "packaging", "build_linux.py"), encoding="utf-8") as f:
            self.assertIn('"--hidden-import", "lzma"', f.read())


class WorkflowTests(unittest.TestCase):
    def test_tests_run_on_linux_and_on_the_linux_branch(self):
        text = _read(".github", "workflows", "tests.yml")
        self.assertIn("branches: [main, Linux]", text)
        self.assertIn("runs-on: windows-latest", text)
        self.assertRegex(text, r"tests-linux:\n\s+runs-on: ubuntu-22\.04")
        self.assertIn("xvfb-run -a python3", text)

    def test_release_workflow_builds_only_linux_and_reacts_only_to_linux_tags(self):
        text = _read(".github", "workflows", "release.yml")
        self.assertIn('tags: ["Linux-v*"]', text)
        self.assertNotIn('"v*"', text, "les étiquettes Windows (v*) relèvent du workflow de la branche main")
        self.assertNotIn("windows-latest", text)
        self.assertNotIn("choco", text)
        self.assertEqual(text.count("    runs-on:"), 1, "un seul job, sous Ubuntu")
        self.assertIn("runs-on: ubuntu-22.04", text)
        self.assertIn("packaging/build_linux.py", text)
        self.assertIn("--platform linux", text)

    def test_the_linux_release_is_a_prerelease_never_marked_latest(self):
        """Le logiciel Windows 0.1.7 interroge « releases/latest » : une release Linux normale la détournerait."""
        text = _read(".github", "workflows", "release.yml")
        self.assertRegex(text, r"prerelease: true")
        self.assertRegex(text, r'make_latest: "false"')
        self.assertIn("startsWith(github.ref, 'refs/tags/Linux-v')", text)
        self.assertEqual(text.count("softprops/action-gh-release"), 1)

    def test_the_tag_is_checked_against_the_version_with_the_linux_prefix_and_notes_come_from_the_linux_changelog(self):
        text = _read(".github", "workflows", "release.yml")
        self.assertIn('check-tag "${{ github.ref_name }}" --prefix Linux-v', text)
        self.assertIn("--changelog CHANGELOG-linux.md", text)
        self.assertNotIn("CHANGELOG.md", text.replace("CHANGELOG-linux.md", ""))

    def test_linux_release_pins_appimagetool(self):
        text = _read(".github", "workflows", "release.yml")
        self.assertRegex(text, r"appimagetool/releases/download/1\.9\.1/")
        self.assertRegex(text, r"[0-9a-f]{64}  appimagetool")
        self.assertIn("sha256sum -c -", text)

    def test_the_pinned_checksum_has_a_sha256_shape_and_the_tool_is_not_unpinned(self):
        text = _read(".github", "workflows", "release.yml")
        self.assertNotIn("/continuous/", text)
        self.assertEqual(len(re.findall(r"\b[0-9a-f]{64}\b", text)), 1)


if __name__ == "__main__":
    unittest.main()
