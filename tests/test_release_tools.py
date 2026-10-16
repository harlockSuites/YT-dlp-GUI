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
        notes = rt.release_notes(_read(os.path.join(ROOT, "CHANGELOG.md")), m.__version__)
        self.assertTrue(notes.strip())

    def test_cli_writes_notes_file(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        out = os.path.join(d, "sub", "notes.md")
        self.assertEqual(rt.main(["notes", "--out", out]), 0)
        self.assertTrue(_read(out).strip())


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

    def test_triggers_on_version_tags_and_can_be_run_by_hand(self):
        self.assertIn('tags: ["v*"]', self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("contents: write", self.text)

    def test_publishes_only_for_tags(self):
        self.assertRegex(self.text, r"Publier la release\s+if: startsWith\(github\.ref, 'refs/tags/v'\)")

    def test_published_files_match_the_checksum_patterns(self):
        listed = set(re.findall(r"^\s+dist/(\S+)$", self.text, re.M))
        for pattern in rt.ARTIFACT_PATTERNS:
            self.assertIn(pattern, listed)
        self.assertIn("SHA256SUMS.txt", listed)

    def test_referenced_scripts_and_requirements_exist(self):
        for rel in re.findall(r"python (?:-X utf8 )?(packaging/\S+\.py)", self.text):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), rel)
        req = _read(os.path.join(ROOT, "packaging", "requirements-build.txt"))
        self.assertRegex(req, r"^pyinstaller==\d+\.\d+\.\d+$")

    def test_tests_run_before_building(self):
        self.assertLess(self.text.index("unittest discover"), self.text.index("packaging/build.py"))


if __name__ == "__main__":
    unittest.main()
