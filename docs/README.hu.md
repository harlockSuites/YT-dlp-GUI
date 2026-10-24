# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Grafikus felület a [yt-dlp](https://github.com/yt-dlp/yt-dlp) programhoz, amely mindenki számára elérhetővé teszi, miközben teljes mértékben kihasználja a képességeit.

> **Fejlesztés alatt álló projekt.** Egyes funkciók változhatnak, hiányosak lehetnek vagy hibákat tartalmazhatnak. Windowson érhető el; **Linuxra előzetes verzió** is elérhető, kevésbé kipróbálva.

🐧 **Linux** : [README-LINUX (français)](../README-LINUX.md) · [README-LINUX (English)](README-LINUX.en.md)

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funkciók

### Egyedi letöltő és sor

- **Beállítások**: maximális minőség (akár 4K), csak hang (MP3), feliratok (vtt, srt, ass formátum), feliratok és indexkép beágyazása, fő hangnyelv, másodlagos hangsávok (többsávos MKV-fájl) és „szkriptblokkok” könyvtára (utófeldolgozás, exportálás, hálózat, viselkedés), amelyet saját blokkokkal bővíthet.
- **Több hangsáv**: az MKV-fájlban minden hangsáv viseli a nyelve címkéjét („hun”, „eng”…); a lejátszó megjeleníti az audiomenüben.
- **Előállított parancs**: a választásainak megfelelő yt-dlp-parancs élőben látható.
- **Sor**: adja hozzá az aktuális URL-t, majd indítsa el az egész sort, egy elemtől kezdve, egyetlen videót vagy egy tartományt; szüneteltetés és folytatás, az aktuális elem kihagyása, leállítás a részleges fájlok takarításával. A sor munkamenetek között megmarad.
- **Már létező fájlnevek**: az a különálló videó, amelynek a neve már létezik a célmappában, utótagot kap (`_2`, `_3`…), hogy semmi se íródjon felül. Az ezzel a letöltővel letöltött lejátszási listát nem számozza újra: a mappában már meglévő videókat kihagyja („has already been downloaded”).

### Lejátszási lista vizsgáló

- **Elemzés**: a lejátszási lista minden videója megjelenik az elérhető hangsávokkal és feliratokkal; a rejtett, privát vagy törölt elemeket a program kihagyja, anélkül hogy a többit akadályozná.
- **Általános szabályok** (minőség, csak hang, feliratformátum és beágyazás, indexkép, számozás, nyelvek, szkriptblokkok, célmappa) **videónkénti kivételekkel** a fő nyelvre, a másodlagos sávokra és a feliratokra.
- **Színkód**: piros, ha hiányzik a fő nyelv, narancs, ha egy másodlagos sáv vagy felirat hiányzik.
- **A kijelölés letöltése** naplóval, szüneteltetéssel, folytatással és kihagyással; ha a kért sávok nem léteznek, a videót azok nélkül újrapróbálja, majd egy **összegzés** mutatja, mi sikerült, mit módosított a program, és mi hiúsult meg.

### Intelligens mappa és nyilvántartás

- **Intelligens mappa**: a yt-dlp kihagyja a már letöltött videókat a célmappában tárolt nyilvántartás segítségével. A `.yt-dlp-registre.json` fájl minden videó azonosítóját, URL-jét, címét, hosszát, fájlnevét és dátumát tartalmazza; a yt-dlp által olvasott `.yt-dlp-archive.txt` ebből származik.
- **Visszamenőleges ellenőrzés**: ha a kijelölt videók már a mappában vannak, de a nyilvántartásban nem szerepelnek, egy ablak felajánlja a felvételüket és a kihagyásukat (a címek összehasonlításával). A téves találatok kijelölését megszüntetheti.
- **Nyilvántartás frissítése**: megszámolja a mappában, a nyilvántartásban lévő és a hiányzó videókat, majd a YouTube-on megkeresi a hiányzó adatokat (cím, valamint hossz az ffprobe segítségével). A megerősítése nélkül semmi nem kerül be, és két gomb megnyitja a helyi fájlt vagy a megtalált YouTube-hivatkozást az ellenőrzéshez.

![yt-dlp GUI](img/registry.en.png)

### Böngészősütik

- Válassza ki azt a böngészőt (Chrome, Firefox, Edge, Brave, Opera), amelynek sütijeit a yt-dlp helyben olvassa: a másodlagos hangsávokhoz és egyes feliratokhoz szükségesek. **A Firefox ajánlott.**
- **Tesztjeink eredményei** (Windows 11, 2026. október, minden böngészőben bejelentkezett YouTube-fiókkal): a **Firefox** működik, nyitott és zárt böngészővel is. Az **Opera** **csak zárt böngészővel** működik: nyitva zárolja a sütiadatbázisát, és a yt-dlp ilyenkor a „Could not copy Chrome cookie database” üzenetet jeleníti meg. A **Chrome, az Edge és a Brave** zárt állapotban is hibázik: úgy titkosítják a sütiket, hogy a yt-dlp nem mindig tudja beolvasni őket. Ezek a korlátok a böngészőktől és a yt-dlp-től származnak, nem a programtól, és a frissítéseikkel változhatnak.
- Ha a böngésző úgy van beállítva, hogy **bezáráskor törli a sütiket** (vagy privát módban böngészik), nem marad olvasható süti a lemezen: a yt-dlp semmit sem tud kinyerni, sem Chrome-mal, Edge-dzsel, Brave-vel, sem Firefoxszal. Chrome, Edge és Brave esetén ez csapda: be kell zárni a böngészőt, ami törli a sütiket. Kapcsolja ki ezt a beállítást, vagy tartsa meg a youtube.com és a google.com sütijeit.
- Egy **jelzőfény** mutatja az állapotot: piros, ha ki van kapcsolva vagy hibás, narancs, ha nincs tesztelve vagy folyamatban van, zöld, ha a sütik betöltődtek. A ↻ gomb tesztet indít, a buborékszöveg pedig elmagyarázza az állapotot vagy a hibát.
- **Linuxon (előzetes verzió)**: alapértelmezés szerint a Firefox, a Google Chrome, a Chromium, a Brave és a Vivaldi érhető el, ezek a leggyakrabban használtak ezen a rendszeren; a beállítások menü „Böngészők a cookie-khoz” ablakában legfeljebb 11 böngésző jelölhető be (az Opera, a Microsoft Edge, a LibreWolf, a Waterfox, a Floorp és a Zen Browser is). A Chromium-családba tartozó böngészők az asztali kulcstartóval (GNOME Keyring, KWallet) védik a sütiket: feloldottnak kell lennie, vagyis grafikus munkamenetnek kell nyitva lennie. Csak a Firefox sütijeinek olvasását próbáltuk ki bejelentkezett YouTube-fiókkal (privát videókkal együtt); **a Firefox ajánlott**.

### Telepítő varázsló, függőségek és a yt-dlp frissítései

- **Telepítő varázsló**: az első indításkor felajánlja a yt-dlp és az ffmpeg letöltését a hivatalos GitHub-tárolókból. Az SHA-256 ellenőrzőösszeg ellenőrzésre kerül, és nincs szükség rendszergazdai jogosultságra.
- **Függőségek**: a külön ablak ellenőrzi az ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 és deno meglétét, és Chocolatey segítségével telepítheti őket. Csak az ffmpeg és az ffprobe nélkülözhetetlen; a deno ajánlott (másodlagos hangsávok); az AtomicParsley, az MKVToolNix és az aria2 választható: a program nélkülük is működik. Linuxon a varázsló letölti az ffmpeg, az ffprobe és a deno eszközt (ellenőrzött SHA-256 összeg, rendszergazdai jogok nélkül); az AtomicParsley, az MKVToolNix és az aria2 esetén az ablak a csomagkezelő (apt, dnf, pacman vagy zypper) parancsát mutatja, amelyet terminálba kell másolni.
- **Frissítés és diagnosztika**: frissíti a yt-dlp-t (`yt-dlp -U`) vagy lecseréli a futtatható fájlját, megmutatja a verzióját, és ellenőrzi a felület által használt kapcsolókat.
- **Programfrissítés**: a naponta végzett (kikapcsolható) ellenőrzés egy diszkrét sávval jelzi az új verziót; a külön ablak megmutatja az újdonságokat, és megnyitja a telepítésének megfelelő letöltést (telepítő vagy hordozható változat). Semmi nem települ automatikusan. A beállítások menü kapcsolója („Frissítések keresése indításkor”) be- vagy kikapcsolja az automatikus ellenőrzést, a „Programfrissítés keresése…” pedig kérésre lefuttatja. Linuxon ez az architektúrájának megfelelő AppImage vagy `.tar.gz` archívum.

### Felület és nyelvek

- A vezérlők az ablak szélességéhez igazodva tördelődnek; a tartalom függőlegesen görgethető, a vizsgáló táblázata pedig vízszintesen is.
- **15 nyelvű** felület: francia, angol, spanyol, portugál, olasz, lengyel, magyar, szerb, orosz, vietnami, kínai, hindi, japán, koreai és filippínó. A nyelvváltás újraindításkor lép érvénybe, azonnali újraindítási lehetőséggel.

### Hiba jelentése

- A „Hiba jelentése” gomb műszaki jelentést készít: a program, a Python, az operációs rendszer és a yt-dlp verziója, ártalmatlan beállítások és a napló utolsó sorai. A mappái, a felhasználóneve és az e-mail-címei el vannak takarva. A jelentés GitHubon való elküldéséhez ingyenes GitHub-fiók szükséges.
- Semmi nem megy el automatikusan: Ön átnézi és szerkeszti a jelentést, majd megnyit egy előre kitöltött GitHub-hibajegyoldalt (vagy kimásolja a jelentést).

## Telepítés

- **Telepítő (ajánlott)**: töltse le a `yt-dlp-gui-setup-X.Y.Z.exe` fájlt a [kiadások oldaláról](https://github.com/harlockSuites/YT-dlp-GUI/releases), és futtassa. Windows 10 vagy 11 (64 bites), rendszergazdai jogosultság nélkül; Python nem szükséges.
- **Hordozható változat**: töltse le a `yt-dlp-gui-portable-X.Y.Z.zip` fájlt, csomagolja ki bárhová, és futtassa a `yt-dlp-gui.exe` fájlt; a beállítások ebben a mappában maradnak.
- **Linux, AppImage (előzetes verzió)**: töltse le a `yt-dlp-gui-X.Y.Z-x86_64.AppImage` fájlt a [kiadások oldaláról](https://github.com/harlockSuites/YT-dlp-GUI/releases), tegye futtathatóvá (`chmod +x`), és indítsa el. Szüksége van a `libfuse2` csomagra (`libfuse2` vagy `fuse-libs`); nélküle indítsa a `--appimage-extract-and-run` kapcsolóval.
- **Linux, archívum (előzetes verzió)**: töltse le a `yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz` fájlt, csomagolja ki (`tar xzf`), és futtassa a `./yt-dlp-gui/yt-dlp-gui` parancsot. A beállítások és a letöltött eszközök a `~/.local/share/yt-dlp-GUI` mappában vannak; eltávolításhoz törölje ezt a mappát és a program fájlját vagy mappáját.
- **Linux, hozzáadás az alkalmazásmenühöz (előzetes)**: az AppImage-ből vagy az archívumból a beállítások menü › „Telepítés a menübe” a programot a `~/.local/share/yt-dlp-GUI/app` mappába másolja, az indítót és az ikont felveszi az asztal menüjébe, igény szerint az Asztalra is parancsikont tesz, rendszergazdai jog nélkül. Ugyanebben az ablakban frissíthető vagy eltávolítható; a beállítások megmaradnak.
- **Linux, .deb csomag (előzetes)**: Debianon, Ubuntun és származékaikon töltse le a `yt-dlp-gui_X.Y.Z_amd64.deb` fájlt, és telepítse a `sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb` paranccsal. A program ikonnal megjelenik az alkalmazásmenüben; a `sudo apt remove yt-dlp-gui` eltávolítja, a beállítások (`~/.local/share/yt-dlp-GUI`) megmaradnak.
- **Linux, követelmények és ellenőrzés**: 64 bites Linux (x86_64), 2022-es vagy újabb disztribúció (glibc 2.35 vagy újabb). Egy fájl ellenőrzéséhez töltse le a `SHA256SUMS-linux.txt` fájlt is, és ugyanabban a mappában futtassa: `sha256sum -c SHA256SUMS-linux.txt --ignore-missing`. A Linuxos fájlok külön jelennek meg, azokban a kiadásokban, amelyek címkéje „Linux-v” előtaggal kezdődik (a GitHubon „Pre-release” jelölést kapnak); az oldalon alapértelmezésként megjelenő kiadás a Windowsos.
- **Forráskódból**: lásd lentebb a „Követelmények” és a „Gyors kezdés” részt.
- **Eltávolítás**: Windows Beállítások › Alkalmazások › Telepített alkalmazások › yt-dlp GUI, vagy a Start menü „Eltávolítás” parancsikonja. A program felajánlja az adatai (beállítások, várólista, letöltött yt-dlp és ffmpeg) törlését is; a videóid soha nem törlődnek. Mivel a telepítés Windows-fiókonként külön van, a program csak azon fiók listájában jelenik meg, amelyik telepítette. A hordozható változatnál elég a mappáját törölni. A Chocolatey-vel külön telepített eszközök (ffmpeg, Deno…) nem törlődnek.
- **Víruskeresős elemzés (VirusTotal)**: a 0.1.7-es verziót 2026. október 21-én elemezték. A [telepítőt](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c) a 69 motorból 4 (Arctic Wolf, Microsoft, SecureAge, Skyhigh) jelöli általános heurisztikus észleléssel; a [hordozható verzió indítóját](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a) a 70-ből 5 (Arctic Wolf, CrowdStrike Falcon, Microsoft, SecureAge, Zillya), a [hordozható ZIP-archívumot](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706) pedig a 66-ból 1 (Zillya, magán az archívumon) jelöli. Valószínűleg téves riasztások, mert a program tömörített és nincs aláírva. Ezek az eredmények csak erre a verzióra érvényesek. Ha bizonytalan, ellenőrizze az SHA-256 összeget.
- **Code signing policy**: a fájlok nincsenek digitálisan aláírva. Az ingyenes aláírásra a SignPath Foundationnél benyújtott kérelmet 2026. október 19-én elutasították (a projekt még nem elég ismert nyilvánosan), és később újra benyújtható; a [kódaláírási irányelv](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) a tervezett folyamatot írja le, ha sikerül tanúsítványt szerezni.
- **Windows SmartScreen figyelmeztetés**: a telepítő nincs digitálisan aláírva, ezért a Windows megjelenítheti: „A Windows megvédte a számítógépét”. Kattintson a „További információ”, majd a „Futtatás mindenképpen” lehetőségre. A fájl hitelességét ellenőrizheti, ha összeveti az SHA-256 összegét a minden kiadással közzétett `SHA256SUMS.txt` fájlban szereplővel:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## A Windows és a böngészők figyelmeztetései

Ez a program ingyenes, egyetlen személy adja ki, és a fájljai **még nincsenek digitálisan aláírva**. Egy új fájlnak, amelyet szinte senki sem töltött le, nincs „hírneve”: a böngészők és a Windows ezért **még biztonságos programnál is** figyelmeztetést jelenítenek meg. A figyelmeztetés nem bizonyítja, hogy a fájl veszélyes, hiánya pedig nem bizonyítja, hogy biztonságos: így ellenőrizheti saját maga.

- **Böngésző** (Firefox, Chrome, Edge, Brave): a letöltést „ritkán letöltöttként” vagy „vírust vagy kártevőt tartalmazóként” jelölheti meg. Ez a fájl hírnevének automatikus vizsgálata. Először ellenőrizze az ellenőrző összeget (lent); ha egyezik, kiválaszthatja a letöltést engedélyező vagy megtartó lehetőséget.
- **Windows SmartScreen**: „A Windows megvédte a számítógépét” → kattintson a „További információ”, majd a „Futtatás mindenképp” gombra, az ellenőrző összeg ellenőrzése **után**.
- **Microsoft Defender (Windows Biztonság)**: karanténba teheti vagy törölheti a fájlt, a „Trojan:Win32/Wacatac.C!ml” megjelöléssel. Az `!ml` végződés automatikus, gépi tanuláson alapuló észlelést jelent, ami új, aláíratlan fájloknál gyakori; ezeket az észleléseket téves riasztásként jelentettük a Microsoftnak. Az SHA-256 összeg ellenőrzése után (lent) visszaállíthatja a fájlt: Windows Biztonság › Vírus- és fenyegetésvédelem › Védelmi előzmények › nyissa meg az elemet › Műveletek › „Engedélyezés az eszközön” (vagy „Visszaállítás”). Ne kapcsolja ki a Windows védelmét, és ne adjon hozzá az egyetlen fájlnál szélesebb kivételt.
- **Víruskereső**: néhány motor általános észlelést jelez (lásd fent a víruskeresős elemzést). A fájl elemzésének megtekintéséhez illessze be az SHA-256 összegét a [VirusTotal](https://www.virustotal.com/) keresőjébe: ha a fájl már ismert, feltöltés nélkül megkapja a jelentést.
- **Ellenőrizze a letöltést**: töltse le a `SHA256SUMS.txt` fájlt is ugyanarról a kiadási oldalról, nyissa meg a PowerShellt a fájlok mappájában, és futtassa az alábbi parancsot: minden fájlt összehasonlít a közzétett összeggel, és `OK` vagy `DIFFERENT` értéket ír ki. Ha egy fájl `DIFFERENT`, ne futtassa.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- Ez az ellenőrzés azt bizonyítja, hogy a fájl **azonos** a GitHubon közzétettel; önmagában nem bizonyítja, hogy ártalmatlan. A forráskód és a fájlok automatikus összeállítása ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) nyilvános, digitális aláírás viszont még nincs: a SignPath Foundationnél benyújtott kérelmet 2026. október 19-én elutasították (lásd a „Code signing policy” részt).

## Követelmények

- Windows 10 vagy 11, illetve 64 bites Linux (előzetes verzió)
- [Python 3](https://www.python.org/) Tkinterrel (a szabványos telepítés része) (Linuxon: a `python3-tk` csomag)
- `yt-dlp.exe` és lehetőleg az [ffmpeg](https://ffmpeg.org/): a telepítő varázsló az első indításkor letölti őket (Linuxon: `yt-dlp`, `.exe` nélkül)

## Gyors kezdés

1. Töltse le vagy klónozza ezt a tárolót, és lépjen a mappájába.
2. Indítsa el a `yt-dlp-gui.bat` fájlt (vagy a `pythonw yt-dlp-gui.pyw` parancsot). Linuxon: `python3 yt-dlp-gui.pyw`.
3. Az első indításkor hagyja, hogy a varázsló telepítse a yt-dlp-t és az ffmpeg-et; a beállítások menüből később is elérhető.
4. Illesszen be egy URL-t, válassza ki a beállításokat, majd töltsön le, adja hozzá a sorhoz, vagy nyissa meg a vizsgálót egy lejátszási listához.

## Adatvédelem és felelős használat

- Ez a program nem küld adatot a szerzőnek, és nem tartalmaz telemetriát. A hálózati kapcsolatok a yt-dlp (videóoldalak), a telepítő varázsló (GitHub) és a nyilvántartás-eszköz (YouTube-keresés) révén jönnek létre. Az automatikus frissítésellenőrzés indításkor szintén a GitHubhoz csatlakozik (naponta legfeljebb egyszer); a „Frissítések keresése indításkor” ablakban kikapcsolható.
- A sütik az Ön számítógépén maradnak: a yt-dlp helyben olvassa őket a kiválasztott böngészőből.
- Használja az eszközt a szerzői jog, az oldalak felhasználási feltételei és országa törvényei szerint, és csak azt töltse le, amihez joga van.

## Fejlesztés

A teszteket (fordítások, nyilvántartás, parancsok összeállítása, felület, telepítő varázsló, dokumentáció) így lehet futtatni:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Minden feltöltéskor automatikusan lefutnak a GitHubon is. A verziószámot a `yt-dlp-gui.pyw` fájlban lévő `__version__` határozza meg, és egyeznie kell a [CHANGELOG.md](../CHANGELOG.md) fejlécével. A felület fordításai a `lang/` mappában, e dokumentáció fordításai a `docs/` mappában találhatók; az anyanyelvi lektorálást szívesen fogadjuk.

## A projekt támogatása

Ennek a felületnek a használata ingyenes volt, ingyenes és az is marad, bárki számára szabadon elérhető. Ha az eszköz különösen hasznos az Ön számára, a [Ko-fi](https://ko-fi.com/harlocksuites) oldalon támogathatja a projektet.

## Köszönetnyilvánítás

Köszönet a közösségnek, amely rendszeresen frissíti a [yt-dlp](https://github.com/yt-dlp/yt-dlp)-t, enélkül mindez nem lenne lehetséges.

## Licenc

A kód [MIT](../LICENSE) licenc alatt jelent meg. Az ikon, a logó és a „Harlock S.” banner (a `yt-dlp-gui.ico` fájl és az `assets/` mappa) a szerző kérésére MI által készített eredeti alkotások. Ezek a projekt vizuális arculatát alkotják, és nem tartoznak az MIT licenc hatálya alá: ne használja őket más projekthez, sem megtévesztő módon.
