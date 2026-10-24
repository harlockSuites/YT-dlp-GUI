# yt-dlp GUI — verzija za Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Pretpremijera.** Ovaj dokument dopunjuje [glavni README](README.sr.md): reč je o istom programu, ali ovde se govori samo o onome što je specifično za Linux (instalacija, kolačići i priveznici ključeva, fajlovi, rešavanje problema). Novosti svake verzije nalaze se u [CHANGELOG-linux.md](../CHANGELOG-linux.md). Prevode tek treba da pregledaju izvorni govornici; u slučaju sumnje, merodavni su tekstovi na francuskom i engleskom.

## Sadržaj

1. [Stanje pretpremijere](#s1)
2. [Instalacija](#s2)
3. [Prvo pokretanje i zavisnosti](#s3)
4. [Kolačići pregledača](#s4)
5. [Priveznici ključeva: ručne operacije](#s5)
6. [Gde su fajlovi](#s6)
7. [Rešavanje problema](#s7)
8. [Prijava greške](#s8)
9. [Za programere](#s9)

<a id="s1"></a>

## 1. Stanje pretpremijere

Linux verzija reprodukuje ponašanje Windows verzije 0.1.7 (zamrznute, koja služi kao uzor). Objavljuje se kao **GitHub pretpremijera (pre-release)** pod oznakama `Linux-vX.Y.Z`: nikada se ne predstavlja kao „najnovije izdanje” repozitorijuma.

**Šta je isprobano** (virtuelna mašina Debian 12, GNOME radna površina, Python 3.11, pravi YouTube nalog prijavljen u svakom pregledaču, oktobar 2026):

- **Kolačići Firefoxa, Waterfoxa, Floorpa i Zen Browsera**: pročitani sa otvorenim ili zatvorenim pregledačem.
- **Kolačići Google Chromea, Chromiuma, Bravea, Vivaldija, Opere i Microsoft Edgea**: pročitani sa **zatvorenim** pregledačem, nakon što je svaki pregledač jednom pokrenut i u njemu je izvršena prijava na YouTube (vidi [odeljak 5](#s5)). Pojedinačno preuzimanje i Inspektor plejlista su uspeli.
- **LibreWolf**: čitaju se samo dok je otvoren i prijavljen (podrazumevano briše kolačiće pri zatvaranju).
- **Privatni video** sa kolačićima Firefoxa, i plejlista od tri videa od kojih je jedan privatan.
- **Paketi**: AppImage i arhivu `.tar.gz` gradi CI na Ubuntu 22.04; `.deb` je napravljen, instaliran, pokrenut i uklonjen na Debianu 12; „Instaliraj u meni” je isproban sa pravim AppImage-om u privremenom kućnom folderu.

**Šta još nije isprobano**:

- druge distribucije (Ubuntu, Fedora, Arch, openSUSE…) i radne površine osim GNOME-a, uključujući KDE Plasma (KWallet);
- pregledači instalirani kao Flatpak ili Snap (osim rasporeda LibreWolfa u Flatpaku, koji je uočen);
- Vivaldi, Opera ili Edge **bez** instaliranog Chromea ili Chromiuma (vidi [odeljak 5](#s5));
- arhitektura aarch64 (program je podržava, ali se paketi grade samo za x86_64);
- prozor „Instaliraj u meni” korišćen mišem na pravoj radnoj površini (testira se programski);
- prevodi: još ih treba da pregledaju izvorni govornici.

<a id="s2"></a>

## 2. Instalacija

### Koji format izabrati

| Format | Za koga | Administratorska prava | Stavka u meniju |
|---|---|---|---|
| **AppImage** | svaka novija 64-bitna distribucija | ne | „Instaliraj u meni” (odeljak 2.3) |
| **Arhiva `.tar.gz`** | isto, bez AppImage-a i FUSE-a | ne | „Instaliraj u meni” |
| **Paket `.deb`** | Debian, Ubuntu i derivati | da (`sudo`) | automatska |
| **Izvorni kod** | programeri, probe | ne | nema |

Zahtevi: 64-bitni Linux (x86_64) iz distribucije iz 2022. ili novije (glibc 2.35 ili novija), jer se paketi grade na Ubuntu 22.04.

**Ako ste novi u Linuxu**: samo se paket `.deb` instalira „zaista” i pojavljuje se u upravniku softvera. AppImage i arhiva su obični fajlovi ili folderi, koje čuvate gde želite: da biste ih uklonili, obrišete ih kao bilo koji drugi fajl (odeljci 2.2 i 2.5). Njihova podešavanja se čuvaju odvojeno, u `~/.local/share/yt-dlp-GUI` (odeljak 6), i preživljavaju to brisanje.

Fajlovi su na [stranici izdanja](https://github.com/harlockSuites/YT-dlp-GUI/releases): potražite oznake `Linux-v…`, označene sa „Pre-release”.

### 2.1 Provera preuzimanja

Preuzmite i `SHA256SUMS-linux.txt` u isti folder, pa zatim:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Svaki prisutan fajl treba da prikaže `OK`. To dokazuje da je vaš fajl identičan objavljenom, a ne da je bezopasan: izvorni kod i automatska izgradnja su javni.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage zahteva biblioteku FUSE 2:

| Distribucija | Paket |
|---|---|
| Debian, Ubuntu 22.04 i derivati | `libfuse2` |
| Ubuntu 24.04 i novije | `libfuse2t64` |
| Fedora | `fuse-libs` |

Bez FUSE-a ga ipak pokrenite: sam se raspakuje u privremeni folder:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage nije „instaliran”: ne pojavljuje se u upravniku softvera. Da biste ga uklonili, obrišite fajl:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

### 2.3 Instaliraj u meni (bez administratora)

AppImage pokrenut dvostrukim klikom ne ostavlja ikonu u meniju aplikacija. U programu: meni opcija › **„Instaliraj u meni…”**. Prozor:

- kopira program u `~/.local/share/yt-dlp-GUI/app/`;
- upisuje pokretač `~/.local/share/applications/yt-dlp-gui.desktop` i ikonu `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- dodaje, ako je polje označeno, prečicu na radnoj površini (označenu kao „pouzdanu” za GNOME kada postoji alat `gio`);
- zatim nudi „Ažuriraj” (ponovo kopira verziju koja radi) i „Deinstaliraj”.

„Deinstaliraj” uklanja samo ono što je instalacija napravila i **čuva vaša podešavanja** i preuzete alate. Pokretač bez naše unutrašnje oznake (`X-YtDlpGui-Installer=1`) nikada se ne briše.

Ograničenja: prozor je dostupan iz AppImage-a i iz arhive. Iz izvornog koda vas upućuje na AppImage; iz paketa `.deb` objašnjava da je program već u meniju.

Ako prečica na radnoj površini prikaže upozorenje: desni klik na ikonu › „Dozvoli pokretanje”. Neke radne površine (GNOME podrazumevano) ne prikazuju ikone na radnoj površini: pokretač u meniju radi u svakom slučaju.

Da sve uklonite ručno:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 Paket `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Program ide u `/opt/yt-dlp-gui`, sa vezom `/usr/bin/yt-dlp-gui`, pokretačem u meniju, ikonom i licencom (`/usr/share/doc/yt-dlp-gui/`). Zavisi od `libc6 (>= 2.35)` i `libx11-6`.

Da ga uklonite (vaša podešavanja, u `~/.local/share/yt-dlp-GUI`, nikada se ne diraju):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Arhiva `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Da podešavanja i alati ostanu **unutar raspakovanog foldera** (USB memorija, proba bez tragova), napravite prazan fajl `portable.flag` pored izvršnog fajla:

```bash
touch yt-dlp-gui/portable.flag
```

Bez ovog fajla podaci idu u `~/.local/share/yt-dlp-GUI` (odeljak 6).

Arhiva nije „instalirana”: ne pojavljuje se u upravniku softvera. Da biste je uklonili, obrišite raspakovani folder:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Iz izvornog koda

```bash
python3 yt-dlp-gui.pyw
```

Iz izvornog koda, podešavanja i preuzeti alati idu u isti folder kao kod instaliranih verzija (`~/.local/share/yt-dlp-GUI`): ponovno preuzimanje koda ili brisanje njegovog foldera ih ne briše. Da podaci ostanu u folderu sa kodom (proba bez tragova), napravite prazan fajl `portable.flag` pored `yt-dlp-gui.pyw`.

Potreban je Python 3 sa Tkinterom:

| Distribucija | Paket |
|---|---|
| Debian, Ubuntu i derivati, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Ažuriranja

Dnevna provera (koja se može isključiti u meniju opcija) traži verzije `Linux-vX.Y.Z`, uključujući pretpremijere, i **nikada** ne predlaže Windows verziju. Otvara stranicu za preuzimanje fajla koji odgovara vašoj instalaciji (AppImage, arhiva ili `.deb`); **ništa se ne instalira automatski**. Za ažuriranje:

- **AppImage ili arhiva instalirani u meni**: preuzmite novi AppImage, pokrenite ga, pa „Instaliraj u meni… › Ažuriraj”;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **arhiva koja nije instalirana**: raspakujte novu arhivu preko stare.

### 2.8 Uklanjanje svega, uključujući podatke

Nakon uklanjanja programa (odeljci 2.3 do 2.5), da obrišete i podešavanja, red čekanja i preuzete alate (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Vaši preuzeti video snimci nikada nisu u ovom folderu.

<a id="s3"></a>

## 3. Prvo pokretanje i zavisnosti

Pri prvom pokretanju, pomoćnik za instalaciju predlaže preuzimanje programa **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (arhiva `.tar.xz` zvaničnih yt-dlp izgradnji) i **deno** iz njihovih GitHub repozitorijuma. SHA-256 zbirovi se proveravaju, ne traže se administratorska prava, a fajlovi idu u `~/.local/share/yt-dlp-GUI` (yt-dlp) i `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Ostaje dostupan u meniju opcija.

Neophodni su samo ffmpeg i ffprobe; deno se preporučuje (dodatne audio numere). **AtomicParsley, MKVToolNix i aria2** su opcioni: prozor „Zavisnosti” prikazuje komandu vašeg upravnika paketa, koju kopirate u terminal. Program je nikada sam ne pokreće. Iste komande:

| Upravnik paketa | Komanda |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Kolačići pregledača

yt-dlp čita kolačiće **lokalno**, u pregledaču koji izaberete (dodatne audio numere, titlovi, privatni video snimci, sadržaj za članove). Podrazumevano, program nudi pet najčešće korišćenih pregledača na Linuxu (Firefox, Google Chrome, Chromium, Brave, Vivaldi). Stavka **„Pregledači za kolačiće…”** u meniju opcija otvara prozor „Pregledači za kolačiće”, koji nudi 11: označite one koji su vam potrebni; znak ✔ označava one čiji folder profila postoji na vašem računaru.

| Pregledač | yt-dlp ga čita kao | Priveznik ključeva | Pretraživani folderi profila |
|---|---|---|---|
| Firefox | `firefox` | ne | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | da | `~/.config/google-chrome` |
| Chromium | `chromium` | da | `~/.config/chromium` |
| Brave | `brave` | da | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | da | `~/.config/vivaldi` |
| Opera | `opera` | da | `~/.config/opera` |
| Microsoft Edge | `edge` | da | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + folder profila | ne | `~/.librewolf`, `~/.config/librewolf`… (ista šema za ostale), uključujući Flatpak |

Derivati Firefoxa nemaju ime koje yt-dlp poznaje: program traži njihovu bazu `cookies.sqlite` (do tri nivoa ispod njihovih foldera) i yt-dlp-u predaje folder poslednje korišćenog profila. `XDG_CONFIG_HOME` se poštuje kada je apsolutna putanja.

**Indikator** pored liste prikazuje stanje: crveno (isključeno ili neuspešno), narandžasto (nije testirano ili je u toku), zeleno (kolačići pročitani). Dugme ↻ pokreće test; objašnjenje pri prelasku mišem tumači grešku. Test koji pročita **0 kolačića** nikada nije zelen.

### Česti slučajevi

| Šta vidite | Verovatni uzrok | Šta učiniti |
|---|---|---|
| „Extracted 0 cookies”, pa „Sign in to confirm you're not a bot” | pregledač ne čuva nijedan kolačić na disku (LibreWolf ih podrazumevano briše pri zatvaranju; profil nikada nije prijavljen; privatni režim) | ostaviti ga otvorenim i prijavljenim na YouTube, ili isključiti brisanje kolačića pri zatvaranju u njegovim podešavanjima privatnosti |
| „Item does not exist!” sa Chromeom, Chromiumom, Braveom, Vivaldijem, Operom ili Edgeom | yt-dlp nije našao ključ pregledača u privezniku ključeva radne površine | jednom pokrenuti pregledač, prijaviti se na YouTube, zatvoriti ga i ponoviti test; inače [odeljak 5](#s5) |
| „Could not copy Chrome cookie database” ili „database is locked” | pregledač zaključava svoju bazu dok radi | zatvoriti ga, pa ponoviti test |
| „Failed to decrypt” | kolačići šifrovani ključem koji yt-dlp nije dobio | [odeljak 5](#s5) |

### Testiranje pregledača iz terminala

Ovo je najbolji način da vidite tačnu grešku (zamenite `IDENTIFIER` identifikatorom bilo kog YouTube videa):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Linije koje treba tražiti: `Extracted N cookies from chromium` (N mora biti veće od 0), `Chosen keyring: GNOMEKEYRING` (izabrani priveznik ključeva) i `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (kolačići `v11` zahtevaju priveznik ključeva, `v10` ne).

Za derivat Firefoxa navedite folder profila. Da ga nađete:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

U Flatpak instalaciji tražite u `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Zatim, sa folderom koji sadrži `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Priveznici ključeva: ručne operacije

### Čemu služi

Pregledači iz porodice Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) šifruju svoje kolačiće. Ključ za šifrovanje čuva se u **privezniku ključeva radne površine**: GNOME Keyring (ili kompatibilni ekvivalent, preko „Secret Service”) u GNOME-u, XFCE-u, Cinnamonu, MATE-u…, KWallet u KDE-u. Da bi dešifrovao, yt-dlp traži taj ključ od priveznika. Firefoxu i njegovim derivatima nije potreban.

Dve korisne činjenice:

- **Ključ postoji tek nakon prvog pokretanja pregledača.** U našoj virtuelnoj mašini greška „Item does not exist!” nestala je kada je svaki pregledač jednom pokrenut i u njemu je izvršena prijava na YouTube. Tačan uzrok prvog neuspeha nije sa sigurnošću utvrđen: priveznik je postojao, bio je podrazumevani i otključan.
- **Koji priveznik yt-dlp koristi** zavisi od otkrivene radne površine (promenljive `XDG_CURRENT_DESKTOP` i `DESKTOP_SESSION`), prema kodu yt-dlp-a (oktobar 2026):

| Otkrivena radna površina | Priveznik koji koristi yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, neprepoznata radna površina (samo upravnici prozora: sway, i3…) | nijedan: običan tekst (`BASICTEXT`) |

U poslednjem slučaju yt-dlp čita samo kolačiće `v10`: ako vaš pregledač čuva ključ u GNOME Keyringu, njegovi kolačići `v11` neće biti dešifrovani. Tada morate nametnuti priveznik iz terminala (odeljak 5.6); program još ne nudi to podešavanje.

Stavke koje se traže u privezniku zovu se „*ime* Safe Storage”. Prema kodu yt-dlp-a, to je **„Chrome Safe Storage”** za Chrome i Vivaldi, **„Chromium Safe Storage”** za Chromium, Operu i Edge, **„Brave Safe Storage”** za Brave. U našoj virtuelnoj mašini bili su instalirani i pokrenuti i Chrome i Chromium: ne znamo da li bi Vivaldi, Opera ili Edge radili sami.

### 5.1 Da li priveznik postoji?

```bash
ls -la ~/.local/share/keyrings/
```

Treba da vidite fajl `login.keyring` (priveznik „login”). Zatim: koji priveznik je **podrazumevani**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Odgovor `(objectpath '/org/freedesktop/secrets/collection/login',)`: postoji podrazumevani priveznik. Odgovor `'/'`: **nijedan**, pređite na odeljak 5.4.

### 5.2 Da li je zaključan?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: otključan. `(<true>,)`: zaključan; otvorite ga pomoću Seahorsea (odeljak 5.4), koji traži njegovu lozinku.

### 5.3 Da li je ključ mog pregledača u njemu?

Izlistajte stavke:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

Odgovor daje putanje koje se završavaju brojem (`…/login/1`, `…/login/2`…). Da pročitate ime svake (prilagodite listu brojeva):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Treba da vidite, na primer, `Chromium Safe Storage`, `Chrome Safe Storage` ili `Brave Safe Storage`. Prazna imena su bezopasna. Ako ime vašeg pregledača nedostaje: jednom ga pokrenite, prijavite se na YouTube, zatvorite ga, pa ponovo pokrenite ovu komandu.

### 5.4 Pravljenje ili otključavanje priveznika pomoću Seahorsea

Instalirajte Seahorse („Lozinke i ključevi”) i povezane alate. Tačna komanda je i u prozoru „Pregledači za kolačiće” u programu:

| Upravnik paketa | Komanda |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Zatim ga otvorite:

```bash
seahorse
```

- **Nema podrazumevanog priveznika**: napravite jedan (dugme „+” ili meni Fajl › Novo › priveznik lozinki), nazovite ga „Login”, pa desni klik na njega › „Postavi kao podrazumevani”. Tačni nazivi zavise od verzije Seahorsea.
- **Zaključan priveznik**: dvostruki klik ili desni klik › „Otključaj”, pa unesite njegovu lozinku (unesite je sami, program je nikada ne traži).
- **Automatska prijava**: priveznik zaštićen lozinkom ne može se otvoriti sam ako pri pokretanju sesije ne unesete nikakvu lozinku; ostaje zaključan dok ga ne otključate (ili dok ne koristite istu lozinku za sesiju i za priveznik).

Zatim **pokrenite pregledač, prijavite se na YouTube, zatvorite ga** i ponovite test (odeljak 4).

### 5.5 KDE Plasma (KWallet)

U KDE-u yt-dlp ispituje KWallet (`kwallet-query`). Upravnik se zove `kwalletmanager` (ili `kwalletmanager5`), zavisno od distribucije. Ova konfiguracija **nije isprobana** u našim testovima.

### 5.6 Nametanje priveznika programu yt-dlp (terminal)

Program prepušta yt-dlp-u da izabere priveznik prema radnoj površini. Da ga nametnete, dodajte `+PRIVEZNIK` imenu pregledača (vrednosti: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Da saznate koji priveznik Chromium zaista koristi (komanda preuzeta iz koda yt-dlp-a, ovde neisprobana):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Bez priveznika: `--password-store=basic` (napredno, neisprobano)

Chromium prihvata `--password-store=basic`: tada čuva svoj ključ u čitljivom obliku (stalan, opšte poznat ključ) i svoje nove kolačiće šifruje kao `v10`, koje yt-dlp čita bez priveznika (`chromium+basictext`). **To je manje bezbedno**: svaki program koji može da čita vaše fajlove može da dešifruje ove kolačiće. Koristite to samo ako razumete taj kompromis; već sačuvani kolačići verovatno se ne šifruju ponovo: prijavite se ponovo.

### 5.8 Poslednja mera

Ako je priveznik oštećen, **prvo napravite rezervnu kopiju**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Brisanje `login.keyring` briše **sve** lozinke koje sadrži (Wi-Fi, onlajn nalozi…): ne radite to ne razumevši posledice.

<a id="s6"></a>

## 6. Gde su fajlovi

Folder sa podacima je `$XDG_DATA_HOME/yt-dlp-GUI` (podrazumevano `~/.local/share/yt-dlp-GUI`), osim ako se `portable.flag` ne nalazi pored izvršnog fajla arhive (ili skripte `yt-dlp-gui.pyw`).

| Fajl ili folder | Sadržaj |
|---|---|
| `gui-config.json` | podešavanja (jezik, pregledač, folderi, izbor pregledača…) |
| `download-queue.json` | red preuzimanja |
| `custom-blocks.json` | prilagođeni blokovi opcija |
| `yt-dlp` | izvršni fajl koji je preuzeo pomoćnik |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | privremeni konfiguracioni fajlovi programa yt-dlp |
| `app/` | kopija programa koju je napravilo „Instaliraj u meni” |
| `~/.local/share/fonts/yt-dlp-GUI/` (van foldera sa podacima) | Noto font preuzet za korejski, japanski ili kineski; da ga uklonite: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Rešavanje problema

| Problem | Trag |
|---|---|
| AppImage se ne pokreće | pokrenuti ga iz terminala da se pročita greška; instalirati FUSE 2 (odeljak 2.2) ili dodati `--appimage-extract-and-run` |
| Ništa se ne prikazuje, ili greška biblioteke | proveriti verziju glibc-a: `ldd --version` mora prikazati 2.35 ili novije |
| Nema ikone na radnoj površini | GNOME podrazumevano ne prikazuje nijednu; koristite meni aplikacija |
| Prečica na radnoj površini sa upozorenjem | desni klik › „Dozvoli pokretanje” |
| Prevlačenje između domaćina i virtuelne mašine ne radi | to je funkcija VirtualBoxa (Guest Additions), a ne programa |
| Interfejs je pogrešne veličine | program prati sistemske fontove (Tk); probajte drugu veličinu sistemskog fonta |
| Ažuriranje programa yt-dlp ne uspeva | koristite „Ažuriranje i dijagnostika” u meniju opcija; inače preuzmite `yt-dlp_linux` i izaberite ga u prozoru za zamenu (izabrani fajl postaje izvršni) |
| Kvadratići umesto teksta (korejski, kineski, japanski…) | nijedan sistemski font ne sadrži ove znakove; na Debianu i Ubuntuu: `sudo apt install fonts-noto-cjk` (~90 MB), pa zatvorite i ponovo otvorite program; na drugim distribucijama instalirajte paket „Noto Sans CJK” te distribucije ; program može i sam da preuzme font (korejski, japanski, kineski) kada izaberete jezik, bez administratorskih prava |

<a id="s8"></a>

## 8. Prijava greške

Dugme „Prijavi grešku” priprema tehnički izveštaj u kojem su vaši folderi, korisničko ime i e-adrese sakriveni; ništa se ne šalje automatski. Za Linux dodajte:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

i napišite **kako** ste instalirali program (AppImage, arhiva, `.deb`, izvorni kod) i, kod problema sa kolačićima, **rezultat testa iz terminala** (odeljak 4), bez lepljenja vaših kolačića.

<a id="s9"></a>

## 9. Za programere

Testovi (na virtuelnom ekranu, bez pravog ekrana):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Izgradnja paketa (alati za izgradnju: `pip install -r packaging/requirements-build.txt`, plus `appimagetool`, čiju putanju daje promenljiva `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Rezultati su u `dist/`. Za najbolju kompatibilnost gradite na najstarijoj podržanoj distribuciji (glibc mašine za izgradnju je minimum koji se traži od mašina koje pokreću program). Korisne provere paketa `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

Jedina poznata greška u obliku je `dir-or-file-in-opt` (program smešten u `/opt`).

**Objavljivanje**: proveriti `__version__` u `yt-dlp-gui.pyw`, datirati odeljak verzije u `CHANGELOG-linux.md`, napraviti commit, pa napraviti i poslati oznaku `Linux-vX.Y.Z`. Tok „Release Linux” pokreće testove, gradi AppImage, arhivu i `.deb`, računa zbirove i pravi izdanje kao **pretpremijeru (pre-release)**, nikada kao „najnovije izdanje” (provera ažuriranja Windows verzije 0.1.7 ne sme tamo da nađe Linux oznaku).

Licenca: MIT, kao i ostatak repozitorijuma (vidi [LICENSE](../LICENSE)).
