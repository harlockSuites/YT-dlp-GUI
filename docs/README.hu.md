# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Grafikus felület a [yt-dlp](https://github.com/yt-dlp/yt-dlp) programhoz, amely mindenki számára elérhetővé teszi, miközben teljes mértékben kihasználja a képességeit.

> **Fejlesztés alatt álló projekt.** Egyes funkciók változhatnak, hiányosak lehetnek vagy hibákat tartalmazhatnak.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funkciók

### Egyedi letöltő és sor

- **Beállítások**: maximális minőség (akár 4K), csak hang (MP3), feliratok (vtt, srt, ass formátum), feliratok és indexkép beágyazása, fő hangnyelv, másodlagos hangsávok (többsávos MKV-fájl) és „szkriptblokkok” könyvtára (utófeldolgozás, exportálás, hálózat, viselkedés), amelyet saját blokkokkal bővíthet.
- **Több hangsáv**: az MKV-fájlban minden hangsáv viseli a nyelve címkéjét („hun”, „eng”…); a lejátszó megjeleníti az audiomenüben.
- **Előállított parancs**: a választásainak megfelelő yt-dlp-parancs élőben látható.
- **Sor**: adja hozzá az aktuális URL-t, majd indítsa el az egész sort, egy elemtől kezdve, egyetlen videót vagy egy tartományt; szüneteltetés és folytatás, az aktuális elem kihagyása, leállítás a részleges fájlok takarításával. A sor munkamenetek között megmarad.

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

### Telepítő varázsló, függőségek és a yt-dlp frissítései

- **Telepítő varázsló**: az első indításkor felajánlja a yt-dlp és az ffmpeg letöltését a hivatalos GitHub-tárolókból. Az SHA-256 ellenőrzőösszeg ellenőrzésre kerül, és nincs szükség rendszergazdai jogosultságra.
- **Függőségek**: a külön ablak ellenőrzi az ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 és deno meglétét, és Chocolatey segítségével telepítheti őket.
- **Frissítés és diagnosztika**: frissíti a yt-dlp-t (`yt-dlp -U`) vagy lecseréli a futtatható fájlját, megmutatja a verzióját, és ellenőrzi a felület által használt kapcsolókat.
- **Programfrissítés**: a naponta végzett (kikapcsolható) ellenőrzés egy diszkrét sávval jelzi az új verziót; a külön ablak megmutatja az újdonságokat, és megnyitja a telepítésének megfelelő letöltést (telepítő vagy hordozható változat). Semmi nem települ automatikusan. A beállítások menü kapcsolója („Frissítések keresése indításkor”) be- vagy kikapcsolja az automatikus ellenőrzést, a „Programfrissítés keresése…” pedig kérésre lefuttatja.

### Felület és nyelvek

- A vezérlők az ablak szélességéhez igazodva tördelődnek; a tartalom függőlegesen görgethető, a vizsgáló táblázata pedig vízszintesen is.
- **15 nyelvű** felület: francia, angol, spanyol, portugál, olasz, lengyel, magyar, szerb, orosz, vietnami, kínai, hindi, japán, koreai és filippínó. A nyelvváltás újraindításkor lép érvénybe, azonnali újraindítási lehetőséggel.

### Hiba jelentése

- A „Hiba jelentése” gomb műszaki jelentést készít: a program, a Python, a Windows és a yt-dlp verziója, ártalmatlan beállítások és a napló utolsó sorai. A mappái, a felhasználóneve és az e-mail-címei el vannak takarva.
## Telepítés

- **Telepítő (ajánlott)**: töltse le a `yt-dlp-gui-setup-X.Y.Z.exe` fájlt a [kiadások oldaláról](https://github.com/harlockSuites/YT-dlp-GUI/releases), és futtassa. Windows 10 vagy 11 (64 bites), rendszergazdai jogosultság nélkül; Python nem szükséges.
- **Hordozható változat**: töltse le a `yt-dlp-gui-portable-X.Y.Z.zip` fájlt, csomagolja ki bárhová, és futtassa a `yt-dlp-gui.exe` fájlt; a beállítások ebben a mappában maradnak.
- **Forráskódból**: lásd lentebb a „Követelmények” és a „Gyors kezdés” részt.
- **Eltávolítás**: Windows Beállítások › Alkalmazások › Telepített alkalmazások › yt-dlp GUI, vagy a Start menü „Eltávolítás” parancsikonja. A program felajánlja az adatai (beállítások, várólista, letöltött yt-dlp és ffmpeg) törlését is; a videóid soha nem törlődnek. Mivel a telepítés Windows-fiókonként külön van, a program csak azon fiók listájában jelenik meg, amelyik telepítette. A hordozható változatnál elég a mappáját törölni. A Chocolatey-vel külön telepített eszközök (ffmpeg, Deno…) nem törlődnek.
- **Víruskeresős elemzés (VirusTotal)**: a 0.1.4-es verziót 2026. október 18-án elemezték. A [hordozható verziót](https://www.virustotal.com/gui/file/976d53e5bc8588a0f754497875d36b474aabf275ff9f88942f99f9e08f05ca18) a 66 motor közül egyik sem jelöli (0/66); a [telepítőt](https://www.virustotal.com/gui/file/b4d111d8b41516424ba451f26e71e58950a16d2f168e8ce8b0ab71ee21cd64ee) a 71-ből 4 (Arctic Wolf, DeepInstinct, SecureAge, Skyhigh) jelöli általános heurisztikus észleléssel („obfuscatedpoly”), valószínűleg téves riasztásként, mert a telepítő tömörített és nincs aláírva. Ezek az eredmények csak erre a verzióra érvényesek. Ha bizonytalan, használja a hordozható verziót, vagy ellenőrizze az SHA-256 összeget.
- **Code signing policy**: a jövőbeli verziók digitális aláírása előkészületben van (kérelem a SignPath Foundationhöz); a [kódaláírási irányelv](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) leírja a folyamatot. A 0.1.4-ig kiadott verziók nincsenek aláírva.
- **Windows SmartScreen figyelmeztetés**: a telepítő nincs digitálisan aláírva, ezért a Windows megjelenítheti: „A Windows megvédte a számítógépét”. Kattintson a „További információ”, majd a „Futtatás mindenképpen” lehetőségre. A fájl hitelességét ellenőrizheti, ha összeveti az SHA-256 összegét a minden kiadással közzétett `SHA256SUMS.txt` fájlban szereplővel:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Semmi nem megy el automatikusan: Ön átnézi és szerkeszti a jelentést, majd megnyit egy előre kitöltött GitHub-hibajegyoldalt (vagy kimásolja a jelentést).

## Követelmények

- Windows
- [Python 3](https://www.python.org/) Tkinterrel (a szabványos telepítés része)
- `yt-dlp.exe` és lehetőleg az [ffmpeg](https://ffmpeg.org/): a telepítő varázsló az első indításkor letölti őket

## Gyors kezdés

1. Töltse le vagy klónozza ezt a tárolót, és lépjen a mappájába.
2. Indítsa el a `yt-dlp-gui.bat` fájlt (vagy a `pythonw yt-dlp-gui.pyw` parancsot).
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
