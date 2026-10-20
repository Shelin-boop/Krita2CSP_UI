# SPDX-License-Identifier: GPL-3.0-or-later
"""The CSP-style tool palette and which Krita tools or brush presets
belong to each entry.

Two kinds of entries:

* "brush": a group of Krita brush presets used with Krita's freehand
  brush tool (Pen, Pencil, Brush, ...). Users can add and remove presets.
* "tool": a group of Krita tools (Selection, Figure, ...), each item is a
  Krita tool action ID.

Preset names refer to Krita's bundled default presets. Missing presets
are skipped at runtime, so a renamed or deleted preset never breaks the
palette.
"""

from .qtcompat import QLocale

BRUSH_TOOL = "KritaShape/KisToolBrush"

# (group id, kind, icon id, label, items)
# items: list of (key, display label). For "brush" the key is the Krita
# preset name, for "tool" the key is the Krita tool action ID.
GROUPS = [
    ("zoom", "tool", "zoom", "Zoom", [
        ("ZoomTool", "Zoom"),
    ]),
    ("hand", "tool", "hand", "Hand", [
        ("PanTool", "Hand"),
    ]),
    ("operation", "tool", "operation", "Operation", [
        ("InteractionTool", "Object (vector shapes)"),
        ("PathTool", "Edit shapes"),
    ]),
    ("move", "tool", "move", "Move layer", [
        ("KritaTransform/KisToolMove", "Move layer"),
        ("KisToolTransform", "Transform"),
        ("KisToolCrop", "Crop"),
    ]),
    "-",
    ("selection", "tool", "selection", "Selection area", [
        ("KisToolSelectRectangular", "Rectangle"),
        ("KisToolSelectElliptical", "Ellipse"),
        ("KisToolSelectOutline", "Lasso"),
        ("KisToolSelectPolygonal", "Polyline"),
        ("KisToolSelectPath", "Bezier"),
        ("KisToolSelectMagnetic", "Magnetic"),
    ]),
    ("autoselect", "tool", "autoselect", "Auto select", [
        ("KisToolSelectContiguous", "Contiguous area"),
        ("KisToolSelectSimilar", "Similar color"),
    ]),
    ("eyedropper", "tool", "eyedropper", "Eyedropper", [
        ("KritaSelected/KisToolColorSampler", "Eyedropper"),
    ]),
    "-",
    ("pen", "brush", "pen", "Pen", [
        ("d) Ink-3 Gpen", "G-pen"),
        ("d) Ink-1 Precision", "Mapping pen"),
        ("d) Ink-2 Fineliner", "Fineliner"),
        ("d) Ink-4 Pen Rough", "Rough pen"),
        ("e) Marker Details", "Marker"),
        ("b) Basic-5 Size Opacity", "Round pen"),
    ]),
    ("pencil", "brush", "pencil", "Pencil", [
        ("c) Pencil-2", "Pencil"),
        ("c) Pencil-1 Hard", "Hard pencil"),
        ("c) Pencil-4 Soft", "Soft pencil"),
        ("c) Pencil-3 Large 4B", "4B pencil"),
        ("c) Pencil-5 Tilted", "Tilt pencil"),
        ("h) Charcoal Pencil Thin", "Charcoal pencil"),
    ]),
    ("brush", "brush", "brush", "Brush", [
        ("j) Watercolor Texture", "Watercolor"),
        ("j) Waterpaint Soft Edges", "Soft watercolor"),
        ("j) Waterpaint Hard Edges", "Hard-edge watercolor"),
        ("j) Watercolor Fringe", "Watercolor fringe"),
        ("i) Wet Paint", "Wet paint"),
        ("i) Wet Bristles", "Wet bristles"),
        ("f) Bristles-2 Flat Rough", "Flat brush"),
        ("d) Ink-7 Brush Rough", "Ink brush"),
        ("d) Ink-8 Sumi-e", "Sumi-e"),
        ("g) Dry Bristles", "Dry brush"),
    ]),
    ("airbrush", "brush", "airbrush", "Airbrush", [
        ("b) Airbrush Soft", "Soft airbrush"),
        ("b) Basic-3 Flow", "Soft round"),
        ("b) Basic-4 Flow Opacity", "Soft round (opacity)"),
        ("y) Texture Spray", "Spray"),
    ]),
    ("decoration", "brush", "decoration", "Decoration", [
        ("y) Screentones Regular", "Screentone"),
        ("y) Screentone Pressure", "Screentone (pressure)"),
        ("z) Stamp Sparkles", "Sparkles"),
        ("z) Stamp Shoujo Bubbles", "Bubbles"),
        ("z) Stamp Leaves", "Leaves"),
        ("z) Stamp Grass", "Grass"),
        ("y) Texture Noise", "Noise"),
    ]),
    ("eraser", "brush", "eraser", "Eraser", [
        ("a) Eraser Circle", "Hard eraser"),
        ("a) Eraser Soft", "Soft eraser"),
        ("a) Eraser Small", "Small eraser"),
    ]),
    ("blend", "brush", "blend", "Blend", [
        ("k) Blender Basic", "Blend"),
        ("k) Blender Blur", "Blur"),
        ("k) Blender Smear", "Smudge"),
        ("k) Blender Textured Soft", "Textured blend"),
        ("v) Clone Tool", "Copy stamp"),
    ]),
    "-",
    ("fill", "tool", "fill", "Fill", [
        ("KritaFill/KisToolFill", "Fill"),
        ("KisToolEncloseAndFill", "Enclose and fill"),
        ("KritaShape/KisToolLazyBrush", "Colorize mask"),
        ("KritaShape/KisToolSmartPatch", "Smart patch"),
    ]),
    ("gradient", "tool", "gradient", "Gradient", [
        ("KritaFill/KisToolGradient", "Gradient"),
    ]),
    ("figure", "tool", "figure", "Figure", [
        ("KritaShape/KisToolLine", "Straight line"),
        ("KritaShape/KisToolRectangle", "Rectangle"),
        ("KritaShape/KisToolEllipse", "Ellipse"),
        ("KisToolPolygon", "Polygon"),
        ("KisToolPolyline", "Polyline"),
        ("KisToolPath", "Curve (Bezier)"),
        ("KisToolPencil", "Freehand path"),
    ]),
    ("frame", "tool", "frame", "Frame border", [
        ("KritaShape/KisToolKnife", "Cut panels (vector layer)"),
        ("KritaShape/KisToolRectangle", "Rectangle frame"),
    ]),
    ("ruler", "tool", "ruler", "Ruler", [
        ("KisAssistantTool", "Assistants (perspective, ...)"),
        ("KritaShape/KisToolMultiBrush", "Symmetry"),
        ("KritaShape/KisToolMeasure", "Measure"),
    ]),
    "-",
    ("text", "tool", "text", "Text", [
        ("SvgTextTool", "Text"),
    ]),
    ("correct", "tool", "correct", "Correct line", [
        ("PathTool", "Edit vector lines"),
        ("KarbonCalligraphyTool", "Calligraphy"),
    ]),
]

# Shortcut cycles, as in CSP: pressing the key again moves to the next
# tool that shares the key.
CYCLES = {
    "pen": ["pen", "pencil"],
    "brush": ["brush", "airbrush", "decoration"],
    "eraser": ["eraser"],
    "blend": ["blend"],
}


def groups():
    """All entries without separators."""
    return [g for g in GROUPS if g != "-"]


def group(gid):
    for g in groups():
        if g[0] == gid:
            return g
    return None


# ---------------------------------------------------------------------------
# German labels. Krita follows the system language; when it is German the
# palette labels are German as well. Plain German, not CSP's exact wording.
# ---------------------------------------------------------------------------
_DE = {
    "Zoom": "Zoom", "Hand": "Hand", "Operation": "Objekt",
    "Object (vector shapes)": "Objekt (Vektorformen)", "Edit shapes": "Formen bearbeiten",
    "Move layer": "Ebene verschieben", "Transform": "Transformieren", "Crop": "Zuschneiden",
    "Selection area": "Auswahlbereich", "Rectangle": "Rechteck", "Ellipse": "Ellipse",
    "Lasso": "Lasso", "Polyline": "Polylinie", "Bezier": "Bézier", "Magnetic": "Magnetisch",
    "Auto select": "Automatische Auswahl", "Contiguous area": "Zusammenhängender Bereich",
    "Similar color": "Ähnliche Farbe", "Eyedropper": "Pipette",
    "Pen": "Stift", "Pencil": "Bleistift", "Brush": "Pinsel", "Airbrush": "Airbrush",
    "Decoration": "Dekoration", "Eraser": "Radierer", "Blend": "Verwischen",
    "Fill": "Füllen", "Enclose and fill": "Umschließen und füllen",
    "Colorize mask": "Kolorierungsmaske", "Smart patch": "Smart Patch",
    "Gradient": "Verlauf", "Figure": "Figur", "Straight line": "Gerade Linie",
    "Polygon": "Polygon", "Curve (Bezier)": "Kurve (Bézier)", "Freehand path": "Freihandpfad",
    "Frame border": "Rahmen", "Cut panels (vector layer)": "Panels schneiden (Vektorebene)",
    "Rectangle frame": "Rechteckrahmen", "Ruler": "Lineal",
    "Assistants (perspective, ...)": "Hilfslinien (Perspektive, ...)",
    "Symmetry": "Symmetrie", "Measure": "Messen", "Text": "Text",
    "Correct line": "Linie korrigieren", "Edit vector lines": "Vektorlinien bearbeiten",
    "Calligraphy": "Kalligrafie",
    # brush presets
    "G-pen": "G-Feder", "Mapping pen": "Kartografenfeder", "Fineliner": "Fineliner",
    "Rough pen": "Rauer Stift", "Marker": "Marker", "Round pen": "Runder Stift",
    "Hard pencil": "Harter Bleistift", "Soft pencil": "Weicher Bleistift",
    "4B pencil": "4B-Bleistift", "Tilt pencil": "Neigungs-Bleistift",
    "Charcoal pencil": "Kohlestift", "Watercolor": "Aquarell",
    "Soft watercolor": "Weiches Aquarell", "Hard-edge watercolor": "Aquarell mit Rand",
    "Watercolor fringe": "Aquarell-Saum", "Wet paint": "Nasse Farbe",
    "Wet bristles": "Nasse Borsten", "Flat brush": "Flachpinsel", "Ink brush": "Tuschepinsel",
    "Sumi-e": "Sumi-e", "Dry brush": "Trockenpinsel", "Soft airbrush": "Weicher Airbrush",
    "Soft round": "Weich rund", "Soft round (opacity)": "Weich rund (Deckkraft)",
    "Spray": "Spray", "Screentone": "Raster", "Screentone (pressure)": "Raster (Druck)",
    "Sparkles": "Funkeln", "Bubbles": "Blasen", "Leaves": "Blätter", "Grass": "Gras",
    "Noise": "Rauschen", "Hard eraser": "Harter Radierer", "Soft eraser": "Weicher Radierer",
    "Small eraser": "Kleiner Radierer", "Blur": "Weichzeichnen", "Smudge": "Wischen",
    "Textured blend": "Strukturiert verwischen", "Copy stamp": "Kopierstempel",
    # docker texts
    "Tool": "Werkzeug", "Sub Tool": "Unterwerkzeug", "Tool Property": "Werkzeugeigenschaft",
    "Brush Size": "Pinselgröße", "Brush size": "Pinselgröße", "Opacity": "Deckkraft",
    "Density": "Dichte", "Use pen pressure": "Stiftdruck verwenden",
    "Add current brush": "Aktuellen Pinsel hinzufügen",
    "Remove from group": "Aus Gruppe entfernen", "Open a canvas to start": "Leinwand öffnen, um zu beginnen",
    "(not available in this Krita version)": "(in dieser Krita-Version nicht verfügbar)",
    "Apply CSP layout": "CSP-Layout anwenden",
    "Reset CSP brush groups": "CSP-Pinselgruppen zurücksetzen",
    "CSP: Pen / Pencil": "CSP: Stift / Bleistift",
    "CSP: Brush / Airbrush / Decoration": "CSP: Pinsel / Airbrush / Dekoration",
    "CSP: Eraser": "CSP: Radierer", "CSP: Blend": "CSP: Verwischen",
    "Restore default": "Standard wiederherstellen",
}


def _is_german():
    try:
        return QLocale().name().lower().startswith("de")
    except Exception:
        return False


_GERMAN = _is_german()


def tr(text):
    if _GERMAN:
        return _DE.get(text, text)
    return text
