import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WheelTests(unittest.TestCase):
    def setUp(self):
        m.save_config({})
        m.load_lang("fr")
        self.app = m.YtDlpGui()
        self.app.geometry("900x520+20+20")           # fenêtre basse : la page défile
        self.addCleanup(self._close)
        self._settle()
        self.cv = self.app._page_cv

    def _close(self):
        self.app.destroy()
        m.save_config({})

    def _settle(self, n=40):
        for _ in range(n):
            self.app.update()

    def _wheel(self, widget, delta):
        # le contrôle « sous le pointeur » est imposé : sur un serveur d'intégration sans écran réel (ou à
        # l'écran plus petit que la fenêtre), la position du pointeur ne désigne pas forcément ce contrôle
        with mock.patch.object(self.app, "winfo_containing", return_value=widget):
            widget.event_generate("<MouseWheel>", delta=delta)
            self._settle(5)

    def test_wheel_scrolls_the_page_over_labels_frames_and_buttons(self):
        for name in ("_lbl_dep_warn", "_frm_url", "btn_dl", "_cookie_frame"):
            self.cv.yview_moveto(0.0)
            self._settle(3)
            self._wheel(getattr(self.app, name), -120)
            self.assertGreater(self.cv.yview()[0], 0.0, name)

    def test_one_notch_scrolls_exactly_one_step(self):
        self.cv.yview_moveto(0.0)
        self._settle(3)
        self._wheel(self.app._frm_url, -120)
        one_notch = self.cv.yview()[0]
        self.cv.yview_moveto(0.0)
        self._settle(3)
        self.cv.yview_scroll(1, "units")
        self.assertAlmostEqual(self.cv.yview()[0], one_notch, places=6, msg="défilement doublé")

    def test_wheel_up_goes_back(self):
        self.cv.yview_moveto(0.1)
        self._settle(3)
        before = self.cv.yview()[0]
        self._wheel(self.app._frm_url, 120)
        self.assertLess(self.cv.yview()[0], before)

    def test_combobox_scrolls_the_page_without_changing_its_value(self):
        combo = self.app._primary_combo
        value = combo.get()
        self.cv.yview_moveto(0.0)
        self._settle(3)
        self._wheel(combo, -120)
        self.assertEqual(combo.get(), value)
        self.assertGreater(self.cv.yview()[0], 0.0)

    def test_text_and_tables_keep_their_own_scrolling(self):
        self.cv.yview_moveto(1.0)
        self._settle(3)
        before = self.cv.yview()[0]
        self.assertIsNone(m.wheel_target(self.app.log_text, -120))
        self.assertIsNone(m.wheel_target(self.app._tv_queue, -120))
        self.assertEqual(self.cv.yview()[0], before)

    def test_nothing_to_scroll_when_the_page_fits(self):
        import tkinter as tk
        top = tk.Toplevel(self.app)            # fenêtre à part : tout le contenu y tient, rien à défiler
        self.addCleanup(top.destroy)
        cv = tk.Canvas(top, height=40, width=40, scrollregion=(0, 0, 40, 40))
        cv.configure(yscrollcommand=lambda *a: None)
        cv.pack()
        self._settle()
        self.assertEqual(cv.yview(), (0.0, 1.0))
        self.assertIsNone(m.wheel_target(cv, -120))
        self.assertIsNone(m.wheel_target(cv, 120))

    def test_nested_scroll_areas_fall_back_to_the_outer_one(self):
        import tkinter as tk
        outer = self.cv
        inner = tk.Canvas(self.app._frm_url, height=40, width=40)
        inner.configure(yscrollcommand=lambda *a: None, scrollregion=(0, 0, 40, 40))   # contenu = hauteur : rien à défiler
        inner.pack()
        self.addCleanup(inner.destroy)
        self._settle()
        self.assertEqual(inner.yview(), (0.0, 1.0))
        self.assertIs(m.wheel_target(inner, -120), outer)


if __name__ == "__main__":
    unittest.main()
