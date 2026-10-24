# yt-dlp GUI — wersja dla Linuksa

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Wersja zapoznawcza.** Ten dokument uzupełnia [główny README](README.pl.md): to ten sam program, ale tutaj omawiamy tylko to, co jest specyficzne dla Linuksa (instalacja, pliki cookie i pęki kluczy, pliki, rozwiązywanie problemów). Nowości w każdej wersji znajdują się w [CHANGELOG-linux.md](../CHANGELOG-linux.md). Tłumaczenia nadal wymagają sprawdzenia przez rodzimych użytkowników języka; w razie wątpliwości obowiązują wersje francuska i angielska.

## Spis treści

1. [Stan wersji zapoznawczej](#s1)
2. [Instalacja](#s2)
3. [Pierwsze uruchomienie i zależności](#s3)
4. [Pliki cookie przeglądarki](#s4)
5. [Pęki kluczy: operacje ręczne](#s5)
6. [Gdzie są pliki](#s6)
7. [Rozwiązywanie problemów](#s7)
8. [Zgłaszanie błędu](#s8)
9. [Dla programistów](#s9)

<a id="s1"></a>

## 1. Stan wersji zapoznawczej

Wersja dla Linuksa odtwarza zachowanie wersji dla Windows 0.1.7 (zamrożonej, służącej za wzór). Jest publikowana jako **wersja wstępna (pre-release) na GitHubie** pod znacznikami `Linux-vX.Y.Z`: nigdy nie jest przedstawiana jako „najnowsze wydanie” repozytorium.

**Co wypróbowano** (maszyna wirtualna Debian 12, pulpit GNOME, Python 3.11, prawdziwe konto YouTube zalogowane w każdej przeglądarce, październik 2026):

- **Pliki cookie Firefoksa, Waterfoksa, Floorpa i Zen Browser**: odczytane przy otwartej lub zamkniętej przeglądarce.
- **Pliki cookie Google Chrome, Chromium, Brave, Vivaldi, Opery i Microsoft Edge**: odczytane przy **zamkniętej** przeglądarce, po jednorazowym uruchomieniu każdej z nich i zalogowaniu się w niej do YouTube (zob. [sekcja 5](#s5)). Pojedyncze pobieranie i Inspektor playlist zadziałały.
- **LibreWolf**: odczyt tylko wtedy, gdy jest otwarty i zalogowany (domyślnie usuwa swoje cookie przy zamknięciu).
- **Film prywatny** z plikami cookie Firefoksa oraz playlista z trzema filmami, z których jeden jest prywatny.
- **Pakiety**: AppImage i archiwum `.tar.gz` buduje CI na Ubuntu 22.04; pakiet `.deb` został zbudowany, zainstalowany, uruchomiony i usunięty w Debianie 12; AppImage, archiwum i `.deb` uruchomiono w maszynie wirtualnej, a „Zainstaluj w menu” / „Odinstaluj” wypróbowano myszą z AppImage (ikona dodana, a potem usunięta z menu i z Pulpitu).
- **Język i czcionka**: koreański wybrany na maszynie bez koreańskiej czcionki; okno „Font needed” proponuje czcionkę, jest ona pobierana i sprawdzana, program uruchamia się ponownie i tekst jest czytelny.

**Czego jeszcze nie wypróbowano**:

- innych dystrybucji (Ubuntu, Fedora, Arch, openSUSE…) i pulpitów innych niż GNOME, w tym KDE Plasma (KWallet);
- przeglądarek zainstalowanych jako Flatpak lub Snap (poza układem LibreWolfa we Flatpaku, który zaobserwowano);
- Vivaldi, Opery lub Edge **bez** zainstalowanego Chrome ani Chromium (zob. [sekcja 5](#s5));
- architektury aarch64 (program ją przewiduje, ale pakiety są budowane tylko dla x86_64);
- prawdziwego komputera z Linuksem, poza maszyną wirtualną (prawdziwego pulpitu i sprzętu);
- tłumaczeń: nadal wymagają sprawdzenia przez rodzimych użytkowników języka.

<a id="s2"></a>

## 2. Instalacja

### Jaki format wybrać

| Format | Dla kogo | Uprawnienia administratora | Pozycja w menu |
|---|---|---|---|
| **AppImage** | każda nowa 64-bitowa dystrybucja | nie | „Zainstaluj w menu” (sekcja 2.3) |
| **Archiwum `.tar.gz`** | jak wyżej, bez AppImage i FUSE | nie | „Zainstaluj w menu” |
| **Pakiet `.deb`** | Debian, Ubuntu i pochodne | tak (`sudo`) | automatyczna |
| **Kod źródłowy** | programiści, próby | nie | brak |

Wymagania: 64-bitowy Linux (x86_64) z dystrybucji z 2022 roku lub nowszej (glibc 2.35 lub nowsza), ponieważ pakiety są budowane na Ubuntu 22.04.

**Jeśli dopiero zaczynasz z Linuksem**: tylko pakiet `.deb` jest instalowany „naprawdę” i pojawia się w menedżerze oprogramowania. AppImage i archiwum to zwykłe pliki lub foldery, przechowywane tam, gdzie chcesz: aby je usunąć, wystarczy skasować je jak każdy inny plik (sekcje 2.2 i 2.5). Ich ustawienia są przechowywane osobno, w `~/.local/share/yt-dlp-GUI` (sekcja 6), i przetrwają to usunięcie.

Pliki są na [stronie wydań](https://github.com/harlockSuites/YT-dlp-GUI/releases): szukaj znaczników `Linux-v…` oznaczonych „Pre-release”.

### 2.1 Weryfikacja pobranego pliku

Pobierz też `SHA256SUMS-linux.txt` do tego samego folderu, a następnie:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Każdy obecny plik powinien pokazać `OK`. To dowodzi, że Twój plik jest identyczny z opublikowanym, a nie że jest nieszkodliwy: kod źródłowy i automatyczny proces budowania są publiczne.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

AppImage wymaga biblioteki FUSE 2:

| Dystrybucja | Pakiet |
|---|---|
| Debian, Ubuntu 22.04 i pochodne | `libfuse2` |
| Ubuntu 24.04 i nowsze | `libfuse2t64` |
| Fedora | `fuse-libs` |

Bez FUSE i tak go uruchom; sam rozpakuje się do folderu tymczasowego:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

AppImage nie jest „instalowany”: nie pojawia się w menedżerze oprogramowania. Aby go usunąć, skasuj plik:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

Aby znaleźć AppImage w menu aplikacji, wraz z ikoną, użyj funkcji **„Zainstaluj w menu…” wbudowanej w program** (sekcja 2.3): nie trzeba wpisywać żadnego polecenia.

### 2.3 Zainstaluj w menu (bez administratora)

AppImage uruchomiony dwukliknięciem nie zostawia ikony w menu aplikacji. W programie: menu opcji › **„Zainstaluj w menu…”**. To okno:

- kopiuje program do `~/.local/share/yt-dlp-GUI/app/`;
- zapisuje starter `~/.local/share/applications/yt-dlp-gui.desktop` i ikonę `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- dodaje, jeśli pole jest zaznaczone, skrót na Pulpicie (oznaczony jako „zaufany” dla GNOME, gdy istnieje narzędzie `gio`);
- potem oferuje „Zaktualizuj” (kopiuje ponownie działającą wersję) i „Odinstaluj”.

„Odinstaluj” usuwa tylko to, co utworzyła instalacja, i **zachowuje Twoje ustawienia** oraz pobrane narzędzia. Starter bez naszego wewnętrznego znacznika (`X-YtDlpGui-Installer=1`) nigdy nie jest usuwany.

Ograniczenia: okno jest dostępne z AppImage i z archiwum. Z kodu źródłowego odsyła do AppImage; z pakietu `.deb` wyjaśnia, że program jest już w menu.

Jeśli skrót na Pulpicie pokazuje ostrzeżenie: kliknij ikonę prawym przyciskiem › „Zezwól na uruchamianie”. Niektóre pulpity (domyślnie GNOME) nie pokazują ikon na Pulpicie: starter w menu działa zawsze.

Aby usunąć wszystko ręcznie:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

Jeśli pakiet `.deb` jest już zainstalowany, nie używaj tej funkcji: program jest już w menu i pojawiłaby się druga pozycja „yt-dlp GUI” (najpierw usuń `.deb` poleceniem `sudo apt remove yt-dlp-gui`, jeśli wolisz tę metodę).

### 2.4 Pakiet `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Program trafia do `/opt/yt-dlp-gui`, wraz z dowiązaniem `/usr/bin/yt-dlp-gui`, starterem w menu, ikoną i licencją (`/usr/share/doc/yt-dlp-gui/`). Zależy od `libc6 (>= 2.35)` i `libx11-6`.

Aby go usunąć (Twoje ustawienia, w `~/.local/share/yt-dlp-GUI`, nigdy nie są ruszane):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Archiwum `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Aby ustawienia i narzędzia zostały **wewnątrz rozpakowanego folderu** (pendrive, próba bez śladów), utwórz pusty plik `portable.flag` obok pliku wykonywalnego:

```bash
touch yt-dlp-gui/portable.flag
```

Bez tego pliku dane trafiają do `~/.local/share/yt-dlp-GUI` (sekcja 6).

Archiwum nie jest „instalowane”: nie pojawia się w menedżerze oprogramowania. Aby je usunąć, skasuj rozpakowany folder:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Z kodu źródłowego

```bash
python3 yt-dlp-gui.pyw
```

Z kodu źródłowego ustawienia i pobrane narzędzia trafiają do tego samego folderu co w wersjach zainstalowanych (`~/.local/share/yt-dlp-GUI`): ponowne pobranie kodu lub usunięcie jego folderu ich nie kasuje. Aby dane zostały w folderze z kodem (próba bez śladów), utwórz pusty plik `portable.flag` obok `yt-dlp-gui.pyw`.

Potrzebny jest Python 3 z Tkinterem:

| Dystrybucja | Pakiet |
|---|---|
| Debian, Ubuntu i pochodne, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Aktualizacje

Codzienne sprawdzanie (które można wyłączyć w menu opcji) szuka wersji `Linux-vX.Y.Z`, razem z wersjami wstępnymi, i **nigdy** nie proponuje wersji dla Windows. Otwiera stronę pobierania pliku odpowiadającego Twojej instalacji (AppImage, archiwum lub `.deb`); **nic nie jest instalowane automatycznie**. Aby zaktualizować:

- **AppImage lub archiwum zainstalowane w menu**: pobierz nowy AppImage, uruchom go, potem „Zainstaluj w menu… › Zaktualizuj”;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **archiwum niezainstalowane**: rozpakuj nowe archiwum w miejsce starego.

### 2.8 Usunięcie wszystkiego, razem z danymi

Po usunięciu programu (sekcje od 2.3 do 2.5), aby skasować też ustawienia, kolejkę i pobrane narzędzia (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

Twoje pobrane filmy nigdy nie znajdują się w tym folderze.

<a id="s3"></a>

## 3. Pierwsze uruchomienie i zależności

Przy pierwszym uruchomieniu asystent instalacji proponuje pobranie **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (archiwum `.tar.xz` z oficjalnych kompilacji yt-dlp) i **deno** z ich repozytoriów na GitHubie. Sumy SHA-256 są weryfikowane, nie są wymagane uprawnienia administratora, a pliki trafiają do `~/.local/share/yt-dlp-GUI` (yt-dlp) i `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Asystent pozostaje dostępny w menu opcji.

Niezbędne są tylko ffmpeg i ffprobe; deno jest zalecany (dodatkowe ścieżki dźwiękowe). **AtomicParsley, MKVToolNix i aria2** są opcjonalne: okno „Zależności” pokazuje polecenie Twojego menedżera pakietów, do skopiowania w terminalu. Program nigdy sam go nie uruchamia. Te same polecenia:

| Menedżer pakietów | Polecenie |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Pliki cookie przeglądarki

yt-dlp odczytuje pliki cookie **lokalnie**, w wybranej przeglądarce (dodatkowe ścieżki dźwiękowe, napisy, filmy prywatne, treści dla członków). Domyślnie program proponuje pięć najczęściej używanych przeglądarek w Linuksie (Firefox, Google Chrome, Chromium, Brave, Vivaldi). Pozycja **„Przeglądarki dla cookies…”** w menu opcji otwiera okno „Przeglądarki dla cookies”, które oferuje 11: zaznacz te, których potrzebujesz; znak ✔ oznacza te, których folder profilu istnieje na Twoim komputerze.

| Przeglądarka | Odczytywana przez yt-dlp jako | Pęk kluczy | Przeszukiwane foldery profilu |
|---|---|---|---|
| Firefox | `firefox` | nie | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | tak | `~/.config/google-chrome` |
| Chromium | `chromium` | tak | `~/.config/chromium` |
| Brave | `brave` | tak | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | tak | `~/.config/vivaldi` |
| Opera | `opera` | tak | `~/.config/opera` |
| Microsoft Edge | `edge` | tak | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + folder profilu | nie | `~/.librewolf`, `~/.config/librewolf`… (ten sam schemat dla pozostałych), razem z Flatpakiem |

Pochodne Firefoksa nie mają nazwy znanej yt-dlp: program szuka ich bazy `cookies.sqlite` (do trzech poziomów pod ich folderami) i przekazuje yt-dlp folder ostatnio używanego profilu. `XDG_CONFIG_HOME` jest uwzględniany, gdy jest ścieżką bezwzględną.

**Wskaźnik** obok listy pokazuje stan: czerwony (wyłączone lub błąd), pomarańczowy (nie przetestowano lub w toku), zielony (cookie odczytane). Przycisk ↻ uruchamia test; podpowiedź wyjaśnia błąd. Test, który odczytuje **0 plików cookie**, nigdy nie jest zielony.

### Częste przypadki

| Co widzisz | Prawdopodobna przyczyna | Co zrobić |
|---|---|---|
| „Extracted 0 cookies”, a potem „Sign in to confirm you're not a bot” | przeglądarka nie trzyma żadnych cookie na dysku (LibreWolf domyślnie usuwa je przy zamknięciu; profil nigdy nie był zalogowany; tryb prywatny) | zostawić ją otwartą i zalogowaną w YouTube albo wyłączyć usuwanie cookie przy zamknięciu w jej ustawieniach prywatności |
| „Item does not exist!” z Chrome, Chromium, Brave, Vivaldi, Operą lub Edge | yt-dlp nie znalazł klucza przeglądarki w pęku kluczy pulpitu | uruchomić przeglądarkę raz, zalogować się do YouTube, zamknąć ją i powtórzyć test; w przeciwnym razie [sekcja 5](#s5) |
| „Could not copy Chrome cookie database” lub „database is locked” | przeglądarka blokuje swoją bazę, gdy działa | zamknąć ją i powtórzyć test |
| „Failed to decrypt” | cookie zaszyfrowane kluczem, którego yt-dlp nie uzyskał | [sekcja 5](#s5) |

### Test przeglądarki z terminala

To najlepszy sposób, by zobaczyć dokładny błąd (zastąp `IDENTIFIER` identyfikatorem dowolnego filmu z YouTube):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Linie, których należy szukać: `Extracted N cookies from chromium` (N musi być większe od 0), `Chosen keyring: GNOMEKEYRING` (wybrany pęk kluczy) oraz `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (cookie `v11` wymagają pęku kluczy, `v10` nie).

Dla pochodnej Firefoksa podaj folder profilu. Aby go znaleźć:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

W instalacji Flatpak szukaj w `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Potem, z folderem zawierającym `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Pęki kluczy: operacje ręczne

### Do czego służy pęk kluczy

Przeglądarki z rodziny Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) szyfrują swoje cookie. Klucz szyfrujący jest przechowywany w **pęku kluczy pulpitu**: GNOME Keyring (lub zgodnym odpowiedniku, przez „Secret Service”) w GNOME, XFCE, Cinnamon, MATE…, KWallet w KDE. Aby odszyfrować cookie, yt-dlp prosi pęk kluczy o ten klucz. Firefox i jego pochodne go nie potrzebują.

Dwa przydatne fakty:

- **Klucz istnieje dopiero po pierwszym uruchomieniu przeglądarki.** W naszej maszynie wirtualnej błąd „Item does not exist!” zniknął, gdy każdą przeglądarkę uruchomiono raz i zalogowano w niej do YouTube. Dokładnej przyczyny pierwszego niepowodzenia nie ustalono z pewnością: pęk kluczy istniał, był domyślny i odblokowany.
- **Z którego pęku kluczy korzysta yt-dlp**, zależy od wykrytego pulpitu (zmienne `XDG_CURRENT_DESKTOP` i `DESKTOP_SESSION`), według kodu yt-dlp (październik 2026):

| Wykryty pulpit | Pęk kluczy używany przez yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, nierozpoznany pulpit (same menedżery okien: sway, i3…) | brak: zwykły tekst (`BASICTEXT`) |

W ostatnim przypadku yt-dlp odczytuje tylko cookie `v10`: jeśli Twoja przeglądarka trzyma klucz w GNOME Keyring, jej cookie `v11` nie zostaną odszyfrowane. Wtedy trzeba wymusić pęk kluczy z terminala (sekcja 5.6); program nie oferuje jeszcze tego ustawienia.

Elementy wyszukiwane w pęku kluczy nazywają się „*nazwa* Safe Storage”. Według kodu yt-dlp jest to **„Chrome Safe Storage”** dla Chrome i Vivaldi, **„Chromium Safe Storage”** dla Chromium, Opery i Edge, **„Brave Safe Storage”** dla Brave. W naszej maszynie wirtualnej były też zainstalowane i uruchomione Chrome i Chromium: nie wiemy, czy Vivaldi, Opera lub Edge działałyby samodzielnie.

### 5.1 Czy pęk kluczy istnieje?

```bash
ls -la ~/.local/share/keyrings/
```

Powinieneś zobaczyć plik `login.keyring` (pęk kluczy „login”). Następnie: który pęk kluczy jest **domyślny**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Odpowiedź `(objectpath '/org/freedesktop/secrets/collection/login',)`: istnieje domyślny pęk kluczy. Odpowiedź `'/'`: **brak**, przejdź do sekcji 5.4.

### 5.2 Czy jest zablokowany?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: odblokowany. `(<true>,)`: zablokowany; otwórz go w Seahorse (sekcja 5.4), który zapyta o jego hasło.

### 5.3 Czy jest w nim klucz mojej przeglądarki?

Wypisz elementy:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

Odpowiedź zawiera ścieżki kończące się numerem (`…/login/1`, `…/login/2`…). Aby odczytać nazwę każdego z nich (dostosuj listę numerów):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Powinieneś zobaczyć na przykład `Chromium Safe Storage`, `Chrome Safe Storage` lub `Brave Safe Storage`. Puste nazwy są nieszkodliwe. Jeśli brakuje nazwy Twojej przeglądarki: uruchom ją raz, zaloguj się do YouTube, zamknij ją i ponownie wykonaj to polecenie.

### 5.4 Tworzenie lub odblokowanie pęku kluczy w Seahorse

Zainstaluj Seahorse („Hasła i klucze”) oraz powiązane narzędzia. Dokładne polecenie jest też w oknie „Przeglądarki dla cookies” programu:

| Menedżer pakietów | Polecenie |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Potem go otwórz:

```bash
seahorse
```

- **Brak domyślnego pęku kluczy**: utwórz go (przycisk „+” lub menu Plik › Nowy › pęk kluczy haseł), nazwij „Login”, potem kliknij go prawym przyciskiem › „Ustaw jako domyślny”. Dokładne nazwy zależą od wersji Seahorse.
- **Zablokowany pęk kluczy**: dwukrotne kliknięcie lub prawy przycisk › „Odblokuj”, potem wpisz jego hasło (wpisz je sam, program nigdy o nie nie prosi).
- **Automatyczne logowanie**: pęk kluczy chroniony hasłem nie może otworzyć się sam, jeśli przy starcie sesji nie wpisujesz żadnego hasła; pozostaje zablokowany, dopóki go nie odblokujesz (albo dopóki nie użyjesz tego samego hasła do sesji i do pęku kluczy).

Potem **uruchom przeglądarkę, zaloguj się do YouTube, zamknij ją** i powtórz test (sekcja 4).

### 5.5 KDE Plasma (KWallet)

W KDE yt-dlp odpytuje KWallet (`kwallet-query`). Menedżer nazywa się `kwalletmanager` (lub `kwalletmanager5`), zależnie od dystrybucji. Ta konfiguracja **nie została wypróbowana** w naszych testach.

### 5.6 Wymuszenie pęku kluczy w yt-dlp (terminal)

Program pozwala yt-dlp wybrać pęk kluczy zależnie od pulpitu. Aby go wymusić, dodaj `+PĘK` do nazwy przeglądarki (wartości: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Aby sprawdzić, z którego pęku kluczy Chromium faktycznie korzysta (polecenie z kodu yt-dlp, tu niewypróbowane):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Bez pęku kluczy: `--password-store=basic` (zaawansowane, niewypróbowane)

Chromium akceptuje `--password-store=basic`: wtedy przechowuje swój klucz jawnie (stały, powszechnie znany klucz) i szyfruje nowe cookie jako `v10`, które yt-dlp odczytuje bez pęku kluczy (`chromium+basictext`). **To mniej bezpieczne**: każdy program, który może czytać Twoje pliki, może odszyfrować te cookie. Używaj tego tylko wtedy, gdy rozumiesz ten kompromis; już zapisane cookie prawdopodobnie nie są przekodowywane: zaloguj się ponownie.

### 5.8 Ostateczność

Jeśli pęk kluczy jest uszkodzony, **najpierw zrób jego kopię zapasową**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Usunięcie `login.keyring` kasuje **wszystkie** zawarte w nim hasła (Wi-Fi, konta online…): nie rób tego, nie rozumiejąc konsekwencji.

<a id="s6"></a>

## 6. Gdzie są pliki

Folder danych to `$XDG_DATA_HOME/yt-dlp-GUI` (domyślnie `~/.local/share/yt-dlp-GUI`), chyba że `portable.flag` leży obok pliku wykonywalnego archiwum (lub skryptu `yt-dlp-gui.pyw`).

| Plik lub folder | Zawartość |
|---|---|
| `gui-config.json` | ustawienia (język, przeglądarka, foldery, wybór przeglądarek…) |
| `download-queue.json` | kolejka pobierania |
| `custom-blocks.json` | własne bloki opcji |
| `yt-dlp` | plik wykonywalny pobrany przez asystenta |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | tymczasowe pliki konfiguracyjne yt-dlp |
| `app/` | kopia programu wykonana przez „Zainstaluj w menu” |
| `~/.local/share/fonts/yt-dlp-GUI/` (poza folderem danych) | czcionka Noto pobrana dla koreańskiego, japońskiego lub chińskiego; aby ją usunąć: `rm -rf ~/.local/share/fonts/yt-dlp-GUI` |

<a id="s7"></a>

## 7. Rozwiązywanie problemów

| Problem | Wskazówka |
|---|---|
| AppImage się nie uruchamia | uruchomić go z terminala, aby przeczytać błąd; zainstalować FUSE 2 (sekcja 2.2) lub dodać `--appimage-extract-and-run` |
| Nic się nie wyświetla albo błąd biblioteki | sprawdzić wersję glibc: `ldd --version` musi wskazywać 2.35 lub nowszą |
| Brak ikony na Pulpicie | GNOME domyślnie jej nie pokazuje; użyj menu aplikacji |
| Skrót na Pulpicie z ostrzeżeniem | prawy przycisk › „Zezwól na uruchamianie” |
| Przeciąganie i upuszczanie między hostem a maszyną wirtualną nie działa | to funkcja VirtualBoxa (Guest Additions), nie programu |
| Interfejs ma zły rozmiar | program używa czcionek systemowych (Tk); spróbuj innego rozmiaru czcionki systemowej |
| Aktualizacja yt-dlp się nie powiodła | użyj „Aktualizacja i diagnostyka” w menu opcji; w przeciwnym razie pobierz `yt-dlp_linux` i wskaż go w oknie zamiany (wybrany plik zostanie uczyniony wykonywalnym) |
| Kwadraty zamiast tekstu (koreański, chiński, japoński…) | żadna czcionka systemowa nie zawiera tych znaków; w Debianie i Ubuntu: `sudo apt install fonts-noto-cjk` (~90 MB), potem zamknąć i ponownie otworzyć program; w innych dystrybucjach zainstalować pakiet „Noto Sans CJK” dystrybucji; program może też sam pobrać czcionkę (koreański, japoński, chiński) po wybraniu języka, bez uprawnień administratora |

<a id="s8"></a>

## 8. Zgłaszanie błędu

Przycisk „Zgłoś błąd” przygotowuje raport techniczny, w którym Twoje foldery, nazwa użytkownika i adresy e-mail są zamaskowane; nic nie jest wysyłane automatycznie. Dla Linuksa dodaj do niego:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

i napisz, **jak** zainstalowano program (AppImage, archiwum, `.deb`, kod źródłowy) oraz — przy problemie z cookie — **wynik testu z terminala** (sekcja 4), bez wklejania swoich cookie.

<a id="s9"></a>

## 9. Dla programistów

Testy (na wirtualnym ekranie, bez prawdziwego ekranu):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Budowanie pakietów (narzędzia: `pip install -r packaging/requirements-build.txt`, a także `appimagetool`, którego ścieżkę podaje zmienna `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

Wyniki trafiają do `dist/`. Dla najlepszej zgodności buduj na najstarszej obsługiwanej dystrybucji (glibc maszyny budującej to minimum wymagane od maszyn uruchamiających program). Przydatne kontrole pakietu `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

Jedyny znany błąd formalny to `dir-or-file-in-opt` (program umieszczony w `/opt`).

**Publikowanie**: sprawdzić `__version__` w `yt-dlp-gui.pyw`, opatrzyć datą sekcję wersji w `CHANGELOG-linux.md`, zrobić commit, potem utworzyć i wypchnąć znacznik `Linux-vX.Y.Z`. Przepływ „Release Linux” uruchamia testy, buduje AppImage, archiwum i `.deb`, liczy sumy i tworzy wydanie jako **wersję wstępną (pre-release)**, nigdy jako „najnowsze wydanie” (sprawdzanie aktualizacji wersji dla Windows 0.1.7 nie może tam znaleźć znacznika Linuksa).

Licencja: MIT, jak reszta repozytorium (zob. [LICENSE](../LICENSE)).
