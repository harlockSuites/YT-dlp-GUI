import http.server
import json
import os
import threading
import time
import unittest
from unittest import mock

from tests._loader import load_gui, tk_available

m = load_gui()


def _release(tag="v9.0.0", **over):
    data = {
        "tag_name": tag, "name": f"yt-dlp GUI {tag}", "body": "### Ajouté\n- Une nouveauté",
        "html_url": f"https://github.com/harlockSuites/YT-dlp-GUI/releases/tag/{tag}",
        "assets": [
            {"name": f"yt-dlp-gui-setup-{tag[1:]}.exe", "size": 11,
             "browser_download_url": "https://github.com/harlockSuites/YT-dlp-GUI/releases/download/x/setup.exe"},
            {"name": f"yt-dlp-gui-portable-{tag[1:]}.zip", "size": 12,
             "browser_download_url": "https://github.com/harlockSuites/YT-dlp-GUI/releases/download/x/portable.zip"},
            {"name": "SHA256SUMS.txt", "size": 1,
             "browser_download_url": "https://github.com/harlockSuites/YT-dlp-GUI/releases/download/x/SHA256SUMS.txt"},
            {"name": "evil.exe", "size": 1, "browser_download_url": "https://evil.example.com/evil.exe"},
        ],
    }
    data.update(over)
    return data


class _Handler(http.server.BaseHTTPRequestHandler):
    status = 200
    payload = b"{}"

    def do_GET(self):
        self.send_response(self.status)
        self.send_header("Content-Length", str(len(self.payload)))
        self.end_headers()
        self.wfile.write(self.payload)

    def log_message(self, *a):
        pass


class FakeGitHub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/latest"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def serve(self, payload, status=200):
        _Handler.status = status
        _Handler.payload = json.dumps(payload).encode() if not isinstance(payload, bytes) else payload
        patcher = mock.patch.object(m, "RELEASES_API_URL", self.url)
        patcher.start()
        self.addCleanup(patcher.stop)


class VersionTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(m._parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(m._parse_version(" 0.10.0 "), (0, 10, 0))
        for bad in ("", "1.2", "v1.2.3-rc1", "abc", None):
            self.assertIsNone(m._parse_version(bad), bad)

    def test_compare_numerically_not_alphabetically(self):
        self.assertTrue(m._is_newer("0.10.0", "0.9.0"))
        self.assertTrue(m._is_newer("v1.0.0", "0.99.99"))
        self.assertFalse(m._is_newer("0.1.0", "0.1.0"))
        self.assertFalse(m._is_newer("0.1.0", "0.2.0"))
        self.assertFalse(m._is_newer("garbage", "0.1.0"))

    def test_github_urls_only(self):
        self.assertTrue(m._is_github_url("https://github.com/x/y/releases"))
        self.assertTrue(m._is_github_url("https://objects.githubusercontent.com/abc"))
        for bad in ("http://github.com/x", "https://evil.example.com/github.com", "https://github.com.evil.com/x",
                    "https://notgithub.com/x", "", None, "javascript:alert(1)"):
            self.assertFalse(m._is_github_url(bad), bad)

    def test_install_kind(self):
        self.assertEqual(m._install_kind(frozen=False), "source")
        import tempfile
        d = tempfile.mkdtemp()
        exe = os.path.join(d, "yt-dlp-gui.exe")
        self.assertEqual(m._install_kind(True, exe), "installer")
        with open(os.path.join(d, "portable.flag"), "w") as f:
            f.write("x")
        self.assertEqual(m._install_kind(True, exe), "portable")

    def test_throttling(self):
        now = 1_000_000.0
        self.assertTrue(m.should_check_updates({}, now))
        self.assertFalse(m.should_check_updates({"update_check": False}, now))
        self.assertFalse(m.should_check_updates({"update_last_check": now - 3600}, now))
        self.assertTrue(m.should_check_updates({"update_last_check": now - 90000}, now))


class FetchTests(FakeGitHub):
    def test_new_release_is_reported_with_safe_assets_only(self):
        self.serve(_release("v9.0.0"))
        info = m.check_for_update(current="0.1.0")
        self.assertEqual(info["version"], "9.0.0")
        self.assertIn("nouveauté", info["notes"])
        self.assertEqual(sorted(a["name"] for a in info["assets"]),
                         ["SHA256SUMS.txt", "yt-dlp-gui-portable-9.0.0.zip", "yt-dlp-gui-setup-9.0.0.exe"],
                         "le fichier hors github.com est écarté")
        self.assertTrue(info["url"].startswith("https://github.com/"))

    def test_up_to_date_returns_none(self):
        self.serve(_release("v0.1.0"))
        self.assertIsNone(m.check_for_update(current="0.1.0"))
        self.assertIsNone(m.check_for_update(current="0.2.0"))

    def test_not_found_is_explicit(self):
        self.serve({"message": "Not Found"}, status=404)
        with self.assertRaises(m.UpdateError) as cm:
            m.check_for_update()
        self.assertTrue(cm.exception.not_found)

    def test_other_http_error_and_garbage(self):
        self.serve({}, status=403)
        with self.assertRaises(m.UpdateError):
            m.check_for_update()
        self.serve(b"pas du json")
        with self.assertRaises(m.UpdateError):
            m.check_for_update()

    def test_invalid_tag_is_rejected(self):
        self.serve(_release("v1.x"))
        with self.assertRaises(m.UpdateError):
            m.check_for_update()

    def test_network_failure_is_an_update_error(self):
        with mock.patch.object(m, "RELEASES_API_URL", "http://127.0.0.1:9/latest"):
            with self.assertRaises(m.UpdateError):
                m.check_for_update()

    def test_foreign_release_page_falls_back_to_repo(self):
        self.serve(_release("v9.0.0", html_url="https://evil.example.com/x"))
        self.assertEqual(m.check_for_update(current="0.1.0")["url"], m.REPO_URL + "/releases")

    def test_asset_choice_depends_on_install_kind(self):
        self.serve(_release("v9.0.0"))
        info = m.check_for_update(current="0.1.0")
        self.assertTrue(m.pick_asset(info, "installer")["name"].endswith(".exe"))
        self.assertTrue(m.pick_asset(info, "portable")["name"].endswith(".zip"))
        self.assertIsNone(m.pick_asset(info, "source"))


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        m.save_config({})
        self.app._update_info = None
        self.app._frm_update.pack_forget()

    def _pump(self, until, timeout=5):
        deadline = time.time() + timeout

        def tick():
            if until() or time.time() > deadline:
                self.app.quit()
            else:
                self.app.after(20, tick)
        self.app.after(20, tick)
        self.app.mainloop()

    def _info(self, version="9.0.0"):
        return {
            "version": version, "tag": f"v{version}", "name": "", "notes": "Notes de test",
            "url": f"https://github.com/harlockSuites/YT-dlp-GUI/releases/tag/v{version}",
            "assets": [{"name": f"yt-dlp-gui-setup-{version}.exe", "size": 1,
                        "url": "https://github.com/harlockSuites/YT-dlp-GUI/releases/download/x/s.exe"}]}

    def test_banner_shows_for_new_version_and_hides_when_ignored(self):
        info = self._info()
        self.app._record_update_check(info)
        self.assertIn("9.0.0", self.app._lbl_update.cget("text"))
        self.assertTrue(self.app._frm_update.winfo_manager())
        cfg = m.load_config()
        self.assertGreater(cfg["update_last_check"], 0)
        m.save_config(dict(cfg, update_ignored="9.0.0"))
        self.app._record_update_check(info)
        self.assertFalse(self.app._frm_update.winfo_manager(), "version ignorée : bandeau masqué")
        self.app._record_update_check(self._info("9.1.0"))
        self.assertTrue(self.app._frm_update.winfo_manager(), "une version plus récente réapparaît")

    def test_no_banner_when_up_to_date(self):
        self.app._record_update_check(None)
        self.assertFalse(self.app._frm_update.winfo_manager())

    def test_startup_check_is_throttled_and_silent_on_errors(self):
        with mock.patch.object(m, "check_for_update") as chk:
            m.save_config({"update_check": False})
            self.app._maybe_check_updates()
            m.save_config({"update_last_check": time.time()})
            self.app._maybe_check_updates()
            chk.assert_not_called()
        m.save_config({})
        with mock.patch.object(m, "check_for_update", side_effect=m.UpdateError("hors ligne")):
            self.app._maybe_check_updates()
            time.sleep(0.2)
            self.app.update()
        self.assertFalse(self.app._frm_update.winfo_manager())

    def test_startup_check_displays_banner(self):
        with mock.patch.object(m, "check_for_update", return_value=self._info()):
            self.app.after(10, self.app._maybe_check_updates)
            self._pump(lambda: bool(self.app._frm_update.winfo_manager()))
        self.assertTrue(self.app._frm_update.winfo_manager())

    def test_options_menu_has_the_check_now_entry_and_the_auto_switch(self):
        captured = []
        with mock.patch.object(m.tk.Menu, "tk_popup", autospec=True,
                               side_effect=lambda menu, x, y: captured.append(menu)):
            self.app._open_options_menu()
        menu = captured[0]
        labels = [(menu.type(i), menu.entrycget(i, "label")) for i in range(menu.index("end") + 1)
                  if menu.type(i) in ("command", "checkbutton")]
        self.assertIn(("command", m.t("toolbar.menu_check_update")), labels)
        self.assertIn(("checkbutton", m.t("toolbar.menu_auto_update_check")), labels)

    def test_auto_switch_is_saved_and_reflects_the_config(self):
        m.save_config({"update_check": False})
        captured = []
        with mock.patch.object(m.tk.Menu, "tk_popup", autospec=True,
                               side_effect=lambda menu, x, y: captured.append(menu)):
            self.app._open_options_menu()
        self.assertFalse(self.app._var_auto_update.get(), "le menu reflète la config")
        self.app._var_auto_update.set(True)
        self.app._toggle_auto_update()
        self.assertTrue(m.load_config()["update_check"])
        self.app._var_auto_update.set(False)
        self.app._toggle_auto_update()
        self.assertFalse(m.load_config()["update_check"])

    def _window(self, **kw):
        win = m.AppUpdateWindow(self.app, **kw)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def test_window_with_known_update_enables_buttons_and_opens_github_only(self):
        win = self._window(info=self._info())
        self.assertIn("9.0.0", win.var_status.get())
        self.assertIn("Notes de test", win.txt.get("1.0", "end"))
        self.assertEqual(str(win.btn_page.cget("state")), "normal")
        with mock.patch.object(m.webbrowser, "open") as opened, \
                mock.patch.object(m, "_install_kind", return_value="installer"):
            win._open_page()
            win._download()
        urls = [c.args[0] for c in opened.call_args_list]
        self.assertTrue(all(u.startswith("https://github.com/") for u in urls))
        self.assertTrue(urls[1].endswith("s.exe"))

    def test_window_from_source_has_no_download_button(self):
        with mock.patch.object(m, "_install_kind", return_value="source"):
            win = self._window(info=self._info())
        self.assertEqual(str(win.btn_dl.cget("state")), "disabled")
        self.assertIn("git pull", win.lbl_hint.cget("text"))

    def test_window_checks_by_itself_and_reports_up_to_date(self):
        with mock.patch.object(m, "check_for_update", return_value=None):
            win = self._window()
            self._pump(lambda: "dernière" in win.var_status.get())
        self.assertIn(m.__version__, win.var_status.get())
        self.assertEqual(str(win.btn_page.cget("state")), "disabled")

    def test_window_reports_errors(self):
        with mock.patch.object(m, "check_for_update", side_effect=m.UpdateError("réseau coupé")):
            win = self._window()
            self._pump(lambda: "réseau coupé" in win.var_status.get())
        self.assertIn("réseau coupé", win.var_status.get())

    def test_ignore_and_auto_check_settings_are_saved(self):
        win = self._window(info=self._info())
        win.var_auto.set(False)
        self.assertFalse(m.load_config()["update_check"])
        win._ignore()
        self.assertEqual(m.load_config()["update_ignored"], "9.0.0")
        self.assertFalse(self.app._frm_update.winfo_manager())


if __name__ == "__main__":
    unittest.main()
