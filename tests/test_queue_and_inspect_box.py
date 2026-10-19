import json
import time
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

INFO = {"title": "THE AMAZING DIGITAL CIRCUS: PILOT", "duration_string": "24:03", "uploader": "GLITCH",
        "formats": [{"language": "fr-FR", "acodec": "opus"}, {"language": "en-US", "acodec": "opus"}],
        "subtitles": {"fr": [{}], "en": [{}]}, "automatic_captions": {}}


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class AppCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        m.save_config({})
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()
        m.save_config({})

    def _pump(self, until, timeout=5):
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)
        self.app.after(20, tick)
        self.app.mainloop()


class RetryErrorsTests(AppCase):
    def setUp(self):
        self.app._queue = [
            {"url": "https://a", "args": ["x"], "status": "error"},
            {"url": "https://b", "args": ["x"], "status": "done"},
            {"url": "https://c", "args": ["x"], "status": "error"},
        ]
        self.app._queue_running = False

    def test_errors_go_back_to_pending_and_the_queue_starts(self):
        with mock.patch.object(m, "save_queue"), mock.patch.object(self.app, "_refresh_queue_tv"), \
                mock.patch.object(self.app, "_queue_run") as run:
            self.app._queue_retry_errors()
        self.assertEqual([e["status"] for e in self.app._queue], ["pending", "done", "pending"])
        run.assert_called_once_with(0)

    def test_nothing_to_retry_tells_the_user(self):
        for e in self.app._queue:
            e["status"] = "done"
        with mock.patch.object(m.messagebox, "showinfo") as info, mock.patch.object(self.app, "_queue_run") as run:
            self.app._queue_retry_errors()
        info.assert_called_once()
        run.assert_not_called()

    def test_ignored_while_the_queue_is_running(self):
        self.app._queue_running = True
        with mock.patch.object(self.app, "_queue_run") as run:
            self.app._queue_retry_errors()
        run.assert_not_called()
        self.assertEqual(self.app._queue[0]["status"], "error")


class InspectBoxTests(AppCase):
    def tearDown(self):
        self.app.var_url.set("")

    def _fake_run(self, rc, stdout="", stderr=""):
        return mock.patch.object(m.subprocess, "run", return_value=types.SimpleNamespace(
            returncode=rc, stdout=stdout, stderr=stderr))

    def test_result_is_shown_under_the_url_field(self):
        self.app.var_url.set("https://www.youtube.com/watch?v=abc")
        with self._fake_run(0, json.dumps(INFO)), mock.patch.object(m.subprocess, "Popen") as popen:
            popen.return_value.stdout = iter([])
            self.app._inspect()
            self._pump(lambda: "THE AMAZING" in self.app._lbl_inspect.cget("text"))
        text = self.app._lbl_inspect.cget("text")
        self.assertIn("THE AMAZING DIGITAL CIRCUS: PILOT (24:03) — GLITCH", text)
        self.assertIn("FR", text)
        self.assertTrue(self.app._lbl_inspect.winfo_manager())

    def test_failure_is_shown_too(self):
        self.app.var_url.set("https://www.youtube.com/watch?v=abc")
        with self._fake_run(1, "", "ERROR: Video unavailable"):
            self.app._inspect()
            self._pump(lambda: self.app._lbl_inspect.cget("text") == m.t("inspect.box_failed"))
        self.assertEqual(self.app._lbl_inspect.cget("text"), m.t("inspect.box_failed"))

    def test_box_is_hidden_when_the_url_changes(self):
        self.app._show_inspect_box("x", "#27ae60", "https://u1")
        self.app.var_url.set("https://u1")
        self.assertTrue(self.app._lbl_inspect.winfo_manager())
        self.app.var_url.set("https://u2")
        self.assertFalse(self.app._lbl_inspect.winfo_manager())


if __name__ == "__main__":
    unittest.main()
