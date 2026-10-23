import json
import os
import shutil
import tempfile
import threading
import types
import unittest
from unittest import mock

from tests._loader import load_gui

m = load_gui()
VID_A = "dQw4w9WgXcQ"
VID_B = "jNQXAC9IVRw"


def _text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _json(path):
    return json.loads(_text(path))


def _touch(folder, *names):
    for n in names:
        open(os.path.join(folder, n), "w").close()


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="reg-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)


class SyncRegistryTests(TempDirCase):
    def test_migrates_archive_and_inbox(self):
        with open(os.path.join(self.d, m.ARCHIVE_NAME), "w") as f:
            f.write("youtube old1\n")
        with open(os.path.join(self.d, m.TITLES_NAME), "w", encoding="utf-8") as f:
            f.write("id9\tRenomme\t10\tC:/x/R.webm\n")
        reg = m._sync_registry(self.d)
        self.assertEqual(set(reg), {"old1", "id9"})
        self.assertEqual(reg["id9"]["title"], "Renomme")
        self.assertEqual(reg["id9"]["duration"], 10)
        self.assertEqual(reg["id9"]["file"], "R.webm")
        self.assertEqual(reg["old1"]["title"], "")
        self.assertFalse(os.path.exists(os.path.join(self.d, m.TITLES_NAME)), "boîte de réception vidée")
        txt = _text(os.path.join(self.d, m.ARCHIVE_NAME)).split("\n")
        self.assertEqual([x for x in txt if x], ["youtube id9", "youtube old1"])

    def test_empty_folder_creates_registry(self):
        reg = m._sync_registry(self.d)
        self.assertEqual(reg, {})
        data = _json(os.path.join(self.d, m.REGISTRY_NAME))
        self.assertEqual(data, {"version": 1, "videos": {}})

    def test_corrupted_registry_is_ignored(self):
        with open(os.path.join(self.d, m.REGISTRY_NAME), "w") as f:
            f.write("{pas du json")
        self.assertEqual(m._sync_registry(self.d), {})

    def test_sync_is_idempotent(self):
        with open(os.path.join(self.d, m.ARCHIVE_NAME), "w") as f:
            f.write("youtube a1\n")
        first = m._sync_registry(self.d)
        second = m._sync_registry(self.d)
        self.assertEqual(first, second)


class RegisterTests(TempDirCase):
    def test_register_and_invalid_ids(self):
        m._register_in_archive(self.d, [(VID_A, "Titre", "Titre.mp4", 212),
                                        ("id invalide\nyoutube x", "X", "X.mp4")])
        reg = m._sync_registry(self.d)
        self.assertEqual(list(reg), [VID_A])
        self.assertEqual(reg[VID_A]["duration"], 212)
        self.assertEqual(reg[VID_A]["url"], m._watch_url(VID_A))
        txt = _text(os.path.join(self.d, m.ARCHIVE_NAME))
        self.assertEqual(txt, f"youtube {VID_A}\n")


class MatchingTests(TempDirCase):
    def test_find_existing_matches(self):
        _touch(self.d, "Mon Titre.mp4", "03 - Autre video (1).mkv", "x.part", "notes.txt")
        m._register_in_archive(self.d, [(VID_B, "Deja connu", "Deja connu.mp4")])
        rows = [{"vid": {"id": i, "title": ti}} for i, ti in
                [("aaaaaaaaaaa", "Mon titre"), ("bbbbbbbbbbb", "Autre video"),
                 (VID_B, "Mon Titre"), ("ccccccccccc", "Absent")]]
        found = {r["vid"]["id"]: fn for r, fn, _src in m._find_existing_matches(rows, self.d)}
        self.assertEqual(found, {"aaaaaaaaaaa": "Mon Titre.mp4", "bbbbbbbbbbb": "03 - Autre video (1).mkv"})

    def test_scan_registry_folder_counts(self):
        _touch(self.d, "A.mp4", "B.mp3", "C.webm", "ignore.jpg")
        m._register_in_archive(self.d, [(VID_A, "A", "A.mp4")])
        reg, media, missing, incomplete = m._scan_registry_folder(self.d)
        self.assertEqual(len(media), 3)
        self.assertEqual(sorted(missing), ["B.mp3", "C.webm"])
        self.assertEqual(incomplete, 0)

    def test_helpers(self):
        self.assertEqual(m._norm_title("Hello, World! (Live)"), "helloworldlive")
        self.assertEqual(m._clean_stem("03 - Song (2).mp4"), "Song")
        self.assertEqual(m._tmpl_esc("100% pur"), "100%% pur")


class SearchTests(unittest.TestCase):
    @staticmethod
    def _run_returning(cands):
        out = "\n".join(json.dumps(c) for c in cands)
        return lambda *a, **k: types.SimpleNamespace(stdout=out, stderr="", returncode=0)

    def _search(self, cands, title, dur):
        with mock.patch.object(m.subprocess, "run", self._run_returning(cands)):
            return m._search_video(title, dur)

    def test_sure_when_duration_and_title_match(self):
        cand, tag = self._search([{"id": VID_A, "title": "My Song (Official)", "duration": 200}], "My Song", 201.2)
        self.assertEqual((cand["id"], tag), (VID_A, "sure"))

    def test_title_only_without_local_duration(self):
        _, tag = self._search([{"id": VID_A, "title": "my song", "duration": 200}], "My Song", None)
        self.assertEqual(tag, "title")

    def test_check_when_duration_differs(self):
        cand, tag = self._search([{"id": VID_A, "title": "Autre chose", "duration": 50}], "My Song", 500)
        self.assertEqual((cand["id"], tag), (VID_A, "check"))

    def test_none_without_results_or_with_invalid_ids(self):
        self.assertEqual(self._search([], "x", None), (None, "none"))
        self.assertEqual(self._search([{"id": "pas-valide", "title": "t"}], "t", None), (None, "none"))


class JsonWriteTests(TempDirCase):
    def test_atomic_write_leaves_no_temp_file(self):
        path = os.path.join(self.d, "c.json")
        m._write_json_atomic(path, {"a": "é"})
        self.assertEqual(_json(path), {"a": "é"})
        self.assertEqual(os.listdir(self.d), ["c.json"])

    def test_concurrent_writes_stay_valid(self):
        path = os.path.join(self.d, "c.json")
        threads = [threading.Thread(target=m._write_json_atomic, args=(path, {"n": i})) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertIn("n", _json(path))
        self.assertEqual(os.listdir(self.d), ["c.json"])


class ConfigTests(TempDirCase):
    def test_roundtrip_and_corruption(self):
        m.save_config({"lang": "en", "x": 1})
        self.assertEqual(m.load_config(), {"lang": "en", "x": 1})
        with open(m.CONFIG_FILE, "w") as f:
            f.write("{cassé")
        self.assertEqual(m.load_config(), {})


class OutputTemplateTests(TempDirCase):
    def test_unique_output_path_escapes_percent(self):
        _touch(self.d, "100% Cotton.mp4")
        path = m.YtDlpGui._unique_output_path(self.d, "100% Cotton")
        self.assertEqual(os.path.basename(path), "100%% Cotton_2.%(ext)s")

    def test_no_conflict_returns_none(self):
        self.assertIsNone(m.YtDlpGui._unique_output_path(self.d, "Inexistant"))


class ProcessTreeTests(unittest.TestCase):
    def test_child_pids(self):
        import subprocess
        import time
        p = subprocess.Popen(["cmd", "/c", "ping -n 6 127.0.0.1 >nul"], **m.PROCESS_GROUP) if os.name == "nt" else \
            subprocess.Popen(["sh", "-c", "sleep 6; true"], **m.PROCESS_GROUP)   # sh reste le parent de sleep
        try:
            time.sleep(1.0)
            self.assertTrue(m._child_pids(p.pid))
            self.assertEqual(m._child_pids(99999999), [])
        finally:
            m.kill_process_tree(p)
            p.wait()


class VersionTests(unittest.TestCase):
    def test_version_is_semver_and_in_changelog(self):
        from tests._loader import ROOT
        self.assertRegex(m.__version__, r"^\d+\.\d+\.\d+$")
        changelog = _text(os.path.join(ROOT, "CHANGELOG.md"))
        self.assertIn(f"[{m.__version__}]", changelog)


if __name__ == "__main__":
    unittest.main()
