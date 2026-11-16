"""Genera le icone del programma (PNG per Linux, ICNS per macOS, ICO per Windows) dall'SVG incluso nel sorgente.
Uso:  python packaging/genera_icone.py        (richiede PyQt6 e Pillow)"""
import os, re, sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QByteArray, QRectF, Qt
from PyQt6.QtGui import QGuiApplication, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer


def leggi_svg() -> str:
    sorgenti = [f for f in os.listdir(RADICE) if f.startswith("ZimbraViewer") and f.endswith(".py")]
    testo = open(os.path.join(RADICE, sorted(sorgenti)[-1]), encoding="utf-8").read()
    return re.search(r'ICON_SVG = """(.*?)"""', testo, re.S).group(1)


def main():
    app = QGuiApplication(sys.argv)
    rend = QSvgRenderer(QByteArray(leggi_svg().encode("utf-8")))
    img = QImage(1024, 1024, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    rend.render(p, QRectF(0, 0, 1024, 1024))
    p.end()
    png = os.path.join(RADICE, "zimbra_icon.png")
    img.save(png, "PNG")
    from PIL import Image
    im = Image.open(png)
    im.save(os.path.join(RADICE, "zimbra_icon.icns"))
    ico = os.path.join(RADICE, "zimbra_icon.ico")
    if not os.path.exists(ico):
        im.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Icone generate in", RADICE)
    del app


if __name__ == "__main__":
    main()
