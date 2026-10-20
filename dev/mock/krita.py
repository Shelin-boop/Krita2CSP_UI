# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal stand-in for Krita's `krita` Python module.

Only for development: it lets dev/preview.py run the Krita2CSP dockers
outside Krita (for example headless with QT_QPA_PLATFORM=offscreen) to
check layout and drawing. It mimics the parts of the Krita 6 API that the
plugin uses; it is not a full emulation.
"""

from PyQt6.QtCore import QObject, pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QAction, QImage, QPainter, QPen, QColor
from PyQt6.QtWidgets import QDockWidget

KNOWN_TOOLS = {
    "ZoomTool", "PanTool", "InteractionTool", "PathTool", "KritaTransform/KisToolMove",
    "KisToolTransform", "KisToolCrop", "KisToolSelectRectangular", "KisToolSelectElliptical",
    "KisToolSelectOutline", "KisToolSelectPolygonal", "KisToolSelectPath",
    "KisToolSelectMagnetic", "KisToolSelectContiguous", "KisToolSelectSimilar",
    "KritaSelected/KisToolColorSampler", "KritaShape/KisToolBrush", "KritaFill/KisToolFill",
    "KisToolEncloseAndFill", "KritaShape/KisToolLazyBrush", "KritaShape/KisToolSmartPatch",
    "KritaFill/KisToolGradient", "KritaShape/KisToolLine", "KritaShape/KisToolRectangle",
    "KritaShape/KisToolEllipse", "KisToolPolygon", "KisToolPolyline", "KisToolPath",
    "KisToolPencil", "KritaShape/KisToolKnife", "KisAssistantTool",
    "KritaShape/KisToolMultiBrush", "KritaShape/KisToolMeasure", "SvgTextTool",
    "KarbonCalligraphyTool",
}

PRESET_NAMES = [
    "a) Eraser Circle", "a) Eraser Soft", "a) Eraser Small", "b) Airbrush Soft",
    "b) Basic-3 Flow", "b) Basic-4 Flow Opacity", "b) Basic-5 Size Opacity",
    "c) Pencil-1 Hard", "c) Pencil-2", "c) Pencil-3 Large 4B", "c) Pencil-4 Soft",
    "c) Pencil-5 Tilted", "d) Ink-1 Precision", "d) Ink-2 Fineliner", "d) Ink-3 Gpen",
    "d) Ink-4 Pen Rough", "d) Ink-7 Brush Rough", "d) Ink-8 Sumi-e", "e) Marker Details",
    "f) Bristles-2 Flat Rough", "g) Dry Bristles", "h) Charcoal Pencil Thin",
    "i) Wet Bristles", "i) Wet Paint", "j) Watercolor Fringe", "j) Watercolor Texture",
    "j) Waterpaint Hard Edges", "j) Waterpaint Soft Edges", "k) Blender Basic",
    "k) Blender Blur", "k) Blender Smear", "k) Blender Textured Soft", "v) Clone Tool",
    "y) Screentone Pressure", "y) Screentones Regular", "y) Texture Noise",
    "y) Texture Spray", "z) Stamp Grass", "z) Stamp Leaves", "z) Stamp Shoujo Bubbles",
    "z) Stamp Sparkles",
]


def _thumb(name):
    img = QImage(64, 64, QImage.Format.Format_ARGB32)
    img.fill(QColor(255, 255, 255))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    seed = sum(map(ord, name))
    width = 2 + seed % 9
    color = QColor.fromHsv(seed * 37 % 360, 40 + seed % 120, 60)
    pen = QPen(color, width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(10, 50), QPointF(54, 14))
    p.end()
    return img


class Resource:
    def __init__(self, name):
        self._name = name
        self._image = _thumb(name)

    def name(self):
        return self._name

    def image(self):
        return self._image

    def type(self):
        return "preset"


class View(QObject):
    currentToolChanged = pyqtSignal(str)
    currentBrushPresetChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._preset = None
        self._size, self._opacity, self._flow = 12.0, 1.0, 1.0
        self._nopressure = False
        self.tool = ""

    def activateResource(self, res):
        self._preset = res
        self.currentBrushPresetChanged.emit()

    def currentBrushPreset(self):
        return self._preset

    def brushSize(self):
        return self._size

    def setBrushSize(self, v):
        self._size = v

    def paintingOpacity(self):
        return self._opacity

    def setPaintingOpacity(self, v):
        self._opacity = v

    def paintingFlow(self):
        return self._flow

    def setPaintingFlow(self, v):
        self._flow = v

    def disablePressure(self):
        return self._nopressure

    def setDisablePressure(self, v):
        self._nopressure = v


class Window(QObject):
    def __init__(self, main_window=None):
        super().__init__()
        self._mw = main_window
        self._view = View()

    def qwindow(self):
        return self._mw

    def activeView(self):
        return self._view

    def views(self):
        return [self._view]

    def createAction(self, action_id, text="", menu="tools/scripts"):
        a = QAction(text, self._mw)
        a.setObjectName(action_id)
        Krita.instance()._actions[action_id] = a
        return a


class Notifier(QObject):
    windowCreated = pyqtSignal()

    def setActive(self, value):
        pass


class Extension(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class DockWidget(QDockWidget):
    def __init__(self):
        super().__init__()

    def canvas(self):
        return None


class DockWidgetFactoryBase:
    class DockPosition:
        DockLeft = 4
        DockRight = 3

    def __init__(self, _id, pos):
        self._id, self._pos = _id, pos


class DockWidgetFactory(DockWidgetFactoryBase):
    def __init__(self, _id, pos, klass):
        super().__init__(_id, pos)
        self.klass = klass

    def createDockWidget(self):
        dock = self.klass()
        dock.setObjectName(self._id)
        return dock


class Krita(QObject):
    _instance = None

    def __init__(self):
        super().__init__()
        self._settings = {}
        self._actions = {}
        self._presets = {n: Resource(n) for n in PRESET_NAMES}
        self._window = None
        self._notifier = Notifier()
        self.extensions = []
        self.factories = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Krita()
        return cls._instance

    # settings
    def readSetting(self, group, name, default):
        return self._settings.get((group, name), default)

    def writeSetting(self, group, name, value):
        self._settings[(group, name)] = value

    # resources and actions
    def resources(self, rtype):
        return dict(self._presets) if rtype == "preset" else {}

    def action(self, name):
        if name in self._actions:
            return self._actions[name]
        if name not in KNOWN_TOOLS:
            return None
        a = QAction(name)
        a.setObjectName(name)

        def fire(_checked=False, n=name):
            view = self._window.activeView() if self._window else None
            if view is not None:
                view.tool = n
                view.currentToolChanged.emit(n)
        a.triggered.connect(fire)
        self._actions[name] = a
        return a

    # windows
    def set_window(self, window):
        self._window = window

    def activeWindow(self):
        return self._window

    def windows(self):
        return [self._window] if self._window else []

    def notifier(self):
        return self._notifier

    def addExtension(self, ext):
        self.extensions.append(ext)

    def addDockWidgetFactory(self, factory):
        self.factories.append(factory)
