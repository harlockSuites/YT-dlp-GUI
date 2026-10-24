# yt-dlp GUI — bersyon para sa Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Preview.** Dinadagdagan ng dokumentong ito ang [pangunahing README](README.fil.md): iisang software ito, pero dito ay ang mga bagay na tiyak lang sa Linux ang tinatalakay (pag-install, mga cookie at key ring, mga file, pag-troubleshoot). Ang mga bago sa bawat bersyon ay nasa [CHANGELOG-linux.md](../CHANGELOG-linux.md). Kailangan pang suriin ng mga katutubong nagsasalita ang mga salin; kapag may duda, ang mga tekstong Pranses at Ingles ang masusunod.

## Nilalaman

1. [Kalagayan ng preview](#s1)
2. [Pag-install](#s2)
3. [Unang paglunsad at mga dependency](#s3)
4. [Mga cookie ng browser](#s4)
5. [Mga key ring: mano-manong gawain](#s5)
6. [Kung nasaan ang mga file](#s6)
7. [Pag-troubleshoot](#s7)
8. [Pag-uulat ng bug](#s8)
9. [Para sa mga developer](#s9)

<a id="s1"></a>

## 1. Kalagayan ng preview

Ginagaya ng bersyon para sa Linux ang kilos ng bersyon para sa Windows na 0.1.7 (naka-freeze at ginagamit na modelo). Inilalathala ito bilang **GitHub pre-release** na may mga tag na `Linux-vX.Y.Z`: hindi ito kailanman ipinapakita bilang "pinakabagong release" ng repository.

**Ang mga nasubukan na** (Debian 12 virtual machine, GNOME desktop, Python 3.11, totoong YouTube account na naka-sign in sa bawat browser, Oktubre 2026):

- **Mga cookie ng Firefox, Waterfox, Floorp at Zen Browser**: nababasa kahit bukas o sarado ang browser.
- **Mga cookie ng Google Chrome, Chromium, Brave, Vivaldi, Opera at Microsoft Edge**: nababasa kapag **sarado** ang browser, matapos buksan nang minsan ang bawat browser at mag-sign in sa YouTube dito (tingnan ang [seksyon 5](#s5)). Parehong nagtagumpay ang single download at ang Playlist Inspector.
- **LibreWolf**: nababasa lang habang bukas ito at naka-sign in (bilang default, binubura nito ang mga cookie nito kapag isinara).
- **Pribadong video** gamit ang mga cookie ng Firefox, at isang playlist ng tatlong video na may isang pribado.
- **Mga package**: ang AppImage at ang `.tar.gz` archive ay binubuo ng CI sa Ubuntu 22.04; ang `.deb` ay binuo, ini-install, pinatakbo at inalis sa Debian 12; sinubukan ang "I-install sa menu" gamit ang totoong AppImage sa isang disposable na home folder.

**Ang hindi pa nasusubukan**:

- ibang mga distribution (Ubuntu, Fedora, Arch, openSUSE…) at mga desktop na hindi GNOME, kasama ang KDE Plasma (KWallet);
- mga browser na naka-install bilang Flatpak o Snap (maliban sa layout ng LibreWolf sa Flatpak, na naobserbahan);
- Vivaldi, Opera o Edge na **walang** naka-install na Chrome o Chromium (tingnan ang [seksyon 5](#s5));
- ang aarch64 architecture (sinusuportahan ito ng software, pero x86_64 lang ang binubuong package);
- ang window na "I-install sa menu" na ginamitan ng mouse sa totoong desktop (sinusubok ito sa pamamagitan ng programa);
- ang mga salin: kailangan pa silang suriin ng mga katutubong nagsasalita.

<a id="s2"></a>

## 2. Pag-install

### Aling format ang pipiliin

| Format | Para kanino | Karapatan ng administrator | Entry sa menu |
|---|---|---|---|
| **AppImage** | anumang bagong 64-bit na distribution | hindi | "I-install sa menu" (seksyon 2.3) |
| **`.tar.gz` archive** | pareho, nang walang AppImage o FUSE | hindi | "I-install sa menu" |
| **`.deb` package** | Debian, Ubuntu at mga hango nito | oo (`sudo`) | awtomatiko |
| **Source code** | mga developer, pagsubok | hindi | wala |

Mga kinakailangan: 64-bit na Linux (x86_64) mula sa distribution na 2022 o mas bago (glibc 2.35 o mas mataas), dahil binubuo ang mga package sa Ubuntu 22.04.

**Kung bago ka sa Linux**: ang `.deb` package lang ang ini-install nang "totoo" at lumalabas sa software manager. Ang AppImage at ang archive ay karaniwang mga file o folder, na maaari mong ilagay saan mo gusto: para alisin ang mga ito, buburahin mo lang tulad ng alinmang file (mga seksyon 2.2 at 2.5). Hiwalay ang mga setting nila, sa `~/.local/share/yt-dlp-GUI` (seksyon 6), at nananatili ang mga ito kahit burahin sila.

Nasa [pahina ng mga release](https://github.com/harlockSuites/YT-dlp-GUI/releases) ang mga file: hanapin ang mga tag na `Linux-v…`, na may markang "Pre-release".

### 2.1 Pag-verify ng download

I-download din ang `SHA256SUMS-linux.txt` sa parehong folder, pagkatapos:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Dapat magpakita ng `OK` ang bawat file na naroon. Pinatutunayan nito na kapareho ng inilathala ang file mo, hindi na ligtas ito: pampubliko ang source code at ang awtomatikong build.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Kailangan ng AppImage ang FUSE 2 library:

| Distribution | Package |
|---|---|
| Debian, Ubuntu 22.04 at mga hango | `libfuse2` |
| Ubuntu 24.04 at mas bago | `libfuse2t64` |
| Fedora | `fuse-libs` |

Kahit walang FUSE, patakbuhin pa rin ito: kusa itong nag-e-extract sa isang pansamantalang folder:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

Hindi "ini-install" ang AppImage: hindi ito lumalabas sa software manager. Para alisin ito, burahin ang file:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

### 2.3 I-install sa menu (walang administrator)

Ang AppImage na pinatakbo sa pamamagitan ng double click ay hindi nag-iiwan ng icon sa menu ng mga application. Sa software: menu ng mga opsyon › **"I-install sa menu…"**. Ang window na ito ay:

- kinokopya ang programa sa `~/.local/share/yt-dlp-GUI/app/`;
- isinusulat ang launcher na `~/.local/share/applications/yt-dlp-gui.desktop` at ang icon na `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- nagdaragdag, kung may tsek ang kahon, ng shortcut sa Desktop (minamarkahang "pinagkakatiwalaan" para sa GNOME kapag mayroong tool na `gio`);
- pagkatapos ay nag-aalok ng "I-update" (kinokopya ulit ang bersyong tumatakbo) at "I-uninstall".

Ang "I-uninstall" ay inaalis lang ang ginawa ng pag-install at **pinananatili ang mga setting mo** at ang mga na-download na tool. Ang launcher na walang sarili naming panloob na marka (`X-YtDlpGui-Installer=1`) ay hindi kailanman binubura.

Mga limitasyon: available ang window mula sa AppImage at sa archive. Mula sa source code, itinuturo ka nito sa AppImage; mula sa `.deb` package, ipinapaliwanag nitong nasa menu na ang software.

Kung may babala ang shortcut sa Desktop: i-right-click ang icon › "Allow Launching". May mga desktop (ang GNOME bilang default) na hindi nagpapakita ng mga icon sa Desktop: gumagana sa lahat ng kaso ang launcher sa menu.

Para alisin ang lahat nang mano-mano:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 `.deb` package

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Napupunta ang programa sa `/opt/yt-dlp-gui`, kasama ang link na `/usr/bin/yt-dlp-gui`, ang launcher sa menu, ang icon at ang lisensya (`/usr/share/doc/yt-dlp-gui/`). Nakadepende ito sa `libc6 (>= 2.35)` at `libx11-6`.

Para alisin ito (hindi kailanman ginagalaw ang mga setting mo, na nasa `~/.local/share/yt-dlp-GUI`):

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

Para manatili ang mga setting at tool **sa loob ng na-extract na folder** (USB stick, pagsubok na walang iniiwang bakas), gumawa ng walang lamang file na `portable.flag` sa tabi ng executable:

```bash
touch yt-dlp-gui/portable.flag
```

Kung wala ang file na ito, napupunta ang data sa `~/.local/share/yt-dlp-GUI` (seksyon 6).

Hindi "ini-install" ang archive: hindi ito lumalabas sa software manager. Para alisin ito, burahin ang na-extract na folder:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Mula sa source code

```bash
python3 yt-dlp-gui.pyw
```

Mula sa source code, napupunta ang mga setting at na-download na tool sa parehong folder ng mga naka-install na bersyon (`~/.local/share/yt-dlp-GUI`): hindi sila nabubura kapag ida-download ulit ang source code o buburahin ang folder nito. Para manatili ang data sa loob ng folder ng source code (pagsubok na walang iniiwang bakas), gumawa ng walang lamang file na `portable.flag` sa tabi ng `yt-dlp-gui.pyw`.

Kailangan ang Python 3 na may Tkinter:

| Distribution | Package |
|---|---|
| Debian, Ubuntu at mga hango, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Mga update

Ang pang-araw-araw na pagsusuri (na maaaring patayin sa menu ng mga opsyon) ay naghahanap ng mga bersyong `Linux-vX.Y.Z`, kasama ang mga pre-release, at **hindi kailanman** nagmumungkahi ng bersyon para sa Windows. Binubuksan nito ang pahina ng download ng file na tumutugma sa pag-install mo (AppImage, archive o `.deb`); **walang awtomatikong ini-install**. Para mag-update:

- **AppImage o archive na naka-install sa menu**: i-download ang bagong AppImage, patakbuhin ito, pagkatapos ay "I-install sa menu… › I-update";
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **archive na hindi naka-install**: i-extract ang bagong archive sa halip ng luma.

### 2.8 Pag-alis ng lahat, pati ang data

Pagkatapos alisin ang programa (mga seksyon 2.3 hanggang 2.5), para mabura rin ang mga setting mo, ang queue at ang mga na-download na tool (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Hindi kailanman nasa folder na ito ang mga na-download mong video.

<a id="s3"></a>

## 3. Unang paglunsad at mga dependency

Sa unang paglunsad, iminumungkahi ng setup assistant na i-download ang **yt-dlp** (`yt-dlp_linux`), ang **ffmpeg** (ang `.tar.xz` archive ng mga opisyal na build ng yt-dlp) at ang **deno** mula sa kanilang mga GitHub repository. Bine-verify ang mga SHA-256 sum, hindi hinihingi ang karapatan ng administrator, at napupunta ang mga file sa `~/.local/share/yt-dlp-GUI` (yt-dlp) at `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Nananatili itong available sa menu ng mga opsyon.

Ang ffmpeg at ffprobe lang ang kailangang-kailangan; inirerekomenda ang deno (para sa pangalawang audio track). Opsyonal ang **AtomicParsley, MKVToolNix at aria2**: ipinapakita ng window na "Mga Dependency" ang command ng package manager mo, na kokopyahin sa terminal. Hindi ito kailanman pinapatakbo ng software nang mag-isa. Ang parehong mga command:

| Package manager | Command |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Mga cookie ng browser

Binabasa ng yt-dlp ang mga cookie **nang lokal**, sa browser na pipiliin mo (mga pangalawang audio track, subtitle, pribadong video, nilalamang para sa mga miyembro). Bilang default, iminumungkahi ng software ang limang pinakaginagamit na browser sa Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). Ang entry na **"Mga browser para sa cookies…"** sa menu ng mga opsyon ay nagbubukas ng window na "Mga browser para sa cookies", na nag-aalok ng 11: lagyan ng tsek ang mga kailangan mo; minamarkahan ng ✔ ang mga browser na may profile folder sa computer mo.

| Browser | Binabasa ng yt-dlp bilang | Key ring | Mga profile folder na hinahanap |
|---|---|---|---|
| Firefox | `firefox` | hindi | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | oo | `~/.config/google-chrome` |
| Chromium | `chromium` | oo | `~/.config/chromium` |
| Brave | `brave` | oo | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | oo | `~/.config/vivaldi` |
| Opera | `opera` | oo | `~/.config/opera` |
| Microsoft Edge | `edge` | oo | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + profile folder | hindi | `~/.librewolf`, `~/.config/librewolf`… (parehong pattern para sa iba), kasama ang Flatpak |

Walang pangalang kilala ng yt-dlp ang mga hango ng Firefox: hinahanap ng software ang kanilang `cookies.sqlite` database (hanggang tatlong antas sa ilalim ng kanilang mga folder) at ibinibigay sa yt-dlp ang folder ng pinakabagong ginamit na profile. Iginagalang ang `XDG_CONFIG_HOME` kapag absolute ito.

Ipinapakita ng **indicator** sa tabi ng listahan ang kalagayan: pula (naka-disable o nabigo), orange (hindi pa nasusubukan o isinasagawa), berde (nabasa ang mga cookie). Nagpapatakbo ng pagsubok ang button na ↻; ipinapaliwanag ng tooltip ang error. Ang pagsubok na nakabasa ng **0 cookie** ay hindi kailanman nagiging berde.

### Mga karaniwang kaso

| Ang nakikita mo | Posibleng dahilan | Ano ang gagawin |
|---|---|---|
| "Extracted 0 cookies" at pagkatapos ay "Sign in to confirm you're not a bot" | walang cookie na iniingatan ang browser sa disk (binubura ito ng LibreWolf kapag isinara bilang default; profile na hindi pa kailanman na-sign in; private mode) | panatilihin itong bukas at naka-sign in sa YouTube, o patayin ang pagbura ng cookie kapag isinara sa mga setting nito sa privacy |
| "Item does not exist!" sa Chrome, Chromium, Brave, Vivaldi, Opera o Edge | hindi nakita ng yt-dlp ang susi ng browser sa key ring ng desktop | buksan nang minsan ang browser, mag-sign in sa YouTube, isara ito, ulitin ang pagsubok; kung hindi pa rin, [seksyon 5](#s5) |
| "Could not copy Chrome cookie database" o "database is locked" | ni-lo-lock ng browser ang database nito habang tumatakbo | isara ito, pagkatapos ay ulitin ang pagsubok |
| "Failed to decrypt" | mga cookie na na-encrypt gamit ang susing hindi nakuha ng yt-dlp | [seksyon 5](#s5) |

### Pagsubok ng browser mula sa terminal

Ito ang pinakamainam na paraan para makita ang eksaktong error (palitan ang `IDENTIFIER` ng identifier ng alinmang video sa YouTube):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Mga linyang hahanapin: `Extracted N cookies from chromium` (dapat mas malaki sa 0 ang N), `Chosen keyring: GNOMEKEYRING` (ang napiling key ring), at `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (kailangan ng key ring ng mga cookie na `v11`, ang `v10` ay hindi).

Para sa hango ng Firefox, ibigay ang profile folder. Para mahanap ito:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Sa Flatpak na pag-install, maghanap sa `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Pagkatapos, gamit ang folder na may `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Mga key ring: mano-manong gawain

### Para saan ito

Ine-encrypt ng mga browser na kabilang sa pamilyang Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) ang kanilang mga cookie. Nakatago ang susi ng encryption sa **key ring ng desktop**: GNOME Keyring (o katumbas na compatible, sa pamamagitan ng "Secret Service") sa GNOME, XFCE, Cinnamon, MATE…, KWallet sa KDE. Para mag-decrypt, hinihingi ng yt-dlp sa key ring ang susing iyon. Hindi ito kailangan ng Firefox at ng mga hango nito.

Dalawang kapaki-pakinabang na katotohanan:

- **Umiiral lang ang susi pagkatapos mabuksan nang minsan ang browser.** Sa virtual machine namin, nawala ang error na "Item does not exist!" nang mabuksan nang minsan ang bawat browser at makapag-sign in dito sa YouTube. Hindi natiyak nang may katiyakan ang eksaktong dahilan ng unang pagkabigo: umiiral ang key ring, ito ang default at naka-unlock.
- **Kung aling key ring ang ginagamit ng yt-dlp** ay nakadepende sa natukoy na desktop (ang mga variable na `XDG_CURRENT_DESKTOP` at `DESKTOP_SESSION`), ayon sa code ng yt-dlp (Oktubre 2026):

| Natukoy na desktop | Key ring na ginagamit ng yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, desktop na hindi nakilala (mga window manager lang: sway, i3…) | wala: plain text (`BASICTEXT`) |

Sa huling kaso, mga cookie na `v10` lang ang binabasa ng yt-dlp: kung iniimbak ng browser mo ang susi nito sa GNOME Keyring, hindi made-decrypt ang mga cookie nitong `v11`. Kailangan mo noon na pilitin ang key ring mula sa terminal (seksyon 5.6); hindi pa nag-aalok ng setting na ito ang software.

Ang mga item na hinahanap sa key ring ay tinatawag na "*pangalan* Safe Storage". Ayon sa code ng yt-dlp, ito ay **"Chrome Safe Storage"** para sa Chrome at Vivaldi, **"Chromium Safe Storage"** para sa Chromium, Opera at Edge, **"Brave Safe Storage"** para sa Brave. Sa virtual machine namin, naka-install at nabuksan din ang Chrome at Chromium: hindi namin alam kung gagana ang Vivaldi, Opera o Edge nang mag-isa.

### 5.1 Umiiral ba ang key ring?

```bash
ls -la ~/.local/share/keyrings/
```

Dapat makita mo ang file na `login.keyring` (ang key ring na "login"). Susunod, aling key ring ang **default**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Sagot na `(objectpath '/org/freedesktop/secrets/collection/login',)`: may default na key ring. Sagot na `'/'`: **wala**, pumunta sa seksyon 5.4.

### 5.2 Naka-lock ba ito?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: naka-unlock. `(<true>,)`: naka-lock; buksan ito gamit ang Seahorse (seksyon 5.4), na hihingi ng password nito.

### 5.3 Nandoon ba ang susi ng browser ko?

Ilista ang mga item:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

Magbibigay ang sagot ng mga path na nagtatapos sa numero (`…/login/1`, `…/login/2`…). Para basahin ang pangalan ng bawat isa (iangkop ang listahan ng mga numero):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Dapat makita mo, halimbawa, ang `Chromium Safe Storage`, `Chrome Safe Storage` o `Brave Safe Storage`. Hindi nakakasama ang mga walang lamang pangalan. Kung wala ang pangalan ng browser mo: buksan ito nang minsan, mag-sign in sa YouTube, isara ito, pagkatapos ay patakbuhin ulit ang command na ito.

### 5.4 Gumawa o mag-unlock ng key ring gamit ang Seahorse

I-install ang Seahorse ("Passwords and Keys") at ang mga kaugnay na tool. Nasa window ding "Mga browser para sa cookies" ng software ang eksaktong command:

| Package manager | Command |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Pagkatapos ay buksan ito:

```bash
seahorse
```

- **Walang default na key ring**: gumawa ng isa (button na "+" o menu na File › New › password keyring), pangalanan itong "Login", pagkatapos ay i-right-click ito › "Set as default". Nag-iiba ang eksaktong mga label depende sa bersyon ng Seahorse.
- **Naka-lock na key ring**: double-click o right-click › "Unlock", pagkatapos ay i-type ang password nito (ikaw mismo ang mag-type, hindi ito kailanman hinihingi ng software).
- **Awtomatikong pag-login**: hindi kusang mabubuksan ang key ring na protektado ng password kung wala kang tina-type na password sa pagsisimula ng session; mananatili itong naka-lock hanggang i-unlock mo ito (o hanggang gamitin mo ang parehong password para sa session at para sa key ring).

Pagkatapos ay **buksan ang browser, mag-sign in sa YouTube, isara ito**, at ulitin ang pagsubok (seksyon 4).

### 5.5 KDE Plasma (KWallet)

Sa KDE, ini-query ng yt-dlp ang KWallet (`kwallet-query`). Tinatawag ang manager na `kwalletmanager` (o `kwalletmanager5`) depende sa distribution. Ang setup na ito ay **hindi pa nasusubukan** sa aming mga pagsubok.

### 5.6 Pagpilit ng key ring sa yt-dlp (terminal)

Hinahayaan ng software ang yt-dlp na pumili ng key ring ayon sa desktop. Para pilitin ito, magdagdag ng `+KEYRING` sa pangalan ng browser (mga halaga: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Para malaman kung aling key ring talaga ang ginagamit ng isang Chromium (command na kinuha mula sa code ng yt-dlp, hindi nasubukan dito):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Walang key ring: `--password-store=basic` (advanced, hindi nasubukan)

Tumatanggap ang Chromium ng `--password-store=basic`: iniimbak nito noon ang susi nito nang hindi naka-encrypt (isang nakapirming susi na kilala ng lahat) at ine-encrypt ang mga bago nitong cookie bilang `v10`, na binabasa ng yt-dlp nang walang key ring (`chromium+basictext`). **Mas hindi ito ligtas**: maaaring i-decrypt ng anumang programang nakakabasa ng mga file mo ang mga cookie na ito. Gamitin lang ito kung nauunawaan mo ang kapalit na ito; malamang na hindi na-re-encode ang mga cookie na naka-save na: mag-sign in ulit.

### 5.8 Huling paraan

Kung sira ang isang key ring, **mag-backup muna**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Binubura ng pagbura sa `login.keyring` ang **lahat** ng password na nasa loob nito (Wi-Fi, mga online account…): huwag itong gawin nang hindi nauunawaan ang mga kahihinatnan.

<a id="s6"></a>

## 6. Kung nasaan ang mga file

Ang data folder ay `$XDG_DATA_HOME/yt-dlp-GUI` (bilang default, `~/.local/share/yt-dlp-GUI`), maliban kung nasa tabi ng executable ng archive (o ng script na `yt-dlp-gui.pyw`) ang `portable.flag`.

| File o folder | Laman |
|---|---|
| `gui-config.json` | mga setting (wika, browser, mga folder, pagpili ng mga browser…) |
| `download-queue.json` | queue ng mga download |
| `custom-blocks.json` | mga custom na block ng opsyon |
| `yt-dlp` | executable na na-download ng assistant |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | mga pansamantalang configuration file ng yt-dlp |
| `app/` | kopya ng programang ginawa ng "I-install sa menu" |
| `~/.local/share/fonts/yt-dlp-GUI/` (sa labas ng data folder) | Noto font na na-download para sa Korean, Japanese o Chinese; para alisin ito: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Pag-troubleshoot

| Problema | Palatandaan |
|---|---|
| Hindi nagsisimula ang AppImage | patakbuhin ito mula sa terminal para mabasa ang error; i-install ang FUSE 2 (seksyon 2.2) o idagdag ang `--appimage-extract-and-run` |
| Walang lumalabas, o error sa library | suriin ang bersyon ng glibc: dapat 2.35 o mas mataas ang ipakita ng `ldd --version` |
| Walang icon sa Desktop | hindi nagpapakita ng icon ang GNOME bilang default; gamitin ang menu ng mga application |
| Shortcut sa Desktop na may babala | right-click › "Allow Launching" |
| Hindi gumagana ang drag and drop sa pagitan ng host at ng virtual machine | tampok ito ng VirtualBox (Guest Additions), hindi ng software |
| Mali ang laki ng interface | sinusunod ng software ang mga font ng system (Tk); subukan ang ibang laki ng font ng system |
| Nabibigo ang update ng yt-dlp | gamitin ang "I-update at Diagnostics" sa menu ng mga opsyon; kung hindi, i-download ang `yt-dlp_linux` at piliin ito sa window ng pagpapalit (gagawing executable ang napiling file) |
| Mga parisukat sa halip na teksto (Korean, Chinese, Japanese…) | walang font sa system na naglalaman ng mga karakter na ito; sa Debian at Ubuntu: `sudo apt install fonts-noto-cjk` (~90 MB), pagkatapos ay isara at buksan ulit ang software; sa ibang distribution, i-install ang package na "Noto Sans CJK" ng distribution ; kaya ring i-download mismo ng software ang font (Korean, Japanese, Chinese) kapag pinili mo ang wika, nang walang karapatan ng administrator |

<a id="s8"></a>

## 8. Pag-uulat ng bug

Ang button na "Mag-ulat ng bug" ay naghahanda ng teknikal na ulat kung saan nakatago ang mga folder, user name at e-mail address mo; walang awtomatikong ipinapadala. Para sa Linux, idagdag dito ang:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

at sabihin **kung paano** mo ini-install ang software (AppImage, archive, `.deb`, source code) at, kung problema sa cookie, **ang resulta ng pagsubok sa terminal** (seksyon 4), nang hindi ipinapaste ang mga cookie mo.

<a id="s9"></a>

## 9. Para sa mga developer

Mga pagsubok (sa virtual na display, hindi kailangan ng totoong screen):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Pagbuo ng mga package (mga build tool: `pip install -r packaging/requirements-build.txt`, dagdag ang `appimagetool`, na ang path ay ibinibigay ng variable na `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Nasa `dist/` ang mga resulta. Para sa pinakamainam na compatibility, bumuo sa pinakamatandang sinusuportahang distribution (ang glibc ng build machine ang pinakamababang hinihingi sa mga makinang nagpapatakbo ng programa). Mga kapaki-pakinabang na pagsusuri sa `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

Ang tanging kilalang error sa anyo ay ang `dir-or-file-in-opt` (programang nasa loob ng `/opt`).

**Paglalathala**: suriin ang `__version__` sa `yt-dlp-gui.pyw`, lagyan ng petsa ang seksyon ng bersyon sa `CHANGELOG-linux.md`, mag-commit, pagkatapos ay gumawa at mag-push ng tag na `Linux-vX.Y.Z`. Pinapatakbo ng workflow na "Release Linux" ang mga pagsubok, binubuo ang AppImage, ang archive at ang `.deb`, kinukuwenta ang mga sum, at ginagawa ang release bilang **pre-release**, hindi kailanman bilang "pinakabagong release" (hindi dapat makakita ng tag ng Linux doon ang pagsusuri ng update ng bersyon para sa Windows na 0.1.7).

Lisensya: MIT, tulad ng iba pang bahagi ng repository (tingnan ang [LICENSE](../LICENSE)).
