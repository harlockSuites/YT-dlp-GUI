"""Noms de langues en anglais d'abord (Linux), détection des polices manquantes et téléchargement vérifié de la police
du coréen, du japonais et du chinois."""
import hashlib
import json
import os
import re
import shutil
import tempfile
import threading
import time
import unittest
import urllib.error
from unittest import mock

from tests._loader import ROOT, load_gui, tk_available

m = load_gui()

ALL_CODES = ["fr", "en", "es", "pt", "it", "pl", "hu", "sr", "ru", "vi", "zh", "hi", "ja", "ko", "fil"]
EVERYTHING = "80-2ffff"   # une « police » qui contient tous les caractères
NOTHING = "20-7e"          # une « police » ASCII seulement


class FakeRun:
    """Remplace subprocess.run pour `fc-list` : renvoie le texte de charset donné."""

    def __init__(self, charset=EVERYTHING, returncode=0):
        self.charset, self.returncode, self.calls = charset, returncode, []

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        return mock.Mock(stdout=self.charset + "\n", returncode=self.returncode)


class FakeResponse:
    def __init__(self, data):
        self._data, self.headers = data, {"Content-Length": str(len(data))}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, n=-1):
        chunk, self._data = self._data[:n if n > 0 else None], self._data[n if n > 0 else len(self._data):]
        return chunk


def _opener(files, record=None):
    """Opener de test : `files` = {adresse: octets}."""
    def opener(url, timeout=30, headers=None):
        if record is not None:
            record.append(url)
        if url not in files:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return FakeResponse(files[url])
    return opener


class LabelTests(unittest.TestCase):
    def test_every_language_has_an_english_name(self):
        langs = sorted(n[:-5] for n in os.listdir(os.path.join(ROOT, "lang")) if n.endswith(".json"))
        self.assertEqual(sorted(m.LANGUAGE_ENGLISH_NAMES), sorted(langs))
        self.assertEqual(sorted(ALL_CODES), sorted(langs))

    def test_english_comes_first_then_the_native_name(self):
        self.assertEqual(m.language_label("ko", "한국어"), "Korean — 한국어")
        self.assertEqual(m.language_label("fr", "Français"), "French — Français")
        self.assertEqual(m.language_label("pt", "Português (Brasil)"), "Portuguese (Brazil) — Português (Brasil)")
        self.assertEqual(m.language_label("zh", "中文（简体）"), "Chinese (Simplified) — 中文（简体）")
        self.assertEqual(m.language_label("en", "English"), "English")
        self.assertEqual(m.language_label("fil", "Filipino"), "Filipino")
        self.assertEqual(m.language_label("xx", "Native"), "Native", "langue inconnue : nom natif seul")


class CharsetTests(unittest.TestCase):
    def test_ranges_are_merged_and_garbage_is_ignored(self):
        self.assertEqual(m.parse_fc_charsets("20-7e a0-ff 100 101-103 zz 3000\n20-30 7f"),
                         [(0x20, 0x7f), (0xa0, 0x103), (0x3000, 0x3000)])
        self.assertEqual(m.parse_fc_charsets(""), [])

    def test_coverage_looks_up_single_points_and_ranges(self):
        ranges = m.parse_fc_charsets("20-7e ac00-d7a3 2139")
        for cp in (0x20, 0x7e, 0xac00, 0xd55c, 0xd7a3, 0x2139):
            self.assertTrue(m._glyph_covered(ranges, cp), hex(cp))
        for cp in (0x1f, 0x7f, 0xabff, 0xd7a4, 0x213a, 0x10ffff):
            self.assertFalse(m._glyph_covered(ranges, cp), hex(cp))
        self.assertFalse(m._glyph_covered([], 0x20))


class MissingGlyphsTests(unittest.TestCase):
    def test_the_glyphs_of_a_language_come_from_its_translation_file(self):
        korean = m.language_glyphs("ko")
        self.assertIn("한", korean)
        self.assertGreater(len(korean), 300)
        self.assertNotIn("a", korean)
        self.assertEqual(m.language_glyphs("fr") & set("한日中"), set())
        self.assertEqual(m.language_glyphs("xx"), set())

    def test_nothing_is_missing_when_the_installed_fonts_cover_everything(self):
        self.assertEqual(m.missing_glyphs("ko", FakeRun(EVERYTHING))[0], 0)

    def test_everything_is_missing_with_an_ascii_only_system(self):
        missing, total = m.missing_glyphs("ko", FakeRun(NOTHING))
        self.assertEqual(missing, total)
        self.assertGreater(total, 300)

    def test_several_installed_fonts_complete_each_other(self):
        hangul = "ac00-d7a3 1100-11ff 3130-318f"
        missing, total = m.missing_glyphs("ko", FakeRun(f"20-7e\n{hangul}\n2139 25a0-25ff 2190-21ff 2600-26ff"))
        self.assertLess(missing, total * 0.01)

    def test_unknown_when_fontconfig_is_unavailable_or_fails(self):
        self.assertIsNone(m.missing_glyphs("ko", FakeRun(returncode=1)))
        self.assertIsNone(m.missing_glyphs("ko", FakeRun("")))
        self.assertIsNone(m.missing_glyphs("ko", mock.Mock(side_effect=FileNotFoundError)))
        self.assertIsNone(m.missing_glyphs("ko", mock.Mock(side_effect=m.subprocess.TimeoutExpired("fc-list", 30))))

    def test_the_font_is_needed_only_when_a_real_share_of_characters_has_no_font(self):
        with mock.patch.object(m, "IS_WINDOWS", False):
            self.assertTrue(m.language_needs_font("ko", FakeRun(NOTHING)))
            self.assertFalse(m.language_needs_font("ko", FakeRun(EVERYTHING)))
            self.assertFalse(m.language_needs_font("ko", FakeRun(returncode=1)), "fontconfig absent : on ne dérange pas")
            self.assertFalse(m.language_needs_font("fr", FakeRun(NOTHING)), "pas de police à proposer pour le français")
            self.assertFalse(m.language_needs_font("hi", FakeRun(NOTHING)))
            few = mock.Mock(side_effect=lambda *a, **k: mock.Mock(stdout="20-7e\n80-2ffff", returncode=0))
            self.assertFalse(m.language_needs_font("ja", few))
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertFalse(m.language_needs_font("ko", FakeRun(NOTHING)))

    def test_one_percent_threshold(self):
        total = len(m.language_glyphs("ko"))
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "missing_glyphs") as mg:
            mg.return_value = (int(total * 0.005), total)
            self.assertFalse(m.language_needs_font("ko"))
            mg.return_value = (int(total * 0.05), total)
            self.assertTrue(m.language_needs_font("ko"))
            mg.return_value = (0, 0)
            self.assertFalse(m.language_needs_font("ko"))


class PinnedFontsTests(unittest.TestCase):
    def test_only_the_three_east_asian_languages_have_a_pinned_font(self):
        self.assertEqual(sorted(m.FONT_PACKS), ["ja", "ko", "zh"])
        for code, pack in m.FONT_PACKS.items():
            with self.subTest(code=code):
                self.assertRegex(pack["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(pack["size"], 1_000_000)
                self.assertTrue(pack["path"].endswith(".otf"))
                self.assertTrue(pack["family"].startswith("Noto Sans"))
        self.assertRegex(m.FONT_LICENSE["sha256"], r"^[0-9a-f]{64}$")

    def test_the_download_address_is_pinned_to_one_commit_on_github(self):
        self.assertRegex(m.FONT_COMMIT, r"^[0-9a-f]{40}$")
        self.assertEqual(m.FONT_BASE_URL,
                         f"https://raw.githubusercontent.com/notofonts/noto-cjk/{m.FONT_COMMIT}/Sans/")
        self.assertTrue(m._is_github_url(m.FONT_BASE_URL))

    def test_fonts_go_to_the_users_own_font_folder(self):
        self.assertEqual(m.linux_fonts_dir({"XDG_DATA_HOME": os.path.abspath(os.sep + "data")}),
                         os.path.join(os.path.abspath(os.sep + "data"), "fonts", "yt-dlp-GUI"))


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env = {"XDG_DATA_HOME": self.tmp}
        self.font, self.licence = b"OTTO-fake-font" * 1000, b"licence text"
        sha = lambda b: hashlib.sha256(b).hexdigest()
        self.packs = {"ko": {"family": "Noto Sans KR", "path": "SubsetOTF/KR/NotoSansKR-Regular.otf",
                             "size": len(self.font), "sha256": sha(self.font)}}
        self.lic = {"path": "LICENSE", "name": "LICENSE-OFL.txt", "size": len(self.licence), "sha256": sha(self.licence)}
        for patcher in (mock.patch.dict(m.FONT_PACKS, self.packs, clear=True), mock.patch.object(m, "FONT_LICENSE", self.lic),
                        mock.patch.object(m, "_run_quiet", return_value="")):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.files = {m.FONT_BASE_URL + self.packs["ko"]["path"]: self.font, m.FONT_BASE_URL + "LICENSE": self.licence}
        self.folder = os.path.join(self.tmp, "fonts", "yt-dlp-GUI")

    def _install(self, files=None, run=None, **kw):
        record = []
        result = m.install_font_pack("ko", env=self.env, opener=_opener(self.files if files is None else files, record),
                                     run=run or FakeRun(EVERYTHING), **kw)
        return result, record

    def test_the_font_and_its_licence_are_downloaded_checked_and_registered(self):
        progress = []
        result, urls = self._install(progress=lambda done, total: progress.append((done, total)))
        self.assertTrue(result)
        with open(os.path.join(self.folder, "NotoSansKR-Regular.otf"), "rb") as f:
            self.assertEqual(f.read(), self.font)
        with open(os.path.join(self.folder, "LICENSE-OFL.txt"), "rb") as f:
            self.assertEqual(f.read(), self.licence)
        self.assertEqual(urls, list(self.files))
        self.assertEqual(progress[-1], (len(self.font), len(self.font)))
        self.assertFalse([n for n in os.listdir(self.folder) if n.endswith(".part")])
        m._run_quiet.assert_called_with(["fc-cache", "-f", self.folder])

    def test_a_font_already_installed_and_intact_is_not_downloaded_again(self):
        self._install()
        result, urls = self._install()
        self.assertEqual(urls, [])
        self.assertTrue(result)

    def test_a_damaged_file_is_downloaded_again(self):
        self._install()
        with open(os.path.join(self.folder, "NotoSansKR-Regular.otf"), "wb") as f:
            f.write(b"corrompu")
        _, urls = self._install()
        self.assertEqual(urls, [m.FONT_BASE_URL + self.packs["ko"]["path"]])

    def test_a_wrong_checksum_deletes_the_file_and_says_so(self):
        files = dict(self.files)
        files[m.FONT_BASE_URL + self.packs["ko"]["path"]] = b"autre contenu"
        with self.assertRaises(m.FontInstallError) as ctx:
            self._install(files)
        self.assertEqual(str(ctx.exception), m.FONT_DIALOG["err_checksum"])
        self.assertFalse(os.path.exists(os.path.join(self.folder, "NotoSansKR-Regular.otf")))
        m._run_quiet.assert_not_called()

    def test_a_network_failure_is_explained_in_english(self):
        with self.assertRaises(m.FontInstallError) as ctx:
            self._install({})
        self.assertIn("Download failed", str(ctx.exception))
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_no_connection_at_all(self):
        def opener(url, timeout=30, headers=None):
            raise urllib.error.URLError("Temporary failure in name resolution")
        with self.assertRaises(m.FontInstallError) as ctx:
            m.install_font_pack("ko", env=self.env, opener=opener, run=FakeRun())
        self.assertIn("Temporary failure in name resolution", str(ctx.exception))

    def test_a_full_disk_is_reported_as_a_write_error(self):
        with mock.patch.object(m, "_download_file", side_effect=OSError(28, "No space left on device", "x.part")):
            with self.assertRaises(m.FontInstallError) as ctx:
                self._install()
        self.assertIn("Could not write the font", str(ctx.exception))

    def test_cancelling_stops_the_download(self):
        stop = threading.Event()
        stop.set()
        with self.assertRaises(m.FontInstallError) as ctx:
            self._install(stop=stop)
        self.assertEqual(str(ctx.exception), m.FONT_DIALOG["cancelled"])
        self.assertFalse(os.path.exists(os.path.join(self.folder, "NotoSansKR-Regular.otf")))

    def test_the_result_tells_whether_the_system_now_sees_the_font(self):
        self.assertTrue(self._install(run=FakeRun(EVERYTHING))[0])
        self.assertFalse(self._install(run=FakeRun(NOTHING))[0])
        self.assertIsNone(self._install(run=FakeRun(returncode=1))[0])


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class DialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        for patcher in (mock.patch.object(m.tk.Toplevel, "grab_set"), mock.patch.object(m, "IS_WINDOWS", False)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _dialog(self, installer=None, manager="apt"):
        with mock.patch.object(m, "linux_package_manager", return_value=manager):
            dlg = m.LanguageFontDialog(self.app, "ko", "Korean — 한국어", installer=installer)
        dlg.withdraw()
        self.addCleanup(lambda: dlg.winfo_exists() and dlg.destroy())
        return dlg

    def _pump(self, until, timeout=5):
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)
        self.app.after(20, tick)
        self.app.mainloop()

    def _texts(self, widget):
        for child in widget.winfo_children():
            try:
                yield str(child.cget("text"))
            except Exception:
                pass
            yield from self._texts(child)

    def test_the_dialog_is_in_english_and_names_the_language_the_size_and_the_licence(self):
        text = "\n".join(self._texts(self._dialog()))
        self.assertIn("Korean — 한국어 needs a font", text)
        self.assertIn("4.6 MB", text)
        self.assertIn("SIL Open Font License", text)
        self.assertIn("no administrator rights are needed", text)
        for button in ("Download font", "Use anyway", "Cancel"):
            self.assertIn(button, text)

    def test_the_apt_command_is_offered_on_debian_and_a_generic_hint_elsewhere(self):
        dlg = self._dialog(manager="apt")
        self.assertEqual(dlg.var_command.get(), "sudo apt install fonts-noto-cjk")
        dlg._copy()
        self.assertEqual(dlg.clipboard_get(), "sudo apt install fonts-noto-cjk")
        other = "\n".join(self._texts(self._dialog(manager="dnf")))
        self.assertIn("Noto Sans CJK", other)
        self.assertNotIn("sudo", other)

    def test_a_successful_download_closes_the_dialog_with_the_installed_result(self):
        calls = []

        def installer(code, progress=None, stop=None):
            calls.append(code)
            progress(50, 100)
            return True
        dlg = self._dialog(installer)
        dlg._download()
        self._pump(lambda: not dlg.winfo_exists())
        self.assertEqual(calls, ["ko"])
        self.assertEqual(dlg.result, "installed")

    def test_a_failure_keeps_the_dialog_open_with_a_readable_message_and_lets_retry(self):
        def installer(code, progress=None, stop=None):
            raise m.FontInstallError("Download failed: HTTP 404")
        dlg = self._dialog(installer)
        dlg._download()
        self._pump(lambda: "HTTP 404" in str(dlg.lbl_status.cget("text")))
        self.assertIn("Download failed: HTTP 404", str(dlg.lbl_status.cget("text")))
        self.assertEqual(str(dlg.lbl_status.cget("fg")), m.WARN_TEXT)
        self.assertEqual(str(dlg.btn_download.cget("state")), "normal")
        self.assertEqual(str(dlg.btn_anyway.cget("state")), "normal")
        self.assertEqual(dlg.result, "cancel")

    def test_an_unexpected_error_never_freezes_the_dialog(self):
        def installer(code, progress=None, stop=None):
            raise RuntimeError("boum")
        dlg = self._dialog(installer)
        dlg._download()
        self._pump(lambda: "boum" in str(dlg.lbl_status.cget("text")))
        self.assertEqual(str(dlg.btn_download.cget("state")), "normal")

    def test_installed_but_not_listed_by_the_system_warns_and_waits_for_ok(self):
        dlg = self._dialog(lambda code, progress=None, stop=None: False)
        dlg._download()
        self._pump(lambda: dlg.result == "installed")
        self.assertIn("does not list it yet", str(dlg.lbl_status.cget("text")))
        self.assertTrue(dlg.winfo_exists())
        self.assertEqual(str(dlg.btn_download.cget("text")), "OK")

    def test_buttons_are_locked_during_the_download_and_cancel_asks_it_to_stop(self):
        release = threading.Event()
        seen = {}

        def installer(code, progress=None, stop=None):
            seen["stop"] = stop
            release.wait(5)
            raise m.FontInstallError(m.FONT_DIALOG["cancelled"])
        dlg = self._dialog(installer)
        dlg._download()
        self.assertEqual(str(dlg.btn_download.cget("state")), "disabled")
        self.assertEqual(str(dlg.btn_anyway.cget("state")), "disabled")
        dlg._download()   # un second clic ne relance rien
        dlg._cancel()
        self.assertTrue(dlg._stop.is_set())
        self.assertTrue(dlg.winfo_exists(), "le téléchargement s'arrête d'abord")
        release.set()
        self._pump(lambda: m.FONT_DIALOG["cancelled"] in str(dlg.lbl_status.cget("text")))
        self.assertEqual(str(dlg.btn_download.cget("state")), "normal")

    def test_use_anyway_and_cancel(self):
        dlg = self._dialog()
        dlg._anyway()
        self.assertEqual(dlg.result, "anyway")
        dlg2 = self._dialog()
        dlg2._cancel()
        self.assertEqual(dlg2.result, "cancel")
        self.assertFalse(dlg2.winfo_exists())


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class LanguageListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _radio_texts(self, windows):
        found = []
        with mock.patch.object(m.tk.Toplevel, "grab_set"), mock.patch.object(m.tk.Toplevel, "wait_window"), \
                mock.patch.object(m, "IS_WINDOWS", windows):
            self.app._open_lang_dialog()
        for top in self.app.winfo_children():
            if isinstance(top, m.tk.Toplevel):
                stack = list(top.winfo_children())
                while stack:
                    w = stack.pop()
                    stack.extend(w.winfo_children())
                    if w.winfo_class() == "Radiobutton":
                        found.append(str(w.cget("text")))
                top.destroy()
        return found

    def test_linux_lists_english_names_first(self):
        texts = self._radio_texts(windows=False)
        self.assertEqual(len(texts), 15)
        self.assertIn("Korean — 한국어", texts)
        self.assertIn("French — Français", texts)
        self.assertIn("English", texts)
        for text in texts:
            self.assertRegex(text, r"^[A-Za-z]")

    def test_windows_keeps_the_native_names_only(self):
        texts = self._radio_texts(windows=True)
        self.assertEqual(len(texts), 15)
        self.assertIn("한국어", texts)
        self.assertIn("Français", texts)
        self.assertNotIn("Korean — 한국어", texts)

    def _confirm_flow(self, code, needs, result):
        parent = mock.Mock()
        with mock.patch.object(m, "IS_WINDOWS", False), \
                mock.patch.object(m, "language_needs_font", return_value=needs) as check, \
                mock.patch.object(m, "LanguageFontDialog") as dialog_class:
            dialog_class.return_value.result = result
            ready = self.app._language_font_ready(code, "Label", parent)
        return ready, check, dialog_class, parent

    def test_a_language_that_needs_no_font_goes_straight_through(self):
        ready, check, dialog, parent = self._confirm_flow("ko", False, "cancel")
        self.assertTrue(ready)
        dialog.assert_not_called()
        self.assertEqual(parent.configure.call_args_list[-1], mock.call(cursor=""))

    def test_a_latin_language_is_never_checked(self):
        ready, check, dialog, _ = self._confirm_flow("fr", True, "cancel")
        self.assertTrue(ready)
        check.assert_not_called()
        dialog.assert_not_called()

    def test_a_missing_font_opens_the_dialog_and_follows_its_answer(self):
        for answer, expected in (("installed", True), ("anyway", True), ("cancel", False)):
            with self.subTest(answer=answer):
                ready, _, dialog, parent = self._confirm_flow("ko", True, answer)
                self.assertEqual(ready, expected)
                dialog.assert_called_once()
                parent.wait_window.assert_called_once()

    def test_windows_never_asks_for_a_font(self):
        with mock.patch.object(m, "IS_WINDOWS", True), mock.patch.object(m, "language_needs_font") as check:
            self.assertTrue(self.app._language_font_ready("ko", "Label", mock.Mock()))
        check.assert_not_called()

    def test_the_language_dialog_confirm_stays_open_when_the_user_cancels_the_font(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertRegex(source, r"if not self\._language_font_ready\(new_code, new_name, dlg\):\n\s+dlg\.grab_set\(\)"
                                 r".*\n\s+return")


if __name__ == "__main__":
    unittest.main()
