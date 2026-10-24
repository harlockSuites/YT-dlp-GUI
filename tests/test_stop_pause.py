import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()
RUNNING = types.SimpleNamespace(pid=4242, poll=lambda: None)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class StopQuestionPausesTests(unittest.TestCase):
    """Pendant la question d'arrêt d'une playlist, le téléchargement est en pause."""

    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app._process = RUNNING
        self.app._paused = False
        self.app._queue_running = False
        self.app._current_dl_files = ["C:/Dl/Deux.f133.mp4"]
        self.app._finished_items_files = ["C:/Dl/Un.f133.mp4", "C:/Dl/Un.mp4"]
        self.events = []
        for name in ("_suspend_process", "_resume_process"):
            patcher = mock.patch.object(self.app, name, side_effect=lambda pid, n=name: self.events.append(n))
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(setattr, self.app, "_process", None)

    def _ask(self, answer):
        def question(*_args, **_kwargs):
            self.events.append("question")
            return answer
        return mock.patch.object(m.messagebox, "askyesnocancel", side_effect=question)

    def test_pause_before_the_question_and_resume_when_cancelled(self):
        with self._ask(None):
            self.assertFalse(self.app._confirm_stop_scope())
        self.assertEqual(self.events, ["_suspend_process", "question", "_resume_process"])

    def test_yes_or_no_leaves_the_download_paused_until_it_is_killed(self):
        for answer in (True, False):
            with self.subTest(answer=answer):
                self.events.clear()
                self.app._finished_items_files = ["C:/Dl/Un.mp4"]
                with self._ask(answer):
                    self.assertTrue(self.app._confirm_stop_scope())
                self.assertEqual(self.events, ["_suspend_process", "question"])

    def test_already_paused_download_is_left_alone(self):
        self.app._paused = True
        with self._ask(None):
            self.assertFalse(self.app._confirm_stop_scope())
        self.assertEqual(self.events, ["question"])

    def test_a_failing_dialog_resumes_the_download(self):
        with mock.patch.object(m.messagebox, "askyesnocancel", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self.app._confirm_stop_scope()
        self.assertEqual(self.events, ["_suspend_process", "_resume_process"])

    def test_the_lists_are_read_after_the_answer(self):
        def late_item(*_args, **_kwargs):
            self.app._finished_items_files.append("C:/Dl/Trois.mp4")      # apparu pendant la question
            return True
        with mock.patch.object(m.messagebox, "askyesnocancel", side_effect=late_item):
            self.assertTrue(self.app._confirm_stop_scope())
        self.assertIn("C:/Dl/Trois.mp4", self.app._current_dl_files)

    def test_no_pause_when_there_is_nothing_to_ask(self):
        self.app._finished_items_files = []
        with self._ask(True) as question:
            self.assertTrue(self.app._confirm_stop_scope())
        question.assert_not_called()
        self.assertEqual(self.events, [])


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class DependencyBannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def _banner(self, installed):
        with mock.patch.object(m, "dep_installed", side_effect=lambda exe: exe in installed):
            self.app._check_deps_quick()
        return self.app.var_dep_warn.get(), str(self.app._lbl_dep_warn.cget("foreground"))

    def test_only_optional_tools_missing_is_a_quiet_information(self):
        text, color = self._banner(("ffmpeg", "ffprobe", "deno"))
        self.assertIn("AtomicParsley", text)
        self.assertIn("fonctionne sans", text)
        self.assertNotIn("⚠", text)
        self.assertEqual(color, "#7f8c8d")

    def test_a_missing_required_tool_is_still_a_warning_and_lists_only_required_tools(self):
        text, color = self._banner(("deno",))
        self.assertIn("⚠", text)
        self.assertIn("ffmpeg", text)
        self.assertNotIn("AtomicParsley", text, "les outils facultatifs ne sont plus listés comme manquants")
        self.assertEqual(color, m.WARN_TEXT)

    def test_everything_installed_is_green(self):
        every = {d["exe"] for d in m.DEPS}
        text, color = self._banner(every)
        self.assertEqual(text, m.t("app.dep_ok"))
        self.assertEqual(color, "#27ae60")


if __name__ == "__main__":
    unittest.main()
