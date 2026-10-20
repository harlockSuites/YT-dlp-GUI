# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Isang graphical interface para sa [yt-dlp](https://github.com/yt-dlp/yt-dlp), na idinisenyo para maging abot-kamay ng lahat habang lubos na ginagamit ang mga kakayahan nito.

> **Ginagawa pa ang proyekto.** Maaaring magbago, hindi pa kumpleto o may mga bug ang ilang feature.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Mga feature

### Indibidwal na downloader at pila

- **Mga opsyon**: pinakamataas na kalidad (hanggang 4K), audio lang (MP3), mga subtitle (mga format na vtt, srt, ass), pag-embed ng mga subtitle at thumbnail, pangunahing wika ng audio, mga pangalawang audio track (multi-track na MKV file) at isang aklatan ng mga "script block" (post-processing, export, network, gawi) na maaari mong dagdagan ng sarili mong mga block.
- **Maraming audio track**: sa MKV file, may tag ng wika ang bawat audio track ("fil", "eng"…); ipinapakita ito ng player sa audio menu.
- **Nabuong command**: ipinapakita nang live ang yt-dlp command na tugma sa mga pinili mo.
- **Pila**: idagdag ang kasalukuyang URL, saka patakbuhin ang buong pila, mula sa isang item pasulong, isang video lang o isang saklaw; pause at resume, paglaktaw sa kasalukuyang item, paghinto na may paglilinis ng mga hindi kumpletong file. Napapanatili ang pila sa pagitan ng mga session.
- **Mga umiiral nang pangalan ng file**: ang isang video na ang pangalan ay nasa destination folder na ay nagkakaroon ng suffix (`_2`, `_3`…) para walang mapatungan. Ang playlist na dina-download sa downloader na ito ay hindi binabago ang numero: nilalaktawan ang mga video na nasa folder na ("has already been downloaded").

### Inspector ng playlist

- **Pagsusuri** ng isang playlist: nakalista ang bawat video kasama ang mga available na audio track at subtitle nito; nilalaktawan ang mga nakatago, pribado o nabura nang hindi hinaharangan ang iba.
- **Mga pangkalahatang tuntunin** (kalidad, audio lang, format at pag-embed ng subtitle, thumbnail, pagnunumero, mga wika, mga script block, output na folder) na may **mga eksepsiyon kada video** para sa pangunahing wika, mga pangalawang track at mga subtitle.
- **Kulay**: pula kapag wala ang pangunahing wika, kahel kapag kulang ang pangalawang track o subtitle.
- **Pag-download ng napili** na may log, pause, resume at laktaw; kung wala ang mga hinihinging track, uulitin ang video nang wala ang mga ito, at pagkatapos ay ipinapakita ng **buod** kung ano ang nagtagumpay, naayos o nabigo.

### Smart na direktoryo at talaan

- **Smart na direktoryo**: nilalaktawan ng yt-dlp ang mga video na na-download na dahil sa isang talaan na nakaimbak sa output na folder. Ang file na `.yt-dlp-registre.json` ay naglalaman ng identifier, URL, pamagat, haba, pangalan ng file at petsa ng bawat video; ang `.yt-dlp-archive.txt`, na binabasa ng yt-dlp, ay hango rito.
- **Pagsusuring pabalik**: kung nasa folder na ang mga napiling video pero wala sa talaan, mag-aalok ang isang window na itala at laktawan ang mga ito (sa pamamagitan ng paghahambing ng mga pamagat). Maaari mong alisin ang tsek sa mga maling tugma.
- **I-update ang talaan**: binibilang ang mga video sa folder, sa talaan at ang mga kulang, saka hinahanap sa YouTube ang kulang na impormasyon (pamagat, at haba sa pamamagitan ng ffprobe). Walang itinatala nang walang pagkumpirma mo, at binubuksan ng dalawang button ang lokal na file o ang nahanap na YouTube link para masuri mo.

![yt-dlp GUI](img/registry.en.png)

### Mga cookie ng browser

- Piliin ang browser (Chrome, Firefox, Edge, Brave, Opera) na ang mga cookie ay lokal na binabasa ng yt-dlp: kailangan ang mga ito para sa mga pangalawang audio track at ilang subtitle. **Inirerekomenda ang Firefox.**
- **Mga resulta ng aming mga pagsubok** (Windows 11, Oktubre 2026, naka-sign in ang YouTube account sa bawat browser): gumagana ang **Firefox**, bukas man o sarado ang browser. Gumagana ang **Opera** **kapag sarado lang ang browser**: ni-lo-lock nito ang cookie database habang bukas, at ipapakita ng yt-dlp ang "Could not copy Chrome cookie database". Pumapalya ang **Chrome, Edge at Brave** kahit sarado: ine-encrypt nila ang mga cookie sa paraang hindi laging nababasa ng yt-dlp. Ang mga limitasyong ito ay mula sa mga browser at yt-dlp, hindi sa software na ito, at maaaring magbago sa mga update nila.
- Kung naka-set ang browser na **burahin ang mga cookie kapag isinara** (o nagba-browse ka sa private mode), walang matitirang cookie sa disk na mababasa: wala nang makukuha ang yt-dlp, gamit man ang Chrome, Edge, Brave o Firefox. Sa Chrome, Edge at Brave, isa itong bitag: kailangang isara ang browser, at buburahin nito ang mga cookie. I-off ang opsyong iyon, o panatilihin ang mga cookie ng youtube.com at google.com.
- Ipinapakita ng isang **ilaw na indikasyon** ang kalagayan: pula kung naka-disable o nabigo, kahel kung hindi pa nasusubok o isinasagawa, berde kung na-load ang mga cookie. Nagpapatakbo ng pagsubok ang button na ↻ at ipinaliliwanag ng tooltip ang kalagayan o error.

### Katulong sa pag-install, mga dependency at mga update ng yt-dlp

- **Katulong sa pag-install**: sa unang pagbukas, iminumungkahi nitong i-download ang yt-dlp at ffmpeg mula sa kanilang opisyal na GitHub repository. Bine-verify ang SHA-256 checksum at hindi kailangan ng administrator rights.
- **Mga dependency**: sinusuri ng nakalaang window ang ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 at deno, at maaari silang i-install gamit ang Chocolatey. Ang ffmpeg at ffprobe lamang ang kailangang-kailangan; inirerekomenda ang deno (mga pangalawang audio track); opsyonal ang AtomicParsley, MKVToolNix at aria2: gumagana ang software kahit wala ang mga ito.
- **Update at diagnostic**: ina-update ang yt-dlp (`yt-dlp -U`) o pinapalitan ang executable nito, ipinapakita ang bersyon at sinusuri ang mga opsyong ginagamit ng interface.
- **Update ng software**: ang araw-araw na pagsusuri (maaaring i-off) ay nagsasaad ng bagong bersyon gamit ang isang banayad na banner; ipinapakita ng nakalaang window ang mga bago at binubuksan ang download na tugma sa iyong pag-install (installer o portable na bersyon). Walang awtomatikong ini-install. Ino-on o ino-off ng switch sa menu ng mga opsyon ("Suriin ang mga update sa pagsisimula") ang awtomatikong pagsusuri, at pinapatakbo ito kapag hiniling ng "Maghanap ng update ng software…".

### Interface at mga wika

- Nagbabalot ang mga kontrol ayon sa lapad ng window; nag-i-scroll nang patayo ang nilalaman, at pahalang din ang talahanayan ng inspector.
- Interface sa **15 wika**: Pranses, Ingles, Espanyol, Portuges, Italyano, Polako, Hungaro, Serbiyo, Ruso, Biyetnames, Tsino, Hindi, Hapones, Koreano at Filipino. Ipinapatupad ang pagbabago ng wika sa muling pagsisimula, na may opsyong mag-restart agad.

### Mag-ulat ng bug

- Naghahanda ang button na "Mag-ulat ng bug" ng teknikal na ulat: mga bersyon ng software, Python, Windows at yt-dlp, mga hindi mapanganib na setting at ang mga huling linya ng log. Nakatago ang iyong mga folder, pangalan ng user at mga e-mail address.
## Pag-install

- **Installer (inirerekomenda)**: i-download ang `yt-dlp-gui-setup-X.Y.Z.exe` mula sa [pahina ng mga release](https://github.com/harlockSuites/YT-dlp-GUI/releases) at patakbuhin ito. Windows 10 o 11 (64-bit), walang kailangang administrator rights; hindi kailangan ang Python.
- **Portable na bersyon**: i-download ang `yt-dlp-gui-portable-X.Y.Z.zip`, i-extract kahit saan at patakbuhin ang `yt-dlp-gui.exe`; nananatili ang mga setting sa folder na iyon.
- **Mula sa source code**: tingnan ang mga seksyong "Mga kinakailangan" at "Mabilis na simula" sa ibaba.
- **Pag-uninstall**: Windows Settings › Apps › Installed apps › yt-dlp GUI, o ang shortcut na "Uninstall" sa Start menu. Iniaalok ng software na burahin din ang sarili nitong data (settings, pila, na-download na yt-dlp at ffmpeg); hindi kailanman binubura ang iyong mga video. Dahil sa bawat Windows account ang installation, lalabas lang ang software sa listahan ng account na nag-install nito. Sa portable na bersyon, burahin lang ang folder nito. Hindi inaalis ang mga tool na hiwalay na na-install gamit ang Chocolatey (ffmpeg, Deno…).
- **Pagsusuri ng antivirus (VirusTotal)**: sinuri ang bersyon 0.1.5 noong 19 Oktubre 2026. Ang [installer](https://www.virustotal.com/gui/file/09a52ad01147b519c828bcd8708990e411cc3ab0af018ebadf294f9f2591bc45) ay namarkahan ng 4 sa 71 na engine (Arctic Wolf, DeepInstinct, SecureAge, Skyhigh) sa pamamagitan ng pangkalahatang heuristic na pagtuklas ("obfuscatedpoly"); ang [launcher ng portable na bersyon](https://www.virustotal.com/gui/file/056a45eb80a50223ae34da91fcf0357ae885557a129c1be9dddf2205fe5160ad) ay namarkahan ng 2 sa 71 (Arctic Wolf, SecureAge) at ang [portable na ZIP archive](https://www.virustotal.com/gui/file/57ca0c679d9653bfde6bb3c374985ba8a324589f887f7f39467f8a0130649d58) ng 1 sa 67 (Zillya, sa mismong archive). Malamang na maling alarma ang mga ito dahil sa naka-compress at hindi pirmadong programa. Para lang sa bersyong ito ang mga resultang ito. Kung may alinlangan, suriin ang SHA-256 na kabuuan.
- **Code signing policy**: inihahanda ang digital na pirma para sa mga susunod na bersyon (aplikasyon sa SignPath Foundation); inilalarawan ng [code signing policy](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) ang proseso. Hindi pa pirmado ang mga bersyon hanggang 0.1.4.
- **Babala ng Windows SmartScreen**: hindi digitally signed ang installer, kaya maaaring magpakita ang Windows ng "Windows protected your PC". I-click ang "More info", saka ang "Run anyway". Para tiyaking totoo ang file, ihambing ang SHA-256 sum nito sa nasa `SHA256SUMS.txt` na inilalathala kasama ng bawat release:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Walang awtomatikong ipinapadala: sinusuri at ine-edit mo ang ulat, saka magbubukas ng paunang-punong GitHub issue page (o kokopyahin ang ulat).

## Mga kinakailangan

- Windows
- [Python 3](https://www.python.org/) na may Tkinter (kasama sa karaniwang pag-install)
- `yt-dlp.exe` at mas mainam ang [ffmpeg](https://ffmpeg.org/): dina-download ang mga ito ng katulong sa pag-install sa unang pagbukas

## Mabilis na simula

1. I-download o i-clone ang repository na ito at pumunta sa folder nito.
2. Patakbuhin ang `yt-dlp-gui.bat` (o `pythonw yt-dlp-gui.pyw`).
3. Sa unang pagbukas, hayaang i-install ng katulong ang yt-dlp at ffmpeg; nananatili itong available sa menu ng mga opsyon.
4. Mag-paste ng URL, piliin ang mga opsyon, saka mag-download, magdagdag sa pila o buksan ang inspector para sa isang playlist.

## Privacy at responsableng paggamit

- Walang ipinapadalang data ang software na ito sa may-akda at walang telemetry. Dumadaan ang mga koneksyon sa network sa yt-dlp (mga video site), sa katulong sa pag-install (GitHub) at sa tool ng talaan (paghahanap sa YouTube). Kumokonekta rin sa GitHub ang awtomatikong pagsusuri ng update sa pagsisimula (isang beses lang kada araw nang pinakamarami); maaari mo itong i-off sa "Suriin ang mga update sa pagsisimula".
- Nananatili sa iyong computer ang iyong mga cookie: lokal na binabasa ng yt-dlp ang mga ito mula sa napiling browser.
- Gamitin ang tool na ito alinsunod sa copyright, sa mga tuntunin ng paggamit ng mga site at sa mga batas ng iyong bansa, at i-download lang ang may karapatan kang i-download.

## Pag-develop

Pinapatakbo ang mga test (mga salin, talaan, pagbuo ng command, interface, katulong sa pag-install, dokumentasyon) gamit ang:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Awtomatiko rin silang tumatakbo sa GitHub sa bawat push. Ang numero ng bersyon ay tinutukoy ng `__version__` sa `yt-dlp-gui.pyw` at dapat tumugma sa header ng [CHANGELOG.md](../CHANGELOG.md). Nasa `lang/` ang mga file ng salin ng interface at nasa `docs/` ang sa dokumentasyong ito; malugod na tinatanggap ang pagsusuri ng mga katutubong tagapagsalita.

## Suportahan ang proyekto

Ang paggamit ng GUI na ito ay libre, palaging naging libre at mananatiling libre at bukas para sa sinuman. Kung lalo kang nakinabang sa tool, maaari mong suportahan ang proyekto sa [Ko-fi](https://ko-fi.com/harlocksuites).

## Pasasalamat

Salamat sa komunidad na regular na nag-a-update ng [yt-dlp](https://github.com/yt-dlp/yt-dlp), na kung wala ay hindi magiging posible ang lahat ng ito.

## Lisensya

Inilabas ang code sa ilalim ng lisensyang [MIT](../LICENSE). Ang icon, logo at banner na "Harlock S." (file na `yt-dlp-gui.ico` at folder na `assets/`) ay orihinal na likha na binuo ng AI sa kahilingan ng may-akda. Bumubuo ang mga ito ng visual na pagkakakilanlan ng proyekto at hindi sakop ng lisensyang MIT: huwag gamitin muli ang mga ito sa ibang proyekto o sa paraang maaaring magdulot ng kalituhan.
