# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller multipiattaforma per ZimbraViewer.
#   Windows : python -m PyInstaller ZimbraViewer.spec            -> dist\ZimbraViewer.exe (un solo file)
#   macOS   : python -m PyInstaller ZimbraViewer.spec            -> dist/ZimbraViewer.app
#   Linux   : python -m PyInstaller ZimbraViewer.spec            -> dist/ZimbraViewer/ (poi AppImage con build_zimbra.sh)
# Variabile ZV_ONEDIR=1 su Windows: cartella al posto del singolo exe (avvio più veloce).
import glob
import os
import sys

VERSIONE = "3.2.0"
SCRIPT = sorted(glob.glob("ZimbraViewer *.py"))[-1]
IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
ONEFILE = IS_WIN and os.environ.get("ZV_ONEDIR") != "1"

binaries = []
if IS_WIN:
    # cryptography per Python 3.15 free-threaded si lega a python3t.dll, che PyInstaller non include da solo
    dll = os.path.join(sys.base_prefix, "abi3t-compat", "python3t.dll")
    if os.path.exists(dll):
        binaries.append((dll, "."))

datas = []
if os.path.exists("TSL-IT.xml"):          # copia offline facoltativa della Trusted List AgID
    datas.append(("TSL-IT.xml", "."))

hiddenimports = ["PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtNetwork", "PyQt6.QtSvg"]
for opzionale in ("certifi", "olefile", "pypff"):
    try:
        __import__(opzionale)
        hiddenimports.append(opzionale)
    except ImportError:
        pass

if IS_WIN:
    icona = "zimbra_icon.ico"
elif IS_MAC:
    icona = "zimbra_icon.icns"
else:
    icona = "zimbra_icon.png"
icona = [icona] if os.path.exists(icona) else None

a = Analysis(
    [SCRIPT],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "matplotlib", "numpy", "scipy", "pandas", "PIL"],
    noarchive=False,
    optimize=0,
)
if not IS_WIN:
    # Il motore Chromium porta con sé QML: PyInstaller includerebbe anche Quick3D, Multimedia, i controlli QML e i
    # 50 MB di traduzioni di Chromium, che il programma non usa. Si tengono solo le librerie davvero collegate
    # e le lingue italiana e inglese (circa 120 MB in meno).
    import re as _re
    _INUTILI = _re.compile(
        r"(^|[/\\])PyQt6[/\\]Qt6[/\\]qml[/\\]"
        r"|Qt6?(Quick3D\w*|QuickControls2\w*|QuickDialogs2\w*|QuickEffects|QuickLayouts|QuickParticles|QuickShapes"
        r"|QuickTemplates2|QuickTest|QuickTimeline\w*|QuickVectorImage\w*|Multimedia\w*|Sensors\w*|TextToSpeech"
        r"|RemoteObjects\w*|SpatialAudio|ShaderTools|StateMachine\w*|Test|WebEngineQuick\w*|WebChannelQuick"
        r"|PositioningQuick|QmlCore|WebSockets)(\.|_|$|[/\\])"
        r"|qtwebengine_devtools_resources")
    _LINGUA = _re.compile(r"translations[/\\](qtwebengine_locales[/\\](?!(it|en-US)\.pak$)|\w+_(?!(it|en)\.qm$)[\w-]+\.qm$)")

    def _tieni(voce):
        destinazione = voce[0].replace("\\", "/")
        return not (_INUTILI.search(destinazione) or _LINGUA.search(destinazione))

    a.binaries = [b for b in a.binaries if _tieni(b)]
    a.datas = [d for d in a.datas if _tieni(d)]

pyz = PYZ(a.pure)

if ONEFILE:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name="ZimbraViewer",
        debug=False, bootloader_ignore_signals=False, strip=False, upx=False, upx_exclude=[],
        runtime_tmpdir=None, console=False, disable_windowed_traceback=False,
        argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None,
        version="version_info.txt" if os.path.exists("version_info.txt") else None,
        icon=icona,
    )
else:
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name="ZimbraViewer",
        debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
        console=False, disable_windowed_traceback=False,
        argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None,
        version="version_info.txt" if IS_WIN and os.path.exists("version_info.txt") else None,
        icon=icona,
    )
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, upx_exclude=[], name="ZimbraViewer")

if IS_MAC:
    def tipo(nome, estensioni, ruolo="Viewer"):
        return {"CFBundleTypeName": nome, "CFBundleTypeRole": ruolo, "LSHandlerRank": "Alternate",
                "CFBundleTypeExtensions": estensioni}

    app = BUNDLE(
        coll,
        name="ZimbraViewer.app",
        icon=icona[0] if icona else None,
        bundle_identifier="io.github.konjikinoyami1991.zimbraviewer",
        version=VERSIONE,
        info_plist={
            "CFBundleName": "ZimbraViewer",
            "CFBundleDisplayName": "ZimbraViewer",
            "CFBundleShortVersionString": VERSIONE,
            "CFBundleVersion": VERSIONE,
            "LSMinimumSystemVersion": "12.0",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "LSApplicationCategoryType": "public.app-category.productivity",
            "CFBundleDocumentTypes": [
                tipo("Messaggio di posta", ["eml", "emlx", "msg"]),
                tipo("Casella di posta", ["mbox", "pst", "ost"]),
                tipo("Archivio di posta", ["tgz", "tar", "gz", "zip"]),
                tipo("Documento firmato", ["p7m", "p7s"]),
                {"CFBundleTypeName": "Cartella di posta", "CFBundleTypeRole": "Viewer",
                 "LSHandlerRank": "Alternate", "LSItemContentTypes": ["public.folder"]},
            ],
        },
    )
