# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the Krita2CSP layout outside Krita, for development checks.

    QT_QPA_PLATFORM=offscreen python3 dev/preview.py [dark|light] out.png

Krita's own dockers are replaced by simple placeholders here; the
Krita2CSP dockers are the real code running against dev/mock/krita.py.
"""

import configparser
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "mock"))
sys.path.insert(0, os.path.join(ROOT, "krita-resources", "pykrita"))

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPalette, QColor, QPainter, QConicalGradient, QBrush, QPen
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QLabel, QWidget,
                             QListWidget, QVBoxLayout, QGridLayout, QFrame)

theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
out = sys.argv[2] if len(sys.argv) > 2 else "preview.png"

app = QApplication(sys.argv)


def load_palette(path):
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    cp.read(path)

    def col(group, key):
        return QColor(*[int(x) for x in cp[group][key].split(",")])

    pal = QPalette()
    R = QPalette.ColorRole
    pal.setColor(R.Window, col("Colors:Window", "BackgroundNormal"))
    pal.setColor(R.WindowText, col("Colors:Window", "ForegroundNormal"))
    pal.setColor(R.Base, col("Colors:View", "BackgroundNormal"))
    pal.setColor(R.AlternateBase, col("Colors:View", "BackgroundAlternate"))
    pal.setColor(R.Text, col("Colors:View", "ForegroundNormal"))
    pal.setColor(R.Button, col("Colors:Button", "BackgroundNormal"))
    pal.setColor(R.ButtonText, col("Colors:Button", "ForegroundNormal"))
    pal.setColor(R.Highlight, col("Colors:Selection", "BackgroundNormal"))
    pal.setColor(R.HighlightedText, col("Colors:Selection", "ForegroundNormal"))
    pal.setColor(R.ToolTipBase, col("Colors:Tooltip", "BackgroundNormal"))
    pal.setColor(R.ToolTipText, col("Colors:Tooltip", "ForegroundNormal"))
    return pal


scheme = "Krita2CSP-Dark.colors" if theme == "dark" else "Krita2CSP-Light.colors"
app.setStyle("Fusion")
app.setPalette(load_palette(os.path.join(ROOT, "krita-resources", "color-schemes", scheme)))

import krita  # the mock
import krita2csp  # registers extension and docker factories
from krita2csp import layout
from krita2csp.state import controller

mw = QMainWindow()
mw.resize(1600, 940)
window = krita.Window(mw)
krita.Krita.instance().set_window(window)


class Canvas(QWidget):
    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(128, 128, 128))
        w, h = int(self.height() * 0.62), int(self.height() * 0.88)
        p.fillRect((self.width() - w) // 2, (self.height() - h) // 2, w, h, QColor(255, 255, 255))
        p.end()


mw.setCentralWidget(Canvas())


class ColorWheel(QWidget):
    """Placeholder for Krita's color selector (ring with a square)."""

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = min(self.width(), self.height()) - 16
        c = QPointF(self.width() / 2, self.height() / 2)
        grad = QConicalGradient(c, 0)
        for i in range(7):
            grad.setColorAt(i / 6, QColor.fromHsv((i * 60) % 360, 255, 255))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(c, s / 2, s / 2)
        p.setBrush(self.palette().color(QPalette.ColorRole.Window))
        p.drawEllipse(c, s / 2 - 14, s / 2 - 14)
        q = (s / 2 - 18) * 1.3
        p.fillRect(QRectF(c.x() - q / 2, c.y() - q / 2, q, q), QColor(200, 60, 60))
        p.end()


def placeholder(name, title, widget):
    d = QDockWidget(title)
    d.setObjectName(name)
    d.setWidget(widget)
    mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, d)
    return d


def text(t):
    lab = QLabel(t)
    lab.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    lab.setMargin(6)
    return lab


layers = QListWidget()
layers.addItems(["Line art", "Color", "Shading", "Paper"])
swatches = QWidget()
grid = QGridLayout(swatches)
for i in range(24):
    f = QFrame()
    f.setFixedSize(18, 18)
    f.setStyleSheet("background: %s" % QColor.fromHsv(i * 15, 160, 220).name())
    grid.addWidget(f, i // 8, i % 8)

placeholder("ToolBox", "Toolbox", text("(Krita toolbox, hidden by layout)"))
placeholder("PresetDocker", "Brush Presets", text("(hidden by layout)"))
placeholder("sharedtooldocker", "Tool Options", text("Brush Smoothing: Stabilizer\nDistance: 50\nDelay ..."))
placeholder("KisLayerBox", "Layers", layers)
placeholder("OverviewDocker", "Overview", text("(navigator preview)"))
placeholder("History", "Undo History", text("(history)"))
placeholder("PaletteDocker", "Palette", swatches)
placeholder("WideGamutColorSelector", "Wide Gamut Color Selector", ColorWheel())

app_k = krita.Krita.instance()
for f in app_k.factories:
    d = f.createDockWidget()
    mw.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, d)
for ext in app_k.extensions:
    ext.setup()
    ext.createActions(window)

mw.show()
missing = layout.apply_csp_layout(window)
print("missing dockers:", missing)

ctl = controller()
for d in mw.findChildren(QDockWidget):
    if hasattr(d, "canvasChanged"):
        d.canvasChanged(None)

# behavior checks
ctl.cycle("pen")
assert ctl.current_group == "pen", ctl.current_group
assert window.activeView().currentBrushPreset().name() == "d) Ink-3 Gpen"
ctl.cycle("pen")
assert ctl.current_group == "pencil", ctl.current_group
ctl.cycle("pen")
assert ctl.current_group == "pen"
ctl.cycle("brush")
ctl.cycle("brush")
assert ctl.current_group == "airbrush"
# switching tools inside "Krita" moves the palette along
app_k.action("KisToolSelectOutline").trigger()
assert ctl.current_group == "selection" and ctl.current_item == "KisToolSelectOutline"
# picking a preset elsewhere selects its group
window.activeView().activateResource(app_k.resources("preset")["a) Eraser Soft"])
assert ctl.current_group == "eraser" and ctl.current_item == "a) Eraser Soft"
ctl.activate_group(os.environ.get("PREVIEW_GROUP", "pen"))
window.activeView().setBrushSize(12.0)
# layout checks: CSP tabs exist, Krita's own toolbox and preset docker are hidden
for first, second in (("krita2csp_toolproperty", "sharedtooldocker"),
                      ("OverviewDocker", "History"),
                      ("WideGamutColorSelector", "PaletteDocker")):
    d = mw.findChild(QDockWidget, first)
    assert second in [x.objectName() for x in mw.tabifiedDockWidgets(d)], (first, second)
for hidden in ("ToolBox", "PresetDocker"):
    assert not mw.findChild(QDockWidget, hidden).isVisible(), hidden
print("behavior and layout checks passed")

app.processEvents()
mw.grab().save(out)
print("saved", out)
