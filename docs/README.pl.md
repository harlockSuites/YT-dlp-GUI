# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Graficzny interfejs dla [yt-dlp](https://github.com/yt-dlp/yt-dlp), stworzony, aby uczynić go dostępnym dla wszystkich i w pełni wykorzystać jego możliwości.

> **Projekt w trakcie rozwoju.** Niektóre funkcje mogą się zmienić, być niekompletne lub zawierać błędy.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funkcje

### Pojedyncze pobieranie i kolejka

- **Opcje**: maksymalna jakość (do 4K), tylko dźwięk (MP3), napisy (formaty vtt, srt, ass), osadzanie napisów i miniatury, główny język ścieżki dźwiękowej, dodatkowe ścieżki audio (wielościeżkowy plik MKV) oraz biblioteka „bloków skryptów” (postprodukcja, eksport, sieć, zachowanie), którą można uzupełnić własnymi blokami.
- **Wygenerowane polecenie**: polecenie yt-dlp odpowiadające Twoim wyborom jest wyświetlane na bieżąco.
- **Kolejka**: dodaj bieżący adres URL, a następnie uruchom całą kolejkę, od wybranej pozycji, pojedynczy film lub zakres; pauza i wznowienie, pominięcie bieżącej pozycji, zatrzymanie z usunięciem plików częściowych. Kolejka jest zachowywana między sesjami.

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

- Wybierz przeglądarkę (Chrome, Firefox, Edge, Brave, Opera), z której yt-dlp lokalnie odczytuje ciasteczka: są potrzebne do dodatkowych ścieżek audio i niektórych napisów.
- **Wskaźnik** pokazuje stan: czerwony, gdy wyłączone lub błąd, pomarańczowy, gdy nie przetestowano lub trwa test, zielony, gdy ciasteczka są wczytane. Przycisk ↻ uruchamia test, a podpowiedź wyjaśnia stan lub błąd.

### Asystent instalacji, zależności i aktualizacje yt-dlp

- **Asystent instalacji**: przy pierwszym uruchomieniu proponuje pobranie yt-dlp i ffmpeg z ich oficjalnych repozytoriów GitHub. Suma kontrolna SHA-256 jest weryfikowana i nie są potrzebne uprawnienia administratora.
- **Zależności**: dedykowane okno sprawdza ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 i deno oraz może je zainstalować przez Chocolatey.
- **Aktualizacja i diagnostyka**: aktualizuje yt-dlp (`yt-dlp -U`) lub podmienia jego plik wykonywalny, pokazuje wersję i sprawdza opcje używane przez interfejs.
- **Aktualizacja programu**: codzienne sprawdzanie (można je wyłączyć) sygnalizuje nową wersję dyskretnym paskiem; osobne okno pokazuje nowości i otwiera pobieranie odpowiednie dla Twojej instalacji (instalator lub wersja przenośna). Nic nie jest instalowane automatycznie.

### Interfejs i języki

- Elementy sterujące zawijają się zależnie od szerokości okna; zawartość przewija się pionowo, a tabela inspektora także poziomo.
- Interfejs w **15 językach**: francuski, angielski, hiszpański, portugalski, włoski, polski, węgierski, serbski, rosyjski, wietnamski, chiński, hindi, japoński, koreański i filipiński. Zmiana języka działa po ponownym uruchomieniu, z możliwością natychmiastowego restartu.

### Zgłoś błąd

- Przycisk „Zgłoś błąd” przygotowuje raport techniczny: wersje programu, Pythona, Windows i yt-dlp, niegroźne ustawienia i ostatnie linie dziennika. Twoje foldery, nazwa użytkownika i adresy e-mail są zasłaniane.
## Instalacja

- **Instalator (zalecany)**: pobierz `yt-dlp-gui-setup-X.Y.Z.exe` ze [strony wydań](https://github.com/harlockSuites/YT-dlp-GUI/releases) i uruchom go. Windows 10 lub 11 (64-bitowy), bez uprawnień administratora; Python nie jest potrzebny.
- **Wersja przenośna**: pobierz `yt-dlp-gui-portable-X.Y.Z.zip`, rozpakuj w dowolnym miejscu i uruchom `yt-dlp-gui.exe`; ustawienia zostają w tym folderze.
- **Z kodu źródłowego**: zobacz sekcje „Wymagania” i „Szybki start” poniżej.
- **Ostrzeżenie Windows SmartScreen**: instalator nie jest podpisany cyfrowo, więc Windows może wyświetlić „System Windows ochronił ten komputer”. Kliknij „Więcej informacji”, a następnie „Uruchom mimo to”. Aby sprawdzić autentyczność pliku, porównaj jego sumę SHA-256 z sumą z pliku `SHA256SUMS.txt` publikowanego z każdą wersją:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Nic nie jest wysyłane automatycznie: sprawdzasz i edytujesz raport, a następnie otwierasz wstępnie wypełnioną stronę zgłoszenia GitHub (lub kopiujesz raport).

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

- To oprogramowanie nie wysyła żadnych danych autorowi i nie zawiera telemetrii. Połączenia sieciowe realizują yt-dlp (serwisy wideo), asystent instalacji (GitHub) i narzędzie rejestru (wyszukiwanie w YouTube). Automatyczne sprawdzanie aktualizacji także łączy się z GitHubem przy uruchomieniu (najwyżej raz dziennie); można je wyłączyć w „Sprawdź aktualizację programu…”.
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

Kod jest udostępniony na licencji [MIT](../LICENSE). Logo i baner „Harlock S.” (folder `assets/`) są osobistą marką autora i nie są objęte tą licencją: wszelkie prawa zastrzeżone.
