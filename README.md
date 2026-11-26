<p align="center">
  <img src="docs/social-preview.png" alt="ZimbraViewer" width="100%">
</p>

<p align="center">
  <b>Italiano</b> · <a href="README.en.md">English</a>
</p>

# ZimbraViewer

**Lettore locale di archivi di posta con verifica delle firme digitali.**
Apre l'export di Zimbra, Carbonio, Gmail, Outlook, Thunderbird, Apple/iCloud (o qualsiasi mbox, Maildir, `.eml`, `.ics`, `.vcf`), lo indicizza in un database locale e permette di **cercare, leggere, stampare in PDF ed esportare** mail e allegati, ma anche **calendario, attività, contatti, chat, note e file** — **senza server, senza client di posta e senza internet**: i file restano sul tuo computer.

Integra un verificatore di **firme digitali** (CAdES `.p7m`, PAdES, XAdES, FatturaPA) con catena di fiducia verso la **Trusted List AgID (eIDAS)**, e mostra le **PEC** come in una casella certificata.

![Schermata iniziale](docs/screenshot.png)

## Funzionalità

### Apertura della posta
- **Formato riconosciuto da solo**: trascina un file o una cartella sulla finestra, oppure usa *Apri…* (Ctrl+O / Ctrl+Maiusc+O) o la riga di comando.
- **Sorgenti supportate**
  | Sorgente | Formato |
  |---|---|
  | Zimbra, Carbonio | `.tgz` / `.tar.gz` / `.tar` (REST `fmt=tgz`) o cartella estratta |
  | Gmail (Google Takeout) | `.mbox` o `.zip` — cartelle ricostruite dalle etichette `X-Gmail-Labels` |
  | Outlook | `.pst` / `.ost` (libpff), singole `.msg` (olefile, anche RTF compresso) |
  | Thunderbird | file mbox e sottocartelle `.sbd` |
  | Apple Mail | caselle `.mbox`, file `.emlx` |
  | Generico | mbox, Maildir/Maildir++, `.eml`, `.zip` |
- Gli archivi vengono **convertiti una volta sola** in una cartella `Posta - <nome>` di `.eml`; le volte successive si apre direttamente.
- mbox letti **in streaming**, anche di molti GB. Importazioni in coda, con avanzamento e annullo.

### Calendario, attività, contatti, chat, note e file
Tutto ciò che l'export contiene oltre alla posta compare in **sezioni** a sinistra (Posta, Calendario, Attività, Contatti, Chat, Note, File, con il numero di elementi), ognuna con cartelle, ricerca, anteprima, stampa in PDF ed **esportazione in `.ics`, `.vcf` o `.csv`** (i file della Valigetta si aprono o si salvano).

| Da dove | Cosa viene letto |
|---|---|
| Zimbra / Carbonio (`.tgz`) | appuntamenti (`.appt`), attività (`.task`), contatti e gruppi (metadati `.meta`), chat (`.chat`), note, Valigetta (Briefcase) |
| Google Takeout | Calendar (`.ics`), Contatti (`.vcf`), Tasks (`Tasks.json`), Keep (`.json`), Google Chat (`messages.json`) |
| Microsoft Outlook | elementi di calendario, attività, contatti e note dentro `.pst`/`.ost` e `.msg`; contatti `.csv` |
| Apple / iCloud | Calendario e Promemoria (`.ics`), Contatti (`.vcf`) |
| Thunderbird | rubrica (`abook.sqlite`), calendario locale (`local.sqlite`), `.ics`/`.vcf` esportati |
| Qualsiasi programma | `.ics`, `.vcs` (eventi, attività, diario), `.vcf` (vCard 2.1/3.0/4.0, anche quoted-printable), CSV di contatti |

Eventi con fuso orario, giorni interi, ricorrenze (in chiaro: «ogni settimana · lun, mer»), partecipanti con risposta, priorità e stato delle attività. Gli indici creati dalle versioni precedenti vengono completati in automatico alla prima apertura.

### Ricerca e lettura
- Indice **SQLite** (`zimbra_index.db`) dentro la cartella, con **percorsi relativi**: la cartella si può spostare o copiare senza re-indicizzare.
- Ricerca su mittente, destinatario, oggetto, cartella, corpo e **nomi degli allegati**; più parole = AND, frasi esatte tra `<parentesi angolari>`.
- Selezionando una cartella si vedono anche le mail di **tutte le sottocartelle**.
- Anteprima Chromium sicura (link non navigabili, JavaScript spento) con immagini incorporate (`cid:`).
- **Storico della conversazione**: intestazioni dei messaggi citati/inoltrati trasformate in separatori leggibili (Outlook, Gmail, Zimbra, Thunderbird).
- **PEC**: fascia con il tipo di ricevuta e i dati di certificazione letti da `daticert.xml`; il messaggio originale in `postacert.eml` viene mostrato direttamente.

### Firme digitali (P7MReader integrato)
- **CAdES** (`.p7m`, anche annidati o in base64; `.p7s` detached), **PAdES** (PDF firmati, con rilevamento modifiche dopo la firma), **XAdES** (`.xml`, verifica crittografica), riepilogo **FatturaPA**.
- Controfirme e **marche temporali** RFC 3161 verificate; validazione alla data di firma per i certificati scaduti.
- Catena di fiducia verso la **Trusted List AgID** (aggiornata a ogni avvio, con copia offline) + archivio certificati di sistema (Windows, portachiavi macOS, CA della distribuzione Linux); revoca OCSP/CRL in soft-fail.
- Esiti chiari: **Verificato / Attenzione / Non valido**, con l'elenco dei controlli per ogni firma; report CSV/HTML.

### Esportazione
- **Esporta PDF + allegati** (massiva sulle mail spuntate o sulla singola mail): per ogni mail una cartella `AAAA.MM.GG HH.mm.ss <oggetto>` con PDF, allegati (`.p7m` originale **e** documento estratto), `Dettagli mail.txt` con intestazioni ed esiti delle verifiche, e `postacert.eml` scompattato.
- Nomi file validi su Windows, macOS e Linux, adattati al limite dei 260 caratteri di Windows (le esportazioni si copiano ovunque).

### Interfaccia
- Tema scuro, finestra **a istanza singola** (le nuove aperture vengono passate alla finestra già aperta), lavori lunghi in finestre **non modali** riducibili nella barra di stato.

### Accessibilità (WCAG 2.2 AA / EN 301 549)
- **Tastiera**: focus sempre visibile; frecce in sezioni, cartelle ed elenchi (l'anteprima segue); **Spazio** spunta, **Invio** apre; tasto Menu / Maiusc+F10 per le azioni; **F6** passa tra le zone della finestra; **F1** elenca tutte le scorciatoie.
- **Lettori di schermo** (NVDA, JAWS, Assistente vocale, VoiceOver, Orca): nomi e descrizioni per pulsanti con sola icona, campi, tabelle, barre di avanzamento e anteprima; conteggi dei risultati segnalati; pagine dell'anteprima in italiano dichiarato.
- **Vista**: contrasto del testo ≥ 4,5:1 e dei bordi dei controlli ≥ 3:1; **tema ad alto contrasto** (menu *Accessibilità* o automatico se attivo nel sistema); **zoom del testo** con Ctrl+ / Ctrl- / Ctrl+0, anche nell'anteprima.
- **Movimento**: le animazioni si fermano da sole dopo 5 secondi e si spengono con *Riduci le animazioni* (automatico se il sistema chiede meno movimento).

## Download e installazione

Le versioni pronte si scaricano dalla pagina **Releases** (oppure dagli *Artifacts* del workflow **Build** nella scheda Actions). Sono **standalone**: Python, Qt e Chromium sono inclusi, non serve installare altro.

| Sistema | File | Come si avvia |
|---|---|---|
| **Windows 10/11** (x64) | `ZimbraViewer-<ver>-windows-x64.exe` | doppio clic |
| **macOS 12+** Apple Silicon (M1…M4) | `ZimbraViewer-<ver>-macOS-arm64.dmg` | apri il `.dmg` e trascina l'app in *Applicazioni* |
| **macOS 12+** Intel | `ZimbraViewer-<ver>-macOS-x86_64.dmg` | come sopra |
| **Linux** x86_64 (Debian 12+, Ubuntu 22.04+, Fedora 36+, Arch, Manjaro, openSUSE…) | `ZimbraViewer-<ver>-x86_64.AppImage` | `chmod +x` e doppio clic |
| **Linux** x86_64, installazione nel menu | `ZimbraViewer-<ver>-linux-x86_64.tar.gz` | estrai ed esegui `./installa-linux.sh` |

**macOS** – l'app non è firmata con un certificato Apple Developer, quindi al primo avvio macOS la blocca: apri *Impostazioni di Sistema → Privacy e sicurezza* e premi **Apri comunque** (una volta sola). In alternativa, da Terminale:

```bash
xattr -dr com.apple.quarantine /Applications/ZimbraViewer.app
```

Su macOS i file si aprono anche con *Apri con → ZimbraViewer* o trascinandoli sull'icona nel Dock.

**Linux (AppImage)**

```bash
chmod +x ZimbraViewer-*-x86_64.AppImage
```

```bash
./ZimbraViewer-*-x86_64.AppImage
```

Se il sistema non ha FUSE l'AppImage si avvia comunque con `--appimage-extract-and-run`, oppure usa il `.tar.gz`. Il `.tar.gz` si installa per il solo utente (in `~/.local/opt/zimbraviewer`, con voce nel menu e comando `zimbraviewer`) e si rimuove con `./installa-linux.sh --rimuovi`.
Sulle distribuzioni che vietano i namespace utente ai programmi non installati (es. Ubuntu 23.10+ con AppArmor) la sandbox di Chromium dell'anteprima viene disattivata automaticamente; le anteprime restano comunque senza JavaScript e con link non navigabili.

## Requisiti (avvio da sorgente)

- **Windows 10/11**, **macOS 12+** o **Linux** con desktop grafico (X11 o Wayland)
- **Python 3.12+** (testato con 3.13 e 3.15)

| Pacchetto | Uso | Obbligatorio |
|---|---|---|
| `PyQt6`, `PyQt6-WebEngine` | interfaccia e anteprima | ✅ |
| `asn1crypto`, `pyhanko`, `pyhanko-certvalidator`, `cryptography`, `lxml` | verifica firme | facoltativo |
| `olefile` | Outlook `.msg` | facoltativo |
| `libpff-python` | Outlook `.pst` / `.ost` | facoltativo |

Senza una libreria facoltativa il resto funziona: le firme risultano *Non verificato* e i `.pst` danno un messaggio chiaro.

## Avvio da sorgente

```bash
pip install pyqt6 pyqt6-webengine asn1crypto pyhanko pyhanko-certvalidator cryptography lxml olefile certifi tzdata libpff-python
```

```bash
python "ZimbraViewer 3.2.py"
```

Riga di comando (file e cartelle in qualsiasi combinazione):

```bash
python "ZimbraViewer 3.2.py" "C:\Mail\export" backup.tgz takeout.zip outlook.pst mail.msg documento.p7m
```

## Compilare l'eseguibile

PyInstaller non fa cross-compilazione: ogni versione si compila sul proprio sistema. Il modo più semplice è il workflow **GitHub Actions** `.github/workflows/build.yml`, che compila tutte le versioni in parallelo: avvialo da *Actions → Build → Run workflow*, oppure crea un tag `v*` (es. `v3.2.0`) per ottenere anche una Release con tutti i pacchetti.

### macOS e Linux

```bash
./build_zimbra.sh
```

Crea un ambiente virtuale `.venv-build`, installa le dipendenze e usa `ZimbraViewer.spec`:
- **macOS** → `dist/ZimbraViewer.app` e `dist/ZimbraViewer-<ver>-macOS-<arch>.dmg` (per l'architettura del Mac su cui gira);
- **Linux** → `dist/ZimbraViewer-<ver>-x86_64.AppImage` e `dist/ZimbraViewer-<ver>-linux-x86_64.tar.gz`. Per un'AppImage compatibile con più distribuzioni compila sulla distribuzione con la glibc più vecchia da supportare (il workflow usa Ubuntu 22.04).

`libpff-python` (per i `.pst`) si compila dai sorgenti e richiede un compilatore C (`build-essential` / `gcc` / Xcode Command Line Tools); se manca, la build prosegue senza supporto `.pst`. Le icone `zimbra_icon.png` / `.icns` si rigenerano con `python packaging/genera_icone.py`.

### Windows

Lo script `build_zimbra.bat` installa le dipendenze e crea l'exe con PyInstaller, con icona e informazioni di versione (`version_info.txt`):

```bash
build_zimbra.bat
```

```bash
build_zimbra.bat onedir
```

Il primo crea un singolo `dist\ZimbraViewer.exe`; `onedir` crea una cartella (avvio più veloce). L'icona `zimbra_icon.ico` viene generata al primo avvio del `.py` se manca.

## Dove salva i dati

| Cosa | Dove |
|---|---|
| Indice della posta | `zimbra_index.db` dentro la cartella della posta |
| Trusted List AgID | Windows `%LOCALAPPDATA%\ZimbraViewer\TSL-IT.xml` · macOS `~/Library/Caches/ZimbraViewer/TSL-IT.xml` · Linux `~/.cache/ZimbraViewer/TSL-IT.xml` |
| Impostazioni firme | lette (senza modificarle) da `P7MReader/impostazioni.json` in `%APPDATA%` (Windows), `~/Library/Application Support` (macOS) o `~/.config` (Linux), se presente |
| Preferenze dell'interfaccia | QSettings: registro (Windows), `~/Library/Preferences` (macOS), `~/.config/ZimbraViewer` (Linux) |
| Allegati aperti al volo | cartella temporanea, ripulita all'uscita |

## Licenza

Distribuito con licenza **GNU GPL v3.0** — vedi [LICENSE](LICENSE).
