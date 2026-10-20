# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Grafički interfejs za [yt-dlp](https://github.com/yt-dlp/yt-dlp), osmišljen da ga učini dostupnim svima i da u potpunosti iskoristi njegove mogućnosti.

> **Projekat je u razvoju.** Neke funkcije mogu se menjati, biti nepotpune ili sadržati greške.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funkcije

### Pojedinačno preuzimanje i red čekanja

- **Opcije**: maksimalan kvalitet (do 4K), samo zvuk (MP3), titlovi (formati vtt, srt, ass), ugrađivanje titlova i sličice, glavni jezik zvuka, dodatni audio zapisi (višezapisni MKV fajl) i biblioteka „blokova skripti” (naknadna obrada, izvoz, mreža, ponašanje) koju možete dopuniti sopstvenim blokovima.
- **Više audio traka**: u MKV datoteci svaka audio traka nosi oznaku svog jezika („srp”, „eng”…); plejer je prikazuje u meniju za zvuk.
- **Generisana komanda**: yt-dlp komanda koja odgovara vašim izborima prikazuje se uživo.
- **Red čekanja**: dodajte trenutni URL, pa pokrenite ceo red, od jedne stavke nadalje, samo jedan video ili opseg; pauza i nastavak, preskakanje trenutne stavke, zaustavljanje sa brisanjem delimičnih fajlova. Red se čuva između sesija.
- **Postojeća imena fajlova**: pojedinačni video čije ime već postoji u odredišnom folderu dobija sufiks (`_2`, `_3`…) da se ništa ne prepiše. Plejlista preuzeta ovim preuzimačem ne dobija novu numeraciju: video-zapisi koji su već u folderu se preskaču („has already been downloaded”).

### Inspektor plejlisti

- **Analiza** plejliste: svaki video se prikazuje sa dostupnim audio zapisima i titlovima; skrivene, privatne ili obrisane stavke se preskaču bez blokiranja ostalih.
- **Opšta pravila** (kvalitet, samo zvuk, format i ugrađivanje titlova, sličica, numeracija, jezici, blokovi skripti, izlazna fascikla) sa **izuzecima po videu** za glavni jezik, dodatne zapise i titlove.
- **Boje**: crvena kada nedostaje glavni jezik, narandžasta kada nedostaje dodatni zapis ili titl.
- **Preuzimanje izbora** sa dnevnikom, pauzom, nastavkom i preskakanjem; ako traženi zapisi ne postoje, video se ponavlja bez njih, a zatim **rezime** pokazuje šta je uspelo, šta je prilagođeno, a šta nije uspelo.

### Pametna fascikla i evidencija

- **Pametna fascikla**: yt-dlp preskače već preuzete video snimke zahvaljujući evidenciji koja se čuva u izlaznoj fascikli. Fajl `.yt-dlp-registre.json` sadrži identifikator, URL, naslov, trajanje, naziv fajla i datum svakog videa; `.yt-dlp-archive.txt`, koji čita yt-dlp, izvodi se iz njega.
- **Naknadna provera**: ako su video snimci iz izbora već u fascikli, a nisu u evidenciji, prozor predlaže da se upišu i preskoče (poređenjem naslova). Pogrešna poklapanja možete isključiti.
- **Ažuriraj evidenciju**: broji video snimke u fascikli, one u evidenciji i one koji nedostaju, a zatim na YouTube-u traži podatke koji nedostaju (naslov i trajanje preko ffprobe). Ništa se ne upisuje bez vaše potvrde, a dva dugmeta otvaraju lokalni fajl ili pronađeni YouTube link radi provere.

![yt-dlp GUI](img/registry.en.png)

### Kolačići pregledača

- Izaberite pregledač (Chrome, Firefox, Edge, Brave, Opera) čije kolačiće yt-dlp čita lokalno: potrebni su za dodatne audio zapise i neke titlove. **Preporučuje se Firefox.**
- **Rezultati naših testova** (Windows 11, oktobar 2026, YouTube nalog prijavljen u svakom pregledaču): **Firefox** radi, bilo da je pregledač otvoren ili zatvoren. **Opera** radi **samo sa zatvorenim pregledačem**: dok je otvorena zaključava bazu kolačića, a yt-dlp tada prikazuje „Could not copy Chrome cookie database”. **Chrome, Edge i Brave** ne rade ni kada su zatvoreni: šifruju kolačiće na način koji yt-dlp ne može uvek da pročita. Ova ograničenja potiču od pregledača i yt-dlp-a, a ne od programa, i mogu se promeniti njihovim ažuriranjima.
- Ako je pregledač podešen da **briše kolačiće pri zatvaranju** (ili koristite privatni režim), na disku ne ostaje nijedan kolačić: yt-dlp ne može ništa da povrati, ni sa Chrome-om, Edge-om, Brave-om ni Firefox-om. Kod Chrome-a, Edge-a i Brave-a to je zamka: pregledač treba zatvoriti, a to briše kolačiće. Isključite tu opciju ili sačuvajte kolačiće sajtova youtube.com i google.com.
- **Signalna lampica** pokazuje stanje: crvena ako je isključeno ili neuspešno, narandžasta ako nije testirano ili je u toku, zelena ako su kolačići učitani. Dugme ↻ pokreće test, a opis prikazuje stanje ili grešku.

### Pomoćnik za instalaciju, zavisnosti i ažuriranja yt-dlp-a

- **Pomoćnik za instalaciju**: pri prvom pokretanju predlaže preuzimanje yt-dlp-a i ffmpeg-a iz njihovih zvaničnih GitHub repozitorijuma. SHA-256 kontrolna suma se proverava i nisu potrebna administratorska prava.
- **Zavisnosti**: poseban prozor proverava ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 i deno i može da ih instalira preko Chocolatey-ja.
- **Ažuriranje i dijagnostika**: ažurira yt-dlp (`yt-dlp -U`) ili menja njegov izvršni fajl, prikazuje verziju i proverava opcije koje interfejs koristi.
- **Ažuriranje programa**: dnevna provera (može se isključiti) diskretnom trakom javlja da postoji nova verzija; poseban prozor prikazuje novosti i otvara preuzimanje koje odgovara vašoj instalaciji (instalater ili prenosiva verzija). Ništa se ne instalira automatski. Prekidač u meniju opcija („Proveri ažuriranja pri pokretanju”) uključuje ili isključuje automatsku proveru, a „Potraži ažuriranje programa…” je pokreće na zahtev.

### Interfejs i jezici

- Kontrole se prelamaju prema širini prozora; sadržaj se pomera uspravno, a tabela inspektora i vodoravno.
- Interfejs na **15 jezika**: francuski, engleski, španski, portugalski, italijanski, poljski, mađarski, srpski, ruski, vijetnamski, kineski, hindi, japanski, korejski i filipinski. Promena jezika važi posle ponovnog pokretanja, uz mogućnost da se odmah ponovo pokrene.

### Prijavi grešku

- Dugme „Prijavi grešku” priprema tehnički izveštaj: verzije programa, Pythona, Windowsa i yt-dlp-a, bezopasna podešavanja i poslednje linije dnevnika. Vaše fascikle, korisničko ime i e-adrese su sakriveni.
## Instalacija

- **Instalater (preporučeno)**: preuzmite `yt-dlp-gui-setup-X.Y.Z.exe` sa [stranice izdanja](https://github.com/harlockSuites/YT-dlp-GUI/releases) i pokrenite ga. Windows 10 ili 11 (64-bitni), bez administratorskih prava; Python nije potreban.
- **Prenosiva verzija**: preuzmite `yt-dlp-gui-portable-X.Y.Z.zip`, raspakujte ga gde želite i pokrenite `yt-dlp-gui.exe`; podešavanja ostaju u toj fascikli.
- **Iz izvornog koda**: pogledajte odeljke „Zahtevi” i „Brzi početak” ispod.
- **Deinstalacija**: Windows Podešavanja › Aplikacije › Instalirane aplikacije › yt-dlp GUI ili prečica „Deinstaliraj” u meniju Start. Program nudi da obriše i svoje podatke (podešavanja, red čekanja, preuzeti yt-dlp i ffmpeg); vaši video snimci se nikada ne brišu. Pošto je instalacija vezana za svaki Windows nalog, program se pojavljuje samo na listi naloga koji ga je instalirao. Kod prenosive verzije dovoljno je obrisati njen folder. Alati instalirani zasebno preko Chocolatey-ja (ffmpeg, Deno…) se ne uklanjaju.
- **Antivirusna analiza (VirusTotal)**: verzija 0.1.5 analizirana je 19. oktobra 2026. [Instalaciju](https://www.virustotal.com/gui/file/09a52ad01147b519c828bcd8708990e411cc3ab0af018ebadf294f9f2591bc45) označava 4 od 71 mehanizma (Arctic Wolf, DeepInstinct, SecureAge, Skyhigh) opštim heurističkim detekcijama („obfuscatedpoly”); [pokretač prenosive verzije](https://www.virustotal.com/gui/file/056a45eb80a50223ae34da91fcf0357ae885557a129c1be9dddf2205fe5160ad) označavaju 2 od 71 (Arctic Wolf, SecureAge), a [prenosivu ZIP arhivu](https://www.virustotal.com/gui/file/57ca0c679d9653bfde6bb3c374985ba8a324589f887f7f39467f8a0130649d58) 1 od 67 (Zillya, na samoj arhivi). Verovatno su to lažne uzbune zbog nepotpisanog, kompresovanog programa. Rezultati važe samo za ovu verziju. Ako sumnjate, proverite SHA-256 zbir.
- **Code signing policy**: digitalno potpisivanje budućih verzija je u pripremi (zahtev SignPath Foundation); [politika potpisivanja koda](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) opisuje proces. Verzije do 0.1.4 nisu potpisane.
- **Upozorenje Windows SmartScreen**: instalater nije digitalno potpisan, pa Windows može da prikaže „Windows je zaštitio vaš računar”. Kliknite na „Više informacija”, a zatim na „Ipak pokreni”. Da proverite autentičnost fajla, uporedite njegovu SHA-256 sumu sa onom iz `SHA256SUMS.txt`, objavljenog uz svako izdanje:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

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

- Ovaj softver ne šalje nikakve podatke autoru i ne sadrži telemetriju. Mrežne veze idu preko yt-dlp-a (video sajtovi), pomoćnika za instalaciju (GitHub) i alata za evidenciju (pretraga na YouTube-u). Automatska provera ažuriranja takođe se povezuje sa GitHub-om pri pokretanju (najviše jednom dnevno); možete je isključiti u „Proveri ažuriranja pri pokretanju”.
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

Kôd je objavljen pod [MIT](../LICENSE) licencom. Ikona, logo i baner „Harlock S.” (fajl `yt-dlp-gui.ico` i fascikla `assets/`) originalne su kreacije koje je na zahtev autora generisala veštačka inteligencija. Čine vizuelni identitet projekta i nisu obuhvaćeni MIT licencom: nemojte ih koristiti za drugi projekat niti na način koji može da zavara.
