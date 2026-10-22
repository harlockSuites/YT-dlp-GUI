# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Graficzny interfejs dla [yt-dlp](https://github.com/yt-dlp/yt-dlp), stworzony, aby uczynić go dostępnym dla wszystkich i w pełni wykorzystać jego możliwości.

> **Projekt w trakcie rozwoju.** Niektóre funkcje mogą się zmienić, być niekompletne lub zawierać błędy.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funkcje

### Pojedyncze pobieranie i kolejka

- **Opcje**: maksymalna jakość (do 4K), tylko dźwięk (MP3), napisy (formaty vtt, srt, ass), osadzanie napisów i miniatury, główny język ścieżki dźwiękowej, dodatkowe ścieżki audio (wielościeżkowy plik MKV) oraz biblioteka „bloków skryptów” (postprodukcja, eksport, sieć, zachowanie), którą można uzupełnić własnymi blokami.
- **Wiele ścieżek audio**: w pliku MKV każda ścieżka audio ma etykietę swojego języka („pol”, „eng”…); odtwarzacz pokazuje ją w menu audio.
- **Wygenerowane polecenie**: polecenie yt-dlp odpowiadające Twoim wyborom jest wyświetlane na bieżąco.
- **Kolejka**: dodaj bieżący adres URL, a następnie uruchom całą kolejkę, od wybranej pozycji, pojedynczy film lub zakres; pauza i wznowienie, pominięcie bieżącej pozycji, zatrzymanie z usunięciem plików częściowych. Kolejka jest zachowywana między sesjami.
- **Istniejące nazwy plików**: pojedynczy film, którego nazwa już istnieje w folderze docelowym, otrzymuje przyrostek (`_2`, `_3`…), aby niczego nie nadpisać. Playlista pobierana tym narzędziem nie jest renumerowana: filmy już obecne w folderze są pomijane („has already been downloaded”).

### Inspektor playlist

- **Analiza** playlisty: każdy film jest wyświetlany wraz z dostępnymi ścieżkami audio i napisami; ukryte, prywatne lub usunięte pozycje są pomijane bez blokowania reszty.
- **Reguły globalne** (jakość, tylko dźwięk, format i osadzanie napisów, miniatura, numeracja, języki, bloki skryptów, folder docelowy) z **wyjątkami dla pojedynczych filmów** dotyczącymi języka głównego, ścieżek dodatkowych i napisów.
- **Kolory**: czerwony, gdy brakuje języka głównego, pomarańczowy, gdy brakuje dodatkowej ścieżki lub napisów.
- **Pobieranie zaznaczenia** z dziennikiem, pauzą, wznowieniem i pominięciem; jeśli żądane ścieżki nie istnieją, film jest ponawiany bez nich, a następnie **podsumowanie** pokazuje, co się udało, co dostosowano, a co się nie powiodło.

### Inteligentny katalog i rejestr

- **Inteligentny katalog**: yt-dlp pomija już pobrane filmy dzięki rejestrowi zapisanemu w folderze docelowym. Plik `.yt-dlp-registre.json` zawiera identyfikator, adres URL, tytuł, czas trwania, nazwę pliku i datę każdego filmu; plik `.yt-dlp-archive.txt`, odczytywany przez yt-dlp, jest z niego tworzony.
- **Kontrola wsteczna**: jeśli filmy z zaznaczenia są już w folderze, ale nie ma ich w rejestrze, okno proponuje ich wpisanie i pominięcie (porównanie tytułów). Fałszywe dopasowania można odznaczyć.
- **Aktualizuj rejestr**: zlicza filmy w folderze, w rejestrze i brakujące, a następnie wyszukuje brakujące informacje w YouTube (tytuł oraz czas trwania przez ffprobe). Nic nie jest wpisywane bez Twojego potwierdzenia, a dwa przyciski otwierają plik lokalny lub znaleziony link YouTube, aby sprawdzić.

![yt-dlp GUI](img/registry.en.png)

### Ciasteczka przeglądarki

- Wybierz przeglądarkę (Chrome, Firefox, Edge, Brave, Opera), z której yt-dlp lokalnie odczytuje ciasteczka: są potrzebne do dodatkowych ścieżek audio i niektórych napisów. **Zalecamy Firefoksa.**
- **Wyniki naszych testów** (Windows 11, październik 2026, konto YouTube zalogowane w każdej przeglądarce): **Firefox** działa, niezależnie od tego, czy przeglądarka jest otwarta, czy zamknięta. **Opera** działa **tylko przy zamkniętej przeglądarce**: blokuje bazę ciasteczek, dopóki jest otwarta, a yt-dlp wyświetla wtedy „Could not copy Chrome cookie database”. **Chrome, Edge i Brave** zawodzą nawet po zamknięciu: szyfrują ciasteczka w sposób, którego yt-dlp nie zawsze potrafi odczytać. Te ograniczenia pochodzą od przeglądarek i yt-dlp, nie od programu, i mogą się zmienić wraz z ich aktualizacjami.
- Jeśli przeglądarka jest ustawiona na **usuwanie ciasteczek przy zamknięciu** (lub używasz trybu prywatnego), na dysku nie zostaje żadne ciasteczko: yt-dlp nie odzyska niczego, ani z Chrome, Edge, Brave, ani z Firefoksa. W Chrome, Edge i Brave to pułapka: przeglądarkę trzeba zamknąć, co usuwa ciasteczka. Wyłącz tę opcję lub zachowaj ciasteczka youtube.com i google.com.
- **Wskaźnik** pokazuje stan: czerwony, gdy wyłączone lub błąd, pomarańczowy, gdy nie przetestowano lub trwa test, zielony, gdy ciasteczka są wczytane. Przycisk ↻ uruchamia test, a podpowiedź wyjaśnia stan lub błąd.

### Asystent instalacji, zależności i aktualizacje yt-dlp

- **Asystent instalacji**: przy pierwszym uruchomieniu proponuje pobranie yt-dlp i ffmpeg z ich oficjalnych repozytoriów GitHub. Suma kontrolna SHA-256 jest weryfikowana i nie są potrzebne uprawnienia administratora.
- **Zależności**: dedykowane okno sprawdza ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 i deno oraz może je zainstalować przez Chocolatey. Niezbędne są tylko ffmpeg i ffprobe; deno jest zalecany (dodatkowe ścieżki audio); AtomicParsley, MKVToolNix i aria2 są opcjonalne: program działa bez nich.
- **Aktualizacja i diagnostyka**: aktualizuje yt-dlp (`yt-dlp -U`) lub podmienia jego plik wykonywalny, pokazuje wersję i sprawdza opcje używane przez interfejs.
- **Aktualizacja programu**: codzienne sprawdzanie (można je wyłączyć) sygnalizuje nową wersję dyskretnym paskiem; osobne okno pokazuje nowości i otwiera pobieranie odpowiednie dla Twojej instalacji (instalator lub wersja przenośna). Nic nie jest instalowane automatycznie. Przełącznik w menu opcji („Sprawdzaj aktualizacje przy uruchomieniu”) włącza lub wyłącza automatyczne sprawdzanie, a „Sprawdź aktualizację programu…” uruchamia je na żądanie.

### Interfejs i języki

- Elementy sterujące zawijają się zależnie od szerokości okna; zawartość przewija się pionowo, a tabela inspektora także poziomo.
- Interfejs w **15 językach**: francuski, angielski, hiszpański, portugalski, włoski, polski, węgierski, serbski, rosyjski, wietnamski, chiński, hindi, japoński, koreański i filipiński. Zmiana języka działa po ponownym uruchomieniu, z możliwością natychmiastowego restartu.

### Zgłoś błąd

- Przycisk „Zgłoś błąd” przygotowuje raport techniczny: wersje programu, Pythona, Windows i yt-dlp, niegroźne ustawienia i ostatnie linie dziennika. Twoje foldery, nazwa użytkownika i adresy e-mail są zasłaniane. Wysłanie raportu na GitHubie wymaga bezpłatnego konta GitHub.
- Nic nie jest wysyłane automatycznie: sprawdzasz i edytujesz raport, a następnie otwierasz wstępnie wypełnioną stronę zgłoszenia GitHub (lub kopiujesz raport).

## Instalacja

- **Instalator (zalecany)**: pobierz `yt-dlp-gui-setup-X.Y.Z.exe` ze [strony wydań](https://github.com/harlockSuites/YT-dlp-GUI/releases) i uruchom go. Windows 10 lub 11 (64-bitowy), bez uprawnień administratora; Python nie jest potrzebny.
- **Wersja przenośna**: pobierz `yt-dlp-gui-portable-X.Y.Z.zip`, rozpakuj w dowolnym miejscu i uruchom `yt-dlp-gui.exe`; ustawienia zostają w tym folderze.
- **Z kodu źródłowego**: zobacz sekcje „Wymagania” i „Szybki start” poniżej.
- **Odinstalowanie**: Ustawienia systemu Windows › Aplikacje › Zainstalowane aplikacje › yt-dlp GUI lub skrót „Odinstaluj” w menu Start. Program proponuje usunięcie także swoich danych (ustawienia, kolejka, pobrane yt-dlp i ffmpeg); Twoje filmy nigdy nie są usuwane. Ponieważ instalacja jest przypisana do konta Windows, program pojawia się tylko na liście konta, które go zainstalowało. W wersji przenośnej wystarczy usunąć jej folder. Narzędzia zainstalowane osobno przez Chocolatey (ffmpeg, Deno…) nie są usuwane.
- **Analiza antywirusowa (VirusTotal)**: wersja 0.1.6 została przeanalizowana 20 października 2026. [Instalator](https://www.virustotal.com/gui/file/683b157e1072ae7c2abcff09c1f0d94ac1d36701715682798c10792359fa9bae) jest oznaczony przez 4 z 70 silników (Arctic Wolf, DeepInstinct, SecureAge, Skyhigh) ogólnymi detekcjami heurystycznymi („obfuscatedpoly”); [przenośne archiwum ZIP](https://www.virustotal.com/gui/file/45cfe1a79d7eb96323634ba1ac6c8247eb5a4e9e79f1519e3f70f7c92b2538c3) nie jest oznaczone przez żaden z 66 silników (0/66), a jego [program uruchamiający](https://www.virustotal.com/gui/file/0896bf3d524774b4f53224160bf9f216ccb0922ec2b8b5ddc8495b2d2c1680f2) przez 2 z 71 (SecureAge, Zillya). Prawdopodobnie są to fałszywe alarmy wynikające z niepodpisanego, skompresowanego programu. Wyniki dotyczą tylko tej wersji. W razie wątpliwości sprawdź sumę SHA-256.
- **Code signing policy**: podpisywanie cyfrowe przyszłych wersji jest w przygotowaniu (wniosek do SignPath Foundation); [polityka podpisywania kodu](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) opisuje ten proces. Wersje do 0.1.4 nie są podpisane.
- **Ostrzeżenie Windows SmartScreen**: instalator nie jest podpisany cyfrowo, więc Windows może wyświetlić „System Windows ochronił ten komputer”. Kliknij „Więcej informacji”, a następnie „Uruchom mimo to”. Aby sprawdzić autentyczność pliku, porównaj jego sumę SHA-256 z sumą z pliku `SHA256SUMS.txt` publikowanego z każdą wersją:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Ostrzeżenia systemu Windows i przeglądarek

To oprogramowanie jest bezpłatne, publikuje je jedna osoba, a jego pliki **nie są jeszcze podpisane cyfrowo**. Nowy plik, którego prawie nikt jeszcze nie pobrał, nie ma „reputacji”: przeglądarki i Windows wyświetlają więc ostrzeżenia **nawet dla bezpiecznego programu**. Ostrzeżenie nie dowodzi, że plik jest niebezpieczny, a jego brak nie dowodzi, że jest bezpieczny: oto jak sprawdzić to samodzielnie.

- **Przeglądarka** (Firefox, Chrome, Edge, Brave): pobieranie może zostać oznaczone jako „rzadko pobierane” lub „zawierające wirusa lub złośliwe oprogramowanie”. To automatyczna ocena reputacji pliku. Najpierw sprawdź sumę kontrolną (poniżej); jeśli się zgadza, możesz wybrać opcję zezwalającą na pobranie lub zachowującą plik.
- **Windows SmartScreen**: „System Windows ochronił ten komputer” → kliknij „Więcej informacji”, a potem „Uruchom mimo to”, **po** sprawdzeniu sumy kontrolnej.
- **Antywirus**: kilka silników zgłasza ogólne detekcje (zobacz analizę antywirusową powyżej). Aby zobaczyć analizę swojego pliku, wklej jego sumę SHA-256 w pasku wyszukiwania [VirusTotal](https://www.virustotal.com/): jeśli plik jest już znany, otrzymasz raport bez wysyłania pliku.
- **Sprawdź pobrany plik**: pobierz też `SHA256SUMS.txt` z tej samej strony wersji, otwórz PowerShell w folderze z plikami i uruchom poniższe polecenie: porównuje każdy plik z opublikowaną sumą i wyświetla `OK` lub `DIFFERENT`. Jeśli plik jest `DIFFERENT`, nie uruchamiaj go.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- To sprawdzenie dowodzi, że plik jest **identyczny** z opublikowanym na GitHubie; samo w sobie nie dowodzi, że jest nieszkodliwy. Kod źródłowy i automatyczna budowa plików ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) są publiczne, a podpis cyfrowy jest w przygotowaniu (zobacz „Code signing policy”).

## Wymagania

- Windows
- [Python 3](https://www.python.org/) z Tkinter (w standardowej instalacji)
- `yt-dlp.exe` i najlepiej [ffmpeg](https://ffmpeg.org/): asystent instalacji pobiera je przy pierwszym uruchomieniu

## Szybki start

1. Pobierz lub sklonuj to repozytorium i przejdź do jego folderu.
2. Uruchom `yt-dlp-gui.bat` (lub `pythonw yt-dlp-gui.pyw`).
3. Przy pierwszym uruchomieniu pozwól asystentowi zainstalować yt-dlp i ffmpeg; pozostaje dostępny w menu opcji.
4. Wklej adres URL, wybierz opcje, a następnie pobierz, dodaj do kolejki lub otwórz inspektora dla playlisty.

## Prywatność i odpowiedzialne korzystanie

- To oprogramowanie nie wysyła żadnych danych autorowi i nie zawiera telemetrii. Połączenia sieciowe realizują yt-dlp (serwisy wideo), asystent instalacji (GitHub) i narzędzie rejestru (wyszukiwanie w YouTube). Automatyczne sprawdzanie aktualizacji także łączy się z GitHubem przy uruchomieniu (najwyżej raz dziennie); można je wyłączyć w „Sprawdzaj aktualizacje przy uruchomieniu”.
- Twoje ciasteczka pozostają na Twoim komputerze: yt-dlp odczytuje je lokalnie z wybranej przeglądarki.
- Korzystaj z narzędzia zgodnie z prawem autorskim, regulaminami serwisów i prawem Twojego kraju oraz pobieraj tylko to, do czego masz prawo.

## Rozwój

Testy (tłumaczenia, rejestr, budowanie poleceń, interfejs, asystent instalacji, dokumentacja) uruchamiasz poleceniem:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Uruchamiają się też automatycznie na GitHubie przy każdym wysłaniu zmian. Numer wersji jest zdefiniowany przez `__version__` w `yt-dlp-gui.pyw` i musi zgadzać się z nagłówkiem [CHANGELOG.md](../CHANGELOG.md). Pliki tłumaczeń interfejsu znajdują się w `lang/`, a tej dokumentacji w `docs/`; uwagi native speakerów są mile widziane.

## Wesprzyj projekt

Korzystanie z tego interfejsu jest, było i pozostanie bezpłatne i dostępne dla każdego. Jeśli narzędzie jest dla Ciebie szczególnie przydatne, możesz wesprzeć projekt na [Ko-fi](https://ko-fi.com/harlocksuites).

## Podziękowania

Dziękuję społeczności, która regularnie aktualizuje [yt-dlp](https://github.com/yt-dlp/yt-dlp), bez którego nic z tego nie byłoby możliwe.

## Licencja

Kod jest udostępniony na licencji [MIT](../LICENSE). Ikona, logo i baner „Harlock S.” (plik `yt-dlp-gui.ico` i folder `assets/`) to oryginalne twory wygenerowane przez AI na prośbę autora. Stanowią tożsamość wizualną projektu i nie są objęte licencją MIT: nie używaj ich w innym projekcie ani w sposób wprowadzający w błąd.
