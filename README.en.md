<p align="center">
  <img src="docs/social-preview.png" alt="ZimbraViewer" width="100%">
</p>

<p align="center">
  <a href="README.md">Italiano</a> · <b>English</b>
</p>

# ZimbraViewer

**Offline mail-archive viewer with digital signature verification.**
Opens exports from Zimbra, Carbonio, Gmail, Outlook, Thunderbird, Apple/iCloud (or any mbox, Maildir, `.eml`, `.ics`, `.vcf`), indexes them in a local database and lets you **search, read, print to PDF and export** messages and attachments, plus **calendar, tasks, contacts, chats, notes and files** — **no server, no mail client, no internet**: your files never leave your computer.

It ships with a **digital signature** verifier (CAdES `.p7m`, PAdES, XAdES, Italian e-invoices/FatturaPA) that builds trust chains against the **Italian AgID Trusted List (eIDAS)**, and renders Italian **PEC** (certified e-mail) the way a certified mailbox does.

> The user interface is in Italian.

![Home screen](docs/screenshot.png)

## Features

### Opening mail
- **Automatic format detection**: drag a file or folder onto the window, use *Apri…* (Ctrl+O / Ctrl+Shift+O), or pass paths on the command line.
- **Supported sources**
  | Source | Format |
  |---|---|
  | Zimbra, Carbonio | `.tgz` / `.tar.gz` / `.tar` (REST `fmt=tgz`) or extracted folder |
  | Gmail (Google Takeout) | `.mbox` or `.zip` — folders rebuilt from `X-Gmail-Labels` |
  | Outlook | `.pst` / `.ost` (libpff), single `.msg` files (olefile, compressed RTF included) |
  | Thunderbird | mbox files and `.sbd` subfolders |
  | Apple Mail | `.mbox` mailboxes, `.emlx` files |
  | Generic | mbox, Maildir/Maildir++, `.eml`, `.zip` |
- Archives are **converted once** into a `Posta - <name>` folder of `.eml` files; afterwards that folder opens directly.
- mbox files are **streamed**, even multi-GB ones. Imports are queued, with progress and cancel.

### Calendar, tasks, contacts, chats, notes and files
Everything the export holds besides mail shows up in **sections** on the left (Mail, Calendar, Tasks, Contacts, Chat, Notes, Files, with item counts), each with folders, search, preview, print to PDF and **export to `.ics`, `.vcf` or `.csv`** (Briefcase files can be opened or saved).

| Source | What is read |
|---|---|
| Zimbra / Carbonio (`.tgz`) | appointments (`.appt`), tasks (`.task`), contacts and groups (`.meta` metadata), chats (`.chat`), notes, Briefcase |
| Google Takeout | Calendar (`.ics`), Contacts (`.vcf`), Tasks (`Tasks.json`), Keep (`.json`), Google Chat (`messages.json`) |
| Microsoft Outlook | calendar, task, contact and note items inside `.pst`/`.ost` and `.msg`; `.csv` contacts |
| Apple / iCloud | Calendar and Reminders (`.ics`), Contacts (`.vcf`) |
| Thunderbird | address book (`abook.sqlite`), local calendar (`local.sqlite`), exported `.ics`/`.vcf` |
| Any program | `.ics`, `.vcs` (events, tasks, journal), `.vcf` (vCard 2.1/3.0/4.0, quoted-printable too), contact CSV |

Time zones, all-day events, recurrences (in plain words), attendees with their replies, task priority and status. Indexes built by earlier versions are completed automatically on first open.

### Search and reading
- **SQLite** index (`zimbra_index.db`) stored inside the mail folder with **relative paths**: move or copy the folder without re-indexing.
- Search across sender, recipient, subject, folder, body and **attachment names**; multiple words = AND, exact phrases in `<angle brackets>`.
- Selecting a folder also shows mail from **all its subfolders**.
- Sandboxed Chromium preview (no link navigation, JavaScript off) with inline (`cid:`) images.
- **Conversation history**: quoted/forwarded headers turned into readable separators (Outlook, Gmail, Zimbra, Thunderbird).
- **PEC**: banner with receipt type and certification data from `daticert.xml`; the original message inside `postacert.eml` is shown directly.

### Digital signatures (built-in P7MReader)
- **CAdES** (`.p7m`, nested or base64; detached `.p7s`), **PAdES** (signed PDFs, detects changes after signing), **XAdES** (`.xml`, cryptographic check), **FatturaPA** summary.
- Counter-signatures and RFC 3161 **timestamps** verified; expired certificates validated at signing time.
- Trust chain against the **AgID Trusted List** (refreshed at every start, with offline copy; accepted only if its XAdES signature is intact and its signer is the one listed in the **EU Commission's LOTL**), certifier status **at signing time** (ServiceHistory), **eIDAS qualification** (QES, AdES/QC, QSCD) and qualified timestamps, key-usage check + system certificate store (Windows, macOS keychain, Linux distribution CAs); OCSP/CRL revocation in soft-fail mode.
- Clear outcomes: **Verified / Warning / Invalid**, with the list of checks for every signature; CSV/HTML reports.

### Export
- **Export PDF + attachments** (bulk on checked messages or a single one): for each message a folder `YYYY.MM.DD HH.mm.ss <subject>` containing the PDF, attachments (original `.p7m` **and** extracted document), a `Dettagli mail.txt` with headers and verification results, and unpacked `postacert.eml`.
- File names valid on Windows, macOS and Linux, within Windows' 260-character path limit (exports can be copied anywhere).

### Interface
- Dark theme, **single-instance** window (new launches hand their paths to the open window), long jobs in **non-modal** dialogs that can be minimised to the status bar.

### Accessibility (WCAG 2.2 AA / EN 301 549)
- **Keyboard**: focus always visible; arrow keys in sections, folders and lists (the preview follows); **Space** checks, **Enter** opens; Menu key / Shift+F10 for actions; **F6** moves between window areas; **F1** lists every shortcut.
- **Screen readers** (NVDA, JAWS, Narrator, VoiceOver, Orca): names and descriptions for icon-only buttons, fields, tables, progress bars and preview; result counts are reported; preview pages declare their language.
- **Vision**: text contrast ≥ 4.5:1 and control borders ≥ 3:1; **high-contrast theme** (*Accessibilità* menu, or automatic when enabled in the OS); **text zoom** with Ctrl+ / Ctrl- / Ctrl+0, preview included.
- **Motion**: animations stop by themselves after 5 seconds and can be switched off with *Riduci le animazioni* (automatic when the OS asks for reduced motion).

## Download and install

Ready-made builds are on the **Releases** page (or in the *Artifacts* of the **Build** workflow under Actions). They are **standalone**: Python, Qt and Chromium are bundled, nothing else to install.

| System | File | How to start |
|---|---|---|
| **Windows 10/11** (x64) | `ZimbraViewer-<ver>-windows-x64.exe` | double-click |
| **macOS 12+** Apple Silicon (M1…M4) | `ZimbraViewer-<ver>-macOS-arm64.dmg` | open the `.dmg`, drag the app to *Applications* |
| **macOS 12+** Intel | `ZimbraViewer-<ver>-macOS-x86_64.dmg` | same as above |
| **Linux** x86_64 (Debian 12+, Ubuntu 22.04+, Fedora 36+, Arch, Manjaro, openSUSE…) | `ZimbraViewer-<ver>-x86_64.AppImage` | `chmod +x`, then double-click |
| **Linux** x86_64, menu install | `ZimbraViewer-<ver>-linux-x86_64.tar.gz` | extract and run `./installa-linux.sh` |

**macOS** – the app is not signed with an Apple Developer certificate, so macOS blocks it on first launch: open *System Settings → Privacy & Security* and click **Open Anyway** (once). Or, from Terminal:

```bash
xattr -dr com.apple.quarantine /Applications/ZimbraViewer.app
```

On macOS files also open via *Open With → ZimbraViewer* or by dropping them on the Dock icon.

**Linux (AppImage)**

```bash
chmod +x ZimbraViewer-*-x86_64.AppImage
```

```bash
./ZimbraViewer-*-x86_64.AppImage
```

Without FUSE the AppImage still starts with `--appimage-extract-and-run`, or use the `.tar.gz`. The `.tar.gz` installs for the current user only (`~/.local/opt/zimbraviewer`, with a menu entry and the `zimbraviewer` command); remove it with `./installa-linux.sh --rimuovi`.
On distributions that forbid user namespaces to non-installed programs (e.g. Ubuntu 23.10+ with AppArmor) the Chromium sandbox of the preview is disabled automatically; previews still run with JavaScript off and non-navigable links.

## Requirements (running from source)

- **Windows 10/11**, **macOS 12+** or **Linux** with a graphical desktop (X11 or Wayland)
- **Python 3.12+** (tested with 3.13 and 3.15)

| Package | Purpose | Required |
|---|---|---|
| `PyQt6`, `PyQt6-WebEngine` | UI and preview | ✅ |
| `asn1crypto`, `pyhanko`, `pyhanko-certvalidator`, `cryptography`, `lxml` | signature verification | optional |
| `olefile` | Outlook `.msg` | optional |
| `libpff-python` | Outlook `.pst` / `.ost` | optional |

Without an optional library everything else still works: signatures show as *Not verified* and `.pst` files give a clear message.

## Run from source

```bash
pip install pyqt6 pyqt6-webengine asn1crypto pyhanko pyhanko-certvalidator cryptography lxml olefile certifi tzdata libpff-python
```

```bash
python "ZimbraViewer 3.2.py"
```

Command line (any mix of files and folders):

```bash
python "ZimbraViewer 3.2.py" "C:\Mail\export" backup.tgz takeout.zip outlook.pst mail.msg document.p7m
```

## Build the executable

PyInstaller does not cross-compile: each build is made on its own OS. The easiest way is the **GitHub Actions** workflow `.github/workflows/build.yml`, which builds every version in parallel: start it from *Actions → Build → Run workflow*, or push a `v*` tag (e.g. `v3.2.0`) to also get a Release with all packages attached.

### macOS and Linux

```bash
./build_zimbra.sh
```

It creates a `.venv-build` virtual environment, installs the dependencies and uses `ZimbraViewer.spec`:
- **macOS** → `dist/ZimbraViewer.app` and `dist/ZimbraViewer-<ver>-macOS-<arch>.dmg` (for the architecture of the Mac it runs on);
- **Linux** → `dist/ZimbraViewer-<ver>-x86_64.AppImage` and `dist/ZimbraViewer-<ver>-linux-x86_64.tar.gz`. For an AppImage that runs on many distributions, build on the one with the oldest glibc you want to support (the workflow uses Ubuntu 22.04).

`libpff-python` (for `.pst`) is compiled from source and needs a C compiler (`build-essential` / `gcc` / Xcode Command Line Tools); without it the build continues without `.pst` support. Icons `zimbra_icon.png` / `.icns` are regenerated with `python packaging/genera_icone.py`.

### Windows

`build_zimbra.bat` installs the dependencies and builds the exe with PyInstaller, including icon and version info (`version_info.txt`):

```bash
build_zimbra.bat
```

```bash
build_zimbra.bat onedir
```

The first produces a single `dist\ZimbraViewer.exe`; `onedir` produces a folder (faster start-up). The `zimbra_icon.ico` icon is generated on the first run of the `.py` if missing.

## Where data is stored

| What | Where |
|---|---|
| Mail index | `zimbra_index.db` inside the mail folder |
| AgID Trusted List | Windows `%LOCALAPPDATA%\ZimbraViewer\TSL-IT.xml` · macOS `~/Library/Caches/ZimbraViewer/TSL-IT.xml` · Linux `~/.cache/ZimbraViewer/TSL-IT.xml` |
| Signature settings | read (never written) from `P7MReader/impostazioni.json` in `%APPDATA%` (Windows), `~/Library/Application Support` (macOS) or `~/.config` (Linux), if present |
| UI preferences | QSettings: registry (Windows), `~/Library/Preferences` (macOS), `~/.config/ZimbraViewer` (Linux) |
| Attachments opened on the fly | temp folder, cleaned up on exit |

## License

Released under the **GNU GPL v3.0** — see [LICENSE](LICENSE).
