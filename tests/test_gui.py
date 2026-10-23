import os
import shutil
import tempfile
import unittest

from tests._loader import load_gui, tk_available

m = load_gui()
HAS_TK = tk_available()
VID = {"id": "dQw4w9WgXcQ", "title": "Ma vidéo", "audio_langs": ["fr", "en"],
       "sub_langs": ["fr"], "auto_only_subs": []}


def _opt(args, flag):
    return args[args.index(flag) + 1]


@unittest.skipUnless(HAS_TK, "pas d'affichage Tk disponible")
class GuiCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        m.save_config({})
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="out-")
        self.addCleanup(shutil.rmtree, self.out, ignore_errors=True)


class MainWindowTests(GuiCase):
    def test_title_shows_version(self):
        self.assertIn(m.__version__, self.app.title())

    def test_audio_only_with_embedded_subs_does_not_crash(self):
        app = self.app
        app.var_audio_only.set(True)
        app.var_embed_subs.set(True)
        app._subs_sel.set_options([("alang_fr", "FR")])
        app._subs_sel.set_selected(["alang_fr"])
        try:
            args = app._build_args()
        finally:
            app.var_audio_only.set(False)
            app._subs_sel.set_selected([])
        self.assertIn("--extract-audio", args)

    def test_output_dir_with_percent_is_escaped(self):
        self.app.var_outdir.set(r"C:\Temp\100% test")
        args = self.app._build_args()
        self.assertEqual(_opt(args, "-o"), os.path.join(r"C:\Temp\100%% test", "%(title)s.%(ext)s"))

    def test_cookies_argument_follows_browser(self):
        self.app.var_browser.set("firefox")
        self.assertEqual(_opt(self.app._build_args(), "--cookies-from-browser"), "firefox")
        self.app.var_browser.set(m.BROWSER_OFF)
        self.assertNotIn("--cookies-from-browser", self.app._build_args())


class InspectorTests(GuiCase):
    def setUp(self):
        super().setUp()
        self.insp = m.PlaylistInspectorWindow(self.app, outdir=self.out)
        self.insp.withdraw()
        self.addCleanup(self.insp.destroy)
        self.insp._add_row(1, dict(VID))
        self.row = self.insp._rows[0]

    def test_basic_command(self):
        args = self.insp._build_video_args(self.row)
        self.assertEqual(args[-2:], ["--", m._watch_url(VID["id"])])
        self.assertIn("-f", args)
        self.assertNotIn("--cookies-from-browser", args)

    def test_cookies(self):
        self.insp.var_g_browser.set("edge")
        self.assertEqual(_opt(self.insp._build_video_args(self.row), "--cookies-from-browser"), "edge")

    def test_audio_only_with_embedded_subs_does_not_crash(self):
        i = self.insp
        i._g_subs.set_options([("fr", "FR")])
        i._g_subs.set_selected(["fr"])
        i.var_g_embed_subs.set(True)
        i.var_g_audio_only.set(True)
        args = i._build_video_args(self.row)
        self.assertIn("--extract-audio", args)

    def test_unresolved_manual_choice_falls_back_to_global_rule(self):
        self.row["var_primary"].set(self.insp._g_opt_manual)
        args = self.insp._build_video_args(self.row)
        self.assertNotIn("—", " ".join(args))

    def test_percent_in_title_is_escaped_on_name_conflict(self):
        vid = dict(VID, title="100% Cotton")
        self.insp._clear_rows()
        self.insp._add_row(1, vid)
        open(os.path.join(self.out, "100% Cotton.mp4"), "w").close()
        args = self.insp._build_video_args(self.insp._rows[0])
        self.assertEqual(os.path.basename(_opt(args, "-o")), "100%% Cotton_2.%(ext)s")

    def test_smart_directory_adds_archive_and_inbox(self):
        self.insp.var_g_smart_dir.set(True)
        args = self.insp._build_video_args(self.row)
        self.assertEqual(_opt(args, "--download-archive"), os.path.join(self.out, m.ARCHIVE_NAME))
        self.assertIn("--print-to-file", args)

    def test_numbering_prefix(self):
        self.insp.var_g_numbering.set(True)
        args = self.insp._build_video_args(self.row)
        self.assertTrue(os.path.basename(_opt(args, "-o")).startswith("01 - "))

    def test_subs_only(self):
        self.assertEqual(self.insp._build_video_args(self.row, subs_only=True), [])
        self.insp._g_subs.set_options([("fr", "FR")])
        self.insp._g_subs.set_selected(["fr"])
        self.assertIn("--skip-download", self.insp._build_video_args(self.row, subs_only=True))

    def test_inherits_and_returns_browser_choice(self):
        self.app.var_browser.set("edge")
        insp2 = m.PlaylistInspectorWindow(self.app)
        insp2.withdraw()
        self.assertEqual(insp2.var_g_browser.get(), "edge")
        insp2.var_g_browser.set("chrome")
        insp2._on_inspector_close()
        self.assertEqual(self.app.var_browser.get(), "chrome")


class WidgetTests(GuiCase):
    def test_browser_combo_shows_translated_label_but_keeps_sentinel(self):
        import tkinter as tk
        m.load_lang("en")
        try:
            var = tk.StringVar(value=m.BROWSER_OFF)
            cb = m._browser_combo(self.app, var)
            self.assertEqual(cb.get(), "Disabled")
            var.set("firefox")
            self.assertEqual(cb.get(), "firefox")
            cb.set("Disabled")
            cb.event_generate("<<ComboboxSelected>>")
            self.app.update()
            self.assertEqual(var.get(), m.BROWSER_OFF)
        finally:
            m.load_lang("fr")

    def test_flow_frame_wraps_children(self):
        import tkinter as tk
        from tkinter import ttk
        top = tk.Toplevel(self.app)
        top.geometry("300x200")
        flow = m._FlowFrame(top)
        flow.pack(fill="x")
        boxes = []
        for _ in range(3):
            b = ttk.Frame(flow, width=120, height=20)
            flow.add(b)
            boxes.append(b)
        for _ in range(5):
            top.update()
        ys = [b.winfo_y() for b in boxes]
        self.assertEqual(ys[0], ys[1], "les deux premiers tiennent sur la même ligne")
        self.assertGreater(ys[2], ys[0], "le troisième passe à la ligne")
        top.destroy()


@unittest.skipUnless(HAS_TK, "pas d'affichage Tk disponible")
class CloseKeepsConfigTests(unittest.TestCase):
    def test_close_preserves_language_and_other_keys(self):
        m.save_config({"lang": "en", "autre": 42})
        app = m.YtDlpGui()
        app.withdraw()
        app.var_outdir.set("C:/x")
        app._on_close()
        cfg = m.load_config()
        self.assertEqual(cfg["lang"], "en")
        self.assertEqual(cfg["autre"], 42)
        self.assertEqual(cfg["outdir"], "C:/x")
        m.save_config({})


if __name__ == "__main__":
    unittest.main()
