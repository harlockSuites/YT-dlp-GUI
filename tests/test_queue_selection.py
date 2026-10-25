import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def entry(i, status="pending"):
    return {"url": f"https://example.com/v{i}", "args": ["-o", r"C:\dl\%(title)s.%(ext)s", f"https://example.com/v{i}"],
            "summary": "1080p", "status": status, "title": f"Titre {i}"}


class RowsBetweenTests(unittest.TestCase):
    def test_range_is_ordered_and_inclusive_in_both_directions(self):
        rows = ["0", "1", "2", "3", "4"]
        self.assertEqual(m.rows_between(rows, "1", "3"), ["1", "2", "3"])
        self.assertEqual(m.rows_between(rows, "3", "1"), ["1", "2", "3"])
        self.assertEqual(m.rows_between(rows, "2", "2"), ["2"])


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class QueueSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        a = self.app
        a._process = None
        a._queue_running = False
        a._queue_targets = None
        a._queue_report = []
        a._queue_sel_origin = "manual"
        a._queue = [entry(i) for i in range(6)]
        a._refresh_queue_tv()
        self.started = []
        for name, patcher in (("_start_download", mock.patch.object(a, "_start_download",
                                                                    side_effect=lambda args: self.started.append(args[-1]))),
                              ("_unique_output_path", mock.patch.object(a, "_unique_output_path", return_value=None)),
                              ("save", mock.patch.object(m, "save_queue"))):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.info = mock.patch.object(m.messagebox, "showinfo").start()
        self.warn = mock.patch.object(m.messagebox, "showwarning").start()
        self.ask = mock.patch.object(m.messagebox, "askyesno", return_value=True).start()
        self.addCleanup(mock.patch.stopall)

    def _select(self, *rows):
        self.app._tv_queue.selection_set([str(r) for r in rows])
        self.app.update()

    def _finish_current(self, success=True):
        self.app._on_done(success)

    # ── sélection ───────────────────────────────────────────────────
    def test_table_accepts_several_rows(self):
        self.assertEqual(str(self.app._tv_queue.cget("selectmode")), "extended")
        self._select(0, 2, 5)
        self.assertEqual(self.app._queue_selected_indices(), [0, 2, 5])

    def test_selection_survives_a_refresh_even_when_positions_change(self):
        chosen = [self.app._queue[1], self.app._queue[3]]
        self._select(1, 3)
        del self.app._queue[0]                       # les positions reculent d'un cran
        self.app._refresh_queue_tv()
        self.assertEqual([self.app._queue[i] for i in self.app._queue_selected_indices()], chosen)

    def test_select_all(self):
        self.app._queue_select_all()
        self.app.update()
        self.assertEqual(self.app._queue_selected_indices(), list(range(6)))

    def test_range_spinboxes_select_the_rows(self):
        self.app._spin_from.set("2")
        self.app._spin_to.set("4")
        self.app._queue_select_range()
        self.assertEqual(self.app._queue_selected_indices(), [1, 2, 3])
        self.assertEqual(self.app._queue_sel_origin, "range")

    def test_range_outside_the_queue_is_ignored(self):
        self._select(0)
        self.app._spin_from.set("9")
        self.app._spin_to.set("12")
        self.app._queue_select_range()
        self.assertEqual(self.app._queue_selected_indices(), [0])

    # ── bouton « Télécharger sél. » ─────────────────────────────────
    def test_button_becomes_download_selection_for_a_manual_multiple_selection(self):
        self.assertEqual(self.app.btn_q_range.cget("text"), m.t("queue.btn_run_range"))
        self._select(0, 1, 4)
        self.assertEqual(self.app.btn_q_range.cget("text"), m.t("queue.btn_run_selection", n=3))
        self._select(1)
        self.assertEqual(self.app.btn_q_range.cget("text"), m.t("queue.btn_run_range"))

    def test_button_keeps_the_range_label_when_the_rows_come_from_the_range(self):
        self.app._spin_from.set("1")
        self.app._spin_to.set("3")
        self.app._queue_select_range()
        self.app.update()
        self.assertEqual(self.app.btn_q_range.cget("text"), m.t("queue.btn_run_range"))

    # ── lancement de la sélection ───────────────────────────────────
    def test_only_the_selected_videos_are_downloaded_in_queue_order(self):
        self._select(4, 1)
        self.app._queue_run_selection()
        self.assertEqual(self.started, ["https://example.com/v1"])
        self._finish_current(True)
        self.assertEqual(self.started, ["https://example.com/v1", "https://example.com/v4"])
        self._finish_current(True)
        self.assertFalse(self.app._queue_running)
        self.assertEqual([e["title"] for e in self.app._queue], ["Titre 0", "Titre 2", "Titre 3", "Titre 5"])

    def test_a_selected_video_in_error_is_retried(self):
        self.app._queue[2]["status"] = "error"
        self._select(2, 3)
        self.app._queue_run_selection()
        self.assertEqual(self.started, ["https://example.com/v2"])

    def test_a_removed_target_is_skipped_and_the_others_still_run(self):
        self._select(1, 2, 3)
        self.app._queue_run_selection()
        victim = self.app._queue[3]
        self.app._queue.remove(victim)               # retirée pendant que la 1re se télécharge
        self._finish_current(True)
        self.assertEqual(self.started, ["https://example.com/v1", "https://example.com/v2"])

    def test_failure_does_not_stop_the_selection(self):
        self._select(0, 5)
        self.app._queue_run_selection()
        self._finish_current(False)
        self.assertEqual(self.started, ["https://example.com/v0", "https://example.com/v5"])
        self.assertEqual(self.app._queue[0]["status"], "error")

    def test_stop_forgets_the_remaining_targets(self):
        self._select(0, 1)
        self.app._queue_run_selection()
        with mock.patch.object(self.app, "_confirm_stop_scope", return_value=True), \
                mock.patch.object(self.app, "_kill_current_process", return_value=False):
            self.app._queue_stop()
        self.assertIsNone(self.app._queue_targets)
        self.assertFalse(self.app._queue_running)

    # ── suppression ─────────────────────────────────────────────────
    def test_several_rows_are_removed_after_a_confirmation(self):
        self._select(0, 2, 4)
        self.app._queue_remove_selected()
        self.ask.assert_called_once()
        self.assertEqual([e["title"] for e in self.app._queue], ["Titre 1", "Titre 3", "Titre 5"])

    def test_declining_the_confirmation_removes_nothing(self):
        self.ask.return_value = False
        self._select(0, 1)
        self.app._queue_remove_selected()
        self.assertEqual(len(self.app._queue), 6)

    def test_one_row_is_removed_without_a_question(self):
        self._select(3)
        self.app._queue_remove_selected()
        self.ask.assert_not_called()
        self.assertEqual(len(self.app._queue), 5)

    def test_the_video_being_downloaded_is_never_removed_and_the_run_keeps_its_place(self):
        self.app._queue_run(1, 4)
        self.assertEqual(self.started, ["https://example.com/v1"])
        self.app._queue_remove_indices([0, 1, 3])      # 1 se télécharge : seules 0 et 3 partent
        self.assertEqual([e["title"] for e in self.app._queue], ["Titre 1", "Titre 2", "Titre 4", "Titre 5"])
        self.assertEqual(self.app._queue_index, 0)
        self.assertEqual(self.app._queue_end_index, 2)
        self._finish_current(True)
        self.assertEqual(self.started[-1], "https://example.com/v2")

    # ── un seul téléchargeur ────────────────────────────────────────
    def test_a_second_download_is_refused_while_one_runs(self):
        self.app._process = mock.Mock()
        self.addCleanup(setattr, self.app, "_process", None)
        self.app.var_url.set("https://example.com/watch?v=abc")
        self.app._download()
        self.app._queue_run(0)
        self._select(1, 2)
        self.app._queue_run_selection()
        self.assertEqual(self.started, [])
        self.assertEqual(self.info.call_count, 3)

    def test_the_queue_cannot_be_started_twice(self):
        self.app._queue_run(0)
        self.app._queue_run(2)
        self.assertEqual(self.started, ["https://example.com/v0"])
        self.assertEqual(self.info.call_count, 1)

    # ── bilan ───────────────────────────────────────────────────────
    def test_a_report_is_shown_after_several_videos(self):
        self.app._queue_run(0, 2)
        shown = []
        with mock.patch.object(m, "DownloadReportWindow", side_effect=lambda parent, rows: shown.append(rows)), \
                mock.patch.object(self.app, "after", side_effect=lambda ms, fn=None, *a: fn(*a) if fn else None):
            self._finish_current(True)
            self._finish_current(False)
            self._finish_current(True)
        self.assertEqual([r["status"] for r in shown[0]], ["ok", "erreur", "ok"])

    def test_no_report_for_a_single_video(self):
        self.app._queue_run(0, 0)
        with mock.patch.object(m, "DownloadReportWindow") as report, \
                mock.patch.object(self.app, "after", side_effect=lambda ms, fn=None, *a: fn(*a) if fn else None):
            self._finish_current(True)
        report.assert_not_called()


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class ExpandedViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app._process = None
        self.app._queue_running = False
        self.app._queue = [entry(i) for i in range(4)]
        self.app._refresh_queue_tv()
        mock.patch.object(m, "save_queue").start()
        self.addCleanup(mock.patch.stopall)
        self.view = m.QueueExpandedWindow(self.app)
        self.view.withdraw()
        self.addCleanup(lambda: self.view.winfo_exists() and self.view.destroy())

    def test_it_shows_the_same_queue_and_follows_changes(self):
        self.assertEqual(len(self.view.tv.get_children()), 4)
        self.app._queue.pop()
        self.app._refresh_queue_tv()
        self.assertEqual(len(self.view.tv.get_children()), 3)

    def test_select_all_and_download_button_label(self):
        self.assertEqual(self.view.btn_dl.cget("text"), m.t("qwin.btn_download_none"))
        self.assertEqual(str(self.view.btn_dl.cget("state")), "disabled")
        self.view._select_all()
        self.view.update()
        self.assertEqual(self.view.btn_dl.cget("text"), m.t("qwin.btn_download_n", n=4))
        self.assertEqual(str(self.view.btn_dl.cget("state")), "normal")
        self.view._select_none()
        self.view.update()
        self.assertEqual(self.view.btn_dl.cget("text"), m.t("qwin.btn_download_none"))

    def test_buttons_delegate_to_the_main_window(self):
        self.view.tv.selection_set(["1", "3"])
        with mock.patch.object(self.app, "_queue_run_indices") as run, \
                mock.patch.object(self.app, "_queue_remove_indices") as remove:
            self.view._download_selection()
            self.view._remove_selection()
        run.assert_called_once_with([1, 3], parent=self.view)
        remove.assert_called_once_with([1, 3], parent=self.view)

    def test_running_state_enables_the_controls_and_locks_the_launchers(self):
        self.view.tv.selection_set(["0"])
        self.view.set_running(True)
        self.app._queue_running = True
        self.view.set_running(True)
        self.assertEqual(str(self.view.btn_stop.cget("state")), "normal")
        self.assertEqual(str(self.view.btn_dl.cget("state")), "disabled")
        self.assertEqual(str(self.view.btn_all.cget("state")), "disabled")
        self.app._queue_running = False
        self.view.set_running(False)
        self.assertEqual(str(self.view.btn_stop.cget("state")), "disabled")

    def test_range_fields_select_the_rows(self):
        self.view.spin_from.set("2")
        self.view.spin_to.set("3")
        self.view._select_range()
        self.view.update()
        self.assertEqual(self.view._indices(), [1, 2])
        self.assertEqual(self.view.btn_dl.cget("text"), m.t("qwin.btn_download_n", n=2))

    def test_range_outside_the_queue_selects_nothing(self):
        self.view.spin_from.set("9")
        self.view.spin_to.set("12")
        self.view._select_range()
        self.assertEqual(self.view._indices(), [])

    def test_run_range_goes_through_the_main_window(self):
        self.view.spin_from.set("2")
        self.view.spin_to.set("4")
        with mock.patch.object(self.app, "_queue_run") as run:
            self.view._run_range()
        run.assert_called_once_with(1, end_idx=3)

    def test_a_bad_range_warns_instead_of_running(self):
        self.view.spin_from.set("4")
        self.view.spin_to.set("2")
        with mock.patch.object(m.messagebox, "showwarning") as warn, mock.patch.object(self.app, "_queue_run") as run:
            self.view._run_range()
        warn.assert_called_once()
        run.assert_not_called()

    def test_empty_range_fields_do_nothing(self):
        self.view.spin_from.set("")
        self.view.spin_to.set("")
        with mock.patch.object(self.app, "_queue_run") as run:
            self.view._run_range()
        run.assert_not_called()

    def test_range_button_is_locked_while_the_queue_runs(self):
        self.app._queue_running = True
        self.view.set_running(True)
        self.assertEqual(str(self.view.btn_range.cget("state")), "disabled")
        self.app._queue_running = False
        self.view.set_running(False)
        self.assertEqual(str(self.view.btn_range.cget("state")), "normal")

    def test_pause_button_follows_the_pause_state(self):
        self.view.set_paused(True)
        self.assertEqual(self.view.btn_pause.cget("text"), m.t("dl.btn_resume"))
        self.view.set_paused(False)
        self.assertEqual(self.view.btn_pause.cget("text"), m.t("queue.btn_pause_queue"))

    def test_the_log_is_mirrored_and_cleared_with_the_main_one(self):
        self.app._log("ligne un")
        self.assertIn("ligne un", self.view.log.get("1.0", "end"))
        self.app._clear_log()
        self.assertEqual(self.view.log.get("1.0", "end").strip(), "")

    def test_the_log_toggle_shows_and_hides_the_pane(self):
        self.view.deiconify()
        self.view.update()
        self.view._toggle_log()
        self.view.update()
        self.assertTrue(self.view.frm_log.winfo_ismapped())
        self.view._toggle_log()
        self.view.update()
        self.assertFalse(self.view.frm_log.winfo_ismapped())

    def test_closing_the_view_unregisters_it(self):
        self.assertIn(self.view, self.app._queue_views)
        self.view.destroy()
        self.assertNotIn(self.view, self.app._queue_views)

    def test_opening_twice_reuses_the_same_window(self):
        self.app._open_queue_view()
        self.assertEqual(sum(1 for v in self.app._queue_views if v.winfo_exists()), 1)
        self.view.destroy()


if __name__ == "__main__":
    unittest.main()
