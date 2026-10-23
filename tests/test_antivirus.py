import os
import shutil
import tempfile
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _winerror(code, cls=OSError, errno=0, message="message"):
    exc = cls(errno, message, None, code)   # sous Windows, le 4e argument devient .winerror
    if getattr(exc, "winerror", None) != code:   # ailleurs il devient filename2 : on pose l'attribut à la main
        exc.winerror = code
    return exc


class BlockDetectionTests(unittest.TestCase):
    def setUp(self):
        m.load_lang("fr")

    def test_virus_errors_are_recognised(self):
        for code in (225, 226):
            self.assertTrue(m.is_antivirus_block(_winerror(code)), code)

    def test_other_errors_are_not(self):
        for exc in (_winerror(32), _winerror(2), ValueError("x"), None):
            self.assertFalse(m.is_antivirus_block(exc))
            self.assertEqual(m.av_advice(exc), "")

    def test_advice_names_the_data_folder_and_is_translated(self):
        text = m.av_advice(_winerror(225))
        self.assertIn(m.DATA_DIR, text)
        self.assertIn("antivirus", text.lower())
        m.load_lang("en")
        try:
            self.assertIn("antivirus", m.av_advice(_winerror(225)).lower())
        finally:
            m.load_lang("fr")


class ReplaceWithRetryTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.src, self.dst = os.path.join(self.d, "a.new"), os.path.join(self.d, "a")
        with open(self.src, "w") as f:
            f.write("nouveau")

    def test_succeeds_after_the_antivirus_releases_the_file(self):
        real = os.replace
        calls = []

        def flaky(a, b):
            calls.append(1)
            if len(calls) < 3:
                raise _winerror(32, PermissionError, 13, "utilisé par un autre processus")
            real(a, b)

        with mock.patch.object(m.os, "replace", flaky), mock.patch.object(m.time, "sleep") as sleep:
            m._replace_with_retry(self.src, self.dst)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleep.call_count, 2)
        with open(self.dst) as f:
            self.assertEqual(f.read(), "nouveau")

    def test_gives_up_after_the_last_attempt(self):
        def always(a, b):
            raise _winerror(32, PermissionError, 13, "utilisé")

        with mock.patch.object(m.os, "replace", always), mock.patch.object(m.time, "sleep"):
            with self.assertRaises(PermissionError):
                m._replace_with_retry(self.src, self.dst, attempts=3)

    def test_other_errors_are_not_retried(self):
        calls = []

        def broken(a, b):
            calls.append(1)
            raise _winerror(3, message="autre")

        with mock.patch.object(m.os, "replace", broken), mock.patch.object(m.time, "sleep") as sleep:
            with self.assertRaises(OSError):
                m._replace_with_retry(self.src, self.dst)
        self.assertEqual(len(calls), 1)
        sleep.assert_not_called()

    def test_downloads_and_installs_use_the_retry(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        for needle in ("_replace_with_retry(tmp, dest)", "_replace_with_retry(tmp, YTDLP)",
                       '_replace_with_retry(target + ".new", target)'):
            self.assertIn(needle, source)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class GlobalHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_antivirus_block_shows_advice_not_a_bug_report_prompt(self):
        exc = _winerror(225)
        with mock.patch.object(m.messagebox, "showwarning") as warn, \
                mock.patch.object(m.messagebox, "askyesno") as ask:
            self.app._on_tk_error(OSError, exc, None)
        warn.assert_called_once()
        self.assertIn(m.DATA_DIR, warn.call_args[0][1])
        ask.assert_not_called()

    def test_other_errors_still_offer_a_bug_report(self):
        with mock.patch.object(m.messagebox, "askyesno", return_value=False) as ask, \
                mock.patch.object(m.messagebox, "showwarning") as warn:
            self.app._on_tk_error(ValueError, ValueError("boum"), None)
        ask.assert_called_once()
        warn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
