import unittest

from tests._loader import load_gui, tk_available

m = load_gui()


class ScreenFitTests(unittest.TestCase):
    SW, SH = 1366, 768   # petit écran de portable

    def test_window_that_fits_keeps_its_position(self):
        self.assertEqual(m._screen_fit_geometry(self.SW, self.SH, 460, 300, 200, 100), (460, 300, 200, 100))

    def test_window_that_overflows_the_bottom_is_moved_up(self):
        w, h, x, y = m._screen_fit_geometry(self.SW, self.SH, 460, 500, 200, 600)
        self.assertEqual((w, h, x), (460, 500, 200))
        self.assertLessEqual(y + h, self.SH - 60, "reste au-dessus de la barre des tâches")
        self.assertGreaterEqual(y, 10)

    def test_window_taller_than_the_screen_is_shortened(self):
        w, h, x, y = m._screen_fit_geometry(self.SW, 600, 520, 900, 100, 400)
        self.assertLessEqual(h, 600 - 60)
        self.assertLessEqual(y + h, 600 - 60)
        self.assertGreaterEqual(y, 10)

    def test_window_overflowing_the_right_edge_is_moved_left(self):
        w, h, x, y = m._screen_fit_geometry(self.SW, self.SH, 520, 300, 1300, 100)
        self.assertLessEqual(x + w, self.SW - 10)

    def test_both_popups_use_the_helper(self):
        with open(m.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertEqual(source.count("_screen_fit_geometry(pop.winfo_screenwidth()"), 2)
        self.assertNotIn('pop.geometry(f"520x480+{x}+{y}")', source)
        self.assertNotIn('pop.geometry(f"460x{h}+{x}+{y}")', source)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class QueueButtonsStayVisibleTests(unittest.TestCase):
    def setUp(self):
        m.save_config({})
        m.load_lang("fr")
        self.app = m.YtDlpGui()
        self.app.update()
        self.addCleanup(self._close)

    def _close(self):
        self.app.destroy()
        m.save_config({})

    def _settle(self):
        for _ in range(40):
            self.app.update()

    def _buttons_inside_queue_pane(self):
        app = self.app
        pane = app._frm_queue
        low = max(b.winfo_rooty() + b.winfo_height() for b in (app.btn_q_pause, app.btn_q_skip, app.btn_q_stop))
        return low <= pane.winfo_rooty() + pane.winfo_height()

    def test_right_after_startup(self):
        self._settle()
        self.assertTrue(self._buttons_inside_queue_pane())
        self.assertGreaterEqual(self.app._frm_queue.winfo_height(), self.app._frm_queue.winfo_reqheight() - 5)

    def test_short_windows_scroll_instead_of_covering_buttons(self):
        for geo in ("900x600", "800x420"):
            self.app.geometry(geo)
            self._settle()
            self.assertTrue(self._buttons_inside_queue_pane(), geo)
            self.assertTrue(self.app._page_vsb.winfo_ismapped(), f"barre de défilement attendue à {geo}")

    def test_dragging_the_separator_cannot_hide_the_buttons(self):
        self.app.geometry("900x700")
        self._settle()
        self.app._paned.sash_place(0, 0, 5)        # tente de réduire le tableau de la file au maximum
        self._settle()
        self.assertTrue(self._buttons_inside_queue_pane())
        self.app._paned.sash_place(0, 0, 4000)     # ... puis de réduire le journal au maximum
        self._settle()
        self.assertTrue(self._buttons_inside_queue_pane())
        self.assertGreater(self.app._frm_log.winfo_height(), 40)


if __name__ == "__main__":
    unittest.main()
