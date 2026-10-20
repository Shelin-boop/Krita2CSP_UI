# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared state between the CSP-style dockers and shortcut actions.

Keeps track of the active palette entry (Pen, Pencil, Selection, ...),
remembers the last used sub tool per entry like CSP does, and keeps the
palette in sync when the user switches tools inside Krita.
"""

import json
import re
import time

from krita import Krita

from . import catalog
from .qtcompat import QObject, pyqtSignal

SETTINGS_GROUP = "krita2csp"


def _norm(name):
    return re.sub(r"[\s_]+", " ", name or "").strip().lower()


def _app():
    return Krita.instance()


def _read(key, default=""):
    try:
        return _app().readSetting(SETTINGS_GROUP, key, default)
    except Exception:
        return default


def _write(key, value):
    try:
        _app().writeSetting(SETTINGS_GROUP, key, value)
    except Exception:
        pass


class Controller(QObject):
    """Single shared instance, see `controller()`."""

    # emitted with the group id when the active palette entry changes
    groupChanged = pyqtSignal(str)
    # emitted when the items of a brush group were edited
    groupsEdited = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_group = ""
        self.current_item = ""
        self._last = self._load_json("lastItems", {})
        self._custom = self._load_json("brushGroups", {})
        self._view = None
        self._presets = None
        self._presets_time = 0.0

    # -- persistence ---------------------------------------------------------

    @staticmethod
    def _load_json(key, default):
        try:
            value = json.loads(_read(key, ""))
            return value if isinstance(value, dict) else default
        except (ValueError, TypeError):
            return default

    def _save(self):
        _write("lastItems", json.dumps(self._last))
        _write("brushGroups", json.dumps(self._custom))

    # -- catalog with user changes ---------------------------------------------

    def items(self, gid):
        """List of (key, label) for a group, including user changes."""
        g = catalog.group(gid)
        if g is None:
            return []
        if g[1] == "brush" and gid in self._custom:
            defaults = {k: label for k, label in g[4]}
            return [(k, defaults.get(k, _strip_prefix(k))) for k in self._custom[gid]]
        return list(g[4])

    def add_preset_to_group(self, gid, preset_name):
        keys = [k for k, _ in self.items(gid)]
        if preset_name and _norm(preset_name) not in {_norm(k) for k in keys}:
            keys.append(preset_name)
            self._custom[gid] = keys
            self._save()
            self.groupsEdited.emit()

    def remove_from_group(self, gid, key):
        keys = [k for k, _ in self.items(gid) if k != key]
        self._custom[gid] = keys
        self._save()
        self.groupsEdited.emit()

    def reset_group(self, gid):
        self._custom.pop(gid, None)
        self._save()
        self.groupsEdited.emit()

    def reset_groups(self):
        self._custom = {}
        self._save()
        self.groupsEdited.emit()

    # -- Krita lookups ---------------------------------------------------------

    def view(self):
        win = _app().activeWindow()
        return win.activeView() if win else None

    def presets(self):
        """Krita's brush presets by name, cached for a few seconds because
        building the dictionary is not free and the dockers ask often."""
        now = time.monotonic()
        if self._presets is None or now - self._presets_time > 5.0:
            try:
                self._presets = _app().resources("preset") or {}
            except Exception:
                self._presets = {}
            self._presets_time = now
        return self._presets

    def find_preset(self, name, presets=None):
        presets = presets if presets is not None else self.presets()
        if name in presets:
            return presets[name]
        wanted = _norm(name)
        for key, res in presets.items():
            if _norm(key) == wanted:
                return res
        return None

    @staticmethod
    def tool_action(tool_id):
        try:
            return _app().action(tool_id)
        except Exception:
            return None

    def available(self, gid, key):
        g = catalog.group(gid)
        if g is None:
            return False
        if g[1] == "brush":
            return self.find_preset(key) is not None
        return self.tool_action(key) is not None

    # -- activation ------------------------------------------------------------

    def activate_group(self, gid):
        """Select a palette entry with its last used sub tool."""
        items = [k for k, _ in self.items(gid) if self.available(gid, k)]
        if not items:
            self._set_current(gid, "")
            return
        key = self._last.get(gid)
        if key not in items:
            key = items[0]
        self.activate_item(gid, key)

    def activate_item(self, gid, key):
        g = catalog.group(gid)
        if g is None:
            return
        if g[1] == "brush":
            res = self.find_preset(key)
            action = self.tool_action(catalog.BRUSH_TOOL)
            if action is not None:
                action.trigger()
            view = self.view()
            if view is not None and res is not None:
                view.activateResource(res)
        else:
            action = self.tool_action(key)
            if action is not None:
                action.trigger()
        self._last[gid] = key
        self._save()
        self._set_current(gid, key)

    def cycle(self, first_gid):
        """CSP behavior: the same shortcut steps through related tools."""
        ring = catalog.CYCLES.get(first_gid, [first_gid])
        if self.current_group in ring:
            nxt = ring[(ring.index(self.current_group) + 1) % len(ring)]
        else:
            nxt = ring[0]
        self.activate_group(nxt)

    def _set_current(self, gid, key):
        changed = (gid != self.current_group) or (key != self.current_item)
        self.current_group, self.current_item = gid, key
        if changed:
            self.groupChanged.emit(gid)

    # -- follow changes made in Krita itself ------------------------------------

    def attach_view(self, view):
        if view is self._view:
            return
        self._disconnect_view()
        self._view = view
        if view is None:
            return
        for sig, slot in (("currentToolChanged", self._on_tool_changed),
                          ("currentBrushPresetChanged", self._on_preset_changed)):
            signal = getattr(view, sig, None)
            if signal is not None:
                try:
                    signal.connect(slot)
                except Exception:
                    pass
        self._on_preset_changed()

    def _disconnect_view(self):
        view = self._view
        if view is None:
            return
        for sig, slot in (("currentToolChanged", self._on_tool_changed),
                          ("currentBrushPresetChanged", self._on_preset_changed)):
            signal = getattr(view, sig, None)
            if signal is not None:
                try:
                    signal.disconnect(slot)
                except Exception:
                    pass
        self._view = None

    def _on_tool_changed(self, tool_id):
        if tool_id == catalog.BRUSH_TOOL:
            self._on_preset_changed()
            return
        if self.current_group:
            g = catalog.group(self.current_group)
            if g and g[1] == "tool" and tool_id in [k for k, _ in g[4]]:
                self._set_current(self.current_group, tool_id)
                return
        for g in catalog.groups():
            if g[1] == "tool" and tool_id in [k for k, _ in g[4]]:
                self._set_current(g[0], tool_id)
                return

    def _on_preset_changed(self):
        view = self._view or self.view()
        if view is None:
            return
        try:
            preset = view.currentBrushPreset()
            name = preset.name() if preset else ""
        except Exception:
            return
        gid = self.group_of_preset(name)
        if gid:
            key = self._match_key(gid, name)
            self._last[gid] = key
            self._set_current(gid, key)
        elif self.current_group and (catalog.group(self.current_group) or ("", ""))[1] == "brush":
            # a preset outside the CSP groups, chosen in Krita's own preset docker
            self._set_current(self.current_group, name)

    def _match_key(self, gid, name):
        for key, _ in self.items(gid):
            if _norm(key) == _norm(name):
                return key
        return name

    def group_of_preset(self, name):
        wanted = _norm(name)
        if not wanted:
            return ""
        # prefer the current group if the preset belongs to several groups
        order = [self.current_group] + [g[0] for g in catalog.groups()]
        for gid in order:
            g = catalog.group(gid)
            if g and g[1] == "brush" and wanted in {_norm(k) for k, _ in self.items(gid)}:
                return gid
        return ""


def _strip_prefix(name):
    """'d) Ink-3 Gpen' -> 'Ink-3 Gpen'"""
    return re.sub(r"^[a-z]\)\s*", "", name or "")


def display_name(label_or_key):
    return catalog.tr(label_or_key)


_controller = None


def controller():
    global _controller
    if _controller is None:
        _controller = Controller()
    return _controller
