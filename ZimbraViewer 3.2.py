r"""
ZimbraViewer 3.2 - Lettore locale di archivi di posta + verifica firme digitali (PyQt6)
=====================================================================================

CHANGELOG
---------
3.2.1 (2026-11-26)
  Aggiunto: oltre alla posta, calendario, attività, contatti, chat, note e file dell'export, in sezioni dedicate
            della scheda (elenco, ricerca, anteprima, esportazione in .ics / .vcf / .csv, stampa in PDF):
            Zimbra e Carbonio (.tgz REST: .meta, .appt, .task, .chat, Valigetta), Google Takeout (Calendar, Contatti,
            Tasks, Keep, Google Chat), Outlook (.pst/.ost e .msg di calendario, attività, contatti e note; CSV dei
            contatti), Apple/iCloud (.ics, .vcf), Thunderbird (abook.sqlite, local.sqlite) e file .ics/.vcf/.csv singoli.
            Gli indici delle versioni precedenti vengono completati da soli.
  Accessibilità (WCAG 2.2 AA / EN 301 549): focus da tastiera sempre visibile, contrasti >= 4,5:1 per i testi e
            >= 3:1 per i bordi dei controlli, tema ad alto contrasto (anche automatico dalle impostazioni del sistema),
            zoom del testo (Ctrl+ / Ctrl- / Ctrl+0) anche nell'anteprima, animazioni che si fermano dopo 5 secondi o
            spente («Riduci le animazioni», anche dal sistema), nomi accessibili per pulsanti, campi, tabelle e
            anteprima, albero delle cartelle navigabile con le frecce, Spazio/Invio nelle tabelle, menu contestuali
            da tastiera, F6 tra le zone della finestra, F1 con le scorciatoie, lingua italiana dichiarata nelle pagine.
3.2 multipiattaforma (2026-11-16)
  Aggiunto: versioni standalone per macOS (.app/.dmg, Apple Silicon e Intel) e Linux (AppImage e .tar.gz per Debian,
            Ubuntu, Fedora, Arch...). Apertura dal Finder ("Apri con", Dock), "Mostra nella cartella" con Finder e file
            manager Linux, cache e impostazioni nelle cartelle standard di ciascun sistema, certificati di sistema
            (portachiavi macOS, raccolta CA della distribuzione) al posto dell'archivio di Windows, HTTPS verificato
            anche nell'app per macOS, sandbox di Chromium disattivata solo dove la distribuzione la impedisce.
3.2 (2026-11-09)
  Modificato: selezionando una cartella nell'albero si vedono anche le mail di tutte le sue sottocartelle, a qualunque
              profondità: le mail nidificate non sfuggono più. La colonna "Cartella" indica dove si trova ciascuna mail
              (percorso completo nel suggerimento al passaggio del mouse).

COSA FA
-------
Apre l'archivio della posta esportato da Zimbra, Gmail (Google Takeout), Outlook, Thunderbird, Apple Mail e da
qualsiasi programma che salvi in mbox, Maildir o .eml; lo indicizza in un database locale e permette di cercare,
leggere, stampare in PDF ed esportare le mail con i loro allegati, senza server e senza client di posta.
Integra il P7MReader: verifica ed estrazione di documenti firmati (.p7m, PDF, XML, fatture elettroniche).

REQUISITI E COMPILAZIONE
------------------------
Obbligatori: PyQt6, PyQt6-WebEngine.
Firme digitali (le stesse del P7MReader): asn1crypto, pyhanko-certvalidator, pyhanko (PDF firmati), cryptography, lxml (XML firmati).
Outlook: olefile (.msg), libpff-python (.pst/.ost).
Senza una libreria opzionale il resto funziona: le firme risultano "Non verificato", i .pst danno un messaggio chiaro.
    pip install pyqt6 pyqt6-webengine asn1crypto pyhanko pyhanko-certvalidator cryptography lxml olefile libpff-python pyinstaller
    pyinstaller --noconsole --onefile --icon=zimbra_icon.ico "ZimbraViewer 3.2.py"
macOS e Linux: ./build_zimbra.sh (usa ZimbraViewer.spec; .app + .dmg su macOS, AppImage + .tar.gz su Linux).

COME SI APRE LA POSTA
---------------------
- Scheda "Inizio" (sempre presente): zona di rilascio animata e, per ogni programma (Zimbra, Gmail, Outlook,
  Thunderbird, Apple Mail, altri), i passi per ottenere l'export e il pulsante per aprirlo.
- Pulsante "Apri…" (Ctrl+O file, Ctrl+Maiusc+O cartella), trascinamento sulla finestra (un velo animato indica dove
  rilasciare), riga di comando (ZimbraViewer.exe "C:\Mail\export" backup.tgz mail.msg documento.p7m).
- Il formato si riconosce da solo (rileva_sorgente):
    cartella con .eml o con zimbra_index.db  -> si apre subito
    .eml                                     -> scheda della singola mail
    .msg (Outlook), .emlx (Apple)            -> convertita al volo in .eml e aperta
    .p7m, .p7s, .pdf, .xml                   -> scheda "Verifica firme"
    .tgz/.tar.gz/.tar/.zip, .mbox, .pst/.ost, cartelle di Thunderbird/Apple/Maildir/.msg
                                             -> IMPORTAZIONE: si sceglie dove creare la cartella "Posta - <nome>",
                                                le mail vengono convertite in .eml (una sottocartella per casella)
                                                e poi indicizzate. Le volte successive si apre direttamente la cartella.
- Conversioni (ConvertitorePosta, in un thread con avanzamento e annullo):
    mbox (Gmail, Thunderbird, Apple, generico) in streaming, anche file di molti GB; per Google Takeout la cartella
      è data dalle etichette X-Gmail-Labels (Posta inviata, Bozze, Spam, Cestino, etichette personali, Posta in arrivo,
      Archivio); le righe ">From " vengono ripristinate.
    Thunderbird: file mbox e sottocartelle .sbd; Apple Mail: caselle .mbox esportate e file .emlx; Maildir/Maildir++.
    Outlook .msg letto dalla struttura OLE (olefile): intestazioni originali di trasporto, destinatari, corpo testo/HTML
      (o RTF compresso LZFu convertito in testo), allegati, immagini incorporate e mail allegate.
    Outlook .pst/.ost con libpff: cartelle, mail, destinatari, corpi, allegati e mail allegate.
    Archivi .zip/.tgz/.tar: estratti con nomi sicuri; se contengono formati da convertire, le copie estratte vengono
      convertite e poi eliminate.
- Archivi e conversioni vanno uno alla volta (coda), le schede restano utilizzabili.

SINGOLA ISTANZA
---------------
Una sola finestra per utente (Windows, macOS, Linux): il primo avvio apre un QLocalServer; le esecuzioni successive gli passano i
percorsi ricevuti da riga di comando (JSON via QLocalSocket) e terminano. La finestra si porta in primo piano.

INDICIZZAZIONE E PERCORSI RELATIVI
----------------------------------
- Alla prima apertura di una cartella l'indice si crea da solo (thread IndexerWorker, finestra riducibile).
  Database SQLite "zimbra_index.db" DENTRO la cartella: tabelle emails (cartella, mittente, destinatario, oggetto,
  data, percorso, corpo testuale) e allegati.
- Percorsi salvati RELATIVI alla cartella: si può spostare o copiare senza ri-indicizzare. Gli indici delle versioni
  precedenti (percorsi assoluti) vengono convertiti alla prima apertura, anche se la cartella è già stata spostata.
- Cartelle di sistema tradotte (Inbox -> Posta in arrivo, Sent/Sent Items -> Posta inviata, Trash/Deleted Items ->
  Cestino, Drafts -> Bozze, Junk -> Spam...). "Ricostruisci l'indice" è nel menu "Altro".

RICERCA E LETTURA
-----------------
- Una cartella selezionata mostra le sue mail e quelle di tutte le sottocartelle (la colonna "Cartella" dice dove sono).
- La ricerca parte solo con Invio. Più parole = tutte presenti (AND) in mittente, destinatario, oggetto, cartella,
  corpo o nome di un allegato; frasi esatte tra <parentesi angolari>; campo vuoto = ultime 500 mail.
- Anteprima Chromium (link non navigabili) su foglio sempre chiaro (il tema scuro non tocca l'area di lettura),
  intestazione completa (Da, Data, A, Cc, Ccn, Rispondi a, Oggetto) e immagini incorporate (cid:) visibili.
- Storico della conversazione: nel corpo le intestazioni dei messaggi precedenti e inoltrati (Outlook, Gmail, Zimbra,
  Thunderbird, testo semplice "-----Messaggio originale-----") e le righe "Il giorno ... ha scritto:" diventano
  riquadri-intestazione che fanno da separatore; le righe citate con ">" hanno una barra laterale.
- PEC come in una casella certificata: fascia con tipo (posta certificata, accettazione, consegna, mancata consegna...)
  e dati di certificazione letti da daticert.xml (gestore, data, mittente, destinatari, identificativo); nelle buste
  di trasporto si legge direttamente il messaggio originale contenuto in postacert.eml.
- Pannello allegati: apri al volo (file temporanei ripuliti all'uscita, conferma per gli eseguibili, anche dentro
  un .p7m), salva, verifica firma (icona a scudo per .p7m/.pdf/.xml). Doppio clic su una mail = scheda dedicata.
- Righe di aiuto chiudibili ("Come si usa") che non ricompaiono una volta chiuse (QSettings).

ALLEGATI, POSTACERT.EML E P7M
-----------------------------
- Allegato = parte con nome file, "attachment" o senza Content-ID (le immagini nel corpo non contano); gli .eml
  allegati restano un unico allegato .eml.
- postacert.eml, daticert.xml e smime.p7s (busta e file tecnici PEC/S-MIME): nascosti nella vista, nel conteggio
  della graffetta e nella ricerca (si vedono solo i veri allegati); nell'esportazione restano, come prova della PEC,
  e postacert.eml viene scompattato.
- I .p7m vengono SEMPRE conservati e accanto si salva il documento estratto (motore del P7MReader, anche buste
  annidate/base64), in ogni salvataggio ed esportazione; in apertura si apre direttamente il documento.

FIRME DIGITALI: IL P7MREADER INTEGRATO
--------------------------------------
- Motore ripreso da P7MReader 3.0, con le stesse regole e gli stessi esiti (Verificato / Attenzione / Non valido):
  CAdES (.p7m anche annidati, .p7s sul file accanto), PAdES (.pdf con pyhanko: integrità e modifiche dopo la firma),
  XAdES (.xml, con verifica crittografica), riepilogo FatturaPA, controfirme verificate, marca temporale verificata
  (se valida la firma si valuta a quella data), elenco dei controlli per ogni firma, nomi puliti («.pdf (1) (1).p7m» -> «.pdf»), catena di fiducia con
  pyhanko-certvalidator verso la Trusted List AgID (eIDAS) + archivio certificati di sistema + CA aggiunte nel
  P7MReader (completata via AIA), revoca OCSP/CRL in soft-fail, validazione alla data di firma per i certificati scaduti.
- Trusted List AgID (https://eidas.agid.gov.it/TL/TSL-IT.xml): riscaricata a ogni avvio se c'è rete e salvata in
  %LOCALAPPDATA%\ZimbraViewer\TSL-IT.xml (macOS ~/Library/Caches/ZimbraViewer, Linux ~/.cache/ZimbraViewer); offline si usa quella copia, altrimenti il TSL-IT.xml accanto al programma
  (o incluso nell'exe con --add-data "TSL-IT.xml;."). Certificatori ritirati prima della firma -> "Attenzione".
- Impostazioni lette (senza modificarle) da %APPDATA%\P7MReader\impostazioni.json; se il P7MReader non c'è, i suoi default.
- Scheda "Verifica firme": file o cartelle intere (anche trascinati), filtri per esito e ricerca, dettaglio di ogni
  firma, apertura del documento, estrazione (accanto all'originale come nel P7MReader, o nella cartella scelta),
  certificati, copia del report, report CSV/HTML. Gli allegati delle mail arrivano qui con l'icona a scudo.
- Le verifiche girano in thread separati (parallelismo = impostazione "concorrenza" del P7MReader, 120 s al massimo
  ciascuna): l'interfaccia e le esportazioni non si bloccano mai.

ESPORTAZIONE PDF + ALLEGATI (MASSIVA O DELLA SINGOLA MAIL)
----------------------------------------------------------
Mail spuntate + "Esporta PDF + allegati", oppure "Esporta mail completa" sulla mail aperta. Per ogni mail una
cartella "AAAA.MM.GG HH.mm.ss <oggetto>" (se esiste: "(2)", "(3)"...) con: PDF della mail; allegati (p7m originale +
documento estratto); "Dettagli mail.txt" (intestazioni, allegati, esito delle verifiche di .p7m e di PDF/XML firmati,
completato appena pronto); per ogni postacert.eml il file e la sottocartella "postacert" con il vero messaggio
scompattato (fino a 3 livelli). Nomi validi per Windows e adattati al limite dei 260 caratteri.
PDF generati da Chromium uno alla volta a passi asincroni (15 s per i contenuti remoti, 60 s per PDF, JavaScript
spento, mail enormi via file temporaneo). Riepilogo finale con firme verificate/con avvisi/non valide e problemi.

AVANZAMENTO
-----------
Importazioni, indicizzazione, salvataggio allegati ed esportazioni mostrano una finestra NON modale: "Riduci e
continua a lavorare" (o X / Esc) la trasforma in un indicatore con la percentuale nella barra in basso, da cui si
riapre o si annulla. Barre con testo bianco su indaco scuro: leggibili sia sulla parte piena sia su quella vuota.
Chiudendo una scheda o il programma durante un lavoro viene chiesta conferma.
"""
from __future__ import annotations

import sys
import os
import re
import io
import csv
import json
import html
import math
import time
import base64
import ssl
import struct
import shutil
import sqlite3
import atexit
import asyncio
import hashlib
import logging
import tarfile
import zipfile
import tempfile
import mimetypes
import threading
import subprocess
import urllib.request
import email
import email.header
import email.parser
import email.utils
import xml.etree.ElementTree as ET
from concurrent.futures import Future
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from email import policy
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QSplitter, QFileDialog, QHeaderView, QLabel,
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QCheckBox, QScrollArea, QMenu, QTabWidget,
                             QTabBar, QDialog, QProgressBar, QFrame, QSizePolicy, QComboBox, QStackedWidget,
                             QTextBrowser, QGraphicsOpacityEffect, QListWidget, QListWidgetItem)
from PyQt6.QtCore import (Qt, QThread, QObject, pyqtSignal, QTimer, QUrl, QSize, QRectF, QPointF, QSettings,
                          QPropertyAnimation, QEasingCurve, QEvent, QModelIndex)
from PyQt6.QtGui import (QIcon, QPixmap, QDesktopServices, QShortcut, QKeySequence, QColor, QPainter, QPen,
                         QLinearGradient)
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

# ==========================================
# PIATTAFORMA: WINDOWS, MACOS, LINUX
# ==========================================
IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")
FROZEN = bool(getattr(sys, 'frozen', False))

def cartella_cache_app() -> str:
    """Cache per utente: %LOCALAPPDATA%\\ZimbraViewer, ~/Library/Caches/ZimbraViewer, $XDG_CACHE_HOME/ZimbraViewer."""
    if IS_WIN:
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    elif IS_MAC:
        base = os.path.join(os.path.expanduser("~"), "Library", "Caches")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "ZimbraViewer")

def cartelle_config_utente() -> List[str]:
    """Dove cercare le impostazioni di altri programmi (P7MReader), in ordine di preferenza."""
    if IS_WIN:
        return [os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")]
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    if IS_MAC:
        return [os.path.join(os.path.expanduser("~"), "Library", "Application Support"), xdg]
    return [xdg]

def ambiente_esterno() -> dict:
    """Ambiente per i programmi esterni (file manager, visualizzatori). Nell'eseguibile PyInstaller/AppImage su Linux
    LD_LIBRARY_PATH e le variabili Qt puntano alle librerie incluse: un programma di sistema le caricherebbe al posto
    delle sue e potrebbe non partire. Qui si ripristina l'ambiente originale."""
    env = dict(os.environ)
    if not FROZEN or IS_WIN:
        return env
    for var in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH"):
        orig = env.pop(var + "_ORIG", None)
        if orig:
            env[var] = orig
        else:
            env.pop(var, None)
    for var in list(env):
        if var.startswith(("QT_", "QTWEBENGINE", "QML", "PYTHON", "_PYI", "_MEI")) or var in ("APPDIR", "APPIMAGE", "ARGV0", "OWD"):
            if var not in ("QT_QPA_PLATFORMTHEME", "QT_SCALE_FACTOR", "QT_AUTO_SCREEN_SCALE_FACTOR", "QT_SCREEN_SCALE_FACTORS"):
                env.pop(var, None)
    return env

def _avvia_esterno(comando) -> bool:
    try:
        subprocess.Popen(comando, env=ambiente_esterno(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=not IS_WIN)
        return True
    except Exception:
        return False

def apri_esterno(percorso: str) -> bool:
    """Apre un file o una cartella con il programma predefinito del sistema."""
    if IS_LINUX and FROZEN and shutil.which("xdg-open"):
        return _avvia_esterno(["xdg-open", percorso])
    return QDesktopServices.openUrl(QUrl.fromLocalFile(percorso))

def mostra_nel_file_manager(percorso: str) -> None:
    """Apre la cartella del file con il file selezionato (Esplora file, Finder o il file manager di Linux)."""
    percorso = os.path.abspath(percorso)
    if IS_WIN and _avvia_esterno(["explorer", f"/select,{os.path.normpath(percorso)}"]):
        return
    if IS_MAC and _avvia_esterno(["open", "-R", percorso]):
        return
    if IS_LINUX and shutil.which("dbus-send"):
        uri = QUrl.fromLocalFile(percorso).toString(QUrl.ComponentFormattingOption.FullyEncoded)
        try:
            r = subprocess.run(["dbus-send", "--session", "--print-reply", "--dest=org.freedesktop.FileManager1",
                                "--type=method_call", "/org/freedesktop/FileManager1",
                                "org.freedesktop.FileManager1.ShowItems", f"array:string:{uri}", "string:"],
                               env=ambiente_esterno(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            if r.returncode == 0:
                return
        except Exception:
            pass
    apri_esterno(os.path.dirname(percorso))

def contesto_ssl() -> ssl.SSLContext:
    """HTTPS verificato ovunque: certificati di sistema + quelli di certifi (indispensabili nell'app per macOS,
    dove l'OpenSSL incluso non conosce il portachiavi di sistema)."""
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    if not IS_WIN:
        for f in FILE_CA_SISTEMA:
            if os.path.isfile(f):
                try:
                    ctx.load_verify_locations(f)
                except Exception:
                    pass
                break
    return ctx

# Raccolte di certificati delle principali distribuzioni (Debian/Ubuntu, Fedora/RHEL, openSUSE, Arch, Alpine) e macOS
FILE_CA_SISTEMA = ("/etc/ssl/certs/ca-certificates.crt", "/etc/pki/tls/certs/ca-bundle.crt",
                   "/etc/ssl/ca-bundle.pem", "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
                   "/etc/ca-certificates/extracted/tls-ca-bundle.pem", "/etc/ssl/cert.pem")

def scarica_url(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    if url.lower().startswith("https://"):
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX_SSL()) as r:
            return r.read()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

_ctx_ssl_cache = []
def _CTX_SSL():
    if not _ctx_ssl_cache:
        _ctx_ssl_cache.append(contesto_ssl())
    return _ctx_ssl_cache[0]

def prepara_webengine():
    """Da chiamare prima di creare QApplication. Su Linux Chromium usa i namespace utente come sandbox: alcune
    distribuzioni (Ubuntu 23.10+ con AppArmor, kernel con unprivileged_userns_clone=0) li vietano ai programmi
    non installati e l'anteprima non partirebbe. Solo in quel caso si disattiva la sandbox di Chromium
    (le anteprime hanno comunque JavaScript spento e link non navigabili)."""
    if not IS_LINUX or "QTWEBENGINE_DISABLE_SANDBOX" in os.environ:
        return
    def leggi(p):
        try:
            with open(p) as f:
                return f.read().strip()
        except Exception:
            return None
    vietati = (leggi("/proc/sys/kernel/apparmor_restrict_unprivileged_userns") == "1"
               or leggi("/proc/sys/kernel/unprivileged_userns_clone") == "0"
               or leggi("/proc/sys/user/max_user_namespaces") == "0")
    if vietati or os.geteuid() == 0:
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# ==========================================
# TEMA: PALETTE, FOGLIO DI STILE, ICONE
# ==========================================
VERSIONE_APP = "3.2.1"
NOME_APP = f"ZimbraViewer {VERSIONE_APP}"

C = {   # palette scura "inchiostro e lavanda"
    "sfondo": "#13141B", "superficie": "#1A1B24", "rilievo": "#22232E", "hover": "#2A2C39",
    "bordo": "#2E303D", "bordo_tenue": "#24252F", "testo": "#E8E9F0", "attenuato": "#A0A3B8",
    "tenue": "#9094AA", "accento": "#8E9DFF", "accento_chiaro": "#A9B5FF", "accento_scuro": "#4C57CC",
    "accento_medio": "#6B79EE", "su_accento": "#0D0E15", "selezione": "#2D3253",
    "ok": "#5CD3A0", "warn": "#F4C46A", "error": "#F2738D", "none": "#8E92A8", "info": "#7CC4F5",
    # accessibilità: bordi dei controlli >= 3:1 (WCAG 1.4.11), anello di focus ben visibile (2.4.7)
    "bordo_controllo": "#70749A", "focus": "#F5F6FF", "carta_hover": "#1D1E29", "bordo_hover": "#3B3E58",
    "campo_focus": "#252738", "premuto": "#323447", "suggerimento": "#1E2033", "bordo_suggerimento": "#343A66",
    "barra": "#0E0F15", "scroll": "#3A3C50", "scroll_hover": "#545873",
}
# Tema ad alto contrasto (Impostazioni di accessibilità del sistema o menu «Accessibilità»): nero, bianco e giallo
C_ALTO_CONTRASTO = {
    "sfondo": "#000000", "superficie": "#000000", "rilievo": "#0A0A0A", "hover": "#1C1C1C",
    "bordo": "#FFFFFF", "bordo_tenue": "#BFBFBF", "testo": "#FFFFFF", "attenuato": "#F0F0F0",
    "tenue": "#E0E0E0", "accento": "#FFD400", "accento_chiaro": "#FFE45C", "accento_scuro": "#7A6500",
    "accento_medio": "#B39500", "su_accento": "#000000", "selezione": "#0047AB",
    "ok": "#3DFF8C", "warn": "#FFD400", "error": "#FF7A8E", "none": "#E0E0E0", "info": "#7FD4FF",
    "bordo_controllo": "#FFFFFF", "focus": "#00E5FF", "carta_hover": "#111111", "bordo_hover": "#FFFFFF",
    "campo_focus": "#000000", "premuto": "#333333", "suggerimento": "#000000", "bordo_suggerimento": "#FFFFFF",
    "barra": "#000000", "scroll": "#BFBFBF", "scroll_hover": "#FFFFFF",
}
COLORE_ESITO = {"ok": C["ok"], "warn": C["warn"], "error": C["error"], "none": C["none"]}
ACCESSIBILITA = {"scala": 1.0, "alto_contrasto": False, "animazioni_ridotte": False}


def applica_palette(alto_contrasto):
    """Da chiamare prima di creare le finestre: i colori del programma passano al tema ad alto contrasto."""
    if alto_contrasto:
        C.update(C_ALTO_CONTRASTO)
        COLORE_ESITO.update({"ok": C["ok"], "warn": C["warn"], "error": C["error"], "none": C["none"]})
        _cache_icone.clear()

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A9B5FF"/><stop offset="1" stop-color="#6B79EE"/></linearGradient></defs>
    <rect x="6" y="6" width="116" height="116" rx="28" fill="#1A1B24"/>
    <rect x="22" y="34" width="84" height="58" rx="10" fill="none" stroke="url(#g)" stroke-width="7"/>
    <path d="M 24 40 L 64 68 L 104 40" fill="none" stroke="url(#g)" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="96" cy="88" r="15" fill="#13141B" stroke="#5CD3A0" stroke-width="6"/>
    <path d="M 89 88 L 94 93 L 103 83" fill="none" stroke="#5CD3A0" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

# Icone a tratto (24x24), disegnate per questo programma
_TRACCIATI = {
    "cartella": "M3 7.5A2.5 2.5 0 0 1 5.5 5H9l2 2h7.5A2.5 2.5 0 0 1 21 9.5v8a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z",
    "archivio": "M3.5 8h17v11a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 19z M2.5 4.5h19V8h-19z M10 12h4",
    "busta": "M3.5 6.5h17v11h-17z M3.5 7l8.5 6.5L20.5 7",
    "cerca": "M10.5 4a6.5 6.5 0 1 0 0 13a6.5 6.5 0 1 0 0-13z M15.5 15.5L20 20",
    "esporta": "M12 15V3.5 M7.5 8L12 3.5 16.5 8 M4.5 14v5.5h15V14",
    "scarica": "M12 4v11 M7.5 10.5L12 15l4.5-4.5 M4.5 19.5h15",
    "apri": "M13.5 4.5h6v6 M19.5 4.5l-8.5 8.5 M18 14v5.5H4.5V6H10",
    "scudo": "M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z M8.8 12l2.2 2.2 4.3-4.4",
    "cestino": "M4 7h16 M9.5 7V4.5h5V7 M6 7l1 13h10l1-13 M10 11v5.5 M14 11v5.5",
    "documento": "M6 3h8.5L19 7.5V21H6z M14 3v5h5 M9 13h7 M9 16.5h7",
    "casa": "M3.5 11L12 4l8.5 7 M6 9.5V20h12V9.5 M10 20v-5h4v5",
    "aggiorna": "M19.5 12a7.5 7.5 0 1 1-2.2-5.3 M19.5 4.5v4.5H15",
    "spunta": "M5 12.5l4.5 4.5L19 7.5",
    "certificato": "M4 4.5h16v11H4z M8 8.5h8 M8 11.5h5 M15 15.5l-1.5 5 2.5-1.5 2.5 1.5-1.5-5",
    "tabella": "M4 5h16v14H4z M4 10h16 M4 14.5h16 M10 5v14",
    "carica": "M12 16V4.5 M7.5 9L12 4.5 16.5 9 M4.5 15.5V19.5h15v-4",
    "copia": "M8.5 8.5h11v11h-11z M5 15.5H4.5V4.5h11V5",
    "chiudi": "M6.5 6.5l11 11 M17.5 6.5l-11 11",
    "riduci": "M5 18.5h14",
    "graffetta": "M15.5 7.5l-6.8 6.8a2 2 0 0 0 2.8 2.8l7-7a4 4 0 0 0-5.7-5.7l-7.2 7.2a6 6 0 0 0 8.5 8.5l6.2-6.2",
    "stampa": "M7 9V3.5h10V9 M5 9h14a1.5 1.5 0 0 1 1.5 1.5V16H17v4.5H7V16H3.5v-5.5A1.5 1.5 0 0 1 5 9z M9.5 16.5h5",
    "pacco": "M12 3l8 4.5v9L12 21l-8-4.5v-9z M4 7.5l8 4.5 8-4.5 M12 12v9",
    "aiuto": "M12 3.5a8.5 8.5 0 1 0 0 17a8.5 8.5 0 1 0 0-17z M9.6 9.5a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.7 M12 16.8v.2",
    "nuvola": "M7 18.5a4.5 4.5 0 0 1-.6-9A6 6 0 0 1 18 8.5a4 4 0 0 1-.5 10z",
    "lettere": "M3.5 5.5h11v8h-11z M3.5 6l5.5 4 5.5-4 M9.5 15.5v3h11v-8h-3",
    "calendario": "M4 6.5h16V20H4z M4 10.5h16 M8.5 3.5v5 M15.5 3.5v5 M8 14h2 M11 14h2 M14 14h2 M8 17h2 M11 17h2",
    "persona": "M12 4a4 4 0 1 0 0 8a4 4 0 1 0 0-8z M4.5 20.5c.8-3.6 3.8-6 7.5-6s6.7 2.4 7.5 6",
    "fumetto": "M4 5.5h16v10.5H10l-4.5 3.5V16H4z M8 9.5h8 M8 12.5h5",
    "accessibilita": "M12 3.5a1.8 1.8 0 1 0 0 3.6a1.8 1.8 0 1 0 0-3.6z M5 8.5l7 1.5 7-1.5 M12 10v4.5 M12 14.5l-3 6 M12 14.5l3 6",
    "tastiera": "M3 6.5h18v11H3z M6.5 10h1 M10 10h1 M13.5 10h1 M17 10h.5 M7.5 14h9",
}
_cache_icone = {}

def icona(nome, colore=None, dimensione=18):
    """QIcon vettoriale nel colore richiesto (renderizzata al doppio della dimensione: nitida anche in HiDPI)."""
    colore = colore or C["testo"]
    chiave = (nome, colore, dimensione)
    if chiave not in _cache_icone:
        lato = dimensione * 2
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{lato}" height="{lato}">'
               f'<path d="{_TRACCIATI.get(nome, _TRACCIATI["documento"])}" fill="none" stroke="{colore}" '
               f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
        pix = QPixmap()
        pix.loadFromData(svg.encode('utf-8'))
        _cache_icone[chiave] = QIcon(pix)
    return _cache_icone[chiave]

def pulsante(testo, nome_icona=None, ruolo=None, suggerimento=None, colore_icona=None):
    """QPushButton nello stile del programma. ruolo: primario | pericolo | fantasma | piccolo (combinabili)."""
    b = QPushButton(testo)
    if nome_icona:
        colore = colore_icona or (C["su_accento"] if ruolo and "primario" in ruolo else
                                  C["error"] if ruolo and "pericolo" in ruolo else C["accento_chiaro"])
        b.setIcon(icona(nome_icona, colore))
        b.setIconSize(QSize(16, 16))
    if ruolo:
        b.setProperty("ruolo", ruolo)
    if suggerimento:
        b.setToolTip(suggerimento)
        if not testo:
            b.setAccessibleName(suggerimento)       # pulsante con sola icona: il lettore di schermo legge questo
        else:
            b.setAccessibleDescription(suggerimento)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b

FONT_UI = ("'Segoe UI Variable Text', 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', 'Inter', 'Cantarell', "
           "'Noto Sans', 'Ubuntu', 'Roboto', 'DejaVu Sans', sans-serif")
FONT_HTML = ("'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Cantarell', 'Noto Sans', "
             "'Ubuntu', 'DejaVu Sans', Arial, sans-serif")
FONT_MONO = "Consolas, 'Cascadia Mono', Menlo, 'SF Mono', 'DejaVu Sans Mono', 'Liberation Mono', monospace"

def costruisci_stile(scala=1.0):
    """Foglio di stile dell'interfaccia; 'scala' ingrandisce tutti i testi (Ctrl + / Ctrl - / Ctrl 0)."""
    stile = f"""
QWidget {{ color: {C['testo']}; font-family: {FONT_UI}; font-size: 13px; }}
QMainWindow, QDialog, QWidget#sfondo, QStackedWidget {{ background-color: {C['sfondo']}; }}
QLabel {{ background: transparent; }}
QLabel#titolo {{ font-size: 26px; font-weight: 700; color: {C['testo']}; }}
QLabel#titoloMedio {{ font-size: 17px; font-weight: 700; }}
QLabel#sottotitolo {{ color: {C['attenuato']}; font-size: 14px; }}
QLabel#etichetta {{ color: {C['tenue']}; font-size: 11px; font-weight: 700; letter-spacing: 1px; }}
QLabel#attenuato {{ color: {C['attenuato']}; }}
QLabel#lblRisultati {{ color: {C['attenuato']}; padding: 0 6px; font-weight: 600; }}
QLabel#marchio {{ font-size: 15px; font-weight: 700; letter-spacing: 0.3px; }}
QLabel#versione {{ color: {C['tenue']}; font-size: 12px; }}

QWidget#barraTitolo {{ background-color: {C['superficie']}; border-bottom: 1px solid {C['bordo_tenue']}; }}
QFrame#carta {{ background-color: {C['superficie']}; border: 1px solid {C['bordo_tenue']}; border-radius: 14px; }}
QFrame#carta:hover {{ border-color: {C['bordo_hover']}; background-color: {C['carta_hover']}; }}
QFrame#pannello {{ background-color: {C['superficie']}; border: 1px solid {C['bordo_tenue']}; border-radius: 12px; }}
QFrame#suggerimento {{ background-color: {C['suggerimento']}; border: 1px solid {C['bordo_suggerimento']}; border-radius: 10px; }}

QPushButton {{ background-color: {C['rilievo']}; color: {C['testo']}; border: 1px solid {C['bordo']};
    border-radius: 8px; padding: 7px 14px; font-weight: 600; }}
QPushButton:hover {{ background-color: {C['hover']}; border-color: {C['bordo_controllo']}; }}
QPushButton:pressed {{ background-color: {C['premuto']}; }}
QPushButton:disabled {{ color: {C['tenue']}; background-color: {C['superficie']}; border-color: {C['bordo_tenue']}; }}
QPushButton[ruolo~="primario"] {{ background-color: {C['accento']}; color: {C['su_accento']}; border: 1px solid {C['accento']}; }}
QPushButton[ruolo~="primario"]:hover {{ background-color: {C['accento_chiaro']}; border-color: {C['accento_chiaro']}; }}
QPushButton[ruolo~="primario"]:disabled {{ background-color: #343960; color: #8D92B8; border-color: #343960; }}
QPushButton[ruolo~="pericolo"] {{ background-color: transparent; color: {C['error']}; border-color: #4E2E3A; }}
QPushButton[ruolo~="pericolo"]:hover {{ background-color: #2E1F27; border-color: #6A3A4A; }}
QPushButton[ruolo~="fantasma"] {{ background-color: transparent; border-color: transparent; color: {C['attenuato']}; }}
QPushButton[ruolo~="fantasma"]:hover {{ background-color: {C['rilievo']}; color: {C['testo']}; }}
QPushButton[ruolo~="piccolo"] {{ padding: 3px 10px; font-size: 12px; border-radius: 6px; }}
QPushButton::menu-indicator {{ width: 0; }}

QLineEdit, QComboBox {{ background-color: {C['rilievo']}; border: 1px solid {C['bordo_controllo']}; border-radius: 8px;
    padding: 7px 12px; selection-background-color: {C['accento']}; selection-color: {C['su_accento']}; }}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {C['focus']}; padding: 6px 11px; background-color: {C['campo_focus']}; }}
QLineEdit:disabled {{ color: {C['tenue']}; background-color: {C['superficie']}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{ background-color: {C['rilievo']}; border: 1px solid {C['bordo']};
    selection-background-color: {C['selezione']}; selection-color: {C['testo']}; padding: 4px; }}

QTableWidget, QTreeWidget, QListWidget, QTextBrowser, QScrollArea#elenco {{ background-color: {C['superficie']};
    border: 1px solid {C['bordo_tenue']}; border-radius: 12px; alternate-background-color: #1D1E28; gridline-color: transparent; }}
QTableWidget::item, QTreeWidget::item {{ padding: 6px 8px; border: none; }}
QTableWidget::item:hover, QTreeWidget::item:hover {{ background-color: #232533; }}
QTableWidget::item:selected, QTreeWidget::item:selected {{ background-color: {C['selezione']}; color: {C['testo']}; }}
QTableView::indicator, QTreeView::indicator, QCheckBox::indicator {{ width: 15px; height: 15px; border-radius: 4px;
    border: 1px solid {C['bordo_controllo']}; background-color: {C['rilievo']}; }}
QTableView::indicator:checked, QTreeView::indicator:checked, QCheckBox::indicator:checked {{
    background-color: {C['accento']}; border-color: {C['accento']}; }}
QCheckBox {{ spacing: 8px; }}
QHeaderView {{ background-color: transparent; }}
QHeaderView::section {{ background-color: {C['superficie']}; color: {C['tenue']}; border: none;
    border-bottom: 1px solid {C['bordo']}; padding: 8px 10px; font-weight: 700; font-size: 12px; }}
QTableCornerButton::section {{ background-color: {C['superficie']}; border: none; }}

QTabWidget::pane {{ border: none; top: 0px; }}
QTabBar {{ background: transparent; }}
QTabBar::tab {{ background: transparent; color: {C['attenuato']}; padding: 9px 16px; margin: 0 2px 0 0; border: none;
    border-bottom: 2px solid transparent; font-weight: 600; }}
QTabBar::tab:hover {{ color: {C['testo']}; background-color: #1C1D27; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
QTabBar::tab:selected {{ color: {C['testo']}; border-bottom: 2px solid {C['accento']}; }}

QSplitter::handle {{ background-color: transparent; }}
QSplitter::handle:horizontal {{ width: 8px; }}
QSplitter::handle:vertical {{ height: 8px; }}
QSplitter::handle:hover {{ background-color: #2F3247; border-radius: 3px; }}

QScrollBar:vertical {{ background: transparent; width: 11px; margin: 3px; }}
QScrollBar::handle:vertical {{ background-color: {C['scroll']}; border-radius: 4px; min-height: 32px; }}
QScrollBar::handle:vertical:hover {{ background-color: {C['scroll_hover']}; }}
QScrollBar:horizontal {{ background: transparent; height: 11px; margin: 3px; }}
QScrollBar::handle:horizontal {{ background-color: {C['scroll']}; border-radius: 4px; min-width: 32px; }}
QScrollBar::handle:horizontal:hover {{ background-color: {C['scroll_hover']}; }}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ width: 0; height: 0; background: none; }}

QMenu {{ background-color: {C['rilievo']}; border: 1px solid {C['bordo']}; border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 7px 24px 7px 12px; border-radius: 6px; }}
QMenu::item:selected {{ background-color: {C['selezione']}; }}
QMenu::item:disabled {{ color: {C['tenue']}; }}
QMenu::separator {{ height: 1px; background-color: {C['bordo']}; margin: 5px 8px; }}
QMenu::icon {{ padding-left: 8px; }}

/* Barre di avanzamento: testo bianco in grassetto, leggibile sia sulla parte piena (indaco scuro) sia su quella vuota */
QProgressBar {{ background-color: {C['barra']}; border: 1px solid {C['bordo_controllo']}; border-radius: 8px; text-align: center;
    color: #FFFFFF; font-weight: 700; min-height: 20px; }}
QProgressBar::chunk {{ border-radius: 7px; background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop:0 {C['accento_scuro']}, stop:1 {C['accento_medio']}); }}
QProgressBar#barraChip {{ min-height: 16px; max-height: 18px; font-size: 11px; border-radius: 7px; }}
QProgressBar#barraChip::chunk {{ border-radius: 6px; }}

QStatusBar {{ background-color: {C['superficie']}; color: {C['attenuato']}; border-top: 1px solid {C['bordo_tenue']}; }}
QStatusBar::item {{ border: none; }}
QWidget#chipEsportazione {{ background-color: {C['rilievo']}; border: 1px solid {C['bordo']}; border-radius: 8px; }}
QWidget#chipEsportazione QLabel {{ color: {C['testo']}; font-weight: 600; }}

QToolTip {{ background-color: {C['rilievo']}; color: {C['testo']}; border: 1px solid {C['bordo']}; padding: 6px 8px; border-radius: 6px; }}
QMessageBox {{ background-color: {C['superficie']}; }}
QMessageBox QLabel {{ color: {C['testo']}; }}
QMessageBox QPushButton {{ min-width: 84px; }}

QListWidget::item {{ padding: 5px 6px; border-radius: 6px; }}
QListWidget::item:hover {{ background-color: {C['hover']}; }}
QListWidget::item:selected {{ background-color: {C['selezione']}; color: {C['testo']}; }}

/* Focus da tastiera sempre visibile (WCAG 2.4.7) */
QPushButton:focus {{ border: 2px solid {C['focus']}; padding: 6px 13px; }}
QPushButton[ruolo~="piccolo"]:focus {{ padding: 2px 9px; }}
QCheckBox:focus {{ border: 2px solid {C['focus']}; border-radius: 4px; padding: 1px 3px; }}
QTableWidget:focus, QTreeWidget:focus, QListWidget:focus, QTextBrowser:focus, QScrollArea:focus {{
    border: 2px solid {C['focus']}; }}
QTableView::item:focus, QTreeView::item:focus, QListView::item:focus {{ border: 1px solid {C['focus']}; }}
QTabBar:focus {{ border: none; }}
QTabBar::tab:focus {{ border: 2px solid {C['focus']}; border-radius: 6px; }}
QMenu::item:selected {{ border: 1px solid {C['focus']}; }}
"""
    if scala != 1.0:
        stile = re.sub(r'font-size: ?(\d+(?:\.\d+)?)px',
                       lambda m: f"font-size: {max(8, round(float(m.group(1)) * scala))}px", stile)
    return stile

STILE = costruisci_stile()

# ==========================================
# UTILITA': ERRORI, NOMI DI FILE, PERCORSI, PARTI DELLE MAIL
# ==========================================
def mostra_errore_con_copia(parent, titolo, messaggio):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(titolo)
    msg_box.setText(messaggio)
    btn_copia = msg_box.addButton("Copia il testo", QMessageBox.ButtonRole.ActionRole)
    msg_box.addButton(QMessageBox.StandardButton.Ok)
    msg_box.exec()
    if msg_box.clickedButton() == btn_copia:
        QApplication.clipboard().setText(messaggio)
        QMessageBox.information(parent, "Copiato", "Il testo dell'errore è stato copiato negli appunti.")

# Estensioni che possono eseguire codice: prima di aprirle si chiede conferma
ESTENSIONI_PERICOLOSE = {
    '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.msi', '.dll', '.cpl', '.lnk',
    '.js', '.jse', '.vbs', '.vbe', '.wsf', '.wsh', '.ps1', '.hta', '.jar', '.reg',
    '.sh', '.bash', '.zsh', '.run', '.bin', '.appimage', '.desktop', '.deb', '.rpm', '.py', '.pl',  # Linux
    '.app', '.command', '.tool', '.pkg', '.mpkg', '.dmg', '.workflow', '.scpt', '.applescript',    # macOS
}

_base_temp_allegati = None

def cartella_temp_allegati():
    """Cartella temporanea per gli allegati aperti al volo; viene ripulita all'uscita."""
    global _base_temp_allegati
    if _base_temp_allegati is None or not os.path.isdir(_base_temp_allegati):
        _base_temp_allegati = tempfile.mkdtemp(prefix="ZimbraViewer_")
        atexit.register(shutil.rmtree, _base_temp_allegati, True)
    return _base_temp_allegati

def percorso_libero(cartella, nome):
    path_out = os.path.join(cartella, nome)
    base, ext = os.path.splitext(nome)
    contatore = 1
    while os.path.exists(path_out):
        path_out = os.path.join(cartella, f"{base}_{contatore}{ext}")
        contatore += 1
    return path_out

# ==========================================
# NOMI WINDOWS-SAFE, POSTACERT.EML, ALLEGATI E P7M
# ==========================================
NOMI_RISERVATI_WINDOWS = {"CON", "PRN", "AUX", "NUL",
                          *(f"COM{i}" for i in range(1, 10)),
                          *(f"LPT{i}" for i in range(1, 10))}

def nome_windows_sicuro(nome, max_len=100, fallback="senza_nome", con_estensione=True):
    """Nome valido su Windows: niente caratteri vietati, niente punti/spazi finali,
    niente nomi riservati (CON, NUL...) e lunghezza limitata (l'estensione viene preservata)."""
    nome = re.sub(r'[\\/*?:"<>|\x00-\x1F\x7F]', "_", str(nome or ""))
    nome = re.sub(r'\s+', ' ', nome).strip(' .')
    if not nome:
        nome = fallback
    base, ext = os.path.splitext(nome) if con_estensione else (nome, "")
    if not base or len(ext) > 12:   # estensione implausibile: fa parte del nome
        base, ext = nome, ""
    if len(base) + len(ext) > max_len:
        base = base[:max(1, max_len - len(ext))]
    base = base.rstrip(' .') or "_"
    if base.split('.')[0].strip().upper() in NOMI_RISERVATI_WINDOWS:
        base = "_" + base
    return base + ext

def e_percorso_assoluto(p):
    """Assoluto in stile Windows (C:\\..., \\\\server\\...) o POSIX, a prescindere dal sistema su cui gira."""
    return bool(p) and (os.path.isabs(p) or re.match(r'^[A-Za-z]:[\\/]', p) is not None or p.startswith(('\\\\', '//')))

def risolvi_percorso_eml(radice, salvato):
    """Percorso reale di un .eml a partire dal valore salvato nell'indice (relativo alla cartella dell'export)."""
    if not salvato or e_percorso_assoluto(salvato):
        return salvato
    return os.path.normpath(os.path.join(radice, *salvato.split('/')))

def cartella_libera(cartella_padre, nome):
    """Percorso di una sottocartella non ancora esistente: 'nome', poi 'nome (2)', 'nome (3)'..."""
    percorso = os.path.join(cartella_padre, nome)
    contatore = 2
    while os.path.exists(percorso):
        percorso = os.path.join(cartella_padre, f"{nome} ({contatore})")
        contatore += 1
    return percorso

# postacert.eml (busta di trasporto PEC) è come se non esistesse: non si elenca, non si estrae, non si apre
def e_postacert(nome):
    return os.path.basename(str(nome or "").replace('\\', '/')).strip().lower() == "postacert.eml"

# allegati che la vista non mostra (anche negli indici creati dalle versioni precedenti): busta PEC e file tecnici
FILTRO_ALLEGATI_SQL = "LOWER(nome_file) NOT IN ('postacert.eml', 'daticert.xml', 'smime.p7s')"

def _percorri_parti(msg, per_esportazione):
    """Come msg.walk(), ma senza scendere nei messaggi allegati (message/rfc822): restano un unico allegato .eml.
    Eccezione: nella vista normale si scende dentro postacert.eml, così i veri allegati della PEC restano
    visibili e apribili; nell'esportazione, invece, il postacert.eml viene scompattato a parte."""
    def rec(part):
        yield part
        if part.is_multipart():
            if part.get_content_type() == "message/rfc822" and (per_esportazione or not e_postacert(part.get_filename())):
                return
            for sub in part.iter_parts():
                yield from rec(sub)
    yield from rec(msg)

def e_parte_allegato(part, per_esportazione=False):
    """True se la parte MIME è un allegato vero (non un'immagine incorporata nel corpo).
    postacert.eml, daticert.xml e smime.p7s sono nascosti nella vista e inclusi solo nell'esportazione (sono le prove PEC)."""
    nome = part.get_filename()
    if not nome or part.get_content_maintype() == 'multipart':
        return False
    if not per_esportazione and (e_postacert(nome) or e_allegato_tecnico(part, nome)):
        return False                      # come una casella PEC: busta, daticert.xml e smime.p7s non si vedono
    return part.get_content_disposition() == 'attachment' or not part.get('Content-ID')

def allegati_da_msg(msg, per_esportazione=False):
    return [(part.get_filename(), part) for part in _percorri_parti(msg, per_esportazione)
            if e_parte_allegato(part, per_esportazione)]

def payload_allegato(part):
    """Contenuto binario di un allegato; gestisce anche i messaggi .eml allegati (message/rfc822)."""
    if part.get_content_type() == "message/rfc822":
        interni = part.get_payload()
        if isinstance(interni, list) and interni:
            try:
                return interni[0].as_bytes()
            except Exception:
                return interni[0].as_bytes(policy=policy.compat32)
        return None
    return part.get_payload(decode=True)

def prefisso_data_ora(msg, data_tabella=""):
    """'AAAA.MM.GG HH.mm.ss' dalla data della mail (stessa logica dell'indice: ora scritta nell'intestazione)."""
    candidati = [msg.get('Date')] + [(r.split(';')[-1].strip() if ';' in r else None) for r in msg.get_all('Received', [])]
    for raw in candidati:
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(str(raw))
            return dt.strftime('%Y.%m.%d %H.%M.%S')
        except Exception:
            continue
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})(?: (\d{2}):(\d{2}))?', data_tabella or "")
    if m:
        a, me, g, h, mi = m.groups()
        return f"{a}.{me}.{g} {h or '00'}.{mi or '00'}.00"
    return "0000.00.00 00.00.00"


def testo_parte(part):
    """Testo di una parte MIME anche con charset sconosciuti o errati (es. "unknown-8bit", comune nella posta vecchia)."""
    try:
        return str(part.get_content())
    except Exception:
        dati = part.get_payload(decode=True) or b""
        for codifica in (part.get_content_charset() or "", "utf-8", "cp1252"):
            if not codifica:
                continue
            try:
                return dati.decode(codifica)
            except (LookupError, UnicodeDecodeError):
                continue
        return dati.decode("latin-1", "replace")

def data_da_msg(msg):
    """Data della mail 'AAAA-MM-GG HH:MM' dall'intestazione Date o, se manca, dall'ultimo Received."""
    raw_date = msg.get('Date')
    if raw_date:
        try:
            return parsedate_to_datetime(raw_date).strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass
    for r_hdr in msg.get_all('Received', []):
        try:
            parti = r_hdr.split(';')
            if len(parti) > 1:
                return parsedate_to_datetime(parti[-1].strip()).strftime('%Y-%m-%d %H:%M')
        except Exception:
            continue
    return str(raw_date or 'Sconosciuta')

# ==========================================
# HTML DELLA MAIL (anteprima ed esportazione PDF)
# ==========================================

# ==========================================
# PAGINA DELLA MAIL: INTESTAZIONI, STORICO DELLA CONVERSAZIONE, PEC
# L'area di lettura è sempre chiara (come un foglio), indipendentemente dal tema scuro del programma.
# ==========================================
P = {"foglio": "#FFFFFF", "testo": "#1D2030", "tenue": "#5F6475", "bordo": "#E1E4EE", "accento": "#6B79EE",
     "accento_testo": "#4C57CC",
     "fondo_blocco": "#F5F6FB", "citazione": "#C9CDE3", "testo_citato": "#555A72",
     "ok": "#1E9E6A", "warn": "#C98A12", "error": "#D6455F"}
FONT_PAGINA = FONT_HTML
STILE_BASE_PAGINA = (f"<style>html{{background:{P['foglio']};color:{P['testo']}}}"
                     f"a{{color:{P['accento_testo']}}}</style>")

# ---------- intestazioni ----------
_SINONIMI = {"da": "Da", "from": "Da", "mittente": "Da", "inviato": "Data", "sent": "Data", "data": "Data",
             "date": "Data", "a": "A", "to": "A", "cc": "Cc", "ccn": "Ccn", "bcc": "Ccn", "oggetto": "Oggetto",
             "subject": "Oggetto", "rispondi a": "Rispondi a", "reply-to": "Rispondi a"}
_ORDINE_CAMPI = ["Da", "Data", "A", "Cc", "Ccn", "Rispondi a", "Oggetto"]
_ETICHETTE_RE = r"(da|from|mittente|inviato|sent|data|date|a|to|cc|ccn|bcc|oggetto|subject|rispondi a|reply-to)"
_PAROLE_SEPARATORE = re.compile(r"(messaggio originale|original message|messaggio inoltrato|forwarded message|"
                                r"inizio messaggio inoltrato|begin forwarded message|mail inoltrata)", re.I)

def _normalizza_campi(campi):
    """[(etichetta qualsiasi, valore)] -> [(etichetta italiana, valore)] nell'ordine Da, Data, A, Cc, Ccn, Oggetto."""
    visti = {}
    for k, v in campi:
        k2 = _SINONIMI.get(k.strip().lower(), k.strip().capitalize())
        v = re.sub(r"\s+", " ", v).strip()
        if v and k2 not in visti:
            visti[k2] = v
    return sorted(visti.items(), key=lambda kv: _ORDINE_CAMPI.index(kv[0]) if kv[0] in _ORDINE_CAMPI else 99)

def _campi_validi(campi):
    chiavi = {k for k, _v in _normalizza_campi(campi)}
    return len(chiavi) >= 2 and "Da" in chiavi and bool(chiavi & {"Oggetto", "Data", "A"})

def blocco_intestazione(campi, titolo=None, principale=False, colore=None):
    """Intestazione vera (Da, Data, A, Cc, Ccn, Oggetto): in cima alla mail e come separatore nello storico."""
    colore = colore or P["accento"]
    e = html.escape
    campi = _normalizza_campi(campi)
    oggetto = next((v for k, v in campi if k == "Oggetto"), "")
    righe = "".join(
        f"<tr><td style='width:96px;color:{P['tenue']};font-weight:600;padding:2px 10px 2px 0;vertical-align:top'>{e(k)}</td>"
        f"<td style='padding:2px 0;color:{P['testo']}'>{e(v)}</td></tr>"
        for k, v in campi if not (principale and k == "Oggetto"))
    if principale:
        return (f"<div style=\"font-family:{FONT_PAGINA};background:{P['foglio']};border:1px solid {P['bordo']};"
                f"border-left:4px solid {colore};border-radius:10px;padding:16px 18px;margin:0 0 22px 0;color:{P['testo']}\">"
                f"<div style='font-size:19px;font-weight:700;margin:0 0 10px 0;color:#141625'>{e(oggetto or '(Nessun oggetto)')}</div>"
                f"<table style='width:100%;font-size:13px;border-collapse:collapse'>{righe}</table></div>")
    return (f"<div style=\"font-family:{FONT_PAGINA};clear:both;background:{P['fondo_blocco']};border:1px solid {P['bordo']};"
            f"border-left:4px solid {colore};border-radius:8px;padding:10px 14px;margin:26px 0 14px 0;color:{P['testo']};"
            f"font-size:12.5px;line-height:1.45\">"
            f"<div style='font-size:10.5px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;color:{colore};"
            f"margin:0 0 6px 0'>{e(titolo or 'Messaggio precedente')}</div>"
            f"<table style='border-collapse:collapse;font-size:12.5px'>{righe}</table></div>")

def blocco_attribuzione(testo):
    """Riga "Il giorno ... ha scritto:" resa come separatore."""
    return (f"<div style=\"font-family:{FONT_PAGINA};clear:both;margin:22px 0 10px 0;padding:7px 12px;background:{P['fondo_blocco']};"
            f"border-left:4px solid {P['accento']};border-radius:6px;font-size:12.5px;color:#41465E\">"
            f"&#8617;&nbsp; {html.escape(testo.strip())}</div>")

def intestazione_principale(msg, data_formattata, colore=None):
    campi = [("Da", str(msg.get('From', '') or '')), ("Data", str(data_formattata or '')), ("A", str(msg.get('To', '') or '')),
             ("Cc", str(msg.get('Cc', '') or '')), ("Ccn", str(msg.get('Bcc', '') or '')),
             ("Rispondi a", str(msg.get('Reply-To', '') or '')), ("Oggetto", str(msg.get('Subject', '') or ''))]
    return blocco_intestazione(campi, principale=True, colore=colore)

# ---------- storico nel testo semplice ----------
_RE_CAMPO_TXT = re.compile(r"^\s*(?:>\s*)*[*\s]*" + _ETICHETTE_RE + r"[*\s]*:[*\s]*(.*?)\s*$", re.I)
_RE_ATTRIB_INIZIO = re.compile(r"^\s*(?:>\s*)*(il giorno|il |on |in data )", re.I)
_RE_ATTRIB_FINE = re.compile(r"(ha scritto|wrote|scrisse)\s*:\s*$", re.I)

def _e_separatore_testo(riga):
    t = riga.strip().lstrip(">").strip()
    if re.fullmatch(r"[-_=]{8,}", t):
        return True
    return bool(_PAROLE_SEPARATORE.search(t)) and len(t) < 90 and bool(re.match(r"^[-_=*\s]*[A-Za-z]", t) or "--" in t)

def _leggi_campi_testo(righe, j):
    campi = []
    while j < len(righe):
        m = _RE_CAMPO_TXT.match(righe[j])
        if m:
            campi.append((m.group(1), m.group(2)))
            j += 1
        elif campi and campi[-1][0].lower() in ("a", "to", "cc", "ccn", "bcc") and "@" in righe[j] and righe[j].strip():
            campi[-1] = (campi[-1][0], campi[-1][1] + " " + righe[j].strip())     # elenco destinatari andato a capo
            j += 1
        else:
            break
    return campi, j

def testo_con_storico(testo):
    """Testo semplice -> HTML, con le intestazioni dei messaggi precedenti trasformate in separatori."""
    righe = testo.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(righe)
    while i < n:
        riga = righe[i]
        titolo, j = None, i
        if _e_separatore_testo(riga):
            titolo = "Messaggio inoltrato" if re.search(r"inoltrat|forward", riga, re.I) else "Messaggio precedente"
            j = i + 1
            while j < n and not righe[j].strip():
                j += 1
        campi, k = _leggi_campi_testo(righe, j)
        if _campi_validi(campi):
            out.append(blocco_intestazione(campi, titolo or "Messaggio precedente"))
            i = k
            continue
        if titolo:                                     # separatore senza intestazioni: lo si mostra comunque
            out.append(blocco_attribuzione(riga.strip(" -_=>")))
            i += 1
            continue
        if _RE_ATTRIB_INIZIO.match(riga):
            unita = riga if _RE_ATTRIB_FINE.search(riga) else (riga + " " + righe[i + 1] if i + 1 < n else riga)
            if _RE_ATTRIB_FINE.search(unita) and len(unita) < 400:
                out.append(blocco_attribuzione(unita.lstrip("> ")))
                i += 1 if _RE_ATTRIB_FINE.search(riga) else 2
                continue
        livello = len(re.match(r"^((?:>\s?)*)", riga).group(1).replace(" ", ""))
        contenuto = html.escape(riga[len(re.match(r"^((?:>\s?)*)", riga).group(1)):]) or "&nbsp;"
        if livello:
            out.append(f"<div style='border-left:3px solid {P['citazione']};padding-left:10px;margin-left:{(livello - 1) * 12}px;"
                       f"color:{P['testo_citato']}'>{contenuto}</div>")
        else:
            out.append(f"<div>{contenuto}</div>")
        i += 1
    return "".join(out)

# ---------- storico nell'HTML ----------
_TAG_INLINE = r"(?:b|strong|span|font|i|em|u)"
_RE_CAMPO_HTML = re.compile(
    r"(?:<" + _TAG_INLINE + r"\b[^>]*>\s*)*(?<![\w&;])" + _ETICHETTE_RE + r"\s*:\s*(?:</" + _TAG_INLINE + r">\s*|&nbsp;\s*)*"
    r"(?P<val>(?:(?!<br\b|</p>|</div>|<p[\s>]|<div[\s>]|</td>|<tr[\s>]|</li>).){0,700}?)"
    r"(?=<br\b|</p>|</div>|<p[\s>]|<div[\s>]|</td>|<tr[\s>]|</li>|$)", re.I | re.S)
_RE_INTERVALLO = re.compile(r"^(?:\s|&nbsp;|<br\s*/?>|</?(?:p|div|span|font|b|strong|i|em|u|o:p)\b[^>]*>)*$", re.I)
_RE_SEP_PRIMA = re.compile(r"(?:<hr\b[^>]*>|[-_]{2,}\s*(?:messaggio originale|original message|messaggio inoltrato|"
                           r"forwarded message|inizio messaggio inoltrato|begin forwarded message)\s*[-_]*:?)"
                           r"(?:\s|&nbsp;|<br\s*/?>|</?(?:p|div|span|font|b|strong|o:p)\b[^>]*>)*$", re.I)

def _testo_da_html(frammento):
    testo = html.unescape(re.sub(r"<[^>]+>", " ", frammento))
    testo = re.sub(r"<\s+", "<", re.sub(r"\s+>", ">", testo))       # "< mario@x.it >" -> "<mario@x.it>"
    return re.sub(r"[ \t]+", " ", testo)

def html_con_storico(h):
    """Nel corpo HTML: intestazioni dei messaggi precedenti (Outlook, Gmail, Zimbra, Thunderbird...) -> separatori."""
    # 1) Thunderbird: tabella delle intestazioni dei messaggi inoltrati
    def _tabella(m):
        campi = [(_testo_da_html(a).strip().rstrip(":"), _testo_da_html(b))
                 for a, b in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", m.group(0), re.I | re.S)]
        return blocco_intestazione(campi, "Messaggio inoltrato") if _campi_validi(campi) else m.group(0)
    h = re.sub(r"(?:-{2,}\s*(?:messaggio inoltrato|messaggio originale|forwarded message|original message)\s*-{2,}\s*(?:<br\s*/?>\s*)*)?"
               r"<table[^>]*moz-email-headers-table[^>]*>.*?</table>", _tabella, h, flags=re.I | re.S)
    # 2) sequenze "Da: ... <br> Inviato: ... <br> A: ... <br> Oggetto: ..."
    gruppi, corrente = [], []
    for m in _RE_CAMPO_HTML.finditer(h):
        if corrente and not _RE_INTERVALLO.match(h[corrente[-1].end():m.start()]):
            gruppi.append(corrente)
            corrente = []
        corrente.append(m)
    if corrente:
        gruppi.append(corrente)
    for gruppo in reversed(gruppi):
        campi = [(m.group(1), _testo_da_html(m.group("val"))) for m in gruppo]
        if not _campi_validi(campi):
            continue
        inizio, fine = gruppo[0].start(), gruppo[-1].end()
        prima = _RE_SEP_PRIMA.search(h[max(0, inizio - 400):inizio])
        titolo = "Messaggio precedente"
        if prima:
            if re.search(r"inoltrat|forward", prima.group(0), re.I):
                titolo = "Messaggio inoltrato"
            inizio = max(0, inizio - 400) + prima.start()
        dopo = re.match(r"(?:\s|&nbsp;|<br\s*/?>)*", h[fine:])
        fine += dopo.end() if dopo else 0
        h = h[:inizio] + blocco_intestazione(campi, titolo) + h[fine:]
    # 3) "Il giorno ... ha scritto:" (Gmail, Thunderbird e testo libero)
    def _attrib(m):
        testo = re.sub(r"\s+", " ", _testo_da_html(m.group(1))).strip()
        return blocco_attribuzione(testo) if _RE_ATTRIB_FINE.search(testo) and len(testo) < 400 else m.group(0)
    h = re.sub(r"<div[^>]*(?:gmail_attr|moz-cite-prefix)[^>]*>(.*?)</div>", _attrib, h, flags=re.I | re.S)
    h = re.sub(r"(?<=>)(\s*(?:Il|On)\s[^<>]{3,300}?(?:ha scritto|wrote)\s*:\s*)(?=<)",
               lambda m: blocco_attribuzione(html.unescape(m.group(1))), h)
    return h

# ---------- PEC ----------
_TIPI_PEC = {"posta-certificata": ("Posta certificata", "ok"), "accettazione": ("Ricevuta di accettazione", "ok"),
             "avvenuta-consegna": ("Ricevuta di avvenuta consegna", "ok"), "presa-in-carico": ("Ricevuta di presa in carico", "ok"),
             "non-accettazione": ("Avviso di non accettazione", "error"), "errore-consegna": ("Avviso di mancata consegna", "error"),
             "preavviso-errore-consegna": ("Preavviso di mancata consegna", "warn"),
             "rilevazione-virus": ("Rilevazione di virus informatico", "error"), "errore": ("Anomalia del messaggio", "error")}
NOMI_TECNICI_PEC = {"daticert.xml", "smime.p7s"}

def e_allegato_tecnico(part, nome=None):
    """Allegati che una casella PEC (o un client S/MIME) non mostra: daticert.xml e la firma smime.p7s."""
    nome = os.path.basename(str(nome or part.get_filename() or "").replace("\\", "/")).strip().lower()
    return nome in NOMI_TECNICI_PEC or part.get_content_type() in ("application/pkcs7-signature", "application/x-pkcs7-signature")

def _parti_della_busta(msg):
    """Parti della mail (anche dentro multipart/signed e multipart/mixed), senza entrare nei messaggi allegati."""
    if not msg.is_multipart() or msg.get_content_type() == "message/rfc822":
        return
    for sub in msg.iter_parts():
        yield sub
        if sub.is_multipart() and sub.get_content_type() != "message/rfc822":
            yield from _parti_della_busta(sub)

def info_pec(msg):
    """Dati di una mail PEC (busta di trasporto o ricevuta), letti dalle intestazioni e da daticert.xml; None se non è PEC."""
    tipo = str(msg.get("X-Ricevuta") or msg.get("X-Trasporto") or "").strip().lower()
    daticert, busta = None, None
    for part in _parti_della_busta(msg):
        nome = (part.get_filename() or "").strip().lower()
        if nome == "daticert.xml" and daticert is None:
            daticert = part.get_payload(decode=True)
        elif e_postacert(nome) and busta is None:
            busta = part
    if not tipo and daticert is None:
        return None
    info = {"tipo": tipo, "campi": [], "postacert": busta, "errore": ""}
    if daticert:
        try:
            radice = ET.fromstring(daticert)
            info["tipo"] = info["tipo"] or radice.get("tipo", "")
            info["errore"] = radice.get("errore", "") if radice.get("errore", "") not in ("", "nessuno") else ""
            testo = lambda percorso: " ".join((x.text or "").strip() for x in radice.iterfind(percorso) if (x.text or "").strip())
            data = radice.find("dati/data")
            quando = ""
            if data is not None:
                quando = f"{(data.findtext('giorno') or '').strip()} {(data.findtext('ora') or '').strip()} {data.get('zona', '')}".strip()
            destinatari = ", ".join(f"{(d.text or '').strip()}" + (" (certificato)" if d.get("tipo") == "certificato" else "")
                                    for d in radice.iterfind("intestazione/destinatari") if (d.text or "").strip())
            info["campi"] = [("Gestore", testo("dati/gestore-emittente")), ("Data e ora", quando),
                             ("Mittente", testo("intestazione/mittente")), ("Destinatari", destinatari),
                             ("Oggetto", testo("intestazione/oggetto")), ("Consegnata a", testo("dati/consegna")),
                             ("Identificativo", testo("dati/identificativo")), ("Errore", testo("dati/errore-esteso"))]
        except Exception:
            pass
    return info

def blocco_pec(info, testo_busta=""):
    titolo, esito = _TIPI_PEC.get(info["tipo"], ("Posta elettronica certificata", "ok"))
    if info.get("errore"):
        esito = "error"
    colore = P[esito]
    e = html.escape
    righe = "".join(f"<tr><td style='color:{P['tenue']};font-weight:600;padding:2px 12px 2px 0;vertical-align:top;white-space:nowrap'>{e(k)}</td>"
                    f"<td style='padding:2px 0'>{e(v)}</td></tr>" for k, v in info["campi"] if v)
    busta = (f"<div style='margin-top:8px;color:{P['tenue']};font-size:12px;white-space:pre-wrap'>{e(testo_busta.strip())}</div>"
             if testo_busta.strip() else "")
    return (f"<div style=\"font-family:{FONT_PAGINA};background:{colore}12;border:1px solid {colore}55;border-left:4px solid {colore};"
            f"border-radius:10px;padding:12px 16px;margin:0 0 20px 0;color:{P['testo']};font-size:12.5px\">"
            f"<div style='font-weight:700;color:{colore};font-size:13px;margin-bottom:6px'>&#10003;&nbsp; {e(titolo)}"
            f"{' — ' + e(info['errore']) if info.get('errore') else ''}</div>"
            f"<table style='border-collapse:collapse;font-size:12.5px'>{righe}</table>{busta}</div>")

# ---------- costruzione della pagina ----------
def _immagini_cid(msg):
    immagini = {}
    for part in msg.walk():
        if part.get_content_maintype() == 'image' and part.get('Content-ID'):
            dati = part.get_payload(decode=True)
            if dati:
                immagini[part['Content-ID'].strip().strip('<>')] = \
                    f"data:{part.get_content_type()};base64,{base64.b64encode(dati).decode('ascii')}"
    return immagini

def _corpo(msg):
    """(tipo, testo) del corpo principale, senza scendere negli allegati (es. postacert.eml)."""
    try:
        parte = msg.get_body(preferencelist=('html', 'plain'))
    except Exception:
        parte = None
    if parte is None:
        for p in msg.walk():
            if p.get_content_type() in ("text/html", "text/plain") and p.get_content_disposition() != "attachment":
                parte = p
                break
    if parte is None:
        return "plain", ""
    return ("html" if parte.get_content_type() == "text/html" else "plain"), testo_parte(parte)

def _contenuto_body(documento):
    """Parte tra <body> e </body> di un documento HTML (per inserirlo dentro un'altra pagina)."""
    m = re.search(r"<body[^>]*>(.*)</body>", documento, re.I | re.S)
    corpo = m.group(1) if m else re.sub(r"(?is)<(?:!doctype|html|/html|head).*?>|<head>.*?</head>", "", documento)
    return re.sub(r"(?is)<script.*?</script>", "", corpo)

def _corpo_elaborato(msg):
    tipo, testo = _corpo(msg)
    immagini = _immagini_cid(msg)
    if tipo == "html":
        for cid, uri in immagini.items():
            testo = testo.replace(f"cid:{cid}", uri)
        return "html", html_con_storico(testo)
    return "plain", f"<div style=\"font-family:{FONT_PAGINA};font-size:14px;line-height:1.5\">{testo_con_storico(testo)}</div>"

def _messaggio_interno(part, livello):
    """Messaggio originale contenuto in postacert.eml, mostrato dentro la busta come in una casella PEC."""
    try:
        interno = part.get_payload()[0] if part.get_content_type() == "message/rfc822" else \
            email.message_from_bytes(part.get_payload(decode=True) or b"", policy=policy.default)
    except Exception:
        return ""
    campi = [("Da", str(interno.get('From', '') or '')), ("Data", data_da_msg(interno)), ("A", str(interno.get('To', '') or '')),
             ("Cc", str(interno.get('Cc', '') or '')), ("Oggetto", str(interno.get('Subject', '') or ''))]
    tipo, corpo = _corpo_elaborato(interno)
    if tipo == "html":
        corpo = _contenuto_body(corpo)
    pec_interna = info_pec(interno) if livello < 2 else None
    extra = _messaggio_interno(pec_interna["postacert"], livello + 1) if pec_interna and pec_interna["postacert"] is not None else ""
    return blocco_intestazione(campi, "Messaggio originale certificato", colore=P["ok"]) + corpo + extra

def costruisci_html_mail(msg, data_formattata):
    """Pagina completa della mail: intestazione, eventuale fascia PEC, corpo con lo storico a separatori."""
    pec = info_pec(msg)
    testata = intestazione_principale(msg, data_formattata, colore=P["ok"] if pec else None)
    tipo, corpo = _corpo_elaborato(msg)
    if pec:
        if pec["postacert"] is not None and pec["tipo"] in ("posta-certificata", ""):
            # busta di trasporto: come in una casella PEC si legge il messaggio originale; il testo della busta va nella fascia
            _t, testo_busta = _corpo(msg)
            testo_busta = _testo_da_html(testo_busta) if _t == "html" else testo_busta
            testata += blocco_pec(pec, testo_busta) + _messaggio_interno(pec["postacert"], 1)
            tipo, corpo = "plain", ""
        else:
            testata += blocco_pec(pec)
    if tipo == "html":
        documento = corpo
        if re.search(r"<head[^>]*>", documento, re.I):
            documento = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + STILE_BASE_PAGINA, documento, count=1, flags=re.I)
        else:
            documento = STILE_BASE_PAGINA + documento
        m = re.search(r"<body[^>]*>", documento, re.I)
        if m:
            return documento[:m.end()] + testata + documento[m.end():]
        return testata + documento
    return (f"<html lang='it'><head><meta charset='utf-8'>{STILE_BASE_PAGINA}</head>"
            f"<body style=\"margin:0;padding:22px;background:{P['foglio']};color:{P['testo']};font-family:{FONT_PAGINA};"
            f"font-size:14px;line-height:1.5\">{testata}{corpo}</body></html>")

def html_avviso(titolo, testo="", nome_icona="busta", colore=None):
    """Pagina d'appoggio dell'anteprima (nessuna mail selezionata, file mancante...), chiara come il foglio della mail."""
    colore = colore or P["accento"]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="56" height="56"><path d="{_TRACCIATI.get(nome_icona, "")}" '
           f'fill="none" stroke="{colore}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return (f"<html lang='it'><body style=\"margin:0;height:100vh;display:flex;align-items:center;justify-content:center;"
            f"background:{P['foglio']};color:{P['tenue']};font-family:{FONT_PAGINA}\">"
            f"<div style='text-align:center;max-width:420px;padding:20px'>{svg}"
            f"<div style='color:{P['testo']};font-size:17px;font-weight:600;margin:14px 0 6px'>{html.escape(titolo)}</div>"
            f"<div style='font-size:13px;line-height:1.5'>{html.escape(testo)}</div></div></body></html>")

# ==========================================
# FORMATI DI EXPORT: RICONOSCIMENTO E CONVERSIONE IN UNA CARTELLA DI .EML
# Tutti i formati vengono convertiti in una cartella di file .eml (una sottocartella per ogni casella):
# così indicizzazione, ricerca, anteprima ed esportazione funzionano allo stesso modo per tutti.
# ==========================================
try:
    import olefile                      # Outlook .msg (puro Python)
    OLEFILE_OK = True
except Exception:
    olefile = None
    OLEFILE_OK = False
try:
    import pypff                        # Outlook .pst/.ost (libpff-python)
    PYPFF_OK, PYPFF_ERRORE = True, ""
except Exception as _err_pff:
    pypff = None
    PYPFF_OK, PYPFF_ERRORE = False, f"{type(_err_pff).__name__}: {_err_pff}"

NOME_DB = "zimbra_index.db"
ESTENSIONI_ARCHIVIO = ('.tgz', '.tar.gz', '.tar', '.zip')
ESTENSIONI_FIRMATI = ('.p7m', '.p7s', '.pdf', '.xml')
ESTENSIONI_VERIFICA = ESTENSIONI_FIRMATI
ESTENSIONI_PST = ('.pst', '.ost')
_NON_MBOX = {'.msf', '.dat', '.json', '.sqlite', '.db', '.html', '.htm', '.txt', '.ini', '.js', '.log', '.xml',
             '.pdf', '.jpg', '.png', '.gif', '.eml', '.emlx', '.msg', '.pst', '.ost', '.zip', '.tgz', '.gz', '.tar'}

def e_archivio(percorso):
    return percorso.lower().endswith(ESTENSIONI_ARCHIVIO)

def e_file_mbox(percorso):
    """Un file mbox (Gmail, Thunderbird, Apple Mail...) inizia con una riga "From ..."."""
    try:
        if os.path.splitext(percorso)[1].lower() in _NON_MBOX or os.path.getsize(percorso) < 20:
            return False
        with open(percorso, 'rb') as f:
            return f.read(64).lstrip(b"\xef\xbb\xbf\r\n").startswith(b"From ")
    except OSError:
        return False

def e_cartella_maildir(d):
    return os.path.isdir(os.path.join(d, "cur")) and os.path.isdir(os.path.join(d, "new"))

def contiene_eml(cartella):
    if os.path.exists(os.path.join(cartella, NOME_DB)):
        return True
    for _r, _d, files in os.walk(cartella):
        if any(f.lower().endswith('.eml') for f in files):
            return True
    return False

def cerca_sorgenti(cartella):
    """Caselle convertibili dentro una cartella: [(tipo, percorso, cartella_logica)]."""
    trovate = []
    for radice, dirs, files in os.walk(cartella):
        dirs.sort()
        rel = os.path.relpath(radice, cartella).replace('\\', '/')
        rel = "" if rel == "." else rel
        if e_cartella_maildir(radice):
            base = os.path.basename(radice)
            # Maildir++ (Dovecot): la casella principale è la posta in arrivo, le sottocartelle sono ".Sent", ".Lavoro.Clienti"
            nome = base[1:].replace('.', '/') if base.startswith('.') and len(base) > 1 else "Posta in arrivo"
            for sub in ("cur", "new"):
                for f in sorted(os.listdir(os.path.join(radice, sub))):
                    trovate.append(("maildir", os.path.join(radice, sub, f), nome))
            dirs[:] = [d for d in dirs if d not in ("cur", "new", "tmp")]
        for f in sorted(files):
            p = os.path.join(radice, f)
            ext = os.path.splitext(f)[1].lower()
            logica = _cartella_logica(rel)
            if ext == '.emlx':
                trovate.append(("emlx", p, logica))
            elif ext == '.msg':
                trovate.append(("msg", p, logica))
            elif ext in ESTENSIONI_PST:
                trovate.append(("pst", p, logica))
            elif e_file_mbox(p):
                # Thunderbird: "Inbox" dentro "Local Folders"; Apple: "Casella.mbox/mbox"; Gmail: "Tutti i messaggi.mbox"
                nome = os.path.splitext(f)[0] if ext == '.mbox' else f
                if f == "mbox" and radice.lower().endswith(".mbox"):
                    nome = ""
                trovate.append(("mbox", p, "/".join(x for x in (logica, nome) if x)))
    return trovate

def _cartella_logica(rel):
    """Percorso di cartella leggibile: toglie le estensioni tecniche (.sbd di Thunderbird, .mbox di Apple)."""
    parti = []
    for p in rel.split('/'):
        if not p or p.lower() in ("messages", "data") or re.fullmatch(r'[0-9A-Fa-f-]{36}', p) or p.isdigit():
            continue
        for ext in (".sbd", ".mbox", ".imapmbox", ".mbx"):
            if p.lower().endswith(ext):
                p = p[:-len(ext)]
        if p:
            parti.append(p)
    return "/".join(parti)

def rileva_sorgente(percorso):
    """Cosa è stato aperto? -> (tipo, descrizione). tipo None = non riconosciuto."""
    if os.path.isdir(percorso):
        if contiene_eml(percorso):
            return "cartella_eml", "cartella di mail .eml (export Zimbra, Carbonio o simile)"
        sorgenti = cerca_sorgenti(percorso)
        if sorgenti:
            conta = {}
            for t, _p, _c in sorgenti:
                conta[t] = conta.get(t, 0) + 1
            nomi = {"mbox": "caselle mbox", "emlx": "mail Apple (.emlx)", "maildir": "mail Maildir",
                    "msg": "mail Outlook (.msg)", "pst": "file Outlook (.pst/.ost)"}
            return "cartella_da_convertire", ", ".join(f"{n} {nomi[t]}" for t, n in conta.items())
        if contiene_pim(percorso):
            return "cartella_eml", "cartella con calendario, contatti o altri dati"
        return None, "nessuna mail riconoscibile nella cartella"
    if not os.path.isfile(percorso):
        return None, "percorso inesistente"
    basso = percorso.lower()
    if basso.endswith('.eml'):
        return "eml", "singola mail"
    if basso.endswith('.msg'):
        return "msg", "singola mail Outlook"
    if basso.endswith('.emlx'):
        return "emlx", "singola mail Apple"
    if supportato(os.path.basename(basso)):
        return "firmato", "documento da verificare"
    if e_archivio(basso):
        return "archivio", "archivio compresso"
    if basso.endswith(ESTENSIONI_PST):
        return "pst", "file dati di Outlook"
    if basso.endswith('.mbox') or e_file_mbox(percorso):
        return "mbox", "casella mbox"
    if basso.endswith(('.ics', '.ical', '.icalendar', '.vcs', '.ifb')):
        return "pim", "calendario o attività (.ics)"
    if basso.endswith(('.vcf', '.vcard')):
        return "pim", "rubrica (.vcf)"
    if basso.endswith('.csv'):
        try:
            with open(percorso, 'rb') as f:
                if elementi_csv_contatti(f.read(65536)):
                    return "pim", "rubrica (.csv)"
        except OSError:
            pass
    return None, "formato non supportato"

# ---------- etichette Gmail (Google Takeout) ----------
_GMAIL_SISTEMA = {"inbox": "Posta in arrivo", "posta in arrivo": "Posta in arrivo",
                  "sent": "Posta inviata", "inviati": "Posta inviata", "posta inviata": "Posta inviata",
                  "drafts": "Bozze", "bozze": "Bozze", "spam": "Spam", "trash": "Cestino", "cestino": "Cestino",
                  "chat": "Chat"}
_GMAIL_IGNORATE = {"opened", "aperti", "aperte", "unread", "da leggere", "non letti", "important", "importanti",
                   "starred", "speciali", "archived", "archiviati", "sent messages"}
_GMAIL_PRIORITA = ["Cestino", "Spam", "Bozze", "Posta inviata"]

def cartella_gmail(valore_intestazione):
    """Sceglie la cartella di una mail di Google Takeout dalle sue etichette (X-Gmail-Labels)."""
    try:
        testo = str(email.header.make_header(email.header.decode_header(valore_intestazione)))
    except Exception:
        testo = valore_intestazione
    try:
        etichette = [e.strip() for e in next(csv.reader([testo])) if e.strip()]
    except Exception:
        etichette = [e.strip() for e in testo.split(',') if e.strip()]
    sistema, utente = set(), []
    for e in etichette:
        b = e.lower()
        if b in _GMAIL_SISTEMA:
            sistema.add(_GMAIL_SISTEMA[b])
        elif b not in _GMAIL_IGNORATE and not b.startswith(("categor", "imap")):
            utente.append(e)
    for s in _GMAIL_PRIORITA:
        if s in sistema:
            return s
    if utente:
        return utente[0]
    if "Posta in arrivo" in sistema:
        return "Posta in arrivo"
    if "Chat" in sistema:
        return "Chat"
    return "Archivio"

def _intestazione_grezza(dati, nome):
    """Valore di un'intestazione letto direttamente dai byte (veloce, senza analizzare tutta la mail)."""
    fine = dati.find(b"\n\n")
    fine2 = dati.find(b"\r\n\r\n")
    fine = min(x for x in (fine, fine2, len(dati)) if x >= 0)
    m = re.search(rb'(?im)^' + re.escape(nome.encode()) + rb':[ \t]*(.*(?:\r?\n[ \t].*)*)', dati[:fine])
    if not m:
        return None
    return re.sub(rb'\r?\n[ \t]+', b' ', m.group(1)).decode('utf-8', 'replace').strip()

# ---------- Outlook .msg (formato OLE/CFB) ----------
_LZFU_PREBUF = (b"{\\rtf1\\ansi\\mac\\deff0\\deftab720{\\fonttbl;}{\\f0\\fnil \\froman \\fswiss \\fmodern \\fscript "
                b"\\fdecor MS Sans SerifSymbolArialTimes New RomanCourier{\\colortbl\\red0\\green0\\blue0\r\n\\par "
                b"\\pard\\plain\\f0\\fs20\\b\\i\\u\\tab\\tx")

def decomprimi_rtf(dati):
    """RTF compresso di Outlook (LZFu, MS-OXRTFCP)."""
    if len(dati) < 16:
        return b""
    _comp, grezzo, magia, _crc = struct.unpack('<IIII', dati[:16])
    if magia == 0x414C454D:                  # "MELA": non compresso
        return dati[16:16 + grezzo]
    if magia != 0x75465A4C:                  # "LZFu"
        return b""
    diz = bytearray(4096)
    diz[:len(_LZFU_PREBUF)] = _LZFU_PREBUF
    scrivi = len(_LZFU_PREBUF)
    out = bytearray()
    pos = 16
    while pos < len(dati) and len(out) < grezzo:
        flag = dati[pos]
        pos += 1
        for bit in range(8):
            if pos >= len(dati):
                break
            if flag & (1 << bit):
                if pos + 1 >= len(dati):
                    return bytes(out)
                rif = (dati[pos] << 8) | dati[pos + 1]
                pos += 2
                off, lung = rif >> 4, (rif & 0xF) + 2
                if off == scrivi % 4096:
                    return bytes(out)
                for i in range(lung):
                    c = diz[(off + i) % 4096]
                    out.append(c)
                    diz[scrivi % 4096] = c
                    scrivi += 1
            else:
                c = dati[pos]
                pos += 1
                out.append(c)
                diz[scrivi % 4096] = c
                scrivi += 1
    return bytes(out)

def rtf_in_testo(rtf):
    """Testo semplice da un RTF (per le rare mail che hanno solo il corpo RTF)."""
    testo = rtf.decode('latin-1', 'replace') if isinstance(rtf, (bytes, bytearray)) else rtf
    cp = re.search(r'\\ansicpg(\d+)', testo)
    codifica = f"cp{cp.group(1)}" if cp else "cp1252"
    out, profondita_saltata, pila = [], None, []
    i, n = 0, len(testo)
    while i < n:
        c = testo[i]
        if c == '{':
            pila.append(profondita_saltata)
            i += 1
            if testo.startswith('\\*', i) or re.match(r'\\(fonttbl|colortbl|stylesheet|info|pict|object|themedata|header|footer)\b', testo[i:i + 12]):
                profondita_saltata = profondita_saltata if profondita_saltata is not None else len(pila)
            continue
        if c == '}':
            if profondita_saltata is not None and len(pila) <= profondita_saltata:
                profondita_saltata = None
            if pila:
                pila.pop()
            i += 1
            continue
        if c == '\\':
            m = re.match(r"\\'([0-9a-fA-F]{2})|\\([a-zA-Z]+)(-?\d+)? ?|\\(.)", testo[i:])
            if not m:
                i += 1
                continue
            i += m.end()
            if profondita_saltata is not None:
                continue
            if m.group(1):
                try:
                    out.append(bytes([int(m.group(1), 16)]).decode(codifica, 'replace'))
                except LookupError:
                    out.append(bytes([int(m.group(1), 16)]).decode('cp1252', 'replace'))
            elif m.group(2):
                w = m.group(2)
                if w in ('par', 'line'):
                    out.append('\n')
                elif w == 'tab':
                    out.append('\t')
                elif w == 'u' and m.group(3):
                    out.append(chr(int(m.group(3)) % 65536))
                    if i < n and testo[i] == '?':
                        i += 1
            elif m.group(4) in '\\{}':
                out.append(m.group(4))
            continue
        if profondita_saltata is None and c not in '\r\n':
            out.append(c)
        i += 1
    return re.sub(r'\n{3,}', '\n\n', "".join(out)).strip()

def _decodifica_corpo(dati):
    if dati is None:
        return ""
    if isinstance(dati, str):
        return dati
    m = re.search(rb'charset=["\']?([A-Za-z0-9_\-]+)', dati[:3000])
    for cod in ([m.group(1).decode('ascii', 'ignore')] if m else []) + ['utf-8', 'cp1252']:
        try:
            return dati.decode(cod)
        except (UnicodeDecodeError, LookupError):
            continue
    return dati.decode('latin-1', 'replace')

_INTESTAZIONI_DA_COPIARE = ("From", "Sender", "To", "Cc", "Bcc", "Reply-To", "Date", "Subject", "Message-ID",
                            "In-Reply-To", "References", "X-Mailer")

def costruisci_eml(intestazioni_trasporto=None, oggetto="", mittente="", a="", cc="", data=None,
                   testo=None, html_corpo=None, rtf=None, allegati=(), message_id=""):
    """Mail RFC 822 a partire dai campi di Outlook.
    allegati: [(nome, dati, mime, content_id)]; dati può essere un EmailMessage (mail allegata).
    Gli allegati con Content-ID citati nell'HTML diventano immagini incorporate (non compaiono tra gli allegati)."""
    msg = EmailMessage()
    usati = set()
    if intestazioni_trasporto:
        try:
            h = email.parser.HeaderParser(policy=policy.compat32).parsestr(intestazioni_trasporto.strip() + "\n\n")
            for k in _INTESTAZIONI_DA_COPIARE:
                v = h.get(k)
                if v:
                    _imposta_intestazione(msg, k, str(v))
                    usati.add(k)
        except Exception:
            pass
    for k, v in (("Subject", oggetto), ("From", mittente), ("To", a), ("Cc", cc), ("Message-ID", message_id)):
        if v and k not in usati:
            _imposta_intestazione(msg, k, v)
    if "Date" not in usati and data is not None:
        try:
            _imposta_intestazione(msg, "Date", email.utils.format_datetime(
                data if data.tzinfo else data.replace(tzinfo=timezone.utc)))
        except Exception:
            pass
    if not testo and not html_corpo and rtf:
        testo = rtf_in_testo(rtf)
    if html_corpo:
        msg.set_content(testo or "")
        msg.add_alternative(html_corpo, subtype="html")
    else:
        msg.set_content(testo or "")
    for nome, dati, mime, cid in allegati:
        try:
            if isinstance(dati, EmailMessage):
                msg.add_attachment(dati, filename=nome)
            else:
                tipo = (mime or mimetypes.guess_type(nome)[0] or "application/octet-stream").split('/', 1)
                if len(tipo) != 2 or tipo[0] in ("multipart", "text", "message"):
                    tipo = ["application", "octet-stream"]
                cid = str(cid or "").strip().strip('<>')
                if cid and html_corpo and f"cid:{cid}" in html_corpo:
                    msg.add_attachment(bytes(dati), maintype=tipo[0], subtype=tipo[1], filename=nome,
                                       disposition="inline", cid=f"<{cid}>")
                else:
                    msg.add_attachment(bytes(dati), maintype=tipo[0], subtype=tipo[1], filename=nome)
        except Exception:
            continue
    return msg

def _imposta_intestazione(msg, k, v):
    v = " ".join(str(v).split())
    try:
        msg[k] = v
    except Exception:
        try:
            msg[k] = v.encode('ascii', 'replace').decode('ascii')
        except Exception:
            pass

def msg_bytes(msg):
    try:
        return msg.as_bytes()
    except Exception:
        return msg.as_bytes(policy=policy.compat32)

class LettoreMsg:
    """Converte un .msg di Outlook in EmailMessage leggendo direttamente la struttura OLE (serve olefile)."""

    def __init__(self, sorgente):
        if not OLEFILE_OK:
            raise RuntimeError("libreria 'olefile' non installata: i file .msg non si possono leggere")
        self.ole = olefile.OleFileIO(sorgente)

    def chiudi(self):
        try:
            self.ole.close()
        except Exception:
            pass

    def _stream(self, nome):
        try:
            if self.ole.exists(nome):
                return self.ole.openstream(nome).read()
        except Exception:
            pass
        return None

    def _prop(self, base, pid):
        """Proprietà stringa o binaria (da stream __substg1.0_PPPPTTTT)."""
        for tipo in ("001F", "001E", "0102"):
            dati = self._stream(f"{base}__substg1.0_{pid:04X}{tipo}")
            if dati is None:
                continue
            if tipo == "001F":
                return dati.decode('utf-16-le', 'replace').rstrip('\x00')
            if tipo == "001E":
                return dati.decode('cp1252', 'replace').rstrip('\x00')
            return dati
        return None

    def _fisse(self, base, intestazione):
        """Proprietà a dimensione fissa (date, interi) dello stream __properties_version1.0."""
        dati = self._stream(f"{base}__properties_version1.0") or b""
        out = {}
        for pos in range(intestazione, len(dati) - 15, 16):
            tag, _flag, valore = struct.unpack('<II8s', dati[pos:pos + 16])
            tipo, pid = tag & 0xFFFF, tag >> 16
            if tipo == 0x0040:                # PT_SYSTIME (FILETIME)
                ft = struct.unpack('<Q', valore)[0]
                if ft:
                    try:
                        out[pid] = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ft // 10)
                    except OverflowError:
                        pass
            elif tipo in (0x0003, 0x000B):    # intero / booleano
                out[pid] = struct.unpack('<i', valore[:4])[0]
        return out

    def _sotto(self, base, prefisso):
        visti = set()
        for voce in self.ole.listdir(streams=True, storages=True):
            percorso = "/".join(voce)
            if percorso.startswith(base) and len(voce) > base.count('/'):
                nome = voce[base.count('/')]
                if nome.startswith(prefisso) and nome not in visti:
                    visti.add(nome)
        return sorted(visti)

    def leggi(self, base="", annidato=False):
        p = lambda pid: self._prop(base, pid)
        fisse = self._fisse(base, 24 if annidato else 32)
        destinatari = {1: [], 2: [], 3: []}
        for r in self._sotto(base, "__recip_version1.0_"):
            rb = f"{base}{r}/"
            nome = self._prop(rb, 0x3001) or ""
            indirizzo = self._prop(rb, 0x39FE) or self._prop(rb, 0x3003) or ""
            if isinstance(indirizzo, bytes):
                indirizzo = ""
            tipo = self._fisse(rb, 8).get(0x0C15, 1)
            if '@' not in indirizzo:
                indirizzo = ""
            destinatari.setdefault(tipo, []).append(email.utils.formataddr((nome, indirizzo)) if indirizzo else nome)
        allegati = []
        for a in self._sotto(base, "__attach_version1.0_"):
            ab = f"{base}{a}/"
            nome = self._prop(ab, 0x3707) or self._prop(ab, 0x3704) or self._prop(ab, 0x3001) or "allegato"
            if isinstance(nome, bytes):
                nome = "allegato"
            mime = self._prop(ab, 0x370E)
            cid = self._prop(ab, 0x3712)
            dati = self._stream(f"{ab}__substg1.0_37010102")
            if dati is not None:
                allegati.append((nome, dati, mime if isinstance(mime, str) else None, cid if isinstance(cid, str) else None))
            elif self.ole.exists(f"{ab}__substg1.0_3701000D"):
                interno = self.leggi(f"{ab}__substg1.0_3701000D/", annidato=True)
                nome_eml = nome if nome.lower().endswith(('.eml', '.msg')) else nome + ".eml"
                allegati.append((os.path.splitext(nome_eml)[0] + ".eml", interno, None, None))
        mittente_nome = p(0x0C1A) or p(0x0042) or ""
        mittente_ind = p(0x5D01) or p(0x0C1F) or p(0x0065) or ""
        if isinstance(mittente_ind, bytes) or '@' not in str(mittente_ind):
            mittente_ind = ""
        html_corpo = p(0x1013)
        rtf = p(0x1009)
        return costruisci_eml(
            intestazioni_trasporto=p(0x007D) if isinstance(p(0x007D), str) else None,
            oggetto=p(0x0037) or "", mittente=email.utils.formataddr((mittente_nome, mittente_ind)) if mittente_ind else mittente_nome,
            a=", ".join(destinatari.get(1, [])) or (p(0x0E04) or ""), cc=", ".join(destinatari.get(2, [])) or (p(0x0E03) or ""),
            data=fisse.get(0x0039) or fisse.get(0x0E06), testo=p(0x1000) if isinstance(p(0x1000), str) else None,
            html_corpo=_decodifica_corpo(html_corpo) if html_corpo else None,
            rtf=decomprimi_rtf(rtf) if isinstance(rtf, bytes) else None,
            allegati=allegati, message_id=p(0x1035) or "")

def _msg_nominate(lettore):
    """Proprietà con nome di un .msg: {LID: id della proprietà 0x8000+} (solo quelle numeriche)."""
    dati = lettore._stream("__nameid_version1.0/__substg1.0_00030102") or b""
    mappa = {}
    for pos in range(0, len(dati) - 7, 8):
        ident, info = struct.unpack('<II', dati[pos:pos + 8])
        if info & 1 == 0:                       # numerica: ident = LID
            mappa[ident] = 0x8000 + (info >> 16)
    return mappa


_PROP_CONTATTO = (0x3001, 0x3A06, 0x3A11, 0x3A16, 0x3A17, 0x3A1C, 0x3A08, 0x3A09, 0x3A24, 0x3A1F, 0x3A29, 0x3A2A,
                  0x3A27, 0x3A28, 0x3A26, 0x3A5D, 0x3A5B, 0x3A59, 0x3A5C, 0x3A5A, 0x3A51)


def msg_pim(sorgente):
    """.msg di calendario, attività, contatto o nota -> (estensione, byte) oppure None se è una mail."""
    if not OLEFILE_OK:
        return None
    lettore = LettoreMsg(sorgente)
    try:
        classe = lettore._prop("", 0x001A)
        tipo = tipo_classe_outlook(classe if isinstance(classe, str) else "")
        if tipo is None:
            return None
        prop_str = {pid: v for pid in _PROP_CONTATTO for v in [lettore._prop("", pid)] if isinstance(v, str)}
        fisse = lettore._fisse("", 32)
        nominate = {}
        for lid, pid in _msg_nominate(lettore).items():
            v = lettore._prop("", pid)
            if isinstance(v, str):
                nominate[lid] = v
                prop_str[pid] = v
            elif pid in fisse:
                nominate[lid] = fisse[pid]
        oggetto = lettore._prop("", 0x0037)
        corpo = lettore._prop("", 0x1000)
        return pim_outlook(tipo, prop_str, fisse, nominate, oggetto if isinstance(oggetto, str) else "",
                           corpo if isinstance(corpo, str) else "")
    finally:
        lettore.chiudi()


def msg_in_eml(sorgente):
    lettore = LettoreMsg(sorgente)
    try:
        return msg_bytes(lettore.leggi())
    finally:
        lettore.chiudi()

def emlx_in_eml(dati):
    """Apple Mail .emlx: prima riga = lunghezza del messaggio, poi il messaggio, poi metadati plist."""
    riga, _sep, resto = dati.partition(b"\n")
    try:
        return resto[:int(riga.strip())]
    except ValueError:
        return dati

# ---------- Outlook .pst / .ost (libpff) ----------
def _pff_entry(item, tipi):
    """Valore di una proprietà MAPI di un elemento pypff (cerca nei record set)."""
    try:
        for rs in item.record_sets:
            for e in rs.entries:
                if e.entry_type in tipi:
                    try:
                        return e.data_as_string
                    except Exception:
                        try:
                            return e.data_as_integer
                        except Exception:
                            return e.data
    except Exception:
        pass
    return None

def _pff_val(oggetto, nome):
    try:
        return getattr(oggetto, nome)
    except Exception:
        return None

def _pff_pim(m):
    """Elemento di un .pst/.ost che non è una mail -> (estensione, byte) oppure None."""
    classe = _pff_entry(m, (0x001A,))
    tipo = tipo_classe_outlook(classe if isinstance(classe, str) else "")
    if tipo is None:
        return None
    prop_str, prop_data = {}, {}
    try:
        for rs in m.record_sets:
            for e in rs.entries:
                try:
                    vt = e.value_type
                    if vt in (0x001F, 0x001E):
                        prop_str[e.entry_type] = e.data_as_string
                    elif vt == 0x0040:
                        prop_data[e.entry_type] = e.data_as_datetime
                except Exception:
                    continue
    except Exception:
        pass
    corpo = _decodifica_corpo(_pff_val(m, "plain_text_body")) or ""
    return pim_outlook(tipo, prop_str, prop_data, {}, _pff_val(m, "subject") or "", corpo)


def _pff_messaggio(m, profondita=0):
    destinatari = {1: [], 2: [], 3: []}
    try:
        rec = m.recipients
        for rs in (rec.record_sets if rec is not None else []):
            valori = {}
            for e in rs.entries:
                try:
                    valori[e.entry_type] = e.data_as_integer if e.entry_type == 0x0C15 else e.data_as_string
                except Exception:
                    pass
            ind = valori.get(0x39FE) or valori.get(0x3003) or ""
            nome = valori.get(0x3001) or ""
            voce = email.utils.formataddr((nome, ind)) if '@' in str(ind) else nome
            if voce:
                destinatari.setdefault(valori.get(0x0C15, 1), []).append(voce)
    except Exception:
        pass
    allegati = []
    for i in range(_pff_val(m, "number_of_attachments") or 0):
        try:
            a = m.get_attachment(i)
            nome = _pff_val(a, "long_filename") or _pff_entry(a, (0x3707, 0x3704, 0x3001)) or f"allegato_{i + 1}"
            dim = _pff_val(a, "size") or 0
            if dim:
                allegati.append((str(nome), a.read_buffer(dim), _pff_entry(a, (0x370E,)), _pff_entry(a, (0x3712,))))
            elif profondita < 3 and (_pff_val(a, "number_of_sub_items") or 0):
                interno = _pff_messaggio(a.get_sub_item(0), profondita + 1)
                allegati.append((os.path.splitext(str(nome))[0] + ".eml", interno, None, None))
        except Exception:
            continue
    mittente = _pff_val(m, "sender_name") or ""
    ind = _pff_entry(m, (0x5D01, 0x0C1F, 0x0065))
    if ind and '@' in str(ind):
        mittente = email.utils.formataddr((mittente, ind))
    return costruisci_eml(
        intestazioni_trasporto=_pff_val(m, "transport_headers"), oggetto=_pff_val(m, "subject") or "",
        mittente=mittente, a=", ".join(destinatari.get(1, [])) or (_pff_entry(m, (0x0E04,)) or ""),
        cc=", ".join(destinatari.get(2, [])) or (_pff_entry(m, (0x0E03,)) or ""),
        data=_pff_val(m, "client_submit_time") or _pff_val(m, "delivery_time"),
        testo=_decodifica_corpo(_pff_val(m, "plain_text_body")) or None,
        html_corpo=_decodifica_corpo(_pff_val(m, "html_body")) or None,
        rtf=_pff_val(m, "rtf_body"), allegati=allegati)

# ---------- motore di conversione ----------
class ConvertitorePosta:
    """Converte qualsiasi sorgente supportata in file .eml dentro 'dest' (una sottocartella per casella).
    avanzamento(frazione 0..1, testo) e annullato() sono richiamati periodicamente."""

    def __init__(self, dest, avanzamento=None, annullato=None):
        self.dest = dest
        self._avanz = avanzamento or (lambda f, t: None)
        self._annullato = annullato or (lambda: False)
        self._numeri = {}
        self.convertite = 0
        self.errori = []

    def _cartella(self, logica):
        parti = [nome_windows_sicuro(p, 60, "Senza nome", con_estensione=False)
                 for p in str(logica or "").replace('\\', '/').split('/') if p.strip()] or ["Posta"]
        d = os.path.join(self.dest, *parti)
        os.makedirs(d, exist_ok=True)
        return d

    def scrivi(self, logica, dati):
        d = self._cartella(logica)
        n = self._numeri.get(d, 0)
        while True:
            n += 1
            p = os.path.join(d, f"{n:06d}.eml")
            if not os.path.exists(p):
                break
        self._numeri[d] = n
        with open(p, 'wb') as f:
            f.write(dati)
        self.convertite += 1

    def scrivi_file(self, logica, estensione, dati):
        """Elemento non di posta (calendario, attività, contatto, nota) salvato come .ics / .vcf."""
        d = self._cartella(logica)
        n = self._numeri.get(d, 0)
        while True:
            n += 1
            p = os.path.join(d, f"{n:06d}{estensione}")
            if not os.path.exists(p):
                break
        self._numeri[d] = n
        with open(p, 'wb') as f:
            f.write(dati)
        self.elementi = getattr(self, "elementi", 0) + 1

    def mbox(self, percorso, logica, quota=(0.0, 1.0)):
        """mbox in streaming (file anche di molti GB): Gmail usa le etichette X-Gmail-Labels come cartelle."""
        totale = max(1, os.path.getsize(percorso))
        a, b = quota
        nome = os.path.basename(percorso)
        with open(percorso, 'rb') as f:
            righe, prec_vuota, contatore = [], True, 0
            for riga in f:
                if riga.startswith(b"From ") and (prec_vuota or not righe or re.search(rb'\d{1,2}:\d{2}:\d{2}', riga)):
                    if righe:
                        self._mbox_messaggio(righe, logica)
                    righe, prec_vuota = [], False
                    contatore += 1
                    if contatore % 200 == 0:
                        if self._annullato():
                            return
                        self._avanz(a + (b - a) * f.tell() / totale, f"{nome}: {self.convertite} mail convertite")
                    continue
                if riga.startswith(b">") and re.match(rb'^>+From ', riga):
                    riga = riga[1:]
                righe.append(riga)
                prec_vuota = riga in (b"\n", b"\r\n")
            if righe:
                self._mbox_messaggio(righe, logica)
        self._avanz(b, f"{nome}: {self.convertite} mail convertite")

    def _mbox_messaggio(self, righe, logica):
        while righe and righe[-1] in (b"\n", b"\r\n"):
            righe.pop()
        dati = b"".join(righe)
        if not dati.strip():
            return
        etichette = _intestazione_grezza(dati, "X-Gmail-Labels")
        try:
            self.scrivi(cartella_gmail(etichette) if etichette is not None else logica, dati)
        except Exception as e:
            self.errori.append(f"mbox {logica}: {e}")

    def pst(self, percorso, quota=(0.0, 1.0)):
        if not PYPFF_OK:
            raise RuntimeError("Per leggere i file .pst/.ost serve la libreria libpff-python "
                               f"(pip install libpff-python). Dettaglio: {PYPFF_ERRORE}")
        f = pypff.file()
        f.open(percorso)
        try:
            radice = f.get_root_folder()
            totale = max(1, self._pff_conta(radice))
            fatte = [0]
            self._pff_cartella(radice, [], totale, fatte, quota, os.path.basename(percorso))
        finally:
            try:
                f.close()
            except Exception:
                pass

    def _pff_conta(self, cartella):
        n = _pff_val(cartella, "number_of_sub_messages") or 0
        for i in range(_pff_val(cartella, "number_of_sub_folders") or 0):
            try:
                n += self._pff_conta(cartella.get_sub_folder(i))
            except Exception:
                pass
        return n

    _PFF_RADICI = {"top of personal folders", "inizio file dati di outlook", "inizio delle cartelle personali",
                   "top of outlook data file", "root - mailbox", "ipm_subtree", ""}

    def _pff_cartella(self, cartella, percorso, totale, fatte, quota, nome_file):
        nome = (_pff_val(cartella, "name") or "").strip()
        if nome.lower() not in self._PFF_RADICI:
            percorso = percorso + [nome]
        logica = "/".join(percorso) or "Posta"
        a, b = quota
        for i in range(_pff_val(cartella, "number_of_sub_messages") or 0):
            if self._annullato():
                return
            try:
                m = cartella.get_sub_message(i)
                try:
                    pim = _pff_pim(m)
                except Exception:
                    pim = None                      # non riconosciuto: si converte come mail
                if pim is not None:
                    self.scrivi_file(logica, *pim)
                else:
                    self.scrivi(logica, msg_bytes(_pff_messaggio(m)))
            except Exception as e:
                self.errori.append(f"{logica} #{i + 1}: {e}")
            fatte[0] += 1
            if fatte[0] % 25 == 0:
                self._avanz(a + (b - a) * fatte[0] / totale, f"{nome_file}: {logica} ({fatte[0]}/{totale})")
        for i in range(_pff_val(cartella, "number_of_sub_folders") or 0):
            try:
                self._pff_cartella(cartella.get_sub_folder(i), percorso, totale, fatte, quota, nome_file)
            except Exception as e:
                self.errori.append(f"cartella {logica}: {e}")

    def sorgenti(self, elenco, quota=(0.0, 1.0)):
        """Converte l'elenco prodotto da cerca_sorgenti()."""
        a, b = quota
        pesi = [max(1, os.path.getsize(p)) if t in ("mbox", "pst") else 1 for t, p, _l in elenco]
        tot, fatto = max(1, sum(pesi)), 0
        for (tipo, p, logica), peso in zip(elenco, pesi):
            if self._annullato():
                return
            q = (a + (b - a) * fatto / tot, a + (b - a) * (fatto + peso) / tot)
            try:
                if tipo == "mbox":
                    self.mbox(p, logica or "Posta", q)
                elif tipo == "pst":
                    self.pst(p, q)
                else:
                    with open(p, 'rb') as f:
                        dati = f.read()
                    if tipo == "emlx":
                        dati = emlx_in_eml(dati)
                    elif tipo == "msg":
                        try:
                            pim = msg_pim(p)
                        except Exception:
                            pim = None              # non riconosciuto: si converte come mail
                        if pim is not None:
                            self.scrivi_file(logica or "Outlook", *pim)
                            fatto += peso
                            continue
                        dati = msg_in_eml(p)
                    self.scrivi(logica or "Posta", dati)
            except Exception as e:
                self.errori.append(f"{os.path.basename(p)}: {e}")
            fatto += peso
            if tipo not in ("mbox", "pst") and self.convertite % 50 == 0:
                self._avanz(a + (b - a) * fatto / tot, f"{self.convertite} mail convertite")

def estrai_archivio(percorso, dest, avanzamento=None, annullato=None):
    """Estrae .tgz/.tar.gz/.tar/.zip in 'dest' con nomi sicuri per Windows (niente percorsi fuori da dest)."""
    avanzamento = avanzamento or (lambda f, t: None)
    annullato = annullato or (lambda: False)

    def destinazione(nome_interno):
        parti = [nome_windows_sicuro(x, 120, "_") for x in nome_interno.replace('\\', '/').split('/') if x not in ("", ".", "..")]
        return os.path.join(dest, *parti) if parti else None

    if percorso.lower().endswith('.zip'):
        with zipfile.ZipFile(percorso) as z:
            voci = z.infolist()
            for i, v in enumerate(voci):
                if annullato():
                    return False
                t = destinazione(v.filename)
                if t is None:
                    continue
                if v.is_dir():
                    os.makedirs(t, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(t), exist_ok=True)
                    with z.open(v) as s, open(t, 'wb') as d:
                        shutil.copyfileobj(s, d, 1 << 20)
                if i % 20 == 0:
                    avanzamento(i / max(1, len(voci)), f"Estrazione: {os.path.basename(v.filename)}")
        return True
    with tarfile.open(percorso, "r:*") as tar:
        voci = tar.getmembers()
        for i, v in enumerate(voci):
            if annullato():
                return False
            t = destinazione(v.name)
            if t is None:
                continue
            if v.isdir():
                os.makedirs(t, exist_ok=True)
            elif v.isfile():
                os.makedirs(os.path.dirname(t), exist_ok=True)
                with tar.extractfile(v) as s, open(t, 'wb') as d:
                    shutil.copyfileobj(s, d, 1 << 20)
            if i % 20 == 0:
                avanzamento(i / max(1, len(voci)), f"Estrazione: {os.path.basename(v.name)}")
    return True

def importa_posta(sorgente, dest, avanzamento=None, annullato=None):
    """Prepara 'dest' come cartella di .eml a partire da qualunque sorgente supportata.
    Restituisce (ok, info) con info = {"convertite": n, "errori": [...], "tipo": ...}."""
    avanzamento = avanzamento or (lambda f, t: None)
    annullato = annullato or (lambda: False)
    os.makedirs(dest, exist_ok=True)
    info = {"convertite": 0, "errori": [], "tipo": ""}
    conv = ConvertitorePosta(dest, avanzamento, annullato)
    if os.path.isfile(sorgente) and e_archivio(sorgente):
        info["tipo"] = "archivio"
        if not estrai_archivio(sorgente, dest, lambda f, t: avanzamento(f * 0.5, t), annullato):
            return False, info
        if contiene_eml(dest) or (contiene_pim(dest) and not cerca_sorgenti(dest)):
            avanzamento(1.0, "Estrazione completata")
            return True, info
        elenco = cerca_sorgenti(dest)
        conv.sorgenti(elenco, (0.5, 1.0))
        for _t, p, _l in elenco:                 # le copie estratte già convertite non servono più
            try:
                os.remove(p)
            except OSError:
                pass
        _rimuovi_cartelle_vuote(dest)
    elif os.path.isdir(sorgente):
        info["tipo"] = "cartella"
        conv.sorgenti(cerca_sorgenti(sorgente), (0.0, 0.95))
        copia_file_pim(sorgente, dest, conv)
    else:
        tipo, _d = rileva_sorgente(sorgente)
        info["tipo"] = tipo or ""
        if tipo == "pim":
            d = os.path.join(dest, "Calendario" if sorgente.lower().endswith(('.ics', '.ical', '.icalendar', '.vcs', '.ifb'))
                             else "Contatti")
            os.makedirs(d, exist_ok=True)
            shutil.copy2(sorgente, os.path.join(d, nome_windows_sicuro(os.path.basename(sorgente), 120, "dati")))
            conv.elementi = 1
        elif tipo == "pst":
            conv.pst(sorgente)
        elif tipo == "mbox":
            base = os.path.splitext(os.path.basename(sorgente))[0]
            conv.mbox(sorgente, base)
        else:
            raise ValueError("formato non supportato")
    info["convertite"], info["errori"] = conv.convertite, conv.errori
    info["elementi"] = getattr(conv, "elementi", 0)
    if annullato():
        return False, info
    if conv.convertite == 0 and not info["elementi"] and not contiene_eml(dest) and not contiene_pim(dest):
        raise ValueError("nessuna mail o altro dato trovato da convertire" + (f" ({conv.errori[0]})" if conv.errori else ""))
    avanzamento(1.0, f"{conv.convertite} mail pronte" + (f", {info['elementi']} altri elementi" if info["elementi"] else ""))
    return True, info


def copia_file_pim(sorgente, dest, conv=None):
    """Copia nella cartella pronta calendario, rubrica, attività, note e chat trovati nella cartella d'origine."""
    for p in cerca_file_pim(sorgente):
        rel = os.path.relpath(p, sorgente)
        parti = [nome_windows_sicuro(x, 120, "_") for x in rel.replace('\\', '/').split('/') if x not in ("", ".", "..")]
        if not parti:
            continue
        t = os.path.join(dest, "Altri dati", *parti)
        try:
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(p, t)
            if conv is not None:
                conv.elementi = getattr(conv, "elementi", 0) + 1
        except OSError as e:
            if conv is not None:
                conv.errori.append(f"{os.path.basename(p)}: {e}")

def _rimuovi_cartelle_vuote(radice):
    for r, dirs, files in os.walk(radice, topdown=False):
        if r != radice and not os.listdir(r):
            try:
                os.rmdir(r)
            except OSError:
                pass

def converti_singola_in_eml(percorso):
    """.msg o .emlx singolo -> file .eml temporaneo da aprire in una scheda."""
    basso = percorso.lower()
    if basso.endswith('.msg'):
        dati = msg_in_eml(percorso)
    else:
        with open(percorso, 'rb') as f:
            dati = emlx_in_eml(f.read())
    out = percorso_libero(cartella_temp_allegati(), os.path.splitext(os.path.basename(percorso))[0] + ".eml")
    with open(out, 'wb') as f:
        f.write(dati)
    return out

# ==========================================
# DATI PERSONALI: CALENDARIO, ATTIVITA', CONTATTI, CHAT, NOTE, FILE
# Oltre alla posta, gli export contengono agenda, rubrica, attività, chat, note e documenti. Qui si leggono:
#   standard          .ics/.ical/.vcs (eventi, attività, diario), .vcf (vCard 2.1/3.0/4.0), CSV di contatti
#   Zimbra / Carbonio .tgz REST (fmt=tgz): ogni elemento ha un .meta JSON con "type" (appointment, task, contact,
#                     chat, document, note, wiki); appuntamenti e attività stanno in .appt/.task (messaggio d'invito
#                     con la parte text/calendar), contatti nei campi "fld" dei metadati, chat in .chat (MIME)
#   Google Takeout    Calendar/*.ics, Contacts/*.vcf, Tasks/Tasks.json, Keep/*.json, Google Chat/**/messages.json
#   Microsoft         .pst/.ost e .msg di tipo IPM.Appointment, IPM.Task, IPM.Contact, IPM.StickyNote (convertiti
#                     in .ics/.vcf durante l'importazione), CSV dei contatti di Outlook
#   Apple / iCloud    .ics (Calendario, Promemoria), .vcf (Contatti)
#   Thunderbird       abook.sqlite (rubrica) e calendar-data/local.sqlite (calendario locale)
# Ogni elemento diventa un dizionario: tipo, titolo, inizio, fine, luogo, persone, testo (per la ricerca),
# campi (etichetta, valore) per il dettaglio, descrizione, messaggi (chat) e il testo originale per riesportarlo.
# ==========================================
TIPI_PIM = [  # (tipo, nome della sezione, icona)
    ("evento", "Calendario", "calendario"),
    ("attivita", "Attività", "spunta"),
    ("contatto", "Contatti", "persona"),
    ("chat", "Chat", "fumetto"),
    ("nota", "Note", "documento"),
    ("file", "File", "graffetta"),
]
NOMI_TIPI_PIM = {t: n for t, n, _i in TIPI_PIM}
ESTENSIONI_PIM = ('.ics', '.ical', '.icalendar', '.ifb', '.vcs', '.vcf', '.vcard', '.csv', '.json', '.meta',
                  '.chat', '.appt', '.task')
_TRADUZIONI_CARTELLE_PIM = {
    "calendar": "Calendario", "calendars": "Calendario", "calendario": "Calendario", "contacts": "Contatti",
    "contatti": "Contatti", "emailed contacts": "Contatti automatici", "tasks": "Attività", "attività": "Attività",
    "briefcase": "Valigetta", "valigetta": "Valigetta", "chats": "Chat", "chat": "Chat", "notebook": "Note",
    "notes": "Note", "keep": "Note", "google chat": "Chat", "reminders": "Promemoria",
}


def _cartella_pim(rel_dir):
    parti = [re.sub(r'!\d+$', '', p) for p in rel_dir.replace('\\', '/').split('/') if p and p != '.']
    if parti:
        parti[0] = _TRADUZIONI_CARTELLE_PIM.get(parti[0].lower(), parti[0])
    return "/".join(parti)


def _leggi_testo(dati):
    if isinstance(dati, str):
        return dati
    for cod in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return dati.decode(cod)
        except UnicodeDecodeError:
            continue
    return dati.decode("utf-8", "replace")


def _fmt(dt, tutto_giorno=False):
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            try:
                dt = dt.astimezone()       # ora locale del computer
            except (OverflowError, OSError, ValueError):
                pass
        return dt.strftime("%Y-%m-%d") if tutto_giorno else dt.strftime("%Y-%m-%d %H:%M")
    return str(dt)


def _da_epoca(valore):
    """Secondi o millisecondi dall'epoca -> datetime locale."""
    try:
        v = float(valore)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    if v > 1e14:
        v /= 1e6
    elif v > 1e11:
        v /= 1000.0
    try:
        return datetime.fromtimestamp(v, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _iso(valore):
    try:
        return datetime.fromisoformat(str(valore).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def nuovo_elemento(tipo, titolo="", **altri):
    e = {"tipo": tipo, "titolo": (titolo or "").strip(), "inizio": "", "fine": "", "luogo": "", "persone": "",
         "campi": [], "descrizione": "", "cartella": ""}
    e.update(altri)
    return e


def _testo_ricerca(e):
    pezzi = [e.get("titolo", ""), e.get("luogo", ""), e.get("persone", ""), e.get("descrizione", "")]
    pezzi += [str(v) for _k, v in e.get("campi", [])]
    pezzi += [f"{m.get('autore', '')} {m.get('testo', '')}" for m in e.get("messaggi", [])]
    return "\n".join(p for p in pezzi if p)[:200000]


# ---------- iCalendar (RFC 5545) ----------
def _righe_spiegate(testo):
    """Righe logiche: le righe che iniziano con spazio/tab continuano la precedente."""
    righe = []
    for r in testo.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if r[:1] in (" ", "\t") and righe:
            righe[-1] += r[1:]
        elif r.strip():
            righe.append(r)
    return righe


def _scomponi_riga(riga):
    """'NOME;PARAM=val;P2="a,b":valore' -> (NOME, {PARAM: val}, valore). I due punti tra virgolette non contano."""
    tra_virgolette, pos = False, -1
    for i, c in enumerate(riga):
        if c == '"':
            tra_virgolette = not tra_virgolette
        elif c == ':' and not tra_virgolette:
            pos = i
            break
    if pos < 0:
        return riga.upper(), {}, ""
    testa, valore = riga[:pos], riga[pos + 1:]
    parti = re.findall(r'(?:[^;"]|"[^"]*")+', testa)
    nome = parti[0].strip().upper() if parti else ""
    if "." in nome:                        # vCard: "item1.EMAIL" -> EMAIL
        nome = nome.split(".", 1)[1]
    parametri = {}
    for p in parti[1:]:
        k, _s, v = p.partition("=")
        k = k.strip().upper()
        v = v.strip().strip('"')
        if not _s:                         # vCard 2.1: "TEL;CELL;VOICE:..." -> TYPE
            parametri.setdefault("TYPE", [])
            parametri["TYPE"] = (parametri["TYPE"] if isinstance(parametri["TYPE"], list) else [parametri["TYPE"]]) + [k]
        else:
            parametri[k] = v
    return nome, parametri, valore


def _sfuggi_ics(v):
    return (v.replace("\\n", "\n").replace("\\N", "\n").replace("\\,", ",").replace("\\;", ";")
            .replace("\\:", ":").replace("\\\\", "\\"))


def _data_ics(valore, parametri):
    """-> (datetime/date-string, tutto_giorno)."""
    v = valore.strip()
    if not v:
        return None, False
    if parametri.get("VALUE", "").upper() == "DATE" or re.fullmatch(r'\d{8}', v):
        try:
            return datetime.strptime(v[:8], "%Y%m%d"), True
        except ValueError:
            return None, False
    m = re.fullmatch(r'(\d{8})T(\d{4})(\d{2})?(Z)?', v)
    if not m:
        return None, False
    try:
        dt = datetime.strptime(m.group(1) + m.group(2) + (m.group(3) or "00"), "%Y%m%d%H%M%S")
    except ValueError:
        return None, False
    if m.group(4):
        return dt.replace(tzinfo=timezone.utc), False
    tzid = parametri.get("TZID", "")
    if tzid:
        try:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(_tzid_iana(tzid)))
        except Exception:
            pass                           # fuso sconosciuto (es. nomi Windows): resta l'ora così come scritta
    return dt, False


_TZ_WINDOWS = {"w. europe standard time": "Europe/Rome", "romance standard time": "Europe/Paris",
               "central europe standard time": "Europe/Budapest", "gmt standard time": "Europe/London",
               "utc": "UTC", "eastern standard time": "America/New_York", "pacific standard time": "America/Los_Angeles",
               "central standard time": "America/Chicago"}


def _tzid_iana(tzid):
    t = tzid.strip().strip('"')
    if "/" in t and not t.startswith("/"):
        m = re.search(r'([A-Za-z_]+/[A-Za-z_]+(?:/[A-Za-z_]+)?)$', t)    # "/mozilla.org/.../Europe/Rome"
        return m.group(1) if m else t
    return _TZ_WINDOWS.get(t.lower(), t)


def _durata_ics(v):
    m = re.fullmatch(r'([+-])?P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', v.strip())
    if not m:
        return None
    segno = -1 if m.group(1) == "-" else 1
    w, d, h, mi, s = (int(x or 0) for x in m.groups()[1:])
    return segno * timedelta(weeks=w, days=d, hours=h, minutes=mi, seconds=s)


_FREQ = {"DAILY": "ogni giorno", "WEEKLY": "ogni settimana", "MONTHLY": "ogni mese", "YEARLY": "ogni anno",
         "HOURLY": "ogni ora", "MINUTELY": "ogni minuto"}
_GIORNI = {"MO": "lun", "TU": "mar", "WE": "mer", "TH": "gio", "FR": "ven", "SA": "sab", "SU": "dom"}


def _ripetizione_leggibile(rrule):
    p = dict(x.split("=", 1) for x in rrule.split(";") if "=" in x)
    testo = _FREQ.get(p.get("FREQ", "").upper(), p.get("FREQ", "").lower())
    if p.get("INTERVAL", "1") not in ("", "1"):
        testo += f" (ogni {p['INTERVAL']})"
    if p.get("BYDAY"):
        testo += " · " + ", ".join(_GIORNI.get(g[-2:], g) for g in p["BYDAY"].split(","))
    if p.get("COUNT"):
        testo += f" · {p['COUNT']} volte"
    if p.get("UNTIL"):
        d, _t = _data_ics(p["UNTIL"], {})
        testo += f" · fino al {_fmt(d, True) if d else p['UNTIL']}"
    return testo


def _persona_ics(valore, parametri):
    nome = parametri.get("CN", "").strip('"')
    ind = re.sub(r'(?i)^mailto:', '', valore.strip())
    return f"{nome} <{ind}>" if nome and ind and nome != ind else (nome or ind)


_STATO_ICS = {"CONFIRMED": "confermato", "TENTATIVE": "provvisorio", "CANCELLED": "annullato",
              "NEEDS-ACTION": "da fare", "COMPLETED": "completata", "IN-PROCESS": "in corso"}
_PARTECIPAZIONE = {"ACCEPTED": "accettato", "DECLINED": "rifiutato", "TENTATIVE": "forse",
                   "NEEDS-ACTION": "nessuna risposta", "DELEGATED": "delegato"}


def elementi_ics(testo, cartella=""):
    """Eventi (VEVENT), attività (VTODO) e voci di diario (VJOURNAL) di un file iCalendar."""
    out = []
    pila, corrente, righe_raw, nome_cal = [], None, [], ""
    for riga in _righe_spiegate(_leggi_testo(testo)):
        nome, par, val = _scomponi_riga(riga)
        if nome == "BEGIN":
            comp = val.strip().upper()
            pila.append(comp)
            if comp in ("VEVENT", "VTODO", "VJOURNAL") and corrente is None:
                corrente, righe_raw = {"_comp": comp, "_prop": []}, [riga]
                continue
        elif nome == "END":
            comp = val.strip().upper()
            if pila:
                pila.pop()
            if corrente is not None and comp == corrente["_comp"]:
                righe_raw.append(riga)
                corrente["_raw"] = "\r\n".join(righe_raw)
                out.append(corrente)
                corrente = None
                continue
        elif nome == "X-WR-CALNAME" and corrente is None:
            nome_cal = _sfuggi_ics(val).strip()
        if corrente is not None:
            righe_raw.append(riga)
            if pila and pila[-1] == corrente["_comp"]:     # niente proprietà dei VALARM annidati
                corrente["_prop"].append((nome, par, val))
    risultati = []
    for c in out:
        tipo = {"VEVENT": "evento", "VTODO": "attivita", "VJOURNAL": "nota"}[c["_comp"]]
        e = nuovo_elemento(tipo, cartella=(f"{cartella}/{nome_cal}" if cartella and nome_cal and not cartella.endswith(nome_cal)
                                           else nome_cal or cartella))
        inizio = fine = scadenza = None
        tutto_giorno = False
        partecipanti, categorie = [], []
        durata = None
        for nome, par, val in c["_prop"]:
            v = _sfuggi_ics(val)
            if nome == "SUMMARY":
                e["titolo"] = v.strip()
            elif nome == "DTSTART":
                inizio, tutto_giorno = _data_ics(val, par)
            elif nome == "DTEND":
                fine, _t = _data_ics(val, par)
            elif nome == "DUE":
                scadenza, _t = _data_ics(val, par)
            elif nome == "DURATION":
                durata = _durata_ics(val)
            elif nome == "LOCATION":
                e["luogo"] = v.strip()
            elif nome == "DESCRIPTION":
                e["descrizione"] = v.strip()
            elif nome == "ORGANIZER":
                e["campi"].append(("Organizzatore", _persona_ics(val, par)))
            elif nome == "ATTENDEE":
                stato = _PARTECIPAZIONE.get(par.get("PARTSTAT", "").upper(), "")
                partecipanti.append(_persona_ics(val, par) + (f" ({stato})" if stato else ""))
            elif nome == "RRULE":
                e["campi"].append(("Si ripete", _ripetizione_leggibile(val)))
            elif nome == "STATUS":
                e["campi"].append(("Stato", _STATO_ICS.get(val.strip().upper(), val.strip().lower())))
            elif nome == "CATEGORIES":
                categorie += [x.strip() for x in v.split(",") if x.strip()]
            elif nome == "PRIORITY" and val.strip() not in ("", "0"):
                p = int(val) if val.strip().isdigit() else 0
                e["campi"].append(("Priorità", "alta" if 1 <= p <= 4 else "media" if p == 5 else "bassa" if p else val))
            elif nome == "PERCENT-COMPLETE":
                e["campi"].append(("Completamento", f"{val.strip()}%"))
            elif nome == "COMPLETED":
                d, _t = _data_ics(val, par)
                e["campi"].append(("Completata il", _fmt(d)))
            elif nome == "URL":
                e["campi"].append(("Collegamento", v.strip()))
            elif nome == "CLASS" and val.strip().upper() in ("PRIVATE", "CONFIDENTIAL"):
                e["campi"].append(("Visibilità", "privato"))
            elif nome == "ATTACH":
                e["campi"].append(("Allegato", par.get("FILENAME") or par.get("X-FILENAME") or v[:120]))
        if fine is None and inizio is not None and durata is not None:
            fine = inizio + durata
        if tutto_giorno and fine is not None and inizio is not None and (fine - inizio) >= timedelta(days=1):
            fine = fine - timedelta(days=1)           # DTEND dei giorni interi è esclusivo
        if tipo == "attivita":
            e["inizio"] = _fmt(scadenza or inizio, tutto_giorno)
            if scadenza is not None:
                e["campi"].insert(0, ("Scadenza", _fmt(scadenza)))
            if inizio is not None:
                e["campi"].insert(0, ("Inizio", _fmt(inizio, tutto_giorno)))
        else:
            e["inizio"] = _fmt(inizio, tutto_giorno)
            e["fine"] = _fmt(fine, tutto_giorno) if fine is not None else ""
        e["tutto_giorno"] = tutto_giorno
        if partecipanti:
            e["campi"].append(("Partecipanti", "\n".join(partecipanti)))
            e["persone"] = ", ".join(partecipanti)
        if categorie:
            e["campi"].append(("Categorie", ", ".join(categorie)))
        e["titolo"] = e["titolo"] or ("(senza titolo)")
        e["raw"], e["formato_raw"] = c["_raw"], "ics"
        risultati.append(e)
    return risultati


# ---------- vCard (RFC 2426 / 6350, anche 2.1) ----------
def _qp(valore, charset):
    try:
        return quopri_decode(valore.encode("latin-1", "replace")).decode(charset or "utf-8", "replace")
    except Exception:
        return valore


def quopri_decode(b):
    import quopri
    return quopri.decodestring(b)


_TIPI_TEL = {"CELL": "cellulare", "MOBILE": "cellulare", "HOME": "casa", "WORK": "lavoro", "FAX": "fax",
             "MAIN": "principale", "PAGER": "cercapersone", "IPHONE": "iPhone", "OTHER": "altro", "VOICE": ""}


def _etichetta_tipo(par):
    tipi = par.get("TYPE", [])
    if isinstance(tipi, str):
        tipi = tipi.split(",")
    nomi = [_TIPI_TEL.get(t.strip().upper(), t.strip().lower()) for t in tipi if t.strip()]
    nomi = [n for n in dict.fromkeys(nomi) if n and n not in ("internet", "pref", "x400")]
    return ", ".join(nomi)


def elementi_vcf(testo, cartella=""):
    out = []
    righe = _righe_spiegate_vcard(_leggi_testo(testo))
    corrente, raw = None, []
    for riga in righe:
        nome, par, val = _scomponi_riga(riga)
        if nome == "BEGIN" and val.strip().upper() == "VCARD":
            corrente, raw = [], [riga]
            continue
        if corrente is None:
            continue
        raw.append(riga)
        if nome == "END" and val.strip().upper() == "VCARD":
            e = _contatto_da_vcard(corrente, cartella)
            e["raw"], e["formato_raw"] = "\r\n".join(raw), "vcf"
            out.append(e)
            corrente = None
            continue
        if par.get("ENCODING", "").upper() in ("QUOTED-PRINTABLE", "Q"):
            val = _qp(val, par.get("CHARSET"))
        corrente.append((nome, par, val))
    return out


def _righe_spiegate_vcard(testo):
    """Come _righe_spiegate, più le righe "soft" del quoted-printable (finiscono con '=')."""
    righe = []
    for r in _righe_spiegate(testo):
        if righe and righe[-1].endswith("=") and "QUOTED-PRINTABLE" in righe[-1].upper().split(":", 1)[0]:
            righe[-1] = righe[-1][:-1] + r
        else:
            righe.append(r)
    return righe


def _contatto_da_vcard(prop, cartella):
    e = nuovo_elemento("contatto", cartella=cartella)
    email_, tel, indirizzi, altri = [], [], [], []
    nome_n = ""
    for nome, par, val in prop:
        v = _sfuggi_ics(val).strip()
        if nome == "FN":
            e["titolo"] = v
        elif nome == "N":
            parti = [x.strip() for x in re.split(r'(?<!\\);', val)]
            parti = [_sfuggi_ics(x) for x in parti] + [""] * 5
            nome_n = " ".join(x for x in (parti[3], parti[1], parti[2], parti[0], parti[4]) if x)
        elif nome == "EMAIL" and v:
            et = _etichetta_tipo(par)
            email_.append(v + (f" ({et})" if et else ""))
        elif nome == "TEL" and v:
            et = _etichetta_tipo(par)
            tel.append(re.sub(r'(?i)^tel:', '', v) + (f" ({et})" if et else ""))
        elif nome == "ADR":
            parti = [_sfuggi_ics(x).strip() for x in re.split(r'(?<!\\);', val)]
            testo_ind = ", ".join(x for x in parti if x)
            if testo_ind:
                et = _etichetta_tipo(par)
                indirizzi.append(testo_ind + (f" ({et})" if et else ""))
        elif nome == "ORG":
            altri.append(("Azienda", " · ".join(x for x in (_sfuggi_ics(y).strip() for y in re.split(r'(?<!\\);', val)) if x)))
        elif nome == "TITLE":
            altri.append(("Ruolo", v))
        elif nome == "NICKNAME":
            altri.append(("Soprannome", v))
        elif nome == "BDAY":
            d, _t = _data_ics(v.replace("-", "")[:8], {"VALUE": "DATE"}) if re.match(r'\d{4}-?\d{2}-?\d{2}', v) else (None, False)
            altri.append(("Compleanno", _fmt(d, True) if d else v))
        elif nome == "URL":
            altri.append(("Sito web", v))
        elif nome == "NOTE":
            e["descrizione"] = v
        elif nome == "CATEGORIES":
            altri.append(("Gruppi", v))
        elif nome == "PHOTO":
            if val.startswith("data:image"):
                e["foto"] = val
            elif par.get("ENCODING", "").upper() in ("B", "BASE64") and len(val) < 400000:
                tipo = (par.get("TYPE") or ["jpeg"])
                tipo = (tipo[0] if isinstance(tipo, list) else tipo).lower().replace("image/", "") or "jpeg"
                e["foto"] = f"data:image/{tipo};base64,{val.strip()}"
    e["titolo"] = e["titolo"] or nome_n or (email_[0].split(" ")[0] if email_ else "") or "(senza nome)"
    if email_:
        e["campi"].append(("Email", "\n".join(email_)))
    if tel:
        e["campi"].append(("Telefono", "\n".join(tel)))
    if indirizzi:
        e["campi"].append(("Indirizzo", "\n".join(indirizzi)))
    e["campi"] += [(k, v) for k, v in altri if v]
    e["persone"] = ", ".join(x.split(" (")[0] for x in email_ + tel)
    e["luogo"] = next((v for k, v in altri if k == "Azienda"), "")
    return e


# ---------- CSV dei contatti (Google, Outlook, Apple, generici) ----------
def _norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def elementi_csv_contatti(dati, cartella=""):
    testo = _leggi_testo(dati)
    try:
        dialetto = csv.Sniffer().sniff(testo[:4096], delimiters=",;\t")
    except csv.Error:
        dialetto = csv.excel
    righe = list(csv.reader(io.StringIO(testo), dialetto))
    if len(righe) < 2:
        return []
    intest = [_norm(h) for h in righe[0]]
    col_email = [i for i, h in enumerate(intest) if ("mail" in h) and ("type" not in h and "tipo" not in h and "label" not in h)]
    col_nome = [i for i, h in enumerate(intest) if h in ("name", "nome", "display name", "full name", "nome visualizzato",
                                                          "nome completo", "fn")]
    col_primo = [i for i, h in enumerate(intest) if h in ("given name", "first name", "nome", "nome di battesimo")]
    col_cognome = [i for i, h in enumerate(intest) if h in ("family name", "last name", "cognome", "surname")]
    if not col_email or not (col_nome or col_primo or col_cognome):
        return []
    col_tel = [i for i, h in enumerate(intest) if ("phone" in h or "telefono" in h or "cellulare" in h or "mobile" in h)
               and "type" not in h and "label" not in h]
    col_org = [i for i, h in enumerate(intest) if h in ("organization 1 name", "organization name", "company", "azienda",
                                                         "società", "societa", "organizzazione")]
    col_ruolo = [i for i, h in enumerate(intest) if h in ("organization 1 title", "job title", "title", "ruolo", "posizione")]
    col_note = [i for i, h in enumerate(intest) if h in ("notes", "note")]
    out = []
    for r in righe[1:]:
        r = r + [""] * (len(intest) - len(r))
        val = lambda cols: [r[i].strip() for i in cols if i < len(r) and r[i].strip()]
        nome = " ".join(val(col_nome)[:1]) or " ".join(val(col_primo)[:1] + val(col_cognome)[:1])
        emails = [x for v in val(col_email) for x in re.split(r'\s*:::\s*|;\s*', v) if '@' in x]
        tel = [x for v in val(col_tel) for x in re.split(r'\s*:::\s*', v) if x]
        if not (nome or emails or tel):
            continue
        e = nuovo_elemento("contatto", nome or emails[0] if (nome or emails) else tel[0], cartella=cartella)
        if emails:
            e["campi"].append(("Email", "\n".join(emails)))
        if tel:
            e["campi"].append(("Telefono", "\n".join(tel)))
        for etich, cols in (("Azienda", col_org), ("Ruolo", col_ruolo)):
            if val(cols):
                e["campi"].append((etich, val(cols)[0]))
        e["descrizione"] = "\n".join(val(col_note))
        e["persone"] = ", ".join(emails + tel)
        e["luogo"] = (val(col_org) or [""])[0]
        out.append(e)
    return out


# ---------- Google Takeout: Tasks, Keep, Chat ----------
def elementi_json(dati, rel, cartella=""):
    try:
        j = json.loads(_leggi_testo(dati))
    except Exception:
        return []
    out = []
    if isinstance(j, dict) and str(j.get("kind", "")).startswith("tasks#"):          # Google Tasks
        for elenco in j.get("items", []):
            nome_elenco = elenco.get("title", "") or "Attività"
            for t in elenco.get("items", []) or []:
                e = nuovo_elemento("attivita", t.get("title", "") or "(senza titolo)",
                                   cartella=f"Attività/{nome_elenco}")
                scad = _iso(t.get("due"))
                e["inizio"] = _fmt(scad, True) if scad else ""
                e["descrizione"] = t.get("notes", "") or ""
                stato = "completata" if t.get("status") == "completed" else "da fare"
                e["campi"].append(("Stato", stato))
                if scad:
                    e["campi"].append(("Scadenza", _fmt(scad, True)))
                if t.get("completed"):
                    e["campi"].append(("Completata il", _fmt(_iso(t["completed"]))))
                for link in t.get("links", []) or []:
                    e["campi"].append(("Collegamento", link.get("link", "")))
                out.append(e)
        return out
    if isinstance(j, dict) and ("textContent" in j or "listContent" in j) and "userEditedTimestampUsec" in j:  # Keep
        e = nuovo_elemento("nota", j.get("title", "") or os.path.splitext(os.path.basename(rel))[0], cartella="Note")
        testo = j.get("textContent", "") or ""
        if j.get("listContent"):
            testo += "\n".join(("☑ " if x.get("isChecked") else "☐ ") + x.get("text", "") for x in j["listContent"])
        e["descrizione"] = testo
        e["inizio"] = _fmt(_da_epoca(j.get("userEditedTimestampUsec")))
        etichette = [x.get("name", "") for x in j.get("labels", []) or []]
        if etichette:
            e["campi"].append(("Etichette", ", ".join(etichette)))
        if j.get("isTrashed"):
            e["campi"].append(("Stato", "nel cestino"))
        elif j.get("isArchived"):
            e["campi"].append(("Stato", "archiviata"))
        if j.get("isPinned"):
            e["campi"].append(("Fissata", "sì"))
        return [e]
    if isinstance(j, dict) and isinstance(j.get("messages"), list) and (
            not j["messages"] or isinstance(j["messages"][0], dict) and "creator" in j["messages"][0]):  # Google Chat
        cartella_gc = os.path.dirname(rel)
        nome_gruppo = os.path.basename(cartella_gc)
        info_file = os.path.join(os.path.dirname(os.path.abspath(rel)), "group_info.json")
        partecipanti = []
        try:
            with open(info_file, encoding="utf-8") as f:
                info = json.load(f)
            nome_gruppo = info.get("name") or nome_gruppo
            partecipanti = [m.get("name") or m.get("email", "") for m in info.get("members", [])]
        except Exception:
            pass
        messaggi = []
        for m in j["messages"]:
            autore = (m.get("creator") or {}).get("name") or (m.get("creator") or {}).get("email", "")
            data = m.get("created_date", "") or m.get("updated_date", "")
            testo = m.get("text", "")
            for a in m.get("attached_files", []) or []:
                testo += f"\n[allegato: {a.get('original_name') or a.get('export_name', '')}]"
            messaggi.append({"autore": autore, "data": _data_google_chat(data), "testo": testo})
        if not messaggi:
            return []
        if not partecipanti:
            partecipanti = list(dict.fromkeys(m["autore"] for m in messaggi if m["autore"]))
        e = nuovo_elemento("chat", nome_gruppo or "Conversazione", cartella="Chat/Google Chat")
        e["messaggi"] = messaggi
        e["inizio"], e["fine"] = messaggi[0]["data"], messaggi[-1]["data"]
        e["persone"] = ", ".join(partecipanti)
        e["campi"] = [("Partecipanti", "\n".join(partecipanti)), ("Messaggi", str(len(messaggi)))]
        return [e]
    return []


def _data_google_chat(testo):
    """'Wednesday, 3 April 2024 at 10:15:02 UTC' (o in altre lingue) -> 'AAAA-MM-GG HH:MM' se riconosciuta."""
    m = re.search(r'(\d{1,2}) (\w+) (\d{4})\D+(\d{1,2}):(\d{2})', testo or "")
    mesi = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12, "gennaio": 1, "febbraio": 2, "marzo": 3,
            "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10,
            "novembre": 11, "dicembre": 12}
    if m and m.group(2).lower() in mesi:
        try:
            dt = datetime(int(m.group(3)), mesi[m.group(2).lower()], int(m.group(1)), int(m.group(4)), int(m.group(5)),
                          tzinfo=timezone.utc if "UTC" in testo else None)
            return _fmt(dt)
        except ValueError:
            pass
    d = _iso(testo)
    return _fmt(d) if d else (testo or "")


# ---------- Zimbra / Carbonio: .meta JSON (ItemData) + metadati in BEncoding ----------
def decodifica_bencode(testo):
    """Metadati Zimbra (classe Metadata): stile bencode, d...e dizionari, l...e liste, i...e interi,
    <lunghezza in byte>:<stringa>. Restituisce dict/list/int/str."""
    b = testo.encode("utf-8") if isinstance(testo, str) else testo
    pos = [0]

    def valore():
        c = b[pos[0]:pos[0] + 1]
        if c == b"d":
            pos[0] += 1
            d = {}
            while b[pos[0]:pos[0] + 1] != b"e":
                k = valore()
                d[str(k)] = valore()
            pos[0] += 1
            return d
        if c == b"l":
            pos[0] += 1
            lista = []
            while b[pos[0]:pos[0] + 1] != b"e":
                lista.append(valore())
            pos[0] += 1
            return lista
        if c == b"i":
            fine = b.index(b"e", pos[0])
            n = b[pos[0] + 1:fine]
            pos[0] = fine + 1
            try:
                return int(n)
            except ValueError:
                return n.decode("ascii", "replace")
        if c.isdigit():
            due = b.index(b":", pos[0])
            lung = int(b[pos[0]:due])
            s = b[due + 1:due + 1 + lung]
            pos[0] = due + 1 + lung
            return s.decode("utf-8", "replace")
        if c in (b"t", b"f"):                # booleani (se presenti)
            pos[0] += 1
            return c == b"t"
        raise ValueError(f"metadati non riconosciuti alla posizione {pos[0]}")

    return valore()


_CAMPI_ZIMBRA = [
    ("Email", ("email", "email2", "email3", "workEmail1", "workEmail2", "workEmail3", "homeEmail")),
    ("Cellulare", ("mobilePhone", "mobile2Phone")),
    ("Telefono lavoro", ("workPhone", "workPhone2", "companyPhone", "assistantPhone")),
    ("Telefono casa", ("homePhone", "homePhone2")),
    ("Altro telefono", ("otherPhone", "carPhone", "callbackPhone", "pager")),
    ("Fax", ("workFax", "homeFax", "otherFax")),
    ("Azienda", ("company",)), ("Reparto", ("department",)), ("Ruolo", ("jobTitle",)),
    ("Soprannome", ("nickname",)), ("Compleanno", ("birthday",)), ("Anniversario", ("anniversary",)),
    ("Sito web", ("homeURL", "workURL", "otherURL")),
]


def _contatto_zimbra(fld, cartella):
    nome = fld.get("fullName") or " ".join(x for x in (fld.get("namePrefix"), fld.get("firstName"), fld.get("middleName"),
                                                       fld.get("lastName"), fld.get("nameSuffix")) if x)
    e = nuovo_elemento("contatto", nome or fld.get("fileAs", "") or fld.get("company", "") or fld.get("email", "")
                       or "(senza nome)", cartella=cartella)
    usati = {"fullName", "namePrefix", "firstName", "middleName", "lastName", "nameSuffix", "fileAs", "notes",
             "image", "type", "dlist", "nickname"}
    for etich, chiavi in _CAMPI_ZIMBRA:
        valori = [str(fld[k]) for k in chiavi if fld.get(k)]
        usati.update(chiavi)
        if valori:
            e["campi"].append((etich, "\n".join(valori)))
    for pref, etich in (("home", "Indirizzo casa"), ("work", "Indirizzo lavoro"), ("other", "Altro indirizzo")):
        parti = [fld.get(pref + k) for k in ("Street", "PostalCode", "City", "State", "Country")]
        usati.update(pref + k for k in ("Street", "PostalCode", "City", "State", "Country"))
        if any(parti):
            e["campi"].append((etich, ", ".join(str(p) for p in parti if p)))
    if fld.get("type") == "group" or fld.get("dlist"):
        e["campi"].append(("Membri del gruppo", str(fld.get("dlist", "")).replace(",", "\n")))
    for k, v in sorted(fld.items()):       # campi personalizzati o non previsti: si mostrano comunque
        if k not in usati and v and not k.startswith("zimbra") and isinstance(v, (str, int)):
            e["campi"].append((k, str(v)))
    e["descrizione"] = str(fld.get("notes", ""))
    e["persone"] = ", ".join(str(fld[k]) for chiavi in (_CAMPI_ZIMBRA[0][1],) for k in chiavi if fld.get(k))
    e["luogo"] = str(fld.get("company", ""))
    return e


def _ics_da_mime(dati):
    """Parte text/calendar di un messaggio MIME (inviti Zimbra .appt/.task, inviti allegati)."""
    try:
        msg = email.message_from_bytes(dati, policy=policy.default)
        for part in msg.walk():
            if part.get_content_type() in ("text/calendar", "application/ics"):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload
    except Exception:
        pass
    if b"BEGIN:VCALENDAR" in dati[:200000]:
        i = dati.find(b"BEGIN:VCALENDAR")
        return dati[i:]
    return None


def elementi_zimbra_meta(percorso_meta, rel_dir, radice):
    """Un elemento dell'export Zimbra/Carbonio descritto dal suo .meta. -> (elementi, percorso_contenuto o None)."""
    try:
        with open(percorso_meta, "rb") as f:
            j = json.loads(f.read().decode("utf-8", "replace"))
    except Exception:
        return [], None
    if not isinstance(j, dict) or "type" not in j:
        return [], None
    tipo = str(j.get("type", "")).lower()
    contenuto = percorso_meta[:-5]
    if not os.path.isfile(contenuto):
        contenuto = None
    cartella = _cartella_pim(str(j.get("Path", "") or "").lstrip("/").rsplit("/", 1)[0] if j.get("Path") else rel_dir)
    meta = {}
    if j.get("metadata"):
        try:
            meta = decodifica_bencode(j["metadata"])
        except Exception:
            meta = {}
    data_el = _da_epoca(j.get("date"))
    if tipo == "contact":
        fld = meta.get("fld", {}) if isinstance(meta, dict) else {}
        if not isinstance(fld, dict) or not fld:
            return [], contenuto
        e = _contatto_zimbra(fld, cartella or "Contatti")
        return [e], contenuto
    if tipo in ("appointment", "task"):
        elementi = []
        if contenuto:
            try:
                with open(contenuto, "rb") as f:
                    ics = _ics_da_mime(f.read())
                if ics:
                    elementi = [x for x in elementi_ics(ics, cartella)
                                if x["tipo"] == ("evento" if tipo == "appointment" else "attivita")] or elementi_ics(ics, cartella)
            except Exception:
                elementi = []
        if not elementi:              # nessuna parte iCalendar: titolo e date dai metadati
            e = nuovo_elemento("evento" if tipo == "appointment" else "attivita",
                               j.get("subject") or j.get("name") or "(senza titolo)", cartella=cartella)
            if isinstance(meta, dict):
                e["inizio"] = _fmt(_da_epoca(meta.get("aps"))) if meta.get("aps") else _fmt(data_el)
                e["fine"] = _fmt(_da_epoca(meta.get("ape"))) if meta.get("ape") else ""
            elementi = [e]
        for e in elementi:
            e["cartella"] = e.get("cartella") or cartella
            if j.get("TagNames"):
                e["campi"].append(("Etichette", str(j["TagNames"]).replace(":", ", ")))
        return elementi, contenuto
    if tipo == "chat":
        e = nuovo_elemento("chat", j.get("subject") or "Chat", cartella=cartella or "Chat", mime=True)
        e["inizio"] = _fmt(data_el)
        e["persone"] = str(j.get("sender", "") or "")
        return [e], contenuto
    if tipo in ("note", "wiki"):
        e = nuovo_elemento("nota", j.get("subject") or j.get("name") or "Nota", cartella=cartella or "Note")
        e["inizio"] = _fmt(data_el)
        if contenuto:
            try:
                with open(contenuto, "rb") as f:
                    testo = _leggi_testo(f.read(2_000_000))
                e["descrizione"] = re.sub(r'<[^>]+>', ' ', testo) if "<" in testo[:200] else testo
            except OSError:
                pass
        return [e], contenuto
    if tipo == "document" and contenuto:
        e = nuovo_elemento("file", j.get("name") or os.path.basename(contenuto), cartella=cartella or "Valigetta",
                           file=True)
        e["inizio"] = _fmt(data_el)
        e["campi"] = [("Dimensione", dimensione_leggibile(j.get("size") or os.path.getsize(contenuto)))]
        if j.get("sender"):
            e["campi"].append(("Autore", str(j["sender"])))
        return [e], contenuto
    return [], contenuto


def dimensione_leggibile(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return ""
    for unita in ("byte", "KB", "MB", "GB"):
        if n < 1024 or unita == "GB":
            return f"{n:.0f} {unita}" if unita == "byte" else f"{n:.1f} {unita}"
        n /= 1024


# ---------- Thunderbird: rubrica abook.sqlite e calendario local.sqlite ----------
def elementi_sqlite_thunderbird(percorso, cartella=""):
    nome = os.path.basename(percorso).lower()
    out = []
    try:
        conn = sqlite3.connect(f"file:{percorso}?mode=ro", uri=True)
    except Exception:
        return []
    try:
        tabelle = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if nome.startswith(("abook", "history")) and "properties" in tabelle:
            schede = {}
            for card, chiave, valore in conn.execute("SELECT card, name, value FROM properties"):
                schede.setdefault(card, {})[chiave] = valore
            rubrica = "Rubrica personale" if nome.startswith("abook") else "Indirizzi raccolti"
            for p in schede.values():
                if p.get("_vCard"):
                    out += [dict(x, cartella=f"Contatti/{rubrica}") for x in elementi_vcf(p["_vCard"])]
                    continue
                nome_c = p.get("DisplayName") or " ".join(x for x in (p.get("FirstName"), p.get("LastName")) if x)
                e = nuovo_elemento("contatto", nome_c or p.get("PrimaryEmail", "") or "(senza nome)",
                                   cartella=f"Contatti/{rubrica}")
                for etich, chiavi in (("Email", ("PrimaryEmail", "SecondEmail")), ("Telefono", ("CellularNumber",
                                      "WorkPhone", "HomePhone")), ("Azienda", ("Company",)), ("Ruolo", ("JobTitle",))):
                    valori = [p[k] for k in chiavi if p.get(k)]
                    if valori:
                        e["campi"].append((etich, "\n".join(valori)))
                e["descrizione"] = p.get("Notes", "")
                e["persone"] = ", ".join(p[k] for k in ("PrimaryEmail", "SecondEmail") if p.get(k))
                out.append(e)
        elif "cal_events" in tabelle:
            proprieta = {}
            if "cal_properties" in tabelle:
                for item, chiave, valore in conn.execute("SELECT item_id, key, value FROM cal_properties"):
                    proprieta.setdefault(item, {})[chiave] = valore
            nomi_cal = {}
            for riga in conn.execute("SELECT id, title, event_start, event_end, flags FROM cal_events"):
                item, titolo, inizio, fine, flags = riga
                e = nuovo_elemento("evento", titolo or "(senza titolo)", cartella="Calendario/Thunderbird")
                tutto = bool((flags or 0) & 8)
                e["inizio"] = _fmt(_da_epoca(inizio), tutto)
                e["fine"] = _fmt(_da_epoca(fine), tutto)
                pr = proprieta.get(item, {})
                e["luogo"] = pr.get("LOCATION", "") or ""
                e["descrizione"] = pr.get("DESCRIPTION", "") or ""
                out.append(e)
            if "cal_todos" in tabelle:
                for item, titolo, scad, completata in conn.execute(
                        "SELECT id, title, todo_due, todo_completed FROM cal_todos"):
                    e = nuovo_elemento("attivita", titolo or "(senza titolo)", cartella="Attività/Thunderbird")
                    e["inizio"] = _fmt(_da_epoca(scad))
                    e["campi"].append(("Stato", "completata" if completata else "da fare"))
                    e["descrizione"] = proprieta.get(item, {}).get("DESCRIPTION", "") or ""
                    out.append(e)
            del nomi_cal
    except Exception:
        pass
    finally:
        conn.close()
    return out


# ---------- Outlook: elementi non di posta in .pst/.ost e .msg ----------
_CLASSI_OUTLOOK = {"ipm.appointment": "evento", "ipm.task": "attivita", "ipm.contact": "contatto",
                   "ipm.distlist": "contatto", "ipm.stickynote": "nota", "ipm.activity": "nota"}


def tipo_classe_outlook(classe):
    c = (classe or "").lower()
    for prefisso, tipo in _CLASSI_OUTLOOK.items():
        if c == prefisso or c.startswith(prefisso + "."):
            return tipo
    return None


def _ics_escape(v):
    return str(v or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_dt(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ics_da_campi(tipo, titolo, inizio=None, fine=None, luogo="", descrizione="", partecipanti=(), completata=None,
                 uid=""):
    comp = "VTODO" if tipo == "attivita" else "VJOURNAL" if tipo == "nota" else "VEVENT"
    righe = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ZimbraViewer//IT", f"BEGIN:{comp}",
             f"UID:{uid or hashlib.sha1((titolo + str(inizio)).encode()).hexdigest()}@zimbraviewer",
             f"SUMMARY:{_ics_escape(titolo)}"]
    if inizio:
        righe.append(f"{'DUE' if comp == 'VTODO' else 'DTSTART'}:{_ics_dt(inizio)}")
    if fine and comp == "VEVENT":
        righe.append(f"DTEND:{_ics_dt(fine)}")
    if luogo:
        righe.append(f"LOCATION:{_ics_escape(luogo)}")
    if descrizione:
        righe.append(f"DESCRIPTION:{_ics_escape(descrizione)}")
    for p in partecipanti:
        righe.append(f"ATTENDEE;CN={_ics_escape(p)}:mailto:{p if '@' in p else 'nessuno@invalid'}")
    if completata is not None and comp == "VTODO":
        righe.append(f"STATUS:{'COMPLETED' if completata else 'NEEDS-ACTION'}")
    righe += [f"END:{comp}", "END:VCALENDAR", ""]
    return "\r\n".join(righe).encode("utf-8")


def vcf_da_campi(nome, nome_proprio="", cognome="", emails=(), telefoni=(), azienda="", ruolo="", note="",
                 indirizzi=(), sito=""):
    esc = lambda v: str(v or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    righe = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{esc(nome)}", f"N:{esc(cognome)};{esc(nome_proprio)};;;"]
    righe += [f"EMAIL;TYPE=INTERNET:{esc(x)}" for x in emails if x]
    righe += [f"TEL;TYPE={t}:{esc(x)}" for t, x in telefoni if x]
    righe += [f"ADR;TYPE={t}:;;{esc(x)};;;;" for t, x in indirizzi if x]
    if azienda:
        righe.append(f"ORG:{esc(azienda)}")
    if ruolo:
        righe.append(f"TITLE:{esc(ruolo)}")
    if sito:
        righe.append(f"URL:{esc(sito)}")
    if note:
        righe.append(f"NOTE:{esc(note)}")
    righe += ["END:VCARD", ""]
    return "\r\n".join(righe).encode("utf-8")


_RE_EMAIL = re.compile(r'^[^@\s<>"]+@[^@\s<>"]+\.[A-Za-z]{2,}$')


def pim_outlook(tipo, prop_str, prop_data, prop_nominate, oggetto, corpo):
    """File .ics/.vcf per un elemento Outlook. prop_str/prop_data: {id MAPI: valore}; prop_nominate: {LID: valore}
    delle proprietà con nome (quando note). -> (estensione, byte)."""
    s = lambda pid: prop_str.get(pid) or ""
    if tipo == "contatto":
        emails = [prop_nominate.get(l) for l in (0x8083, 0x8093, 0x80A3)]
        emails = [x for x in emails if x and _RE_EMAIL.match(str(x))]
        if not emails:                         # proprietà con nome non mappate (pst): si cercano gli indirizzi
            emails = list(dict.fromkeys(v for k, v in prop_str.items()
                                        if k >= 0x8000 and isinstance(v, str) and _RE_EMAIL.match(v.strip())))
        telefoni = [("CELL", s(0x3A1C)), ("WORK", s(0x3A08)), ("HOME", s(0x3A09)), ("WORK,FAX", s(0x3A24)),
                    ("OTHER", s(0x3A1F))]
        ind_lavoro = ", ".join(x for x in (s(0x3A29), s(0x3A2A), s(0x3A27), s(0x3A28), s(0x3A26)) if x)
        ind_casa = ", ".join(x for x in (s(0x3A5D), s(0x3A5B), s(0x3A59), s(0x3A5C), s(0x3A5A)) if x)
        nome = s(0x3001) or oggetto or " ".join(x for x in (s(0x3A06), s(0x3A11)) if x) or (emails[0] if emails else "")
        return ".vcf", vcf_da_campi(nome, s(0x3A06), s(0x3A11), emails, telefoni, s(0x3A16), s(0x3A17), corpo,
                                    [("WORK", ind_lavoro), ("HOME", ind_casa)], s(0x3A51))
    inizio = prop_nominate.get(0x820D) or prop_nominate.get(0x8104) or prop_data.get(0x0060)
    fine = prop_nominate.get(0x820E) or prop_nominate.get(0x8105) or prop_data.get(0x0061)
    luogo = prop_nominate.get(0x8208) or ""
    completata = prop_nominate.get(0x811C) if tipo == "attivita" else None
    if tipo == "attivita" and prop_nominate.get(0x8105):
        inizio = prop_nominate.get(0x8105)
    return ".ics", ics_da_campi(tipo, oggetto or "(senza titolo)", inizio, fine, luogo if isinstance(luogo, str) else "",
                                corpo or "", completata=bool(completata) if completata is not None else None)


# ---------- dispatcher: tutti gli elementi di un file ----------
def e_file_pim(nome):
    b = nome.lower()
    return (b.endswith(ESTENSIONI_PIM) and not b.endswith(".eml.meta")) or \
        (b.endswith(".sqlite") and (b.startswith(("abook", "history")) or b == "local.sqlite"))


def elementi_da_file(percorso, radice):
    """Elementi (eventi, attività, contatti, chat, note, file) contenuti in un file dell'export.
    Restituisce [(elemento, percorso_relativo_del_contenuto)]."""
    rel = os.path.relpath(percorso, radice).replace("\\", "/")
    rel_dir = os.path.dirname(rel)
    cartella = _cartella_pim(rel_dir)
    b = percorso.lower()
    try:
        if b.endswith(".meta"):
            elementi, contenuto = elementi_zimbra_meta(percorso, rel_dir, radice)
            rel_c = os.path.relpath(contenuto, radice).replace("\\", "/") if contenuto else rel
            return [(e, rel_c) for e in elementi]
        if b.endswith((".appt", ".task", ".chat")):
            if os.path.exists(percorso + ".meta"):
                return []                         # lo descrive già il suo .meta
            with open(percorso, "rb") as f:
                dati = f.read()
            if b.endswith(".chat"):
                return [(nuovo_elemento("chat", os.path.splitext(os.path.basename(percorso))[0], cartella=cartella or "Chat",
                                        mime=True), rel)]
            ics = _ics_da_mime(dati)
            return [(e, rel) for e in elementi_ics(ics, cartella)] if ics else []
        if os.path.getsize(percorso) > 200 * 1024 * 1024:
            return []
        if b.endswith(".sqlite"):
            return [(e, rel) for e in elementi_sqlite_thunderbird(percorso, cartella)]
        with open(percorso, "rb") as f:
            dati = f.read()
        if b.endswith((".ics", ".ical", ".icalendar", ".ifb", ".vcs")):
            return [(e, rel) for e in elementi_ics(dati, cartella or "Calendario")]
        if b.endswith((".vcf", ".vcard")):
            return [(e, rel) for e in elementi_vcf(dati, cartella or "Contatti")]
        if b.endswith(".csv"):
            return [(e, rel) for e in elementi_csv_contatti(dati, cartella or "Contatti")]
        if b.endswith(".json"):
            return [(e, rel) for e in elementi_json(dati, percorso, cartella)]
    except Exception:
        return []
    return []


def contiene_pim(cartella, limite=4000):
    """Vero se la cartella contiene dati non di posta leggibili (calendario, rubrica...). Guarda al massimo
    'limite' file per non rallentare l'apertura di cartelle enormi."""
    visti = 0
    for _r, _d, files in os.walk(cartella):
        for f in files:
            visti += 1
            b = f.lower()
            if b.endswith((".ics", ".vcf", ".vcard", ".appt.meta", ".task.meta", ".chat")) or b == "tasks.json" or \
                    (b.startswith("abook") and b.endswith(".sqlite")):
                return True
            if visti > limite:
                return False
    return False


def cerca_file_pim(cartella):
    """File con dati non di posta da copiare nella cartella di destinazione durante un'importazione."""
    trovati = []
    for radice, _dirs, files in os.walk(cartella):
        for f in files:
            b = f.lower()
            p = os.path.join(radice, f)
            if b.endswith(".json"):
                if b in ("tasks.json", "messages.json", "group_info.json") or os.path.basename(radice).lower() == "keep":
                    trovati.append(p)
            elif b.endswith(".csv"):
                try:
                    with open(p, "rb") as fh:
                        if elementi_csv_contatti(fh.read(65536)):
                            trovati.append(p)
                except OSError:
                    pass
            elif e_file_pim(f) and not b.endswith(".meta"):
                trovati.append(p)
    return trovati


# ---------- esportazione degli elementi ----------
def esporta_elementi(elementi, percorso):
    """Salva gli elementi scelti: .ics (eventi/attività/note), .vcf (contatti) o .csv (qualsiasi tipo)."""
    if percorso.lower().endswith(".csv"):
        with open(percorso, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Tipo", "Titolo", "Inizio", "Fine", "Luogo", "Persone", "Cartella", "Dettagli", "Descrizione"])
            for e in elementi:
                w.writerow([NOMI_TIPI_PIM.get(e["tipo"], e["tipo"]), e.get("titolo", ""), e.get("inizio", ""),
                            e.get("fine", ""), e.get("luogo", ""), e.get("persone", ""), e.get("cartella", ""),
                            " | ".join(f"{k}: {str(v).replace(chr(10), ', ')}" for k, v in e.get("campi", [])),
                            e.get("descrizione", "")])
        return
    if percorso.lower().endswith(".vcf"):
        with open(percorso, "wb") as f:
            for e in elementi:
                if e.get("formato_raw") == "vcf" and e.get("raw"):
                    f.write(e["raw"].encode("utf-8") + b"\r\n")
                elif e["tipo"] == "contatto":
                    campi = dict(e.get("campi", []))
                    f.write(vcf_da_campi(e["titolo"], emails=str(campi.get("Email", "")).split("\n"),
                                         telefoni=[("VOICE", t) for t in str(campi.get("Telefono", "")).split("\n")],
                                         azienda=campi.get("Azienda", ""), ruolo=campi.get("Ruolo", ""),
                                         note=e.get("descrizione", "")))
        return
    righe = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ZimbraViewer//IT"]
    for e in elementi:
        if e.get("formato_raw") == "ics" and e.get("raw"):
            righe.append(e["raw"])
        elif e["tipo"] in ("evento", "attivita", "nota"):
            dt = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M") if len(s) == 16 else (
                datetime.strptime(s, "%Y-%m-%d") if len(s) == 10 else None)
            corpo = ics_da_campi(e["tipo"], e["titolo"], dt(e.get("inizio", "")), dt(e.get("fine", "")),
                                 e.get("luogo", ""), e.get("descrizione", "")).decode("utf-8")
            interno = corpo.split("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ZimbraViewer//IT\r\n", 1)[-1]
            righe.append(interno.rsplit("END:VCALENDAR", 1)[0].rstrip())
    righe += ["END:VCALENDAR", ""]
    with open(percorso, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(righe))

# ==========================================
# FIRME DIGITALI - MOTORE DEL P7MREADER 3.0 (integrato)
# Codice ripreso da "P7MReader v3.py": CAdES (.p7m, .p7s), PAdES (.pdf), XAdES (.xml), riepilogo FatturaPA, report.
# Stesse regole e stessi esiti (Verificato / Attenzione / Non valido); impostazioni lette da
# %APPDATA%\P7MReader\impostazioni.json. Differenze: lavora sui byte (anche degli allegati delle mail),
# l'archivio di fiducia (Trusted List AgID inclusa) si carica in sottofondo all'avvio, le verifiche girano in thread separati.
# ==========================================
try:
    from asn1crypto import cms, x509, pem, tsp
    from asn1crypto.core import Void
    from pyhanko_certvalidator import CertificateValidator, ValidationContext
    from pyhanko_certvalidator.errors import PathValidationError
    P7M_LIBRERIE_OK, P7M_LIBRERIE_ERRORE = True, ""
except Exception as _err_librerie:
    cms = x509 = pem = tsp = None
    Void = type(None)
    PathValidationError = Exception
    P7M_LIBRERIE_OK, P7M_LIBRERIE_ERRORE = False, f"{type(_err_librerie).__name__}: {_err_librerie}"
try:
    from pyhanko.pdf_utils.reader import PdfFileReader
    PDF_OK = True
except Exception:
    PdfFileReader = None
    PDF_OK = False
try:
    from pyhanko.sign.validation import async_validate_pdf_signature
except Exception:
    async_validate_pdf_signature = None
try:
    from pyhanko.sign.validation import validate_pdf_signature
except Exception:
    validate_pdf_signature = None
try:
    from pyhanko.sign.validation import async_validate_pdf_timestamp
except Exception:
    async_validate_pdf_timestamp = None
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, ec, rsa, dsa, ed25519, ed448
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
try:
    from lxml import etree
except Exception:
    etree = None
for _nome_log in ("pyhanko", "pyhanko_certvalidator"):      # gli esiti li gestisce il programma: niente traceback sul log
    logging.getLogger(_nome_log).setLevel(logging.CRITICAL)

MOTORE_FIRME = "motore P7MReader 3.0"
MAX_ANNIDAMENTO = 6
OID_TIMESTAMP_TOKEN = '1.2.840.113549.1.9.16.2.14'
OID_COUNTER_SIGNATURE = '1.2.840.113549.1.9.6'

class _ImpostazioniP7MReader:
    """Impostazioni del P7MReader, solo in lettura: se il P7MReader è installato sullo stesso PC si usano
    le sue scelte (CA aggiunte, controllo revoca, validazione alla data di firma), altrimenti i suoi default."""
    DEFAULT = {"revoca": True, "valida_data_firma": True, "estrai_annidati": True,
               "concorrenza": 4, "radici_extra": []}

    def __init__(self):
        self.d = dict(self.DEFAULT)
        for base in cartelle_config_utente():
            try:
                with open(os.path.join(base, "P7MReader", "impostazioni.json"), "r", encoding="utf-8") as f:
                    letto = json.load(f)
                for k in self.DEFAULT:
                    if k in letto:
                        self.d[k] = letto[k]
                break
            except Exception:
                pass

    def __getitem__(self, k):
        return self.d.get(k, self.DEFAULT.get(k))

IMP = _ImpostazioniP7MReader()

_EST_BUSTA = ('.p7m', '.p7s')
_RE_SEGNO_COPIA = re.compile(r'\s*(?:[\(\[]\s*(\d+)\s*[\)\]]|-\s*cop(?:ia|y))\s*$', re.IGNORECASE)
_RE_ESTENSIONE = re.compile(r'\.[A-Za-z0-9]{1,8}$')


def _estensione_vera(s: str) -> bool:
    m = _RE_ESTENSIONE.search(s)
    return bool(m) and any(c.isalpha() for c in m.group(0))


def _togli_segni_copia(s: str) -> str:
    """Toglie dalla coda i segni di copia ripetuti: " (1)", "(1) (2)", "[1]", " - Copia", " - Copia (3)".
    Un numero di 4+ cifre resta, a meno che non venga dopo un'estensione: "Bilancio (2024)" e' un nome legittimo."""
    while True:
        s = s.rstrip(' .')
        m = _RE_SEGNO_COPIA.search(s)
        if not m or not s[:m.start()].rstrip(' .'):
            return s
        if m.group(1) and len(m.group(1)) > 3 and not _estensione_vera(s[:m.start()].rstrip(' .')):
            return s
        s = s[:m.start()]


def pulisci_nome_file_globale(filename: str) -> str:
    """"doc.pdf (1) (1).p7m", "doc.pdf.p7m (2)", "doc (3).pdf - Copia.p7m.p7m" -> "doc.pdf"."""
    nome = filename.strip()
    while True:
        nome = _togli_segni_copia(nome)
        base, ext = os.path.splitext(nome)
        if ext.lower() in _EST_BUSTA and base:
            nome = base
            continue
        break
    if nome.lower() in _EST_BUSTA:
        return "documento"
    while _estensione_vera(nome):
        base, ext = os.path.splitext(nome)
        pulita = _togli_segni_copia(base)
        if not pulita:
            break
        if pulita.lower().endswith(ext.lower()):     # "doc.pdf (1).pdf" -> "doc.pdf"
            nome = pulita
            continue
        nome = pulita + ext
        break
    return nome or "documento"


def tipo_documento(nome: str) -> str:
    """Estensione significativa di un file, ignorando i segni di copia in coda: "x.p7m (1)" -> ".p7m"."""
    n = nome.strip().rstrip(' .')
    while True:
        m = _RE_SEGNO_COPIA.search(n)
        if not m or not n[:m.start()]:
            break
        n = n[:m.start()].rstrip(' .')
    return os.path.splitext(n)[1].lower()


def supportato(nome: str, estensioni=ESTENSIONI_VERIFICA) -> bool:
    return tipo_documento(nome) in estensioni


def _sembra_der(dati: bytes) -> bool:
    """SEQUENCE DER/BER con lunghezza in forma lunga o indefinita: e' l'inizio di una busta CMS."""
    return len(dati) > 1 and dati[0] == 0x30 and dati[1] >= 0x80


def sniff_contenuto(dati: bytes) -> Tuple[str, str]:
    if _sembra_der(dati):
        return "Busta P7M", ".p7m"
    if b'%PDF-' in dati[:1024]:
        return "PDF", ".pdf"
    testa = dati[:300].lstrip(b'\xef\xbb\xbf \r\n\t')
    minuscolo = testa[:15].lower()
    if minuscolo.startswith((b'<!doctype html', b'<html')):
        return "HTML", ".html"
    if testa.startswith(b'<'):
        return "XML", ".xml"
    if dati[:3] == b'\xff\xd8\xff':
        return "JPEG", ".jpg"
    if dati[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG", ".png"
    if dati[:4] in (b'II*\x00', b'MM\x00*'):
        return "TIFF", ".tif"
    if dati[:6] in (b'GIF87a', b'GIF89a'):
        return "GIF", ".gif"
    if dati[:5] == b'{\\rtf':
        return "RTF", ".rtf"
    if dati[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        return "Office 97-2003", ".doc"
    if dati[:6] == b'7z\xbc\xaf\x27\x1c':
        return "7-Zip", ".7z"
    if dati[:4] == b'Rar!':
        return "RAR", ".rar"
    if dati[:2] == b'PK':
        try:
            with zipfile.ZipFile(io.BytesIO(dati)) as z:
                nomi = set(z.namelist())
                if 'word/document.xml' in nomi:
                    return "Word", ".docx"
                if 'xl/workbook.xml' in nomi:
                    return "Excel", ".xlsx"
                if 'ppt/presentation.xml' in nomi:
                    return "PowerPoint", ".pptx"
                if 'mimetype' in nomi:
                    tipo = z.read('mimetype')
                    for chiave, risultato in ((b'opendocument.text', ("ODF Testo", ".odt")),
                                              (b'opendocument.spreadsheet', ("ODF Foglio", ".ods")),
                                              (b'opendocument.presentation', ("ODF Presentazione", ".odp"))):
                        if chiave in tipo:
                            return risultato
        except Exception:
            pass
        return "ZIP", ".zip"
    return "File", ""


_EST_DI_TIPO = {"PDF": {".pdf"}, "JPEG": {".jpg", ".jpeg", ".jpe", ".jfif"}, "PNG": {".png"}, "TIFF": {".tif", ".tiff"},
                "GIF": {".gif"}, "RTF": {".rtf", ".doc"}}


def nome_per_contenuto(filename: str, dati: bytes) -> str:
    """Nome pulito con l'estensione giusta per il contenuto: "Determina n.123.p7m" con un PDF -> "Determina n.123.pdf"."""
    nome = pulisci_nome_file_globale(filename)
    tipo, ext_reale = sniff_contenuto(dati)
    ext = os.path.splitext(nome)[1].lower() if _estensione_vera(nome) else ""
    if ext_reale and ((tipo in _EST_DI_TIPO and ext not in _EST_DI_TIPO[tipo]) or not ext):
        nome += ext_reale
    return nome

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blocco in iter(lambda: f.read(1 << 20), b''):
            h.update(blocco)
    return h.hexdigest()


def fmt_size(n: int) -> str:
    n = float(n or 0)
    for unita in ("B", "KB", "MB", "GB"):
        if n < 1024 or unita == "GB":
            return f"{n:.0f} {unita}" if unita == "B" else f"{n:.1f} {unita}"
        n /= 1024
    return "-"


def dt_locale(dt):
    if dt is None:
        return None
    try:
        return dt.astimezone()
    except Exception:
        return dt


def fmt_data(dt) -> str:
    d = dt_locale(dt)
    return d.strftime("%d/%m/%Y") if d else "N/D"


def fmt_ora(dt) -> str:
    d = dt_locale(dt)
    if not d:
        return "N/D"
    off = d.strftime("%z")
    sfx = f" (UTC{off[:3]}:{off[3:]})" if off else ""
    return d.strftime("%H:%M:%S") + sfx


def fmt_dt(dt) -> str:
    return f"{fmt_data(dt)} {fmt_ora(dt)}" if dt else "N/D"


def tronca(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"




def parse_pdf_date(s) -> Optional[datetime]:
    """Converte una data PDF (D:YYYYMMDDHHmmSS+HH'mm') in datetime consapevole del fuso."""
    if not s:
        return None
    s = str(s).strip()
    if s.startswith("D:"):
        s = s[2:]
    m = re.match(r"(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?(?:(Z)|([+\-])(\d{2})(?:'?(\d{2})'?)?)?", s)
    if not m:
        return None
    try:
        anno, mese, giorno, ore, minuti, sec = [int(x) if x else d for x, d in
                                                  zip(m.groups()[:6], (0, 1, 1, 0, 0, 0))]
        dt = datetime(anno, mese, giorno, ore, minuti, sec)
        if m.group(7):
            return dt.replace(tzinfo=timezone.utc)
        if m.group(8):
            delta = timedelta(hours=int(m.group(9)), minutes=int(m.group(10) or 0))
            return dt.replace(tzinfo=timezone(delta if m.group(8) == '+' else -delta))
        return dt.astimezone()          # fuso assente: si assume quello locale
    except Exception:
        return None


def parse_iso(s) -> Optional[datetime]:
    if not s:
        return None
    try:
        s2 = str(s).strip().replace('Z', '+00:00')
        s2 = re.sub(r'\.(\d+)', lambda m: '.' + (m.group(1) + '000000')[:6], s2)
        dt = datetime.fromisoformat(s2)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def _get(nome_obj, chiave: str) -> str:
    try:
        v = nome_obj.native.get(chiave)
        if isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        return str(v) if v else ""
    except Exception:
        return ""

ORDINE_STATO = {"ok": 0, "none": 1, "warn": 2, "error": 3}


@dataclass
class Controllo:
    nome: str
    stato: str                        # ok / warn / error / none (solo informativo)
    dettaglio: str = ""


@dataclass
class FirmaInfo:
    tipo: str = "Firma"
    formato: str = ""
    livello: int = 0
    firmatario: str = "Sconosciuto"
    identificativo: str = ""
    organizzazione: str = ""
    emittente: str = ""
    seriale: str = ""
    data_firma: Optional[datetime] = None
    fonte_data: str = ""
    data_pdf_m: Optional[datetime] = None
    marca_temporale: Optional[datetime] = None
    marca_valida: Optional[bool] = None
    marca_tsa: str = ""
    valido_dal: Optional[datetime] = None
    valido_al: Optional[datetime] = None
    algo_hash: str = ""
    algo_firma: str = ""
    integrita: Optional[bool] = None
    integrita_msg: str = ""
    stato: str = "none"
    esito: str = ""
    note: List[str] = field(default_factory=list)
    controlli: List[Controllo] = field(default_factory=list)
    cert_der: Optional[bytes] = None
    campo: str = ""
    motivo: str = ""
    luogo: str = ""
    contatto: str = ""
    modifiche: str = ""
    mod_livello: str = ""


@dataclass
class RisultatoDoc:
    percorso: str
    nome: str = ""
    formato: str = "?"
    dimensione: int = 0
    sha256: str = ""
    firme: List[FirmaInfo] = field(default_factory=list)
    stato: str = "none"
    esito: str = ""
    errore: str = ""
    nome_contenuto: str = ""
    tipo_contenuto: str = ""
    livelli: int = 0
    fattura: Optional[dict] = None
    durata: float = 0.0
    verificato: bool = True
    note: List[str] = field(default_factory=list)
    origine: str = ""            # es. "allegato della mail «...»"
    non_eseguita: bool = False   # librerie mancanti: nessuna verifica

    def finalizza(self):
        if self.errore:
            self.stato, self.esito = "error", self.errore
        elif not self.firme:
            self.stato, self.esito = "none", "Nessuna firma digitale presente"
        elif not self.verificato:
            self.stato, self.esito = "none", "Verifica non eseguita (solo estrazione)"
        else:
            peggiore = max(self.firme, key=lambda f: ORDINE_STATO.get(f.stato, 0))
            self.stato, self.esito = peggiore.stato, peggiore.esito


ETICHETTA = {"ok": "Verificato", "warn": "Attenzione", "error": "Non valido", "none": "Senza firma"}


def etichetta_doc(r: RisultatoDoc) -> str:
    return "Non verificato" if (r.non_eseguita or (r.stato == "none" and r.firme)) else ETICHETTA[r.stato]


def etichetta_firma(f: FirmaInfo) -> str:
    return "Non verificata" if f.stato == "none" else ETICHETTA[f.stato]

GLIFO = {"ok": "✅", "warn": "⚠️", "error": "❌", "none": "⚪"}

# Trusted List italiana (AgID, eIDAS): l'elenco ufficiale dei certificatori qualificati è la fonte giusta per
# le radici delle firme. Si riscarica a ogni caricamento dell'archivio (se c'è connessione) e si tiene in cache;
# offline si usa l'ultima copia scaricata, altrimenti il TSL-IT.xml distribuito accanto al programma.
URL_TSL = "https://eidas.agid.gov.it/TL/TSL-IT.xml"
_TSL_TIPI_FIDUCIA = {"CA/QC", "CA/PKC", "TSA/QTST", "TSA"}
_TSL_STATI_RITIRATI = {"withdrawn", "deprecatedatnationallevel"}


def _percorso_cache_tsl() -> str:
    return os.path.join(cartella_cache_app(), "TSL-IT.xml")


def _percorsi_tsl_distribuita() -> List[str]:
    cartella = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    cartelle = [getattr(sys, '_MEIPASS', ''), cartella, os.path.dirname(cartella)]
    if IS_MAC and FROZEN:       # ZimbraViewer.app/Contents/MacOS -> Contents/Resources e cartella che contiene l'app
        contents = os.path.dirname(cartella)
        cartelle += [os.path.join(contents, "Resources"), os.path.dirname(os.path.dirname(contents))]
    return [os.path.join(c, "TSL-IT.xml") for c in cartelle if c]


def leggi_tsl(dati: bytes) -> Tuple[List[Tuple[x509.Certificate, str, Optional[datetime]]], str]:
    """Certificati dei servizi CA/TSA della Trusted List: [(certificato, tipo servizio, data ritiro o None)], descrizione.
    Solleva un'eccezione se il file non è una Trusted List con certificati (download troncato, pagina di errore...)."""
    radice = ET.fromstring(dati)
    if _loc(radice.tag) != "TrustServiceStatusList":
        raise ValueError("non e' una Trusted List")
    numero = emessa = ""
    for e in radice.iter():
        nome = _loc(e.tag)
        if nome == "TSLSequenceNumber" and not numero:
            numero = (e.text or "").strip()
        elif nome == "ListIssueDateTime" and not emessa:
            emessa = (e.text or "").strip()
    certificati = []
    for info in radice.iter():
        if _loc(info.tag) != "ServiceInformation":
            continue
        tipo = stato = inizio = ""
        for c in info:
            nome = _loc(c.tag)
            if nome == "ServiceTypeIdentifier":
                tipo = (c.text or "").strip().split("/Svctype/")[-1]
            elif nome == "ServiceStatus":
                stato = (c.text or "").strip().rsplit("/", 1)[-1]
            elif nome == "StatusStartingTime":
                inizio = (c.text or "").strip()
        if tipo not in _TSL_TIPI_FIDUCIA:
            continue
        ritiro = parse_iso(inizio) if stato in _TSL_STATI_RITIRATI else None
        for e in info.iter():
            if _loc(e.tag) == "X509Certificate" and e.text:
                try:
                    certificati.append((x509.Certificate.load(base64.b64decode("".join(e.text.split()))), tipo, ritiro))
                except Exception:
                    pass
    if not certificati:
        raise ValueError("Trusted List senza certificati")
    d = parse_iso(emessa)
    return certificati, f"Trusted List AgID n. {numero or '?'} del {fmt_data(d) if d else emessa or '?'}"


def carica_tsl() -> Tuple[List[Tuple[x509.Certificate, str, Optional[datetime]]], str]:
    """Scarica la Trusted List AgID (e aggiorna la cache); senza rete usa la cache o la copia distribuita."""
    cache = _percorso_cache_tsl()
    try:
        dati = scarica_url(URL_TSL, 20)
        certificati, descr = leggi_tsl(dati)
        try:
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            with open(cache + ".tmp", "wb") as f:
                f.write(dati)
            os.replace(cache + ".tmp", cache)
        except Exception:
            pass
        return certificati, descr + " (aggiornata online)"
    except Exception:
        pass
    for percorso, origine in [(cache, "copia in cache, rete non disponibile")] + \
                             [(p, "copia distribuita, rete non disponibile") for p in _percorsi_tsl_distribuita()]:
        try:
            with open(percorso, "rb") as f:
                certificati, descr = leggi_tsl(f.read())
            return certificati, f"{descr} ({origine})"
        except Exception:
            continue
    return [], "Trusted List AgID non disponibile (nessuna rete e nessuna copia locale)"


class ArchivioFiducia:
    """Radici attendibili: Trusted List AgID (eIDAS) + archivio di sistema + CA aggiunte dall'utente."""

    def __init__(self):
        self.lock = threading.Lock()
        self.radici: List[x509.Certificate] = []
        self.intermedi: List[x509.Certificate] = []
        self.hash_radici = set()
        self.tsl = {}                  # sha256 -> (tipo servizio, data ritiro o None) dei certificati della Trusted List
        self.tsl_descrizione = ""
        self.cache_http = {}
        self.cache_validazione = {}
        self._lock_chiavi = {}
        self.ricarica()

    def lock_chiave(self, chiave):
        """Un lock per certificato: lo stesso firmatario su mille file si valida una volta sola, anche tra thread diversi."""
        with self.lock:
            return self._lock_chiavi.setdefault(chiave, threading.Lock())

    @staticmethod
    def _carica_file(percorso: str) -> List[x509.Certificate]:
        with open(percorso, 'rb') as f:
            dati = f.read()
        if b'-----BEGIN' in dati:     # PEM, anche con commenti in testa (raccolte delle distribuzioni Linux)
            return [x509.Certificate.load(der) for _, _, der in pem.unarmor(dati, multiple=True)]
        return [x509.Certificate.load(dati)]

    def _radici_di_sistema(self):
        """CA attendibili del sistema: portachiavi di macOS, raccolta della distribuzione Linux, in mancanza certifi."""
        radici = []
        if IS_MAC:
            for keychain in ("/System/Library/Keychains/SystemRootCertificates.keychain", "/Library/Keychains/System.keychain"):
                try:
                    r = subprocess.run(["/usr/bin/security", "find-certificate", "-a", "-p", keychain],
                                       capture_output=True, timeout=20, env=ambiente_esterno())
                    if r.returncode == 0 and r.stdout:
                        radici.extend(x509.Certificate.load(der) for _, _, der in pem.unarmor(r.stdout, multiple=True))
                except Exception:
                    pass
        else:
            for f in FILE_CA_SISTEMA:
                if os.path.isfile(f):
                    try:
                        trovati = self._carica_file(f)
                    except Exception:
                        continue
                    if trovati:
                        radici.extend(trovati)
                        break
        if not radici:
            try:
                import certifi
                radici.extend(self._carica_file(certifi.where()))
            except Exception:
                pass
        return radici

    def ricarica(self):
        radici, intermedi, tsl = [], [], {}
        certificati_tsl, descrizione_tsl = carica_tsl()
        for c, tipo, ritiro in certificati_tsl:
            radici.append(c)
            tsl[hashlib.sha256(c.dump()).hexdigest()] = (tipo, ritiro)
        if sys.platform == "win32":
            for store, dest in (("ROOT", radici), ("CA", intermedi)):
                try:
                    for cert_bytes, encoding, _trust in ssl.enum_certificates(store):
                        if encoding == "x509_asn":
                            try:
                                dest.append(x509.Certificate.load(cert_bytes))
                            except Exception:
                                pass
                except Exception:
                    pass
        else:
            radici.extend(self._radici_di_sistema())
        for p in IMP["radici_extra"]:
            try:
                radici.extend(self._carica_file(p))
            except Exception:
                pass
        visti, finali = set(), []
        for c in radici:
            h = hashlib.sha256(c.dump()).hexdigest()
            if h not in visti:
                visti.add(h)
                finali.append(c)
        with self.lock:
            self.radici, self.intermedi = finali, intermedi
            self.hash_radici = visti
            self.tsl, self.tsl_descrizione = tsl, descrizione_tsl
            self.cache_validazione.clear()

    def ancora_tsl(self, cert, extra):
        """Primo certificato della catena (il firmatario escluso) presente nella Trusted List, o None."""
        corrente = cert
        for _ in range(8):
            nxt = self._cerca_emittente(corrente, list(extra) + self.intermedi + self.radici)
            if nxt is None:
                return None
            if hashlib.sha256(nxt.dump()).hexdigest() in self.tsl:
                return nxt
            if nxt.issuer == nxt.subject:
                return None
            corrente = nxt
        return None

    def scarica(self, url: str) -> Optional[bytes]:
        if url in self.cache_http:
            return self.cache_http[url]
        dati = None
        if url.lower().startswith(("http://", "https://")):
            try:
                dati = scarica_url(url, 6)
            except Exception:
                dati = None
        self.cache_http[url] = dati
        return dati

    @staticmethod
    def _cerca_emittente(cert, pool):
        aki = None
        try:
            aki = cert.authority_key_identifier
        except Exception:
            pass
        for c in pool:
            try:
                if c.subject != cert.issuer and c.subject.dump() != cert.issuer.dump():
                    continue
                if aki and c.key_identifier and aki != c.key_identifier:
                    continue
                return c
            except Exception:
                continue
        return None

    def completa_catena(self, cert, extra_certs) -> List[x509.Certificate]:
        """Risale la catena usando busta, archivio di sistema e AIA. Restituisce i certificati utili."""
        trovati = list(extra_certs)
        corrente = cert
        for _ in range(6):
            if corrente.issuer == corrente.subject:
                break
            emittente = self._cerca_emittente(corrente, trovati + self.intermedi + self.radici)
            if emittente is not None:
                corrente = emittente
                continue
            nuovo = None
            try:
                aia = corrente.authority_information_access_value
            except Exception:
                aia = None
            for ad in (aia or []):
                try:
                    if ad['access_method'].native != 'ca_issuers':
                        continue
                    dati = self.scarica(ad['access_location'].native)
                    if not dati:
                        continue
                    try:
                        nuovo = x509.Certificate.load(dati)
                    except Exception:
                        sd = cms.ContentInfo.load(dati)['content']
                        cand = [c.chosen for c in sd['certificates'] if c.name == 'certificate']
                        nuovo = self._cerca_emittente(corrente, cand)
                    if nuovo is not None:
                        break
                except Exception:
                    continue
            if nuovo is None:
                break
            trovati.append(nuovo)
            corrente = nuovo
        return trovati

    def radice_catena(self, cert, extra):
        corrente = cert
        for _ in range(8):
            if corrente.issuer == corrente.subject:
                return corrente
            nxt = self._cerca_emittente(corrente, list(extra) + self.intermedi + self.radici)
            if nxt is None:
                return None
            corrente = nxt
        return None

_ARCHIVIO = None
_ARCHIVIO_LOCK = threading.Lock()

def archivio_fiducia():
    """Archivio delle radici attendibili, caricato al primo uso (non rallenta l'avvio del programma)."""
    global _ARCHIVIO
    with _ARCHIVIO_LOCK:
        if _ARCHIVIO is None:
            _ARCHIVIO = ArchivioFiducia()
    return _ARCHIVIO


def carica_cms(raw: bytes, consenti_b64: bool = False):
    if raw[:1] != b'\x30':
        try:
            testa = raw.lstrip()
            if testa.startswith(b'-----BEGIN'):
                _, _, raw = pem.unarmor(testa)
            elif consenti_b64:
                raw = base64.b64decode(b''.join(raw.split()), validate=True)
        except Exception:
            pass
    return cms.ContentInfo.load(raw)


def e_busta_cms(raw: bytes):
    try:
        info = carica_cms(raw, raw.lstrip()[:1] == b'M')       # le buste base64 iniziano sempre per "M"
        return info if info['content_type'].native == 'signed_data' else None
    except Exception:
        return None


def byte_ottetti(v) -> bytes:
    """Byte di un OCTET STRING, anche costruito o a lunghezza indefinita."""
    try:
        return v.__bytes__()
    except Exception:
        return v.contents

def certificati_da_sd(sd) -> List[x509.Certificate]:
    try:
        campo = sd['certificates']
        if isinstance(campo, Void):
            return []
        return [c.chosen for c in campo if c.name == 'certificate']
    except Exception:
        return []


def _stessi_nomi(a, b) -> bool:
    try:
        return a == b or a.dump() == b.dump()
    except Exception:
        return False


def trova_cert_signer(signer_info, certs):
    try:
        sid = signer_info['sid']
        if sid.name == 'issuer_and_serial_number':
            emittente = sid.chosen['issuer']
            seriale = sid.chosen['serial_number'].native
            for c in certs:
                if c.serial_number == seriale and _stessi_nomi(c.issuer, emittente):
                    return c
            for c in certs:
                if c.serial_number == seriale:
                    return c
        elif sid.name == 'subject_key_identifier':
            ski = sid.chosen.native
            for c in certs:
                if c.key_identifier == ski:
                    return c
    except Exception:
        pass
    return None


def gen_time_da_eci(eci):
    try:
        return tsp.TSTInfo.load(byte_ottetti(eci['content']))['gen_time'].native
    except Exception:
        return None

def estrai_tempi(signer_info):
    """(signing_time dichiarato, gen_time della marca temporale)"""
    st = marca = None
    try:
        sa = signer_info['signed_attrs']
        if not isinstance(sa, Void):
            for a in sa:
                if a['type'].native == 'signing_time':
                    st = a['values'][0].native
                    break
    except Exception:
        pass
    try:
        ua = signer_info['unsigned_attrs']
        if not isinstance(ua, Void):
            for a in ua:
                if a['type'].dotted == OID_TIMESTAMP_TOKEN:
                    tok = a['values'][0]
                    marca = gen_time_da_eci(tok['content']['encap_content_info'])
                    break
    except Exception:
        pass
    return st, marca


def controfirme(signer_info):
    out = []
    try:
        ua = signer_info['unsigned_attrs']
        if not isinstance(ua, Void):
            for a in ua:
                if a['type'].dotted == OID_COUNTER_SIGNATURE:
                    out.extend(list(a['values']))
    except Exception:
        pass
    return out


def algoritmi(signer_info) -> Tuple[str, str]:
    h = s = ""
    try:
        h = signer_info['digest_algorithm']['algorithm'].native
    except Exception:
        pass
    try:
        s = signer_info['signature_algorithm'].signature_algo
    except Exception:
        try:
            s = signer_info['signature_algorithm']['algorithm'].native
        except Exception:
            pass
    return str(h), str(s)


_HASH_CLASSI = ({'sha1': hashes.SHA1, 'sha224': hashes.SHA224, 'sha256': hashes.SHA256, 'sha384': hashes.SHA384,
                 'sha512': hashes.SHA512, 'sha3_224': hashes.SHA3_224, 'sha3_256': hashes.SHA3_256,
                 'sha3_384': hashes.SHA3_384, 'sha3_512': hashes.SHA3_512} if HAS_CRYPTO else {})


def _verifica_firma_grezza(chiave, firma: bytes, dati: bytes, sig_algo, classe_hash):
    tipo = sig_algo.signature_algo
    try:
        classe_h = _HASH_CLASSI.get(sig_algo.hash_algo, classe_hash)
    except Exception:
        classe_h = classe_hash
    if tipo == 'rsassa_pkcs1v15':
        chiave.verify(firma, dati, padding.PKCS1v15(), classe_h())
    elif tipo == 'rsassa_pss':
        p = sig_algo['parameters']
        h_pss = _HASH_CLASSI.get(p['hash_algorithm']['algorithm'].native, classe_h)
        h_mgf = _HASH_CLASSI.get(p['mask_gen_algorithm']['parameters']['algorithm'].native, h_pss)
        chiave.verify(firma, dati, padding.PSS(mgf=padding.MGF1(h_mgf()), salt_length=p['salt_length'].native), h_pss())
    elif tipo == 'ecdsa':
        chiave.verify(firma, dati, ec.ECDSA(classe_h()))
    elif tipo == 'dsa':
        chiave.verify(firma, dati, classe_h())
    elif tipo in ('ed25519', 'ed448'):
        chiave.verify(firma, dati)
    else:
        raise NotImplementedError(tipo)


def verifica_integrita(signer_info, cert, payload: Optional[bytes]) -> Tuple[Optional[bool], str]:
    """Controlla digest del contenuto e firma. (True/False/None, messaggio)"""
    if not HAS_CRYPTO:
        return None, "libreria 'cryptography' non disponibile"
    if payload is None:
        return None, "firma detached: documento originale non disponibile"
    try:
        algo = signer_info['digest_algorithm']['algorithm'].native
        classe_hash = _HASH_CLASSI.get(algo)
        if classe_hash is None:
            return None, f"algoritmo di digest '{algo}' non supportato"
        sa = signer_info['signed_attrs']
        if isinstance(sa, Void):
            candidati = [payload]
        else:
            md = None
            for a in sa:
                if a['type'].native == 'message_digest':
                    md = a['values'][0].native
                    break
            if md is None:
                return False, "attributo message-digest mancante"
            if hashlib.new(algo, payload).digest() != md:
                return False, "l'impronta del contenuto non corrisponde: documento alterato dopo la firma"
            # prima la codifica originale (alcuni software non ordinano il SET), poi quella DER canonica
            candidati = [b'\x31' + sa.dump()[1:]]
            canonica = b'\x31' + sa.dump(force=True)[1:]
            if canonica != candidati[0]:
                candidati.append(canonica)
        firma = signer_info['signature'].native
        chiave = serialization.load_der_public_key(cert['tbs_certificate']['subject_public_key_info'].dump())
        for dati in candidati:
            try:
                _verifica_firma_grezza(chiave, firma, dati, signer_info['signature_algorithm'], classe_hash)
                return True, "impronta e firma crittografica verificate: documento integro"
            except InvalidSignature:
                continue
        return False, "firma crittografica non valida: documento alterato o firma corrotta"
    except NotImplementedError as e:
        return None, f"algoritmo di firma '{e}' non supportato"
    except Exception as e:
        return None, f"verifica non eseguibile ({type(e).__name__})"


def verifica_legame_certificato(signer_info, cert) -> Controllo:
    """Attributo ESS signing-certificate: lega la firma proprio a quel certificato."""
    nome = "Legame firma-certificato"
    try:
        sa = signer_info['signed_attrs']
        if not isinstance(sa, Void):
            for a in sa:
                t = a['type'].native
                if t in ('signing_certificate', 'signing_certificate_v2'):
                    primo = a['values'][0]['certs'][0]
                    algo = 'sha1' if t == 'signing_certificate' else primo['hash_algorithm']['algorithm'].native
                    if hashlib.new(algo, cert.dump()).digest() == primo['cert_hash'].native:
                        return Controllo(nome, "ok", "l'attributo signing-certificate corrisponde al certificato usato")
                    return Controllo(nome, "error", "l'attributo signing-certificate indica un certificato diverso da quello usato")
    except Exception as e:
        return Controllo(nome, "none", f"attributo non leggibile ({type(e).__name__})")
    return Controllo(nome, "none", "attributo signing-certificate assente")


def token_marca(signer_info):
    try:
        ua = signer_info['unsigned_attrs']
        if not isinstance(ua, Void):
            for a in ua:
                if a['type'].dotted == OID_TIMESTAMP_TOKEN:
                    return a['values'][0]
    except Exception:
        pass
    return None


async def verifica_marca(token, dati_marcati: Optional[bytes]) -> Tuple[Optional[bool], Optional[datetime], str, str]:
    """Verifica una marca RFC 3161: impronta dei dati marcati, firma del token, certificato TSA.
    -> (valida, istante, TSA, spiegazione)"""
    quando, tsa = None, ""
    try:
        sd = token['content']
        eci = sd['encap_content_info']
        contenuto = byte_ottetti(eci['content'])
        info = tsp.TSTInfo.load(contenuto)
        quando = info['gen_time'].native
        imprint = info['message_imprint']
        algo = imprint['hash_algorithm']['algorithm'].native
        if dati_marcati is not None and hashlib.new(algo, dati_marcati).digest() != imprint['hashed_message'].native:
            return False, quando, tsa, "l'impronta della marca non corrisponde alla firma: marca non valida"
        si = sd['signer_infos'][0]
        certs = certificati_da_sd(sd)
        cert = trova_cert_signer(si, certs)
        if cert is None:
            return None, quando, tsa, "certificato della TSA non incluso nella marca"
        tsa = _get(cert.subject, 'common_name') or _get(cert.subject, 'organization_name')
        integra, msg = verifica_integrita(si, cert, contenuto)
        if integra is False:
            return False, quando, tsa, f"firma della marca non valida ({msg})"
        if integra is None:
            return None, quando, tsa, f"firma della marca non verificabile ({msg})"
        controlli = await valida_certificato(cert, certs, quando, tsa=True)
        peggiore = next((c for c in controlli if c.stato == "error"), None)
        if peggiore is not None:
            return False, quando, tsa, f"certificato TSA non attendibile: {peggiore.dettaglio}"
        return True, quando, tsa, f"marca valida emessa da {tsa or 'TSA'} il {fmt_dt(quando)}"
    except Exception as e:
        return None, quando, tsa, f"marca non verificabile ({type(e).__name__})"

def popola_da_cert(fi: FirmaInfo, cert: x509.Certificate):
    fi.cert_der = cert.dump()
    cn = _get(cert.subject, 'common_name')
    nome = " ".join(x for x in (_get(cert.subject, 'given_name'), _get(cert.subject, 'surname')) if x)
    fi.organizzazione = _get(cert.subject, 'organization_name')
    fi.firmatario = cn or nome or fi.organizzazione or "Sconosciuto"
    fi.identificativo = _get(cert.subject, 'serial_number')
    fi.emittente = _get(cert.issuer, 'common_name') or _get(cert.issuer, 'organization_name')
    fi.seriale = format(cert.serial_number, 'X')
    try:
        fi.valido_dal = cert['tbs_certificate']['validity']['not_before'].native
        fi.valido_al = cert['tbs_certificate']['validity']['not_after'].native
    except Exception:
        pass


_QC_CONFORME = bytes.fromhex("0606040 08E460101".replace(" ", ""))
_QC_QSCD = bytes.fromhex("0606040 08E460104".replace(" ", ""))


def controllo_tipo_certificato(cert) -> Controllo:
    der = cert.dump()
    if _QC_CONFORME in der:
        testo = "certificato qualificato" + (" su dispositivo sicuro (QSCD)" if _QC_QSCD in der else "")
    else:
        testo = "certificato non dichiarato come qualificato"
    try:
        ku = cert.key_usage_value
        if ku is not None and 'non_repudiation' in ku.native:
            testo += ", abilitato alla non ripudiabilità"
    except Exception:
        pass
    return Controllo("Tipo di certificato", "none", testo)


def controllo_algoritmi(fi: FirmaInfo, cert) -> Controllo:
    deboli = []
    if fi.algo_hash.lower() in ('md5', 'md2', 'sha1'):
        deboli.append(f"impronta {fi.algo_hash.upper()}")
    try:
        if cert.public_key.algorithm == 'rsa' and cert.public_key.bit_size < 2048:
            deboli.append(f"chiave RSA a {cert.public_key.bit_size} bit")
    except Exception:
        pass
    testo = " / ".join(x for x in (fi.algo_hash, fi.algo_firma) if x)
    if deboli:
        return Controllo("Algoritmi", "warn", "algoritmi oggi considerati deboli: " + ", ".join(deboli))
    return Controllo("Algoritmi", "ok", testo or "non indicati")


def controllo_tempi(fi: FirmaInfo) -> Optional[Controllo]:
    d = fi.data_firma
    if not d or fi.marca_valida:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    if d > datetime.now(timezone.utc) + timedelta(minutes=5):
        return Controllo("Data di firma", "warn", f"la data dichiarata ({fmt_dt(d)}) è nel futuro")
    if fi.valido_dal and d < fi.valido_dal:
        return Controllo("Data di firma", "warn", f"la data dichiarata ({fmt_dt(d)}) precede l'inizio di validità del certificato")
    if fi.valido_al and d > fi.valido_al:
        return Controllo("Data di firma", "warn", f"la data dichiarata ({fmt_dt(d)}) è successiva alla scadenza del certificato")
    return None


async def _valida_cert_reale(cert, certs_busta, momento_firma, moment, marca, tsa) -> List[Controllo]:
    c: List[Controllo] = []
    ora = datetime.now(timezone.utc)
    try:
        nb = cert['tbs_certificate']['validity']['not_before'].native
        na = cert['tbs_certificate']['validity']['not_after'].native
    except Exception:
        nb = na = None
    scaduto = bool(na and na < ora)
    futuro = bool(nb and nb > ora)
    revoca_attiva = bool(IMP["revoca"])
    extra = await asyncio.to_thread(archivio_fiducia().completa_catena, cert, list(certs_busta))
    ctx = ValidationContext(trust_roots=list(archivio_fiducia().radici), other_certs=list(archivio_fiducia().intermedi) + extra,
                            allow_fetching=revoca_attiva, revocation_mode="soft-fail", moment=moment,
                            # a una data passata OCSP/CRL sono per forza successive: vanno accettate lo stesso
                            retroactive_revinfo=bool(moment))
    try:
        validatore = CertificateValidator(cert, validation_context=ctx)
        if tsa:
            await validatore.async_validate_usage(set(), extended_key_usage={'time_stamping'})
        else:
            await validatore.async_validate_usage(set())
    except Exception as e:
        nome_err = type(e).__name__
        msg = (str(e).strip().splitlines() or [nome_err])[0]
        if 'Revoked' in nome_err:
            quando = getattr(e, 'revocation_dt', None)
            motivo = getattr(getattr(e, 'reason', None), 'human_friendly', '')
            c.append(Controllo("Revoca", "error", "certificato REVOCATO" + (f" il {fmt_dt(quando)}" if quando else "")
                               + (f" ({motivo})" if motivo else "")))
        elif futuro:
            c.append(Controllo("Validità del certificato", "error", f"non ancora valido (dal {fmt_data(nb)})"))
        elif 'Expired' in nome_err or (scaduto and not moment):
            c.append(Controllo("Validità del certificato", "error", f"scaduto il {fmt_data(na)}, nessuna data utile per valutarlo"))
        elif isinstance(e, PathValidationError) or 'PathBuilding' in nome_err or 'Validation' in nome_err:
            radice = archivio_fiducia().radice_catena(cert, extra)
            if radice is not None and hashlib.sha256(radice.dump()).hexdigest() not in archivio_fiducia().hash_radici:
                nome_radice = _get(radice.subject, 'common_name') or _get(radice.subject, 'organization_name')
                c.append(Controllo("Catena di fiducia", "warn", f"catena completa fino a «{nome_radice}», radice non presente "
                                   "tra quelle attendibili (si può aggiungere in Impostazioni)"))
            else:
                emittente = _get(cert.issuer, 'common_name') or _get(cert.issuer, 'organization_name') or "sconosciuto"
                if 'PathBuilding' in nome_err:
                    c.append(Controllo("Catena di fiducia", "error", f"l'emittente «{emittente}» non è tra le autorità attendibili "
                                       "(Trusted List AgID, archivio di sistema, CA aggiunte)"))
                else:
                    c.append(Controllo("Catena di fiducia", "error", f"non verificata: {msg}"))
        else:
            c.append(Controllo("Validazione del certificato", "warn", f"verifica parziale: {msg}"))
        return c
    finally:
        try:
            await ctx.aclose()
        except Exception:
            pass

    periodo = f"dal {fmt_data(nb)} al {fmt_data(na)}"
    if tsa:
        c.append(Controllo("Validità del certificato", "ok", f"valido al momento della marca ({periodo})"))
    elif moment and marca:
        c.append(Controllo("Validità del certificato", "ok", f"valido alla data della marca temporale, {fmt_dt(moment)} ({periodo})"))
    elif moment:
        c.append(Controllo("Validità del certificato", "warn", f"scaduto il {fmt_data(na)}: valido solo alla data di firma "
                           "dichiarata dal firmatario, senza marca temporale opponibile"))
    else:
        c.append(Controllo("Validità del certificato", "ok", f"in corso di validità ({periodo})"))
    ancora = archivio_fiducia().ancora_tsl(cert, extra)
    if ancora is not None:
        tipo, ritiro = archivio_fiducia().tsl[hashlib.sha256(ancora.dump()).hexdigest()]
        nome_ca = _get(ancora.subject, 'common_name') or _get(ancora.subject, 'organization_name')
        quando = moment or momento_firma or ora
        if quando.tzinfo is None:
            quando = quando.replace(tzinfo=timezone.utc)
        c.append(Controllo("Catena di fiducia", "ok", f"verificata fino a «{nome_ca}»"))
        if ritiro and quando >= ritiro:
            c.append(Controllo("Trusted List AgID", "warn", f"certificatore «{nome_ca}» ritirato dalla lista il {fmt_data(ritiro)}, prima della firma"))
        else:
            c.append(Controllo("Trusted List AgID", "ok", f"certificatore qualificato eIDAS ({tipo})"))
    else:
        c.append(Controllo("Catena di fiducia", "ok", "verificata sull'archivio di sistema o sulle CA aggiunte"))
        c.append(Controllo("Trusted List AgID", "none", "certificatore non presente nella lista"))
    if not revoca_attiva:
        c.append(Controllo("Revoca", "none", "controllo OCSP/CRL disattivato nelle impostazioni"))
    else:
        try:
            mancate = list(ctx.soft_fail_exceptions)
        except Exception:
            mancate = []
        if mancate:
            c.append(Controllo("Revoca", "warn", "stato non determinabile: server OCSP/CRL non raggiungibili o senza risposta utile"))
        else:
            c.append(Controllo("Revoca", "ok", "nessuna revoca risultante da OCSP/CRL"))
    return c


async def valida_certificato(cert, certs_busta, momento_firma, marca=None, tsa=False) -> List[Controllo]:
    """Elenco dei controlli sul certificato. marca: istante di una marca GIA' verificata; tsa: certificato di una TSA."""
    ora = datetime.now(timezone.utc)
    try:
        scaduto = cert['tbs_certificate']['validity']['not_after'].native < ora
    except Exception:
        scaduto = False
    if tsa:
        moment = momento_firma
    elif marca:
        moment = marca                      # data certa: revoche e scadenze successive non contano
    elif scaduto and momento_firma and IMP["valida_data_firma"]:
        moment = momento_firma
    else:
        moment = None
    chiave = (hashlib.sha256(cert.dump()).hexdigest(), moment.isoformat() if moment else "", bool(IMP["revoca"]), bool(marca), tsa)
    with archivio_fiducia().lock_chiave(chiave):     # lock tra thread: ogni verifica ha il suo
        if chiave in archivio_fiducia().cache_validazione:
            return list(archivio_fiducia().cache_validazione[chiave])
        controlli = await _valida_cert_reale(cert, certs_busta, momento_firma, moment, marca, tsa)
        if len(archivio_fiducia().cache_validazione) > 3000:
            archivio_fiducia().cache_validazione.clear()
        archivio_fiducia().cache_validazione[chiave] = list(controlli)
    return controlli


def controllo_integrita(fi: FirmaInfo) -> Controllo:
    return Controllo("Integrità del documento", {True: "ok", False: "error", None: "warn"}[fi.integrita],
                     fi.integrita_msg or "non verificata")


def controllo_marca(fi: FirmaInfo, msg: str) -> Controllo:
    if fi.marca_temporale is None and not msg:
        return Controllo("Marca temporale", "none", "assente: la data di firma è solo dichiarata")
    return Controllo("Marca temporale", {True: "ok", False: "warn", None: "warn"}[fi.marca_valida], msg)


def combina_esito(fi: FirmaInfo):
    """L'esito della firma e' il primo controllo peggiore: cosi' la tabella dice sempre il motivo."""
    for s in ("error", "warn"):
        c = next((x for x in fi.controlli if x.stato == s), None)
        if c is not None:
            fi.stato, fi.esito = s, f"{c.nome}: {c.dettaglio}"
            return
    fi.stato = "ok"
    fi.esito = "Firma valida: integrità, certificato e catena di fiducia verificati"


# ============================================================ MOTORE: CAdES
async def _analizza_signer(si, certs, payload, livello, tipo="Firma", formato="CAdES", valida=True) -> FirmaInfo:
    fi = FirmaInfo(tipo=tipo, formato=formato, livello=livello)
    fi.algo_hash, fi.algo_firma = algoritmi(si)
    st, marca = estrai_tempi(si)
    if st:
        fi.data_firma, fi.fonte_data = st, "Attributo signing-time della firma"
    fi.marca_temporale = marca
    if marca and not fi.data_firma:
        fi.data_firma, fi.fonte_data = marca, "Marca temporale (RFC 3161)"
    cert = trova_cert_signer(si, certs)
    if cert is None:
        fi.stato, fi.esito = "error", "Certificato del firmatario non presente nella busta"
        fi.controlli.append(Controllo("Certificato", "error", "non presente nella busta"))
        return fi
    popola_da_cert(fi, cert)
    if not valida:
        fi.esito = "Verifica non eseguita (solo estrazione)"
        return fi
    fi.integrita, fi.integrita_msg = verifica_integrita(si, cert, payload)
    fi.controlli.append(controllo_integrita(fi))
    fi.controlli.append(verifica_legame_certificato(si, cert))
    msg_marca = ""
    token = token_marca(si)
    if token is not None:
        fi.marca_valida, istante, fi.marca_tsa, msg_marca = await verifica_marca(token, si['signature'].native)
        fi.marca_temporale = istante or fi.marca_temporale
    fi.controlli.append(controllo_marca(fi, msg_marca))
    fi.controlli += await valida_certificato(cert, certs, fi.data_firma, fi.marca_temporale if fi.marca_valida else None)
    fi.controlli.append(controllo_algoritmi(fi, cert))
    fi.controlli.append(controllo_tipo_certificato(cert))
    t = controllo_tempi(fi)
    if t is not None:
        fi.controlli.append(t)
    combina_esito(fi)
    return fi


async def _firma_con_controfirme(si, certs, payload, livello, tipo, valida, prof=0) -> List[FirmaInfo]:
    out = [await _analizza_signer(si, certs, payload, livello, tipo=tipo, valida=valida)]
    if prof < 4:
        for ctr in controfirme(si):              # la controfirma firma il valore della firma madre
            out += await _firma_con_controfirme(ctr, certs, si['signature'].native, livello, "Controfirma", valida, prof + 1)
    return out


async def analizza_signed_data(sd, payload, livello, valida=True) -> List[FirmaInfo]:
    certs = certificati_da_sd(sd)
    out = []
    for si in sd['signer_infos']:
        out += await _firma_con_controfirme(si, certs, payload, livello, "Firma", valida)
    return out


def trova_originale_detached(percorso: str) -> Optional[str]:
    """Per una firma detached cerca accanto il file firmato: "doc.pdf.p7s" -> "doc.pdf"."""
    cartella, nome = os.path.split(percorso)
    candidato = pulisci_nome_file_globale(nome)
    p = os.path.join(cartella, candidato)
    if candidato != nome and os.path.isfile(p):
        return p
    return None

async def analizza_p7m(ris: RisultatoDoc, contenuto: bytes, valida: bool = True):
    """analizza_p7m del P7MReader, sui byte invece che sul file."""
    livello = 0
    payload_bytes = None
    while True:
        try:
            info = carica_cms(contenuto, consenti_b64=(contenuto.lstrip()[:1] == b'M'))
        except Exception:
            ris.errore = "Decodifica fallita: il file non è una busta CMS/PKCS#7 valida"
            return
        if info['content_type'].native != 'signed_data':
            ris.errore = "Busta corrotta: tipo CMS diverso da SignedData"
            return
        sd = info['content']
        payload = sd['encap_content_info']['content']
        payload_bytes = None if isinstance(payload, Void) else byte_ottetti(payload)
        detached = payload_bytes is None
        if detached:
            originale = trova_originale_detached(ris.percorso)
            if originale:
                with open(originale, 'rb') as f:
                    payload_bytes = f.read()
                ris.note.append(f"Firma detached verificata sul file accanto: {os.path.basename(originale)}")
            else:
                ris.note.append("Firma detached: il documento firmato non è incluso e non è stato trovato accanto")
        ris.firme.extend(await analizza_signed_data(sd, payload_bytes, livello, valida))
        if not detached and payload_bytes and livello < MAX_ANNIDAMENTO and IMP["estrai_annidati"] and e_busta_cms(payload_bytes):
            contenuto = payload_bytes
            livello += 1
            ris.livelli = livello
            continue
        break
    ris.nome_contenuto = pulisci_nome_file_globale(ris.nome)
    if payload_bytes:
        ris.tipo_contenuto = sniff_contenuto(payload_bytes)[0]
        ris.nome_contenuto = nome_per_contenuto(ris.nome, payload_bytes)
        if ris.tipo_contenuto == "XML" and len(payload_bytes) < 30_000_000:
            ris.fattura = riepilogo_fattura(payload_bytes)

def _pdf_val(obj, chiave: str) -> str:
    try:
        v = obj[chiave]
        return str(v) if v is not None else ""
    except Exception:
        return ""


def descrivi_modifiche(status) -> Tuple[str, str]:
    dr = getattr(status, 'diff_result', None)
    cov = getattr(getattr(status, 'coverage', None), 'name', None)
    if dr is not None and type(dr).__name__ == 'SuspiciousModification':
        return "error", "Il documento risulta MODIFICATO dopo la firma"
    lvl = getattr(getattr(status, 'modification_level', None), 'name', None)
    if cov == 'ENTIRE_FILE':
        return "ok", "La firma copre l'intero file: documento non modificato dopo la firma"
    if cov == 'ENTIRE_REVISION':
        if lvl in (None, 'NONE'):
            return "ok", "Documento non modificato dopo la firma"
        if lvl in ('LTA_UPDATES', 'FORM_FILLING', 'ANNOTATIONS'):
            etichette = {'LTA_UPDATES': "aggiornamenti di validazione a lungo termine",
                         'FORM_FILLING': "compilazione di moduli", 'ANNOTATIONS': "annotazioni"}
            return "warn", f"Dopo la firma sono state aggiunte modifiche consentite ({etichette[lvl]})"
        return "error", "Il documento risulta MODIFICATO dopo la firma"
    if cov:
        return "warn", f"La firma non copre l'intero file (copertura: {cov.lower().replace('_', ' ')})"
    return "", ""


async def _firma_pdf(sig, valida=True) -> FirmaInfo:
    fi = FirmaInfo(formato="PAdES")
    obj = sig.sig_object
    is_ts = 'DocTimeStamp' in str(getattr(sig, 'sig_object_type', ''))
    fi.tipo = "Marca temporale del documento" if is_ts else "Firma"
    fi.campo = str(getattr(sig, 'field_name', '') or '')
    fi.motivo, fi.luogo = _pdf_val(obj, '/Reason'), _pdf_val(obj, '/Location')
    fi.contatto = _pdf_val(obj, '/ContactInfo')
    sd = sig.signed_data
    certs = certificati_da_sd(sd)
    si = sd['signer_infos'][0]
    fi.algo_hash, fi.algo_firma = algoritmi(si)
    st, marca = estrai_tempi(si)
    if is_ts:
        marca = gen_time_da_eci(sd['encap_content_info']) or marca
    try:
        attr = getattr(sig, 'self_reported_timestamp', None) or st
    except Exception:
        attr = st
    m = parse_pdf_date(_pdf_val(obj, '/M'))
    fi.data_pdf_m, fi.marca_temporale = m, marca
    if is_ts and marca:
        fi.data_firma, fi.fonte_data = marca, "Marca temporale (RFC 3161)"
    elif attr:
        fi.data_firma, fi.fonte_data = attr, "Attributo signing-time della firma"
    elif m:
        fi.data_firma, fi.fonte_data = m, "Data /M del dizionario di firma PDF"
    elif marca:
        fi.data_firma, fi.fonte_data = marca, "Marca temporale (RFC 3161)"
    if attr and m and abs((attr - m).total_seconds()) > 300:
        fi.note.append("La data /M del PDF differisce dall'attributo signing-time di oltre 5 minuti")
    cert = trova_cert_signer(si, certs)
    if cert is not None:
        popola_da_cert(fi, cert)
    if not valida:
        fi.esito = "Verifica non eseguita (solo estrazione)"
        return fi

    # integrita' (digest + firma + analisi modifiche) tramite pyHanko; la fiducia si valuta a parte
    ctx_vuoto = ValidationContext(trust_roots=[], allow_fetching=False)
    try:
        if is_ts and async_validate_pdf_timestamp:
            status = await async_validate_pdf_timestamp(sig, validation_context=ctx_vuoto)
        elif async_validate_pdf_signature:
            status = await async_validate_pdf_signature(sig, signer_validation_context=ctx_vuoto)
        elif validate_pdf_signature:
            status = await asyncio.to_thread(validate_pdf_signature, sig)
        else:
            status = None
        if status is not None:
            fi.integrita = bool(status.intact and status.valid)
            fi.integrita_msg = ("impronta e firma crittografica verificate" if fi.integrita
                                else "impronta o firma crittografica non valide: documento alterato o firma corrotta")
            fi.mod_livello, fi.modifiche = descrivi_modifiche(status)
        else:
            fi.integrita_msg = "motore di verifica PDF non disponibile"
    except Exception as e:
        fi.integrita, fi.integrita_msg = None, f"verifica non eseguibile ({type(e).__name__})"
    fi.controlli.append(controllo_integrita(fi))
    if fi.modifiche:
        fi.controlli.append(Controllo("Modifiche dopo la firma", fi.mod_livello or "none", fi.modifiche))

    if cert is None:
        fi.controlli.append(Controllo("Certificato", "error", "non presente nella firma"))
        combina_esito(fi)
        return fi
    msg_marca = ""
    if is_ts:
        fi.marca_valida = fi.integrita
        msg_marca = f"marca del documento: {fi.integrita_msg}"
    else:
        fi.controlli.append(verifica_legame_certificato(si, cert))
        token = token_marca(si)
        if token is not None:
            fi.marca_valida, istante, fi.marca_tsa, msg_marca = await verifica_marca(token, si['signature'].native)
            fi.marca_temporale = istante or fi.marca_temporale
    fi.controlli.append(controllo_marca(fi, msg_marca))
    if is_ts:
        fi.controlli += await valida_certificato(cert, certs, fi.data_firma, tsa=True)
    else:
        fi.controlli += await valida_certificato(cert, certs, fi.data_firma, fi.marca_temporale if fi.marca_valida else None)
    fi.controlli.append(controllo_algoritmi(fi, cert))
    if not is_ts:
        fi.controlli.append(controllo_tipo_certificato(cert))
        t = controllo_tempi(fi)
        if t is not None:
            fi.controlli.append(t)
    combina_esito(fi)
    return fi


def _apri_pdf(f):
    """Prima lettura rigorosa, poi tollerante (molti PDF reali hanno piccoli difetti). I PDF cifrati senza password si aprono."""
    ultimo = None
    for rigoroso in (True, False):
        try:
            f.seek(0)
            reader = PdfFileReader(f, strict=rigoroso)
            if reader.encrypted:
                reader.decrypt("")
            return list(reader.embedded_signatures)
        except Exception as e:
            ultimo = e
    raise ultimo


async def analizza_pdf(ris: RisultatoDoc, dati: bytes, valida: bool = True):
    if not PDF_OK:
        ris.errore = "Verifica PDF non disponibile: libreria pyhanko non installata"
        return
    with io.BytesIO(dati) as f:
        try:
            sigs = _apri_pdf(f)
        except Exception as e:
            ris.errore = f"PDF non leggibile o protetto da password ({type(e).__name__})"
            return
        for sig in sigs:
            try:
                ris.firme.append(await _firma_pdf(sig, valida))
            except Exception as e:
                ris.firme.append(FirmaInfo(formato="PAdES", stato="error",
                                           esito=f"Errore di lettura della firma ({type(e).__name__}: {e})"))

def _loc(tag) -> str:
    return tag.rsplit('}', 1)[-1] if isinstance(tag, str) else ""


def _figlio(el, nome):
    for c in el:
        if _loc(c.tag) == nome:
            return c
    return None


def _percorso(el, *nomi) -> str:
    cur = el
    for n in nomi:
        cur = _figlio(cur, n) if cur is not None else None
    return (cur.text or "").strip() if cur is not None and cur.text else ""


def riepilogo_fattura(dati: bytes) -> Optional[dict]:
    try:
        root = ET.fromstring(dati)
    except Exception:
        return None
    if _loc(root.tag) != 'FatturaElettronica':
        return None
    h, b = _figlio(root, 'FatturaElettronicaHeader'), _figlio(root, 'FatturaElettronicaBody')
    if h is None:
        return None

    def anagrafica(sezione):
        a = _percorso(h, sezione, 'DatiAnagrafici', 'Anagrafica', 'Denominazione')
        if not a:
            a = (_percorso(h, sezione, 'DatiAnagrafici', 'Anagrafica', 'Nome') + " " +
                 _percorso(h, sezione, 'DatiAnagrafici', 'Anagrafica', 'Cognome')).strip()
        return a

    out = {
        "Cedente / prestatore": anagrafica('CedentePrestatore'),
        "P.IVA cedente": _percorso(h, 'CedentePrestatore', 'DatiAnagrafici', 'IdFiscaleIVA', 'IdCodice'),
        "Cessionario / committente": anagrafica('CessionarioCommittente'),
        "P.IVA cessionario": _percorso(h, 'CessionarioCommittente', 'DatiAnagrafici', 'IdFiscaleIVA', 'IdCodice'),
        "Progressivo invio": _percorso(h, 'DatiTrasmissione', 'ProgressivoInvio'),
        "Codice destinatario": _percorso(h, 'DatiTrasmissione', 'CodiceDestinatario'),
    }
    if b is not None:
        out.update({
            "Tipo documento": _percorso(b, 'DatiGenerali', 'DatiGeneraliDocumento', 'TipoDocumento'),
            "Numero": _percorso(b, 'DatiGenerali', 'DatiGeneraliDocumento', 'Numero'),
            "Data": _percorso(b, 'DatiGenerali', 'DatiGeneraliDocumento', 'Data'),
            "Importo totale": (_percorso(b, 'DatiGenerali', 'DatiGeneraliDocumento', 'ImportoTotaleDocumento') + " " +
                               _percorso(b, 'DatiGenerali', 'DatiGeneraliDocumento', 'Divisa')).strip(),
        })
    return {k: v for k, v in out.items() if v}


NS_DS = "http://www.w3.org/2000/09/xmldsig#"
_DS = "{%s}" % NS_DS
_XML_HASH = {"xmldsig#sha1": "sha1", "xmlenc#sha256": "sha256", "xmldsig-more#sha224": "sha224", "xmldsig-more#sha384": "sha384",
             "xmlenc#sha512": "sha512", "xmldsig-more#sha512": "sha512", "xmlenc#sha384": "sha384"}


def _alg_hash_xml(uri: str) -> Optional[str]:
    return next((v for k, v in _XML_HASH.items() if uri.endswith(k)), None)


def _parser_xml():
    return etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=True, remove_blank_text=False)


def _c14n(nodo, alg: str) -> bytes:
    return etree.tostring(nodo, method="c14n", exclusive="xml-exc-c14n" in alg, with_comments=alg.endswith("WithComments"))


def _togli_nodo(el):
    """Rimuove un elemento lasciando il testo che lo segue (etree.remove lo perderebbe)."""
    padre, coda = el.getparent(), el.tail
    if coda:
        prec = el.getprevious()
        if prec is not None:
            prec.tail = (prec.tail or "") + coda
        else:
            padre.text = (padre.text or "") + coda
    padre.remove(el)


def _mappa_id(radice) -> Tuple[dict, set]:
    ids, doppi = {}, set()
    for e in radice.iter():
        if not isinstance(e.tag, str):
            continue
        for a in ("Id", "ID", "id"):
            v = e.get(a)
            if v:
                if v in ids and ids[v] is not e:
                    doppi.add(v)
                ids[v] = e
    return ids, doppi


def _verifica_riferimento(rif, sig_indice: int, dati: bytes) -> Tuple[Optional[bool], str, bool]:
    """Ricalcola l'impronta di un ds:Reference su una copia fresca del documento. -> (esito, messaggio, copre l'intero documento)"""
    albero = etree.parse(io.BytesIO(dati), _parser_xml())
    radice = albero.getroot()
    firma = list(radice.iter())[sig_indice]
    uri = rif.get("URI")
    if uri is None or (uri and not uri.startswith("#")):
        return None, f"riferimento esterno non verificabile ({uri})", False
    if uri in ("", "#xpointer(/)"):
        nodo, copre = albero, True
    else:
        ident = re.sub(r"^#xpointer\(id\('(.*)'\)\)$", r"\1", uri).lstrip("#")
        ids, doppi = _mappa_id(radice)
        if ident in doppi:
            return False, f"Id «{ident}» duplicato nel documento: possibile manomissione", False
        if ident not in ids:
            return False, f"elemento «{ident}» firmato non trovato", False
        nodo, copre = ids[ident], ids[ident] is radice
    c14n_alg = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    trasf = rif.find(_DS + "Transforms")
    for t in (trasf if trasf is not None else []):
        if not isinstance(t.tag, str):
            continue
        alg = t.get("Algorithm", "")
        if alg.endswith("#enveloped-signature"):
            _togli_nodo(firma)
        elif "c14n" in alg:
            c14n_alg = alg
        elif alg.endswith("REC-xpath-19991116") or alg.endswith("xmldsig-filter2"):
            testo = " ".join((x.text or "") for x in t if isinstance(x.tag, str))
            if "Signature" not in testo or not ("not(" in testo or any(x.get("Filter") == "subtract" for x in t if isinstance(x.tag, str))):
                return None, f"trasformazione XPath non supportata ({testo.strip()[:60]})", False
            for s in list(radice.iter(_DS + "Signature")):
                _togli_nodo(s)
        else:
            return None, f"trasformazione non supportata ({alg})", False
    dm, dv = rif.find(_DS + "DigestMethod"), rif.find(_DS + "DigestValue")
    algo = _alg_hash_xml(dm.get("Algorithm", "")) if dm is not None else None
    if algo is None or dv is None:
        return None, "algoritmo di impronta non supportato", False
    calcolata = hashlib.new(algo, _c14n(nodo, c14n_alg)).digest()
    if calcolata != base64.b64decode("".join((dv.text or "").split())):
        return False, f"l'impronta del riferimento «{uri or 'documento'}» non corrisponde: documento alterato", copre
    return True, "", copre


def verifica_xmldsig(firma, radice, dati: bytes, cert) -> Tuple[Optional[bool], str, Optional[bool]]:
    """Verifica un ds:Signature: riferimenti + SignedInfo. -> (esito, messaggio, firma copre l'intero documento)"""
    if etree is None or not HAS_CRYPTO:
        return None, "librerie lxml/cryptography non disponibili", None
    try:
        si = firma.find(_DS + "SignedInfo")
        sv = firma.find(_DS + "SignatureValue")
        if si is None or sv is None:
            return False, "struttura ds:Signature incompleta", None
        indice = list(radice.iter()).index(firma)
        rifs = si.findall(_DS + "Reference")
        if not rifs:
            return False, "nessun riferimento firmato", None
        copre = False
        for r in rifs:
            esito, msg, c = _verifica_riferimento(r, indice, dati)
            if esito is not True:
                return esito, msg, None
            copre = copre or c
        c14n_alg = si.find(_DS + "CanonicalizationMethod").get("Algorithm", "")
        alg_uri = si.find(_DS + "SignatureMethod").get("Algorithm", "")
        canonico = _c14n(si, c14n_alg)
        valore = base64.b64decode("".join((sv.text or "").split()))
        chiave = serialization.load_der_public_key(cert['tbs_certificate']['subject_public_key_info'].dump())
        nome_h = next((n for n in ("sha3-256", "sha3-384", "sha3-512", "sha224", "sha256", "sha384", "sha512", "sha1") if n in alg_uri.lower()), None)
        if nome_h is None:
            return None, f"algoritmo di firma non supportato ({alg_uri})", copre
        h = _HASH_CLASSI[nome_h.replace("-", "_")]()
        if "MGF1" in alg_uri or "rsa-pss" in alg_uri.lower():
            chiave.verify(valore, canonico, padding.PSS(mgf=padding.MGF1(h), salt_length=h.digest_size), h)
        elif "ecdsa" in alg_uri.lower():
            meta = len(valore) // 2
            der = encode_dss_signature(int.from_bytes(valore[:meta], "big"), int.from_bytes(valore[meta:], "big"))
            chiave.verify(der, canonico, ec.ECDSA(h))
        elif "rsa" in alg_uri.lower():
            chiave.verify(valore, canonico, padding.PKCS1v15(), h)
        else:
            return None, f"algoritmo di firma non supportato ({alg_uri})", copre
        return True, "riferimenti e firma crittografica verificati: documento integro", copre
    except InvalidSignature:
        return False, "firma crittografica non valida: documento alterato o firma corrotta", None
    except Exception as e:
        return None, f"verifica non eseguibile ({type(e).__name__}: {e})", None


def _certificato_xades(firma, certs) -> Tuple[Optional[x509.Certificate], Optional[Controllo]]:
    """Sceglie il certificato del firmatario: quello indicato da xades:SigningCertificate, se presente."""
    nome = "Legame firma-certificato"
    non_ca = [c for c in certs if not getattr(c, 'ca', False)]
    scelto = non_ca[0] if non_ca else (certs[0] if certs else None)
    digest_attesi = []
    for e in firma.iter():
        if isinstance(e.tag, str) and _loc(e.tag) in ("SigningCertificate", "SigningCertificateV2"):
            for cd in e.iter():
                if isinstance(cd.tag, str) and _loc(cd.tag) == "CertDigest":
                    dm, dv = cd.find(_DS + "DigestMethod"), cd.find(_DS + "DigestValue")
                    if dm is not None and dv is not None:
                        digest_attesi.append((_alg_hash_xml(dm.get("Algorithm", "")), "".join((dv.text or "").split())))
    if not digest_attesi:
        return scelto, Controllo(nome, "none", "elemento SigningCertificate assente")
    for algo, valore in digest_attesi:
        if not algo:
            continue
        for c in certs:
            if base64.b64encode(hashlib.new(algo, c.dump()).digest()).decode() == valore:
                return c, Controllo(nome, "ok", "SigningCertificate corrisponde al certificato usato")
    return scelto, Controllo(nome, "error", "SigningCertificate indica un certificato diverso da quello incluso")


async def analizza_xml(ris: RisultatoDoc, dati: bytes, valida: bool = True):
    try:
        if etree is None:
            ris.errore = "Libreria lxml non disponibile"
            return
        radice = etree.fromstring(dati, _parser_xml())
    except Exception:
        ris.errore = "XML malformato o non leggibile"
        return
    if ris.dimensione < 30_000_000:
        ris.fattura = riepilogo_fattura(dati)
    for firma in list(radice.iter(_DS + "Signature")):
        fi = FirmaInfo(formato="XAdES")
        certs = []
        for e in firma.iter(_DS + "X509Certificate"):
            if e.text:
                try:
                    certs.append(x509.Certificate.load(base64.b64decode("".join(e.text.split()))))
                except Exception:
                    pass
        for e in firma.iter():
            if isinstance(e.tag, str) and _loc(e.tag) == 'SigningTime' and e.text:
                fi.data_firma = parse_iso(e.text)
                fi.fonte_data = "Elemento SigningTime (XAdES)"
                break
        if not certs:
            fi.stato, fi.esito = "error", "Firma XML senza certificato del firmatario"
            fi.controlli.append(Controllo("Certificato", "error", "non presente nella firma"))
            ris.firme.append(fi)
            continue
        cert, legame = _certificato_xades(firma, certs)
        popola_da_cert(fi, cert)
        sm = firma.find(_DS + "SignedInfo/" + _DS + "SignatureMethod")
        rm = firma.find(_DS + "SignedInfo/" + _DS + "Reference/" + _DS + "DigestMethod")
        fi.algo_firma = (sm.get("Algorithm", "").rsplit("#", 1)[-1] if sm is not None else "")
        fi.algo_hash = (_alg_hash_xml(rm.get("Algorithm", "")) or "") if rm is not None else ""
        if not valida:
            fi.esito = "Verifica non eseguita (solo estrazione)"
            ris.firme.append(fi)
            continue
        fi.integrita, fi.integrita_msg, copre = verifica_xmldsig(firma, radice, dati, cert)
        fi.controlli.append(controllo_integrita(fi))
        if fi.integrita and copre is False:
            fi.controlli.append(Controllo("Copertura", "warn", "la firma copre solo una parte del documento"))
        fi.controlli.append(legame)
        msg_marca = ""
        for e in firma.iter():
            if isinstance(e.tag, str) and _loc(e.tag) == "EncapsulatedTimeStamp" and e.text:
                try:
                    token = cms.ContentInfo.load(base64.b64decode("".join(e.text.split())))
                    cm = next((x for x in e.getparent() if isinstance(x.tag, str) and _loc(x.tag) == "CanonicalizationMethod"), None)
                    alg = cm.get("Algorithm", "") if cm is not None else ""
                    sv = firma.find(_DS + "SignatureValue")
                    fi.marca_valida, istante, fi.marca_tsa, msg_marca = await verifica_marca(token, _c14n(sv, alg))
                    fi.marca_temporale = istante
                except Exception as ex:
                    fi.marca_valida, msg_marca = None, f"marca non leggibile ({type(ex).__name__})"
                break
        fi.controlli.append(controllo_marca(fi, msg_marca))
        fi.controlli += await valida_certificato(cert, certs, fi.data_firma, fi.marca_temporale if fi.marca_valida else None)
        fi.controlli.append(controllo_algoritmi(fi, cert))
        fi.controlli.append(controllo_tipo_certificato(cert))
        t = controllo_tempi(fi)
        if t is not None:
            fi.controlli.append(t)
        combina_esito(fi)
        ris.firme.append(fi)

def report_testuale(r: RisultatoDoc) -> str:
    L = [f"File: {r.nome}", f"Percorso: {r.percorso}", f"Formato: {r.formato}",
         f"Dimensione: {fmt_size(r.dimensione)}", f"SHA-256: {r.sha256}",
         f"Esito complessivo: {etichetta_doc(r)} - {r.esito}", f"Firme rilevate: {len(r.firme)}"]
    if r.nome_contenuto and r.formato == 'CAdES':
        L.append(f"Documento contenuto: {r.nome_contenuto} ({r.tipo_contenuto})")
    L += [f"Nota: {n}" for n in r.note]
    for i, f in enumerate(r.firme, 1):
        L += ["", f"--- {f.tipo} {i} ---", f"Firmatario: {f.firmatario}"]
        if f.identificativo:
            L.append(f"Identificativo: {f.identificativo}")
        if f.organizzazione:
            L.append(f"Organizzazione: {f.organizzazione}")
        L.append(f"Data e ora firma: {fmt_dt(f.data_firma)}" + (f"  [{f.fonte_data}]" if f.fonte_data else ""))
        if f.data_pdf_m:
            L.append(f"Data /M del PDF: {fmt_dt(f.data_pdf_m)}")
        if f.marca_temporale:
            L.append(f"Marca temporale: {fmt_dt(f.marca_temporale)}")
        L += [f"Emittente: {f.emittente}", f"Certificato valido dal {fmt_data(f.valido_dal)} al {fmt_data(f.valido_al)}",
              f"Esito: {etichetta_firma(f)} - {f.esito}", "Controlli:"]
        simboli = {"ok": "[OK]", "warn": "[!!]", "error": "[KO]", "none": "[--]"}
        L += [f"  {simboli[c.stato]} {c.nome}: {c.dettaglio}" for c in f.controlli]
        L += [f"Nota: {n}" for n in f.note]
    L += ["", f"Verifica eseguita il {fmt_dt(datetime.now().astimezone())} con {NOME_APP} ({MOTORE_FIRME})"]
    return "\n".join(L)


def esporta_csv(risultati: List[RisultatoDoc], path: str):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(["File", "Percorso", "Formato", "Dimensione", "SHA-256", "Stato documento", "Esito documento",
                    "N. firme", "Tipo", "Firmatario", "Identificativo", "Organizzazione", "Data firma",
                    "Ora firma", "Fonte data", "Marca temporale", "Marca valida", "Cert. valido dal", "Cert. valido al",
                    "Emittente", "Integrita'", "Esito firma", "Controlli"])
        for r in risultati:
            base = [r.nome, r.percorso, r.formato, r.dimensione, r.sha256, etichetta_doc(r), r.esito, len(r.firme)]
            if not r.firme:
                w.writerow(base + [""] * 15)
            for fi in r.firme:
                w.writerow(base + [fi.tipo, fi.firmatario, fi.identificativo, fi.organizzazione, fmt_data(fi.data_firma),
                                   fmt_ora(fi.data_firma) if fi.data_firma else "", fi.fonte_data,
                                   fmt_dt(fi.marca_temporale) if fi.marca_temporale else "",
                                   {True: "si", False: "no", None: ""}[fi.marca_valida],
                                   fmt_data(fi.valido_dal), fmt_data(fi.valido_al), fi.emittente,
                                   {True: "verificata", False: "NON valida", None: "non verificabile"}[fi.integrita],
                                   f"{etichetta_firma(fi)} - {fi.esito}",
                                   " | ".join(f"{c.nome}: {c.dettaglio}" for c in fi.controlli)])


def esporta_html(risultati: List[RisultatoDoc], path: str):
    colori = {"ok": "#22A06B", "warn": "#E8A317", "error": "#E5484D", "none": "#8A94A6"}
    e = html.escape
    tot = {k: sum(1 for r in risultati if r.stato == k) for k in colori}
    righe = []
    for r in risultati:
        righe.append(f"<tr class='doc'><td><span class='b' style='background:{colori[r.stato]}'>{e(etichetta_doc(r))}</span></td>"
                     f"<td><b>{e(r.nome)}</b><br><small>{e(r.formato)} · {e(fmt_size(r.dimensione))}<br>SHA-256 {e(r.sha256[:32])}…</small></td>"
                     f"<td colspan='3'>{e(r.esito)}</td></tr>")
        for fi in r.firme:
            controlli = "".join(f"<li style='color:{colori[c.stato]}'><span style='color:#344054'>{e(c.nome)}: {e(c.dettaglio)}</span></li>" for c in fi.controlli)
            righe.append(f"<tr><td></td><td>↳ {e(fi.tipo)}: <b>{e(fi.firmatario)}</b><br><small>{e(fi.identificativo)}</small></td>"
                         f"<td>{e(fmt_dt(fi.data_firma))}<br><small>{e(fi.fonte_data)}</small></td>"
                         f"<td>{e(fi.emittente)}<br><small>valido {e(fmt_data(fi.valido_dal))} → {e(fmt_data(fi.valido_al))}</small></td>"
                         f"<td><span class='b' style='background:{colori[fi.stato]}'>{e(etichetta_firma(fi))}</span> {e(fi.esito)}<ul>{controlli}</ul></td></tr>")
    ora = fmt_dt(datetime.now().astimezone())
    doc = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Report verifica firme</title>
<style>body{{font:14px {FONT_HTML};margin:32px;color:#101828;background:#f2f4f8}}
h1{{color:#4C57CC;margin:0 0 4px}}table{{border-collapse:collapse;width:100%;background:#fff;border-radius:10px;overflow:hidden}}
td,th{{padding:8px 10px;border-right:1px solid #e3e7ee;vertical-align:top;text-align:left}}th{{background:#13141B;color:#fff}}
tr.doc td{{background:#f6f8fb}}.b{{color:#fff;border-radius:8px;padding:2px 8px;font-size:12px;font-weight:600}}
small{{color:#667085}}ul{{margin:6px 0 0;padding-left:18px;font-size:12px}}.k{{display:inline-block;margin-right:18px;font-weight:600}}</style></head><body>
<h1>Report di verifica firme</h1><p>Generato il {e(ora)} con {NOME_APP} ({MOTORE_FIRME})</p>
<p><span class='k'>Totale: {len(risultati)}</span><span class='k' style='color:#22A06B'>Verificati: {tot['ok']}</span>
<span class='k' style='color:#E8A317'>Attenzione: {tot['warn'] + tot['none']}</span><span class='k' style='color:#E5484D'>Non validi: {tot['error']}</span></p>
<table><tr><th>Stato</th><th>Documento / firmatario</th><th>Data e ora firma</th><th>Emittente</th><th>Esito e controlli</th></tr>
{''.join(righe)}</table></body></html>"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(doc)

def descrivi_certificato(der: bytes) -> str:
    c = x509.Certificate.load(der)
    L = ["SOGGETTO", "  " + c.subject.human_friendly.replace("; ", "\n  "), "",
         "EMITTENTE", "  " + c.issuer.human_friendly.replace("; ", "\n  "), "",
         f"Numero di serie : {format(c.serial_number, 'X')}"]
    try:
        v = c['tbs_certificate']['validity']
        L.append(f"Valido dal      : {fmt_dt(v['not_before'].native)}")
        L.append(f"Valido fino al  : {fmt_dt(v['not_after'].native)}")
    except Exception:
        pass
    try:
        L.append(f"Chiave pubblica : {c.public_key.algorithm.upper()} {c.public_key.bit_size} bit")
        L.append(f"Algoritmo firma : {c.signature_algo} / {c.hash_algo}")
    except Exception:
        pass
    try:
        L.append(f"CA              : {'si' if c.ca else 'no'}")
    except Exception:
        pass
    for etichetta, attr in (("Uso chiave      ", 'key_usage_value'), ("Uso esteso      ", 'extended_key_usage_value')):
        try:
            val = getattr(c, attr)
            if val is not None:
                L.append(f"{etichetta}: {', '.join(sorted(str(x) for x in val.native))}")
        except Exception:
            pass
    try:
        pol = [str(p['policy_identifier']) for p in c.certificate_policies_value.native]
        if pol:
            L.append("Policy          : " + ", ".join(pol))
    except Exception:
        pass
    try:
        if c.ocsp_urls:
            L.append("OCSP            : " + ", ".join(c.ocsp_urls))
    except Exception:
        pass
    try:
        for dp in (c.crl_distribution_points or []):
            L.append(f"CRL             : {dp.native.get('distribution_point')}")
    except Exception:
        pass
    sha1, sha256 = hashlib.sha1(der).hexdigest().upper(), hashlib.sha256(der).hexdigest().upper()
    fp = lambda h: ":".join(h[i:i + 2] for i in range(0, len(h), 2))
    L += ["", "IMPRONTE", f"  SHA-1   : {fp(sha1)}", f"  SHA-256 : {fp(sha256)}"]
    return "\n".join(L)



# ---------- raccordo con lo ZimbraViewer ----------
def _tipo_reale(dati: bytes) -> str:
    """Il tipo si riconosce dal contenuto; l'estensione conta solo se il contenuto non dice nulla."""
    testa = dati[:2048]
    if _sembra_der(testa):                  # prima la busta: dentro i primi byte puo' esserci il PDF firmato
        return '.p7m'
    if b'%PDF-' in testa[:1024]:
        return '.pdf'
    t = testa.lstrip(b'\xef\xbb\xbf \r\n\t')
    if t[:1] == b'<':
        return '.xml'
    if t[:2] in (b'MI', b'MB', b'MD') or t.startswith(b'-----BEGIN'):
        return '.p7m'
    return ''

_FORMATO_DA_EST = {'.p7m': 'CAdES', '.p7s': 'CAdES', '.pdf': 'PAdES', '.xml': 'XAdES'}

async def analizza_documento_async(ris: RisultatoDoc, dati: bytes):
    """Orchestratore (come analizza_file del P7MReader) ma sui byte: file da disco o allegati delle mail."""
    t0 = time.monotonic()
    ext = tipo_documento(ris.nome)
    ris.dimensione = len(dati)
    ris.sha256 = hashlib.sha256(dati).hexdigest()
    try:
        reale = _tipo_reale(dati)
        if reale and reale != ext and not (reale == '.p7m' and ext == '.p7s'):
            if ext in ESTENSIONI_VERIFICA:
                ris.note.append(f"L'estensione {ext} non corrisponde al contenuto: analizzato come {reale}")
            ext = reale
        ris.formato = _FORMATO_DA_EST.get(ext, '?')
        if ext in ('.p7m', '.p7s'):
            await analizza_p7m(ris, dati)
        elif ext == '.pdf':
            await analizza_pdf(ris, dati)
        elif ext == '.xml':
            await analizza_xml(ris, dati)
        else:
            ris.errore = "Formato non supportato"
    except Exception as e:
        ris.errore = f"Errore imprevisto: {type(e).__name__}: {e}"
    ris.durata = time.monotonic() - t0
    ris.finalizza()

def verifica_documento(nome, dati, percorso="", origine=""):
    """Verifica completa (bloccante: va chiamata da un thread) -> RisultatoDoc."""
    dati = bytes(dati)
    ris = RisultatoDoc(percorso=percorso or nome, nome=nome)
    ris.origine = origine
    manca = ""
    if not P7M_LIBRERIE_OK:
        manca = f"librerie del P7MReader mancanti ({P7M_LIBRERIE_ERRORE})"
    elif tipo_documento(nome) == '.pdf' and not PDF_OK:
        manca = "per i PDF firmati serve la libreria pyhanko, come nel P7MReader"
    elif tipo_documento(nome) == '.xml' and etree is None:
        manca = "per gli XML firmati serve la libreria lxml, come nel P7MReader"
    if manca:
        ris.formato = _FORMATO_DA_EST.get(tipo_documento(nome), '?')
        ris.dimensione, ris.sha256 = len(dati), hashlib.sha256(dati).hexdigest()
        ris.stato, ris.esito = "none", f"verifica non eseguita: {manca}"
        ris.non_eseguita = True
        return ris
    try:
        asyncio.run(analizza_documento_async(ris, dati))
    except Exception as e:
        ris.errore = f"Errore durante la verifica: {type(e).__name__}: {e}"
        ris.finalizza()
    return ris

def e_documento_firmato(nome, dati):
    """Allegati da verificare: tutti i .p7m, i PDF con una firma (/ByteRange), gli XML con una firma XMLDSig."""
    tipo = tipo_documento(nome)                # niente .p7s: lo smime.p7s delle PEC è un file tecnico, non un documento
    if tipo == '.p7m':
        return True
    if tipo == '.pdf':
        return b"/ByteRange" in dati
    if tipo == '.xml':
        return b"Signature" in dati and b"xmldsig" in dati
    return False

def contenuto_p7m(dati):
    """Documento contenuto in un .p7m (anche base64/PEM e buste annidate), come leggi_contenuto_p7m del P7MReader."""
    livello = 0
    while True:
        info = carica_cms(dati, dati.lstrip()[:1] == b'M')
        if info['content_type'].native != 'signed_data':
            raise ValueError("busta non valida")
        payload = info['content']['encap_content_info']['content']
        if isinstance(payload, Void):
            raise ValueError("contenuto assente (firma detached)")
        dati = byte_ottetti(payload)
        if not dati:
            raise ValueError("contenuto vuoto")
        if IMP["estrai_annidati"] and livello < MAX_ANNIDAMENTO and e_busta_cms(dati):
            livello += 1
            continue
        return dati

def risolvi_p7m(nome, dati):
    """Se l'allegato è un .p7m restituisce il documento estratto: (nome, dati, True); altrimenti (nome, dati, False).
    Il nome segue la regola del P7MReader: via .p7m e segni di copia, estensione ricavata dal contenuto."""
    if tipo_documento(nome) != '.p7m' or not P7M_LIBRERIE_OK:
        return nome, dati, False
    try:
        interno = contenuto_p7m(bytes(dati))
    except Exception:
        return nome, dati, False
    return nome_per_contenuto(nome, interno), interno, True

def estensione_effettiva(nome):
    """Estensione vera di un allegato: per 'programma.exe (1).p7m' è '.exe' (serve al controllo di sicurezza)."""
    return os.path.splitext(pulisci_nome_file_globale(nome).lower())[1]

def salva_allegato_con_p7m(cartella, nome, dati, max_len=150):
    """Salva un allegato. Se è un .p7m conserva SEMPRE il file firmato originale e salva accanto il documento
    estratto. Restituisce (percorso del documento salvato, True se era un p7m estratto)."""
    nome_finale, dati_finale, estratto = risolvi_p7m(nome, dati)
    if estratto:
        with open(percorso_libero(cartella, nome_windows_sicuro(nome, max_len, "allegato")), 'wb') as f_out:
            f_out.write(dati)
    path_out = percorso_libero(cartella, nome_windows_sicuro(nome_finale, max_len, "allegato"))
    with open(path_out, 'wb') as f_out:
        f_out.write(dati_finale)
    return path_out, estratto

def etichetta_esito(ris):
    return "Non verificato" if getattr(ris, "non_eseguita", False) else ETICHETTA.get(ris.stato, ris.stato)

def categoria_esito(ris):
    """Chiave del contatore nel riepilogo dell'esportazione."""
    if ris is None or getattr(ris, "non_eseguita", False):
        return "firme_non_verificate"
    return {"ok": "firme_valide", "warn": "firme_attenzione", "error": "firme_non_valide"}.get(ris.stato, "firme_non_verificate")

def righe_verifica(ris):
    """Esito per "Dettagli mail.txt": il report testuale del P7MReader, rientrato sotto il nome del file."""
    if getattr(ris, "non_eseguita", False):
        return [f"{ris.nome}: {etichetta_esito(ris)} - {ris.esito}"]
    righe = [f"{ris.nome}: {etichetta_esito(ris)} - {ris.esito}"]
    corpo = report_testuale(ris).split("\n")
    # il report ripete nome/esito in testa e la riga "Verifica eseguita" in coda: si tengono solo i dettagli
    corpo = [r for r in corpo if not r.startswith(("File: ", "Percorso: ", "Esito complessivo: ", "Verifica eseguita il"))]
    righe += ["    " + r if r else "" for r in corpo]
    while righe and not righe[-1].strip():
        righe.pop()
    return righe

def nota_verifica():
    return (f"Verifica eseguita il {fmt_dt(datetime.now().astimezone())} con il {MOTORE_FIRME} - "
            f"radici attendibili: archivio certificati di sistema + CA aggiunte nel P7MReader; "
            f"revoca OCSP/CRL: {'attiva (soft-fail)' if IMP['revoca'] else 'disattivata'}.")

class VerificaFirme:
    """Esegue le verifiche in thread separati (daemon): non bloccano mai l'interfaccia, l'esportazione
    o la chiusura del programma. Quante in parallelo lo decide l'impostazione "concorrenza" del P7MReader."""
    TIMEOUT = 120                      # secondi dall'avvio effettivo (catena, OCSP e CRL vanno in rete)
    _slot = threading.Semaphore(max(1, min(8, int(IMP["concorrenza"] or 4))))

    @classmethod
    def avvia(cls, nome, dati=None, percorso="", origine=""):
        """Senza 'dati' il file 'percorso' viene letto dal thread di verifica (niente attese nell'interfaccia)."""
        futuro = Future()
        futuro.inizio = None           # impostato quando la verifica parte davvero (non mentre è in coda)
        dati = bytes(dati) if dati is not None else None

        def lavoro():
            with cls._slot:
                futuro.inizio = time.monotonic()
                try:
                    contenuto = dati
                    if contenuto is None:
                        with open(percorso, 'rb') as f:
                            contenuto = f.read()
                    futuro.set_result(verifica_documento(nome, contenuto, percorso, origine))
                except PermissionError:
                    ris = RisultatoDoc(percorso=percorso or nome, nome=nome, errore="Accesso al file negato")
                    ris.finalizza()
                    futuro.set_result(ris)
                except Exception as e:
                    ris = RisultatoDoc(percorso=percorso or nome, nome=nome, errore=f"Errore interno: {e}")
                    ris.finalizza()
                    futuro.set_result(ris)
        threading.Thread(target=lavoro, daemon=True).start()
        return futuro

    @classmethod
    def scaduta(cls, futuro, adesso):
        return (not futuro.done()) and futuro.inizio is not None and adesso - futuro.inizio > cls.TIMEOUT

# ==========================================
# LAVORI IN BACKGROUND: IMPORTAZIONE, INDICIZZAZIONE, ESTRAZIONE, ESPORTAZIONE
# ==========================================
# elenco mail con numero di allegati (postacert.eml escluso anche per gli indici creati dalle versioni precedenti)
SQL_ELENCO = (f"SELECT id, cartella, mittente, oggetto, data, "
              f"(SELECT COUNT(id) FROM allegati WHERE email_id = emails.id AND {FILTRO_ALLEGATI_SQL}) FROM emails")

class _Annullato(Exception):
    """Interrompe un'operazione dentro una transazione SQLite, che così viene annullata (rollback)."""

class ImportWorker(QThread):
    """Prepara in background una cartella di .eml da archivi (.tgz/.tar/.zip) e da export di altri programmi
    (Gmail/Takeout .mbox, Outlook .pst/.ost/.msg, Thunderbird, Apple Mail, Maildir)."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, dict)       # cartella pronta ("" se annullato) e informazioni
    error = pyqtSignal(str)

    def __init__(self, sorgente, dest):
        super().__init__()
        self.sorgente, self.dest = sorgente, dest
        self._is_cancelled = False
        self._ultimo = (-1, 0.0)

    def cancel(self):
        self._is_cancelled = True

    def _avanzamento(self, frazione, testo):
        perc, adesso = int(max(0.0, min(1.0, frazione)) * 100), time.monotonic()
        if perc != self._ultimo[0] or adesso - self._ultimo[1] > 0.3:
            self._ultimo = (perc, adesso)
            self.progress.emit(perc, testo)

    def run(self):
        try:
            ok, info = importa_posta(self.sorgente, self.dest, self._avanzamento, lambda: self._is_cancelled)
            self.finished.emit(self.dest if ok and not self._is_cancelled else "", info)
        except Exception as e:
            self.error.emit(f"{type(e).__name__}: {e}")

class AttachmentExtractorWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(int)
    
    def __init__(self, id_spuntati_con_path, dir_dest):
        super().__init__()
        self.id_spuntati_con_path = id_spuntati_con_path
        self.dir_dest = dir_dest
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        estratti_totali = 0
        totale = len(self.id_spuntati_con_path)
        step = max(1, totale // 100)
        
        for i, data in enumerate(self.id_spuntati_con_path):
            if self._is_cancelled: break
            eml_path = data[1]
            if not os.path.exists(eml_path): 
                self.progress.emit(i + 1, totale)
                continue
            
            try:
                with open(eml_path, 'rb') as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)
                    for nome_originale, part in allegati_da_msg(msg):
                        if nome_originale:
                            payload = payload_allegato(part)
                            if payload:
                                salva_allegato_con_p7m(self.dir_dest, nome_originale, payload)
                                estratti_totali += 1
            except Exception:
                pass
                
            if (i + 1) % step == 0:
                self.progress.emit(i + 1, totale)
                
        if not self._is_cancelled:
            self.progress.emit(totale, totale)
        self.finished.emit(estratti_totali)       # sempre, anche se annullato: chi ascolta guarda _is_cancelled

class IndexerWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, root_dir, db_path, solo_pim=False):
        super().__init__()
        self.root_dir = root_dir
        self.db_path = db_path
        self.solo_pim = solo_pim             # vecchio indice: si leggono solo calendario, rubrica e altri dati
        self._is_cancelled = False
        # nomi delle cartelle di sistema (Zimbra, Outlook, Thunderbird, Maildir...) in italiano
        self.mappa_traduzioni = {
            "inbox": "Posta in arrivo", "sent": "Posta inviata", "sent items": "Posta inviata",
            "sent messages": "Posta inviata", "sent mail": "Posta inviata", "outbox": "Posta in uscita",
            "trash": "Cestino", "deleted items": "Cestino", "deleted messages": "Cestino",
            "drafts": "Bozze", "draft": "Bozze", "junk": "Spam", "junk e-mail": "Spam", "junk email": "Spam",
            "spam": "Spam", "archive": "Archivio", "archives": "Archivio", "templates": "Modelli"
        }

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        eml_files, pim_files = [], []
        for root, dirs, files in os.walk(self.root_dir):
            if self._is_cancelled:
                self.finished.emit()
                return
            for file in files:
                if file.lower().endswith('.eml'):
                    if not self.solo_pim:
                        eml_files.append(os.path.join(root, file))
                elif e_file_pim(file):
                    pim_files.append(os.path.join(root, file))

        totale = len(eml_files) + len(pim_files)
        if totale == 0 or self._is_cancelled:
            self.finished.emit()
            return

        step = max(1, totale // 100)

        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                if not self.solo_pim:
                    self._indicizza(conn, eml_files, totale, step)
                self._indicizza_pim(conn, pim_files, len(eml_files), totale, step)
        except _Annullato:
            pass                                  # la transazione è stata annullata: l'indice precedente resta intatto
        conn.close()
        if not self._is_cancelled:
            self.progress.emit(totale, totale)
        self.finished.emit()                      # sempre, anche se annullato: chi ascolta guarda _is_cancelled

    def _indicizza_pim(self, conn, pim_files, gia, totale, step):
        conn.execute("DELETE FROM elementi")
        for i, path in enumerate(pim_files):
            if self._is_cancelled:
                raise _Annullato()
            for e, rel in elementi_da_file(path, self.root_dir):
                extra = ""
                campi = dict(e.get("campi", []))
                if e["tipo"] == "attivita":
                    extra = campi.get("Stato", "")
                elif e["tipo"] == "file":
                    extra = campi.get("Dimensione", "")
                elif e["tipo"] == "chat":
                    extra = campi.get("Messaggi", "")
                conn.execute("INSERT INTO elementi (tipo, cartella, titolo, inizio, fine, luogo, persone, extra, testo, "
                             "file_path, dati) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (e["tipo"], e.get("cartella") or NOMI_TIPI_PIM.get(e["tipo"], ""), e["titolo"],
                              e.get("inizio", ""), e.get("fine", ""), e.get("luogo", ""), e.get("persone", ""), extra,
                              _testo_ricerca(e), rel, json.dumps(e, ensure_ascii=False, default=str)))
            if (gia + i) % step == 0:
                self.progress.emit(gia + i, totale)

    def _indicizza(self, conn, eml_files, totale, step):
        if True:
            conn.execute("DELETE FROM emails")
            conn.execute("DELETE FROM allegati")

            for i, path in enumerate(eml_files):
                if self._is_cancelled:
                    raise _Annullato()

                rel_path = os.path.relpath(path, self.root_dir).replace('\\', '/')
                cartella_grezza = os.path.dirname(rel_path)

                if not cartella_grezza:
                    cartella_finale = "Root"
                else:
                    parti_cartella = cartella_grezza.split('/')
                    parti_pulite = []

                    for index, parte in enumerate(parti_cartella):
                        parte_pulita = re.sub(r'!\d+$', '', parte)
                        if index == 0:
                            chiave_ricerca = parte_pulita.lower()
                            parte_tradotta = self.mappa_traduzioni.get(chiave_ricerca, parte_pulita)
                            parti_pulite.append(parte_tradotta)
                        else:
                            parti_pulite.append(parte_pulita)

                    cartella_finale = "/".join(parti_pulite)

                try:
                    with open(path, 'rb') as f:
                        msg = email.message_from_binary_file(f, policy=policy.default)

                    mittente = str(msg.get('From', ''))
                    destinatario = str(msg.get('To', ''))
                    oggetto = str(msg.get('Subject', '(Nessun oggetto)'))

                    # testo di tutte le parti testuali, compreso il messaggio originale dentro postacert.eml (PEC)
                    corpo_testo = "\n".join(testo_parte(part) for part in msg.walk()
                                            if part.get_content_type() == "text/plain"
                                            and str(part.get_content_disposition()) != 'attachment')[:300000]

                    data_formattata = data_da_msg(msg)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO emails (cartella, mittente, destinatario, oggetto, data, file_path, corpo)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (cartella_finale, mittente, destinatario, oggetto, data_formattata, rel_path, corpo_testo))  # percorso RELATIVO
                    email_id = cursor.lastrowid

                    for nome_allegato, _part in allegati_da_msg(msg):
                        cursor.execute("INSERT INTO allegati (email_id, nome_file) VALUES (?, ?)", (email_id, nome_allegato))
                except Exception:
                    pass

                if i % step == 0:
                    self.progress.emit(i, totale)

class MassPdfExporter(QObject):
    """Esporta le mail indicate: una sottocartella per ciascuna (data + oggetto) con
      - il PDF della mail;
      - gli allegati (i .p7m vengono conservati E il documento contenuto viene estratto accanto);
      - "Dettagli mail.txt" (intestazioni, allegati, esito della verifica delle firme);
      - per i postacert.eml: il file originale e il suo contenuto scompattato in una sottocartella "postacert"
        (PDF del vero messaggio, dettagli, allegati, p7m...), anche in modo ricorsivo.
    Il PDF si genera con Chromium (QWebEnginePage): tutto gira nel thread della GUI, un PDF alla volta, a passi
    asincroni, quindi l'interfaccia non si blocca. La verifica delle firme gira in thread separati: non rallenta
    l'esportazione e il txt viene completato appena l'esito è pronto."""
    progress = pyqtSignal(int, int, str)
    stato = pyqtSignal(str)
    finished = pyqtSignal(dict)

    TIMEOUT_CARICAMENTO_MS = 15000
    TIMEOUT_PDF_MS = 60000
    SOGLIA_SETHTML = 500000    # setHtml() codifica in URL (limite 2 MB): oltre ~500 KB si passa da un file temporaneo
    LIMITE_PERCORSO = 250      # Windows: 260 caratteri totali, con un po' di margine
    MAX_PROFONDITA_POSTACERT = 3

    def __init__(self, elementi, dir_dest, parent=None):
        super().__init__(parent)
        self.elementi = elementi            # [(email_id, percorso_eml, data_formattata), ...]
        self.dir_dest = dir_dest
        restante = max(40, self.LIMITE_PERCORSO - len(os.path.abspath(dir_dest)) - 2)
        self.max_cartella = max(40, min(90, restante * 2 // 5))     # include il prefisso data/ora (19 caratteri)
        self._cancelled = False
        self._indice = -1
        self._stato = "idle"                # idle -> caricamento -> stampa
        self._pdf_path = None
        self._tmp_html = None
        self._jobs = []                     # PDF ancora da stampare per la mail corrente: [(html, percorso_pdf)]
        self._attese = []                   # file dei dettagli in attesa dell'esito delle verifiche
        self._concludendo = False
        self._terminato = False
        self.report = {"mail": 0, "pdf": 0, "allegati": 0, "p7m": 0, "firmati": 0, "postacert": 0,
                       "firme_valide": 0, "firme_attenzione": 0, "firme_non_valide": 0, "firme_non_verificate": 0,
                       "errori": [], "annullato": False}

        self.page = None
        self._nuova_pagina()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._timeout)
        self._timer_verifiche = QTimer(self)
        self._timer_verifiche.setInterval(300)
        self._timer_verifiche.timeout.connect(self._controlla_verifiche)

    def _nuova_pagina(self):
        """Pagina Chromium per la stampa; dopo una stampa bloccata se ne crea una nuova (non accetta stampe in parallelo)."""
        if self.page is not None:
            try:
                self.page.loadFinished.disconnect()
                self.page.pdfPrintingFinished.disconnect()
            except Exception:
                pass
            self.page.deleteLater()
        self.page = QWebEnginePage(self)
        self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        self.page.loadFinished.connect(self._caricamento_finito)
        self.page.pdfPrintingFinished.connect(self._pdf_finito)

    def start(self):
        QTimer.singleShot(0, self._prossima)

    def cancel(self):
        self._cancelled = True

    def interrompi(self):
        """Chiusura della scheda o del programma: stop immediato, i file dei dettagli in sospeso vengono chiusi
        con l'esito delle verifiche già pronte (le altre risultano "Non verificato"). Nessun riepilogo."""
        self._cancelled = True
        self._terminato = True
        self._timer.stop()
        self._timer_verifiche.stop()
        try:
            self.page.triggerAction(QWebEnginePage.WebAction.Stop)
        except Exception:
            pass
        for voce in self._attese:
            self._scrivi_dettagli(voce, finale=True)
        self._attese = []
        self._pulisci_tmp()

    def _pulisci_tmp(self):
        if self._tmp_html:
            try: os.remove(self._tmp_html)
            except OSError: pass
            self._tmp_html = None

    def _max_file(self, cartella):
        """Lunghezza massima di un nome file dentro 'cartella', per restare sotto il limite del percorso."""
        return max(20, self.LIMITE_PERCORSO - len(os.path.abspath(cartella)) - 1)

    # ---------- ciclo principale: una mail alla volta, un PDF alla volta ----------
    def _prossima(self):
        self._pulisci_tmp()
        if self._cancelled:
            self._concludi()
            return
        if not self._jobs:
            self._indice += 1
            if self._indice >= len(self.elementi):
                self._concludi()
                return
            _email_id, eml_path, data = self.elementi[self._indice]
            try:
                self._prepara_mail(eml_path, data)
            except Exception as e:
                self.progress.emit(self._indice, len(self.elementi), os.path.basename(eml_path))
                self.report["errori"].append(f"{os.path.basename(eml_path)}: {e}")
            if not self._jobs:
                QTimer.singleShot(0, self._prossima)
                return
        html_mail, self._pdf_path = self._jobs.pop(0)
        self._stato = "caricamento"
        self._timer.start(self.TIMEOUT_CARICAMENTO_MS)
        if len(html_mail.encode('utf-8')) > self.SOGLIA_SETHTML:
            self._tmp_html = os.path.join(cartella_temp_allegati(), f"mail_{self._indice}.html")
            with open(self._tmp_html, "w", encoding="utf-8-sig", errors="replace") as f:   # il BOM fissa la codifica
                f.write(html_mail)
            self.page.load(QUrl.fromLocalFile(self._tmp_html))
        else:
            self.page.setHtml(html_mail)

    def _prepara_mail(self, eml_path, data):
        """Crea la cartella della mail, scrive allegati e dettagli e prepara i PDF da stampare."""
        if not os.path.exists(eml_path):
            raise FileNotFoundError("file EML non trovato sul disco (prova a Re-Indicizzare)")
        with open(eml_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        oggetto = str(msg.get('Subject', '') or '').strip()
        self.progress.emit(self._indice, len(self.elementi), oggetto or os.path.basename(eml_path))

        # Prefisso AAAA.MM.GG HH.mm.ss: le cartelle si ordinano cronologicamente anche con oggetti identici
        prefisso = prefisso_data_ora(msg, data)
        nome_base = prefisso + " " + nome_windows_sicuro(oggetto, self.max_cartella - len(prefisso) - 1,
                                                        "Senza oggetto", con_estensione=False)
        cartella = cartella_libera(self.dir_dest, nome_base)
        os.makedirs(cartella)
        self.report["mail"] += 1
        lavori = []
        self._esporta_messaggio(msg, cartella, data, 0, lavori, nome_pdf=os.path.basename(cartella) + ".pdf")
        self._jobs = [j for j in lavori if j]

    def _esporta_messaggio(self, msg, cartella, data, profondita, lavori, origine=None, nome_pdf=None):
        """Scrive in 'cartella' gli allegati e i dettagli di 'msg'; i postacert.eml vengono salvati e scompattati
        in una sottocartella (ricorsivamente). Il PDF del messaggio viene messo in coda in 'lavori'."""
        oggetto = str(msg.get('Subject', '') or '').strip()
        nome_cartella = os.path.basename(cartella)
        max_file = self._max_file(cartella)
        posto_pdf = len(lavori)
        lavori.append(None)                      # il PDF di questo messaggio precede quelli dei postacert annidati
        voce = {"salvati": [], "verifiche": []}

        for nome, part in allegati_da_msg(msg, per_esportazione=True):
            try:
                dati = payload_allegato(part)
                if not dati:
                    continue
                if e_postacert(nome):
                    self._scompatta_postacert(nome, dati, cartella, max_file, profondita, lavori, voce, oggetto)
                    continue
                nome_finale, dati_finale, estratto = risolvi_p7m(nome, dati)
                nome_p7m = None
                if estratto:
                    # il p7m originale si conserva SEMPRE; la verifica parte in background e non attende nessuno
                    path_p7m = percorso_libero(cartella, nome_windows_sicuro(nome, max_file, "allegato"))
                    with open(path_p7m, 'wb') as f_out:
                        f_out.write(dati)
                    nome_p7m = os.path.basename(path_p7m)
                    voce["salvati"].append((nome_p7m, "originale firmato, conservato"))
                    voce["verifiche"].append((nome_p7m, VerificaFirme.avvia(nome, dati)))
                    self.report["p7m"] += 1
                path_out = percorso_libero(cartella, nome_windows_sicuro(nome_finale, max_file, "allegato"))
                with open(path_out, 'wb') as f_out:
                    f_out.write(dati_finale)
                voce["salvati"].append((os.path.basename(path_out), f"estratto da {nome_p7m}" if nome_p7m else ""))
                if not nome_p7m and e_documento_firmato(nome_finale, dati_finale):
                    # PDF (PAdES) o XML (XAdES) firmato: si verifica come nel P7MReader
                    voce["verifiche"].append((os.path.basename(path_out), VerificaFirme.avvia(os.path.basename(path_out), dati_finale)))
                    self.report["firmati"] += 1
                self.report["allegati"] += 1
            except Exception as e:
                self.report["errori"].append(f"{nome_cartella} / {nome}: {e}")

        # PDF: nome scelto DOPO gli allegati, così non si sovrascrive nulla
        if nome_pdf is None:
            base = nome_windows_sicuro(prefisso_data_ora(msg, data) + " " + (oggetto or "Senza oggetto"),
                                       max(20, max_file - 4), "Senza oggetto", con_estensione=False)
            nome_pdf = base + ".pdf"
        lavori[posto_pdf] = (costruisci_html_mail(msg, data), percorso_libero(cartella, nome_pdf))

        # Dettagli mail.txt: subito, con le verifiche "in corso"; si riscrive quando l'esito è pronto
        def campo(nome_campo):
            return " ".join(str(msg.get(nome_campo, '') or '').split())
        testata = [("Oggetto", oggetto or "(Nessun oggetto)"), ("Da", campo('From')), ("A", campo('To')),
                   ("Cc", campo('Cc')), ("Ccn", campo('Bcc')), ("Rispondi a", campo('Reply-To')),
                   ("Data", data or ""), ("Message-ID", campo('Message-ID')), ("Origine", origine or "")]
        voce["testata"] = [(k, v) for k, v in testata if v]
        voce["path"] = percorso_libero(cartella, "Dettagli mail.txt")
        voce["t0"] = time.monotonic()
        voce["cartella"] = nome_cartella
        self._scrivi_dettagli(voce, finale=not voce["verifiche"])
        if voce["verifiche"]:
            self._attese.append(voce)
            self._timer_verifiche.start()

    def _scompatta_postacert(self, nome, dati, cartella, max_file, profondita, lavori, voce, oggetto_esterno):
        """Salva il postacert.eml originale e ne scompatta il contenuto (il vero messaggio) in una sottocartella."""
        path_pc = percorso_libero(cartella, nome_windows_sicuro(nome, max_file, "postacert.eml"))
        with open(path_pc, 'wb') as f_out:
            f_out.write(dati)
        self.report["postacert"] += 1
        nome_pc = os.path.basename(path_pc)
        if profondita >= self.MAX_PROFONDITA_POSTACERT:
            voce["salvati"].append((nome_pc, "busta PEC: salvata ma non scompattata (troppi livelli annidati)"))
            return
        interno = email.message_from_bytes(dati, policy=policy.default)
        sotto = cartella_libera(cartella, "postacert")
        os.makedirs(sotto)
        data_interno = data_da_msg(interno)
        voce["salvati"].append((nome_pc, f"busta PEC: contenuto scompattato nella cartella «{os.path.basename(sotto)}»"))
        self._esporta_messaggio(interno, sotto, data_interno, profondita + 1, lavori,
                                origine=f"contenuto di {nome_pc} della mail «{oggetto_esterno or 'senza oggetto'}»")

    # ---------- file dei dettagli ----------
    def _scrivi_dettagli(self, voce, finale):
        righe = [f"{k}: {v}" for k, v in voce["testata"]]
        if voce["salvati"]:
            righe += ["", f"Allegati salvati ({len(voce['salvati'])}):"]
            righe += [f"- {n}" + (f"  ({nota})" if nota else "") for n, nota in voce["salvati"]]
        if voce["verifiche"]:
            righe += ["", f"Verifica delle firme digitali ({MOTORE_FIRME}):"]
            for nome_p7m, futuro in voce["verifiche"]:
                if futuro.done():
                    righe += righe_verifica(futuro.result())
                elif finale:
                    righe.append(f"{nome_p7m}: Non verificato - verifica non completata (tempo scaduto o esportazione interrotta)")
                else:
                    righe.append(f"{nome_p7m}: verifica in corso...")
            righe += ["", nota_verifica()]
        try:
            with open(voce["path"], 'w', encoding='utf-8-sig', errors='replace', newline='\r\n') as f_txt:
                f_txt.write("\n".join(righe) + "\n")
        except Exception as e:
            self.report["errori"].append(f"{voce.get('cartella', '')} / Dettagli mail.txt: {e}")

    def _controlla_verifiche(self):
        adesso = time.monotonic()
        rimaste = []
        for voce in self._attese:
            # pronta quando ogni verifica è finita o ha superato il tempo massimo (contato dal suo avvio, non dall'attesa in coda)
            pronte = all(f.done() or VerificaFirme.scaduta(f, adesso) for _, f in voce["verifiche"])
            if pronte or self._cancelled:
                self._scrivi_dettagli(voce, finale=True)
                for _nome, futuro in voce["verifiche"]:
                    self.report[categoria_esito(futuro.result() if futuro.done() else None)] += 1
            else:
                rimaste.append(voce)
        self._attese = rimaste
        if rimaste:
            if self._concludendo:
                self.stato.emit(f"Completamento della verifica delle firme digitali ({len(rimaste)} mail)...")
        else:
            self._timer_verifiche.stop()
            if self._concludendo:
                self._emetti_finale()

    # ---------- generazione PDF ----------
    def _caricamento_finito(self, ok):
        if self._stato != "caricamento":
            return
        self._timer.stop()
        if not ok:
            self.report["errori"].append(f"{os.path.basename(os.path.dirname(self._pdf_path))}: "
                                         "contenuto della mail non caricato del tutto, controlla il PDF")
        self._stampa()

    def _stampa(self):
        self._stato = "stampa"
        self._timer.start(self.TIMEOUT_PDF_MS)
        self.page.printToPdf(self._pdf_path)

    def _pdf_finito(self, percorso, successo):
        if self._stato != "stampa" or os.path.basename(percorso) != os.path.basename(self._pdf_path):
            return
        self._timer.stop()
        self._stato = "idle"
        if successo:
            self.report["pdf"] += 1
        else:
            self.report["errori"].append(f"{os.path.basename(os.path.dirname(self._pdf_path))}: PDF non generato")
        QTimer.singleShot(0, self._prossima)

    def _timeout(self):
        if self._stato == "caricamento":
            # Contenuti remoti lenti o irraggiungibili: interrompo il caricamento e stampo quello che c'è.
            # Lo stato cambia PRIMA di Stop: se Stop emette loadFinished subito, non si stampa due volte.
            self._stato = "attesa_stampa"
            self.page.triggerAction(QWebEnginePage.WebAction.Stop)
            self._stampa()
        elif self._stato == "stampa":
            self._stato = "idle"
            self._nuova_pagina()                  # la stampa bloccata impedirebbe le successive
            self.report["errori"].append(f"{os.path.basename(os.path.dirname(self._pdf_path))}: tempo scaduto nella generazione del PDF")
            QTimer.singleShot(0, self._prossima)

    # ---------- chiusura ----------
    def _concludi(self):
        self._timer.stop()
        self._pulisci_tmp()
        self._stato = "idle"
        self._concludendo = True
        self.report["annullato"] = self._cancelled
        if self._attese:     # restano solo le verifiche delle firme: attendo senza bloccare la GUI
            self.stato.emit("Completamento della verifica delle firme digitali...")
            self._timer_verifiche.start()
            self._controlla_verifiche()
        else:
            self._emetti_finale()

    def _emetti_finale(self):
        if self._terminato:
            return
        self._terminato = True
        self._timer_verifiche.stop()
        self.finished.emit(self.report)

def apri_database(parent, percorso_db):
    """Apre (o crea) l'indice; se non si può (cartella in sola lettura, file rovinato) lo dice invece di chiudersi."""
    try:
        return DatabaseManager(percorso_db)
    except Exception as e:
        mostra_errore_con_copia(parent, "Indice non utilizzabile",
                                f"Non riesco ad aprire o creare l'indice della posta:\n{percorso_db}\n\n{type(e).__name__}: {e}\n\n"
                                "Se la cartella è in sola lettura (DVD, condivisione protetta), copiala sul disco del PC e riaprila. "
                                "Se il file è rovinato, cancella zimbra_index.db: verrà ricreato.")
        return None

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.aggiorna_schema_silenzioso()
        self.crea_tabelle()
        self.migra_percorsi_relativi()

    def migra_percorsi_relativi(self):
        """Indici creati da versioni precedenti: converte i percorsi assoluti in relativi rispetto alla
        cartella del database, anche se nel frattempo la cartella è stata spostata o copiata altrove."""
        try:
            radice = os.path.dirname(os.path.abspath(self.db_path))
            righe = self.conn.execute("SELECT id, file_path FROM emails").fetchall()
            assoluti = [(i, p) for i, p in righe if e_percorso_assoluto(p)]
            if not assoluti:
                return
            spezza = lambda p: [x for x in re.split(r'[\\/]+', p) if x]
            passo = max(1, len(assoluti) // 40)
            campione = [spezza(p) for _, p in assoluti[::passo][:40]]
            migliore_k, migliore_n = None, 0
            for k in range(0, 60):     # quante componenti del vecchio percorso vanno scartate
                n = sum(1 for parti in campione
                        if k < len(parti) and os.path.isfile(os.path.join(radice, *parti[k:])))
                if n > migliore_n:
                    migliore_k, migliore_n = k, n
            if migliore_k is None:
                return                  # file non raggiungibili da qui: lascio i percorsi come sono
            aggiorna = []
            for i, p in assoluti:
                parti = spezza(p)
                if migliore_k < len(parti):
                    aggiorna.append(("/".join(parti[migliore_k:]), i))
            with self.conn:
                self.conn.executemany("UPDATE emails SET file_path = ? WHERE id = ?", aggiorna)
        except Exception:
            pass
        
    def close(self):
        if self.conn:
            try: self.conn.close()
            except Exception: pass
            self.conn = None

    def aggiorna_schema_silenzioso(self):
        try:
            self.conn.execute("ALTER TABLE emails ADD COLUMN corpo TEXT")
        except sqlite3.OperationalError:
            pass                                  # colonna già presente

    def crea_tabelle(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cartella TEXT,
                    mittente TEXT,
                    destinatario TEXT,
                    oggetto TEXT,
                    data TEXT,
                    file_path TEXT,
                    corpo TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS allegati (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER,
                    nome_file TEXT,
                    FOREIGN KEY(email_id) REFERENCES emails(id)
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ricerca ON emails(mittente, oggetto, cartella, data)")
            nuova = not self.conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='elementi'").fetchone()
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS elementi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT, cartella TEXT, titolo TEXT, inizio TEXT, fine TEXT, luogo TEXT, persone TEXT,
                    extra TEXT, testo TEXT, file_path TEXT, dati TEXT
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_elementi ON elementi(tipo, cartella, inizio)")
            # indice creato da una versione precedente (solo posta): calendario, rubrica... vanno ancora letti
            self.serve_indice_pim = nuova and bool(self.conn.execute("SELECT 1 FROM emails LIMIT 1").fetchone())

# ==========================================
# WIDGET CONDIVISI: AVANZAMENTO, ZONA DI RILASCIO, BENVENUTO, ANTEPRIMA
# ==========================================
class _DialogoAvanzamento(QDialog):
    """Finestra di avanzamento: la X ed Esc non annullano, riducono a indicatore."""
    riduci_richiesto = pyqtSignal()

    def reject(self):
        self.riduci_richiesto.emit()

    def closeEvent(self, evento):
        evento.ignore()
        self.riduci_richiesto.emit()

class PannelloAvanzamento(QObject):
    """Avanzamento di un'operazione lunga (importazione, indicizzazione, estrazione, esportazione): finestra NON
    modale che con "Riduci" diventa un piccolo indicatore con la percentuale nella barra in basso della finestra
    principale, così si continua a consultare la posta. Dall'indicatore si riapre la finestra o si annulla."""
    annulla = pyqtSignal()

    def __init__(self, finestra_principale, titolo, etichetta_breve, parent=None, nome_icona="esporta"):
        super().__init__(parent)
        self.finestra = finestra_principale
        self._annullato = False
        self._chiuso = False

        self.dialogo = _DialogoAvanzamento(finestra_principale)
        self.dialogo.setWindowTitle(titolo)
        self.dialogo.setModal(False)
        self.dialogo.setMinimumWidth(520)
        self.dialogo.riduci_richiesto.connect(self.riduci)
        lay = QVBoxLayout(self.dialogo)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.setSpacing(12)
        testa = QHBoxLayout()
        ico = QLabel()
        ico.setPixmap(icona(nome_icona, C["accento"], 22).pixmap(26, 26))
        lbl_titolo = QLabel(titolo)
        lbl_titolo.setObjectName("titoloMedio")
        testa.addWidget(ico)
        testa.addWidget(lbl_titolo, 1)
        self.lbl = QLabel("Preparazione...")
        self.lbl.setObjectName("attenuato")
        self.lbl.setWordWrap(True)
        self.lbl.setMinimumHeight(38)
        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        self.barra.setFormat("%p%")
        self.barra.setAccessibleName(titolo)
        pulsanti = QHBoxLayout()
        self.btn_riduci = pulsante("Riduci e continua a lavorare", "riduci",
                                   suggerimento="Nasconde questa finestra: l'avanzamento resta visibile in basso nella finestra principale")
        self.btn_riduci.clicked.connect(self.riduci)
        self.btn_annulla = pulsante("Annulla", "chiudi", "pericolo")
        self.btn_annulla.clicked.connect(self.chiedi_annullamento)
        pulsanti.addWidget(self.btn_riduci)
        pulsanti.addStretch()
        pulsanti.addWidget(self.btn_annulla)
        lay.addLayout(testa)
        lay.addWidget(self.lbl)
        lay.addWidget(self.barra)
        lay.addLayout(pulsanti)

        self.chip = QWidget()
        self.chip.setObjectName("chipEsportazione")
        self.chip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay_chip = QHBoxLayout(self.chip)
        lay_chip.setContentsMargins(8, 3, 4, 3)
        lay_chip.setSpacing(8)
        ico_chip = QLabel()
        ico_chip.setPixmap(icona(nome_icona, C["accento"], 14).pixmap(16, 16))
        self.lbl_chip = QLabel(etichetta_breve)
        self.barra_chip = QProgressBar()
        self.barra_chip.setObjectName("barraChip")
        self.barra_chip.setRange(0, 100)
        self.barra_chip.setFormat("%p%")
        self.barra_chip.setFixedWidth(150)
        self.barra_chip.setAccessibleName(etichetta_breve)
        btn_mostra = pulsante("Mostra", ruolo="piccolo", suggerimento="Riapre la finestra di avanzamento")
        btn_mostra.clicked.connect(self.mostra)
        self.btn_annulla_chip = pulsante("", "chiudi", "piccolo fantasma", "Annulla l'operazione", C["error"])
        self.btn_annulla_chip.clicked.connect(self.chiedi_annullamento)
        for w in (ico_chip, self.lbl_chip, self.barra_chip, btn_mostra, self.btn_annulla_chip):
            lay_chip.addWidget(w)
        self.chip.hide()
        self._barra_stato().addPermanentWidget(self.chip)
        self._aggiorna_visibilita_barra()      # statusBar() la crea visibile: resta nascosta finché non serve

    def _barra_stato(self):
        return self.finestra.statusBar()

    def _aggiorna_visibilita_barra(self):
        sb = self._barra_stato()
        # isHidden() e non isVisible(): con la barra nascosta anche i suoi indicatori risultano "non visibili"
        sb.setVisible(any(not c.isHidden() for c in sb.findChildren(QWidget, "chipEsportazione")))

    def avvia(self):
        self.dialogo.show()

    def aggiorna(self, percentuale, testo):
        if self._chiuso:
            return
        percentuale = max(0, min(100, int(percentuale)))
        self.barra.setValue(percentuale)
        self.barra_chip.setValue(percentuale)
        if not self._annullato:
            self.lbl.setText(testo)
            self.chip.setToolTip(testo)
            self.barra.setAccessibleDescription(testo)

    def riduci(self):
        self.dialogo.hide()
        self.chip.show()
        self._aggiorna_visibilita_barra()

    def mostra(self):
        self.chip.hide()
        self._aggiorna_visibilita_barra()
        self.dialogo.show()
        self.dialogo.raise_()
        self.dialogo.activateWindow()

    def chiedi_annullamento(self):
        if self._annullato:
            return
        r = QMessageBox.question(self.finestra, "Annullare?",
                                 "Interrompo l'operazione?\n\nQuello che è già stato fatto resta dov'è.",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes or self._chiuso:   # il lavoro può essere finito nel frattempo
            return
        self._annullato = True
        self.lbl.setText("Annullamento in corso...")
        self.chip.setToolTip("Annullamento in corso...")
        self.btn_annulla.setEnabled(False)
        self.btn_annulla_chip.setEnabled(False)
        self.annulla.emit()

    def chiudi(self):
        if self._chiuso:
            return
        self._chiuso = True
        self.dialogo.hide()
        self.dialogo.deleteLater()
        self.chip.hide()
        self._barra_stato().removeWidget(self.chip)
        self.chip.deleteLater()
        self._aggiorna_visibilita_barra()

class SafeWebEnginePage(QWebEnginePage):
    """Anteprima della mail: niente navigazione verso i link (si legge e basta)."""
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class CustomWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPage(SafeWebEnginePage(self))
        self.page().setBackgroundColor(QColor("#FFFFFF"))   # l'area di lettura resta chiara anche con il tema scuro
        self.setAcceptDrops(False)       # i file trascinati li gestisce la finestra principale, non l'anteprima
        self.setAccessibleName("Anteprima")
        self.setZoomFactor(ACCESSIBILITA["scala"])

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        azione_copia = menu.addAction(icona("copia", C["accento_chiaro"]), "Copia")
        azione_seleziona_tutto = menu.addAction(icona("spunta", C["accento_chiaro"]), "Seleziona tutto")
        azione_scelta = menu.exec(event.globalPos())
        if azione_scelta == azione_copia:
            self.page().triggerAction(QWebEnginePage.WebAction.Copy)
        elif azione_scelta == azione_seleziona_tutto:
            self.page().triggerAction(QWebEnginePage.WebAction.SelectAll)

class _Animato(QWidget):
    """Base per i widget animati: il timer gira solo mentre il widget è visibile."""
    def __init__(self, parent=None, intervallo=33):
        super().__init__(parent)
        self._fase = 0.0
        self._timer_anim = QTimer(self)
        self._timer_anim.setInterval(intervallo)
        self._timer_anim.timeout.connect(self._passo)

    def _passo(self):
        self._fase = (self._fase + 0.033) % 3600.0
        self.update()

    def showEvent(self, e):
        # WCAG 2.2.2: il movimento si ferma da solo dopo 5 secondi; con «Riduci le animazioni» non parte proprio
        if not ACCESSIBILITA["animazioni_ridotte"]:
            self._timer_anim.start()
            QTimer.singleShot(5000, self._timer_anim.stop)
        super().showEvent(e)

    def hideEvent(self, e):
        self._timer_anim.stop()
        super().hideEvent(e)

class ZonaRilascio(_Animato):
    """Riquadro "trascina qui" con bordo tratteggiato che scorre e icona che fluttua."""
    scegli_file = pyqtSignal()
    scegli_cartella = pyqtSignal()

    def __init__(self, titolo, sottotitolo, testo_file="Scegli un file…", testo_cartella="Scegli una cartella…", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 104, 30, 26)
        lay.setSpacing(6)
        t = QLabel(titolo)
        t.setObjectName("titoloMedio")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st = QLabel(sottotitolo)
        st.setObjectName("attenuato")
        st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.setWordWrap(True)
        riga = QHBoxLayout()
        riga.addStretch()
        if testo_file:
            b1 = pulsante(testo_file, "documento", "primario")
            b1.clicked.connect(self.scegli_file)
            riga.addWidget(b1)
        if testo_cartella:
            b2 = pulsante(testo_cartella, "cartella")
            b2.clicked.connect(self.scegli_cartella)
            riga.addWidget(b2)
        riga.addStretch()
        lay.addWidget(t)
        lay.addWidget(st)
        lay.addSpacing(10)
        lay.addLayout(riga)
        self._pix = icona("carica", C["accento_chiaro"], 30).pixmap(44, 44)

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        sfondo = QLinearGradient(r.topLeft(), r.bottomRight())
        sfondo.setColorAt(0, QColor(30, 32, 52))
        sfondo.setColorAt(1, QColor(24, 25, 36))
        p.setBrush(sfondo)
        penna = QPen(QColor(C["accento"]), 1.6)
        penna.setStyle(Qt.PenStyle.CustomDashLine)
        penna.setDashPattern([6, 5])
        penna.setDashOffset(-self._fase * 14)          # tratteggio che scorre
        p.setPen(penna)
        p.drawRoundedRect(r, 18, 18)
        # cerchio con alone pulsante e icona che fluttua
        cx, cy = r.center().x(), r.top() + 56
        alone = 0.5 + 0.5 * math.sin(self._fase * 3.0)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(142, 157, 255, int(25 + 35 * alone)))
        p.drawEllipse(QPointF(cx, cy), 34 + 6 * alone, 34 + 6 * alone)
        p.setBrush(QColor(37, 40, 66))
        p.drawEllipse(QPointF(cx, cy), 30, 30)
        dy = 3.5 * math.sin(self._fase * 2.2)
        p.drawPixmap(QPointF(cx - 22, cy - 22 + dy), self._pix)
        p.end()

class CartaFonte(QFrame):
    """Scheda di una sorgente (Zimbra, Gmail, Outlook...) con le istruzioni per ottenere l'export."""
    apri = pyqtSignal(object)

    def __init__(self, nome_icona, titolo, formato, passi, filtro, parent=None):
        super().__init__(parent)
        self.setObjectName("carta")
        self.filtro = filtro
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(8)
        testa = QHBoxLayout()
        ico = QLabel()
        ico.setPixmap(icona(nome_icona, C["accento"], 22).pixmap(26, 26))
        lbl = QLabel(titolo)
        lbl.setObjectName("titoloMedio")
        testa.addWidget(ico)
        testa.addSpacing(4)
        testa.addWidget(lbl, 1)
        fmt = QLabel(formato)
        fmt.setStyleSheet(f"color:{C['accento_chiaro']};font-weight:600;font-size:12px")
        fmt.setWordWrap(True)
        elenco = "".join(f"<tr><td style='color:{C['accento']};font-weight:700;padding:0 8px 4px 0;vertical-align:top'>{i}</td>"
                         f"<td style='color:{C['attenuato']};padding:0 0 4px 0'>{html.escape(t)}</td></tr>"
                         for i, t in enumerate(passi, 1))
        istr = QLabel(f"<table cellspacing='0' cellpadding='0'>{elenco}</table>")
        istr.setWordWrap(True)
        istr.setTextFormat(Qt.TextFormat.RichText)
        b = pulsante("Apri il tuo export…" if filtro != "cartella" else "Scegli la cartella…",
                     "cartella" if filtro == "cartella" else "documento", "piccolo")
        b.clicked.connect(lambda: self.apri.emit(self.filtro))
        lay.addLayout(testa)
        lay.addWidget(fmt)
        lay.addWidget(istr, 1)
        lay.addWidget(b, 0, Qt.AlignmentFlag.AlignLeft)

FONTI_POSTA = [
    ("archivio", "Zimbra / Carbonio", "File .tgz: posta, rubrica, calendario, attività, chat, Valigetta",
     ["Zimbra: Preferenze → Importa/Esporta → «Esporta», tipo «Account», tutti i tipi di dati.",
      "Carbonio: chiedi all'amministratore l'export .tgz della casella (REST «fmt=tgz»); i .ics e .vcf "
      "scaricati dalla webmail vanno bene lo stesso.",
      "Trascina qui il file .tgz così com'è: lo estraggo io."],
     "Export Zimbra / Carbonio (*.tgz *.tar.gz *.tar *.zip *.ics *.vcf)"),
    ("nuvola", "Gmail / Google", "Google Takeout: Posta, Calendar, Contatti, Tasks, Keep, Chat",
     ["Vai su takeout.google.com e premi «Deseleziona tutto».",
      "Seleziona Posta, Calendar, Contatti, Tasks, Keep e Google Chat e crea l'esportazione.",
      "Scarica lo .zip che ti arriva via mail e trascinalo qui: non serve estrarlo."],
     "Google Takeout (*.zip *.mbox *.ics *.vcf *.csv)"),
    ("documento", "Microsoft Outlook", "File .pst / .ost (posta, calendario, contatti, attività), .msg",
     ["In Outlook (classico): File → Apri ed esporta → Importa/Esporta.",
      "Scegli «Esporta in un file» → «File di dati di Outlook (.pst)» e la casella con le sottocartelle.",
      "Trascina qui il file .pst. Anche i contatti in .csv e i calendari in .ics."],
     "Outlook (*.pst *.ost *.msg *.csv *.ics *.vcf)"),
    ("lettere", "Thunderbird", "La cartella del profilo: posta, rubrica e calendario",
     ["Menu ≡ → Aiuto → Informazioni per la risoluzione dei problemi.",
      "Alla voce «Cartella del profilo» premi «Apri cartella».",
      "Trascina qui l'intera cartella del profilo (o solo «Mail» / «ImapMail»)."],
     "cartella"),
    ("busta", "Apple / iCloud", "Mail (.mbox), Calendario (.ics), Contatti (.vcf)",
     ["Mail: Casella → Esporta casella…; Calendario: File → Esporta.",
      "Contatti: seleziona tutto e File → Esporta → vCard.",
      "Metti tutto in una cartella e trascinala qui (anche più caselle insieme)."],
     "cartella"),
    ("pacco", "Altri programmi", "mbox, Maildir, .eml, .emlx, .ics, .vcf, archivi .zip/.tar",
     ["Quasi tutti i programmi esportano la posta in mbox o .eml, l'agenda in .ics e la rubrica in .vcf.",
      "Trascina qui il file o la cartella: il formato lo riconosco da solo.",
      "Una singola mail (.eml, .msg) si apre subito in una scheda."],
     "Posta e dati (*.mbox *.eml *.emlx *.msg *.zip *.tgz *.tar *.tar.gz *.pst *.ost *.ics *.vcf *.csv)"),
]

class SchermataBenvenuto(QScrollArea):
    """Scheda "Inizio": spiega in poche righe come aprire un export, sorgente per sorgente."""
    apri_file = pyqtSignal(str)          # filtro del dialogo
    apri_cartella = pyqtSignal()
    apri_firme = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        contenuto = QWidget()
        contenuto.setObjectName("sfondo")
        self.setWidget(contenuto)
        esterno = QHBoxLayout(contenuto)
        esterno.setContentsMargins(24, 26, 24, 30)
        colonna = QWidget()
        colonna.setMaximumWidth(1120)
        esterno.addStretch()
        esterno.addWidget(colonna, 100)
        esterno.addStretch()
        lay = QVBoxLayout(colonna)
        lay.setSpacing(16)

        titolo = QLabel("Benvenuto")
        titolo.setObjectName("titolo")
        sotto = QLabel("Apri l'archivio della tua posta per cercarla, leggerla ed esportarla in PDF. "
                       "Funziona senza internet e senza server: i file restano sul tuo computer.")
        sotto.setObjectName("sottotitolo")
        sotto.setWordWrap(True)
        lay.addWidget(titolo)
        lay.addWidget(sotto)

        self.zona = ZonaRilascio("Trascina qui il tuo export di posta",
                                 "File o cartella: Zimbra, Gmail, Outlook, Thunderbird, Apple Mail, mbox, .eml…  "
                                 "Il formato lo riconosco io.")
        self.zona.scegli_file.connect(lambda: self.apri_file.emit(""))
        self.zona.scegli_cartella.connect(self.apri_cartella)
        lay.addWidget(self.zona)

        passi = QHBoxLayout()
        passi.setSpacing(12)
        for n, (t, d) in enumerate([("Scarica l'export", "dal tuo servizio di posta: sotto trovi come fare"),
                                    ("Trascinalo qui", "o premi «Scegli un file…». Se serve lo estraggo e lo converto"),
                                    ("Cerca, leggi, esporta", "scrivi e premi Invio per cercare; spunta le mail per esportarle")], 1):
            carta = QFrame()
            carta.setObjectName("pannello")
            cl = QHBoxLayout(carta)
            cl.setContentsMargins(14, 12, 14, 12)
            num = QLabel(str(n))
            num.setFixedSize(30, 30)
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setStyleSheet(f"background:{C['selezione']};color:{C['accento_chiaro']};border-radius:15px;font-weight:700")
            testo = QLabel(f"<b>{html.escape(t)}</b><br><span style='color:{C['attenuato']}'>{html.escape(d)}</span>")
            testo.setWordWrap(True)
            cl.addWidget(num, 0, Qt.AlignmentFlag.AlignTop)
            cl.addSpacing(6)
            cl.addWidget(testo, 1)
            passi.addWidget(carta, 1)
        lay.addLayout(passi)

        etichetta = QLabel("DA QUALE PROGRAMMA ARRIVA LA TUA POSTA?")
        etichetta.setObjectName("etichetta")
        lay.addSpacing(6)
        lay.addWidget(etichetta)
        griglia = QGridLayout()
        griglia.setSpacing(12)
        self.carte = []
        for i, (ic, tit, fmt, passi_fonte, filtro) in enumerate(FONTI_POSTA):
            carta = CartaFonte(ic, tit, fmt, passi_fonte, filtro)
            carta.apri.connect(self._apri_da_carta)
            griglia.addWidget(carta, i // 3, i % 3)
            self.carte.append(carta)
        lay.addLayout(griglia)

        firme = QFrame()
        firme.setObjectName("suggerimento")
        fl = QHBoxLayout(firme)
        fl.setContentsMargins(18, 14, 18, 14)
        ico = QLabel()
        ico.setPixmap(icona("scudo", C["ok"], 24).pixmap(28, 28))
        tf = QLabel("<b>Hai un documento firmato digitalmente?</b><br>"
                    f"<span style='color:{C['attenuato']}'>File .p7m, PDF o XML firmati (anche fatture elettroniche): "
                    "verificali ed estraine il contenuto nella scheda «Verifica firme», con lo stesso motore del P7MReader.</span>")
        tf.setWordWrap(True)
        bf = pulsante("Apri Verifica firme", "scudo")
        bf.clicked.connect(self.apri_firme)
        fl.addWidget(ico, 0, Qt.AlignmentFlag.AlignTop)
        fl.addSpacing(8)
        fl.addWidget(tf, 1)
        fl.addWidget(bf)
        lay.addWidget(firme)
        lay.addStretch()
        self._animato = False

    def _apri_da_carta(self, filtro):
        if filtro == "cartella":
            self.apri_cartella.emit()
        else:
            self.apri_file.emit(filtro)

    def showEvent(self, e):
        super().showEvent(e)
        if not self._animato and not ACCESSIBILITA["animazioni_ridotte"]:   # le schede compaiono una dopo l'altra
            self._animato = True
            self._animazioni = []
            for i, carta in enumerate(self.carte):
                eff = QGraphicsOpacityEffect(carta)
                eff.setOpacity(0.0)
                carta.setGraphicsEffect(eff)
                anim = QPropertyAnimation(eff, b"opacity", self)
                anim.setDuration(420)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.finished.connect(lambda c=carta: c.setGraphicsEffect(None))
                QTimer.singleShot(120 + 70 * i, anim.start)
                self._animazioni.append(anim)

class OverlayRilascio(_Animato):
    """Velo che copre la finestra mentre si trascina un file sopra: dice dove rilasciarlo."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.testo = "Rilascia per aprire"
        self.hide()

    def mostra(self, testo):
        self.testo = testo
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(13, 14, 21, 205))
        r = QRectF(self.rect()).adjusted(18, 18, -18, -18)
        alone = 0.5 + 0.5 * math.sin(self._fase * 4.0)
        penna = QPen(QColor(142, 157, 255, int(150 + 100 * alone)), 2.2)
        penna.setStyle(Qt.PenStyle.CustomDashLine)
        penna.setDashPattern([7, 5])
        penna.setDashOffset(-self._fase * 16)
        p.setPen(penna)
        p.setBrush(QColor(142, 157, 255, 18))
        p.drawRoundedRect(r, 22, 22)
        pix = icona("carica", C["accento_chiaro"], 40).pixmap(64, 64)
        c = r.center()
        p.drawPixmap(QPointF(c.x() - 32, c.y() - 70 + 5 * math.sin(self._fase * 2.5)), pix)
        f = p.font()
        f.setPointSize(17)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(C["testo"]))
        p.drawText(QRectF(r.left(), c.y() + 4, r.width(), 34), Qt.AlignmentFlag.AlignCenter, self.testo)
        p.end()

class Suggerimento(QFrame):
    """Riga di aiuto chiudibile; una volta chiusa non ricompare (si ricorda nelle impostazioni dell'utente)."""
    def __init__(self, chiave, testo_html, parent=None):
        super().__init__(parent)
        self.setObjectName("suggerimento")
        self.chiave = chiave
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 6, 8)
        ico = QLabel()
        ico.setPixmap(icona("aiuto", C["accento"], 16).pixmap(18, 18))
        t = QLabel(testo_html)
        t.setWordWrap(True)
        t.setTextFormat(Qt.TextFormat.RichText)
        chiudi = pulsante("", "chiudi", "piccolo fantasma", "Ho capito, non mostrarlo più")
        chiudi.clicked.connect(self._chiudi)
        lay.addWidget(ico, 0, Qt.AlignmentFlag.AlignTop)
        lay.addWidget(t, 1)
        lay.addWidget(chiudi, 0, Qt.AlignmentFlag.AlignTop)
        if impostazioni().value(f"suggerimenti/{chiave}", False, type=bool):
            self.hide()

    def _chiudi(self):
        impostazioni().setValue(f"suggerimenti/{self.chiave}", True)
        self.hide()

def impostazioni():
    return QSettings("ZimbraViewer", "ZimbraViewer")

def annuncia(widget, testo):
    """Messaggio di stato per i lettori di schermo (WCAG 4.1.3): il nome accessibile del widget cambia e Qt
    lo notifica alle tecnologie assistive; resta visibile anche come suggerimento."""
    try:
        widget.setAccessibleName(testo)
        widget.setAccessibleDescription(testo)
        widget.setToolTip(testo)
    except RuntimeError:
        pass


def tasti_tabella(tabella, colonna_spunta, apri):
    """Tastiera nelle tabelle: Spazio spunta la riga corrente, Invio la apre (WCAG 2.1.1)."""
    def spunta():
        r = tabella.currentRow()
        item = tabella.item(r, colonna_spunta) if r >= 0 and colonna_spunta is not None else None
        if item is not None and item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            item.setCheckState(Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked
                               else Qt.CheckState.Checked)
    for seq, funzione in (("Return", apri), ("Enter", apri), ("Space", spunta)):
        if funzione is spunta and colonna_spunta is None:
            continue
        sc = QShortcut(QKeySequence(seq), tabella)
        sc.setContext(Qt.ShortcutContext.WidgetShortcut)
        sc.activated.connect(funzione)


def preferenza_sistema(nome):
    """Preferenze di accessibilità del sistema operativo (Qt 6.10+): alto contrasto e movimento ridotto."""
    try:
        hints = QApplication.styleHints().accessibility()
        if nome == "contrasto":
            return hints.contrastPreference() == Qt.ContrastPreference.HighContrast
        return hints.motionPreference() == Qt.MotionPreference.ReducedMotion
    except Exception:
        return False


def _impostazione_bool(chiave):
    """True / False se l'utente l'ha scelto, None se segue il sistema."""
    v = impostazioni().value(chiave, None)
    if v in (None, ""):
        return None
    return v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes")


def carica_accessibilita():
    try:
        ACCESSIBILITA["scala"] = min(2.0, max(0.8, float(impostazioni().value("accessibilita/scala", 1.0))))
    except (TypeError, ValueError):
        ACCESSIBILITA["scala"] = 1.0
    for chiave, pref in (("alto_contrasto", "contrasto"), ("animazioni_ridotte", "movimento")):
        scelta = _impostazione_bool(f"accessibilita/{chiave}")
        ACCESSIBILITA[chiave] = preferenza_sistema(pref) if scelta is None else scelta


def applica_stile(app):
    """Foglio di stile alla scala del testo scelta, più la crocetta delle schede fuori da Windows; zoom delle anteprime."""
    stile = costruisci_stile(ACCESSIBILITA["scala"])
    if not IS_WIN:
        # Fusion senza tema di icone mostra una "X" rossa sulle schede: la si sostituisce con una crocetta del tema
        try:
            croce = os.path.join(cartella_temp_allegati(), "chiudi_scheda.svg")
            with open(croce, "w", encoding="utf-8") as f:
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M4.5 4.5l7 7M11.5 4.5l-7 7" '
                        f'stroke="{C["attenuato"]}" stroke-width="1.6" stroke-linecap="round"/></svg>')
            stile += (f"\nQTabBar::close-button {{ image: url({croce.replace(os.sep, '/')}); subcontrol-position: right; "
                      f"border-radius: 4px; margin: 2px; }}\nQTabBar::close-button:hover {{ background: {C['hover']}; }}\n")
        except Exception:
            pass
    app.setStyleSheet(stile)
    for w in app.allWidgets():
        if isinstance(w, CustomWebEngineView):
            w.setZoomFactor(ACCESSIBILITA["scala"])


def costruisci_html_elemento(e):
    """Pagina dell'anteprima per un elemento non di posta: intestazione con i campi, descrizione, conversazione."""
    es = html.escape
    tipo = e.get("tipo", "")
    nome_tipo = {"evento": "Evento", "attivita": "Attività", "contatto": "Contatto", "chat": "Conversazione",
                 "nota": "Nota", "file": "File"}.get(tipo, "Elemento")
    righe = []
    if tipo == "evento":
        quando = e.get("inizio", "")
        if e.get("fine") and e.get("fine") != e.get("inizio"):
            quando += f" → {e['fine']}"
        righe.append(("Quando", quando + (" (tutto il giorno)" if e.get("tutto_giorno") else "")))
        righe.append(("Luogo", e.get("luogo", "")))
    elif tipo == "nota" and e.get("inizio"):
        righe.append(("Modificata", e["inizio"]))
    elif tipo == "chat" and e.get("inizio"):
        righe.append(("Periodo", e["inizio"] + (f" → {e['fine']}" if e.get("fine") and e["fine"] != e["inizio"] else "")))
    elif tipo == "file" and e.get("inizio"):
        righe.append(("Data", e["inizio"]))
    righe += [(k, v) for k, v in e.get("campi", []) if not (tipo == "attivita" and k == "Inizio" and False)]
    righe.append(("Cartella", e.get("cartella", "")))
    tabella = "".join(
        f"<tr><th scope='row' style='width:130px;text-align:left;color:{P['tenue']};font-weight:600;padding:3px 12px 3px 0;"
        f"vertical-align:top'>{es(k)}</th><td style='padding:3px 0;color:{P['testo']};white-space:pre-wrap'>{es(str(v))}</td></tr>"
        for k, v in righe if v)
    foto = ""
    if e.get("foto", "").startswith("data:image"):
        foto = (f"<img src='{es(e['foto'])}' alt='Foto di {es(e.get('titolo', ''))}' "
                f"style='float:right;width:84px;height:84px;object-fit:cover;border-radius:42px;margin:0 0 8px 12px'>")
    testa = (f"<header style=\"background:{P['foglio']};border:1px solid {P['bordo']};border-left:4px solid {P['accento']};"
             f"border-radius:10px;padding:16px 18px;margin:0 0 22px 0\">{foto}"
             f"<p style='margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;"
             f"color:{P['accento_testo']}'>{es(nome_tipo)}</p>"
             f"<h1 style='font-size:19px;font-weight:700;margin:0 0 10px;color:#141625'>{es(e.get('titolo', ''))}</h1>"
             f"<table style='font-size:13px;border-collapse:collapse'>{tabella}</table></header>")
    corpo = ""
    if e.get("descrizione"):
        corpo += (f"<section aria-label='Descrizione' style='font-size:14px;line-height:1.55;white-space:pre-wrap'>"
                  f"{es(e['descrizione'])}</section>")
    if e.get("messaggi"):
        voci = []
        precedente = None
        for m in e["messaggi"]:
            autore = m.get("autore", "")
            testa_m = "" if autore == precedente else (
                f"<p style='margin:12px 0 2px;font-weight:700;color:{P['testo']}'>{es(autore)} "
                f"<span style='font-weight:400;color:{P['tenue']};font-size:12px'>{es(m.get('data', ''))}</span></p>")
            precedente = autore
            voci.append(f"<li style='list-style:none;margin:0'>{testa_m}<p style='margin:0 0 4px;padding:6px 10px;"
                        f"background:{P['fondo_blocco']};border-radius:8px;white-space:pre-wrap'>{es(m.get('testo', ''))}</p></li>")
        corpo += f"<ol aria-label='Messaggi' style='padding:0;margin:0;font-size:14px;line-height:1.45'>{''.join(voci)}</ol>"
    return (f"<!doctype html><html lang='it'><head><meta charset='utf-8'><title>{es(e.get('titolo', ''))}</title>"
            f"{STILE_BASE_PAGINA}</head><body style=\"margin:0;padding:22px;background:{P['foglio']};color:{P['testo']};"
            f"font-family:{FONT_PAGINA}\"><main>{testa}{corpo}</main></body></html>")


# Colonne della tabella per ogni tipo di elemento: (intestazione, campo della riga). Intestazione vuota = colonna nascosta
COLONNE_ELEMENTI = {
    "evento": [("Titolo", "titolo"), ("Inizio", "inizio"), ("Fine", "fine"), ("Luogo", "luogo")],
    "attivita": [("Titolo", "titolo"), ("Scadenza", "inizio"), ("Stato", "extra"), ("", "luogo")],
    "contatto": [("Nome", "titolo"), ("Email e telefoni", "persone"), ("Azienda", "luogo"), ("", "fine")],
    "chat": [("Conversazione", "titolo"), ("Inizio", "inizio"), ("Ultimo messaggio", "fine"), ("Partecipanti", "persone")],
    "nota": [("Titolo", "titolo"), ("Modificata", "inizio"), ("", "fine"), ("", "luogo")],
    "file": [("Nome", "titolo"), ("Data", "inizio"), ("Dimensione", "extra"), ("", "luogo")],
}
SQL_ELEMENTI = "SELECT id, titolo, inizio, fine, luogo, persone, extra, cartella FROM elementi"
_CAMPI_RIGA = {"titolo": 1, "inizio": 2, "fine": 3, "luogo": 4, "persone": 5, "extra": 6}

# ==========================================
# SCHEDA DELLA POSTA (export indicizzato oppure singola mail)
# ==========================================
class MailViewerTab(QWidget):
    def __init__(self, path, mode="export", parent_app=None, auto_index=False):
        super().__init__()
        self.path = path
        self.mode = mode
        self.parent_app = parent_app
        self.auto_index = auto_index
        self.db = None
        self.current_eml_path = path if mode == "eml" else None
        self.current_data = ""
        self.checkbox_allegati = []
        self.esportatore = None
        self.pannello_exp = None
        self._export_in_corso = False
        self.worker = None
        self.pannello_idx = None
        self.worker_estrazione_att = None
        self.pannello_att = None
        self._indice_nuovo = False
        self._stampa_in_corso = False
        self.sezione = "posta"                 # posta | evento | attivita | contatto | chat | nota | file
        self._elemento_corrente = None
        self._anteprima_pronta = False
        self._ricerca_attiva = False

        self.layout_principale = QVBoxLayout(self)
        self.layout_principale.setContentsMargins(12, 12, 12, 12)
        self.layout_principale.setSpacing(10)
        if self.mode == "export":
            self.inizializza_ui_export()
            QTimer.singleShot(100, self.verifica_database_e_carica)   # dopo che la UI è disegnata
        else:
            self.inizializza_ui_eml()
            QTimer.singleShot(100, lambda: self.carica_singolo_eml(self.path))

    def _finestra(self):
        return self.parent_app or self.window()

    def percorso_eml(self, salvato):
        """Percorso reale del file .eml: l'indice conserva solo il percorso relativo alla cartella dell'export."""
        return risolvi_percorso_eml(self.path, salvato)

    def _percorso_da_id(self, email_id):
        if not self.db:
            return None
        res = self.db.conn.execute("SELECT file_path FROM emails WHERE id = ?", (email_id,)).fetchone()
        return self.percorso_eml(res[0]) if res else None

    def _allegati_da_id(self, email_id):
        return [r[0] for r in self.db.conn.execute(
            f"SELECT nome_file FROM allegati WHERE email_id = ? AND {FILTRO_ALLEGATI_SQL}", (email_id,))]

    def chiudi(self):
        if self.esportatore is not None:
            self.esportatore.interrompi()
            self.esportatore = None
        for nome in ("pannello_exp", "pannello_idx", "pannello_att"):
            pannello = getattr(self, nome)
            if pannello is not None:
                pannello.chiudi()
                setattr(self, nome, None)
        self._export_in_corso = False
        for worker in (self.worker, self.worker_estrazione_att):
            if worker is not None and worker.isRunning():
                worker.cancel()
                worker.wait()
        if self.db:
            self.db.close()
            self.db = None
        if hasattr(self, 'preview_mail'):
            self.preview_mail.setHtml("")

    # ---------- interfaccia ----------
    def inizializza_ui_export(self):
        barra = QHBoxLayout()
        barra.setSpacing(8)
        self.barra_ricerca = QLineEdit()
        self.barra_ricerca.addAction(icona("cerca", C["tenue"]), QLineEdit.ActionPosition.LeadingPosition)
        self.barra_ricerca.setPlaceholderText("Cerca in mittenti, destinatari, oggetti, testo e allegati… poi premi Invio")
        self.barra_ricerca.setToolTip("Premi Invio per cercare (tutte le parole devono comparire).\n"
                                      "Usa <frase esatta> tra parentesi angolari per una frase intera.\n"
                                      "Svuota il campo per tornare all'elenco.")
        self.barra_ricerca.setClearButtonEnabled(True)
        self.barra_ricerca.setAcceptDrops(False)
        self.barra_ricerca.setEnabled(False)
        self.barra_ricerca.setAccessibleName("Cerca nella posta")
        self.barra_ricerca.setAccessibleDescription("Scrivi e premi Invio. Ctrl+F porta qui da qualunque punto")
        self.barra_ricerca.returnPressed.connect(self.avvia_ricerca)          # solo con Invio: è più veloce
        self.barra_ricerca.textChanged.connect(self.ricerca_testo_cambiato)
        self.barra_ricerca.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_risultati = QLabel("")
        self.lbl_risultati.setObjectName("lblRisultati")
        self.lbl_risultati.setMinimumWidth(80)
        self.lbl_risultati.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.btn_esporta = pulsante("Esporta PDF + allegati", "esporta", "primario",
                                    "Esporta le mail spuntate: una cartella per ogni mail con il PDF, gli allegati\n"
                                    "(i .p7m estratti e verificati), le buste PEC scompattate e i dettagli.")
        self.btn_esporta.clicked.connect(self._esporta_secondo_sezione)
        self.btn_esporta.setEnabled(False)
        self.btn_altro = pulsante("Altro", "tabella", suggerimento="Altre azioni sull'elenco")
        menu = QMenu(self)
        menu.addAction(icona("scarica", C["accento_chiaro"]), "Salva gli allegati delle mail spuntate…", self.estrai_allegati_massivi)
        menu.addAction(icona("tabella", C["accento_chiaro"]), "Esporta l'elenco in CSV…", self.esporta_elenco_csv)
        menu.addSeparator()
        menu.addAction(icona("spunta", C["accento_chiaro"]), "Spunta tutte", lambda: self.imposta_spunte_massivo(Qt.CheckState.Checked))
        menu.addAction(icona("chiudi", C["accento_chiaro"]), "Togli tutte le spunte", lambda: self.imposta_spunte_massivo(Qt.CheckState.Unchecked))
        menu.addSeparator()
        self.azione_indicizza = menu.addAction(icona("aggiorna", C["accento_chiaro"]), "Ricostruisci l'indice", self.avvia_indicizzazione)
        self.btn_altro.setMenu(menu)
        barra.addWidget(self.barra_ricerca, 1)
        barra.addWidget(self.lbl_risultati)
        barra.addWidget(self.btn_altro)
        barra.addWidget(self.btn_esporta)
        self.layout_principale.addLayout(barra, 0)
        self.layout_principale.addWidget(Suggerimento(
            "scheda_posta",
            "<b>Come si usa:</b> a sinistra scegli la sezione (posta, calendario, contatti, attività, chat, note, file) "
            "e la cartella (vedi anche il contenuto delle sottocartelle) "
            "o cerca (scrivi e premi <b>Invio</b>). "
            "Per esportare, <b>spunta le mail</b> con la casella accanto al mittente e premi <b>Esporta PDF + allegati</b>. "
            "Doppio clic su una mail per aprirla in una scheda tutta sua."))

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        sinistra = QWidget()
        ls = QVBoxLayout(sinistra)
        ls.setContentsMargins(0, 0, 0, 0)
        ls.setSpacing(6)
        self.lbl_sezioni = QLabel("SEZIONI")
        self.lbl_sezioni.setObjectName("etichetta")
        self.lista_sezioni = QListWidget()
        self.lista_sezioni.setAccessibleName("Sezioni dell'export")
        self.lista_sezioni.setAccessibleDescription("Posta, calendario, attività, contatti, chat, note e file contenuti nell'export")
        self.lista_sezioni.setIconSize(QSize(16, 16))
        self.lista_sezioni.currentRowChanged.connect(self._sezione_scelta)
        self.lbl_sezioni.setBuddy(self.lista_sezioni)
        self.lbl_cartelle = QLabel("CARTELLE")
        self.lbl_cartelle.setObjectName("etichetta")
        self.albero_cartelle = QTreeWidget()
        self.albero_cartelle.setHeaderHidden(True)
        self.albero_cartelle.setIndentation(14)
        self.albero_cartelle.setAccessibleName("Cartelle")
        self.albero_cartelle.setAccessibleDescription("Scegli una cartella con le frecce: l'elenco a destra si aggiorna")
        # frecce, Invio e clic: l'elenco segue la cartella corrente (prima bastava solo il clic del mouse)
        self.albero_cartelle.currentItemChanged.connect(lambda cur, _prec: cur is not None and self.carica_mail_per_cartella(cur, 0))
        self.albero_cartelle.itemClicked.connect(self._cartella_cliccata)
        self.lbl_cartelle.setBuddy(self.albero_cartelle)
        for w in (self.lbl_sezioni, self.lista_sezioni):
            w.hide()                          # compaiono solo se l'export contiene anche altri dati
        ls.addWidget(self.lbl_sezioni)
        ls.addWidget(self.lista_sezioni)
        ls.addWidget(self.lbl_cartelle)
        ls.addWidget(self.albero_cartelle, 1)
        main_splitter.addWidget(sinistra)

        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.tabella_mail = QTableWidget(0, 6)
        self.tabella_mail.setHorizontalHeaderLabels(["ID", "Cartella", "Mittente", "Oggetto", "Data", ""])
        self.tabella_mail.setColumnHidden(0, True)
        header = self.tabella_mail.horizontalHeader()
        for col, larghezza in ((1, 130), (2, 230), (4, 130), (5, 40)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.tabella_mail.setColumnWidth(col, larghezza)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setHighlightSections(False)
        self.tabella_mail.horizontalHeaderItem(5).setIcon(icona("graffetta", C["tenue"], 14))
        self.tabella_mail.horizontalHeaderItem(5).setToolTip("Allegati")
        self.tabella_mail.horizontalHeaderItem(5).setData(Qt.ItemDataRole.AccessibleTextRole, "Allegati")
        self.tabella_mail.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella_mail.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella_mail.itemSelectionChanged.connect(self.mostra_anteprima_mail_da_tabella)
        self.tabella_mail.setShowGrid(False)
        self.tabella_mail.setAlternatingRowColors(True)
        self.tabella_mail.setWordWrap(False)
        self.tabella_mail.cellDoubleClicked.connect(self.apri_mail_in_scheda)
        header.setSortIndicator(4, Qt.SortOrder.DescendingOrder)        # di default: dalla più recente
        self.tabella_mail.setSortingEnabled(True)
        self.tabella_mail.verticalHeader().setVisible(False)
        self.tabella_mail.verticalHeader().setDefaultSectionSize(34)
        self.tabella_mail.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabella_mail.customContextMenuRequested.connect(self.menu_contestuale_tabella)
        self.tabella_mail.setAccessibleName("Elenco delle mail")
        self.tabella_mail.setAccessibleDescription("Spazio spunta la mail, Invio la apre in una nuova scheda, "
                                                   "tasto Menu o Maiusc+F10 per le altre azioni")
        self.tabella_elementi = QTableWidget(0, 6)
        self.tabella_elementi.setColumnHidden(0, True)
        he = self.tabella_elementi.horizontalHeader()
        for col, larghezza in ((2, 150), (3, 150), (4, 220), (5, 160)):
            he.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.tabella_elementi.setColumnWidth(col, larghezza)
        he.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        he.setHighlightSections(False)
        self.tabella_elementi.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella_elementi.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella_elementi.setShowGrid(False)
        self.tabella_elementi.setAlternatingRowColors(True)
        self.tabella_elementi.setWordWrap(False)
        self.tabella_elementi.verticalHeader().setVisible(False)
        self.tabella_elementi.verticalHeader().setDefaultSectionSize(34)
        self.tabella_elementi.itemSelectionChanged.connect(self.mostra_elemento_da_tabella)
        self.tabella_elementi.cellDoubleClicked.connect(lambda *_: self.apri_file_elemento())
        self.tabella_elementi.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabella_elementi.customContextMenuRequested.connect(self.menu_contestuale_elementi)
        self.pila_elenchi = QStackedWidget()
        self.pila_elenchi.addWidget(self.tabella_mail)
        self.pila_elenchi.addWidget(self.tabella_elementi)
        self.content_splitter.addWidget(self.pila_elenchi)
        self.tabella_elementi.setAccessibleName("Elenco degli elementi")
        self.tabella_elementi.setAccessibleDescription("Spazio spunta l'elemento, tasto Menu o Maiusc+F10 per le azioni")
        tasti_tabella(self.tabella_mail, 2, lambda: self.apri_mail_in_scheda(self.tabella_mail.currentRow()))
        tasti_tabella(self.tabella_elementi, 1, self.apri_file_elemento)
        self.costruisci_area_preview(self.content_splitter)
        self.content_splitter.setStretchFactor(0, 1)
        self.content_splitter.setStretchFactor(1, 1)
        self.content_splitter.setSizes([380, 440])
        main_splitter.addWidget(self.content_splitter)
        main_splitter.setSizes([230, 1100])
        self.layout_principale.addWidget(main_splitter, 1)

    def inizializza_ui_eml(self):
        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.costruisci_area_preview(self.content_splitter)
        self.layout_principale.addWidget(self.content_splitter, 1)

    def costruisci_area_preview(self, parent_splitter):
        preview_allegati_splitter = QSplitter(Qt.Orientation.Horizontal)
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)
        toolbar = QHBoxLayout()
        self.btn_pdf = pulsante("Stampa come PDF", "stampa", suggerimento="Salva questa mail in un file PDF")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.clicked.connect(self.salva_pdf)
        self.btn_esporta_mail = pulsante("Esporta mail completa", "pacco",
                                         suggerimento="Crea una cartella con PDF, allegati (p7m estratti e verificati), buste PEC scompattate e dettagli")
        self.btn_esporta_mail.setEnabled(False)
        self.btn_esporta_mail.clicked.connect(self.esporta_mail_corrente)
        self.btn_apri_file = pulsante("Apri il file", "apri", suggerimento="Apre il file con il programma predefinito")
        self.btn_apri_file.clicked.connect(self.apri_file_elemento)
        self.btn_salva_file = pulsante("Salva una copia…", "scarica", suggerimento="Salva una copia del file dove vuoi")
        self.btn_salva_file.clicked.connect(self.salva_file_elemento)
        for b in (self.btn_apri_file, self.btn_salva_file):
            b.hide()
        toolbar.addWidget(self.btn_pdf)
        toolbar.addWidget(self.btn_esporta_mail)
        toolbar.addWidget(self.btn_apri_file)
        toolbar.addWidget(self.btn_salva_file)
        toolbar.addStretch()
        preview_layout.addLayout(toolbar)
        self.preview_mail = CustomWebEngineView()
        self.preview_mail.setAccessibleName("Anteprima della mail" if self.mode == "eml" else "Anteprima")
        self.preview_mail.page().pdfPrintingFinished.connect(self.pdf_completato)
        self.preview_mail.setHtml(html_avviso("Nessuna mail selezionata",
                                              "Scegli una mail dall'elenco per leggerla qui." if self.mode == "export" else "Caricamento…"))
        preview_layout.addWidget(self.preview_mail, 1)
        preview_allegati_splitter.addWidget(preview_widget)

        self.pannello_allegati_widget = QFrame()
        self.pannello_allegati_widget.setObjectName("pannello")
        pannello = QVBoxLayout(self.pannello_allegati_widget)
        pannello.setContentsMargins(12, 12, 12, 12)
        pannello.setSpacing(8)
        testa = QHBoxLayout()
        self.lbl_allegati = QLabel("ALLEGATI")
        self.lbl_allegati.setObjectName("etichetta")
        b_tutti = pulsante("Tutti", ruolo="piccolo fantasma")
        b_tutti.clicked.connect(self.seleziona_tutti_allegati)
        b_nessuno = pulsante("Nessuno", ruolo="piccolo fantasma")
        b_nessuno.clicked.connect(self.deseleziona_tutti_allegati)
        testa.addWidget(self.lbl_allegati)
        testa.addStretch()
        testa.addWidget(b_tutti)
        testa.addWidget(b_nessuno)
        pannello.addLayout(testa)
        scroll_area = QScrollArea()
        scroll_area.setObjectName("elenco")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.area_checkbox_widget = QWidget()
        self.area_checkbox_widget.setStyleSheet(f"background:{C['superficie']}")
        self.layout_checkbox = QVBoxLayout(self.area_checkbox_widget)
        self.layout_checkbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_checkbox.setContentsMargins(2, 2, 2, 2)
        self.layout_checkbox.setSpacing(4)
        scroll_area.setWidget(self.area_checkbox_widget)
        pannello.addWidget(scroll_area, 1)
        azioni = QHBoxLayout()
        self.btn_apri_selezionati = pulsante("Apri", "apri", suggerimento="Apre gli allegati spuntati senza salvarli")
        self.btn_apri_selezionati.clicked.connect(self.apri_allegati_selezionati)
        self.btn_salva_selezionati = pulsante("Salva…", "scarica", "primario",
                                              "Salva gli allegati spuntati (dei .p7m si salvano l'originale e il documento estratto)")
        self.btn_salva_selezionati.clicked.connect(self.salva_allegati_selezionati)
        azioni.addWidget(self.btn_apri_selezionati, 1)
        azioni.addWidget(self.btn_salva_selezionati, 1)
        pannello.addLayout(azioni)
        self.pannello_allegati_widget.setVisible(False)
        preview_allegati_splitter.addWidget(self.pannello_allegati_widget)
        preview_allegati_splitter.setSizes([700, 320])
        parent_splitter.addWidget(preview_allegati_splitter)

    # ---------- indice ----------
    def verifica_database_e_carica(self):
        percorso_db = os.path.join(self.path, NOME_DB)
        if os.path.exists(percorso_db):
            self.db = apri_database(self, percorso_db)
            if self.db is None:
                self.preview_mail.setHtml(html_avviso("Indice non disponibile", "Vedi il messaggio di errore.", "documento", C["error"]))
                return
            self._abilita_ricerca(True)
            self.aggiorna_sezioni()
            if getattr(self.db, "serve_indice_pim", False) and contiene_pim(self.path):
                self.avvia_indicizzazione(solo_pim=True)      # indice di una versione precedente: si aggiungono agenda, rubrica...
        else:
            # Prima apertura: si indicizza subito, senza domande (l'utente può ridurre o annullare)
            self.avvia_indicizzazione()

    def _abilita_ricerca(self, attiva):
        self.barra_ricerca.setEnabled(attiva)
        self.btn_esporta.setEnabled(attiva)
        self.azione_indicizza.setEnabled(attiva)

    def avvia_indicizzazione(self, solo_pim=False):
        if self.worker is not None and self.worker.isRunning():
            return
        if not self.db:
            self._indice_nuovo = not os.path.exists(os.path.join(self.path, NOME_DB))
            self.db = apri_database(self, os.path.join(self.path, NOME_DB))
            if self.db is None:
                self.preview_mail.setHtml(html_avviso("Indice non disponibile", "Vedi il messaggio di errore.", "documento", C["error"]))
                return
        self._abilita_ricerca(False)
        self.pannello_idx = PannelloAvanzamento(self._finestra(), "Preparo l'elenco" if not solo_pim else
                                                "Leggo calendario, contatti e altri dati",
                                                f"Indicizzazione {os.path.basename(self.path)}", self, "aggiorna")
        self.pannello_idx.aggiorna(0, "Leggo mail, calendario, contatti, attività, chat e note e creo l'indice per la "
                                      "ricerca: si fa una volta sola.")
        self.worker = IndexerWorker(self.path, self.db.db_path, solo_pim=solo_pim)
        self.worker.progress.connect(self.aggiorna_progress_idx)
        self.worker.finished.connect(self.indicizzazione_completata)
        self.pannello_idx.annulla.connect(self.worker.cancel)
        self.pannello_idx.avvia()
        self.worker.start()

    def aggiorna_progress_idx(self, attuale, totale):
        if self.pannello_idx is not None:
            self.pannello_idx.aggiorna(attuale * 100 // max(1, totale), f"Elementi letti: {attuale} di {totale}\n"
                                       "Puoi ridurre questa finestra: l'elenco compare appena ho finito.")

    def indicizzazione_completata(self):
        if self.worker is not None:
            self.worker.wait()
        annullata = self.worker is not None and self.worker._is_cancelled
        if self.pannello_idx is not None:
            self.pannello_idx.chiudi()
            self.pannello_idx = None
        if annullata and self._indice_nuovo:
            # prima indicizzazione annullata: niente indice a metà, la prossima volta si riparte da capo
            if self.db:
                self.db.close()
                self.db = None
            try:
                os.remove(os.path.join(self.path, NOME_DB))
            except OSError:
                pass
            self.preview_mail.setHtml(html_avviso("Indicizzazione annullata",
                                                  "Riapri la cartella quando vuoi: l'indice verrà creato da capo.", "aggiorna", C["warn"]))
            return
        self._indice_nuovo = False
        self._abilita_ricerca(True)
        if self.db is not None:
            self.db.serve_indice_pim = False
        self.aggiorna_sezioni()                   # anche se annullata: l'indice precedente è rimasto intatto

    def aggiorna_sezioni(self):
        """Sezioni presenti nell'export (Posta, Calendario, Contatti...) con il numero di elementi."""
        if not self.db:
            return
        n_mail = self.db.conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
        conta = dict(self.db.conn.execute("SELECT tipo, COUNT(*) FROM elementi GROUP BY tipo").fetchall())
        voci = [("posta", "Posta", "busta", n_mail)] + [(t, n, ic, conta[t]) for t, n, ic in TIPI_PIM if conta.get(t)]
        self.lista_sezioni.blockSignals(True)
        self.lista_sezioni.clear()
        riga_corrente = 0
        for i, (tipo, nome, ic, n) in enumerate(voci):
            voce = QListWidgetItem(icona(ic, C["accento"], 16), f"{nome}  ({n})")
            voce.setData(Qt.ItemDataRole.UserRole, tipo)
            voce.setData(Qt.ItemDataRole.AccessibleTextRole, f"{nome}, {n} elementi")
            self.lista_sezioni.addItem(voce)
            if tipo == self.sezione:
                riga_corrente = i
        self.lista_sezioni.setFixedHeight(min(8, len(voci)) * 30 + 8)
        self.lista_sezioni.blockSignals(False)
        mostra = len(voci) > 1
        self.lbl_sezioni.setVisible(mostra)
        self.lista_sezioni.setVisible(mostra)
        if n_mail == 0 and len(voci) > 1 and self.sezione == "posta":
            riga_corrente = 1                      # export senza posta (solo rubrica, solo calendario...)
        self.lista_sezioni.setCurrentRow(riga_corrente)
        self._sezione_scelta(riga_corrente)

    def _sezione_scelta(self, riga):
        voce = self.lista_sezioni.item(riga) if riga >= 0 else None
        self.sezione = voce.data(Qt.ItemDataRole.UserRole) if voce is not None else "posta"
        posta = self.sezione == "posta"
        self.pila_elenchi.setCurrentIndex(0 if posta else 1)
        self.pannello_allegati_widget.setVisible(False)
        self.btn_esporta_mail.setVisible(posta)
        for b in (self.btn_apri_file, self.btn_salva_file):
            b.setVisible(self.sezione == "file")
            b.setEnabled(False)
        self.btn_esporta.setText("Esporta PDF + allegati" if posta else "Esporta…")
        self.btn_esporta.setToolTip(
            "Esporta le mail spuntate: una cartella per ogni mail con il PDF, gli allegati\n"
            "(i .p7m estratti e verificati), le buste PEC scompattate e i dettagli." if posta else
            "Esporta gli elementi spuntati (o tutti quelli in elenco) in .ics, .vcf o .csv")
        nome = NOMI_TIPI_PIM.get(self.sezione, "Posta")
        self.barra_ricerca.setPlaceholderText(
            "Cerca in mittenti, destinatari, oggetti, testo e allegati… poi premi Invio" if posta else
            f"Cerca in {nome.lower()}… poi premi Invio")
        self.barra_ricerca.setAccessibleName(f"Cerca in {nome.lower()}")
        self.current_eml_path = None
        self._elemento_corrente = None
        self._anteprima_pronta = False
        self.btn_pdf.setEnabled(False)
        self.btn_esporta_mail.setEnabled(False)
        if posta:
            self.preview_mail.setHtml(html_avviso("Nessuna mail selezionata", "Scegli una mail dall'elenco per leggerla qui."))
        else:
            self.preview_mail.setHtml(html_avviso(f"{nome}: scegli un elemento", "Selezionalo nell'elenco per vederlo qui.",
                                                  dict((t, ic) for t, _n, ic in TIPI_PIM).get(self.sezione, "busta")))
        self.aggiorna_lista_cartelle()

    def _cartella_cliccata(self, item, _col):
        if self._ricerca_attiva:              # dopo una ricerca un clic sulla stessa cartella torna al suo elenco
            self.carica_mail_per_cartella(item, 0)

    def aggiorna_lista_cartelle(self):
        if not self.db:
            return
        self._ricerca_attiva = False
        self.albero_cartelle.blockSignals(True)
        self.albero_cartelle.clear()
        if self.sezione == "posta":
            cartelle = [r[0] for r in self.db.conn.execute("SELECT DISTINCT cartella FROM emails ORDER BY cartella")]
        else:
            cartelle = [r[0] for r in self.db.conn.execute(
                "SELECT DISTINCT cartella FROM elementi WHERE tipo = ? ORDER BY cartella", (self.sezione,))]
        icona_cartella = icona("cartella", C["accento"], 16)
        nodi = {}
        radice = self.albero_cartelle.invisibleRootItem()
        for percorso_cartella in cartelle:
            padre, progressivo = radice, ""
            for parte in str(percorso_cartella).split("/"):
                progressivo = f"{progressivo}/{parte}" if progressivo else parte
                if progressivo not in nodi:
                    nodo = QTreeWidgetItem(padre, [parte])
                    nodo.setData(0, Qt.ItemDataRole.UserRole, progressivo)
                    nodo.setIcon(0, icona_cartella)
                    nodi[progressivo] = nodo
                padre = nodi[progressivo]
        self.albero_cartelle.expandAll()
        self.albero_cartelle.blockSignals(False)
        # si apre subito la posta in arrivo (o la prima cartella): zero clic
        if self.sezione != "posta":
            self.albero_cartelle.setCurrentIndex(QModelIndex())
            self.esegui_ricerca("")                # tutti gli elementi della sezione
        elif radice.childCount() > 0:
            scelto = next((radice.child(i) for i in range(radice.childCount())
                           if radice.child(i).text(0) == "Posta in arrivo"), radice.child(0))
            self.albero_cartelle.setCurrentItem(scelto)
        else:
            self.popola_tabella([])
            self.preview_mail.setHtml(html_avviso("Nessuna mail trovata", "In questa cartella non ci sono file .eml.", "busta", C["warn"]))

    def carica_mail_per_cartella(self, item, column):
        if not self.db or item is None:
            return
        self._ricerca_attiva = False
        cartella = item.data(0, Qt.ItemDataRole.UserRole)
        # la cartella e tutte le sue sottocartelle, a qualunque profondità: confronto sul prefisso "percorso/"
        # (non LIKE: i caratteri % e _ nei nomi darebbero falsi positivi e ignorerebbe maiuscole/minuscole)
        prefisso = f"{cartella}/"
        if self.sezione != "posta":
            self.popola_elementi(self.db.conn.execute(
                f"{SQL_ELEMENTI} WHERE tipo = ? AND (cartella = ? OR substr(cartella, 1, ?) = ?) "
                f"ORDER BY {self._ordine_elementi()}", (self.sezione, cartella, len(prefisso), prefisso)).fetchall())
            return
        self.popola_tabella(self.db.conn.execute(
            f"{SQL_ELENCO} WHERE cartella = ? OR substr(cartella, 1, ?) = ? ORDER BY data DESC",
            (cartella, len(prefisso), prefisso)).fetchall())

    # ---------- ricerca ----------
    def avvia_ricerca(self):
        self.esegui_ricerca(self.barra_ricerca.text())

    def ricerca_testo_cambiato(self, testo):
        if testo == "" and self.db:
            self.esegui_ricerca("")

    def esegui_ricerca(self, testo):
        if not self.db:
            return
        testo = testo.strip()
        self.albero_cartelle.blockSignals(True)
        self.albero_cartelle.setCurrentIndex(QModelIndex())
        self.albero_cartelle.clearSelection()
        self.albero_cartelle.blockSignals(False)
        self._ricerca_attiva = True
        termini = re.findall(r'<(.*?)>', testo) + [p for p in re.sub(r'<.*?>', '', testo).split() if p.strip()]
        if self.sezione != "posta":
            blocco = "(titolo LIKE ? OR luogo LIKE ? OR persone LIKE ? OR cartella LIKE ? OR testo LIKE ?)"
            parametri = [self.sezione] + [p for t in termini for p in [f"%{t}%"] * 5]
            dove = " AND ".join(["tipo = ?"] + [blocco] * len(termini))
            self.popola_elementi(self.db.conn.execute(
                f"{SQL_ELEMENTI} WHERE {dove} ORDER BY {self._ordine_elementi()}", parametri).fetchall())
            return
        if not testo:
            self.popola_tabella(self.db.conn.execute(f"{SQL_ELENCO} ORDER BY data DESC LIMIT 500").fetchall())
            return
        if not termini:
            return
        blocco = ("(mittente LIKE ? OR destinatario LIKE ? OR oggetto LIKE ? OR cartella LIKE ? OR corpo LIKE ? OR "
                  f"EXISTS (SELECT 1 FROM allegati WHERE email_id = emails.id AND nome_file LIKE ? AND {FILTRO_ALLEGATI_SQL}))")
        parametri = [p for t in termini for p in [f"%{t}%"] * 6]
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            risultati = self.db.conn.execute(
                f"{SQL_ELENCO} WHERE {' AND '.join([blocco] * len(termini))} ORDER BY data DESC", parametri).fetchall()
        finally:
            QApplication.restoreOverrideCursor()
        self.popola_tabella(risultati)

    def popola_tabella(self, rows):
        self.tabella_mail.setSortingEnabled(False)        # evita che le righe si spostino durante il riempimento
        self.tabella_mail.setUpdatesEnabled(False)
        self.tabella_mail.setRowCount(0)
        self.tabella_mail.setRowCount(len(rows))
        ico_allegato = icona("graffetta", C["accento_chiaro"], 14)
        for r, riga in enumerate(rows):
            self.tabella_mail.setItem(r, 0, QTableWidgetItem(str(riga[0])))
            item_cartella = QTableWidgetItem(str(riga[1]))
            item_cartella.setToolTip(str(riga[1]))        # il percorso completo: la colonna può troncarlo
            self.tabella_mail.setItem(r, 1, item_cartella)
            item_mittente = QTableWidgetItem(str(riga[2]))
            item_mittente.setFlags(item_mittente.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item_mittente.setCheckState(Qt.CheckState.Unchecked)
            item_mittente.setToolTip(str(riga[2]))
            self.tabella_mail.setItem(r, 2, item_mittente)
            item_oggetto = QTableWidgetItem(str(riga[3]))
            item_oggetto.setToolTip(str(riga[3]))
            self.tabella_mail.setItem(r, 3, item_oggetto)
            item_data = QTableWidgetItem(str(riga[4]))
            item_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabella_mail.setItem(r, 4, item_data)
            item_all = QTableWidgetItem("")
            if riga[5] > 0:
                item_all.setIcon(ico_allegato)
                item_all.setToolTip(f"{riga[5]} allegati" if riga[5] > 1 else "1 allegato")
                item_all.setData(Qt.ItemDataRole.AccessibleTextRole, f"{riga[5]} allegati" if riga[5] > 1 else "1 allegato")
                item_all.setData(Qt.ItemDataRole.UserRole, riga[5])
            self.tabella_mail.setItem(r, 5, item_all)
        self.tabella_mail.setSortingEnabled(True)
        self.tabella_mail.setUpdatesEnabled(True)
        n = len(rows)
        self.lbl_risultati.setText("1 mail" if n == 1 else f"{n} mail")
        annuncia(self.lbl_risultati, "1 mail in elenco" if n == 1 else f"{n} mail in elenco")

    def _ordine_elementi(self):
        return {"contatto": "titolo COLLATE NOCASE", "file": "titolo COLLATE NOCASE"}.get(self.sezione, "inizio DESC")

    def popola_elementi(self, rows):
        colonne = COLONNE_ELEMENTI.get(self.sezione, COLONNE_ELEMENTI["nota"])
        t = self.tabella_elementi
        t.setSortingEnabled(False)
        t.setUpdatesEnabled(False)
        t.setRowCount(0)
        t.setHorizontalHeaderLabels(["ID"] + [h for h, _c in colonne] + ["Cartella"])
        for i, (h, _c) in enumerate(colonne, 1):
            t.setColumnHidden(i, not h)
        t.setRowCount(len(rows))
        for r, riga in enumerate(rows):
            t.setItem(r, 0, QTableWidgetItem(str(riga[0])))
            for c, (_h, campo) in enumerate(colonne, 1):
                valore = str(riga[_CAMPI_RIGA[campo]] or "")
                item = QTableWidgetItem(valore.replace("\n", " · "))
                item.setToolTip(valore)
                if c == 1:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                t.setItem(r, c, item)
            cart = QTableWidgetItem(str(riga[7] or ""))
            cart.setToolTip(str(riga[7] or ""))
            t.setItem(r, 5, cart)
        if self.sezione in ("contatto", "file"):
            t.horizontalHeader().setSortIndicator(1, Qt.SortOrder.AscendingOrder)
        else:
            t.horizontalHeader().setSortIndicator(2, Qt.SortOrder.DescendingOrder)
        t.setSortingEnabled(True)
        t.setUpdatesEnabled(True)
        n = len(rows)
        nome = NOMI_TIPI_PIM.get(self.sezione, "").lower()
        self.lbl_risultati.setText(f"{n} elementi" if n != 1 else "1 elemento")
        annuncia(self.lbl_risultati, f"{nome}: {n} elementi in elenco")

    def _elemento_da_riga(self, r):
        item = self.tabella_elementi.item(r, 0) if r >= 0 else None
        if not item or not self.db:
            return None, None
        riga = self.db.conn.execute("SELECT dati, file_path FROM elementi WHERE id = ?", (item.text(),)).fetchone()
        if not riga:
            return None, None
        try:
            return json.loads(riga[0]), riga[1]
        except Exception:
            return None, None

    def mostra_elemento_da_tabella(self):
        righe = self.tabella_elementi.selectionModel().selectedRows() if self.tabella_elementi.selectionModel() else []
        if not righe:
            return
        e, rel = self._elemento_da_riga(righe[0].row())
        if e is None:
            return
        percorso = self.percorso_eml(rel) if rel else None
        self._elemento_corrente = (e, percorso)
        self.current_eml_path = None
        self.pannello_allegati_widget.setVisible(False)
        if e.get("mime") and percorso and os.path.exists(percorso):   # chat salvate come messaggio (Zimbra/Carbonio)
            try:
                with open(percorso, 'rb') as f:
                    msg = email.message_from_binary_file(f, policy=policy.default)
                self.preview_mail.setHtml(costruisci_html_mail(msg, e.get("inizio", "")))
            except Exception as ex:
                self.preview_mail.setHtml(html_avviso("Conversazione non leggibile", str(ex), "fumetto", C["error"]))
        else:
            self.preview_mail.setHtml(costruisci_html_elemento(e))
        self._anteprima_pronta = True
        self.btn_pdf.setEnabled(not self._stampa_in_corso)
        file_ok = e.get("tipo") == "file" and bool(percorso) and os.path.exists(percorso)
        self.btn_apri_file.setEnabled(file_ok)
        self.btn_salva_file.setEnabled(file_ok)

    def apri_file_elemento(self):
        if not self._elemento_corrente:
            return
        e, percorso = self._elemento_corrente
        if e.get("tipo") != "file" or not percorso or not os.path.exists(percorso):
            return
        nome = e.get("titolo") or os.path.basename(percorso)
        if estensione_effettiva(nome) in ESTENSIONI_PERICOLOSE:
            r = QMessageBox.warning(self, "File potenzialmente pericoloso",
                                    f"«{nome}» può eseguire programmi sul computer.\n\nLo apro comunque?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return
        copia = percorso_libero(cartella_temp_allegati(), nome_windows_sicuro(nome, 120, "file"))
        shutil.copy2(percorso, copia)
        if not apri_esterno(copia):
            QMessageBox.warning(self, "Impossibile aprire", f"Nessun programma per aprire «{nome}».")

    def salva_file_elemento(self):
        if not self._elemento_corrente:
            return
        e, percorso = self._elemento_corrente
        if not percorso or not os.path.exists(percorso):
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Salva una copia del file", e.get("titolo") or os.path.basename(percorso))
        if dest:
            try:
                shutil.copy2(percorso, dest)
            except OSError as ex:
                mostra_errore_con_copia(self, "Salvataggio non riuscito", str(ex))

    def _elementi_scelti(self):
        """Elementi spuntati; se nessuno è spuntato, tutti quelli in elenco (dopo conferma)."""
        t = self.tabella_elementi
        righe = [r for r in range(t.rowCount()) if t.item(r, 1) and t.item(r, 1).checkState() == Qt.CheckState.Checked]
        if not righe:
            if t.rowCount() == 0:
                QMessageBox.information(self, "Elenco vuoto", "Non c'è nulla da esportare.")
                return []
            r = QMessageBox.question(self, "Esportare tutto?", f"Nessun elemento spuntato.\n\nEsporto tutti i "
                                     f"{t.rowCount()} elementi in elenco?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return []
            righe = list(range(t.rowCount()))
        return [x for x in (self._elemento_da_riga(r) for r in righe) if x[0] is not None]

    def _esporta_secondo_sezione(self):
        if self.sezione == "posta":
            self.esporta_mail_massivo()
        else:
            self.esporta_elementi_scelti()

    def esporta_elementi_scelti(self):
        scelti = self._elementi_scelti()
        if not scelti:
            return
        tipo = self.sezione
        if tipo == "file":
            dest = QFileDialog.getExistingDirectory(self, "Dove copio i file?")
            if not dest:
                return
            copiati = 0
            for e, rel in scelti:
                p = self.percorso_eml(rel) if rel else None
                if p and os.path.exists(p):
                    shutil.copy2(p, percorso_libero(dest, nome_windows_sicuro(e.get("titolo") or os.path.basename(p), 120, "file")))
                    copiati += 1
            QMessageBox.information(self, "File copiati", f"Ho copiato {copiati} file in:\n{dest}")
            return
        filtri = {"contatto": "Rubrica vCard (*.vcf);;Foglio CSV (*.csv)",
                  "evento": "Calendario iCalendar (*.ics);;Foglio CSV (*.csv)",
                  "attivita": "Calendario iCalendar (*.ics);;Foglio CSV (*.csv)",
                  "nota": "Calendario iCalendar (*.ics);;Foglio CSV (*.csv)"}.get(tipo, "Foglio CSV (*.csv)")
        nome_base = {"contatto": "contatti.vcf", "evento": "calendario.ics", "attivita": "attivita.ics",
                     "nota": "note.ics"}.get(tipo, f"{tipo}.csv")
        dest, filtro = QFileDialog.getSaveFileName(self, f"Esporta {NOMI_TIPI_PIM.get(tipo, '').lower()}", nome_base, filtri)
        if not dest:
            return
        if not os.path.splitext(dest)[1]:
            dest += ".csv" if "csv" in filtro.lower() else os.path.splitext(nome_base)[1]
        try:
            esporta_elementi([e for e, _r in scelti], dest)
            QMessageBox.information(self, "Esportazione completata", f"{len(scelti)} elementi salvati in:\n{dest}")
        except Exception as ex:
            mostra_errore_con_copia(self, "Esportazione non riuscita", str(ex))

    def menu_contestuale_elementi(self, pos):
        menu = QMenu(self)
        ic = lambda n: icona(n, C["accento_chiaro"])
        a_esporta = menu.addAction(ic("esporta"), "Esporta (spuntati o tutti)…")
        a_file = menu.addAction(ic("apri"), "Apri il file") if self.sezione == "file" else None
        menu.addSeparator()
        a_tutte = menu.addAction(ic("spunta"), "Spunta tutti")
        a_nessuna = menu.addAction(ic("chiudi"), "Togli tutte le spunte")
        scelta = menu.exec(self.tabella_elementi.viewport().mapToGlobal(pos))
        if scelta == a_esporta:
            self.esporta_elementi_scelti()
        elif a_file is not None and scelta == a_file:
            self.apri_file_elemento()
        elif scelta == a_tutte:
            self.imposta_spunte_massivo(Qt.CheckState.Checked)
        elif scelta == a_nessuna:
            self.imposta_spunte_massivo(Qt.CheckState.Unchecked)

    def menu_contestuale_tabella(self, pos):
        # riga corrente: funziona sia col clic destro sia col tasto Menu / Maiusc+F10
        riga = self.tabella_mail.currentRow() if self.tabella_mail.currentRow() >= 0 else self.tabella_mail.rowAt(pos.y())
        menu = QMenu(self)
        ic = lambda n: icona(n, C["accento_chiaro"])
        a_apri = menu.addAction(ic("busta"), "Apri la mail in una nuova scheda")
        a_allegati = menu.addAction(ic("apri"), "Apri gli allegati di questa mail")
        a_apri.setEnabled(riga >= 0)
        a_allegati.setEnabled(riga >= 0)
        menu.addSeparator()
        a_esporta = menu.addAction(ic("esporta"), "Esporta PDF + allegati (mail spuntate)…")
        a_salva = menu.addAction(ic("scarica"), "Salva gli allegati (mail spuntate)…")
        menu.addSeparator()
        a_tutte = menu.addAction(ic("spunta"), "Spunta tutte")
        a_nessuna = menu.addAction(ic("chiudi"), "Togli tutte le spunte")
        menu.addSeparator()
        a_csv = menu.addAction(ic("tabella"), "Esporta l'elenco in CSV…")
        scelta = menu.exec(self.tabella_mail.viewport().mapToGlobal(pos))
        azioni = {a_apri: lambda: self.apri_mail_in_scheda(riga), a_allegati: lambda: self.apri_allegati_della_riga(riga),
                  a_esporta: self.esporta_mail_massivo, a_salva: self.estrai_allegati_massivi,
                  a_tutte: lambda: self.imposta_spunte_massivo(Qt.CheckState.Checked),
                  a_nessuna: lambda: self.imposta_spunte_massivo(Qt.CheckState.Unchecked), a_csv: self.esporta_elenco_csv}
        if scelta in azioni:
            azioni[scelta]()

    def imposta_spunte_massivo(self, stato):
        posta = getattr(self, "sezione", "posta") == "posta"
        tabella, col = (self.tabella_mail, 2) if posta else (self.tabella_elementi, 1)
        tabella.setSortingEnabled(False)       # altrimenti le righe si spostano mentre si spunta
        try:
            for i in range(tabella.rowCount()):
                item = tabella.item(i, col)
                if item:
                    item.setCheckState(stato)
        finally:
            tabella.setSortingEnabled(True)

    def _mail_spuntate(self):
        """[(email_id, percorso .eml, data)] delle righe spuntate."""
        elementi = []
        for i in range(self.tabella_mail.rowCount()):
            item_chk = self.tabella_mail.item(i, 2)
            if item_chk and item_chk.checkState() == Qt.CheckState.Checked:
                email_id = self.tabella_mail.item(i, 0).text()
                percorso = self._percorso_da_id(email_id)
                if percorso:
                    elementi.append((email_id, percorso, self.tabella_mail.item(i, 4).text()))
        if not elementi:
            QMessageBox.information(self, "Nessuna mail spuntata",
                                    "Spunta prima le mail che ti interessano: c'è una casella accanto al mittente.\n\n"
                                    "Per spuntarle tutte: menu «Altro» → «Spunta tutte».")
        return elementi

    # ---------- salvataggio degli allegati di più mail ----------
    def estrai_allegati_massivi(self):
        if not self.db:
            return
        if self.worker_estrazione_att is not None and self.worker_estrazione_att.isRunning():
            QMessageBox.information(self, "Salvataggio in corso", "Sto già salvando degli allegati: attendi che finisca.")
            if self.pannello_att is not None:
                self.pannello_att.mostra()
            return
        elementi = self._mail_spuntate()
        if not elementi:
            return
        dir_dest = QFileDialog.getExistingDirectory(self, "Dove salvo gli allegati?")
        if not dir_dest:
            return
        self.pannello_att = PannelloAvanzamento(self._finestra(), "Salvataggio degli allegati",
                                                f"Allegati di {len(elementi)} mail", self, "scarica")
        self.worker_estrazione_att = AttachmentExtractorWorker([(e[0], e[1]) for e in elementi], dir_dest)
        self.worker_estrazione_att.progress.connect(
            lambda a, t: self.pannello_att and self.pannello_att.aggiorna(a * 100 // max(1, t), f"Mail {a} di {t}"))
        self.worker_estrazione_att.finished.connect(self.estrazione_massiva_completata)
        self.pannello_att.annulla.connect(self.worker_estrazione_att.cancel)
        self.pannello_att.avvia()
        self.worker_estrazione_att.start()

    def estrazione_massiva_completata(self, estratti_totali):
        self.worker_estrazione_att.wait()
        annullata = self.worker_estrazione_att._is_cancelled
        if self.pannello_att is not None:
            self.pannello_att.chiudi()
            self.pannello_att = None
        if not annullata:
            QMessageBox.information(self, "Allegati salvati", f"Ho salvato {estratti_totali} allegati.\n\n"
                                    "Dei file .p7m trovi sia l'originale firmato sia il documento estratto.")

    # ---------- esportazione PDF + allegati ----------
    def esporta_mail_massivo(self):
        """Esporta le mail spuntate: una sottocartella per mail con PDF + allegati."""
        if not self.db or self._export_gia_in_corso():
            return
        elementi = self._mail_spuntate()
        if elementi:
            self._avvia_esportazione(elementi)

    def esporta_mail_corrente(self):
        """Esporta la mail aperta in anteprima (cartella con PDF, allegati, dettagli) senza doverla spuntare."""
        if not self.current_eml_path or self._export_gia_in_corso():
            return
        self._avvia_esportazione([(0, self.current_eml_path, self.current_data)])

    def _export_gia_in_corso(self):
        if not self._export_in_corso:
            return False
        QMessageBox.information(self, "Esportazione in corso",
                                "In questa scheda c'è già un'esportazione in corso: attendi che finisca o annullala.")
        if self.pannello_exp is not None:
            self.pannello_exp.mostra()
        return True

    def _avvia_esportazione(self, elementi):
        dir_dest = QFileDialog.getExistingDirectory(self, "Dove esporto le mail? (creo una cartella per ciascuna)")
        if not dir_dest:
            return
        self._export_in_corso = True
        n = len(elementi)
        self.pannello_exp = PannelloAvanzamento(self._finestra(), "Esportazione PDF + allegati",
                                                "Esportazione mail" if n == 1 else f"Esportazione {n} mail", self)
        self.esportatore = MassPdfExporter(elementi, dir_dest, self)
        self.esportatore.progress.connect(self.aggiorna_progress_exp)
        self.esportatore.stato.connect(lambda testo: self.pannello_exp and self.pannello_exp.aggiorna(99, testo))
        self.esportatore.finished.connect(self.esportazione_massiva_pdf_completata)
        self.pannello_exp.annulla.connect(self.esportatore.cancel)
        self.pannello_exp.avvia()
        self.esportatore.start()

    def aggiorna_progress_exp(self, attuale, totale, oggetto):
        if self.pannello_exp is None:
            return
        percentuale = attuale * 100 // max(1, totale)
        testo = oggetto if len(oggetto) <= 70 else oggetto[:67] + "..."
        self.pannello_exp.aggiorna(percentuale, f"Mail {attuale + 1} di {totale}\n{testo}")

    def esportazione_massiva_pdf_completata(self, report):
        self._export_in_corso = False
        dir_dest = self.esportatore.dir_dest if self.esportatore else ""
        if self.esportatore:
            self.esportatore.deleteLater()
            self.esportatore = None
        if self.pannello_exp is not None:
            self.pannello_exp.chiudi()
            self.pannello_exp = None
        testo = ("Esportazione annullata.\n\n" if report.get("annullato") else "Esportazione completata.\n\n")
        testo += (f"Mail esportate: {report['mail']}\n"
                  f"PDF creati: {report['pdf']}\n"
                  f"Allegati salvati: {report['allegati']}\n"
                  f"File .p7m: {report['p7m']} (originale conservato + documento estratto)\n")
        if report['p7m'] or report['firmati']:
            testo += (f"Firme verificate ({MOTORE_FIRME}): {report['firme_valide']} verificate, "
                      f"{report['firme_attenzione']} con avvisi, {report['firme_non_valide']} non valide, "
                      f"{report['firme_non_verificate']} non verificate\n")
        if report['postacert']:
            testo += f"Buste PEC (postacert.eml) scompattate: {report['postacert']}\n"
        testo += f"\nCartella: {dir_dest}"
        errori = report.get("errori", [])
        if errori:
            testo += f"\n\nProblemi riscontrati ({len(errori)}):\n" + "\n".join(errori[:30])
            if len(errori) > 30:
                testo += f"\n... e altri {len(errori) - 30}"
            mostra_errore_con_copia(self, "Esportazione terminata con problemi", testo)
        else:
            box = QMessageBox(QMessageBox.Icon.Information, "Esportazione PDF + allegati", testo, parent=self)
            apri = box.addButton("Apri la cartella", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if box.clickedButton() == apri and dir_dest:
                apri_esterno(dir_dest)

    # ---------- anteprima ----------
    def mostra_anteprima_mail_da_tabella(self):
        if not self.db:
            return
        righe = self.tabella_mail.selectedItems()
        if not righe:
            return
        r = righe[0].row()
        email_id = self.tabella_mail.item(r, 0).text()
        percorso = self._percorso_da_id(email_id)
        if percorso:
            self.renderizza_eml(percorso, self.tabella_mail.item(r, 4).text(), self._allegati_da_id(email_id))

    def carica_singolo_eml(self, percorso_file):
        try:
            with open(percorso_file, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
            self.renderizza_eml(percorso_file, data_da_msg(msg), [nome for nome, _part in allegati_da_msg(msg)])
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nella lettura della mail", f"Impossibile leggere il file:\n{e}")

    def renderizza_eml(self, file_path, data_formattata, allegati):
        self.current_eml_path = file_path
        self.current_data = data_formattata
        for i in reversed(range(self.layout_checkbox.count())):
            widget = self.layout_checkbox.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.checkbox_allegati.clear()
        self.pannello_allegati_widget.setVisible(bool(allegati))
        self.lbl_allegati.setText(f"ALLEGATI ({len(allegati)})")
        for nome_all in allegati:
            riga = QWidget()
            lr = QHBoxLayout(riga)
            lr.setContentsMargins(0, 0, 0, 0)
            lr.setSpacing(4)
            chk = QCheckBox(nome_all)
            chk.setToolTip(nome_all)
            chk.setAccessibleDescription("Spunta per aprire o salvare questo allegato")
            lr.addWidget(chk, 1)
            if supportato(nome_all):
                b_ver = pulsante("", "scudo", "piccolo fantasma", "Verifica la firma digitale (scheda Verifica firme)", C["ok"])
                b_ver.setAccessibleName(f"Verifica la firma di {nome_all}")
                b_ver.clicked.connect(lambda checked=False, n=nome_all: self.verifica_allegato(n))
                lr.addWidget(b_ver)
            b_apri = pulsante("", "apri", "piccolo fantasma", "Apri subito questo allegato senza salvarlo")
            b_apri.setAccessibleName(f"Apri {nome_all}")
            b_apri.clicked.connect(lambda checked=False, n=nome_all: self.apri_allegati([n]))
            lr.addWidget(b_apri)
            self.layout_checkbox.addWidget(riga)
            self.checkbox_allegati.append(chk)

        if not os.path.exists(file_path):
            self.preview_mail.setHtml(html_avviso("File della mail non trovato",
                                                  "Il file .eml non c'è più sul disco. Se hai spostato o cancellato dei file, "
                                                  "ricostruisci l'indice dal menu «Altro».", "documento", C["warn"]))
            self.btn_pdf.setEnabled(False)
            self.btn_esporta_mail.setEnabled(False)
            return
        try:
            with open(file_path, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
            pagina = costruisci_html_mail(msg, data_formattata)
        except Exception as e:
            self.preview_mail.setHtml(html_avviso("Mail non leggibile", f"{type(e).__name__}: {e}", "documento", C["error"]))
            self.btn_pdf.setEnabled(False)
            self.btn_esporta_mail.setEnabled(False)
            return
        if len(pagina.encode('utf-8')) > 500000:
            # setHtml() non mostra pagine oltre ~2 MB (codifica URL): le mail grandi passano da un file temporaneo
            tmp = os.path.join(cartella_temp_allegati(), f"anteprima_{id(self)}.html")
            with open(tmp, "w", encoding="utf-8-sig", errors="replace") as f:
                f.write(pagina)
            self.preview_mail.load(QUrl.fromLocalFile(tmp))
        else:
            self.preview_mail.setHtml(pagina)
        self.btn_pdf.setEnabled(not self._stampa_in_corso)
        self.btn_esporta_mail.setEnabled(True)
        self._anteprima_pronta = True

    def salva_pdf(self):
        if not self.current_eml_path and not self._anteprima_pronta:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salva in PDF", "", "PDF (*.pdf)")
        if path:
            self._stampa_in_corso = True
            self.btn_pdf.setText("Attendere…")
            self.btn_pdf.setEnabled(False)
            self.preview_mail.page().printToPdf(path)

    def pdf_completato(self, path, success):
        self._stampa_in_corso = False
        self.btn_pdf.setText("Stampa come PDF")
        self.btn_pdf.setEnabled(True)
        if success:
            QMessageBox.information(self, "PDF creato", f"PDF salvato in:\n{path}")
        else:
            mostra_errore_con_copia(self, "Errore PDF", "Impossibile generare il file PDF dal motore Chromium.")

    def seleziona_tutti_allegati(self):
        for chk in self.checkbox_allegati:
            chk.setChecked(True)

    def deseleziona_tutti_allegati(self):
        for chk in self.checkbox_allegati:
            chk.setChecked(False)

    def _parti_allegati(self, nomi, eml_path=None):
        """[(nome, byte)] degli allegati richiesti della mail."""
        eml_path = eml_path or self.current_eml_path
        if not eml_path or not os.path.exists(eml_path):
            raise FileNotFoundError("il file della mail non è stato trovato sul disco")
        with open(eml_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        out = []
        for nome, part in allegati_da_msg(msg):
            if nome in nomi:
                dati = payload_allegato(part)
                if dati:
                    out.append((nome, dati))
        return out

    # ---------- apertura diretta (file temporanei ripuliti all'uscita) ----------
    def apri_allegati_selezionati(self):
        nomi = [chk.text() for chk in self.checkbox_allegati if chk.isChecked()]
        if not nomi:
            QMessageBox.information(self, "Nessun allegato spuntato",
                                    "Spunta almeno un allegato, oppure usa l'icona di apertura accanto al suo nome.")
            return
        self.apri_allegati(nomi)

    def apri_allegati(self, nomi, eml_path=None):
        pericolosi = [n for n in nomi if estensione_effettiva(n) in ESTENSIONI_PERICOLOSE]
        if pericolosi:
            risposta = QMessageBox.warning(
                self, "Allegato potenzialmente pericoloso",
                "Questi allegati possono eseguire codice sul tuo computer:\n\n" + "\n".join(pericolosi) +
                "\n\nVuoi aprirli comunque?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if risposta != QMessageBox.StandardButton.Yes:
                return
        try:
            cartella_dest = tempfile.mkdtemp(prefix="allegati_", dir=cartella_temp_allegati())
            non_aperti, aperti = [], 0
            for nome, dati in self._parti_allegati(nomi, eml_path):
                nome, dati, _estratto = risolvi_p7m(nome, dati)
                path_out = percorso_libero(cartella_dest, nome_windows_sicuro(nome, 150, "allegato"))
                with open(path_out, 'wb') as f_out:
                    f_out.write(dati)
                if apri_esterno(path_out):
                    aperti += 1
                else:
                    non_aperti.append(nome)
            if non_aperti:
                mostra_errore_con_copia(self, "Impossibile aprire", "Nessuna applicazione associata a:\n" + "\n".join(non_aperti))
            elif aperti == 0:
                QMessageBox.warning(self, "Allegato vuoto", "Nessun contenuto trovato per gli allegati richiesti.")
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nell'apertura dell'allegato", str(e))

    def verifica_allegato(self, nome):
        """Manda l'allegato firmato alla scheda Verifica firme (stesso motore del P7MReader)."""
        try:
            parti = self._parti_allegati([nome])
        except Exception as e:
            mostra_errore_con_copia(self, "Errore", str(e))
            return
        if parti and self.parent_app:
            oggetto = ""
            try:
                with open(self.current_eml_path, 'rb') as f:
                    oggetto = str(email.message_from_binary_file(f, policy=policy.default).get('Subject', '') or '')
            except Exception:
                pass
            self.parent_app.verifica_dati(parti[0][0], parti[0][1], f"allegato della mail «{oggetto or 'senza oggetto'}»")

    # ---------- azioni sulle righe ----------
    def percorso_eml_da_riga(self, row):
        if not self.db or row < 0:
            return None
        item = self.tabella_mail.item(row, 0)
        return self._percorso_da_id(item.text()) if item else None

    def apri_mail_in_scheda(self, row, column=0):
        percorso = self.percorso_eml_da_riga(row)
        if not percorso or not os.path.exists(percorso):
            QMessageBox.warning(self, "Mail non trovata", "Il file della mail non è stato trovato sul disco.\n"
                                "Prova a ricostruire l'indice dal menu «Altro».")
            return
        if self.parent_app:
            self.parent_app.carica_eml_in_tab(percorso)

    def apri_allegati_della_riga(self, row):
        percorso = self.percorso_eml_da_riga(row)
        if not percorso:
            return
        nomi = self._allegati_da_id(self.tabella_mail.item(row, 0).text())
        if not nomi:
            QMessageBox.information(self, "Nessun allegato", "Questa mail non ha allegati.")
            return
        self.apri_allegati(nomi, eml_path=percorso)

    def esporta_elenco_csv(self):
        if self.tabella_mail.rowCount() == 0:
            QMessageBox.information(self, "Elenco vuoto", "Non c'è nulla da esportare.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Esporta l'elenco in CSV", "elenco_mail.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                scrittore = csv.writer(f, delimiter=';')
                scrittore.writerow(["Cartella", "Mittente", "Oggetto", "Data", "Allegati"])
                for i in range(self.tabella_mail.rowCount()):
                    testo = lambda col: self.tabella_mail.item(i, col).text() if self.tabella_mail.item(i, col) else ""
                    n_all = self.tabella_mail.item(i, 5).data(Qt.ItemDataRole.UserRole) if self.tabella_mail.item(i, 5) else None
                    scrittore.writerow([testo(1), testo(2), testo(3), testo(4), n_all or 0])
            QMessageBox.information(self, "Elenco esportato", f"Elenco salvato in:\n{path}")
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nell'esportazione CSV", str(e))

    def salva_allegati_selezionati(self):
        nomi = [chk.text() for chk in self.checkbox_allegati if chk.isChecked()]
        if not self.current_eml_path or not nomi:
            QMessageBox.information(self, "Nessun allegato spuntato", "Spunta almeno un allegato da salvare.")
            return
        dir_dest = QFileDialog.getExistingDirectory(self, "Dove salvo gli allegati?")
        if not dir_dest:
            return
        try:
            salvati = p7m = 0
            for nome, dati in self._parti_allegati(nomi):
                _path, estratto = salva_allegato_con_p7m(dir_dest, nome, dati)
                salvati += 1
                p7m += estratto
            testo = f"{salvati} allegati salvati."
            if p7m:
                testo += f"\n\nDei {p7m} file .p7m ho salvato sia l'originale firmato sia il documento estratto."
            QMessageBox.information(self, "Allegati salvati", testo)
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nel salvataggio", str(e))

# ==========================================
# SCHEDA "VERIFICA FIRME" (il P7MReader dentro lo ZimbraViewer)
# ==========================================
class ScansioneWorker(QThread):
    """Cerca i file firmati (.p7m, .p7s, .pdf, .xml) nelle cartelle, senza bloccare l'interfaccia."""
    trovati = pyqtSignal(list)

    def __init__(self, percorsi):
        super().__init__()
        self.percorsi = percorsi
        self.annullato = False

    def run(self):
        out = []
        for p in self.percorsi:
            if os.path.isdir(p):
                for radice, _dirs, files in os.walk(p):
                    if self.annullato:
                        break
                    out += [os.path.join(radice, f) for f in sorted(files) if supportato(f)]
            elif os.path.isfile(p) and supportato(os.path.basename(p)):
                out.append(p)
        self.trovati.emit(out)

def html_risultato(r):
    """Scheda di dettaglio di un documento verificato (stesse informazioni del report del P7MReader)."""
    e = html.escape
    colore = COLORE_ESITO.get(r.stato, C["none"])
    chip = lambda testo, col: (f"<span style='background:{col};color:{C['su_accento']};border-radius:6px;"
                               f"padding:2px 8px;font-weight:700;font-size:12px'>&nbsp;{e(testo)}&nbsp;</span>")
    riga = lambda k, v: (f"<tr><td style='color:{C['tenue']};padding:3px 14px 3px 0;vertical-align:top;white-space:nowrap'>{e(k)}</td>"
                         f"<td style='padding:3px 0'>{v}</td></tr>") if v else ""
    out = [f"<div style=\"font-family:{FONT_HTML};font-size:13px;color:{C['testo']}\">",
           f"<div style='margin-bottom:6px'>{chip(etichetta_esito(r), colore)}</div>",
           f"<div style='font-size:17px;font-weight:700;margin:6px 0 2px'>{e(r.nome)}</div>",
           f"<div style='color:{C['attenuato']};margin-bottom:10px'>{e(r.esito)}</div><table>",
           riga("Formato", e(r.formato)), riga("Dimensione", e(fmt_size(r.dimensione))),
           riga("Origine", e(r.origine or r.percorso)), riga("SHA-256", f"<span style=\"font-family:{FONT_MONO};font-size:11px\">{e(r.sha256)}</span>")]
    if r.nome_contenuto and r.formato == 'CAdES':
        out.append(riga("Documento contenuto", e(f"{r.nome_contenuto} ({r.tipo_contenuto})")))
    if r.livelli:
        out.append(riga("Buste annidate", str(r.livelli + 1)))
    out += [riga("Nota", e(n)) for n in r.note]
    out.append("</table>")
    if r.fattura:
        out.append(f"<div style='margin:14px 0 4px;color:{C['tenue']};font-weight:700;font-size:11px'>FATTURA ELETTRONICA</div>"
                   f"<table style='background:{C['rilievo']};border-radius:8px;padding:6px'>")
        out += [riga(k, e(v)) for k, v in r.fattura.items()]
        out.append("</table>")
    for i, f in enumerate(r.firme, 1):
        col = COLORE_ESITO.get(f.stato, C["none"])
        out.append(f"<div style='margin:16px 0 6px;border-left:3px solid {col};padding-left:10px'>"
                   f"<b>{e(f.tipo)} {i}</b>&nbsp; {chip(etichetta_firma(f), col)}"
                   f"<div style='color:{C['attenuato']};margin-top:4px'>{e(f.esito)}</div></div>")
        if f.controlli:
            simboli = {"ok": "✓", "warn": "!", "error": "✕", "none": "–"}
            out.append(f"<div style='margin:8px 0 3px;color:{C['tenue']};font-weight:700;font-size:11px'>CONTROLLI ESEGUITI</div><table>")
            out += [f"<tr><td style='color:{COLORE_ESITO.get(c.stato, C['none'])};font-weight:700;padding:1px 8px 3px 0;vertical-align:top'>{simboli[c.stato]}</td>"
                    f"<td style='padding:1px 0 3px 0'><b>{e(c.nome)}</b> <span style='color:{C['attenuato']}'>{e(c.dettaglio)}</span></td></tr>" for c in f.controlli]
            out.append("</table><div style='height:8px'></div>")
        out.append("<table>")
        out += [riga("Firmatario", f"<b>{e(f.firmatario)}</b>"), riga("Identificativo", e(f.identificativo)),
                riga("Organizzazione", e(f.organizzazione)),
                riga("Data e ora firma", e(fmt_dt(f.data_firma)) + (f" <span style='color:{C['tenue']}'>[{e(f.fonte_data)}]</span>" if f.fonte_data else "")),
                riga("Data /M del PDF", e(fmt_dt(f.data_pdf_m)) if f.data_pdf_m else ""),
                riga("Marca temporale", e(fmt_dt(f.marca_temporale)) if f.marca_temporale else ""),
                riga("TSA", e(f.marca_tsa)),
                riga("Emittente", e(f.emittente)),
                riga("Certificato valido", e(f"dal {fmt_data(f.valido_dal)} al {fmt_data(f.valido_al)}")),
                riga("Motivo", e(f.motivo)), riga("Luogo", e(f.luogo))]
        out += [riga("Nota", e(n)) for n in f.note]
        out.append("</table>")
    out.append(f"<p style='color:{C['tenue']};font-size:11px;margin-top:18px'>{e(nota_verifica())}</p></div>")
    return "".join(out)

class FirmeTab(QWidget):
    """Verifica ed estrazione di documenti firmati: file dal disco, cartelle intere, allegati delle mail."""
    FILTRI = [("Tutti", None), ("Verificati", "ok"), ("Attenzione", "warn"), ("Non validi", "error"), ("Senza firma / non verificati", "none")]

    def __init__(self, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.risultati = []                   # RisultatoDoc nell'ordine di arrivo
        self._dati_allegati = {}              # id(RisultatoDoc) -> byte (per gli allegati delle mail, che non sono su disco)
        self._in_corso = []                   # futures
        self._totale_lotto = 0
        self._scansione = None
        self._in_attesa = []                  # percorsi arrivati mentre una ricerca nelle cartelle è in corso
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._raccogli)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)
        testa = QHBoxLayout()
        ico = QLabel()
        ico.setPixmap(icona("scudo", C["ok"], 26).pixmap(30, 30))
        titoli = QVBoxLayout()
        titoli.setSpacing(0)
        t = QLabel("Verifica firme digitali")
        t.setObjectName("titoloMedio")
        st = QLabel(f"CAdES (.p7m, .p7s), PAdES (.pdf), XAdES (.xml) e fatture elettroniche · {MOTORE_FIRME} · "
                    f"revoca OCSP/CRL {'attiva' if IMP['revoca'] else 'disattivata'}")
        st.setObjectName("attenuato")
        titoli.addWidget(t)
        titoli.addWidget(st)
        testa.addWidget(ico)
        testa.addSpacing(6)
        testa.addLayout(titoli, 1)
        b_file = pulsante("Apri file…", "documento", "primario")
        b_file.clicked.connect(self.scegli_file)
        b_cartella = pulsante("Apri cartella…", "cartella", suggerimento="Verifica tutti i .p7m, .pdf e .xml della cartella e delle sottocartelle")
        b_cartella.clicked.connect(self.scegli_cartella)
        self.b_estrai = pulsante("Estrai documenti", "scarica", suggerimento="Estrae il contenuto dei .p7m (selezionati, o tutti se non ne selezioni)")
        self.b_estrai.clicked.connect(self.estrai_documenti)
        self.b_report = pulsante("Report", "tabella")
        menu = QMenu(self)
        menu.addAction(icona("tabella", C["accento_chiaro"]), "Esporta report CSV…", lambda: self._salva_report("csv"))
        menu.addAction(icona("documento", C["accento_chiaro"]), "Esporta report HTML…", lambda: self._salva_report("html"))
        self.b_report.setMenu(menu)
        self.b_svuota = pulsante("Svuota", "cestino", "pericolo")
        self.b_svuota.clicked.connect(self.svuota)
        for b in (b_file, b_cartella, self.b_estrai, self.b_report, self.b_svuota):
            testa.addWidget(b)
        lay.addLayout(testa)

        filtri = QHBoxLayout()
        self.cmb_filtro = QComboBox()
        for etichetta, _k in self.FILTRI:
            self.cmb_filtro.addItem(etichetta)
        self.cmb_filtro.currentIndexChanged.connect(self.ricostruisci)
        self.cmb_filtro.setAccessibleName("Mostra i documenti con esito")
        self.txt_cerca = QLineEdit()
        self.txt_cerca.addAction(icona("cerca", C["tenue"]), QLineEdit.ActionPosition.LeadingPosition)
        self.txt_cerca.setPlaceholderText("Filtra per nome del file o firmatario…")
        self.txt_cerca.setClearButtonEnabled(True)
        self.txt_cerca.setAcceptDrops(False)
        self.txt_cerca.textChanged.connect(self.ricostruisci)
        self.txt_cerca.setAccessibleName("Filtra per nome del file o firmatario")
        self.lbl_conteggi = QLabel("")
        self.lbl_conteggi.setObjectName("lblRisultati")
        self.barra = QProgressBar()
        self.barra.setFixedWidth(220)
        self.barra.setFormat("%p%")
        self.barra.setAccessibleName("Avanzamento della verifica")
        self.barra.hide()
        filtri.addWidget(self.cmb_filtro)
        filtri.addWidget(self.txt_cerca, 1)
        filtri.addWidget(self.lbl_conteggi)
        filtri.addWidget(self.barra)
        lay.addLayout(filtri)

        self.pila = QStackedWidget()
        self.zona = ZonaRilascio("Trascina qui i documenti firmati",
                                 "File .p7m, PDF o XML firmati (anche fatture elettroniche), oppure una cartella intera. "
                                 "Dalle mail: icona a forma di scudo accanto all'allegato.", "Scegli i file…", "Scegli una cartella…")
        self.zona.scegli_file.connect(self.scegli_file)
        self.zona.scegli_cartella.connect(self.scegli_cartella)
        self.pila.addWidget(self.zona)
        divisore = QSplitter(Qt.Orientation.Horizontal)
        self.tabella = QTableWidget(0, 5)
        self.tabella.setHorizontalHeaderLabels(["Esito", "Documento", "Formato", "Firmatari", "Data firma"])
        h = self.tabella.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col, larg in ((0, 130), (2, 80), (3, 220), (4, 150)):
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.tabella.setColumnWidth(col, larg)
        h.setHighlightSections(False)
        self.tabella.verticalHeader().setVisible(False)
        self.tabella.verticalHeader().setDefaultSectionSize(34)
        self.tabella.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella.setShowGrid(False)
        self.tabella.setAlternatingRowColors(True)
        self.tabella.itemSelectionChanged.connect(self._mostra_dettaglio)
        self.tabella.cellDoubleClicked.connect(lambda *_: self.apri_documento())
        self.tabella.setAccessibleName("Documenti verificati")
        self.tabella.setAccessibleDescription("Invio apre il documento; il dettaglio della verifica è nel pannello a destra")
        tasti_tabella(self.tabella, None, self.apri_documento)
        divisore.addWidget(self.tabella)
        destra = QFrame()
        destra.setObjectName("pannello")
        dl = QVBoxLayout(destra)
        dl.setContentsMargins(12, 12, 12, 12)
        self.dettaglio = QTextBrowser()
        self.dettaglio.setOpenLinks(False)
        self.dettaglio.setAccessibleName("Dettaglio della verifica")
        self.dettaglio.setFrameShape(QFrame.Shape.NoFrame)
        self.dettaglio.setStyleSheet(f"QTextBrowser{{background:{C['superficie']};border:none}}")
        azioni = QHBoxLayout()
        self.b_apri_doc = pulsante("Apri documento", "apri", "primario piccolo")
        self.b_apri_doc.clicked.connect(self.apri_documento)
        self.b_estrai_uno = pulsante("Estrai…", "scarica", "piccolo")
        self.b_estrai_uno.clicked.connect(lambda: self.estrai_documenti(solo_selezionato=True))
        self.b_cartella_doc = pulsante("Mostra nella cartella", "cartella", "piccolo")
        self.b_cartella_doc.clicked.connect(self.mostra_in_cartella)
        self.b_cert = pulsante("Certificato", "certificato", "piccolo")
        self.b_cert.clicked.connect(self.mostra_certificato)
        self.b_copia = pulsante("Copia report", "copia", "piccolo")
        self.b_copia.clicked.connect(self.copia_report)
        for b in (self.b_apri_doc, self.b_estrai_uno, self.b_cartella_doc, self.b_cert, self.b_copia):
            azioni.addWidget(b)
        azioni.addStretch()
        dl.addWidget(self.dettaglio, 1)
        dl.addLayout(azioni)
        divisore.addWidget(destra)
        divisore.setSizes([640, 520])
        self.pila.addWidget(divisore)
        lay.addWidget(self.pila, 1)
        self._aggiorna_stato_ui()

    # ---------- ingresso dei documenti ----------
    def scegli_file(self):
        percorsi, _ = QFileDialog.getOpenFileNames(self, "Scegli i documenti firmati", "",
                                                   "Documenti firmati (*.p7m *.p7s *.pdf *.xml *.p7m*);;Tutti i file (*)")
        if percorsi:
            self.aggiungi_percorsi(percorsi)

    def scegli_cartella(self):
        cartella = QFileDialog.getExistingDirectory(self, "Scegli la cartella con i documenti firmati")
        if cartella:
            self.aggiungi_percorsi([cartella])

    def aggiungi_percorsi(self, percorsi):
        if self._scansione is not None and self._scansione.isRunning():
            self._in_attesa += list(percorsi)   # si verificano appena finisce la ricerca in corso
            return
        self.barra.show()
        self.barra.setRange(0, 0)               # "occupato" mentre cerco i file
        self._scansione = ScansioneWorker(list(percorsi))
        self._scansione.trovati.connect(self._verifica_file)
        self._scansione.finished.connect(self._scansione_finita)
        self._scansione.start()

    def _scansione_finita(self):
        self._aggiorna_stato_ui()
        if self._in_attesa:
            attesa, self._in_attesa = self._in_attesa, []
            self.aggiungi_percorsi(attesa)

    def _verifica_file(self, files):
        self.barra.setRange(0, 100)
        gia = {os.path.normcase(os.path.abspath(r.percorso)) for r in self.risultati if not r.origine}
        nuovi = [f for f in files if os.path.normcase(os.path.abspath(f)) not in gia]
        if not nuovi:
            self._aggiorna_stato_ui()
            if not files:
                QMessageBox.information(self, "Nessun documento", "Non ho trovato file .p7m, .p7s, .pdf o .xml da verificare.")
            return
        for f in nuovi:
            self._in_corso.append(VerificaFirme.avvia(os.path.basename(f), None, f))
        self._totale_lotto += len(nuovi)
        self._timer.start()
        self._aggiorna_stato_ui()

    def verifica_dati(self, nome, dati, origine):
        """Documento che non è su disco (allegato di una mail)."""
        futuro = VerificaFirme.avvia(nome, dati, "", origine)
        futuro.dati = bytes(dati)
        self._in_corso.append(futuro)
        self._totale_lotto += 1
        self._timer.start()
        self._aggiorna_stato_ui()

    def _raccogli(self):
        pronti = [f for f in self._in_corso if f.done()]
        for f in pronti:
            self._in_corso.remove(f)
            r = f.result()
            self.risultati.append(r)
            if getattr(f, "dati", None) is not None:
                self._dati_allegati[id(r)] = f.dati
        if pronti:
            self.ricostruisci()
            if len(self.risultati) == len(pronti) or any(r.origine for r in (f.result() for f in pronti)):
                self.tabella.selectRow(self.tabella.rowCount() - 1)
        if not self._in_corso:
            self._timer.stop()
            self._totale_lotto = 0
        self._aggiorna_stato_ui()

    def _aggiorna_stato_ui(self):
        attivi = len(self._in_corso)
        if attivi or (self._scansione is not None and self._scansione.isRunning()):
            self.barra.show()
            if self._totale_lotto:
                self.barra.setValue((self._totale_lotto - attivi) * 100 // self._totale_lotto)
                self.barra.setToolTip(f"Verifica in corso: {self._totale_lotto - attivi} di {self._totale_lotto}")
        else:
            self.barra.hide()
        self.pila.setCurrentIndex(1 if (self.risultati or attivi) else 0)
        conta = {k: sum(1 for r in self.risultati if r.stato == k) for k in ("ok", "warn", "error", "none")}
        testo_conteggi = (f"{len(self.risultati)} documenti · {conta['ok']} verificati · "
                          f"{conta['warn']} attenzione · {conta['error']} non validi" if self.risultati else "")
        if testo_conteggi != self.lbl_conteggi.text():
            self.lbl_conteggi.setText(testo_conteggi)
            if testo_conteggi:
                annuncia(self.lbl_conteggi, testo_conteggi)
        sel = self._selezionato()
        for b in (self.b_apri_doc, self.b_copia):
            b.setEnabled(sel is not None)
        self.b_estrai_uno.setEnabled(sel is not None and sel.formato == "CAdES" and not sel.errore)
        self.b_cartella_doc.setEnabled(sel is not None and not sel.origine)
        self.b_cert.setEnabled(sel is not None and any(f.cert_der for f in sel.firme))
        self.b_estrai.setEnabled(any(r.formato == "CAdES" for r in self.risultati))
        self.b_report.setEnabled(bool(self.risultati))
        self.b_svuota.setEnabled(bool(self.risultati))

    # ---------- elenco ----------
    def _visibili(self):
        stato = self.FILTRI[self.cmb_filtro.currentIndex()][1]
        testo = self.txt_cerca.text().strip().lower()
        out = []
        for r in self.risultati:
            if stato and r.stato != stato:
                continue
            if testo and testo not in (r.nome + " " + " ".join(f.firmatario for f in r.firme)).lower():
                continue
            out.append(r)
        return out

    def ricostruisci(self):
        sel = self._selezionato()
        self._righe = self._visibili()
        self.tabella.blockSignals(True)         # la selezione si ricalcola qui sotto: niente dettagli di righe sbagliate
        self.tabella.clearSelection()
        self.tabella.setRowCount(len(self._righe))
        for i, r in enumerate(self._righe):
            col = COLORE_ESITO.get(r.stato, C["none"])
            esito = QTableWidgetItem("  " + etichetta_esito(r))
            pix = QPixmap(12, 12)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor(col))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(1, 1, 10, 10)
            p.end()
            esito.setIcon(QIcon(pix))
            esito.setForeground(QColor(col))
            esito.setToolTip(r.esito)
            self.tabella.setItem(i, 0, esito)
            nome = QTableWidgetItem(r.nome)
            nome.setToolTip(r.origine or r.percorso)
            self.tabella.setItem(i, 1, nome)
            self.tabella.setItem(i, 2, QTableWidgetItem(r.formato))
            firmatari = ", ".join(dict.fromkeys(f.firmatario for f in r.firme if f.tipo != "Controfirma")) or "—"
            self.tabella.setItem(i, 3, QTableWidgetItem(firmatari))
            date = [f.data_firma for f in r.firme if f.data_firma]
            self.tabella.setItem(i, 4, QTableWidgetItem(fmt_dt(min(date)) if date else "—"))
            if r is sel:
                self.tabella.selectRow(i)
        self.tabella.blockSignals(False)
        self._mostra_dettaglio()

    def _selezionato(self):
        righe = self.tabella.selectionModel().selectedRows() if self.tabella.selectionModel() else []
        if not righe or not hasattr(self, "_righe"):
            return None
        i = righe[0].row()
        return self._righe[i] if 0 <= i < len(self._righe) else None

    def _mostra_dettaglio(self):
        r = self._selezionato()
        self.dettaglio.setHtml(html_risultato(r) if r else "")
        self._aggiorna_stato_ui()

    def svuota(self):
        self.risultati.clear()
        self._dati_allegati.clear()
        self.ricostruisci()
        self.dettaglio.clear()

    # ---------- azioni ----------
    def _dati(self, r):
        if id(r) in self._dati_allegati:
            return self._dati_allegati[id(r)]
        with open(r.percorso, 'rb') as f:
            return f.read()

    def apri_documento(self):
        r = self._selezionato()
        if r is None:
            return
        try:
            if r.formato == "CAdES" and not r.errore:
                nome, dati, _e = risolvi_p7m(r.nome, self._dati(r))
                path = percorso_libero(tempfile.mkdtemp(prefix="firme_", dir=cartella_temp_allegati()),
                                       nome_windows_sicuro(nome, 150, "documento"))
                with open(path, 'wb') as f:
                    f.write(dati)
            elif r.origine:
                path = percorso_libero(tempfile.mkdtemp(prefix="firme_", dir=cartella_temp_allegati()),
                                       nome_windows_sicuro(r.nome, 150, "documento"))
                with open(path, 'wb') as f:
                    f.write(self._dati(r))
            else:
                path = r.percorso
            if estensione_effettiva(path) in ESTENSIONI_PERICOLOSE:
                if QMessageBox.warning(self, "Contenuto potenzialmente pericoloso",
                                       "Il documento contenuto può eseguire codice sul tuo computer. Lo apro comunque?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                    return
            if not apri_esterno(path):
                mostra_errore_con_copia(self, "Impossibile aprire", f"Nessuna applicazione associata a:\n{path}")
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nell'apertura", str(e))

    def estrai_documenti(self, solo_selezionato=False):
        sel = self._selezionato()
        elenco = [sel] if solo_selezionato and sel else [r for r in self._visibili() if r.formato == "CAdES" and not r.errore]
        elenco = [r for r in elenco if r is not None and r.formato == "CAdES"]
        if not elenco:
            QMessageBox.information(self, "Niente da estrarre", "Non ci sono file .p7m da estrarre.")
            return
        dest_unica = None
        if any(r.origine for r in elenco) or solo_selezionato:
            dest_unica = QFileDialog.getExistingDirectory(self, "Dove salvo i documenti estratti?",
                                                          "" if (sel is None or sel.origine) else os.path.dirname(sel.percorso))
            if not dest_unica:
                return
        fatti, gia_presenti, errori, ultimo = 0, 0, [], ""
        for r in elenco:
            try:
                nome, dati, estratto = risolvi_p7m(r.nome, self._dati(r))
                if not estratto:
                    raise ValueError("contenuto assente (firma detached) o busta non leggibile")
                cartella = dest_unica or os.path.dirname(r.percorso)     # come il P7MReader: accanto all'originale
                nome = nome_windows_sicuro(nome, 150, "documento")
                esistente = os.path.join(cartella, nome)
                if (os.path.isfile(esistente) and os.path.getsize(esistente) == len(dati)
                        and sha256_file(esistente) == hashlib.sha256(dati).hexdigest()):
                    ultimo, gia_presenti = esistente, gia_presenti + 1      # stesso nome pulito e stesso contenuto: non si duplica
                    continue
                ultimo = percorso_libero(cartella, nome)
                with open(ultimo, 'wb') as f:
                    f.write(dati)
                fatti += 1
            except Exception as e:
                errori.append(f"{r.nome}: {e}")
        testo = (f"Documenti estratti: {fatti}" + (f", già presenti: {gia_presenti}" if gia_presenti else "") +
                 (" (accanto agli originali)" if not dest_unica else f"\nCartella: {dest_unica}"))
        if errori:
            mostra_errore_con_copia(self, "Estrazione terminata con problemi", testo + "\n\n" + "\n".join(errori[:30]))
        else:
            box = QMessageBox(QMessageBox.Icon.Information, "Estrazione completata", testo, parent=self)
            apri = box.addButton("Apri la cartella", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if box.clickedButton() == apri and ultimo:
                apri_esterno(os.path.dirname(ultimo))

    def mostra_in_cartella(self):
        r = self._selezionato()
        if r is None or r.origine:
            return
        mostra_nel_file_manager(r.percorso)

    def mostra_certificato(self):
        r = self._selezionato()
        if r is None:
            return
        blocchi = []
        for i, f in enumerate(r.firme, 1):
            if f.cert_der:
                try:
                    blocchi.append(f"=== {f.tipo} {i}: {f.firmatario} ===\n{descrivi_certificato(f.cert_der)}")
                except Exception as e:
                    blocchi.append(f"=== {f.tipo} {i} ===\n(certificato non leggibile: {e})")
        dlg = QDialog(self)
        dlg.setWindowTitle("Certificati dei firmatari")
        dlg.resize(720, 560)
        l = QVBoxLayout(dlg)
        testo = QTextBrowser()
        testo.setPlainText("\n\n".join(blocchi))
        testo.setStyleSheet(f"font-family: {FONT_MONO}; font-size: 12px;")
        l.addWidget(testo)
        riga = QHBoxLayout()
        b_copia = pulsante("Copia", "copia")
        b_copia.clicked.connect(lambda: QApplication.clipboard().setText(testo.toPlainText()))
        b_ok = pulsante("Chiudi", ruolo="primario")
        b_ok.clicked.connect(dlg.accept)
        riga.addWidget(b_copia)
        riga.addStretch()
        riga.addWidget(b_ok)
        l.addLayout(riga)
        dlg.exec()

    def copia_report(self):
        r = self._selezionato()
        if r is not None:
            QApplication.clipboard().setText(report_testuale(r))
            self.b_copia.setText("Copiato")
            QTimer.singleShot(1500, lambda: self.b_copia.setText("Copia report"))

    def _salva_report(self, tipo):
        elenco = self._visibili()
        if not elenco:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salva il report", f"report_firme.{tipo}",
                                              "CSV (*.csv)" if tipo == "csv" else "Pagina HTML (*.html)")
        if not path:
            return
        try:
            if tipo == "csv":
                esporta_csv(elenco, path)
                QMessageBox.information(self, "Report salvato", f"Report salvato in:\n{path}")
            else:
                esporta_html(elenco, path)
                apri_esterno(path)
        except Exception as e:
            mostra_errore_con_copia(self, "Errore nel salvataggio del report", str(e))

    def chiudi(self):
        self._timer.stop()
        if self._scansione is not None and self._scansione.isRunning():
            self._scansione.annullato = True
            self._scansione.wait()              # un QThread non va mai distrutto mentre lavora

# ==========================================
# FINESTRA PRINCIPALE
# ==========================================
FILTRO_TUTTI = ("Tutti i formati supportati (*.tgz *.tar.gz *.tar *.zip *.mbox *.pst *.ost *.msg *.eml *.emlx "
                "*.ics *.vcf *.csv *.p7m *.p7s *.pdf *.xml);;Tutti i file (*)")

class ZimbraViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOME_APP)
        self.resize(1440, 920)
        self.setAcceptDrops(True)
        self._coda_import = []
        self._import_occupato = False         # vero dalla scelta della cartella fino alla fine dell'importazione
        self.worker_import = None
        self.pannello_import = None
        self.tab_firme = None
        pixmap = QPixmap()
        pixmap.loadFromData(ICON_SVG.encode('utf-8'))
        self.setWindowIcon(QIcon(pixmap))
        for sequenza, funzione in (("Ctrl+F", self.focus_ricerca), ("Ctrl+O", lambda: self.apri_file_dialog()),
                                   ("Ctrl+Shift+O", self.apri_cartella_dialog), ("Ctrl+W", self.chiudi_tab_corrente),
                                   ("Ctrl++", lambda: self.cambia_zoom(0.1)), ("Ctrl+=", lambda: self.cambia_zoom(0.1)),
                                   ("Ctrl+-", lambda: self.cambia_zoom(-0.1)), ("Ctrl+0", lambda: self.cambia_zoom(0)),
                                   ("F1", self.mostra_scorciatoie), ("F6", self.pannello_successivo),
                                   ("Shift+F6", lambda: self.pannello_successivo(-1))):
            QShortcut(QKeySequence(sequenza), self).activated.connect(funzione)

        centrale = QWidget()
        centrale.setObjectName("sfondo")
        self.setCentralWidget(centrale)
        lay = QVBoxLayout(centrale)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        barra = QWidget()
        barra.setObjectName("barraTitolo")
        barra.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        bl = QHBoxLayout(barra)
        bl.setContentsMargins(16, 10, 16, 10)
        logo = QLabel()
        logo.setPixmap(pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        marchio = QLabel("ZimbraViewer")
        marchio.setObjectName("marchio")
        versione = QLabel(f"{VERSIONE_APP} · posta archiviata e firme digitali")
        versione.setObjectName("versione")
        bl.addWidget(logo)
        bl.addSpacing(6)
        bl.addWidget(marchio)
        bl.addSpacing(8)
        bl.addWidget(versione)
        bl.addStretch()
        b_inizio = pulsante("Inizio", "casa", "fantasma", "Torna alla schermata con le istruzioni")
        b_inizio.clicked.connect(lambda: self.tabs.setCurrentWidget(self.benvenuto))
        b_firme = pulsante("Verifica firme", "scudo", "fantasma", "Verifica ed estrai documenti firmati (.p7m, .pdf, .xml)")
        b_firme.clicked.connect(self.mostra_firme)
        b_apri = pulsante("Apri…", "cartella", "primario", "Apri un export di posta, una mail o un documento firmato")
        menu = QMenu(self)
        menu.addAction(icona("documento", C["accento_chiaro"]), "Un file (export, mail, documento firmato)…   Ctrl+O", lambda: self.apri_file_dialog())
        menu.addAction(icona("cartella", C["accento_chiaro"]), "Una cartella…   Ctrl+Maiusc+O", self.apri_cartella_dialog)
        b_apri.setMenu(menu)
        b_chiudi = pulsante("Chiudi tutto", "cestino", "fantasma", "Chiude tutte le schede aperte e ferma i lavori in corso")
        b_chiudi.clicked.connect(self.svuota_tutto)
        b_acc = pulsante("Accessibilità", "accessibilita", "fantasma",
                         "Testo più grande, alto contrasto, animazioni ridotte e scorciatoie da tastiera")
        menu_acc = QMenu(self)
        menu_acc.addAction(icona("cerca", C["accento_chiaro"]), "Ingrandisci il testo   Ctrl++", lambda: self.cambia_zoom(0.1))
        menu_acc.addAction(icona("riduci", C["accento_chiaro"]), "Rimpicciolisci il testo   Ctrl+-", lambda: self.cambia_zoom(-0.1))
        menu_acc.addAction(icona("aggiorna", C["accento_chiaro"]), "Dimensione normale   Ctrl+0", lambda: self.cambia_zoom(0))
        menu_acc.addSeparator()
        self.azione_contrasto = menu_acc.addAction("Alto contrasto (si applica al prossimo avvio)")
        self.azione_contrasto.setCheckable(True)
        self.azione_contrasto.setChecked(ACCESSIBILITA["alto_contrasto"])
        self.azione_contrasto.toggled.connect(self.imposta_alto_contrasto)
        self.azione_animazioni = menu_acc.addAction("Riduci le animazioni")
        self.azione_animazioni.setCheckable(True)
        self.azione_animazioni.setChecked(ACCESSIBILITA["animazioni_ridotte"])
        self.azione_animazioni.toggled.connect(self.imposta_animazioni_ridotte)
        menu_acc.addSeparator()
        menu_acc.addAction(icona("tastiera", C["accento_chiaro"]), "Scorciatoie da tastiera   F1", self.mostra_scorciatoie)
        b_acc.setMenu(menu_acc)
        for b in (b_inizio, b_firme, b_acc, b_chiudi, b_apri):
            bl.addWidget(b)
        lay.addWidget(barra)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.chiudi_tab)
        self.tabs.setAccessibleName("Schede aperte")
        contenitore = QWidget()
        cl = QVBoxLayout(contenitore)
        cl.setContentsMargins(10, 6, 10, 0)
        cl.addWidget(self.tabs)
        lay.addWidget(contenitore, 1)

        self.benvenuto = SchermataBenvenuto()
        self.benvenuto.apri_file.connect(self.apri_file_dialog)
        self.benvenuto.apri_cartella.connect(self.apri_cartella_dialog)
        self.benvenuto.apri_firme.connect(self.mostra_firme)
        self.tabs.addTab(self.benvenuto, icona("casa", C["accento"], 16), "Inizio")
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)    # la scheda Inizio non si chiude
        self.tabs.tabBar().setTabButton(0, QTabBar.ButtonPosition.LeftSide, None)
        self.overlay = OverlayRilascio(centrale)
        self.statusBar().hide()

    # ---------- schede ----------
    def _aggiungi_tab(self, widget, nome_icona, titolo, suggerimento=""):
        idx = self.tabs.addTab(widget, icona(nome_icona, C["accento"], 16), titolo if len(titolo) <= 38 else titolo[:36] + "…")
        self.tabs.setTabToolTip(idx, suggerimento or titolo)
        self.tabs.setCurrentIndex(idx)
        return idx

    def mostra_firme(self):
        if self.tab_firme is None or self.tabs.indexOf(self.tab_firme) < 0:
            self.tab_firme = FirmeTab(self)
            self._aggiungi_tab(self.tab_firme, "scudo", "Verifica firme")
        self.tabs.setCurrentWidget(self.tab_firme)
        return self.tab_firme

    def verifica_dati(self, nome, dati, origine):
        self.mostra_firme().verifica_dati(nome, dati, origine)

    def controlla_duplicato(self, percorso):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if getattr(tab, 'path', None) == percorso:
                risposta = QMessageBox.question(self, "Già aperto", "Questo elemento è già aperto in un'altra scheda.\n\n"
                                                "Vuoi aprirne un'altra copia?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if risposta == QMessageBox.StandardButton.No:
                    self.tabs.setCurrentIndex(i)
                    return True
        return False

    def carica_eml_in_tab(self, percorso, titolo=None):
        if self.controlla_duplicato(percorso):
            return
        self._aggiungi_tab(MailViewerTab(percorso, mode="eml", parent_app=self), "busta",
                           titolo or os.path.basename(percorso), percorso)

    def carica_cartella_in_tab(self, percorso, auto_index=False):
        if self.controlla_duplicato(percorso):
            return
        self._aggiungi_tab(MailViewerTab(percorso, mode="export", parent_app=self, auto_index=auto_index),
                           "cartella", os.path.basename(percorso.rstrip("\\/")) or percorso, percorso)

    # ---------- accessibilità ----------
    def cambia_zoom(self, passo):
        scala = 1.0 if passo == 0 else min(2.0, max(0.8, round(ACCESSIBILITA["scala"] + passo, 1)))
        ACCESSIBILITA["scala"] = scala
        impostazioni().setValue("accessibilita/scala", scala)
        applica_stile(QApplication.instance())
        self._messaggio_stato(f"Dimensione del testo: {round(scala * 100)}%")

    def imposta_alto_contrasto(self, attivo):
        impostazioni().setValue("accessibilita/alto_contrasto", bool(attivo))
        QMessageBox.information(self, "Alto contrasto", "Il tema ad alto contrasto " + ("verrà attivato" if attivo else
                                "verrà disattivato") + " al prossimo avvio del programma.")

    def imposta_animazioni_ridotte(self, attivo):
        ACCESSIBILITA["animazioni_ridotte"] = bool(attivo)
        impostazioni().setValue("accessibilita/animazioni_ridotte", bool(attivo))
        if attivo:
            for w in self.findChildren(_Animato):
                w._timer_anim.stop()
        self._messaggio_stato("Animazioni ridotte" if attivo else "Animazioni normali")

    def _messaggio_stato(self, testo):
        sb = self.statusBar()
        sb.show()
        sb.showMessage(testo, 3000)
        annuncia(sb, testo)
        QTimer.singleShot(3200, lambda: sb.setVisible(
            any(not c.isHidden() for c in sb.findChildren(QWidget, "chipEsportazione"))))

    def pannello_successivo(self, verso=1):
        """F6 / Maiusc+F6: passa tra le zone principali (barra in alto, schede, ricerca, cartelle, elenco, anteprima)."""
        scheda = self.tabs.currentWidget()
        candidati = [self.tabs.tabBar()]
        for nome in ("barra_ricerca", "txt_cerca", "lista_sezioni", "albero_cartelle", "tabella_mail", "tabella_elementi",
                     "tabella", "preview_mail", "dettaglio"):
            w = getattr(scheda, nome, None)
            if isinstance(w, QWidget) and w.isVisible() and w.isEnabled():
                candidati.append(w)
        if scheda is self.benvenuto:
            candidati += [b for b in scheda.findChildren(QPushButton) if b.isVisible()][:1]
        attuale = QApplication.focusWidget()
        i = next((k for k, w in enumerate(candidati) if attuale is w or (attuale is not None and w.isAncestorOf(attuale))), -1)
        candidati[(i + verso) % len(candidati)].setFocus(Qt.FocusReason.TabFocusReason)

    def mostra_scorciatoie(self):
        righe = [("Ctrl+O", "Apri un file (export, mail, calendario, rubrica, documento firmato)"),
                 ("Ctrl+Maiusc+O", "Apri una cartella"), ("Ctrl+F", "Vai al campo di ricerca"),
                 ("Invio", "Nel campo di ricerca: cerca. Nell'elenco: apri la mail in una scheda / apri il file"),
                 ("Spazio", "Nell'elenco: spunta o togli la spunta alla riga corrente"),
                 ("Frecce", "Muoviti tra cartelle, sezioni e righe (l'anteprima segue la selezione)"),
                 ("Tasto Menu, Maiusc+F10", "Azioni sulla riga corrente"),
                 ("F6 / Maiusc+F6", "Passa alla zona successiva / precedente della finestra"),
                 ("Ctrl+Tab / Ctrl+Maiusc+Tab", "Scheda successiva / precedente"), ("Ctrl+W", "Chiudi la scheda"),
                 ("Ctrl++ / Ctrl+- / Ctrl+0", "Testo più grande / più piccolo / normale"),
                 ("Esc", "Nelle finestre di avanzamento: riduci e continua a lavorare"), ("F1", "Questo elenco")]
        testo = "<table cellspacing='0' cellpadding='4'>" + "".join(
            f"<tr><td><b>{html.escape(k)}</b></td><td>{html.escape(v)}</td></tr>" for k, v in righe) + "</table>"
        box = QMessageBox(QMessageBox.Icon.Information, "Scorciatoie da tastiera", testo, parent=self)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.exec()

    def focus_ricerca(self):
        barra = getattr(self.tabs.currentWidget(), 'barra_ricerca', None) or getattr(self.tabs.currentWidget(), 'txt_cerca', None)
        if barra is not None and barra.isEnabled():
            barra.setFocus()
            barra.selectAll()

    def chiudi_tab_corrente(self):
        if self.tabs.currentWidget() is not self.benvenuto:
            self.chiudi_tab(self.tabs.currentIndex())

    def chiudi_tab(self, index, chiedi=True):
        widget = self.tabs.widget(index)
        if widget is None or widget is self.benvenuto:
            return
        if chiedi and getattr(widget, "_export_in_corso", False):
            r = QMessageBox.question(self, "Esportazione in corso",
                                     "In questa scheda c'è un'esportazione in corso.\n\nChiudendo la scheda viene interrotta: continuo?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return
        widget.chiudi()
        self.tabs.removeTab(index)
        widget.deleteLater()
        if widget is self.tab_firme:
            self.tab_firme = None

    def svuota_tutto(self):
        if self.tabs.count() <= 1:
            return
        r = QMessageBox.question(self, "Chiudere tutto?", "Chiudo tutte le schede?\n\nI lavori in corso vengono fermati e i file sbloccati.",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            for i in range(self.tabs.count() - 1, -1, -1):
                self.chiudi_tab(i, chiedi=False)
            self.tabs.setCurrentWidget(self.benvenuto)

    def closeEvent(self, evento):
        """Uscita: se ci sono lavori in corso chiede conferma, poi chiude tutto in modo pulito."""
        schede = [self.tabs.widget(i) for i in range(self.tabs.count())]
        occupato = any(getattr(w, "_export_in_corso", False) for w in schede) or \
            (self.worker_import is not None and self.worker_import.isRunning())
        if occupato:
            r = QMessageBox.question(self, "Lavori in corso",
                                     "C'è un'importazione o un'esportazione in corso.\n\nUscendo viene interrotta "
                                     "(quello che è già stato scritto resta). Esco?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                evento.ignore()
                return
        if self.worker_import is not None and self.worker_import.isRunning():
            self.worker_import.cancel()
            self.worker_import.wait()             # mai uscire con il thread ancora vivo
        for w in schede:
            try:
                if hasattr(w, "chiudi"):
                    w.chiudi()
            except Exception:
                pass
        evento.accept()

    def richiama_finestra(self, percorsi):
        """Chiamato quando una seconda esecuzione del programma passa i propri parametri a questa istanza."""
        self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()
        if percorsi:
            self.apri_percorsi(percorsi)

    # ---------- apertura universale (pulsanti, trascinamento, riga di comando) ----------
    def apri_file_dialog(self, filtro=""):
        filtri = (filtro + ";;" if filtro else "") + FILTRO_TUTTI
        percorsi, _ = QFileDialog.getOpenFileNames(self, "Scegli il file da aprire", "", filtri)
        if percorsi:
            self.apri_percorsi(percorsi)

    def apri_cartella_dialog(self):
        percorso = QFileDialog.getExistingDirectory(self, "Scegli la cartella con la posta (export, profilo, caselle .mbox…)")
        if percorso:
            self.apri_percorsi([percorso])

    def apri_percorsi(self, percorsi):
        firmati = []
        verso_firme = isinstance(self.tabs.currentWidget(), FirmeTab)
        for p in percorsi:
            if not p or (p.startswith('-') and not os.path.exists(p)):
                continue                                      # eventuali opzioni da riga di comando
            percorso = os.path.abspath(os.path.expanduser(p))
            if verso_firme and os.path.isdir(percorso):
                firmati.append(percorso)              # la ricerca nella cartella la fa la scheda firme, in background
                continue
            tipo, descrizione = rileva_sorgente(percorso)
            if tipo == "firmato":
                firmati.append(percorso)
            elif tipo == "cartella_eml":
                self.carica_cartella_in_tab(percorso)
            elif tipo == "eml":
                self.carica_eml_in_tab(percorso)
            elif tipo in ("msg", "emlx"):
                try:
                    self.carica_eml_in_tab(converti_singola_in_eml(percorso), os.path.basename(percorso))
                except Exception as e:
                    mostra_errore_con_copia(self, "Impossibile leggere la mail", f"{os.path.basename(percorso)}:\n{e}")
            elif tipo in ("archivio", "pst", "mbox", "cartella_da_convertire", "pim"):
                self._coda_import.append((percorso, descrizione))   # le importazioni vanno una alla volta
            elif not os.path.exists(percorso):
                mostra_errore_con_copia(self, "Percorso non trovato", f"Non esiste:\n{percorso}")
            else:
                mostra_errore_con_copia(
                    self, "Formato non riconosciuto",
                    f"{percorso}\n\n{descrizione.capitalize()}.\n\nPosso aprire: export Zimbra e Carbonio (.tgz), Google Takeout (.zip/.mbox), "
                    "Outlook (.pst, .ost, .msg), Thunderbird e Apple Mail (cartelle o .mbox), Maildir, singole mail (.eml, .emlx) "
                    "calendari (.ics), rubriche (.vcf, .csv) e documenti firmati (.p7m, .pdf, .xml).\n\nNella scheda «Inizio» trovi come ottenere l'export dal tuo programma.")
        if firmati:
            self.mostra_firme().aggiungi_percorsi(firmati)
        self._avvia_prossima_importazione()

    # ---------- importazione (archivi e formati di altri programmi) ----------
    def _avvia_prossima_importazione(self):
        # il dialogo di scelta della cartella apre un ciclo di eventi: nel frattempo può arrivare un'altra richiesta
        if self._import_occupato or (self.worker_import is not None and self.worker_import.isRunning()):
            return
        self._import_occupato = True
        try:
            while self._coda_import:
                sorgente, descrizione = self._coda_import.pop(0)
                if self._avvia_importazione(sorgente, descrizione):
                    return                            # resta occupato fino a fine importazione
        except Exception:
            self._import_occupato = False
            raise
        self._import_occupato = False

    def _avvia_importazione(self, sorgente, descrizione):
        nome = os.path.basename(sorgente.rstrip("\\/"))
        base = re.sub(r'(\.tar\.gz|\.tgz|\.tar|\.zip|\.mbox|\.pst|\.ost|\.ics|\.vcf|\.csv)$', '', nome, flags=re.IGNORECASE) or "posta"
        padre = QFileDialog.getExistingDirectory(
            self, f"Dove creo la cartella con la posta pronta da consultare? ({descrizione})", os.path.dirname(sorgente))
        if not padre:
            return False
        dest = cartella_libera(padre, nome_windows_sicuro(f"Posta - {base}", 80, "Posta", con_estensione=False))
        self.pannello_import = PannelloAvanzamento(self, "Preparazione della posta", f"Importazione {nome}", self, "archivio")
        self.pannello_import.aggiorna(0, f"{nome}\nEstraggo e converto le mail in una cartella che si apre in un attimo "
                                         "anche le volte successive.")
        self.worker_import = ImportWorker(sorgente, dest)
        self.worker_import.progress.connect(lambda perc, testo: self.pannello_import and self.pannello_import.aggiorna(perc, testo))
        self.worker_import.finished.connect(self._importazione_finita)
        self.worker_import.error.connect(self._importazione_errore)
        self.pannello_import.annulla.connect(self.worker_import.cancel)
        self.pannello_import.avvia()
        self.worker_import.start()
        return True

    def _chiudi_pannello_import(self):
        if self.worker_import is not None:
            self.worker_import.wait()             # il segnale arriva da dentro run(): si aspetta che il thread finisca
        self._import_occupato = False
        if self.pannello_import is not None:
            self.pannello_import.chiudi()
            self.pannello_import = None

    def _importazione_finita(self, cartella, info):
        self._chiudi_pannello_import()
        if cartella:
            self.carica_cartella_in_tab(cartella, auto_index=True)
            errori = info.get("errori", [])
            if errori:
                mostra_errore_con_copia(self, "Importazione completata con avvisi",
                                        f"Mail convertite: {info.get('convertite', 0)}\nNon convertite: {len(errori)}\n\n" +
                                        "\n".join(errori[:30]) + (f"\n... e altre {len(errori) - 30}" if len(errori) > 30 else ""))
        QTimer.singleShot(0, self._avvia_prossima_importazione)

    def _importazione_errore(self, messaggio):
        self._chiudi_pannello_import()
        consiglio = ""
        if "libpff" in messaggio:
            consiglio = ("\n\nPer i file di Outlook .pst/.ost serve la libreria libpff-python, da installare prima di "
                         "compilare il programma (pip install libpff-python). In alternativa, da Outlook puoi trascinare "
                         "le mail in una cartella: diventano file .msg che si aprono senza librerie aggiuntive.")
        elif "olefile" in messaggio:
            consiglio = "\n\nPer i file .msg serve la libreria olefile (pip install olefile)."
        mostra_errore_con_copia(self, "Importazione non riuscita", messaggio + consiglio)
        QTimer.singleShot(0, self._avvia_prossima_importazione)

    # ---------- trascinamento ----------
    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        event.acceptProposedAction()
        percorsi = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        firme = isinstance(self.tabs.currentWidget(), FirmeTab) or (
            percorsi and all(supportato(os.path.basename(p)) for p in percorsi))
        self.overlay.mostra("Rilascia per verificare le firme" if firme else "Rilascia per aprire la posta")

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.overlay.hide()

    def dropEvent(self, event):
        self.overlay.hide()
        percorsi = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if percorsi:
            event.acceptProposedAction()
            QTimer.singleShot(0, lambda: self.apri_percorsi(percorsi))     # il trascinamento si chiude subito

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay.isVisible():
            self.overlay.setGeometry(self.overlay.parentWidget().rect())

# ==========================================
# SINGOLA ISTANZA
# ==========================================
def nome_istanza():
    """Nome del canale locale; include l'utente per non far "litigare" sessioni diverse (es. Terminal Server)."""
    utente = re.sub(r'[^A-Za-z0-9_]', '_', os.environ.get('USERNAME') or os.environ.get('USER') or 'utente')
    return f"ZimbraViewer_SingolaIstanza_{utente}"

def invia_a_istanza_esistente(nome, percorsi):
    """Se un'altra istanza è già in esecuzione le passa i percorsi da aprire e restituisce True."""
    socket = QLocalSocket()
    socket.connectToServer(nome)
    if not socket.waitForConnected(500):
        return False
    if IS_WIN:
        try:    # permette alla finestra già aperta di prendere il focus
            import ctypes
            ctypes.windll.user32.AllowSetForegroundWindow(-1)
        except Exception:
            pass
    socket.write(json.dumps(percorsi).encode('utf-8') + b"\n")
    socket.flush()
    socket.waitForBytesWritten(2000)
    socket.disconnectFromServer()
    if socket.state() != QLocalSocket.LocalSocketState.UnconnectedState:
        socket.waitForDisconnected(1000)
    return True

class ServerIstanza(QObject):
    """Resta in ascolto: le esecuzioni successive del programma mandano qui i loro parametri."""
    percorsi_ricevuti = pyqtSignal(list)

    def __init__(self, nome, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.server = QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)  # solo l'utente corrente
        self.server.newConnection.connect(self._nuova_connessione)

    def avvia(self):
        QLocalServer.removeServer(self.nome)   # toglie un socket rimasto da un crash (Linux/macOS)
        return self.server.listen(self.nome)

    def _nuova_connessione(self):
        while self.server.hasPendingConnections():
            conn = self.server.nextPendingConnection()
            buf = bytearray()
            conn.readyRead.connect(lambda c=conn, b=buf: b.extend(c.readAll().data()))
            conn.disconnected.connect(lambda c=conn, b=buf: self._fine_messaggio(c, b))

    def _fine_messaggio(self, conn, buf):
        buf.extend(conn.readAll().data())
        conn.deleteLater()
        try:
            percorsi = json.loads(bytes(buf).decode('utf-8'))
            percorsi = [p for p in percorsi if isinstance(p, str)] if isinstance(percorsi, list) else []
        except Exception:
            percorsi = []
        self.percorsi_ricevuti.emit(percorsi)

class AppZimbra(QApplication):
    """Su macOS i file aperti dal Finder (doppio clic, "Apri con", trascinamento sull'icona del Dock) non arrivano
    nella riga di comando ma come eventi FileOpen: si raccolgono e si passano alla finestra tutti insieme."""
    file_da_aprire = pyqtSignal(list)

    def __init__(self, argv):
        super().__init__(argv)
        self._in_coda = []
        self._pronta = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._consegna)

    def event(self, e):
        if e.type() == QEvent.Type.FileOpen:
            p = e.file() or e.url().toLocalFile()
            if p:
                self._in_coda.append(p)
                if self._pronta:
                    self._timer.start()
            return True
        return super().event(e)

    def pronta(self):
        self._pronta = True
        if self._in_coda:
            self._timer.start()

    def _consegna(self):
        percorsi, self._in_coda = self._in_coda, []
        if percorsi:
            self.file_da_aprire.emit(percorsi)

if __name__ == '__main__':
    prepara_webengine()
    app = AppZimbra(sys.argv)

    # Con --noconsole un errore non gestito in PyQt6 chiude il programma senza dire nulla:
    # lo si mostra in una finestra (copiabile) e il programma resta aperto.
    _gestione_errore = {"attiva": False}
    def errore_non_gestito(tipo, valore, tb):
        if _gestione_errore["attiva"]:
            sys.__excepthook__(tipo, valore, tb)
            return
        _gestione_errore["attiva"] = True
        try:
            import traceback
            testo = "".join(traceback.format_exception(tipo, valore, tb))
            mostra_errore_con_copia(QApplication.activeWindow(), "Errore imprevisto",
                                    "Si è verificato un errore imprevisto; il programma resta aperto.\n\n" + testo[-6000:])
        except Exception:
            sys.__excepthook__(tipo, valore, tb)
        finally:
            _gestione_errore["attiva"] = False
    sys.excepthook = errore_non_gestito
    app.setApplicationName("ZimbraViewer")
    app.setApplicationDisplayName("ZimbraViewer")
    app.setDesktopFileName("zimbraviewer")       # Wayland/GNOME: collega la finestra al file .desktop e alla sua icona
    carica_accessibilita()                       # zoom, alto contrasto (anche dal sistema), animazioni ridotte
    applica_palette(ACCESSIBILITA["alto_contrasto"])
    if not IS_WIN:
        app.setStyle("Fusion")                   # il foglio di stile è pensato su Fusion/Windows, non sullo stile macOS
    applica_stile(app)
    _pix_icona = QPixmap()
    _pix_icona.loadFromData(ICON_SVG.encode('utf-8'))
    app.setWindowIcon(QIcon(_pix_icona))

    # Percorsi assoluti: l'istanza già aperta ha una cartella di lavoro diversa dalla nostra
    argomenti = [os.path.abspath(a) if (not a.startswith('-') or os.path.exists(a)) else a for a in sys.argv[1:]]

    # Singola istanza: se il programma è già aperto gli passo i parametri e esco
    nome_ist = nome_istanza()
    if invia_a_istanza_esistente(nome_ist, argomenti):
        sys.exit(0)
    server_istanza = ServerIstanza(nome_ist)
    if not server_istanza.avvia():
        # Un'altra istanza è partita nello stesso istante: riprovo a passarle i parametri
        if invia_a_istanza_esistente(nome_ist, argomenti):
            sys.exit(0)

    if not hasattr(sys, 'frozen') and IS_WIN and not os.path.exists('zimbra_icon.ico'):
        try:
            pix = QPixmap()
            pix.loadFromData(ICON_SVG.encode('utf-8'))
            pix.save('zimbra_icon.ico', 'ICO')
        except Exception:
            pass

    finestra = ZimbraViewerApp()
    server_istanza.percorsi_ricevuti.connect(finestra.richiama_finestra)
    app.file_da_aprire.connect(finestra.richiama_finestra)
    finestra.show()
    app.pronta()

    # Archivio di fiducia (con il download della Trusted List AgID) preparato in sottofondo:
    # la prima verifica non deve aspettare la rete
    if P7M_LIBRERIE_OK:
        threading.Thread(target=archivio_fiducia, daemon=True).start()

    # Apertura da parametri: cartelle export, .tgz / .tar.gz / .tar, .eml
    # Esempio: ZimbraViewer.exe "C:\Mail\export" takeout.zip outlook.pst mail.msg documento.p7m
    if argomenti:
        QTimer.singleShot(200, lambda: finestra.apri_percorsi(argomenti))

    sys.exit(app.exec())
