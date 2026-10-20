# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt imports that work in Krita 6 (PyQt6) and Krita 5.3 (PyQt5).

Krita 6 is the target. The PyQt5 branch is a fallback so the plugin
does not crash if someone installs it into Krita 5.3.
"""

try:
    from PyQt6.QtCore import (Qt, QTimer, QSize, QRectF, QPointF, QObject,
                              QLocale, pyqtSignal)
    from PyQt6.QtGui import (QIcon, QPixmap, QPainter, QPen, QColor, QBrush,
                             QPainterPath, QPalette, QFont, QLinearGradient,
                             QImage, QAction)
    from PyQt6.QtWidgets import (QWidget, QDockWidget, QToolButton, QButtonGroup,
                                 QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
                                 QListWidget, QListWidgetItem, QSlider, QSpinBox,
                                 QCheckBox, QFrame, QSizePolicy, QAbstractItemView,
                                 QScrollArea, QApplication, QMainWindow)
    QT6 = True
except ImportError:  # Krita 5.x
    from PyQt5.QtCore import (Qt, QTimer, QSize, QRectF, QPointF, QObject,
                              QLocale, pyqtSignal)
    from PyQt5.QtGui import (QIcon, QPixmap, QPainter, QPen, QColor, QBrush,
                             QPainterPath, QPalette, QFont, QLinearGradient,
                             QImage)
    from PyQt5.QtWidgets import (QWidget, QDockWidget, QToolButton, QButtonGroup,
                                 QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
                                 QListWidget, QListWidgetItem, QSlider, QSpinBox,
                                 QCheckBox, QFrame, QSizePolicy, QAbstractItemView,
                                 QScrollArea, QApplication, QMainWindow, QAction)
    QT6 = False


def _enum(owner, scope, name):
    """Return owner.scope.name (PyQt6) or owner.name (PyQt5)."""
    scoped = getattr(owner, scope, None)
    if scoped is not None and hasattr(scoped, name):
        return getattr(scoped, name)
    return getattr(owner, name)


# Frequently used enum values, resolved once.
LEFT_AREA = _enum(Qt, "DockWidgetArea", "LeftDockWidgetArea")
RIGHT_AREA = _enum(Qt, "DockWidgetArea", "RightDockWidgetArea")
HORIZONTAL = _enum(Qt, "Orientation", "Horizontal")
VERTICAL = _enum(Qt, "Orientation", "Vertical")
ALIGN_CENTER = _enum(Qt, "AlignmentFlag", "AlignCenter")
ALIGN_LEFT = _enum(Qt, "AlignmentFlag", "AlignLeft")
ALIGN_TOP = _enum(Qt, "AlignmentFlag", "AlignTop")
ALIGN_VCENTER = _enum(Qt, "AlignmentFlag", "AlignVCenter")
USER_ROLE = _enum(Qt, "ItemDataRole", "UserRole")
TRANSPARENT = _enum(Qt, "GlobalColor", "transparent")
NO_PEN = _enum(Qt, "PenStyle", "NoPen")
DASH_LINE = _enum(Qt, "PenStyle", "DashLine")
NO_BRUSH = _enum(Qt, "BrushStyle", "NoBrush")
ROUND_CAP = _enum(Qt, "PenCapStyle", "RoundCap")
ROUND_JOIN = _enum(Qt, "PenJoinStyle", "RoundJoin")
ANTIALIAS = _enum(QPainter, "RenderHint", "Antialiasing")
TOOL_BUTTON_ICON_ONLY = _enum(Qt, "ToolButtonStyle", "ToolButtonIconOnly")
SLIDER_HORIZONTAL = HORIZONTAL
ROLE_WINDOW_TEXT = _enum(QPalette, "ColorRole", "WindowText")
ROLE_HIGHLIGHT = _enum(QPalette, "ColorRole", "Highlight")
ROLE_BUTTON = _enum(QPalette, "ColorRole", "Button")
ROLE_WINDOW = _enum(QPalette, "ColorRole", "Window")
SINGLE_SELECTION = _enum(QAbstractItemView, "SelectionMode", "SingleSelection")
FRAME_HLINE = _enum(QFrame, "Shape", "HLine")
FRAME_SUNKEN = _enum(QFrame, "Shadow", "Sunken")
SIZE_EXPANDING = _enum(QSizePolicy, "Policy", "Expanding")
SIZE_PREFERRED = _enum(QSizePolicy, "Policy", "Preferred")
SIZE_FIXED = _enum(QSizePolicy, "Policy", "Fixed")
SCROLLBAR_OFF = _enum(Qt, "ScrollBarPolicy", "ScrollBarAlwaysOff")
