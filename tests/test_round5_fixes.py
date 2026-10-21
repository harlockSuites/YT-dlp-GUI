import json
import types
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()

PRIVATE_ID = "J7Nb13oYwjc"


def _contrast(app, fg, bg):
    def luminance(color):
        r, g, b = (c / 65535 for c in app.winfo_rgb(color))
        lin = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class InspectorListingCookiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.insp = m.PlaylistInspectorWindow(self.app, outdir="")
        self.insp.withdraw()
        self.addCleanup(self.insp.destroy)
        self.calls, self.logged = [], []
        patches = [
            mock.patch.object(self.insp, "after", side_effect=lambda ms, fn=None, *a: fn(*a) if fn else None),
            mock.patch.object(self.insp, "_log", side_effect=lambda msg: self.logged.append(msg)),
            mock.patch.object(self.insp, "_add_row"),
            mock.patch("time.sleep"),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def _fake_run(self, listing_stdout="", listing_rc=0, listing_stderr=""):
        def run(args, *a, **k):
            self.calls.append(list(args))
            if "--flat-playlist" in args:
                return types.SimpleNamespace(returncode=listing_rc, stdout=listing_stdout, stderr=listing_stderr)
            return types.SimpleNamespace(returncode=1, stdout="", stderr="ERROR: boom")
        return mock.patch.object(m.subprocess, "run", side_effect=run)

    def _listing(self):
        return next(c for c in self.calls if "--flat-playlist" in c)

    def test_listing_uses_the_chosen_browser_cookies(self):
        """Sans cookies, une vidéo privée du compte connecté n'a pas de titre : elle était ignorée."""
        self.insp.var_g_browser.set("opera")
        stdout = json.dumps({"id": PRIVATE_ID, "title": "Pedro le film"})
        with self._fake_run(stdout):
            self.insp._run_analyze_impl("https://www.youtube.com/playlist?list=PLabc")
        listing = self._listing()
        self.assertEqual(listing[listing.index("--cookies-from-browser") + 1], "opera")
        self.assertLess(listing.index("--cookies-from-browser"), listing.index("--"))
        self.assertTrue(any(PRIVATE_ID in " ".join(c) for c in self.calls if "--flat-playlist" not in c),
                        "la vidéo privée du compte est analysée")

    def test_listing_without_cookies_has_no_cookie_option(self):
        self.insp.var_g_browser.set(m.BROWSER_OFF)
        with self._fake_run(json.dumps({"id": "abc", "title": "Une vidéo"})):
            self.insp._run_analyze_impl("https://www.youtube.com/playlist?list=PLabc")
        self.assertNotIn("--cookies-from-browser", self._listing())

    def test_hidden_videos_are_still_skipped(self):
        self.insp.var_g_browser.set(m.BROWSER_OFF)
        stdout = "\n".join(json.dumps(e) for e in ({"id": "a", "title": None}, {"id": "b", "title": "[Private video]"}))
        with self._fake_run(stdout):
            self.insp._run_analyze_impl("https://www.youtube.com/playlist?list=PLabc")
        self.assertTrue(any("2 élément(s) masqué(s)" in x for x in self.logged))
        self.assertEqual([c for c in self.calls if "--flat-playlist" not in c], [])

    def test_single_private_video_of_the_connected_account_is_not_skipped(self):
        """Adresse d'une vidéo seule : `availability` vaut « private » pour son propriétaire (« 1 élément masqué »)."""
        self.insp.var_g_browser.set("opera")
        stdout = json.dumps({"id": PRIVATE_ID, "title": "Pedro le film", "availability": "private"})
        with self._fake_run(stdout):
            self.insp._run_analyze_impl("https://www.youtube.com/watch?v=" + PRIVATE_ID)
        self.assertFalse(any("masqué(s)" in x for x in self.logged), self.logged)
        self.assertTrue(any(PRIVATE_ID in " ".join(c) for c in self.calls if "--flat-playlist" not in c))

    def test_members_only_videos_are_still_skipped(self):
        self.insp.var_g_browser.set("opera")
        stdout = "\n".join(json.dumps({"id": f"v{n}", "title": "x", "availability": a})
                           for n, a in enumerate(("subscriber_only", "premium_only")))
        with self._fake_run(stdout):
            self.insp._run_analyze_impl("https://www.youtube.com/playlist?list=PLabc")
        self.assertTrue(any("2 élément(s) masqué(s)" in x for x in self.logged))

    def test_duplicate_error_lines_are_logged_once(self):
        self.insp.var_g_browser.set("opera")
        error = "ERROR: Could not copy Chrome cookie database. See https://github.com/yt-dlp/yt-dlp/issues/7271"
        with mock.patch.object(m, "browser_process_count", return_value=0), \
                self._fake_run("", listing_rc=1, listing_stderr=error + "\n" + error + "\n"):
            self.insp._run_analyze_impl("https://www.youtube.com/watch?v=" + PRIVATE_ID)
        self.assertEqual(sum("Could not copy" in x for x in self.logged), 1, self.logged)

    def test_the_reason_of_a_failed_listing_is_logged(self):
        self.insp.var_g_browser.set("opera")
        with mock.patch.object(m, "browser_process_count", return_value=0), \
                self._fake_run("", listing_rc=1, listing_stderr="ERROR: Could not copy Opera cookie database\n"):
            self.insp._run_analyze_impl("https://www.youtube.com/watch?v=" + PRIVATE_ID)
        self.assertTrue(any("[liste]" in x and "Could not copy" in x for x in self.logged), self.logged)
        self.assertTrue(any("Opera" in x and "verrouill" in x for x in self.logged), self.logged)


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class QueueColoursTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_queue_text_is_readable_on_the_table_background(self):
        background = m.ttk.Style(self.app).lookup("Treeview", "background") or "white"
        for tag in ("pending", "running", "error"):
            colour = self.app._tv_queue.tag_configure(tag, "foreground")
            self.assertGreaterEqual(_contrast(self.app, str(colour), str(background)), 4.5, f"{tag} {colour} sur {background}")


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class UpdateWindowWrapTests(unittest.TestCase):
    """La fenêtre doit être affichée pour recevoir ses événements de taille : sa fenêtre parente aussi
    (une fenêtre transitoire d'un parent masqué reste invisible)."""

    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.geometry("+0+0")
        cls.app.update()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def test_long_network_message_wraps_inside_the_window(self):
        info = {"version": "9.9.9", "tag": "v9.9.9", "name": "", "notes": "x", "url": "https://github.com/x", "assets": []}
        with mock.patch.object(m, "_install_kind", return_value="installer"):
            win = m.AppUpdateWindow(self.app, info=info)
        self.addCleanup(win.destroy)
        win.geometry("560x430")
        win._show(None, m.UpdateError(m.t("net.offline", detail="[Errno 11001] getaddrinfo failed")))
        for _ in range(30):
            self.app.update()
        wrap = int(win.lbl_status.cget("wraplength"))
        self.assertGreater(wrap, 0)
        self.assertLessEqual(wrap, win.winfo_width(), "le message ne doit pas dépasser la fenêtre")
        self.assertLessEqual(win.lbl_status.winfo_reqwidth(), win.winfo_width())

    def test_wrap_follows_the_window_width(self):
        info = {"version": "9.9.9", "tag": "v9.9.9", "name": "", "notes": "x", "url": "https://github.com/x", "assets": []}
        with mock.patch.object(m, "_install_kind", return_value="installer"):
            win = m.AppUpdateWindow(self.app, info=info)
        self.addCleanup(win.destroy)
        win.geometry("800x430")
        for _ in range(30):
            self.app.update()
        wide = int(win.lbl_status.cget("wraplength"))
        win.geometry("480x430")
        for _ in range(30):
            self.app.update()
        self.assertLess(int(win.lbl_status.cget("wraplength")), wide)


if __name__ == "__main__":
    unittest.main()
