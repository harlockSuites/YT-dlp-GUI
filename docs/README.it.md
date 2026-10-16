# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Interfaccia grafica per [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensata per renderlo accessibile a tutti sfruttandone al massimo le potenzialità.

> **Progetto in sviluppo.** Alcune funzioni potrebbero cambiare, essere incomplete o contenere errori.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funzioni

### Downloader singolo e coda

- **Opzioni**: qualità massima (fino al 4K), solo audio (MP3), sottotitoli (formati vtt, srt, ass), incorporamento di sottotitoli e miniatura, lingua audio principale, tracce audio secondarie (file MKV multitraccia) e una libreria di «blocchi di script» (post-elaborazione, esportazione, rete, comportamento) che puoi ampliare con blocchi personalizzati.
- **Comando generato**: il comando yt-dlp corrispondente alle tue scelte viene mostrato in tempo reale.
- **Coda**: aggiungi l'URL corrente, poi avvia tutta la coda, da un elemento in poi, un solo video o un intervallo; pausa e ripresa, salto dell'elemento in corso, arresto con pulizia dei file parziali. La coda viene conservata tra una sessione e l'altra.

### Ispettore di playlist

- **Analisi** di una playlist: ogni video è elencato con le tracce audio e i sottotitoli disponibili; gli elementi nascosti, privati o eliminati vengono ignorati senza bloccare il resto.
- **Regole globali** (qualità, solo audio, formato e incorporamento dei sottotitoli, miniatura, numerazione, lingue, blocchi di script, cartella di destinazione) con **eccezioni per video** per la lingua principale, le tracce secondarie e i sottotitoli.
- **Codice colore**: rosso quando manca la lingua principale, arancione quando manca una traccia secondaria o un sottotitolo.
- **Download della selezione** con registro, pausa, ripresa e salto; se le tracce richieste non esistono, il video viene ritentato senza di esse, poi un **riepilogo** indica cosa è riuscito, è stato adattato o è fallito.

### Cartella intelligente e registro

- **Cartella intelligente**: yt-dlp salta i video già scaricati grazie a un registro memorizzato nella cartella di destinazione. Il file `.yt-dlp-registre.json` contiene identificatore, URL, titolo, durata, nome del file e data di ogni video; `.yt-dlp-archive.txt`, letto da yt-dlp, ne deriva.
- **Controllo retroattivo**: se video della selezione sono già presenti nella cartella ma non nel registro, una finestra propone di registrarli e saltarli (confrontando i titoli). Puoi deselezionare i falsi positivi.
- **Aggiorna il registro**: conta i video della cartella, quelli del registro e quelli mancanti, poi cerca su YouTube le informazioni mancanti (titolo e durata tramite ffprobe). Nulla viene registrato senza la tua conferma, e due pulsanti aprono il file locale o il link YouTube trovato per verificare.

![yt-dlp GUI](img/registry.en.png)

### Cookie del browser

- Scegli il browser (Chrome, Firefox, Edge, Brave, Opera) di cui yt-dlp legge i cookie in locale: servono per le tracce audio secondarie e alcuni sottotitoli.
- Una **spia** indica lo stato: rossa se disattivato o in errore, arancione se non testato o in corso, verde se i cookie sono caricati. Il pulsante ↻ avvia un test e il suggerimento spiega lo stato o l'errore.

### Assistente di installazione, dipendenze e aggiornamenti di yt-dlp

- **Assistente di installazione**: al primo avvio propone di scaricare yt-dlp e ffmpeg dai loro repository ufficiali su GitHub. La somma SHA-256 viene verificata e non servono diritti di amministratore.
- **Dipendenze**: la finestra dedicata controlla ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 e deno e può installarli con Chocolatey.
- **Aggiornamento e diagnostica**: aggiorna yt-dlp (`yt-dlp -U`) o ne sostituisce l'eseguibile, mostra la versione e verifica le opzioni usate dall'interfaccia.
- **Aggiornamento del programma**: un controllo giornaliero (disattivabile) segnala una nuova versione con un banner discreto; la finestra dedicata mostra le novità e apre il download corrispondente alla tua installazione (installatore o versione portatile). Nulla viene installato automaticamente.

### Interfaccia e lingue

- I controlli si riorganizzano in base alla larghezza della finestra; il contenuto scorre in verticale e la tabella dell'ispettore anche in orizzontale.
- Interfaccia in **15 lingue**: francese, inglese, spagnolo, portoghese, italiano, polacco, ungherese, serbo, russo, vietnamita, cinese, hindi, giapponese, coreano e filippino. Il cambio di lingua si applica al riavvio, con la possibilità di riavviare subito.

### Segnala un bug

- Il pulsante «Segnala un bug» prepara un rapporto tecnico: versioni del programma, di Python, di Windows e di yt-dlp, impostazioni innocue e ultime righe del registro. Le tue cartelle, il nome utente e gli indirizzi e-mail vengono oscurati.
## Installazione

- **Installatore (consigliato)**: scarica `yt-dlp-gui-setup-X.Y.Z.exe` dalla [pagina delle versioni](https://github.com/harlockSuites/YT-dlp-GUI/releases) e avvialo. Windows 10 o 11 (64 bit), senza diritti di amministratore; Python non è necessario.
- **Versione portatile**: scarica `yt-dlp-gui-portable-X.Y.Z.zip`, estrailo dove vuoi e avvia `yt-dlp-gui.exe`; le impostazioni restano in quella cartella.
- **Dal codice sorgente**: vedi le sezioni «Requisiti» e «Avvio rapido» qui sotto.
- **Avviso di Windows SmartScreen**: l'installatore non è firmato digitalmente, quindi Windows può mostrare «Windows ha protetto il PC». Fai clic su «Ulteriori informazioni», poi su «Esegui comunque». Per verificare l'autenticità del file, confronta la sua somma SHA-256 con quella di `SHA256SUMS.txt`, pubblicata con ogni versione:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

- Nulla viene inviato automaticamente: rivedi e modifichi il rapporto, poi apri una pagina di segnalazione GitHub già compilata (o copi il rapporto).

## Requisiti

- Windows
- [Python 3](https://www.python.org/) con Tkinter (incluso nell'installazione standard)
- `yt-dlp.exe` e, preferibilmente, [ffmpeg](https://ffmpeg.org/): l'assistente di installazione li scarica al primo avvio

## Avvio rapido

1. Scarica o clona questo repository e vai nella sua cartella.
2. Avvia `yt-dlp-gui.bat` (oppure `pythonw yt-dlp-gui.pyw`).
3. Al primo avvio lascia che l'assistente installi yt-dlp e ffmpeg; resta disponibile nel menu delle opzioni.
4. Incolla un URL, scegli le opzioni, poi scarica, aggiungi alla coda o apri l'ispettore per una playlist.

## Privacy e uso responsabile

- Questo software non invia alcun dato all'autore e non contiene telemetria. Le connessioni di rete passano da yt-dlp (siti video), dall'assistente di installazione (GitHub) e dallo strumento del registro (ricerca su YouTube). Un controllo automatico degli aggiornamenti contatta inoltre GitHub all'avvio (al massimo una volta al giorno); puoi disattivarlo da «Cerca un aggiornamento del programma…».
- I tuoi cookie restano sul tuo computer: yt-dlp li legge in locale dal browser scelto.
- Usa questo strumento nel rispetto del diritto d'autore, delle condizioni d'uso dei siti e delle leggi del tuo paese, e scarica solo ciò che hai il diritto di scaricare.

## Sviluppo

I test (traduzioni, registro, costruzione dei comandi, interfaccia, assistente di installazione, documentazione) si avviano con:

```bash
python -X utf8 -m unittest discover -s tests -t .
```

Vengono eseguiti automaticamente anche su GitHub a ogni invio. Il numero di versione è definito da `__version__` in `yt-dlp-gui.pyw` e deve corrispondere all'intestazione di [CHANGELOG.md](../CHANGELOG.md). I file di traduzione dell'interfaccia sono in `lang/` e quelli di questa documentazione in `docs/`; le revisioni di madrelingua sono benvenute.

## Sostieni il progetto

L'uso di questa interfaccia è, è sempre stato e rimarrà gratuito e libero per chiunque. Se lo strumento ti è particolarmente utile, puoi sostenere il progetto su [Ko-fi](https://ko-fi.com/harlocksuites).

## Ringraziamenti

Grazie alla comunità che aggiorna regolarmente [yt-dlp](https://github.com/yt-dlp/yt-dlp), senza il quale nulla di tutto ciò sarebbe possibile.

## Licenza

Il codice è pubblicato con licenza [MIT](../LICENSE). Il logo e il banner «Harlock S.» (cartella `assets/`) sono il marchio personale dell'autore e non sono coperti da questa licenza: tutti i diritti riservati.
