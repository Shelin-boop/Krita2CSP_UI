# SPDX-License-Identifier: GPL-3.0-or-later
"""Arrange Krita's dockers like Clip Studio Paint's default Studio mode.

Left:   Tool | Sub Tool
             | Tool Property (tab: Krita Tool Options)
             | Brush Size
             | Color wheel (tab: Palette)
Right:  Navigator (tab: History)
        Layers

Krita saves the window state when it closes, so the layout only has to be
applied once. It can be applied again from Tools > Scripts.
"""

from .qtcompat import QDockWidget, LEFT_AREA, RIGHT_AREA, HORIZONTAL, VERTICAL

TOOLS = "krita2csp_tools"
SUBTOOL = "krita2csp_subtool"
PROPERTY = "krita2csp_toolproperty"
BRUSHSIZE = "krita2csp_brushsize"

# Krita 6 docker object names (from Krita 6.0.4.1 sources)
KRITA_TOOL_OPTIONS = "sharedtooldocker"
KRITA_LAYERS = "KisLayerBox"
KRITA_OVERVIEW = "OverviewDocker"
KRITA_HISTORY = "History"
KRITA_PALETTE = "PaletteDocker"
COLOR_CANDIDATES = ["WideGamutColorSelector", "ColorSelectorNg", "SmallColorSelector"]


def _docks(main_window):
    return {d.objectName(): d for d in main_window.findChildren(QDockWidget)}


def apply_csp_layout(window):
    """Rearrange the dockers of a Krita `Window`. Returns a list of the
    docker names that were missing, for diagnostics."""
    mw = window.qwindow()
    docks = _docks(mw)
    missing = []

    def get(name):
        d = docks.get(name)
        if d is None:
            missing.append(name)
        return d

    tools, sub, prop, size = get(TOOLS), get(SUBTOOL), get(PROPERTY), get(BRUSHSIZE)
    options = get(KRITA_TOOL_OPTIONS)
    layers, overview = get(KRITA_LAYERS), get(KRITA_OVERVIEW)
    history, palette = docks.get(KRITA_HISTORY), docks.get(KRITA_PALETTE)
    color = next((docks[n] for n in COLOR_CANDIDATES if n in docks), None)
    if color is None:
        missing.append("color selector")

    keep = [d for d in (tools, sub, prop, size, options, color, palette,
                        overview, history, layers) if d is not None]

    # Hide everything else, Krita's own toolbox and preset docker included.
    for d in docks.values():
        if d not in keep:
            d.hide()

    for d in keep:
        d.setFloating(False)
        mw.removeDockWidget(d)

    # Left side: split first, tabify last (Qt adds to a tab group otherwise).
    left = [d for d in (tools, sub) if d is not None]
    if left:
        mw.addDockWidget(LEFT_AREA, left[0])
    if tools is not None and sub is not None:
        mw.splitDockWidget(tools, sub, HORIZONTAL)
    column = sub or tools
    below = column
    for d in (prop, size, color):
        if d is not None and below is not None:
            mw.splitDockWidget(below, d, VERTICAL)
            below = d
    # A removed dock must be back in the window before it can be tabified.
    for first, second in ((prop, options), (color, palette)):
        if first is not None and second is not None:
            mw.addDockWidget(LEFT_AREA, second)
            mw.tabifyDockWidget(first, second)

    # Right side
    if overview is not None:
        mw.addDockWidget(RIGHT_AREA, overview)
    if overview is not None and layers is not None:
        mw.splitDockWidget(overview, layers, VERTICAL)
    elif layers is not None:
        mw.addDockWidget(RIGHT_AREA, layers)
    if overview is not None and history is not None:
        mw.addDockWidget(RIGHT_AREA, history)
        mw.tabifyDockWidget(overview, history)

    for d in keep:
        d.show()
    for d in (prop, color, overview):  # bring the CSP tab to the front
        if d is not None:
            d.raise_()

    # Sizes in pixels; Qt scales them to fit the window.
    try:
        if tools is not None and sub is not None:
            mw.resizeDocks([tools, sub], [48, 250], HORIZONTAL)
        col = [d for d in (sub, prop, size, color) if d is not None]
        mw.resizeDocks(col, [300, 210, 150, 230][:len(col)], VERTICAL)
        right = [d for d in (overview, layers) if d is not None]
        if right:
            mw.resizeDocks(right[:1], [290], HORIZONTAL)
            mw.resizeDocks(right, [220, 620][:len(right)], VERTICAL)
    except Exception:
        pass
    return missing
