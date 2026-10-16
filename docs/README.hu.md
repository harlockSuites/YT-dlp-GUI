# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Grafikus felület a [yt-dlp](https://github.com/yt-dlp/yt-dlp) programhoz, amely mindenki számára elérhetővé teszi, miközben teljes mértékben kihasználja a képességeit.

> **Fejlesztés alatt álló projekt.** Egyes funkciók változhatnak, hiányosak lehetnek vagy hibákat tartalmazhatnak.

## Funkciók

### Egyedi letöltő és sor

- **Beállítások**: maximális minőség (akár 4K), csak hang (MP3), feliratok (vtt, srt, ass formátum), feliratok és indexkép beágyazása, fő hangnyelv, másodlagos hangsávok (többsávos MKV-fájl) és „szkriptblokkok” könyvtára (utófeldolgozás, exportálás, hálózat, viselkedés), amelyet saját blokkokkal bővíthet.
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

### Böngészősütik

- Válassza ki azt a böngészőt (Chrome, Firefox, Edge, Brave, Opera), amelynek sütijeit a yt-dlp helyben olvassa: a másodlagos hangsávokhoz és egyes feliratokhoz szükségesek.
- Egy **jelzőfény** mutatja az állapotot: piros, ha ki van kapcsolva vagy hibás, narancs, ha nincs tesztelve vagy folyamatban van, zöld, ha a sütik betöltődtek. A ↻ gomb tesztet indít, a buborékszöveg pedig elmagyarázza az állapotot vagy a hibát.

### Telepítő varázsló, függőségek és a yt-dlp frissítései

- **Telepítő varázsló**: az első indításkor felajánlja a yt-dlp és az ffmpeg letöltését a hivatalos GitHub-tárolókból. Az SHA-256 ellenőrzőösszeg ellenőrzésre kerül, és nincs szükség rendszergazdai jogosultságra.
- **Függőségek**: a külön ablak ellenőrzi az ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 és deno meglétét, és Chocolatey segítségével telepítheti őket.
- **Frissítés és diagnosztika**: frissíti a yt-dlp-t (`yt-dlp -U`) vagy lecseréli a futtatható fájlját, megmutatja a verzióját, és ellenőrzi a felület által használt kapcsolókat.
- **Programfrissítés**: a naponta végzett (kikapcsolható) ellenőrzés egy diszkrét sávval jelzi az új verziót; a külön ablak megmutatja az újdonságokat, és megnyitja a telepítésének megfelelő letöltést (telepítő vagy hordozható változat). Semmi nem települ automatikusan.

### Felület és nyelvek

- A vezérlők az ablak szélességéhez igazodva tördelődnek; a tartalom függőlegesen görgethető, a vizsgáló táblázata pedig vízszintesen is.
- **15 nyelvű** felület: francia, angol, spanyol, portugál, olasz, lengyel, magyar, szerb, orosz, vietnami, kínai, hindi, japán, koreai és filippínó. A nyelvváltás újraindításkor lép érvénybe, azonnali újraindítási lehetőséggel.

### Hiba jelentése

- A „Hiba jelentése” gomb műszaki jelentést készít: a program, a Python, a Windows és a yt-dlp verziója, ártalmatlan beállítások és a napló utolsó sorai. A mappái, a felhasználóneve és az e-mail-címei el vannak takarva.
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

- Ez a program nem küld adatot a szerzőnek, és nem tartalmaz telemetriát. A hálózati kapcsolatok a yt-dlp (videóoldalak), a telepítő varázsló (GitHub) és a nyilvántartás-eszköz (YouTube-keresés) révén jönnek létre. Az automatikus frissítésellenőrzés indításkor szintén a GitHubhoz csatlakozik (naponta legfeljebb egyszer); a „Programfrissítés keresése…” ablakban kikapcsolható.
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

A kód [MIT](../LICENSE) licenc alatt jelent meg. A „Harlock S.” logó és banner (`assets/` mappa) a szerző személyes védjegye, és nem tartozik e licenc hatálya alá: minden jog fenntartva.
