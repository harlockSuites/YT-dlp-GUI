# yt-dlp GUI — Linux version

[Français](../README-LINUX.md) · [English](README-LINUX.en.md)

> **Preview.** This document complements the [main README](README.en.md): it is the same software, but here we only cover what is specific to Linux (installation, cookies and key rings, files, troubleshooting). What is new in each version is listed in [CHANGELOG-linux.md](../CHANGELOG-linux.md). Other languages will follow once the French and English texts have been reviewed.

## Contents

1. [State of the preview](#1-state-of-the-preview)
2. [Installing](#2-installing)
3. [First launch and dependencies](#3-first-launch-and-dependencies)
4. [Browser cookies](#4-browser-cookies)
5. [Key rings: manual operations](#5-key-rings-manual-operations)
6. [Where the files are](#6-where-the-files-are)
7. [Troubleshooting](#7-troubleshooting)
8. [Reporting a bug](#8-reporting-a-bug)
9. [For developers](#9-for-developers)

## 1. State of the preview

The Linux version reproduces the behaviour of the Windows version 0.1.7 (frozen, used as the model). It is published as a **GitHub pre-release** under `Linux-vX.Y.Z` tags: it is never presented as the repository's "latest release".

**What has been tried** (Debian 12 virtual machine, GNOME desktop, Python 3.11, a real YouTube account signed in to each browser, October 2026):

- **Cookies of Firefox, Waterfox, Floorp and Zen Browser**: read with the browser open or closed.
- **Cookies of Google Chrome, Chromium, Brave, Vivaldi, Opera and Microsoft Edge**: read with the browser **closed**, after starting each browser once and signing in to YouTube in it (see [section 5](#5-key-rings-manual-operations)). Single download and Playlist Inspector both succeeded.
- **LibreWolf**: read only while it is open and signed in (it deletes its cookies when it closes by default).
- **Private video** with Firefox's cookies, and a playlist of three videos with one private.
- **Packages**: the AppImage and the `.tar.gz` archive are built by the CI on Ubuntu 22.04; the `.deb` was built, installed, started and removed on Debian 12; "Install in the menu" was tried with the real AppImage in a disposable home folder.

**What has not been tried yet**:

- other distributions (Ubuntu, Fedora, Arch, openSUSE…) and desktops other than GNOME, including KDE Plasma (KWallet);
- browsers installed as Flatpak or Snap (except the LibreWolf Flatpak layout, which was observed);
- Vivaldi, Opera or Edge **without** Chrome or Chromium installed (see [section 5](#5-key-rings-manual-operations));
- the aarch64 architecture (the software supports it, but packages are only built for x86_64);
- the "Install in the menu" window driven with the mouse on a real desktop (it is tested programmatically);
- the translations: they still need review by native speakers.

## 2. Installing

### Which format to choose

| Format | For whom | Administrator rights | Menu entry |
|---|---|---|---|
| **AppImage** | any recent 64-bit distribution | no | "Install in the menu" (section 2.3) |
| **`.tar.gz` archive** | same, without AppImage or FUSE | no | "Install in the menu" |
| **`.deb` package** | Debian, Ubuntu and derivatives | yes (`sudo`) | automatic |
| **Source files** | developers, testing | no | none |

Requirements: 64-bit Linux (x86_64) from a 2022 or newer distribution (glibc 2.35 or later), because the packages are built on Ubuntu 22.04.

**If you are new to Linux**: only the `.deb` package is installed "for real" and shows up in the software manager. The AppImage and the archive are ordinary files or folders, kept wherever you like: to remove them, you delete them like any other file (sections 2.2 and 2.5). Their settings are kept apart, in `~/.local/share/yt-dlp-GUI` (section 6), and survive that deletion.

Files are on the [releases page](https://github.com/harlockSuites/YT-dlp-GUI/releases): look for the `Linux-v…` tags, marked "Pre-release".

### 2.1 Verifying the download

Also download `SHA256SUMS-linux.txt` into the same folder, then:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Each file present must show `OK`. This proves that your file is identical to the published one, not that it is harmless: the source code and the automated build are public.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

The AppImage needs the FUSE 2 library:

| Distribution | Package |
|---|---|
| Debian, Ubuntu 22.04 and derivatives | `libfuse2` |
| Ubuntu 24.04 and newer | `libfuse2t64` |
| Fedora | `fuse-libs` |

Without FUSE, start it anyway; it extracts itself into a temporary folder:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

The AppImage is not "installed": it does not show up in the software manager. To remove it, delete the file:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

### 2.3 Install in the menu (no administrator)

An AppImage started with a double click leaves no icon in the applications menu. In the software: options menu › **"Install in the menu…"**. The window:

- copies the program to `~/.local/share/yt-dlp-GUI/app/`;
- writes the launcher `~/.local/share/applications/yt-dlp-gui.desktop` and the icon `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- adds, if the box is ticked, a shortcut on the Desktop (marked "trusted" for GNOME when the `gio` tool exists);
- then offers "Update" (it copies the version that is running) and "Uninstall".

"Uninstall" only removes what the installation created and **keeps your settings** and downloaded tools. A launcher without our internal marker (`X-YtDlpGui-Installer=1`) is never deleted.

Limits: the window is available from the AppImage and the archive. From source files it points you to the AppImage; from the `.deb` package it explains that the software is already in the menu.

If the Desktop shortcut shows a warning: right-click the icon › "Allow Launching". Some desktops (GNOME by default) do not show icons on the Desktop: the menu launcher works in every case.

To remove everything by hand:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 `.deb` package

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

The program goes to `/opt/yt-dlp-gui`, with the link `/usr/bin/yt-dlp-gui`, the menu launcher, the icon and the licence (`/usr/share/doc/yt-dlp-gui/`). It depends on `libc6 (>= 2.35)` and `libx11-6`.

To remove it (your settings, in `~/.local/share/yt-dlp-GUI`, are never touched):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 `.tar.gz` archive

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

To keep settings and tools **inside the extracted folder** (USB stick, trace-free test), create an empty `portable.flag` file next to the executable:

```bash
touch yt-dlp-gui/portable.flag
```

Without this file, data goes to `~/.local/share/yt-dlp-GUI` (section 6).

The archive is not "installed": it does not show up in the software manager. To remove it, delete the extracted folder:

```bash
rm -rf yt-dlp-gui
```

### 2.6 From source files

```bash
python3 yt-dlp-gui.pyw
```

From source files, settings and downloaded tools go to the same folder as for the installed versions (`~/.local/share/yt-dlp-GUI`): downloading the sources again or deleting their folder does not erase them. To keep the data inside the sources folder (trace-free test), create an empty `portable.flag` file next to `yt-dlp-gui.pyw`.

You need Python 3 with Tkinter:

| Distribution | Package |
|---|---|
| Debian, Ubuntu and derivatives, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Updates

A daily check (which can be turned off in the options menu) looks for `Linux-vX.Y.Z` versions, pre-releases included, and **never** offers a Windows version. It opens the download page of the file that matches your installation (AppImage, archive or `.deb`); **nothing is installed automatically**. To update:

- **AppImage or archive installed in the menu**: download the new AppImage, start it, then "Install in the menu… › Update";
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **archive that is not installed**: extract the new archive in place of the old one.

### 2.8 Removing everything, data included

After removing the program (sections 2.3 to 2.5), to also erase your settings, the queue and the downloaded tools (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Your downloaded videos are never in this folder.

## 3. First launch and dependencies

On first launch, the setup assistant offers to download **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (the `.tar.xz` archive of yt-dlp's official builds) and **deno** from their GitHub repositories. SHA-256 sums are verified, no administrator rights are requested, and the files go to `~/.local/share/yt-dlp-GUI` (yt-dlp) and `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). It stays available in the options menu.

Only ffmpeg and ffprobe are essential; deno is recommended (secondary audio tracks). **AtomicParsley, MKVToolNix and aria2** are optional: the "Dependencies" window shows the command of your package manager, to copy into a terminal. The software never runs it itself. The same commands:

| Package manager | Command |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

## 4. Browser cookies

yt-dlp reads cookies **locally**, in the browser you choose (secondary audio tracks, subtitles, private videos, members-only content). By default, the software offers the five most used browsers on Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). The **"Cookie browsers…"** entry of the options menu opens the "Browsers for cookies" window, which offers 11: tick those you need; a ✔ marks those whose profile folder exists on your computer.

| Browser | Read by yt-dlp as | Key ring | Profile folders searched |
|---|---|---|---|
| Firefox | `firefox` | no | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | yes | `~/.config/google-chrome` |
| Chromium | `chromium` | yes | `~/.config/chromium` |
| Brave | `brave` | yes | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | yes | `~/.config/vivaldi` |
| Opera | `opera` | yes | `~/.config/opera` |
| Microsoft Edge | `edge` | yes | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + profile folder | no | `~/.librewolf`, `~/.config/librewolf`… (same pattern for the others), Flatpak included |

Firefox derivatives have no name known to yt-dlp: the software looks for their `cookies.sqlite` database (up to three levels below their folders) and gives yt-dlp the folder of the most recently used profile. `XDG_CONFIG_HOME` is honoured when it is absolute.

The **indicator** next to the list shows the state: red (disabled or failed), orange (not tested or in progress), green (cookies read). The ↻ button runs a test; the tooltip explains the error. A test that reads **0 cookies** is never green.

### Frequent cases

| What you see | Probable cause | What to do |
|---|---|---|
| "Extracted 0 cookies" then "Sign in to confirm you're not a bot" | the browser keeps no cookie on disk (LibreWolf deletes them when it closes by default; profile never signed in; private mode) | keep it open and signed in to YouTube, or turn off cookie deletion on close in its privacy settings |
| "Item does not exist!" with Chrome, Chromium, Brave, Vivaldi, Opera or Edge | yt-dlp did not find the browser's key in the desktop key ring | start the browser once, sign in to YouTube, close it, run the test again; otherwise [section 5](#5-key-rings-manual-operations) |
| "Could not copy Chrome cookie database" or "database is locked" | the browser locks its database while running | close it, then run the test again |
| "Failed to decrypt" | cookies encrypted with a key that yt-dlp did not get | [section 5](#5-key-rings-manual-operations) |

### Testing a browser from a terminal

This is the best way to see the exact error (replace `IDENTIFIER` with the identifier of any YouTube video):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Lines to look for: `Extracted N cookies from chromium` (N must be greater than 0), `Chosen keyring: GNOMEKEYRING` (the key ring that was chosen), and `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (`v11` cookies need the key ring, `v10` ones do not).

For a Firefox derivative, give the profile folder. To find it:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

In a Flatpak installation, search in `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Then, with the folder that contains `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

## 5. Key rings: manual operations

### What it is for

Chromium-family browsers (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) encrypt their cookies. The encryption key is stored in the **desktop key ring**: GNOME Keyring (or a compatible equivalent, through the "Secret Service") under GNOME, XFCE, Cinnamon, MATE…, KWallet under KDE. To decrypt, yt-dlp asks the key ring for that key. Firefox and its derivatives do not need it.

Two useful facts:

- **The key only exists after the browser has been started once.** In our virtual machine, the "Item does not exist!" error went away once each browser had been started once and signed in to YouTube. The exact cause of the first failure was not established with certainty: the key ring existed, was the default and was unlocked.
- **Which key ring yt-dlp uses** depends on the detected desktop (the `XDG_CURRENT_DESKTOP` and `DESKTOP_SESSION` variables), according to yt-dlp's code (October 2026):

| Detected desktop | Key ring used by yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, unrecognised desktop (window managers alone: sway, i3…) | none: plain text (`BASICTEXT`) |

In the last case, yt-dlp only reads `v10` cookies: if your browser stores its key in GNOME Keyring, its `v11` cookies will not be decrypted. You then have to force the key ring from a terminal (section 5.6); the software does not offer this setting yet.

The items looked up in the key ring are called "*name* Safe Storage". According to yt-dlp's code, that is **"Chrome Safe Storage"** for Chrome and Vivaldi, **"Chromium Safe Storage"** for Chromium, Opera and Edge, **"Brave Safe Storage"** for Brave. In our virtual machine, Chrome and Chromium were also installed and started: we do not know whether Vivaldi, Opera or Edge would work alone.

### 5.1 Does the key ring exist?

```bash
ls -la ~/.local/share/keyrings/
```

You should see a `login.keyring` file (the "login" key ring). Next, which key ring is the **default** one?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Answer `(objectpath '/org/freedesktop/secrets/collection/login',)`: there is a default key ring. Answer `'/'`: **none**, go to section 5.4.

### 5.2 Is it locked?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: unlocked. `(<true>,)`: locked; open it with Seahorse (section 5.4), which asks for its password.

### 5.3 Is my browser's key in it?

List the items:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

The answer gives paths ending with a number (`…/login/1`, `…/login/2`…). To read the name of each one (adapt the list of numbers):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

You should see, for example, `Chromium Safe Storage`, `Chrome Safe Storage` or `Brave Safe Storage`. Empty names are harmless. If your browser's name is missing: start it once, sign in to YouTube, close it, then run this command again.

### 5.4 Create or unlock a key ring with Seahorse

Install Seahorse ("Passwords and Keys") and the related tools. The exact command is also in the software's "Browsers for cookies" window:

| Package manager | Command |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Then open it:

```bash
seahorse
```

- **No default key ring**: create one ("+" button or File › New › password keyring), name it "Login", then right-click it › "Set as default". Exact labels vary with the Seahorse version.
- **Locked key ring**: double-click or right-click › "Unlock", then type its password (type it yourself, the software never asks for it).
- **Automatic login**: a key ring protected by a password cannot open by itself if you type no password when the session starts; it stays locked until you unlock it (or until you use the same password for the session and for the key ring).

Then **start the browser, sign in to YouTube, close it**, and run the test again (section 4).

### 5.5 KDE Plasma (KWallet)

Under KDE, yt-dlp queries KWallet (`kwallet-query`). The manager is called `kwalletmanager` (or `kwalletmanager5`) depending on the distribution. This setup **has not been tried** in our tests.

### 5.6 Forcing the key ring on yt-dlp (terminal)

The software lets yt-dlp choose the key ring according to the desktop. To force it, add `+KEYRING` to the browser name (values: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

To know which key ring a Chromium really uses (command taken from yt-dlp's code, not tried here):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Without a key ring: `--password-store=basic` (advanced, not tried)

Chromium accepts `--password-store=basic`: it then stores its key in clear (a fixed, well-known key) and encrypts its new cookies as `v10`, which yt-dlp reads without a key ring (`chromium+basictext`). **This is less safe**: any program that can read your files can decrypt these cookies. Only use it if you understand this trade-off; cookies already saved are probably not re-encoded: sign in again.

### 5.8 Last resort

If a key ring is corrupted, **back it up first**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Deleting `login.keyring` erases **all** the passwords it holds (Wi-Fi, online accounts…): do not do it without understanding the consequences.

## 6. Where the files are

The data folder is `$XDG_DATA_HOME/yt-dlp-GUI` (by default `~/.local/share/yt-dlp-GUI`), unless `portable.flag` sits next to the archive's executable (or the `yt-dlp-gui.pyw` script).

| File or folder | Content |
|---|---|
| `gui-config.json` | settings (language, browser, folders, browser choice…) |
| `download-queue.json` | download queue |
| `custom-blocks.json` | custom option blocks |
| `yt-dlp` | executable downloaded by the assistant |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | temporary yt-dlp configuration files |
| `app/` | copy of the program made by "Install in the menu" |

## 7. Troubleshooting

| Problem | Lead |
|---|---|
| The AppImage does not start | start it from a terminal to read the error; install FUSE 2 (section 2.2) or add `--appimage-extract-and-run` |
| Nothing shows, or a library error | check the glibc version: `ldd --version` must say 2.35 or later |
| No icon on the Desktop | GNOME shows none by default; use the applications menu |
| Desktop shortcut with a warning | right-click › "Allow Launching" |
| Drag and drop between the host and a virtual machine does not work | that is a VirtualBox feature (Guest Additions), not the software's |
| The interface is badly sized | the software follows the system fonts (Tk); try another system font size |
| The yt-dlp update fails | use "Update & Diagnostics" in the options menu; otherwise download `yt-dlp_linux` and pick it in the replacement window (the chosen file is made executable) |

## 8. Reporting a bug

The "Report a bug" button prepares a technical report in which your folders, user name and e-mail addresses are masked; nothing is sent automatically. For Linux, add to it:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

and say **how** you installed the software (AppImage, archive, `.deb`, source files) and, for a cookie problem, **the result of the terminal test** (section 4), without pasting your cookies.

## 9. For developers

Tests (under a virtual display, no real screen needed):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Building the packages (build tools: `pip install -r packaging/requirements-build.txt`, plus `appimagetool`, whose path is given by the `APPIMAGETOOL` variable):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Results are in `dist/`. For best compatibility, build on the oldest supported distribution (the build machine's glibc is the minimum required of the machines that run the program). Useful checks of the `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

The only known form error is `dir-or-file-in-opt` (program bundled in `/opt`).

**Publishing**: check `__version__` in `yt-dlp-gui.pyw`, date the version's section in `CHANGELOG-linux.md`, commit, then create and push the `Linux-vX.Y.Z` tag. The "Release Linux" workflow runs the tests, builds the AppImage, the archive and the `.deb`, computes the sums and creates the release as a **pre-release**, never "latest release" (the update check of the Windows version 0.1.7 must not find a Linux tag there).

Licence: MIT, like the rest of the repository (see [LICENSE](../LICENSE)).
