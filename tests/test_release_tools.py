import importlib.util
import os
import re
import shutil
import tempfile
import unittest

from tests._loader import ROOT, load_gui

m = load_gui()


def _load_tools():
    spec = importlib.util.spec_from_file_location("ytgui_release_tools",
                                                  os.path.join(ROOT, "packaging", "release_tools.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rt = _load_tools()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


SAMPLE = """# Journal

## [0.2.0] — 2026-11-01

### Ajouté
- Nouveauté A

## [0.1.0] — en préparation

### Ajouté
- Fonction 1
- Fonction 2

### Corrigé
- Bogue X
"""


class TagTests(unittest.TestCase):
    def test_tag_must_be_v_plus_version(self):
        self.assertTrue(rt.tag_matches_version("v1.2.3", "1.2.3"))
        for bad in ("1.2.3", "v1.2.4", "v1.2.3-rc1", "V1.2.3", ""):
            self.assertFalse(rt.tag_matches_version(bad, "1.2.3"), bad)

    def test_cli_check_tag_exit_codes(self):
        self.assertEqual(rt.main(["check-tag", f"v{m.__version__}"]), 0)
        self.assertEqual(rt.main(["check-tag", "v99.0.0"]), 1)

    def test_linux_tags_use_their_own_prefix(self):
        self.assertTrue(rt.tag_matches_version("Linux-v1.2.3", "1.2.3", "Linux-v"))
        for bad in ("v1.2.3", "Linux-1.2.3", "linux-v1.2.3", "Linux-v1.2.4", "Linux-v1.2.3-rc1", "Linux-vv1.2.3"):
            self.assertFalse(rt.tag_matches_version(bad, "1.2.3", "Linux-v"), bad)
        self.assertFalse(rt.tag_matches_version("Linux-v1.2.3", "1.2.3"), "préfixe Windows par défaut")

    def test_cli_check_tag_with_the_linux_prefix(self):
        self.assertEqual(rt.main(["check-tag", f"Linux-v{m.__version__}", "--prefix", "Linux-v"]), 0)
        self.assertEqual(rt.main(["check-tag", f"v{m.__version__}", "--prefix", "Linux-v"]), 1)
        self.assertEqual(rt.main(["check-tag", "Linux-v99.0.0", "--prefix", "Linux-v"]), 1)

    def test_version_read_matches_application(self):
        self.assertEqual(rt.read_version(), m.__version__)


class NotesTests(unittest.TestCase):
    def test_extracts_only_the_requested_section(self):
        notes = rt.release_notes(SAMPLE, "0.1.0")
        self.assertIn("Fonction 1", notes)
        self.assertIn("Bogue X", notes)
        self.assertNotIn("Nouveauté A", notes)
        self.assertNotIn("## [", notes)

    def test_first_section_stops_at_next_heading(self):
        notes = rt.release_notes(SAMPLE, "0.2.0")
        self.assertIn("Nouveauté A", notes)
        self.assertNotIn("Fonction 1", notes)

    def test_unknown_version_gives_empty(self):
        self.assertEqual(rt.release_notes(SAMPLE, "9.9.9"), "")

    def test_current_changelog_has_notes_for_current_version(self):
        notes = rt.release_notes(_read(os.path.join(ROOT, "CHANGELOG-linux.md")), m.__version__)
        self.assertTrue(notes.strip())
        self.assertIn("Première version Linux", notes)

    def test_cli_writes_notes_file_from_the_chosen_changelog(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        out = os.path.join(d, "sub", "notes.md")
        self.assertEqual(rt.main(["notes", "--changelog", "CHANGELOG-linux.md", "--out", out]), 0)
        self.assertIn("Première version Linux", _read(out))

    def test_the_windows_changelog_is_left_alone_and_has_no_linux_release(self):
        """Windows est figé : son journal ne décrit que Windows et ne contient pas la version Linux."""
        windows = _read(os.path.join(ROOT, "CHANGELOG.md"))
        self.assertNotIn("Première version Linux", windows)
        self.assertNotIn("Linux-v", windows)
        self.assertIn("## [0.1.7] — 2026-10-21", windows)
        self.assertIn("[CHANGELOG.md]", _read(os.path.join(ROOT, "CHANGELOG-linux.md")))


class ChecksumTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def _write(self, name, data):
        with open(os.path.join(self.d, name), "wb") as f:
            f.write(data)

    def test_only_published_artifacts_are_listed_and_hashed(self):
        self._write("yt-dlp-gui-setup-1.0.0.exe", b"installateur")
        self._write("yt-dlp-gui-portable-1.0.0.zip", b"zip")
        self._write("release-notes.md", b"notes")
        self._write("autre.exe", b"x")
        out = os.path.join(self.d, "SHA256SUMS.txt")
        names = rt.write_checksums(self.d, out)
        self.assertEqual(names, ["yt-dlp-gui-portable-1.0.0.zip", "yt-dlp-gui-setup-1.0.0.exe"])
        parsed = m._parse_checksums(_read(out))
        self.assertEqual(sorted(parsed), names, "lisible par le code de l'assistant d'installation")
        self.assertEqual(parsed["yt-dlp-gui-setup-1.0.0.exe"], rt.sha256_of(os.path.join(self.d, names[1])))

    def test_no_artifact_is_an_error(self):
        with self.assertRaises(SystemExit):
            rt.write_checksums(self.d, os.path.join(self.d, "x.txt"))


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = _read(os.path.join(ROOT, ".github", "workflows", "release.yml"))

    """Workflow de la branche Linux : il ne réagit qu'aux étiquettes « Linux-v* » (celui de Windows est sur main)."""

    def test_triggers_on_linux_tags_and_can_be_run_by_hand(self):
        self.assertIn('tags: ["Linux-v*"]', self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("contents: write", self.text)

    def test_publishes_only_for_linux_tags(self):
        self.assertRegex(self.text, r"Publier la préversion Linux\s+if: startsWith\(github\.ref, 'refs/tags/Linux-v'\)")

    def test_published_files_match_the_checksum_patterns(self):
        import fnmatch
        listed = set(re.findall(r"^\s+dist/(\S+)$", self.text, re.M))
        self.assertIn("SHA256SUMS-linux.txt", listed)
        for name in ("yt-dlp-gui-0.1.0-x86_64.AppImage", "yt-dlp-gui-linux-0.1.0-x86_64.tar.gz"):
            self.assertTrue(any(fnmatch.fnmatch(name, g) for g in listed), name)
            self.assertTrue(any(fnmatch.fnmatch(name, p) for p in rt.LINUX_ARTIFACT_PATTERNS), name)

    def test_referenced_scripts_and_requirements_exist(self):
        for rel in re.findall(r"python3? (?:-X utf8 )?(packaging/\S+\.py)", self.text):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), rel)
        req = _read(os.path.join(ROOT, "packaging", "requirements-build.txt"))
        self.assertRegex(req, r"^pyinstaller==\d+\.\d+\.\d+$")

    def test_tests_run_before_building(self):
        self.assertLess(self.text.index("unittest discover"), self.text.index("packaging/build_linux.py"))


if __name__ == "__main__":
    unittest.main()
