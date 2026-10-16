# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Isang graphical interface para sa [yt-dlp](https://github.com/yt-dlp/yt-dlp), na idinisenyo para maging abot-kamay ng lahat habang lubos na ginagamit ang mga kakayahan nito.

> **Ginagawa pa ang proyekto.** Maaaring magbago, hindi pa kumpleto o may mga bug ang ilang feature.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Mga feature

### Indibidwal na downloader at pila

- **Mga opsyon**: pinakamataas na kalidad (hanggang 4K), audio lang (MP3), mga subtitle (mga format na vtt, srt, ass), pag-embed ng mga subtitle at thumbnail, pangunahing wika ng audio, mga pangalawang audio track (multi-track na MKV file) at isang aklatan ng mga "script block" (post-processing, export, network, gawi) na maaari mong dagdagan ng sarili mong mga block.
- **Nabuong command**: ipinapakita nang live ang yt-dlp command na tugma sa mga pinili mo.
- **Pila**: idagdag ang kasalukuyang URL, saka patakbuhin ang buong pila, mula sa isang item pasulong, isang video lang o isang saklaw; pause at resume, paglaktaw sa kasalukuyang item, paghinto na may paglilinis ng mga hindi kumpletong file. Napapanatili ang pila sa pagitan ng mga session.

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

- Piliin ang browser (Chrome, Firefox, Edge, Brave, Opera) na ang mga cookie ay lokal na binabasa ng yt-dlp: kailangan ang mga ito para sa mga pangalawang audio track at ilang subtitle.
- Ipinapakita ng isang **ilaw na indikasyon** ang kalagayan: pula kung naka-disable o nabigo, kahel kung hindi pa nasusubok o isinasagawa, berde kung na-load ang mga cookie. Nagpapatakbo ng pagsubok ang button na ↻ at ipinaliliwanag ng tooltip ang kalagayan o error.

### Katulong sa pag-install, mga dependency at mga update ng yt-dlp

- **Katulong sa pag-install**: sa unang pagbukas, iminumungkahi nitong i-download ang yt-dlp at ffmpeg mula sa kanilang opisyal na GitHub repository. Bine-verify ang SHA-256 checksum at hindi kailangan ng administrator rights.
- **Mga dependency**: sinusuri ng nakalaang window ang ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 at deno, at maaari silang i-install gamit ang Chocolatey.
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
