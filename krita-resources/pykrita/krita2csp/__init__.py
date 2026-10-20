# SPDX-License-Identifier: GPL-3.0-or-later
"""Krita2CSP: a Clip Studio Paint style interface for Krita 6."""

from krita import Krita, Extension, DockWidgetFactory, DockWidgetFactoryBase

from . import catalog, layout
from .catalog import tr
from .dockers import ToolsDocker, SubToolDocker, ToolPropertyDocker, BrushSizeDocker
from .state import controller, SETTINGS_GROUP
from .qtcompat import QTimer

LAYOUT_VERSION = "1"  # bump to re-apply the layout once after an update


class Krita2CSPExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        notifier = Krita.instance().notifier()
        notifier.setActive(True)
        notifier.windowCreated.connect(self._on_window_created)

    def createActions(self, window):
        def add(action_id, text, slot, menu=""):
            action = window.createAction(action_id, text, menu)
            action.triggered.connect(slot)
            return action

        add("krita2csp_tool_pen", tr("CSP: Pen / Pencil"),
            lambda: controller().cycle("pen"))
        add("krita2csp_tool_brush", tr("CSP: Brush / Airbrush / Decoration"),
            lambda: controller().cycle("brush"))
        add("krita2csp_tool_eraser", tr("CSP: Eraser"),
            lambda: controller().cycle("eraser"))
        add("krita2csp_tool_blend", tr("CSP: Blend"),
            lambda: controller().cycle("blend"))
        add("krita2csp_apply_layout", tr("Apply CSP layout"),
            lambda: self._apply_layout(window), "tools/scripts")
        add("krita2csp_reset_groups", tr("Reset CSP brush groups"),
            lambda: controller().reset_groups(), "tools/scripts")

    # First start: arrange the dockers once. Krita restores them afterwards.
    def _on_window_created(self):
        app = Krita.instance()
        if app.readSetting(SETTINGS_GROUP, "layoutApplied", "") == LAYOUT_VERSION:
            return
        windows = app.windows()
        if not windows:
            return
        window = windows[-1]
        # wait until Krita has created and restored all dockers
        QTimer.singleShot(1500, lambda: self._first_run(window))

    def _first_run(self, window):
        self._apply_layout(window)
        Krita.instance().writeSetting(SETTINGS_GROUP, "layoutApplied", LAYOUT_VERSION)
        if controller().current_group == "":
            controller().current_group = "pen"
            controller().groupChanged.emit("pen")

    @staticmethod
    def _apply_layout(window):
        missing = layout.apply_csp_layout(window)
        if missing:
            print("Krita2CSP: dockers not found:", ", ".join(missing))


app = Krita.instance()
app.addExtension(Krita2CSPExtension(app))

try:
    _LEFT = DockWidgetFactoryBase.DockPosition.DockLeft  # Krita 6
except AttributeError:
    _LEFT = DockWidgetFactoryBase.DockLeft  # Krita 5
app.addDockWidgetFactory(DockWidgetFactory(layout.TOOLS, _LEFT, ToolsDocker))
app.addDockWidgetFactory(DockWidgetFactory(layout.SUBTOOL, _LEFT, SubToolDocker))
app.addDockWidgetFactory(DockWidgetFactory(layout.PROPERTY, _LEFT, ToolPropertyDocker))
app.addDockWidgetFactory(DockWidgetFactory(layout.BRUSHSIZE, _LEFT, BrushSizeDocker))
