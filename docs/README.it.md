# yt-dlp GUI

[Français](../README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md) · [Polski](README.pl.md) · [Magyar](README.hu.md) · [Srpski](README.sr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [हिन्दी](README.hi.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Filipino](README.fil.md)

Interfaccia grafica per [yt-dlp](https://github.com/yt-dlp/yt-dlp), pensata per renderlo accessibile a tutti sfruttandone al massimo le potenzialità.

> **Progetto in sviluppo.** Alcune funzioni potrebbero cambiare, essere incomplete o contenere errori.

![yt-dlp GUI](img/main.en.png)

![yt-dlp GUI](img/inspector.en.png)

## Funzioni

### Downloader singolo e coda

- **Opzioni**: qualità massima (fino al 4K), solo audio (MP3), sottotitoli (formati vtt, srt, ass), incorporamento di sottotitoli e miniatura, lingua audio principale, tracce audio secondarie (file MKV multitraccia) e una libreria di «blocchi di script» (post-elaborazione, esportazione, rete, comportamento) che puoi ampliare con blocchi personalizzati.
- **Più tracce audio**: nel file MKV ogni traccia audio riporta l'etichetta della propria lingua («ita», «eng»…); il lettore la mostra nel menu audio.
- **Comando generato**: il comando yt-dlp corrispondente alle tue scelte viene mostrato in tempo reale.
- **Coda**: aggiungi l'URL corrente, poi avvia tutta la coda, da un elemento in poi, un solo video o un intervallo; pausa e ripresa, salto dell'elemento in corso, arresto con pulizia dei file parziali. La coda viene conservata tra una sessione e l'altra.
- **Nomi di file già esistenti**: un video singolo il cui nome esiste già nella cartella di destinazione riceve un suffisso (`_2`, `_3`…) per non sovrascrivere nulla. Una playlist scaricata da questo downloader non viene rinumerata: i video già presenti nella cartella vengono saltati («has already been downloaded»).

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

- Scegli il browser (Chrome, Firefox, Edge, Brave, Opera) di cui yt-dlp legge i cookie in locale: servono per le tracce audio secondarie e alcuni sottotitoli. **Si consiglia Firefox.**
- **Risultati dei nostri test** (Windows 11, ottobre 2026, account YouTube connesso in ogni browser): **Firefox** funziona, con il browser aperto o chiuso. **Opera** funziona **solo a browser chiuso**: blocca il database dei cookie finché è aperto e yt-dlp mostra allora «Could not copy Chrome cookie database». **Chrome, Edge e Brave** falliscono anche da chiusi: cifrano i cookie in un modo che yt-dlp non sempre riesce a leggere. Questi limiti dipendono dai browser e da yt-dlp, non dal programma, e possono cambiare con i loro aggiornamenti.
- Se il browser è impostato per **eliminare i cookie alla chiusura** (o navighi in modalità privata), sul disco non resta alcun cookie: yt-dlp non può recuperare nulla, né con Chrome, Edge, Brave né con Firefox. Con Chrome, Edge e Brave è una trappola: il browser va chiuso, e questo cancella i cookie. Disattiva l'opzione o conserva i cookie di youtube.com e google.com.
- Una **spia** indica lo stato: rossa se disattivato o in errore, arancione se non testato o in corso, verde se i cookie sono caricati. Il pulsante ↻ avvia un test e il suggerimento spiega lo stato o l'errore.

### Assistente di installazione, dipendenze e aggiornamenti di yt-dlp

- **Assistente di installazione**: al primo avvio propone di scaricare yt-dlp e ffmpeg dai loro repository ufficiali su GitHub. La somma SHA-256 viene verificata e non servono diritti di amministratore.
- **Dipendenze**: la finestra dedicata controlla ffmpeg, ffprobe, AtomicParsley, MKVToolNix, aria2 e deno e può installarli con Chocolatey. Solo ffmpeg e ffprobe sono indispensabili; deno è consigliato (tracce audio secondarie); AtomicParsley, MKVToolNix e aria2 sono facoltativi: il programma funziona anche senza.
- **Aggiornamento e diagnostica**: aggiorna yt-dlp (`yt-dlp -U`) o ne sostituisce l'eseguibile, mostra la versione e verifica le opzioni usate dall'interfaccia.
- **Aggiornamento del programma**: un controllo giornaliero (disattivabile) segnala una nuova versione con un banner discreto; la finestra dedicata mostra le novità e apre il download corrispondente alla tua installazione (installatore o versione portatile). Nulla viene installato automaticamente. Un interruttore nel menu delle opzioni («Verifica gli aggiornamenti all'avvio») attiva o disattiva il controllo automatico, e «Cerca un aggiornamento del programma…» lo avvia su richiesta.

### Interfaccia e lingue

- I controlli si riorganizzano in base alla larghezza della finestra; il contenuto scorre in verticale e la tabella dell'ispettore anche in orizzontale.
- Interfaccia in **15 lingue**: francese, inglese, spagnolo, portoghese, italiano, polacco, ungherese, serbo, russo, vietnamita, cinese, hindi, giapponese, coreano e filippino. Il cambio di lingua si applica al riavvio, con la possibilità di riavviare subito.

### Segnala un bug

- Il pulsante «Segnala un bug» prepara un rapporto tecnico: versioni del programma, di Python, di Windows e di yt-dlp, impostazioni innocue e ultime righe del registro. Le tue cartelle, il nome utente e gli indirizzi e-mail vengono oscurati. Per inviare il rapporto su GitHub serve un account GitHub gratuito.
- Nulla viene inviato automaticamente: rivedi e modifichi il rapporto, poi apri una pagina di segnalazione GitHub già compilata (o copi il rapporto).

## Installazione

- **Installatore (consigliato)**: scarica `yt-dlp-gui-setup-X.Y.Z.exe` dalla [pagina delle versioni](https://github.com/harlockSuites/YT-dlp-GUI/releases) e avvialo. Windows 10 o 11 (64 bit), senza diritti di amministratore; Python non è necessario.
- **Versione portatile**: scarica `yt-dlp-gui-portable-X.Y.Z.zip`, estrailo dove vuoi e avvia `yt-dlp-gui.exe`; le impostazioni restano in quella cartella.
- **Dal codice sorgente**: vedi le sezioni «Requisiti» e «Avvio rapido» qui sotto.
- **Disinstallazione**: Impostazioni di Windows › App › App installate › yt-dlp GUI, oppure il collegamento «Disinstalla» nel menu Start. Il programma propone di eliminare anche i suoi dati (impostazioni, coda, yt-dlp e ffmpeg scaricati); i tuoi video non vengono mai eliminati. Poiché l'installazione è propria di ogni account Windows, il programma compare solo nell'elenco dell'account che lo ha installato. Per la versione portatile basta eliminare la sua cartella. Gli strumenti installati a parte con Chocolatey (ffmpeg, Deno…) non vengono rimossi.
- **Analisi antivirus (VirusTotal)**: la versione 0.1.7 è stata analizzata il 21 ottobre 2026. L'[installatore](https://www.virustotal.com/gui/file/7177f2dc75c3b5309b2d6b96a2104d578dbaf67a0c8ed28af286aa37159df91c) è segnalato da 4 motori su 69 (Arctic Wolf, Microsoft, SecureAge, Skyhigh) con rilevamenti euristici generici; l'[avviatore della versione portatile](https://www.virustotal.com/gui/file/6889bde864b341a948dc23c01e29eba3c63315145705eb0d5bb24a4964b0735a) lo è da 5 su 70 (Arctic Wolf, CrowdStrike Falcon, Microsoft, SecureAge, Zillya) e l'[archivio ZIP portatile](https://www.virustotal.com/gui/file/7fd0a4bb101ca4b4c513ff42e0782cc2371304c643bf03cb3ccd8e9abdb43706) da 1 su 66 (Zillya, sull'archivio stesso). Probabilmente sono falsi positivi dovuti a un programma compresso e non firmato. Questi risultati valgono solo per questa versione. In caso di dubbio, verifica la somma SHA-256.
- **Code signing policy**: i file non sono firmati digitalmente. Una richiesta di firma gratuita alla SignPath Foundation è stata rifiutata il 19 ottobre 2026 (il progetto ha ancora poca visibilità pubblica) e potrà essere ripresentata; la [politica di firma del codice](https://github.com/harlockSuites/YT-dlp-GUI/blob/main/docs/CODE_SIGNING_POLICY.md) descrive il processo previsto se si ottiene un certificato.
- **Avviso di Windows SmartScreen**: l'installatore non è firmato digitalmente, quindi Windows può mostrare «Windows ha protetto il PC». Fai clic su «Ulteriori informazioni», poi su «Esegui comunque». Per verificare l'autenticità del file, confronta la sua somma SHA-256 con quella di `SHA256SUMS.txt`, pubblicata con ogni versione:

```powershell
Get-FileHash .\yt-dlp-gui-setup-X.Y.Z.exe -Algorithm SHA256
```

## Avvisi di Windows e dei browser

Questo programma è gratuito, pubblicato da una sola persona, e i suoi file **non sono ancora firmati digitalmente**. Un file nuovo, scaricato da quasi nessuno, non ha «reputazione»: i browser e Windows mostrano quindi avvisi **anche per un programma sicuro**. Un avviso non dimostra che un file sia pericoloso, e la sua assenza non dimostra che sia sicuro: ecco come verificare da soli.

- **Browser** (Firefox, Chrome, Edge, Brave): il download può essere segnalato come «poco comune» o come «contenente un virus o un malware». È un'analisi automatica della reputazione del file. Controlla prima la somma di controllo (sotto); se corrisponde, puoi scegliere l'opzione che consente o mantiene il download.
- **Windows SmartScreen**: «Windows ha protetto il PC» → fai clic su «Ulteriori informazioni» e poi su «Esegui comunque», **dopo** aver controllato la somma di controllo.
- **Microsoft Defender (Sicurezza di Windows)**: può mettere in quarantena o eliminare il file, indicando «Trojan:Win32/Wacatac.C!ml». Il suffisso `!ml` indica un rilevamento automatico tramite apprendimento automatico, frequente su un file nuovo e non firmato; questi rilevamenti sono stati segnalati a Microsoft come falsi positivi. Dopo aver controllato la somma SHA-256 (sotto), puoi ripristinare il file: Sicurezza di Windows › Protezione da virus e minacce › Cronologia protezione › apri l'elemento › Azioni › «Consenti nel dispositivo» (o «Ripristina»). Non disattivare la protezione di Windows e non aggiungere un'esclusione più ampia di questo solo file.
- **Antivirus**: alcuni motori mostrano rilevamenti generici (vedi l'analisi antivirus sopra). Per vedere l'analisi del tuo file, incolla la sua somma SHA-256 nella barra di ricerca di [VirusTotal](https://www.virustotal.com/): se il file è già noto, ottieni il rapporto senza caricarlo.
- **Verifica il tuo download**: scarica anche `SHA256SUMS.txt` dalla stessa pagina della versione, apri PowerShell nella cartella dei file ed esegui il comando qui sotto: confronta ogni file con la somma pubblicata e mostra `OK` o `DIFFERENT`. Se un file è `DIFFERENT`, non eseguirlo.

```powershell
Get-Content .\SHA256SUMS.txt | ForEach-Object { $h, $n = $_ -split '\s+\*?', 2; if ((Get-FileHash $n -Algorithm SHA256).Hash -eq $h.ToUpper()) { "$n : OK" } else { "$n : DIFFERENT" } }
```

- Questa verifica dimostra che il tuo file è **identico** a quello pubblicato su GitHub; da sola non dimostra che sia innocuo. Il codice sorgente e la compilazione automatica dei file ([GitHub Actions](https://github.com/harlockSuites/YT-dlp-GUI/actions)) sono pubblici, e non esiste ancora una firma digitale: una richiesta alla SignPath Foundation è stata rifiutata il 19 ottobre 2026 (vedi la «Code signing policy»).

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

- Questo software non invia alcun dato all'autore e non contiene telemetria. Le connessioni di rete passano da yt-dlp (siti video), dall'assistente di installazione (GitHub) e dallo strumento del registro (ricerca su YouTube). Un controllo automatico degli aggiornamenti contatta inoltre GitHub all'avvio (al massimo una volta al giorno); puoi disattivarlo da «Verifica gli aggiornamenti all'avvio».
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

Il codice è pubblicato con licenza [MIT](../LICENSE). L'icona, il logo e il banner «Harlock S.» (file `yt-dlp-gui.ico` e cartella `assets/`) sono creazioni originali generate dall'IA su richiesta dell'autore. Costituiscono l'identità visiva del progetto e non sono coperti dalla licenza MIT: non riutilizzarli per un altro progetto né in modo da generare confusione.
