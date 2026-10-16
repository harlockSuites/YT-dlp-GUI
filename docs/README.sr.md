# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Grafički interfejs za [yt-dlp](https://github.com/yt-dlp/yt-dlp), osmišljen da ga učini dostupnim svima i da u potpunosti iskoristi njegove mogućnosti.

> **Projekat je u razvoju.** Neke funkcije mogu se menjati, biti nepotpune ili sadržati greške.

## Funkcije

### Pojedinačno preuzimanje i red čekanja

- **Opcije**: maksimalan kvalitet (do 4K), samo zvuk (MP3), titlovi (formati vtt, srt, ass), ugrađivanje titlova i sličice, glavni jezik zvuka, dodatni audio zapisi (višezapisni MKV fajl) i biblioteka „blokova skripti” (naknadna obrada, izvoz, mreža, ponašanje) koju možete dopuniti sopstvenim blokovima.
- **Generisana komanda**: yt-dlp komanda koja odgovara vašim izborima prikazuje se uživo.
- **Red čekanja**: dodajte trenutni URL, pa pokrenite ceo red, od jedne stavke nadalje, samo jedan video ili opseg; pauza i nastavak, preskakanje trenutne stavke, zaustavljanje sa brisanjem delimičnih fajlova. Red se čuva između sesija.

### Inspektor plejlisti

- **Analiza** plejliste: svaki video se prikazuje sa dostupnim audio zapisima i titlovima; skrivene, privatne ili obrisane stavke se preskaču bez blokiranja ostalih.
- **Opšta pravila** (kvalitet, samo zvuk, format i ugrađivanje titlova, sličica, numeracija, jezici, blokovi skripti, izlazna fascikla) sa **izuzecima po videu** za glavni jezik, dodatne zapise i titlove.
- **Boje**: crvena kada nedostaje glavni jezik, narandžasta kada nedostaje dodatni zapis ili titl.
- **Preuzimanje izbora** sa dnevnikom, pauzom, nastavkom i preskakanjem; ako traženi zapisi ne postoje, video se ponavlja bez njih, a zatim **rezime** pokazuje šta je uspelo, šta je prilagođeno, a šta nije uspelo.

### Pametna fascikla i evidencija

- **Pametna fascikla**: yt-dlp preskače već preuzete video snimke zahvaljujući evidenciji koja se čuva u izlaznoj fascikli. Fajl `.yt-dlp-registre.json` sadrži identifikator, URL, naslov, trajanje, naziv fajla i datum svakog videa; `.yt-dlp-archive.txt`, koji čita yt-dlp, izvodi se iz njega.
- **Naknadna provera**: ako su video snimci iz izbora već u fascikli, a nisu u evidenciji, prozor predlaže da se upišu i preskoče (poređenjem naslova). Pogrešna poklapanja možete isključiti.
- **Ažuriraj evidenciju**: broji video snimke u fascikli, one u evidenciji i one koji nedostaju, a zatim na YouTube-u traži podatke koji nedostaju (naslov i trajanje preko ffprobe). Ništa se ne upisuje bez vaše potvrde, a dva dugmeta otvaraju lokalni fajl ili pronađeni YouTube link radi provere.

### Kolačići pregledača

- Izaberite pregledač (Chrome, Firefox, Edge, Brave, Opera) čije kolačiće yt-dlp čita lokalno: potrebni su za dodatne audio zapise i neke titlove.
- **Signalna lampica** pokazuje stanje: crvena ako je isključeno ili neuspešno, narandžasta ako nije testirano ili je u toku, zelena ako su kolačići učitani. Dugme ↻ pokreće test, a opis prikazuje stanje ili grešku.

### Pomoćnik za instalaciju, zavisnosti i ažuriranja yt-dlp-a

- **Pomoćnik za instalaciju**: pri prvom pokretanju predlaže preuzimanje yt-dlp-a i ffmpeg-a iz njihovih zvaničnih GitHub repozitorijuma. SHA-256 kontrolna suma se proverava i nisu potrebna administratorska prava.
- **Zavisnosti**: poseban prozor proverava ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 i deno i može da ih instalira preko Chocolatey-ja.
- **Ažuriranje i dijagnostika**: ažurira yt-dlp (`yt-dlp -U`) ili menja njegov izvršni fajl, prikazuje verziju i proverava opcije koje interfejs koristi.

### Interfejs i jezici

- Kontrole se prelamaju prema širini prozora; sadržaj se pomera uspravno, a tabela inspektora i vodoravno.
- Interfejs na **15 jezika**: francuski, engleski, španski, portugalski, italijanski, poljski, mađarski, srpski, ruski, vijetnamski, kineski, hindi, japanski, korejski i filipinski. Promena jezika važi posle ponovnog pokretanja, uz mogućnost da se odmah ponovo pokrene.

### Prijavi grešku

- Dugme „Prijavi grešku” priprema tehnički izveštaj: verzije programa, Pythona, Windowsa i yt-dlp-a, bezopasna podešavanja i poslednje linije dnevnika. Vaše fascikle, korisničko ime i e-adrese su sakriveni.
- Ništa se ne šalje automatski: pregledate i menjate izveštaj, pa otvarate unapred popunjenu stranicu GitHub prijave (ili kopirate izveštaj).

## Zahtevi

- Windows
- [Python 3](https://www.python.org/) sa Tkinterom (uključen u standardnu instalaciju)
- `yt-dlp.exe` i, po mogućstvu, [ffmpeg](https://ffmpeg.org/): pomoćnik za instalaciju ih preuzima pri prvom pokretanju

## Brzi početak

1. Preuzmite ili klonirajte ovaj repozitorijum i uđite u njegovu fasciklu.
2. Pokrenite `yt-dlp-gui.bat` (ili `pythonw yt-dlp-gui.pyw`).
3. Pri prvom pokretanju pustite pomoćnika da instalira yt-dlp i ffmpeg; ostaje dostupan u meniju opcija.
4. Nalepite URL, izaberite opcije, pa preuzmite, dodajte u red ili otvorite inspektor za plejlistu.

## Privatnost i odgovorna upotreba

- Ovaj softver ne šalje nikakve podatke autoru i ne sadrži telemetriju. Mrežne veze idu preko yt-dlp-a (video sajtovi), pomoćnika za instalaciju (GitHub) i alata za evidenciju (pretraga na YouTube-u).
- Vaši kolačići ostaju na vašem računaru: yt-dlp ih čita lokalno iz izabranog pregledača.
- Koristite alat uz poštovanje autorskih prava, uslova korišćenja sajtova i zakona vaše zemlje, i preuzimajte samo ono što imate pravo da preuzmete.

## Razvoj

Testovi (prevodi, evidencija, pravljenje komandi, interfejs, pomoćnik za instalaciju, dokumentacija) pokreću se komandom:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Automatski se pokreću i na GitHub-u pri svakom slanju. Broj verzije definiše `__version__` u fajlu `yt-dlp-gui.pyw` i mora da odgovara zaglavlju [CHANGELOG.md](../CHANGELOG.md). Fajlovi sa prevodima interfejsa nalaze se u `lang/`, a ove dokumentacije u `docs/`; provere izvornih govornika su dobrodošle.

## Podrška projektu

Korišćenje ovog interfejsa je, bilo je i ostaće besplatno i slobodno dostupno svakome. Ako vam je alat posebno koristan, projekat možete podržati na [Ko-fi](https://ko-fi.com/harlocksuites).

## Zahvalnice

Hvala zajednici koja redovno ažurira [yt-dlp](https://github.com/yt-dlp/yt-dlp), bez kojeg ništa od ovoga ne bi bilo moguće.

## Licenca

Kôd je objavljen pod [MIT](../LICENSE) licencom. Logo i baner „Harlock S.” (fascikla `assets/`) lični su brend autora i nisu obuhvaćeni ovom licencom: sva prava zadržana.
