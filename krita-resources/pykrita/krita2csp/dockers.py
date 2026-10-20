# SPDX-License-Identifier: GPL-3.0-or-later
"""CSP-style dockers: Tool, Sub Tool, Tool Property and Brush Size."""

import math

from krita import DockWidget

from . import catalog, icons
from .catalog import tr
from .state import controller, display_name
from .qtcompat import (Qt, QTimer, QSize, QRectF, QPointF, QWidget, QToolButton,
                       QButtonGroup, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
                       QListWidget, QListWidgetItem, QSlider, QSpinBox, QCheckBox,
                       QFrame, QSizePolicy, QIcon, QPixmap, QPainter, QPen, QColor,
                       QBrush, QFont, ALIGN_CENTER, ALIGN_LEFT, ALIGN_TOP, ALIGN_VCENTER,
                       USER_ROLE, NO_PEN, NO_BRUSH, ANTIALIAS, SLIDER_HORIZONTAL,
                       ROLE_WINDOW_TEXT, ROLE_HIGHLIGHT, SINGLE_SELECTION, FRAME_HLINE,
                       FRAME_SUNKEN, SIZE_EXPANDING, SIZE_PREFERRED, SIZE_FIXED,
                       TOOL_BUTTON_ICON_ONLY)

try:
    from PyQt6.QtCore import QEvent
    PALETTE_CHANGE = QEvent.Type.PaletteChange
except ImportError:
    from PyQt5.QtCore import QEvent
    PALETTE_CHANGE = QEvent.PaletteChange

# Shortcut hints shown in tooltips (set by install.sh, see README).
SHORTCUT_HINTS = {"pen": "P", "pencil": "P", "brush": "B", "airbrush": "B",
                  "decoration": "B", "eraser": "E", "blend": "J", "fill": "F",
                  "gradient": "G", "selection": "M", "autoselect": "W",
                  "eyedropper": "I", "move": "K", "operation": "O", "text": "T",
                  "hand": "H", "zoom": "/"}


def theme_colors(widget):
    pal = widget.palette()
    fg = pal.color(ROLE_WINDOW_TEXT)
    accent = pal.color(ROLE_HIGHLIGHT)
    return fg, accent


def group_icon(widget, gid):
    g = catalog.group(gid)
    fg, accent = theme_colors(widget)
    return icons.make_icon(g[2] if g else "", fg, accent)


def _hline():
    line = QFrame()
    line.setFrameShape(FRAME_HLINE)
    line.setFrameShadow(FRAME_SUNKEN)
    return line


# ---------------------------------------------------------------------------
# Tool palette
# ---------------------------------------------------------------------------

class ToolPalette(QWidget):
    BUTTON = 36
    SPACING = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(3, 3, 3, 3)
        self._grid.setSpacing(self.SPACING)
        self._buttons = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._columns = 0
        for entry in catalog.GROUPS:
            if entry == "-":
                continue
            gid, _kind, _icon, label, _items = entry
            btn = QToolButton(self)
            btn.setCheckable(True)
            btn.setAutoRaise(True)
            btn.setToolButtonStyle(TOOL_BUTTON_ICON_ONLY)
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(self.BUTTON, self.BUTTON)
            hint = SHORTCUT_HINTS.get(gid)
            btn.setToolTip(tr(label) + (" (%s)" % hint if hint else ""))
            btn.clicked.connect(lambda _checked=False, g=gid: controller().activate_group(g))
            self._group.addButton(btn)
            self._buttons[gid] = btn
        self.setSizePolicy(SIZE_PREFERRED, SIZE_PREFERRED)
        self._relayout(1)
        self.refresh_icons()
        controller().groupChanged.connect(self.on_group_changed)

    def refresh_icons(self):
        for gid, btn in self._buttons.items():
            btn.setIcon(group_icon(self, gid))

    def refresh_availability(self):
        ctl = controller()
        for gid, btn in self._buttons.items():
            btn.setEnabled(any(ctl.available(gid, k) for k, _ in ctl.items(gid)))

    def on_group_changed(self, gid):
        btn = self._buttons.get(gid)
        if btn is not None:
            btn.setChecked(True)

    def _relayout(self, columns):
        if columns == self._columns:
            return
        self._columns = columns
        while self._grid.count():
            self._grid.takeAt(0)
        row = col = 0
        for entry in catalog.GROUPS:
            if entry == "-":
                if col:
                    row, col = row + 1, 0
                self._grid.setRowMinimumHeight(row, 6)
                row += 1
                continue
            self._grid.addWidget(self._buttons[entry[0]], row, col)
            col += 1
            if col >= columns:
                row, col = row + 1, 0
        self._grid.setRowStretch(row + 1, 1)

    def resizeEvent(self, event):
        usable = max(self.BUTTON, self.width() - 6)
        self._relayout(max(1, usable // (self.BUTTON + self.SPACING)))
        super().resizeEvent(event)

    def changeEvent(self, event):
        if event.type() == PALETTE_CHANGE:
            icons.clear_cache()
            self.refresh_icons()
        super().changeEvent(event)

    def sizeHint(self):
        return QSize(self.BUTTON + 8, 400)

    def minimumSizeHint(self):
        return QSize(self.BUTTON + 8, self.BUTTON * 4)


class ToolsDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("Tool"))
        self.palette_widget = ToolPalette()
        self.setWidget(self.palette_widget)

    def canvasChanged(self, canvas):
        controller().attach_view(controller().view())
        self.palette_widget.refresh_availability()


# ---------------------------------------------------------------------------
# Sub Tool
# ---------------------------------------------------------------------------

class SubToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        head = QHBoxLayout()
        self._head_icon = QLabel()
        self._head_icon.setFixedSize(24, 24)
        self._head_text = QLabel()
        font = self._head_text.font()
        font.setBold(True)
        self._head_text.setFont(font)
        head.addWidget(self._head_icon)
        head.addWidget(self._head_text, 1)
        layout.addLayout(head)

        self._list = QListWidget()
        self._list.setSelectionMode(SINGLE_SELECTION)
        self._list.setIconSize(QSize(32, 32))
        self._list.setSpacing(1)
        self._list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list, 1)

        bar = QHBoxLayout()
        bar.setSpacing(2)
        self._add = self._small_button("add", tr("Add current brush"), self._on_add)
        self._remove = self._small_button("remove", tr("Remove from group"), self._on_remove)
        self._reset = QToolButton()
        self._reset.setText("↺")
        self._reset.setToolTip(tr("Restore default"))
        self._reset.setAutoRaise(True)
        self._reset.clicked.connect(self._on_reset)
        bar.addWidget(self._add)
        bar.addWidget(self._remove)
        bar.addStretch(1)
        bar.addWidget(self._reset)
        layout.addLayout(bar)

        ctl = controller()
        ctl.groupChanged.connect(self.rebuild)
        ctl.groupsEdited.connect(self.rebuild)
        self.rebuild()

    def _small_button(self, icon_name, tooltip, slot):
        btn = QToolButton()
        btn.setAutoRaise(True)
        btn.setIconSize(QSize(16, 16))
        btn.setToolTip(tooltip)
        btn.setProperty("krita2csp_icon", icon_name)
        btn.clicked.connect(slot)
        return btn

    def _refresh_small_icons(self):
        fg, accent = theme_colors(self)
        for btn in (self._add, self._remove):
            btn.setIcon(icons.make_icon(btn.property("krita2csp_icon"), fg, accent))

    def rebuild(self, *_args):
        ctl = controller()
        gid = ctl.current_group
        g = catalog.group(gid)
        self._refresh_small_icons()
        self._list.clear()
        if g is None:
            self._head_icon.clear()
            self._head_text.setText(tr("Open a canvas to start"))
            for btn in (self._add, self._remove, self._reset):
                btn.setVisible(False)
            return
        icon = group_icon(self, gid)
        self._head_icon.setPixmap(icon.pixmap(24, 24))
        self._head_text.setText(tr(g[3]))
        is_brush = g[1] == "brush"
        for btn in (self._add, self._remove, self._reset):
            btn.setVisible(is_brush)

        presets = ctl.presets() if is_brush else {}
        for key, label in ctl.items(gid):
            if is_brush:
                res = ctl.find_preset(key, presets)
                if res is None:
                    continue
                item_icon = QIcon(QPixmap.fromImage(res.image())) if res.image() is not None else icon
            else:
                if ctl.tool_action(key) is None:
                    continue
                item_icon = icon
            item = QListWidgetItem(item_icon, display_name(label))
            item.setData(USER_ROLE, key)
            item.setToolTip(key)
            self._list.addItem(item)
            if key == ctl.current_item:
                item.setSelected(True)
                self._list.setCurrentItem(item)

    def _on_item_clicked(self, item):
        ctl = controller()
        if ctl.current_group:
            ctl.activate_item(ctl.current_group, item.data(USER_ROLE))

    def _on_add(self):
        ctl = controller()
        view = ctl.view()
        if view is None or not ctl.current_group:
            return
        preset = view.currentBrushPreset()
        if preset is not None:
            ctl.add_preset_to_group(ctl.current_group, preset.name())

    def _on_remove(self):
        ctl = controller()
        item = self._list.currentItem()
        if item is not None and ctl.current_group:
            ctl.remove_from_group(ctl.current_group, item.data(USER_ROLE))

    def _on_reset(self):
        ctl = controller()
        if ctl.current_group:
            ctl.reset_group(ctl.current_group)

    def changeEvent(self, event):
        if event.type() == PALETTE_CHANGE:
            icons.clear_cache()
            self.rebuild()
        super().changeEvent(event)


class SubToolDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("Sub Tool"))
        self.panel = SubToolPanel()
        self.setWidget(self.panel)

    def canvasChanged(self, canvas):
        controller().attach_view(controller().view())
        self.panel.rebuild()


# ---------------------------------------------------------------------------
# Tool Property
# ---------------------------------------------------------------------------

SIZE_MIN = 0.5
SIZE_MAX = 1000.0
_STEPS = 1000


def size_to_slider(size):
    size = min(max(size, SIZE_MIN), SIZE_MAX)
    return int(round(_STEPS * math.log(size / SIZE_MIN) / math.log(SIZE_MAX / SIZE_MIN)))


def slider_to_size(value):
    return SIZE_MIN * (SIZE_MAX / SIZE_MIN) ** (value / float(_STEPS))


class _Row(QWidget):
    """Label, slider and spin box in one row."""

    def __init__(self, label, minimum, maximum, suffix, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(6)
        layout.setVerticalSpacing(0)
        self.label = QLabel(label)
        self.slider = QSlider(SLIDER_HORIZONTAL)
        self.spin = QSpinBox()
        self.spin.setRange(minimum, maximum)
        self.spin.setSuffix(suffix)
        self.spin.setFixedWidth(76)
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.slider, 1, 0)
        layout.addWidget(self.spin, 1, 1)

    def busy(self):
        return self.slider.isSliderDown() or self.spin.hasFocus()


class ToolPropertyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)
        layout.setAlignment(ALIGN_TOP)

        self._title = QLabel()
        font = self._title.font()
        font.setBold(True)
        self._title.setFont(font)
        layout.addWidget(self._title)
        layout.addWidget(_hline())

        self.size = _Row(tr("Brush size"), 1, int(SIZE_MAX), " px")
        self.size.slider.setRange(0, _STEPS)
        self.opacity = _Row(tr("Opacity"), 0, 100, " %")
        self.opacity.slider.setRange(0, 100)
        self.density = _Row(tr("Density"), 1, 100, " %")
        self.density.slider.setRange(1, 100)
        self.pressure = QCheckBox(tr("Use pen pressure"))
        for w in (self.size, self.opacity, self.density, self.pressure):
            layout.addWidget(w)

        self.size.slider.valueChanged.connect(self._size_slider)
        self.size.spin.valueChanged.connect(self._size_spin)
        self.opacity.slider.valueChanged.connect(self.opacity.spin.setValue)
        self.opacity.spin.valueChanged.connect(self.opacity.slider.setValue)
        self.opacity.spin.valueChanged.connect(self._opacity_changed)
        self.density.slider.valueChanged.connect(self.density.spin.setValue)
        self.density.spin.valueChanged.connect(self.density.slider.setValue)
        self.density.spin.valueChanged.connect(self._density_changed)
        self.pressure.toggled.connect(self._pressure_changed)

        self._updating = False
        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self.sync_from_krita)
        controller().groupChanged.connect(self._update_title)
        self._update_title()

    # Krita -> panel
    def sync_from_krita(self):
        view = controller().view()
        self.setEnabled(view is not None)
        if view is None:
            return
        self._updating = True
        try:
            if not self.size.busy():
                size = view.brushSize()
                self.size.slider.setValue(size_to_slider(size))
                self.size.spin.setValue(int(round(size)))
            if not self.opacity.busy():
                self.opacity.spin.setValue(int(round(view.paintingOpacity() * 100)))
            if not self.density.busy():
                self.density.spin.setValue(int(round(view.paintingFlow() * 100)))
            self.pressure.setChecked(not view.disablePressure())
        finally:
            self._updating = False

    def _update_title(self, *_args):
        ctl = controller()
        label = ctl.current_item
        for key, text in ctl.items(ctl.current_group):
            if key == ctl.current_item:
                label = display_name(text)
                break
        self._title.setText(label or tr("Tool Property"))

    # panel -> Krita
    def _size_slider(self, value):
        size = slider_to_size(value)
        if not self._updating:
            self.size.spin.blockSignals(True)
            self.size.spin.setValue(int(round(size)))
            self.size.spin.blockSignals(False)
            self._apply(lambda v: v.setBrushSize(size))

    def _size_spin(self, value):
        if not self._updating:
            self.size.slider.blockSignals(True)
            self.size.slider.setValue(size_to_slider(value))
            self.size.slider.blockSignals(False)
            self._apply(lambda v: v.setBrushSize(float(value)))

    def _opacity_changed(self, value):
        if not self._updating:
            self._apply(lambda v: v.setPaintingOpacity(value / 100.0))

    def _density_changed(self, value):
        if not self._updating:
            self._apply(lambda v: v.setPaintingFlow(value / 100.0))

    def _pressure_changed(self, checked):
        if not self._updating:
            self._apply(lambda v: v.setDisablePressure(not checked))

    def _apply(self, fn):
        view = controller().view()
        if view is not None:
            fn(view)

    def showEvent(self, event):
        self._timer.start()
        self.sync_from_krita()
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)


class ToolPropertyDocker(DockWidget):
    """For brush groups this tab shows size, opacity and so on. For other
    tools (selection, fill, ...) Krita's Tool Options tab is brought to the
    front instead, so the settings of the current tool are always visible,
    as in CSP's Tool Property palette."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("Tool Property"))
        self.panel = ToolPropertyPanel()
        self.setWidget(self.panel)
        controller().groupChanged.connect(self._front_tab)

    def _front_tab(self, gid):
        g = catalog.group(gid)
        mw = self.parentWidget()
        if g is None or mw is None or not hasattr(mw, "tabifiedDockWidgets"):
            return
        options = next((d for d in mw.tabifiedDockWidgets(self)
                        if d.objectName() == "sharedtooldocker"), None)
        if options is None:
            return
        (self if g[1] == "brush" else options).raise_()

    def canvasChanged(self, canvas):
        self.panel.sync_from_krita()


# ---------------------------------------------------------------------------
# Brush Size
# ---------------------------------------------------------------------------

BRUSH_SIZES = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 12, 15, 17, 20, 25, 30, 40,
               50, 60, 70, 80, 100, 120, 150, 200, 250, 300, 400, 500]


class SizeButton(QToolButton):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.brush_size = size
        self.setCheckable(True)
        self.setAutoRaise(True)
        self.setFixedSize(36, 38)
        self.setToolTip("%g px" % size)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(ANTIALIAS, True)
        fg, accent = theme_colors(self)
        color = accent if self.isChecked() else fg
        # dot diameter grows with the logarithm of the size
        t = math.log(self.brush_size) / math.log(BRUSH_SIZES[-1])
        d = 2.0 + t * 16.0
        p.setPen(NO_PEN)
        p.setBrush(QBrush(color))
        p.drawEllipse(QPointF(self.width() / 2.0, 14.0), d / 2.0, d / 2.0)
        p.setPen(QPen(fg))
        font = QFont(self.font())
        font.setPointSizeF(max(6.5, font.pointSizeF() * 0.75))
        p.setFont(font)
        p.drawText(QRectF(0, 25, self.width(), 12), ALIGN_CENTER, "%g" % self.brush_size)
        p.end()


class BrushSizePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(3, 3, 3, 3)
        self._grid.setSpacing(1)
        self._buttons = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for size in BRUSH_SIZES:
            btn = SizeButton(size, self)
            btn.clicked.connect(lambda _c=False, s=size: self._set_size(s))
            self._group.addButton(btn)
            self._buttons.append(btn)
        self._columns = 0
        self._relayout(5)
        self._timer = QTimer(self)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self.sync_from_krita)

    def _relayout(self, columns):
        if columns == self._columns:
            return
        self._columns = columns
        while self._grid.count():
            self._grid.takeAt(0)
        for i, btn in enumerate(self._buttons):
            self._grid.addWidget(btn, i // columns, i % columns)
        self._grid.setRowStretch(len(self._buttons) // columns + 1, 1)

    def resizeEvent(self, event):
        self._relayout(max(1, (self.width() - 6) // 37))
        super().resizeEvent(event)

    def _set_size(self, size):
        view = controller().view()
        if view is not None:
            view.setBrushSize(float(size))

    def sync_from_krita(self):
        view = controller().view()
        self.setEnabled(view is not None)
        if view is None:
            return
        current = view.brushSize()
        best = min(self._buttons, key=lambda b: abs(math.log(b.brush_size) - math.log(max(current, 0.1))))
        exact = abs(best.brush_size - current) < 0.01
        self._group.setExclusive(False)
        for btn in self._buttons:
            btn.setChecked(btn is best and exact)
        self._group.setExclusive(True)

    def showEvent(self, event):
        self._timer.start()
        self.sync_from_krita()
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def sizeHint(self):
        return QSize(6 * 37 + 6, 120)


class BrushSizeDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("Brush Size"))
        self.panel = BrushSizePanel()
        self.setWidget(self.panel)

    def canvasChanged(self, canvas):
        self.panel.sync_from_krita()
