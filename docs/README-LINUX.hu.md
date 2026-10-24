# yt-dlp GUI — Linuxos változat

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Előzetes változat.** Ez a dokumentum a [fő README](README.hu.md) kiegészítése: ugyanarról a programról van szó, de itt csak a Linuxra jellemző dolgokat tárgyaljuk (telepítés, sütik és kulcstartók, fájlok, hibaelhárítás). Az egyes verziók újdonságai a [CHANGELOG-linux.md](../CHANGELOG-linux.md) fájlban vannak. A fordításokat még anyanyelvi beszélőknek kell átnézniük; kétség esetén a francia és az angol szöveg az irányadó.

## Tartalom

1. [Az előzetes változat állapota](#s1)
2. [Telepítés](#s2)
3. [Első indítás és függőségek](#s3)
4. [A böngésző sütijei](#s4)
5. [Kulcstartók: kézi műveletek](#s5)
6. [Hol vannak a fájlok](#s6)
7. [Hibaelhárítás](#s7)
8. [Hiba jelentése](#s8)
9. [Fejlesztőknek](#s9)

<a id="s1"></a>

## 1. Az előzetes változat állapota

A linuxos változat a Windows 0.1.7 változat (befagyasztott, mintaként szolgáló) viselkedését követi. **GitHub előzetes kiadásként (pre-release)** jelenik meg `Linux-vX.Y.Z` címkékkel: soha nem a tároló „legfrissebb kiadásaként” szerepel.

**Amit kipróbáltunk** (Debian 12 virtuális gép, GNOME asztal, Python 3.11, minden böngészőben bejelentkezett valódi YouTube-fiók, 2026 októbere):

- **A Firefox, a Waterfox, a Floorp és a Zen Browser sütijei**: nyitott és zárt böngészővel is kiolvashatók.
- **A Google Chrome, a Chromium, a Brave, a Vivaldi, az Opera és a Microsoft Edge sütijei**: **zárt** böngészővel olvashatók, miután mindegyik böngészőt egyszer elindítottuk, és bejelentkeztünk benne a YouTube-ra (lásd az [5. szakaszt](#s5)). Az egyedi letöltés és a lejátszási lista-vizsgáló is működött.
- **LibreWolf**: csak akkor olvashatók ki, amíg nyitva van és be van jelentkezve (alapértelmezés szerint bezáráskor törli a sütiket).
- **Privát videó** a Firefox sütijeivel, valamint egy háromvideós lejátszási lista, amelyben az egyik privát.
- **Csomagok**: az AppImage-et és a `.tar.gz` archívumot a CI építi Ubuntu 22.04-en; a `.deb` csomagot Debian 12-n építettük, telepítettük, elindítottuk és eltávolítottuk; az AppImage-et, az archívumot és a `.deb` csomagot a virtuális gépben elindítottuk, a „Telepítés a menübe” / „Eltávolítás” funkciót pedig egérrel próbáltuk ki az AppImage-dzsel (az ikon felkerült, majd lekerült a menüből és az Asztalról).
- **Nyelv és betűtípus**: koreai nyelv kiválasztva koreai betűtípus nélküli gépen; a „Font needed” ablak felajánlja a betűtípust, letöltődik és ellenőrződik, a program újraindul, és a szöveg olvasható.

**Amit még nem próbáltunk ki**:

- más disztribúciókat (Ubuntu, Fedora, Arch, openSUSE…) és a GNOME-tól eltérő asztali környezeteket, a KDE Plasmát (KWallet) is beleértve;
- Flatpakként vagy Snapként telepített böngészőket (kivéve a LibreWolf Flatpak-elrendezését, amelyet megfigyeltünk);
- a Vivaldit, az Operát vagy az Edge-et **Chrome vagy Chromium telepítése nélkül** (lásd az [5. szakaszt](#s5));
- az aarch64 architektúrát (a program támogatja, de a csomagok csak x86_64-re készülnek);
- valódi Linuxos számítógépet, virtuális gépen kívül (valódi asztalt és hardvert);
- a fordításokat: még anyanyelvi beszélőknek kell átnézniük őket.

<a id="s2"></a>

## 2. Telepítés

### Melyik formátumot válasszuk

| Formátum | Kinek | Rendszergazdai jog | Menübejegyzés |
|---|---|---|---|
| **AppImage** | bármely friss 64 bites disztribúció | nem | „Telepítés a menübe” (2.3. szakasz) |
| **`.tar.gz` archívum** | ugyanaz, AppImage és FUSE nélkül | nem | „Telepítés a menübe” |
| **`.deb` csomag** | Debian, Ubuntu és származékaik | igen (`sudo`) | automatikus |
| **Forráskód** | fejlesztők, kipróbálás | nem | nincs |

Követelmények: 64 bites Linux (x86_64) 2022-es vagy újabb disztribúcióból (glibc 2.35 vagy újabb), mert a csomagok Ubuntu 22.04-en készülnek.

**Ha új vagy a Linuxban**: csak a `.deb` csomag települ „igazán”, és csak az jelenik meg a szoftverkezelőben. Az AppImage és az archívum közönséges fájl, illetve mappa, ott tarthatod, ahol akarod: az eltávolításuk a törlésüket jelenti, mint bármely más fájlét (2.2. és 2.5. szakasz). A beállításaik külön vannak, a `~/.local/share/yt-dlp-GUI` mappában (6. szakasz), és túlélik ezt a törlést.

A fájlok a [kiadások oldalán](https://github.com/harlockSuites/YT-dlp-GUI/releases) vannak: keresd a „Pre-release” jelölésű `Linux-v…` címkéket.

### 2.1 A letöltés ellenőrzése

Töltsd le ugyanabba a mappába a `SHA256SUMS-linux.txt` fájlt is, majd:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Minden meglévő fájlnál `OK`-nak kell megjelennie. Ez azt bizonyítja, hogy a fájlod azonos a közzétettel, azt nem, hogy ártalmatlan: a forráskód és az automatikus építés nyilvános.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Az AppImage-nek a FUSE 2 könyvtár kell:

| Disztribúció | Csomag |
|---|---|
| Debian, Ubuntu 22.04 és származékaik | `libfuse2` |
| Ubuntu 24.04 és újabb | `libfuse2t64` |
| Fedora | `fuse-libs` |

FUSE nélkül is indítsd el: magától kicsomagolja magát egy ideiglenes mappába:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

Az AppImage nincs „telepítve”: nem jelenik meg a szoftverkezelőben. Az eltávolításához töröld a fájlt:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Hogy az AppImage megjelenjen az alkalmazásmenüben az ikonjával, használd a **programban lévő „Telepítés a menübe…” funkciót** (2.3. szakasz): nincs begépelendő parancs.

### 2.3 Telepítés a menübe (rendszergazda nélkül)

A dupla kattintással indított AppImage nem hagy ikont az alkalmazásmenüben. A programban: a beállítások menü › **„Telepítés a menübe…”**. Az ablak:

- átmásolja a programot a `~/.local/share/yt-dlp-GUI/app/` mappába;
- megírja a `~/.local/share/applications/yt-dlp-gui.desktop` indítót és a `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png` ikont;
- ha be van jelölve a négyzet, parancsikont tesz az Asztalra („megbízhatóként” megjelölve a GNOME számára, ha van `gio` eszköz);
- majd felkínálja a „Frissítés” (újra átmásolja az éppen futó verziót) és az „Eltávolítás” lehetőséget.

Az „Eltávolítás” csak azt távolítja el, amit a telepítés létrehozott, és **megtartja a beállításaidat** és a letöltött eszközöket. A belső jelölésünk (`X-YtDlpGui-Installer=1`) nélküli indítót soha nem törli.

Korlátok: az ablak az AppImage-ből és az archívumból érhető el. A forráskódból az AppImage-re irányít; a `.deb` csomagból elmagyarázza, hogy a program már benne van a menüben.

Ha az Asztal parancsikonja figyelmeztetést mutat: jobb kattintás az ikonra › „Indítás engedélyezése”. Egyes asztali környezetek (alapértelmezésben a GNOME) nem jelenítenek meg ikont az Asztalon: a menü indítója minden esetben működik.

Mindent kézzel eltávolítani:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

Ha a `.deb` csomag már telepítve van, ne használd ezt a funkciót: a program már benne van a menüben, és egy második „yt-dlp GUI” bejegyzés jelenne meg (előbb távolítsd el a `.deb` csomagot a `sudo apt remove yt-dlp-gui` paranccsal, ha ezt a módszert választod).

### 2.4 `.deb` csomag

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

A program a `/opt/yt-dlp-gui` mappába kerül, a `/usr/bin/yt-dlp-gui` hivatkozással, a menü indítójával, az ikonnal és a licenccel (`/usr/share/doc/yt-dlp-gui/`). A `libc6 (>= 2.35)` és a `libx11-6` csomagtól függ.

Az eltávolításához (a beállításaidat, a `~/.local/share/yt-dlp-GUI` mappában, soha nem érinti):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 `.tar.gz` archívum

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Hogy a beállítások és az eszközök **a kicsomagolt mappán belül** maradjanak (USB-meghajtó, nyomok nélküli kipróbálás), hozz létre egy üres `portable.flag` fájlt a futtatható fájl mellett:

```bash
touch yt-dlp-gui/portable.flag
```

E fájl nélkül az adatok a `~/.local/share/yt-dlp-GUI` mappába kerülnek (6. szakasz).

Az archívum nincs „telepítve”: nem jelenik meg a szoftverkezelőben. Az eltávolításához töröld a kicsomagolt mappát:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Forráskódból

```bash
python3 yt-dlp-gui.pyw
```

Forráskódból a beállítások és a letöltött eszközök ugyanabba a mappába kerülnek, mint a telepített változatoknál (`~/.local/share/yt-dlp-GUI`): a forráskód újbóli letöltése vagy a mappájának törlése nem törli őket. Ha az adatokat a forráskód mappájában szeretnéd tartani (nyomok nélküli kipróbálás), hozz létre egy üres `portable.flag` fájlt a `yt-dlp-gui.pyw` mellett.

Python 3 kell Tkinterrel:

| Disztribúció | Csomag |
|---|---|
| Debian, Ubuntu és származékaik, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Frissítések

A napi ellenőrzés (amely a beállítások menüben kikapcsolható) a `Linux-vX.Y.Z` verziókat keresi, az előzetes kiadásokat is beleértve, és **soha** nem ajánl Windows-verziót. Megnyitja a telepítésednek megfelelő fájl letöltési oldalát (AppImage, archívum vagy `.deb`); **semmi nem települ automatikusan**. A frissítéshez:

- **a menübe telepített AppImage vagy archívum**: töltsd le az új AppImage-et, indítsd el, majd „Telepítés a menübe… › Frissítés”;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **nem telepített archívum**: csomagold ki az új archívumot a régi helyére.

### 2.8 Mindent eltávolítani, az adatokat is

A program eltávolítása után (2.3–2.5. szakasz), hogy a beállításaidat, a sort és a letöltött eszközöket (yt-dlp, ffmpeg, deno) is töröld:

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

A letöltött videóid soha nincsenek ebben a mappában.

<a id="s3"></a>

## 3. Első indítás és függőségek

Az első indításkor a telepítési segéd felajánlja a **yt-dlp** (`yt-dlp_linux`), az **ffmpeg** (a yt-dlp hivatalos buildjeinek `.tar.xz` archívuma) és a **deno** letöltését a GitHub-tárolóikból. Az SHA-256 összegeket ellenőrzi, rendszergazdai jog nem kell, a fájlok a `~/.local/share/yt-dlp-GUI` (yt-dlp) és a `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno) mappába kerülnek. A beállítások menüből továbbra is elérhető.

Csak az ffmpeg és az ffprobe nélkülözhetetlen; a deno ajánlott (másodlagos hangsávok). Az **AtomicParsley, az MKVToolNix és az aria2** nem kötelező: a „Függőségek” ablak megmutatja a csomagkezelőd parancsát, amelyet egy terminálba kell másolni. A program soha nem futtatja le maga. Ugyanezek a parancsok:

| Csomagkezelő | Parancs |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. A böngésző sütijei

A yt-dlp a sütiket **helyben** olvassa ki az általad választott böngészőből (másodlagos hangsávok, feliratok, privát videók, tagoknak szóló tartalom). Alapértelmezés szerint a program a Linuxon leggyakrabban használt öt böngészőt kínálja (Firefox, Google Chrome, Chromium, Brave, Vivaldi). A beállítások menü **„Böngészők a cookie-khoz…”** pontja megnyitja a „Böngészők a cookie-khoz” ablakot, amely 11-et kínál: jelöld be, amelyekre szükséged van; a ✔ azokat jelöli, amelyeknek a profilmappája létezik a számítógépeden.

| Böngésző | A yt-dlp így olvassa | Kulcstartó | Keresett profilmappák |
|---|---|---|---|
| Firefox | `firefox` | nem | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | igen | `~/.config/google-chrome` |
| Chromium | `chromium` | igen | `~/.config/chromium` |
| Brave | `brave` | igen | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | igen | `~/.config/vivaldi` |
| Opera | `opera` | igen | `~/.config/opera` |
| Microsoft Edge | `edge` | igen | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + a profil mappája | nem | `~/.librewolf`, `~/.config/librewolf`… (a többinél ugyanez a séma), a Flatpakkal együtt |

A Firefox származékainak nincs a yt-dlp által ismert neve: a program megkeresi a `cookies.sqlite` adatbázisukat (a mappáik alatt legfeljebb három szintig), és a legutóbb használt profil mappáját adja át a yt-dlp-nek. Az `XDG_CONFIG_HOME` értékét figyelembe veszi, ha abszolút útvonal.

A lista melletti **jelző** az állapotot mutatja: piros (kikapcsolva vagy hibás), narancs (nincs tesztelve vagy folyamatban), zöld (a sütik kiolvasva). A ↻ gomb tesztet indít; a súgóbuborék elmagyarázza a hibát. Az a teszt, amely **0 sütit** olvas ki, soha nem zöld.

### Gyakori esetek

| Amit látsz | Valószínű ok | Mit tegyél |
|---|---|---|
| „Extracted 0 cookies”, majd „Sign in to confirm you're not a bot” | a böngésző nem tart sütit a lemezen (a LibreWolf alapértelmezés szerint bezáráskor törli; soha nem bejelentkezett profil; privát mód) | hagyd nyitva és YouTube-ra bejelentkezve, vagy kapcsold ki a sütik bezáráskori törlését az adatvédelmi beállításaiban |
| „Item does not exist!” Chrome, Chromium, Brave, Vivaldi, Opera vagy Edge esetén | a yt-dlp nem találta a böngésző kulcsát az asztali kulcstartóban | indítsd el egyszer a böngészőt, jelentkezz be a YouTube-ra, zárd be, ismételd meg a tesztet; különben [5. szakasz](#s5) |
| „Could not copy Chrome cookie database” vagy „database is locked” | a böngésző zárolja az adatbázisát, amíg fut | zárd be, majd ismételd meg a tesztet |
| „Failed to decrypt” | olyan kulccsal titkosított sütik, amelyet a yt-dlp nem kapott meg | [5. szakasz](#s5) |

### Böngésző tesztelése terminálból

Ez a legjobb módja a pontos hiba megtekintésének (cseréld az `IDENTIFIER` szót bármely YouTube-videó azonosítójára):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Keresendő sorok: `Extracted N cookies from chromium` (N-nek 0-nál nagyobbnak kell lennie), `Chosen keyring: GNOMEKEYRING` (a kiválasztott kulcstartó) és `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (a `v11` sütikhez kell a kulcstartó, a `v10` sütikhez nem).

Firefox-származéknál add meg a profil mappáját. Megkeresése:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

Flatpak-telepítésnél a `~/.var/app` mappában keress:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Majd a `cookies.sqlite`-ot tartalmazó mappával:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Kulcstartók: kézi műveletek

### Mire való

A Chromium-családba tartozó böngészők (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) titkosítják a sütiket. A titkosítókulcs az **asztali kulcstartóban** van: GNOME alatt, XFCE-n, Cinnamonon, MATE-en… a GNOME Keyringben (vagy egy kompatibilis megfelelőjében, a „Secret Service”-en keresztül), KDE alatt a KWalletben. A visszafejtéshez a yt-dlp ezt a kulcsot kéri el a kulcstartótól. A Firefoxnak és a származékainak nincs rá szüksége.

Két hasznos tény:

- **A kulcs csak a böngésző első elindítása után létezik.** A virtuális gépünkön az „Item does not exist!” hiba eltűnt, miután mindegyik böngészőt egyszer elindítottuk, és bejelentkeztünk benne a YouTube-ra. Az első hiba pontos okát nem sikerült biztosan megállapítani: a kulcstartó létezett, alapértelmezett volt és fel volt oldva.
- **Melyik kulcstartót használja a yt-dlp**, az az észlelt asztali környezettől függ (az `XDG_CURRENT_DESKTOP` és a `DESKTOP_SESSION` változók), a yt-dlp kódja szerint (2026 októbere):

| Észlelt asztali környezet | A yt-dlp által használt kulcstartó |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, fel nem ismert asztali környezet (önmagukban álló ablakkezelők: sway, i3…) | egyik sem: egyszerű szöveg (`BASICTEXT`) |

Az utolsó esetben a yt-dlp csak a `v10` sütiket olvassa: ha a böngésződ a kulcsát a GNOME Keyringben tárolja, a `v11` sütijei nem fognak visszafejtődni. Ekkor a kulcstartót terminálból kell kényszeríteni (5.6. szakasz); a program ezt a beállítást még nem kínálja.

A kulcstartóban keresett elemek neve „*név* Safe Storage”. A yt-dlp kódja szerint ez a Chrome és a Vivaldi esetén **„Chrome Safe Storage”**, a Chromium, az Opera és az Edge esetén **„Chromium Safe Storage”**, a Brave esetén **„Brave Safe Storage”**. A virtuális gépünkön a Chrome és a Chromium is telepítve volt és el volt indítva: nem tudjuk, hogy a Vivaldi, az Opera vagy az Edge egyedül is működne-e.

### 5.1 Létezik a kulcstartó?

```bash
ls -la ~/.local/share/keyrings/
```

Egy `login.keyring` fájlt kell látnod (a „login” kulcstartó). Ezután: melyik kulcstartó az **alapértelmezett**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Válasz: `(objectpath '/org/freedesktop/secrets/collection/login',)`: van alapértelmezett kulcstartó. Válasz: `'/'`: **nincs**, lépj az 5.4. szakaszra.

### 5.2 Zárolva van?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: fel van oldva. `(<true>,)`: zárolva van; nyisd meg a Seahorse-szal (5.4. szakasz), amely elkéri a jelszavát.

### 5.3 Benne van a böngészőm kulcsa?

Listázd az elemeket:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

A válasz számra végződő útvonalakat ad (`…/login/1`, `…/login/2`…). Mindegyik nevének kiolvasásához (igazítsd a számok listáját):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Például ezeket kell látnod: `Chromium Safe Storage`, `Chrome Safe Storage` vagy `Brave Safe Storage`. Az üres nevek ártalmatlanok. Ha a böngésződ neve hiányzik: indítsd el egyszer, jelentkezz be a YouTube-ra, zárd be, majd futtasd újra ezt a parancsot.

### 5.4 Kulcstartó létrehozása vagy feloldása a Seahorse-szal

Telepítsd a Seahorse-t („Jelszavak és kulcsok”) és a kapcsolódó eszközöket. A pontos parancs a program „Böngészők a cookie-khoz” ablakában is megvan:

| Csomagkezelő | Parancs |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Ezután nyisd meg:

```bash
seahorse
```

- **Nincs alapértelmezett kulcstartó**: hozz létre egyet („+” gomb vagy Fájl › Új › jelszókulcstartó menü), nevezd el „Login”-nak, majd jobb kattintás rajta › „Beállítás alapértelmezettként”. A pontos feliratok a Seahorse verziójától függően eltérhetnek.
- **Zárolt kulcstartó**: dupla kattintás vagy jobb kattintás › „Feloldás”, majd írd be a jelszavát (te írd be, a program soha nem kéri el).
- **Automatikus bejelentkezés**: a jelszóval védett kulcstartó nem tud magától megnyílni, ha a munkamenet indításakor nem írsz be jelszót; zárolva marad, amíg fel nem oldod (vagy amíg ugyanazt a jelszót nem használod a munkamenethez és a kulcstartóhoz).

Ezután **indítsd el a böngészőt, jelentkezz be a YouTube-ra, zárd be**, és ismételd meg a tesztet (4. szakasz).

### 5.5 KDE Plasma (KWallet)

KDE alatt a yt-dlp a KWalletet kérdezi le (`kwallet-query`). A kezelő neve a disztribúciótól függően `kwalletmanager` (vagy `kwalletmanager5`). Ezt a beállítást a tesztjeinkben **nem próbáltuk ki**.

### 5.6 A kulcstartó kényszerítése a yt-dlp-re (terminál)

A program a yt-dlp-re bízza a kulcstartó kiválasztását az asztali környezet alapján. Kényszerítéséhez fűzz `+KULCSTARTÓ` részt a böngésző nevéhez (értékek: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Hogy megtudd, melyik kulcstartót használja valójában egy Chromium (a yt-dlp kódjából átvett parancs, itt nem próbáltuk ki):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Kulcstartó nélkül: `--password-store=basic` (haladó, nem kipróbált)

A Chromium elfogadja a `--password-store=basic` kapcsolót: ilyenkor a kulcsát nyíltan tárolja (egy rögzített, közismert kulcsot), és az új sütiket `v10` formában titkosítja, amelyeket a yt-dlp kulcstartó nélkül olvas (`chromium+basictext`). **Ez kevésbé biztonságos**: bármely program, amely olvashatja a fájljaidat, visszafejtheti ezeket a sütiket. Csak akkor használd, ha érted ezt a kompromisszumot; a már elmentett sütiket valószínűleg nem kódolja át újra: jelentkezz be újra.

### 5.8 Végső megoldás

Ha egy kulcstartó megsérült, **előbb készíts róla biztonsági másolatot**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

A `login.keyring` törlése **minden** benne lévő jelszót töröl (Wi-Fi, online fiókok…): ne tedd meg a következmények megértése nélkül.

<a id="s6"></a>

## 6. Hol vannak a fájlok

Az adatmappa a `$XDG_DATA_HOME/yt-dlp-GUI` (alapértelmezés szerint `~/.local/share/yt-dlp-GUI`), kivéve, ha a `portable.flag` az archívum futtatható fájlja (vagy a `yt-dlp-gui.pyw` szkript) mellett van.

| Fájl vagy mappa | Tartalom |
|---|---|
| `gui-config.json` | beállítások (nyelv, böngésző, mappák, a böngészők kiválasztása…) |
| `download-queue.json` | letöltési sor |
| `custom-blocks.json` | egyéni beállításblokkok |
| `yt-dlp` | a segéd által letöltött futtatható fájl |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | a yt-dlp ideiglenes konfigurációs fájljai |
| `app/` | a „Telepítés a menübe” által készített programmásolat |
| `~/.local/share/fonts/yt-dlp-GUI/` (az adatmappán kívül) | a koreaihoz, japánhoz vagy kínaihoz letöltött Noto betűtípus; eltávolítása: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Hibaelhárítás

| Probléma | Támpont |
|---|---|
| Az AppImage nem indul | indítsd terminálból a hiba elolvasásához; telepítsd a FUSE 2-t (2.2. szakasz) vagy add hozzá az `--appimage-extract-and-run` kapcsolót |
| Semmi nem jelenik meg, vagy könyvtárhiba | ellenőrizd a glibc verzióját: az `ldd --version` 2.35-öt vagy újabbat mutasson |
| Nincs ikon az Asztalon | a GNOME alapértelmezés szerint nem mutat ilyet; használd az alkalmazásmenüt |
| Az Asztal parancsikonja figyelmeztetéssel jelenik meg | jobb kattintás › „Indítás engedélyezése” |
| A húzd-és-ejtsd nem működik a gazdagép és egy virtuális gép között | ez a VirtualBox (Guest Additions) funkciója, nem a programé |
| A felület mérete rossz | a program a rendszer betűtípusait követi (Tk); próbálj másik rendszerbetűméretet |
| A yt-dlp frissítése nem sikerül | használd a „Frissítés és diagnosztika” pontot a beállítások menüben; különben töltsd le a `yt-dlp_linux` fájlt, és válaszd ki a csere ablakban (a kiválasztott fájl futtathatóvá válik) |
| Négyzetek a szöveg helyén (koreai, kínai, japán…) | a rendszer egyik betűtípusa sem tartalmazza ezeket a karaktereket; Debianon és Ubuntun: `sudo apt install fonts-noto-cjk` (~90 MB), majd zárd be és nyisd meg újra a programot; máshol a disztribúció „Noto Sans CJK” csomagját telepítsd; a program a nyelv kiválasztásakor maga is le tudja tölteni a betűtípust (koreai, japán, kínai), rendszergazdai jog nélkül |

<a id="s8"></a>

## 8. Hiba jelentése

A „Hiba jelentése” gomb olyan műszaki jelentést készít, amelyben a mappáid, a felhasználóneved és az e-mail-címeid el vannak rejtve; semmi nem kerül automatikusan elküldésre. Linuxon add hozzá:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

és írd meg, **hogyan** telepítetted a programot (AppImage, archívum, `.deb`, forráskód), süti-probléma esetén pedig **a terminálos teszt eredményét** (4. szakasz), a sütijeid beillesztése nélkül.

<a id="s9"></a>

## 9. Fejlesztőknek

Tesztek (virtuális képernyőn, valódi képernyő nélkül):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

A csomagok építése (építőeszközök: `pip install -r packaging/requirements-build.txt`, valamint az `appimagetool`, amelynek útvonalát az `APPIMAGETOOL` változó adja):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Az eredmények a `dist/` mappában vannak. A legjobb kompatibilitásért a legrégebbi támogatott disztribúción építs (az építőgép glibc-je a minimum, amelyet a programot futtató gépektől elvárunk). A `.deb` hasznos ellenőrzései:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

Az egyetlen ismert formai hiba a `dir-or-file-in-opt` (az `/opt` alá csomagolt program).

**Közzététel**: ellenőrizd a `__version__` értékét a `yt-dlp-gui.pyw` fájlban, keltezd a verzió szakaszát a `CHANGELOG-linux.md` fájlban, készíts commitot, majd hozd létre és told fel a `Linux-vX.Y.Z` címkét. A „Release Linux” munkafolyamat lefuttatja a teszteket, megépíti az AppImage-et, az archívumot és a `.deb` csomagot, kiszámolja az összegeket, és a kiadást **előzetes kiadásként (pre-release)** hozza létre, soha nem „legfrissebb kiadásként” (a Windows 0.1.7 változat frissítésellenőrzése nem találhat ott Linux-címkét).

Licenc: MIT, mint a tároló többi része (lásd [LICENSE](../LICENSE)).
