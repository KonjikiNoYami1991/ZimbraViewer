#!/usr/bin/env bash
# Installa ZimbraViewer (versione in cartella) per l'utente corrente, senza permessi di amministratore:
#   programma in ~/.local/opt/zimbraviewer, comando "zimbraviewer" in ~/.local/bin, voce nel menu delle applicazioni.
# Uso:  ./installa-linux.sh            (installa/aggiorna)
#       ./installa-linux.sh --rimuovi  (disinstalla)
set -euo pipefail
QUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/opt/zimbraviewer"
BIN="$HOME/.local/bin"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICONE="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"

if [ "${1:-}" = "--rimuovi" ]; then
    rm -rf "$DEST" "$BIN/zimbraviewer" "$APPS/zimbraviewer.desktop" "$ICONE/zimbraviewer.png"
    command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" || true
    echo "ZimbraViewer rimosso."
    exit 0
fi

mkdir -p "$DEST" "$BIN" "$APPS" "$ICONE"
rm -rf "$DEST"/*
cp -a "$QUI/ZimbraViewer/." "$DEST/"
ln -sf "$DEST/ZimbraViewer" "$BIN/zimbraviewer"
cp "$QUI/zimbraviewer.png" "$ICONE/zimbraviewer.png"
sed "s|^Exec=.*|Exec=\"$DEST/ZimbraViewer\" %F|" "$QUI/zimbraviewer.desktop" > "$APPS/zimbraviewer.desktop"
command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" || true
echo "ZimbraViewer installato: lo trovi nel menu delle applicazioni o col comando 'zimbraviewer'."
case ":$PATH:" in *":$BIN:"*) ;; *) echo "Nota: aggiungi $BIN al PATH per usare il comando da terminale.";; esac
