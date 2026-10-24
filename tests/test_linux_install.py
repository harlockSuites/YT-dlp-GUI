"""« Installer dans le menu » (sans administrateur) et paquet .deb : testés sur tous les systèmes avec des dossiers
temporaires (rien n'est écrit dans le vrai ~/.local ni le vrai Bureau)."""
import gzip
import importlib.util
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

from tests._loader import ROOT, load_gui, tk_available

m = load_gui()

LANG_DIR = os.path.join(ROOT, "lang")


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "packaging", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bd = _load_script("build_deb")
rt = _load_script("release_tools")


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _text(path, mode="r"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()


class LauncherTextTests(unittest.TestCase):
    def test_exec_is_quoted_and_escaped_as_the_desktop_specification_wants(self):
        self.assertEqual(m.desktop_exec_quote("/home/u/app/yt-dlp-gui"), '"/home/u/app/yt-dlp-gui"')
        self.assertEqual(m.desktop_exec_quote("/home/u/My Apps/yt-dlp gui"), '"/home/u/My Apps/yt-dlp gui"')
        self.assertEqual(m.desktop_exec_quote('/a"b'), '"/a\\\\"b"')
        self.assertEqual(m.desktop_exec_quote("/a$b"), '"/a\\\\$b"')
        self.assertEqual(m.desktop_exec_quote("/a`b"), '"/a\\\\`b"')
        self.assertEqual(m.desktop_exec_quote("/a\\b"), '"/a\\\\\\\\b"')
        self.assertEqual(m.desktop_exec_quote("/100%/x"), '"/100%%/x"')

    def test_the_launcher_carries_the_marker_the_window_class_and_the_absolute_icon(self):
        text = m.menu_launcher_text("/home/u/app/yt-dlp-gui.AppImage", "/home/u/icons/yt-dlp-gui.png")
        lines = text.splitlines()
        self.assertEqual(lines[0], "[Desktop Entry]")
        self.assertIn('Exec="/home/u/app/yt-dlp-gui.AppImage"', lines)
        self.assertIn("Icon=/home/u/icons/yt-dlp-gui.png", lines)
        self.assertIn("StartupWMClass=yt-dlp-gui", lines)
        self.assertIn("Terminal=false", lines)
        self.assertIn(m.MENU_MARKER, lines)
        self.assertTrue(text.endswith("\n"))

    def test_a_path_with_a_line_break_is_refused(self):
        with self.assertRaises(m.MenuInstallError):
            m.menu_launcher_text("/home/u/a\nb", "/i.png")


class PathsTests(unittest.TestCase):
    def test_xdg_data_home_is_followed_only_when_absolute(self):
        base = os.path.abspath(os.sep + "xdg-data")
        self.assertEqual(m.xdg_data_home({"XDG_DATA_HOME": base}), base)
        home_default = os.path.join(os.path.expanduser("~"), ".local", "share")
        self.assertEqual(m.xdg_data_home({}), home_default)
        self.assertEqual(m.xdg_data_home({"XDG_DATA_HOME": "relatif"}), home_default)

    def test_every_installed_file_lives_in_the_users_own_folders(self):
        base = os.path.abspath(os.sep + "data")
        paths = m.linux_menu_paths({"XDG_DATA_HOME": base})
        self.assertEqual(paths["app_dir"], os.path.join(base, "yt-dlp-GUI", "app"))
        self.assertEqual(paths["launcher"], os.path.join(base, "applications", "yt-dlp-gui.desktop"))
        self.assertEqual(paths["icon"], os.path.join(base, "icons", "hicolor", "256x256", "apps", "yt-dlp-gui.png"))

    def test_the_desktop_folders_are_the_existing_ones_in_order(self):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, ignore_errors=True)
        os.makedirs(os.path.join(home, "Bureau"))
        os.makedirs(os.path.join(home, "Desktop"))
        custom = os.path.join(home, "Custom")
        os.makedirs(custom)
        with mock.patch.object(m, "_run_quiet", return_value=custom):
            self.assertEqual(m.linux_desktop_dirs(home), [custom, os.path.join(home, "Desktop"),
                                                          os.path.join(home, "Bureau")])
        with mock.patch.object(m, "_run_quiet", return_value=""):
            self.assertEqual(m.linux_desktop_dirs(home), [os.path.join(home, "Desktop"), os.path.join(home, "Bureau")])
        with mock.patch.object(m, "_run_quiet", return_value=os.path.join(home, "absent")):
            self.assertEqual(len(m.linux_desktop_dirs(home)), 2)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.data = os.path.join(self.tmp, "data")
        self.desktop = os.path.join(self.tmp, "Desktop")
        os.makedirs(self.desktop)
        self.env = {"XDG_DATA_HOME": self.data}
        self.icon = os.path.join(self.tmp, "icon.png")
        with open(self.icon, "wb") as f:
            f.write(b"\x89PNG-test")
        p = mock.patch.object(m, "_run_quiet", return_value="")
        self.run_quiet = p.start()
        self.addCleanup(p.stop)

    def _appimage(self, content=b"appimage-v1"):
        path = os.path.join(self.tmp, "Downloads", "yt-dlp-gui-0.1.1-x86_64.AppImage")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        os.chmod(path, 0o755)
        return path

    def _install(self, kind="appimage", shortcut=True, **env):
        return m.linux_menu_install(shortcut, kind=kind, env={**self.env, **env}, icon_source=self.icon,
                                    desktop_dirs=[self.desktop])

    def test_an_appimage_is_copied_and_gets_a_launcher_an_icon_and_a_desktop_shortcut(self):
        src = self._appimage()
        result = self._install(APPIMAGE=src)
        paths = m.linux_menu_paths(self.env)
        target = os.path.join(paths["app_dir"], "yt-dlp-gui.AppImage")
        self.assertEqual(result["exec"], target)
        with open(target, "rb") as f:
            self.assertEqual(f.read(), b"appimage-v1")
        if os.name == "posix":
            self.assertTrue(os.access(target, os.X_OK))
        launcher = _text(paths["launcher"])
        self.assertIn(f"Exec={m.desktop_exec_quote(target)}", launcher)
        self.assertIn(f"Icon={paths['icon']}", launcher)
        self.assertTrue(os.path.isfile(paths["icon"]))
        shortcut = os.path.join(self.desktop, "yt-dlp-gui.desktop")
        self.assertEqual(result["shortcut"], shortcut)
        self.assertEqual(_text(shortcut), launcher)
        self.assertFalse(any(n.endswith(".part") for n in os.listdir(paths["app_dir"])))
        self.assertEqual(m.linux_menu_state(self.env, [self.desktop]), {"installed": True, "shortcut": True})

    def test_no_shortcut_unless_asked(self):
        self._install(APPIMAGE=self._appimage(), shortcut=False)
        self.assertEqual(os.listdir(self.desktop), [])
        self.assertEqual(m.linux_menu_state(self.env, [self.desktop]), {"installed": True, "shortcut": False})

    def test_a_missing_desktop_folder_is_reported_and_the_menu_entry_still_works(self):
        result = m.linux_menu_install(True, kind="appimage", env={**self.env, "APPIMAGE": self._appimage()},
                                      icon_source=self.icon, desktop_dirs=[])
        self.assertTrue(result["desktop_missing"])
        self.assertIsNone(result["shortcut"])
        self.assertTrue(os.path.isfile(m.linux_menu_paths(self.env)["launcher"]))

    def test_the_desktop_database_and_gnome_trust_are_refreshed_when_the_tools_exist(self):
        self._install(APPIMAGE=self._appimage())
        commands = [c.args[0][0] for c in self.run_quiet.call_args_list]
        self.assertIn("update-desktop-database", commands)
        gio = [c.args[0] for c in self.run_quiet.call_args_list if c.args[0][0] == "gio"]
        self.assertEqual(gio[0][1:2], ["set"])
        self.assertEqual(gio[0][-2:], ["metadata::trusted", "true"])

    def test_installing_again_updates_the_copy(self):
        self._install(APPIMAGE=self._appimage(b"v1"))
        self._install(APPIMAGE=self._appimage(b"version-2"))
        target = os.path.join(m.linux_menu_paths(self.env)["app_dir"], "yt-dlp-gui.AppImage")
        with open(target, "rb") as f:
            self.assertEqual(f.read(), b"version-2")

    def test_running_the_installed_copy_does_not_break_it(self):
        self._install(APPIMAGE=self._appimage())
        target = os.path.join(m.linux_menu_paths(self.env)["app_dir"], "yt-dlp-gui.AppImage")
        self._install(APPIMAGE=target)
        with open(target, "rb") as f:
            self.assertEqual(f.read(), b"appimage-v1")

    def test_the_archive_folder_is_copied_without_portable_flag(self):
        folder = os.path.join(self.tmp, "yt-dlp-gui")
        os.makedirs(os.path.join(folder, "_internal"))
        for name, data in (("yt-dlp-gui", b"exe"), ("_internal/lib.so", b"lib"), ("portable.flag", b"")):
            with open(os.path.join(folder, name), "wb") as f:
                f.write(data)
        result = m.linux_menu_install(False, kind="portable", env=self.env, icon_source=self.icon,
                                      desktop_dirs=[self.desktop], executable=os.path.join(folder, "yt-dlp-gui"))
        target = os.path.join(m.linux_menu_paths(self.env)["app_dir"], "yt-dlp-gui")
        self.assertEqual(result["exec"], os.path.join(target, "yt-dlp-gui"))
        self.assertTrue(os.path.isfile(os.path.join(target, "_internal", "lib.so")))
        self.assertFalse(os.path.exists(os.path.join(target, "portable.flag")),
                         "la copie installée garde ses réglages dans le dossier de l'utilisateur")

    def test_nothing_to_install_from_the_deb_package_or_the_sources(self):
        with self.assertRaises(m.MenuInstallError) as ctx:
            self._install(kind="deb")
        self.assertEqual(ctx.exception.key, "menu_install.deb")
        for kind in ("source", "installer"):
            with self.assertRaises(m.MenuInstallError) as ctx:
                self._install(kind=kind)
            self.assertEqual(ctx.exception.key, "menu_install.err_source")
        with self.assertRaises(m.MenuInstallError):   # AppImage annoncé mais fichier introuvable
            self._install(kind="appimage", APPIMAGE=os.path.join(self.tmp, "absent.AppImage"))
        self.assertFalse(os.path.exists(m.linux_menu_paths(self.env)["launcher"]))

    def test_a_copy_failure_becomes_a_readable_error(self):
        with mock.patch.object(m.shutil, "copy2", side_effect=OSError("disque plein")):
            with self.assertRaises(m.MenuInstallError) as ctx:
                self._install(APPIMAGE=self._appimage())
        self.assertEqual(ctx.exception.key, "menu_install.err_copy")
        self.assertIn("disque plein", ctx.exception.text())

    def _wanted(self, cfg=None, kind="appimage", **env):
        with mock.patch.object(m, "IS_WINDOWS", False):
            return m.linux_menu_invite_wanted(cfg or {}, kind=kind, env={**self.env, "APPIMAGE": self._appimage(), **env},
                                              desktop_dirs=[self.desktop])

    def test_the_invitation_is_for_the_appimage_and_the_archive_not_yet_in_the_menu(self):
        self.assertTrue(self._wanted())
        self.assertTrue(self._wanted(kind="portable"))

    def test_no_invitation_from_the_deb_package_the_sources_or_windows(self):
        self.assertFalse(self._wanted(kind="deb"))
        self.assertFalse(self._wanted(kind="source"))
        with mock.patch.object(m, "IS_WINDOWS", True):
            self.assertFalse(m.linux_menu_invite_wanted({}, kind="appimage", env={**self.env, "APPIMAGE": self._appimage()}))

    def test_no_invitation_once_installed_in_the_menu_or_after_never_ask_again(self):
        self._install(APPIMAGE=self._appimage())
        self.assertFalse(self._wanted())
        m.linux_menu_uninstall(env=self.env, desktop_dirs=[self.desktop])
        self.assertTrue(self._wanted())
        self.assertFalse(self._wanted({"menu_invite": "never"}))

    def test_uninstall_removes_only_what_the_installation_made_and_keeps_the_users_data(self):
        self._install(APPIMAGE=self._appimage())
        paths = m.linux_menu_paths(self.env)
        config = os.path.join(self.data, "yt-dlp-GUI", "gui-config.json")
        tool = os.path.join(self.data, "yt-dlp-GUI", "yt-dlp")
        for path in (config, tool):
            with open(path, "w") as f:
                f.write("x")
        m.linux_menu_uninstall(self.env, [self.desktop])
        for path in (paths["launcher"], paths["icon"], paths["app_dir"], os.path.join(self.desktop, "yt-dlp-gui.desktop")):
            self.assertFalse(os.path.exists(path), path)
        self.assertTrue(os.path.isfile(config))
        self.assertTrue(os.path.isfile(tool))
        self.assertEqual(m.linux_menu_state(self.env, [self.desktop]), {"installed": False, "shortcut": False})

    def test_uninstall_never_deletes_a_launcher_that_is_not_ours(self):
        foreign = os.path.join(self.desktop, "yt-dlp-gui.desktop")
        with open(foreign, "w") as f:
            f.write("[Desktop Entry]\nName=Autre\n")
        m.linux_menu_uninstall(self.env, [self.desktop])
        self.assertTrue(os.path.isfile(foreign))
        self.assertFalse(m.linux_menu_state(self.env, [self.desktop])["shortcut"])


@unittest.skipUnless(tk_available(), "pas d'affichage Tk disponible")
class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m.load_lang("fr")
        cls.app = m.YtDlpGui()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.desktop = os.path.join(self.tmp, "Desktop")
        os.makedirs(self.desktop)
        self.appimage = os.path.join(self.tmp, "x.AppImage")
        with open(self.appimage, "wb") as f:
            f.write(b"a")
        env = mock.patch.dict(os.environ, {"XDG_DATA_HOME": os.path.join(self.tmp, "data"), "APPIMAGE": self.appimage})
        env.start()
        self.addCleanup(env.stop)
        for patcher in (mock.patch.object(m, "_run_quiet", return_value=""),
                        mock.patch.object(m, "linux_desktop_dirs", return_value=[self.desktop]),
                        mock.patch.object(m, "ICON_PNG", os.path.join(ROOT, "assets", "yt-dlp-gui.png"))):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _window(self, kind="appimage"):
        patcher = mock.patch.object(m, "_install_kind", return_value=kind)
        patcher.start()
        self.addCleanup(patcher.stop)
        win = m.LinuxMenuInstallWindow(self.app)
        win.withdraw()
        self.addCleanup(lambda: win.winfo_exists() and win.destroy())
        return win

    def test_first_open_offers_to_install_with_the_desktop_shortcut_ticked(self):
        win = self._window()
        self.assertEqual(str(win.btn_install.cget("text")), m.t("menu_install.btn_install"))
        self.assertEqual(str(win.btn_remove.cget("state")), "disabled")
        self.assertTrue(win.var_desktop.get())
        self.assertEqual(str(win.lbl_state.cget("text")), m.t("menu_install.state_none"))

    def test_install_then_update_then_remove(self):
        win = self._window()
        win._install()
        self.assertIn(m.t("menu_install.done"), str(win.lbl_result.cget("text")))
        self.assertIn(m.t("menu_install.desktop_added"), str(win.lbl_result.cget("text")))
        self.assertEqual(str(win.btn_install.cget("text")), m.t("menu_install.btn_update"))
        self.assertEqual(str(win.btn_remove.cget("state")), "normal")
        self.assertTrue(os.path.isfile(os.path.join(self.desktop, "yt-dlp-gui.desktop")))
        win._remove()
        self.assertEqual(str(win.lbl_result.cget("text")), m.t("menu_install.removed"))
        self.assertEqual(str(win.btn_install.cget("text")), m.t("menu_install.btn_install"))
        self.assertFalse(os.path.exists(os.path.join(self.desktop, "yt-dlp-gui.desktop")))

    def test_the_deb_package_and_the_sources_get_an_explanation_instead_of_buttons(self):
        for kind, key in (("deb", "menu_install.deb"), ("source", "menu_install.err_source")):
            win = self._window(kind)
            self.assertEqual(str(win.lbl_state.cget("text")), m.t(key))
            self.assertEqual(str(win.btn_install.cget("state")), "disabled")
            self.assertEqual(str(win.btn_remove.cget("state")), "disabled")
        self.assertIn("sudo apt remove yt-dlp-gui", m.t("menu_install.deb"))

    def test_an_error_is_shown_in_the_warning_colour(self):
        win = self._window()
        with mock.patch.object(m, "linux_menu_install", side_effect=m.MenuInstallError("menu_install.err_copy", error="x")):
            win._install()
        self.assertEqual(str(win.lbl_result.cget("fg")), m.WARN_TEXT)
        self.assertIn("x", str(win.lbl_result.cget("text")))

    def test_the_window_stays_small_and_always_shows_its_buttons(self):
        win = self._window()
        win.transient("")
        win.deiconify()
        for _ in range(30):
            self.app.update()
        self.assertLessEqual(win.winfo_reqheight(), 420)
        bottom = win.winfo_rooty() + win.winfo_height()
        for b in (win.btn_install, win.btn_remove):
            self.assertTrue(b.winfo_viewable())
            self.assertLessEqual(b.winfo_rooty() + b.winfo_height(), bottom)

    def _invite(self):
        dlg = m.LinuxMenuInviteDialog(self.app)
        dlg.withdraw()
        self.addCleanup(lambda: dlg.winfo_exists() and dlg.destroy())
        return dlg

    def test_the_invitation_dialog_stays_small_and_always_shows_its_three_buttons(self):
        dlg = self._invite()
        dlg.transient("")
        dlg.deiconify()
        for _ in range(30):
            self.app.update()
        self.assertLessEqual(dlg.winfo_reqheight(), 300)
        bottom = dlg.winfo_rooty() + dlg.winfo_height()
        buttons = [w for w in dlg.winfo_children()[0].winfo_children()[0].winfo_children()]
        self.assertEqual(len(buttons), 3)
        for b in buttons:
            self.assertTrue(b.winfo_viewable())
            self.assertLessEqual(b.winfo_rooty() + b.winfo_height(), bottom)

    def test_yes_opens_the_install_window_later_asks_again_and_never_is_remembered(self):
        config = os.path.join(self.tmp, "gui-config.json")
        with mock.patch.object(m, "CONFIG_FILE", config), mock.patch.object(m, "LinuxMenuInstallWindow") as window:
            dlg = self._invite()
            dlg._answer("yes")
            self.assertEqual(dlg.result, "yes")
            window.assert_called_once_with(self.app)
            self.assertFalse(os.path.exists(config))
            dlg = self._invite()
            dlg._answer("later")
            self.assertEqual(dlg.result, "later")
            self.assertFalse(os.path.exists(config))
            dlg = self._invite()
            dlg._answer("never")
            self.assertEqual(m.load_config().get("menu_invite"), "never")
            self.assertEqual(window.call_count, 1)

    def test_closing_the_dialog_with_the_window_button_counts_as_later(self):
        dlg = self._invite()
        dlg.tk.call(dlg.protocol("WM_DELETE_WINDOW"))
        self.assertEqual(dlg.result, "later")
        self.assertFalse(dlg.winfo_exists())

    def test_the_startup_shows_the_invitation_only_when_it_is_wanted(self):
        for wanted, shown in ((True, 1), (False, 0)):
            with mock.patch.object(m, "linux_menu_invite_wanted", return_value=wanted),                     mock.patch.object(m, "LinuxMenuInviteDialog") as dialog:
                self.app._maybe_menu_invite()
            self.assertEqual(dialog.call_count, shown)

    def test_when_the_setup_wizard_opens_the_invitation_waits_for_it_to_close(self):
        with mock.patch.object(m, "IS_WINDOWS", False), mock.patch.object(m, "SetupWizardWindow") as wizard,                 mock.patch.object(m, "YTDLP", os.path.join(self.tmp, "absent")),                 mock.patch.object(self.app, "_maybe_menu_invite") as invite,                 mock.patch.object(self.app, "after") as after:
            self.app._maybe_first_run()
            invite.assert_not_called()
            sequence, callback = wizard.return_value.bind.call_args[0]
            self.assertEqual(sequence, "<Destroy>")
            callback(mock.Mock(widget=object()))   # un widget enfant de l'assistant : on attend
            after.assert_not_called()
            callback(mock.Mock(widget=wizard.return_value))
            after.assert_called_once()
            self.assertIs(after.call_args[0][1], invite)

    def test_the_startup_invites_right_away_when_the_tools_are_already_there(self):
        with mock.patch.object(m, "SetupWizardWindow") as wizard,                 mock.patch.object(m.os.path, "isfile", return_value=True),                 mock.patch.object(self.app, "_maybe_menu_invite") as invite:
            self.app._maybe_first_run()
        wizard.assert_not_called()
        invite.assert_called_once()

    def test_the_options_menu_offers_it_on_linux_only(self):
        source = _read("yt-dlp-gui.pyw")
        self.assertRegex(source, r"if not IS_WINDOWS:\n\s+menu\.add_command\(label=t\(\"toolbar\.menu_install_menu\"\), "
                                 r"command=lambda: LinuxMenuInstallWindow\(self\)\)")


class TranslationsTests(unittest.TestCase):
    KEYS = ["toolbar.menu_install_menu", "menu_install.title", "menu_install.explain", "menu_install.cb_desktop",
            "menu_install.state_none", "menu_install.state_installed", "menu_install.btn_install",
            "menu_install.btn_update", "menu_install.btn_remove", "menu_install.done",
            "menu_install.desktop_added", "menu_install.desktop_missing", "menu_install.removed",
            "menu_install.err_source", "menu_install.deb", "menu_install.err_copy", "menu_invite.title",
            "menu_invite.text", "menu_invite.btn_yes", "menu_invite.btn_later", "menu_invite.btn_never"]

    def test_every_text_exists_in_every_language_with_its_placeholders(self):
        names = sorted(n for n in os.listdir(LANG_DIR) if n.endswith(".json"))
        self.assertEqual(len(names), 15)
        for name in names:
            with open(os.path.join(LANG_DIR, name), encoding="utf-8") as f:
                data = json.load(f)
            for key in self.KEYS:
                self.assertTrue(data[key].strip(), (name, key))
            self.assertIn("{path}", data["menu_install.state_installed"], name)
            self.assertIn("{error}", data["menu_install.err_copy"], name)
            self.assertIn("sudo apt remove yt-dlp-gui", data["menu_install.deb"], name)
            self.assertIn("yt-dlp GUI", data["menu_install.done"], name)


class DebPackageTests(unittest.TestCase):
    def test_architecture_and_file_name_follow_debian_conventions(self):
        self.assertEqual(bd.deb_arch("x86_64"), "amd64")
        self.assertEqual(bd.deb_arch("AMD64"), "amd64")
        self.assertEqual(bd.deb_arch("aarch64"), "arm64")
        with self.assertRaises(SystemExit):
            bd.deb_arch("riscv64")
        self.assertEqual(bd.deb_name("0.1.1", "amd64"), "yt-dlp-gui_0.1.1_amd64.deb")

    def test_the_file_name_is_what_the_update_check_and_the_release_look_for(self):
        import fnmatch
        name = bd.deb_name("0.2.0", "amd64")
        self.assertTrue(fnmatch.fnmatch(name, m.release_asset_patterns(False, "x86_64")["deb"]))
        self.assertFalse(fnmatch.fnmatch(name, m.release_asset_patterns(False, "aarch64")["deb"]))
        self.assertTrue(any(fnmatch.fnmatch(name, p) for p in rt.LINUX_ARTIFACT_PATTERNS))
        self.assertFalse(any(fnmatch.fnmatch(name, p) for p in rt.ARTIFACT_PATTERNS))

    def test_the_control_file_is_well_formed(self):
        text = bd.control_text("0.1.1", "amd64", 123)
        self.assertTrue(text.endswith("\n"))
        fields = dict(re.findall(r"^([A-Za-z-]+): (.*)$", text, re.M))
        for key, value in (("Package", "yt-dlp-gui"), ("Version", "0.1.1"), ("Architecture", "amd64"),
                           ("Installed-Size", "123"), ("Section", "video"), ("Priority", "optional")):
            self.assertEqual(fields[key], value)
        self.assertIn("libc6 (>= 2.35)", fields["Depends"])
        self.assertIn("@", fields["Maintainer"])
        description = text.split("Description:", 1)[1].splitlines()[1:]
        self.assertTrue(description and all(line.startswith(" ") for line in description if line != ""))
        self.assertIn(" .", description, "séparateur de paragraphe de la description")

    def _fake_app(self):
        app = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, app, ignore_errors=True)
        os.makedirs(os.path.join(app, "_internal"))
        for name in ("yt-dlp-gui", "_internal/libx.so", "LICENSE", "README.md", "CHANGELOG-linux.md"):
            with open(os.path.join(app, name), "wb") as f:
                f.write(name.encode())
        os.chmod(os.path.join(app, "yt-dlp-gui"), 0o755)
        return app

    def test_the_tree_has_the_expected_layout(self):
        app = self._fake_app()
        root = os.path.join(tempfile.mkdtemp(), "deb-root")
        self.addCleanup(shutil.rmtree, os.path.dirname(root), ignore_errors=True)
        links = []
        with mock.patch.object(bd.os, "symlink", side_effect=lambda target, path: links.append((target, path))):
            bd.stage_tree(app, root, "0.1.1", "amd64")
        exists = lambda *p: os.path.exists(os.path.join(root, *p))
        self.assertTrue(exists("opt", "yt-dlp-gui", "yt-dlp-gui"))
        self.assertTrue(exists("opt", "yt-dlp-gui", "_internal", "libx.so"))
        for doc in bd.DOC_FILES:
            self.assertFalse(exists("opt", "yt-dlp-gui", doc), f"{doc} va sous /usr/share/doc")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][0], "../../opt/yt-dlp-gui/yt-dlp-gui")
        self.assertEqual(os.path.normpath(links[0][1]), os.path.normpath(os.path.join(root, "usr", "bin", "yt-dlp-gui")))
        desktop = _text(os.path.join(root, "usr", "share", "applications", "yt-dlp-gui.desktop"))
        self.assertIn("Exec=yt-dlp-gui\n", desktop.replace("\r\n", "\n"))
        self.assertIn("Icon=yt-dlp-gui", desktop)
        self.assertTrue(exists("usr", "share", "icons", "hicolor", "256x256", "apps", "yt-dlp-gui.png"))
        copyright_text = _text(os.path.join(root, "usr", "share", "doc", "yt-dlp-gui", "copyright"))
        self.assertIn("MIT License", copyright_text)
        with gzip.open(os.path.join(root, "usr", "share", "doc", "yt-dlp-gui", "changelog.gz"), "rb") as f:
            self.assertEqual(f.read(), _text(os.path.join(ROOT, "CHANGELOG-linux.md"), "rb"))
        control = _text(os.path.join(root, "DEBIAN", "control"))
        self.assertIn("Package: yt-dlp-gui\nVersion: 0.1.1\nArchitecture: amd64\n", control)

    def test_md5sums_list_every_regular_file_but_not_the_control_files(self):
        app = self._fake_app()
        root = os.path.join(tempfile.mkdtemp(), "deb-root")
        self.addCleanup(shutil.rmtree, os.path.dirname(root), ignore_errors=True)
        with mock.patch.object(bd.os, "symlink"):
            bd.stage_tree(app, root, "0.1.1", "amd64")
        lines = _text(os.path.join(root, "DEBIAN", "md5sums")).splitlines()
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"^[0-9a-f]{32}  [^/].*[^/]$")
            self.assertFalse(line.split("  ", 1)[1].startswith("DEBIAN"))
        names = [line.split("  ", 1)[1] for line in lines]
        self.assertIn("opt/yt-dlp-gui/yt-dlp-gui", names)
        self.assertIn("usr/share/doc/yt-dlp-gui/copyright", names)

    def test_the_build_refuses_a_folder_without_the_program(self):
        empty = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty, ignore_errors=True)
        with self.assertRaises(SystemExit) as ctx:
            bd.build_deb(empty, empty, empty)
        self.assertIn("build_linux.py", str(ctx.exception))

    def test_the_release_workflow_builds_and_publishes_the_deb(self):
        flow = _read(".github", "workflows", "release.yml")
        self.assertIn("packaging/build_deb.py", flow)
        self.assertEqual(flow.count("dist/yt-dlp-gui_*_amd64.deb"), 4, "info + contents + téléversement + release")

    def test_checksums_include_the_deb(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for name in ("yt-dlp-gui-9.0.0-x86_64.AppImage", "yt-dlp-gui-linux-9.0.0-x86_64.tar.gz",
                     "yt-dlp-gui_9.0.0_amd64.deb", "notes.md"):
            with open(os.path.join(d, name), "wb") as f:
                f.write(name.encode())
        out = os.path.join(d, "SHA256SUMS-linux.txt")
        names = rt.write_checksums(d, out, rt.LINUX_ARTIFACT_PATTERNS)
        self.assertIn("yt-dlp-gui_9.0.0_amd64.deb", names)
        self.assertNotIn("notes.md", names)


if __name__ == "__main__":
    unittest.main()
