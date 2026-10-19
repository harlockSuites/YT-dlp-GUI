import hashlib
import http.server
import io
import os
import shutil
import tempfile
import threading
import time
import unittest
import zipfile
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


class _Handler(http.server.BaseHTTPRequestHandler):
    files = {}

    def do_GET(self):
        data = self.files.get(self.path)
        if data is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


class LocalServerCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _Handler.files = {}
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        _Handler.files = {}
        self.d = tempfile.mkdtemp(prefix="setup-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def serve(self, path, data):
        _Handler.files[path] = data
        return self.base + path


class ChecksumTests(unittest.TestCase):
    def test_parse_checksums_formats(self):
        h1, h2 = "a" * 64, "B" * 64
        out = m._parse_checksums(f"{h1}  yt-dlp.exe\n{h2} *autre.zip\nligne invalide\n{'c' * 10}  court")
        self.assertEqual(out, {"yt-dlp.exe": h1, "autre.zip": h2.lower()})

    def test_parse_checksums_powershell_list_format_published_by_deno(self):
        h = "A0C3101B4158D1DFB7D6A78A7BF0F3DE80C96BB423C152BEEC8BEB22786F2238"
        text = ("\nAlgorithm : SHA256\nHash      : " + h +
                "\nPath      : C:\\a\\deno\\deno\\target\\release\\deno-x86_64-pc-windows-msvc.zip\n\n")
        self.assertEqual(m._parse_checksums(text), {"deno-x86_64-pc-windows-msvc.zip": h.lower()})

    def test_sha256_file(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "f")
            with open(p, "wb") as f:
                f.write(b"abc")
            self.assertEqual(m._sha256_file(p), _sha(b"abc"))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class DownloadTests(LocalServerCase):
    def test_download_reports_progress_and_writes_file(self):
        data = os.urandom(300_000)
        url = self.serve("/f.bin", data)
        dest = os.path.join(self.d, "sub", "f.bin")
        calls = []
        m._download_file(url, dest, progress=lambda d, t: calls.append((d, t)))
        with open(dest, "rb") as f:
            self.assertEqual(f.read(), data)
        self.assertEqual(calls[-1], (len(data), len(data)))
        self.assertEqual(os.listdir(os.path.dirname(dest)), ["f.bin"], "pas de .part résiduel")

    def test_failure_leaves_nothing(self):
        dest = os.path.join(self.d, "x.bin")
        with self.assertRaises(Exception):
            m._download_file(self.base + "/inexistant", dest)
        self.assertEqual(os.listdir(self.d), [])

    def test_cancel(self):
        url = self.serve("/big.bin", os.urandom(400_000))
        stop = threading.Event()
        stop.set()
        dest = os.path.join(self.d, "big.bin")
        with self.assertRaises(m.SetupError):
            m._download_file(url, dest, stop=stop)
        self.assertEqual(os.listdir(self.d), [])

    def test_verified_download_ok_mismatch_and_missing_sum(self):
        data = b"contenu de test" * 1000
        url = self.serve("/tool.exe", data)
        good = self.serve("/sums-ok", f"{_sha(data)}  tool.exe\n".encode())
        bad = self.serve("/sums-bad", f"{'0' * 64}  tool.exe\n".encode())
        none = self.serve("/sums-none", f"{_sha(data)}  autre.exe\n".encode())
        dest = os.path.join(self.d, "tool.exe")

        m._verified_download(url, good, "tool.exe", dest)
        self.assertTrue(os.path.isfile(dest))
        os.remove(dest)

        with self.assertRaises(m.SetupError):
            m._verified_download(url, bad, "tool.exe", dest)
        self.assertFalse(os.path.exists(dest), "fichier non vérifié supprimé")

        with self.assertRaises(m.SetupError):
            m._verified_download(url, none, "tool.exe", dest)
        self.assertFalse(os.path.exists(dest))


def _zip_bytes(entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="zip-")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def _zip(self, entries):
        path = os.path.join(self.d, "a.zip")
        with open(path, "wb") as f:
            f.write(_zip_bytes(entries))
        return path

    def test_extracts_only_ffmpeg_and_ffprobe_by_basename(self):
        z = self._zip({"ffmpeg-x/bin/ffmpeg.exe": b"F", "ffmpeg-x/bin/ffprobe.exe": b"P",
                       "ffmpeg-x/bin/ffplay.exe": b"L", "../evil.exe": b"E",
                       "doc/readme.txt": b"R"})
        dest = os.path.join(self.d, "bin")
        done = m._extract_tools(z, dest)
        self.assertEqual(sorted(done), ["ffmpeg.exe", "ffprobe.exe"])
        self.assertEqual(sorted(os.listdir(dest)), ["ffmpeg.exe", "ffprobe.exe"])
        self.assertFalse(os.path.exists(os.path.join(self.d, "evil.exe")))
        with open(os.path.join(dest, "ffmpeg.exe"), "rb") as f:
            self.assertEqual(f.read(), b"F")

    def test_archive_without_tools_raises(self):
        with self.assertRaises(m.SetupError):
            m._extract_tools(self._zip({"x/readme.txt": b"R"}), os.path.join(self.d, "bin"))


class InstallTests(LocalServerCase):
    def test_install_ytdlp_replaces_and_backs_up(self):
        data = b"NOUVEAU" * 2000
        target = os.path.join(self.d, "yt-dlp.exe")
        with open(target, "wb") as f:
            f.write(b"ANCIEN")
        url = self.serve("/yt-dlp.exe", data)
        sums = self.serve("/SHA2-256SUMS", f"{_sha(data)}  yt-dlp.exe\n".encode())
        with mock.patch.object(m, "YTDLP", target), mock.patch.object(m, "YTDLP_URL", url), \
                mock.patch.object(m, "YTDLP_SUMS_URL", sums):
            m.install_ytdlp()
        with open(target, "rb") as f:
            self.assertEqual(f.read(), data)
        with open(target + ".bak", "rb") as f:
            self.assertEqual(f.read(), b"ANCIEN")
        self.assertFalse(os.path.exists(target + ".new"))

    def test_install_ytdlp_bad_checksum_keeps_old_file(self):
        target = os.path.join(self.d, "yt-dlp.exe")
        with open(target, "wb") as f:
            f.write(b"ANCIEN")
        url = self.serve("/yt-dlp.exe", b"corrompu")
        sums = self.serve("/SHA2-256SUMS", f"{'1' * 64}  yt-dlp.exe\n".encode())
        with mock.patch.object(m, "YTDLP", target), mock.patch.object(m, "YTDLP_URL", url), \
                mock.patch.object(m, "YTDLP_SUMS_URL", sums):
            with self.assertRaises(m.SetupError):
                m.install_ytdlp()
        with open(target, "rb") as f:
            self.assertEqual(f.read(), b"ANCIEN")
        self.assertEqual(os.listdir(self.d), ["yt-dlp.exe"])

    def test_install_ffmpeg_extracts_to_local_bin(self):
        archive = _zip_bytes({"b/bin/ffmpeg.exe": b"F", "b/bin/ffprobe.exe": b"P"})
        url = self.serve("/" + m.FFMPEG_ZIP_NAME, archive)
        sums = self.serve("/checksums.sha256", f"{_sha(archive)}  {m.FFMPEG_ZIP_NAME}\n".encode())
        bin_dir = os.path.join(self.d, "bin")
        with mock.patch.object(m, "LOCAL_BIN", bin_dir), mock.patch.object(m, "FFMPEG_URL", url), \
                mock.patch.object(m, "FFMPEG_SUMS_URL", sums):
            m.install_ffmpeg()
        self.assertEqual(sorted(os.listdir(bin_dir)), ["ffmpeg.exe", "ffprobe.exe"])

    def test_install_deno_extracts_to_local_bin_without_chocolatey(self):
        archive = _zip_bytes({"deno.exe": b"D", "LICENSE.md": b"L"})
        url = self.serve("/" + m.DENO_ZIP_NAME, archive)
        h = _sha(archive).upper()
        sums = self.serve("/" + m.DENO_ZIP_NAME + ".sha256sum",
                          f"Algorithm : SHA256\nHash      : {h}\nPath      : C:\\build\\{m.DENO_ZIP_NAME}\n".encode())
        bin_dir = os.path.join(self.d, "bin")
        with mock.patch.object(m, "LOCAL_BIN", bin_dir), mock.patch.object(m, "DENO_URL", url), \
                mock.patch.object(m, "DENO_SUMS_URL", sums):
            m.install_deno()
        self.assertEqual(os.listdir(bin_dir), ["deno.exe"])

    def test_install_deno_refuses_a_wrong_checksum(self):
        archive = _zip_bytes({"deno.exe": b"D"})
        url = self.serve("/" + m.DENO_ZIP_NAME, archive)
        sums = self.serve("/" + m.DENO_ZIP_NAME + ".sha256sum",
                          f"Hash : {'1' * 64}\nPath : {m.DENO_ZIP_NAME}\n".encode())
        bin_dir = os.path.join(self.d, "bin")
        with mock.patch.object(m, "LOCAL_BIN", bin_dir), mock.patch.object(m, "DENO_URL", url), \
                mock.patch.object(m, "DENO_SUMS_URL", sums):
            with self.assertRaises(m.SetupError):
                m.install_deno()
        self.assertFalse(os.path.exists(os.path.join(bin_dir, "deno.exe")))

    def test_deno_urls_are_official_github(self):
        for url in (m.DENO_URL, m.DENO_SUMS_URL):
            self.assertTrue(url.startswith("https://github.com/denoland/deno/releases/"), url)

    def test_official_urls_are_https_github(self):
        for url in (m.YTDLP_URL, m.YTDLP_SUMS_URL, m.FFMPEG_URL, m.FFMPEG_SUMS_URL):
            self.assertTrue(url.startswith("https://github.com/yt-dlp/"), url)

    def test_local_bin_is_on_path(self):
        self.assertIn(m.LOCAL_BIN, os.environ["PATH"].split(os.pathsep))


class ElevationTests(unittest.TestCase):
    def _fake_windll(self, result):
        fake = mock.Mock()
        fake.shell32.ShellExecuteW.return_value = result
        return fake

    def test_uses_shell_execute_runas_without_hidden_powershell(self):
        import ctypes
        fake = self._fake_windll(42)
        with mock.patch.object(ctypes, "windll", fake, create=True):
            self.assertTrue(m.run_elevated("choco install deno -y & pause"))
        args = fake.shell32.ShellExecuteW.call_args[0]
        self.assertEqual(args[1:4], ("runas", "cmd.exe", "/c choco install deno -y & pause"))
        self.assertEqual(args[5], 1, "fenêtre visible")

    def test_returns_false_when_elevation_is_refused(self):
        import ctypes
        with mock.patch.object(ctypes, "windll", self._fake_windll(5), create=True):
            self.assertFalse(m.run_elevated("choco install deno -y"))

    def test_no_hidden_window_and_no_policy_bypass_anywhere(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        for suspicious in ("-ExecutionPolicy", "-WindowStyle", "Start-Process powershell"):
            self.assertNotIn(suspicious, source, "montage que les antivirus de comportement bloquent")


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class DepsWindowWithoutChocolateyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _window(self):
        with mock.patch.object(m, "choco_available", return_value=False),                 mock.patch.object(m, "dep_installed", return_value=False),                 mock.patch.object(m.tk.Toplevel, "grab_set", lambda self: None):
            win = m.DepsWindow(self.app)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def test_install_all_does_nothing_and_explains(self):
        win = self._window()
        with mock.patch.object(m, "choco_available", return_value=False),                 mock.patch.object(m, "run_elevated") as elevated:
            win._install_all()
        elevated.assert_not_called()
        self.assertIn("Chocolatey", win.log.get("1.0", "end"))

    def test_deno_can_still_be_installed_by_the_assistant(self):
        win = self._window()
        row = next(r for r in win._rows if r["dep"]["name"] == "deno")
        self.assertEqual(str(row["btn"].cget("state")), "normal")
        self.assertEqual(row["btn"].cget("text"), m.t("deps.btn_install"))

    def test_cancelled_elevation_is_reported(self):
        win = self._window()
        with mock.patch.object(m, "choco_available", return_value=True),                 mock.patch.object(m, "run_elevated", return_value=False):
            win._choco_install(["aria2"])
        self.assertIn(m.t("deps.log_elevation_cancelled"), win.log.get("1.0", "end"))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WizardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _run_in_mainloop(self, action, until, timeout=5):
        """Lance `action` puis fait tourner la vraie boucle Tk jusqu'à `until()` (les rappels
        envoyés par les fils de travail ne passent que lorsque mainloop tourne)."""
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)

        self.app.after(10, action)
        self.app.after(30, tick)
        self.app.mainloop()

    def _wizard(self, **kw):
        win = m.SetupWizardWindow(self.app, **kw)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def test_missing_ytdlp_is_preselected(self):
        with mock.patch.object(m, "YTDLP", os.path.join(tempfile.gettempdir(), "absent-yt-dlp.exe")):
            win = self._wizard()
        self.assertTrue(win._items["ytdlp"].get())

    def test_installed_tools_are_not_preselected(self):
        with mock.patch.object(m.os.path, "isfile", return_value=True), \
                mock.patch.object(m, "dep_installed", return_value=True):
            win = self._wizard()
        self.assertFalse(win._items["ytdlp"].get())
        self.assertFalse(win._items["ffmpeg"].get())

    def test_install_runs_selected_tools_and_calls_back(self):
        done = []
        with mock.patch.object(m.os.path, "isfile", return_value=False), \
                mock.patch.object(m, "dep_installed", return_value=False):
            win = self._wizard(on_done=lambda: done.append(True))
        with mock.patch.object(m, "install_ytdlp") as y, mock.patch.object(m, "install_ffmpeg") as f, \
                mock.patch.object(m, "install_deno") as d:
            self._run_in_mainloop(win._install, lambda: bool(done))
        y.assert_called_once()
        f.assert_called_once()
        d.assert_called_once()
        self.assertEqual(done, [True])

    def test_deno_is_offered_by_the_assistant_and_preselected_when_missing(self):
        with mock.patch.object(m.os.path, "isfile", return_value=True), \
                mock.patch.object(m, "dep_installed", side_effect=lambda exe: exe != "deno"):
            win = self._wizard()
        self.assertTrue(win._items["deno"].get())
        self.assertFalse(win._items["ytdlp"].get())

    def test_failure_is_logged_and_stops(self):
        with mock.patch.object(m.os.path, "isfile", return_value=False), \
                mock.patch.object(m, "dep_installed", return_value=False):
            win = self._wizard()
        with mock.patch.object(m, "install_ytdlp", side_effect=m.SetupError("boum")), \
                mock.patch.object(m, "install_ffmpeg") as f:
            self._run_in_mainloop(win._install, lambda: win._busy is False and "boum" in win.txt.get("1.0", "end"))
        f.assert_not_called()
        self.assertIn("boum", win.txt.get("1.0", "end"))

    def test_first_run_opens_wizard_only_when_ytdlp_missing(self):
        with mock.patch.object(m, "SetupWizardWindow") as wiz:
            with mock.patch.object(m, "YTDLP", os.path.join(tempfile.gettempdir(), "absent.exe")):
                self.app._maybe_first_run()
            wiz.assert_called_once()
        with mock.patch.object(m, "SetupWizardWindow") as wiz, \
                mock.patch.object(m.os.path, "isfile", return_value=True):
            self.app._maybe_first_run()
            wiz.assert_not_called()


if __name__ == "__main__":
    unittest.main()
