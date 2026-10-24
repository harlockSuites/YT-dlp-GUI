# yt-dlp GUI — versione per Linux

[Français](../README-LINUX.md) · [English](README-LINUX.en.md) · [Español](README-LINUX.es.md) · [Português](README-LINUX.pt.md) · [Italiano](README-LINUX.it.md) · [Polski](README-LINUX.pl.md) · [Magyar](README-LINUX.hu.md) · [Srpski](README-LINUX.sr.md) · [Русский](README-LINUX.ru.md) · [Tiếng Việt](README-LINUX.vi.md) · [中文](README-LINUX.zh.md) · [हिन्दी](README-LINUX.hi.md) · [日本語](README-LINUX.ja.md) · [한국어](README-LINUX.ko.md) · [Filipino](README-LINUX.fil.md)

> **Anteprima.** Questo documento integra il [README principale](README.it.md): è lo stesso programma, ma qui si tratta solo di ciò che è specifico di Linux (installazione, cookie e portachiavi, file, risoluzione dei problemi). Le novità di ogni versione sono in [CHANGELOG-linux.md](../CHANGELOG-linux.md). Le traduzioni devono ancora essere riviste da madrelingua; in caso di dubbio fanno fede i testi in francese e in inglese.

## Indice

1. [Stato dell'anteprima](#s1)
2. [Installare](#s2)
3. [Primo avvio e dipendenze](#s3)
4. [Cookie del browser](#s4)
5. [Portachiavi: operazioni manuali](#s5)
6. [Dove si trovano i file](#s6)
7. [Risoluzione dei problemi](#s7)
8. [Segnalare un bug](#s8)
9. [Per gli sviluppatori](#s9)

<a id="s1"></a>

## 1. Stato dell'anteprima

La versione per Linux riproduce il comportamento della versione per Windows 0.1.7 (congelata, usata come modello). È pubblicata come **anteprima (pre-release) di GitHub** con tag `Linux-vX.Y.Z`: non viene mai presentata come «ultima versione» del repository.

**Cosa è stato provato** (macchina virtuale Debian 12, desktop GNOME, Python 3.11, un vero account YouTube con accesso effettuato in ogni browser, ottobre 2026):

- **Cookie di Firefox, Waterfox, Floorp e Zen Browser**: letti con il browser aperto o chiuso.
- **Cookie di Google Chrome, Chromium, Brave, Vivaldi, Opera e Microsoft Edge**: letti con il browser **chiuso**, dopo aver avviato ogni browser una volta e aver effettuato l'accesso a YouTube (vedi la [sezione 5](#s5)). Il download singolo e l'Ispettore di playlist hanno funzionato.
- **LibreWolf**: letti solo mentre è aperto e con l'accesso effettuato (per impostazione predefinita elimina i cookie alla chiusura).
- **Video privato** con i cookie di Firefox, e una playlist di tre video di cui uno privato.
- **Pacchetti**: l'AppImage e l'archivio `.tar.gz` sono costruiti dalla CI su Ubuntu 22.04; il `.deb` è stato costruito, installato, avviato e rimosso su Debian 12; «Installa nel menu» è stato provato con la vera AppImage in una cartella personale usa e getta.

**Cosa non è ancora stato provato**:

- altre distribuzioni (Ubuntu, Fedora, Arch, openSUSE…) e desktop diversi da GNOME, compreso KDE Plasma (KWallet);
- browser installati come Flatpak o Snap (tranne la struttura di LibreWolf in Flatpak, che è stata osservata);
- Vivaldi, Opera o Edge **senza** Chrome né Chromium installati (vedi la [sezione 5](#s5));
- l'architettura aarch64 (il programma la prevede, ma i pacchetti sono costruiti solo per x86_64);
- la finestra «Installa nel menu» usata con il mouse su un desktop reale (è testata via programma);
- le traduzioni: devono ancora essere riviste da madrelingua.

<a id="s2"></a>

## 2. Installare

### Quale formato scegliere

| Formato | Per chi | Diritti di amministratore | Voce nel menu |
|---|---|---|---|
| **AppImage** | qualsiasi distribuzione recente a 64 bit | no | «Installa nel menu» (sezione 2.3) |
| **Archivio `.tar.gz`** | idem, senza AppImage né FUSE | no | «Installa nel menu» |
| **Pacchetto `.deb`** | Debian, Ubuntu e derivate | sì (`sudo`) | automatica |
| **Codice sorgente** | sviluppatori, prove | no | nessuna |

Requisiti: Linux a 64 bit (x86_64) di una distribuzione del 2022 o più recente (glibc 2.35 o superiore), perché i pacchetti sono costruiti su Ubuntu 22.04.

**Se sei alle prime armi con Linux**: solo il pacchetto `.deb` viene installato «per davvero» e compare nel gestore di software. L'AppImage e l'archivio sono file o cartelle normali, tenuti dove preferisci: per rimuoverli basta eliminarli come qualsiasi altro file (sezioni 2.2 e 2.5). Le loro impostazioni restano a parte, in `~/.local/share/yt-dlp-GUI` (sezione 6), e sopravvivono a quell'eliminazione.

I file sono nella [pagina delle versioni pubblicate](https://github.com/harlockSuites/YT-dlp-GUI/releases): cerca i tag `Linux-v…`, contrassegnati come «Pre-release».

### 2.1 Verificare il download

Scarica anche `SHA256SUMS-linux.txt` nella stessa cartella, poi:

```bash
sha256sum -c SHA256SUMS-linux.txt --ignore-missing
```

Ogni file presente deve mostrare `OK`. Questo dimostra che il tuo file è identico a quello pubblicato, non che sia innocuo: il codice sorgente e la compilazione automatica sono pubblici.

### 2.2 AppImage

```bash
chmod +x yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

L'AppImage richiede la libreria FUSE 2:

| Distribuzione | Pacchetto |
|---|---|
| Debian, Ubuntu 22.04 e derivate | `libfuse2` |
| Ubuntu 24.04 e successive | `libfuse2t64` |
| Fedora | `fuse-libs` |

Senza FUSE, avviala comunque: si estrae da sola in una cartella temporanea:

```bash
./yt-dlp-gui-X.Y.Z-x86_64.AppImage --appimage-extract-and-run
```

L'AppImage non è «installata»: non compare nel gestore di software. Per rimuoverla, elimina il file:

```bash
rm yt-dlp-gui-X.Y.Z-x86_64.AppImage
```

### 2.3 Installa nel menu (senza amministratore)

Un'AppImage avviata con un doppio clic non lascia alcuna icona nel menu delle applicazioni. Nel programma: menu delle opzioni › **«Installa nel menu…»**. La finestra:

- copia il programma in `~/.local/share/yt-dlp-GUI/app/`;
- scrive il lanciatore `~/.local/share/applications/yt-dlp-gui.desktop` e l'icona `~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png`;
- aggiunge, se la casella è spuntata, un collegamento sul Desktop (contrassegnato come «attendibile» per GNOME quando esiste lo strumento `gio`);
- poi propone «Aggiorna» (ricopia la versione in esecuzione) e «Disinstalla».

«Disinstalla» rimuove solo ciò che l'installazione ha creato e **conserva le tue impostazioni** e gli strumenti scaricati. Un lanciatore senza il nostro marcatore interno (`X-YtDlpGui-Installer=1`) non viene mai eliminato.

Limiti: la finestra è disponibile dall'AppImage e dall'archivio. Dal codice sorgente rimanda all'AppImage; dal pacchetto `.deb` spiega che il programma è già nel menu.

Se il collegamento sul Desktop mostra un avviso: clic destro sull'icona › «Consenti avvio». Alcuni desktop (GNOME per impostazione predefinita) non mostrano icone sul Desktop: il lanciatore del menu funziona in ogni caso.

Per rimuovere tutto a mano:

```bash
rm -rf ~/.local/share/yt-dlp-GUI/app ~/.local/share/applications/yt-dlp-gui.desktop ~/.local/share/icons/hicolor/256x256/apps/yt-dlp-gui.png ~/Desktop/yt-dlp-gui.desktop
```

### 2.4 Pacchetto `.deb`

```bash
sudo apt install ./yt-dlp-gui_X.Y.Z_amd64.deb
```

Il programma va in `/opt/yt-dlp-gui`, con il collegamento `/usr/bin/yt-dlp-gui`, il lanciatore del menu, l'icona e la licenza (`/usr/share/doc/yt-dlp-gui/`). Dipende da `libc6 (>= 2.35)` e da `libx11-6`.

Per rimuoverlo (le tue impostazioni, in `~/.local/share/yt-dlp-GUI`, non vengono mai toccate):

```bash
sudo apt remove yt-dlp-gui
```

### 2.5 Archivio `.tar.gz`

```bash
tar xzf yt-dlp-gui-linux-X.Y.Z-x86_64.tar.gz
```

```bash
./yt-dlp-gui/yt-dlp-gui
```

Per tenere impostazioni e strumenti **dentro la cartella estratta** (chiavetta USB, prova senza lasciare tracce), crea un file vuoto `portable.flag` accanto all'eseguibile:

```bash
touch yt-dlp-gui/portable.flag
```

Senza questo file, i dati vanno in `~/.local/share/yt-dlp-GUI` (sezione 6).

L'archivio non è «installato»: non compare nel gestore di software. Per rimuoverlo, elimina la cartella estratta:

```bash
rm -rf yt-dlp-gui
```

### 2.6 Dal codice sorgente

```bash
python3 yt-dlp-gui.pyw
```

Dal codice sorgente, impostazioni e strumenti scaricati vanno nella stessa cartella delle versioni installate (`~/.local/share/yt-dlp-GUI`): riscaricare il codice o eliminare la sua cartella non li cancella. Per tenere i dati dentro la cartella del codice (prova senza lasciare tracce), crea un file vuoto `portable.flag` accanto a `yt-dlp-gui.pyw`.

Serve Python 3 con Tkinter:

| Distribuzione | Pacchetto |
|---|---|
| Debian, Ubuntu e derivate, openSUSE | `python3-tk` |
| Fedora | `python3-tkinter` |
| Arch | `tk` |

### 2.7 Aggiornamenti

Un controllo giornaliero (che si può disattivare nel menu delle opzioni) cerca le versioni `Linux-vX.Y.Z`, anteprime comprese, e **non** propone mai una versione per Windows. Apre la pagina di download del file che corrisponde alla tua installazione (AppImage, archivio o `.deb`); **non viene installato nulla automaticamente**. Per aggiornare:

- **AppImage o archivio installati nel menu**: scarica la nuova AppImage, avviala, poi «Installa nel menu… › Aggiorna»;
- **`.deb`**: `sudo apt install ./new-file.deb`;
- **archivio non installato**: estrai il nuovo archivio al posto del vecchio.

### 2.8 Rimuovere tutto, dati compresi

Dopo aver rimosso il programma (sezioni da 2.3 a 2.5), per cancellare anche le impostazioni, la coda e gli strumenti scaricati (yt-dlp, ffmpeg, deno):

```bash
rm -rf ~/.local/share/yt-dlp-GUI
```

I tuoi video scaricati non sono mai in questa cartella.

<a id="s3"></a>

## 3. Primo avvio e dipendenze

Al primo avvio, l'assistente di installazione propone di scaricare **yt-dlp** (`yt-dlp_linux`), **ffmpeg** (l'archivio `.tar.xz` delle build ufficiali di yt-dlp) e **deno** dai loro repository GitHub. Le somme SHA-256 sono verificate, non servono diritti di amministratore, e i file vanno in `~/.local/share/yt-dlp-GUI` (yt-dlp) e in `~/.local/share/yt-dlp-GUI/bin` (ffmpeg, ffprobe, deno). Resta disponibile nel menu delle opzioni.

Solo ffmpeg e ffprobe sono indispensabili; deno è consigliato (tracce audio secondarie). **AtomicParsley, MKVToolNix e aria2** sono facoltativi: la finestra «Dipendenze» mostra il comando del tuo gestore di pacchetti, da copiare in un terminale. Il programma non lo esegue mai da solo. Gli stessi comandi:

| Gestore di pacchetti | Comando |
|---|---|
| apt | `sudo apt install aria2 atomicparsley mkvtoolnix` |
| dnf | `sudo dnf install AtomicParsley aria2 mkvtoolnix` |
| pacman | `sudo pacman -S aria2 atomicparsley mkvtoolnix-cli` |
| zypper | `sudo zypper install AtomicParsley aria2 mkvtoolnix` |

<a id="s4"></a>

## 4. Cookie del browser

yt-dlp legge i cookie **in locale**, nel browser che scegli (tracce audio secondarie, sottotitoli, video privati, contenuti riservati agli iscritti). Per impostazione predefinita, il programma propone i cinque browser più usati su Linux (Firefox, Google Chrome, Chromium, Brave, Vivaldi). La voce **«Browser per i cookie…»** del menu delle opzioni apre la finestra «Browser per i cookie», che ne propone 11: spunta quelli che ti servono; un ✔ indica quelli la cui cartella del profilo esiste sul tuo computer.

| Browser | Letto da yt-dlp come | Portachiavi | Cartelle di profilo cercate |
|---|---|---|---|
| Firefox | `firefox` | no | `~/.config/mozilla/firefox`, `~/.mozilla/firefox`, Flatpak, Snap |
| Google Chrome | `chrome` | sì | `~/.config/google-chrome` |
| Chromium | `chromium` | sì | `~/.config/chromium` |
| Brave | `brave` | sì | `~/.config/BraveSoftware/Brave-Browser` |
| Vivaldi | `vivaldi` | sì | `~/.config/vivaldi` |
| Opera | `opera` | sì | `~/.config/opera` |
| Microsoft Edge | `edge` | sì | `~/.config/microsoft-edge` |
| LibreWolf, Waterfox, Floorp, Zen Browser | `firefox:` + cartella del profilo | no | `~/.librewolf`, `~/.config/librewolf`… (stesso schema per gli altri), Flatpak compreso |

I derivati di Firefox non hanno un nome noto a yt-dlp: il programma cerca il loro database `cookies.sqlite` (fino a tre livelli sotto le loro cartelle) e dà a yt-dlp la cartella del profilo usato più di recente. `XDG_CONFIG_HOME` è rispettata quando è assoluta.

L'**indicatore** accanto all'elenco mostra lo stato: rosso (disattivato o in errore), arancione (non provato o in corso), verde (cookie letti). Il pulsante ↻ avvia una prova; il suggerimento spiega l'errore. Una prova che legge **0 cookie** non è mai verde.

### Casi frequenti

| Cosa vedi | Causa probabile | Cosa fare |
|---|---|---|
| «Extracted 0 cookies» poi «Sign in to confirm you're not a bot» | il browser non conserva alcun cookie su disco (LibreWolf li elimina alla chiusura per impostazione predefinita; profilo mai connesso; modalità privata) | tenerlo aperto e con l'accesso a YouTube effettuato, oppure disattivare l'eliminazione dei cookie alla chiusura nelle sue impostazioni sulla privacy |
| «Item does not exist!» con Chrome, Chromium, Brave, Vivaldi, Opera o Edge | yt-dlp non ha trovato la chiave del browser nel portachiavi del desktop | avviare il browser una volta, accedere a YouTube, chiuderlo e ripetere la prova; altrimenti [sezione 5](#s5) |
| «Could not copy Chrome cookie database» o «database is locked» | il browser blocca il suo database mentre è in esecuzione | chiuderlo e ripetere la prova |
| «Failed to decrypt» | cookie cifrati con una chiave che yt-dlp non ha ottenuto | [sezione 5](#s5) |

### Provare un browser da un terminale

È il modo migliore per vedere l'errore esatto (sostituisci `IDENTIFIER` con l'identificatore di un qualsiasi video di YouTube):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Righe da cercare: `Extracted N cookies from chromium` (N deve essere maggiore di 0), `Chosen keyring: GNOMEKEYRING` (il portachiavi scelto) e `cookie version breakdown: {'v10': 0, 'v11': 50, …}` (i cookie `v11` richiedono il portachiavi, i `v10` no).

Per un derivato di Firefox, indica la cartella del profilo. Per trovarla:

```bash
find ~ -name cookies.sqlite -path "*librewolf*" 2>/dev/null
```

In un'installazione Flatpak, cerca in `~/.var/app`:

```bash
find ~/.var/app -name cookies.sqlite 2>/dev/null
```

Poi, con la cartella che contiene `cookies.sqlite`:

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser "firefox:/path/to/profile" -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

<a id="s5"></a>

## 5. Portachiavi: operazioni manuali

### A cosa serve

I browser della famiglia Chromium (Chrome, Chromium, Brave, Vivaldi, Opera, Edge) cifrano i loro cookie. La chiave di cifratura è custodita nel **portachiavi del desktop**: GNOME Keyring (o un equivalente compatibile, tramite il «Secret Service») in GNOME, XFCE, Cinnamon, MATE…, KWallet in KDE. Per decifrare, yt-dlp chiede quella chiave al portachiavi. Firefox e i suoi derivati non ne hanno bisogno.

Due fatti utili:

- **La chiave esiste solo dopo il primo avvio del browser.** Nella nostra macchina virtuale, l'errore «Item does not exist!» è scomparso dopo aver avviato ogni browser una volta e aver effettuato l'accesso a YouTube. La causa esatta del primo errore non è stata stabilita con certezza: il portachiavi esisteva, era quello predefinito ed era sbloccato.
- **Quale portachiavi usa yt-dlp** dipende dal desktop rilevato (variabili `XDG_CURRENT_DESKTOP` e `DESKTOP_SESSION`), secondo il codice di yt-dlp (ottobre 2026):

| Desktop rilevato | Portachiavi usato da yt-dlp |
|---|---|
| GNOME, Cinnamon, MATE, XFCE, Pantheon, Unity, Deepin, UKUI | GNOME Keyring (`GNOMEKEYRING`) |
| KDE 4, 5, 6 | KWallet (`KWALLET`, `KWALLET5`, `KWALLET6`) |
| LXQt, KDE 3, desktop non riconosciuto (solo gestori di finestre: sway, i3…) | nessuno: testo semplice (`BASICTEXT`) |

Nell'ultimo caso, yt-dlp legge solo i cookie `v10`: se il tuo browser custodisce la sua chiave in GNOME Keyring, i suoi cookie `v11` non verranno decifrati. Bisogna allora imporre il portachiavi da un terminale (sezione 5.6); il programma non offre ancora questa impostazione.

Gli elementi cercati nel portachiavi si chiamano «*nome* Safe Storage». Secondo il codice di yt-dlp, è **«Chrome Safe Storage»** per Chrome e Vivaldi, **«Chromium Safe Storage»** per Chromium, Opera ed Edge, **«Brave Safe Storage»** per Brave. Nella nostra macchina virtuale erano installati e avviati anche Chrome e Chromium: non sappiamo se Vivaldi, Opera o Edge funzionerebbero da soli.

### 5.1 Il portachiavi esiste?

```bash
ls -la ~/.local/share/keyrings/
```

Dovresti vedere un file `login.keyring` (il portachiavi «login»). Poi, quale portachiavi è quello **predefinito**?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets --method org.freedesktop.Secret.Service.ReadAlias default
```

Risposta `(objectpath '/org/freedesktop/secrets/collection/login',)`: c'è un portachiavi predefinito. Risposta `'/'`: **nessuno**, passa alla sezione 5.4.

### 5.2 È bloccato?

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Locked
```

`(<false>,)`: sbloccato. `(<true>,)`: bloccato; aprilo con Seahorse (sezione 5.4), che chiede la sua password.

### 5.3 La chiave del mio browser è al suo interno?

Elenca gli elementi:

```bash
gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Collection Items
```

La risposta fornisce percorsi che terminano con un numero (`…/login/1`, `…/login/2`…). Per leggere il nome di ciascuno (adatta l'elenco dei numeri):

```bash
for i in 1 2 3 4 5 6; do gdbus call --session --dest org.freedesktop.secrets --object-path /org/freedesktop/secrets/collection/login/$i --method org.freedesktop.DBus.Properties.Get org.freedesktop.Secret.Item Label; done
```

Dovresti vedere, per esempio, `Chromium Safe Storage`, `Chrome Safe Storage` o `Brave Safe Storage`. I nomi vuoti sono innocui. Se manca il nome del tuo browser: avvialo una volta, accedi a YouTube, chiudilo, poi rilancia questo comando.

### 5.4 Creare o sbloccare un portachiavi con Seahorse

Installa Seahorse («Password e chiavi») e gli strumenti associati. Il comando esatto è anche nella finestra «Browser per i cookie» del programma:

| Gestore di pacchetti | Comando |
|---|---|
| apt | `sudo apt install gnome-keyring seahorse libsecret-tools` |
| dnf | `sudo dnf install gnome-keyring seahorse libsecret` |
| pacman | `sudo pacman -S gnome-keyring seahorse libsecret` |
| zypper | `sudo zypper install gnome-keyring seahorse libsecret-tools` |

Poi aprilo:

```bash
seahorse
```

- **Nessun portachiavi predefinito**: creane uno (pulsante «+» o menu File › Nuovo › portachiavi di password), chiamalo «Login», poi clic destro su di esso › «Imposta come predefinito». Le etichette esatte variano con la versione di Seahorse.
- **Portachiavi bloccato**: doppio clic o clic destro › «Sblocca», poi digita la sua password (digitala tu: il programma non la chiede mai).
- **Accesso automatico**: un portachiavi protetto da password non può aprirsi da solo se non digiti alcuna password all'avvio della sessione; resta bloccato finché non lo sblocchi (o finché non usi la stessa password per la sessione e per il portachiavi).

Poi **avvia il browser, accedi a YouTube, chiudilo** e ripeti la prova (sezione 4).

### 5.5 KDE Plasma (KWallet)

In KDE, yt-dlp interroga KWallet (`kwallet-query`). Il gestore si chiama `kwalletmanager` (o `kwalletmanager5`) a seconda della distribuzione. Questa configurazione **non è stata provata** nei nostri test.

### 5.6 Imporre il portachiavi a yt-dlp (terminale)

Il programma lascia che yt-dlp scelga il portachiavi in base al desktop. Per forzarlo, aggiungi `+PORTACHIAVI` al nome del browser (valori: `gnomekeyring`, `kwallet`, `kwallet5`, `kwallet6`, `basictext`):

```bash
~/.local/share/yt-dlp-GUI/yt-dlp --cookies-from-browser chromium+gnomekeyring -v --simulate --no-playlist "https://www.youtube.com/watch?v=IDENTIFIER"
```

Per sapere quale portachiavi usa davvero un Chromium (comando tratto dal codice di yt-dlp, non provato qui):

```bash
chromium --enable-logging=stderr --v=1 2>&1 | grep key_storage_
```

### 5.7 Senza portachiavi: `--password-store=basic` (avanzato, non provato)

Chromium accetta `--password-store=basic`: custodisce allora la sua chiave in chiaro (una chiave fissa e nota) e cifra i suoi nuovi cookie come `v10`, che yt-dlp legge senza portachiavi (`chromium+basictext`). **È meno sicuro**: qualsiasi programma che possa leggere i tuoi file può decifrare questi cookie. Usalo solo se comprendi questo compromesso; i cookie già salvati probabilmente non vengono ricodificati: accedi di nuovo.

### 5.8 Ultima risorsa

Se un portachiavi è danneggiato, **fanne prima una copia di sicurezza**:

```bash
cp -a ~/.local/share/keyrings ~/keyrings-backup
```

Eliminare `login.keyring` cancella **tutte** le password che contiene (Wi-Fi, account online…): non farlo senza averne compreso le conseguenze.

<a id="s6"></a>

## 6. Dove si trovano i file

La cartella dei dati è `$XDG_DATA_HOME/yt-dlp-GUI` (per impostazione predefinita `~/.local/share/yt-dlp-GUI`), a meno che `portable.flag` non si trovi accanto all'eseguibile dell'archivio (o allo script `yt-dlp-gui.pyw`).

| File o cartella | Contenuto |
|---|---|
| `gui-config.json` | impostazioni (lingua, browser, cartelle, scelta dei browser…) |
| `download-queue.json` | coda dei download |
| `custom-blocks.json` | blocchi di opzioni personalizzati |
| `yt-dlp` | eseguibile scaricato dall'assistente |
| `bin/` | ffmpeg, ffprobe, deno |
| `cmd/` | file di configurazione temporanei di yt-dlp |
| `app/` | copia del programma fatta da «Installa nel menu» |

<a id="s7"></a>

## 7. Risoluzione dei problemi

| Problema | Indizio |
|---|---|
| L'AppImage non si avvia | avviarla da un terminale per leggere l'errore; installare FUSE 2 (sezione 2.2) o aggiungere `--appimage-extract-and-run` |
| Non si vede nulla, o errore di libreria | controllare la versione di glibc: `ldd --version` deve indicare 2.35 o superiore |
| Nessuna icona sul Desktop | GNOME non ne mostra per impostazione predefinita; usare il menu delle applicazioni |
| Collegamento sul Desktop con un avviso | clic destro › «Consenti avvio» |
| Il trascinamento tra host e macchina virtuale non funziona | è una funzione di VirtualBox (Guest Additions), non del programma |
| L'interfaccia ha una dimensione errata | il programma segue i caratteri di sistema (Tk); provare un'altra dimensione dei caratteri di sistema |
| L'aggiornamento di yt-dlp non riesce | usare «Aggiornamento & Diagnostica» nel menu delle opzioni; altrimenti scaricare `yt-dlp_linux` e sceglierlo nella finestra di sostituzione (il file scelto diventa eseguibile) |

<a id="s8"></a>

## 8. Segnalare un bug

Il pulsante «Segnala un bug» prepara un rapporto tecnico in cui le tue cartelle, il tuo nome utente e i tuoi indirizzi e-mail sono nascosti; non viene inviato nulla automaticamente. Per Linux, aggiungi:

```bash
cat /etc/os-release
```

```bash
echo "$XDG_CURRENT_DESKTOP $XDG_SESSION_TYPE"
```

e dì **come** hai installato il programma (AppImage, archivio, `.deb`, codice sorgente) e, per un problema di cookie, **il risultato della prova da terminale** (sezione 4), senza incollare i tuoi cookie.

<a id="s9"></a>

## 9. Per gli sviluppatori

Test (con uno schermo virtuale, senza bisogno di uno schermo reale):

```bash
xvfb-run -a python3 -X utf8 -m unittest discover -s tests -t .
```

Costruire i pacchetti (strumenti di compilazione: `pip install -r packaging/requirements-build.txt`, più `appimagetool`, il cui percorso è indicato dalla variabile `APPIMAGETOOL`):

```bash
python3 packaging/build_linux.py
```

```bash
python3 packaging/build_deb.py
```

I risultati sono in `dist/`. Per la migliore compatibilità, compila sulla distribuzione più vecchia supportata (la glibc della macchina di compilazione è il minimo richiesto alle macchine che eseguono il programma). Controlli utili del `.deb`:

```bash
lintian dist/yt-dlp-gui_*_amd64.deb
```

L'unico errore di forma noto è `dir-or-file-in-opt` (programma incluso in `/opt`).

**Pubblicare**: verificare `__version__` in `yt-dlp-gui.pyw`, datare la sezione della versione in `CHANGELOG-linux.md`, fare il commit, poi creare e inviare il tag `Linux-vX.Y.Z`. Il workflow «Release Linux» esegue i test, costruisce l'AppImage, l'archivio e il `.deb`, calcola le somme e crea la release come **anteprima (pre-release)**, mai come «ultima versione» (il controllo degli aggiornamenti della versione per Windows 0.1.7 non deve trovarvi alcun tag Linux).

Licenza: MIT, come il resto del repository (vedi [LICENSE](../LICENSE)).
