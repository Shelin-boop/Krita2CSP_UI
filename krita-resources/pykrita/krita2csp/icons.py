# SPDX-License-Identifier: GPL-3.0-or-later
"""Original line icons for the CSP-style tool palette.

Drawn with QPainter on a 24 x 24 grid so they follow the current Krita
theme (light or dark) and need no image files. These are our own
drawings, not copies of Clip Studio Paint's icons.
"""

from .qtcompat import (QIcon, QPixmap, QPainter, QPen, QColor, QBrush, QPainterPath,
                       QRectF, QPointF, QLinearGradient, TRANSPARENT, NO_PEN, NO_BRUSH,
                       ROUND_CAP, ROUND_JOIN, ANTIALIAS, DASH_LINE)

_W = 1.7  # stroke width on the 24 px grid


def _pen(color, width=_W, style=None):
    pen = QPen(color, width)
    pen.setCapStyle(ROUND_CAP)
    pen.setJoinStyle(ROUND_JOIN)
    if style is not None:
        pen.setStyle(style)
    return pen


def _path(points, close=False):
    path = QPainterPath(QPointF(*points[0]))
    for pt in points[1:]:
        path.lineTo(QPointF(*pt))
    if close:
        path.closeSubpath()
    return path


# --- individual icons -------------------------------------------------------

def _zoom(p, fg, ac):
    p.setPen(_pen(fg))
    p.drawEllipse(QRectF(4, 4, 11, 11))
    p.setPen(_pen(fg, 2.6))
    p.drawLine(QPointF(13.5, 13.5), QPointF(20, 20))
    p.setPen(_pen(ac, 1.5))
    p.drawLine(QPointF(7, 9.5), QPointF(12, 9.5))
    p.drawLine(QPointF(9.5, 7), QPointF(9.5, 12))


def _hand(p, fg, ac):
    p.setPen(_pen(fg))
    # four fingers
    for x, top in ((7.5, 6.5), (10.5, 4.5), (13.5, 5), (16.5, 7.5)):
        p.drawLine(QPointF(x, top), QPointF(x, 12))
    # thumb and palm
    palm = QPainterPath(QPointF(16.5, 12))
    palm.cubicTo(QPointF(16.5, 17), QPointF(15, 20), QPointF(11.5, 20))
    palm.cubicTo(QPointF(8.5, 20), QPointF(6.5, 18), QPointF(5, 15))
    palm.lineTo(QPointF(3.5, 11.5))
    palm.cubicTo(QPointF(3.2, 10.5), QPointF(4.8, 9.8), QPointF(5.6, 11))
    palm.lineTo(QPointF(7.5, 13.5))
    p.drawPath(palm)


def _operation(p, fg, ac):
    p.setPen(_pen(fg, 1.4))
    p.setBrush(QBrush(ac))
    p.drawPath(_path([(6, 3.5), (6, 18.5), (10, 14.8), (12.8, 20.5), (15.2, 19.4),
                      (12.5, 13.8), (17.5, 13.5)], close=True))
    p.setBrush(NO_BRUSH)


def _move(p, fg, ac):
    p.setPen(_pen(fg))
    p.drawLine(QPointF(12, 3.5), QPointF(12, 20.5))
    p.drawLine(QPointF(3.5, 12), QPointF(20.5, 12))
    for a, b, c in (((9.5, 6), (12, 3.5), (14.5, 6)), ((9.5, 18), (12, 20.5), (14.5, 18)),
                    ((6, 9.5), (3.5, 12), (6, 14.5)), ((18, 9.5), (20.5, 12), (18, 14.5))):
        p.drawPolyline([QPointF(*a), QPointF(*b), QPointF(*c)])
    p.setPen(NO_PEN)
    p.setBrush(QBrush(ac))
    p.drawRect(QRectF(10, 10, 4, 4))
    p.setBrush(NO_BRUSH)


def _selection(p, fg, ac):
    p.setPen(_pen(fg, 1.6, DASH_LINE))
    p.drawRect(QRectF(4, 5, 16, 14))
    p.setPen(NO_PEN)
    p.setBrush(QBrush(ac))
    for x, y in ((4, 5), (20, 5), (4, 19), (20, 19)):
        p.drawRect(QRectF(x - 1.6, y - 1.6, 3.2, 3.2))
    p.setBrush(NO_BRUSH)


def _autoselect(p, fg, ac):
    p.setPen(_pen(fg, 2.2))
    p.drawLine(QPointF(4, 20), QPointF(14, 10))
    p.setPen(_pen(ac, 1.4))
    cx, cy = 17, 7
    for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0)):
        p.drawLine(QPointF(cx, cy), QPointF(cx + dx, cy + dy))
    for dx, dy in ((-2.5, -2.5), (2.5, 2.5), (-2.5, 2.5), (2.5, -2.5)):
        p.drawLine(QPointF(cx, cy), QPointF(cx + dx * 0.7, cy + dy * 0.7))


def _eyedropper(p, fg, ac):
    p.setPen(_pen(fg))
    p.drawLine(QPointF(5, 19), QPointF(13, 11))
    p.drawPolyline([QPointF(5, 19), QPointF(4, 20.5), QPointF(5.5, 19.5)])
    body = _path([(11, 9), (15, 13), (13.5, 14.5), (9.5, 10.5)], close=True)
    p.drawPath(body)
    p.setBrush(QBrush(ac))
    p.drawEllipse(QRectF(13.5, 4, 6.5, 6.5))
    p.setBrush(NO_BRUSH)


def _pen_nib(p, fg, ac):
    # fountain pen nib, pointing down-left
    p.setPen(_pen(fg, 1.5))
    p.setBrush(QBrush(ac))
    nib = _path([(4, 20), (7.5, 11.5), (12.5, 8), (16, 11.5), (12.5, 16.5)], close=True)
    p.drawPath(nib)
    p.setBrush(NO_BRUSH)
    p.drawLine(QPointF(4, 20), QPointF(10, 14))
    p.drawEllipse(QRectF(9.4, 12.4, 2.2, 2.2))
    p.setPen(_pen(fg, 2.2))
    p.drawLine(QPointF(14, 9.8), QPointF(19.5, 4.3))


def _pencil(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    body = _path([(7.5, 13.5), (16.5, 4.5), (19.5, 7.5), (10.5, 16.5)], close=True)
    p.setBrush(QBrush(ac))
    p.drawPath(body)
    p.setBrush(NO_BRUSH)
    p.drawPath(_path([(7.5, 13.5), (4.5, 19.5), (10.5, 16.5)]))
    p.drawLine(QPointF(14.5, 6.5), QPointF(17.5, 9.5))
    p.setBrush(QBrush(fg))
    p.drawPath(_path([(5.6, 17.2), (4.5, 19.5), (6.8, 18.4)], close=True))
    p.setBrush(NO_BRUSH)


def _brush(p, fg, ac):
    p.setPen(_pen(fg, 2.0))
    p.drawLine(QPointF(19.5, 4.5), QPointF(12.5, 11.5))
    p.setPen(_pen(fg, 1.4))
    p.setBrush(QBrush(ac))
    tip = QPainterPath(QPointF(12.8, 10.2))
    tip.lineTo(QPointF(13.8, 11.2))
    tip.cubicTo(QPointF(13, 15.5), QPointF(9, 19), QPointF(4, 20))
    tip.cubicTo(QPointF(5, 15), QPointF(8.5, 11), QPointF(12.8, 10.2))
    p.drawPath(tip)
    p.setBrush(NO_BRUSH)


def _airbrush(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    p.drawPath(_path([(10, 9), (19, 9), (19, 13), (10, 13)], close=True))
    p.drawLine(QPointF(14.5, 13), QPointF(13, 19))
    p.drawLine(QPointF(10, 11), QPointF(7.5, 11))
    p.setPen(NO_PEN)
    p.setBrush(QBrush(ac))
    for x, y, r in ((5, 11, 1.4), (3.5, 8, 1.0), (3.5, 14, 1.0), (6, 6.5, 0.8), (6, 15.5, 0.8)):
        p.drawEllipse(QPointF(x, y), r, r)
    p.setBrush(NO_BRUSH)


def _decoration(p, fg, ac):
    star = QPainterPath(QPointF(12, 3.5))
    star.quadTo(QPointF(13.5, 10.5), QPointF(20.5, 12))
    star.quadTo(QPointF(13.5, 13.5), QPointF(12, 20.5))
    star.quadTo(QPointF(10.5, 13.5), QPointF(3.5, 12))
    star.quadTo(QPointF(10.5, 10.5), QPointF(12, 3.5))
    p.setPen(_pen(fg, 1.4))
    p.setBrush(QBrush(ac))
    p.drawPath(star)
    p.setBrush(NO_BRUSH)
    p.setPen(_pen(fg, 1.2))
    p.drawLine(QPointF(18.5, 3.5), QPointF(18.5, 7.5))
    p.drawLine(QPointF(16.5, 5.5), QPointF(20.5, 5.5))


def _eraser(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    p.setBrush(QBrush(ac))
    p.drawPath(_path([(4.5, 14.5), (12.5, 6.5), (19.5, 13.5), (14.5, 18.5), (8.5, 18.5)], close=True))
    p.setBrush(NO_BRUSH)
    p.drawLine(QPointF(8.5, 10.5), QPointF(15.5, 17.5))
    p.drawLine(QPointF(8.5, 20.5), QPointF(20, 20.5))


def _blend(p, fg, ac):
    drop = QPainterPath(QPointF(12, 3.5))
    drop.cubicTo(QPointF(15, 8), QPointF(18.5, 11.5), QPointF(18.5, 14.5))
    drop.cubicTo(QPointF(18.5, 18.2), QPointF(15.5, 20.5), QPointF(12, 20.5))
    drop.cubicTo(QPointF(8.5, 20.5), QPointF(5.5, 18.2), QPointF(5.5, 14.5))
    drop.cubicTo(QPointF(5.5, 11.5), QPointF(9, 8), QPointF(12, 3.5))
    p.setPen(_pen(fg, 1.5))
    p.drawPath(drop)
    wave = QPainterPath(QPointF(7.5, 15.5))
    wave.cubicTo(QPointF(9.5, 13), QPointF(11, 18), QPointF(13, 15.5))
    wave.cubicTo(QPointF(14.5, 13.5), QPointF(15.5, 16), QPointF(16.5, 15))
    p.setPen(_pen(ac, 1.6))
    p.drawPath(wave)


def _fill(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    bucket = _path([(5, 11), (11, 5), (18, 12), (12, 18)], close=True)
    p.drawPath(bucket)
    p.drawLine(QPointF(8, 8), QPointF(5.5, 5.5))
    p.setPen(NO_PEN)
    p.setBrush(QBrush(ac))
    drop = QPainterPath(QPointF(19, 14))
    drop.cubicTo(QPointF(20.5, 16.5), QPointF(21, 17.5), QPointF(21, 18.5))
    drop.cubicTo(QPointF(21, 20), QPointF(17, 20), QPointF(17, 18.5))
    drop.cubicTo(QPointF(17, 17.5), QPointF(17.5, 16.5), QPointF(19, 14))
    p.drawPath(drop)
    p.setBrush(NO_BRUSH)


def _gradient(p, fg, ac):
    grad = QLinearGradient(QPointF(4, 0), QPointF(20, 0))
    grad.setColorAt(0, ac)
    c = QColor(ac)
    c.setAlpha(0)
    grad.setColorAt(1, c)
    p.setPen(NO_PEN)
    p.setBrush(QBrush(grad))
    p.drawRect(QRectF(4, 6, 16, 12))
    p.setBrush(NO_BRUSH)
    p.setPen(_pen(fg, 1.4))
    p.drawRect(QRectF(4, 6, 16, 12))


def _figure(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    p.drawRect(QRectF(4, 4, 10, 10))
    p.setBrush(QBrush(ac))
    p.drawEllipse(QRectF(10, 10, 10, 10))
    p.setBrush(NO_BRUSH)


def _frame(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    p.drawRect(QRectF(3.5, 3.5, 7.5, 7.5))
    p.drawRect(QRectF(13, 3.5, 7.5, 7.5))
    p.setBrush(QBrush(ac))
    p.drawRect(QRectF(3.5, 13, 17, 7.5))
    p.setBrush(NO_BRUSH)


def _ruler(p, fg, ac):
    p.setPen(_pen(fg, 1.5))
    p.setBrush(QBrush(ac))
    p.drawPath(_path([(3.5, 16), (16, 3.5), (20.5, 8), (8, 20.5)], close=True))
    p.setBrush(NO_BRUSH)
    for i, length in enumerate((2.5, 1.5, 2.5, 1.5, 2.5)):
        x = 6.5 + i * 2.3
        y = 13 - i * 2.3
        p.drawLine(QPointF(x, y), QPointF(x + length * 0.7, y + length * 0.7))


def _text(p, fg, ac):
    p.setPen(_pen(fg, 2.0))
    p.drawPolyline([QPointF(5, 20), QPointF(12, 4), QPointF(19, 20)])
    p.setPen(_pen(ac, 2.0))
    p.drawLine(QPointF(8, 14.5), QPointF(16, 14.5))


def _correct(p, fg, ac):
    curve = QPainterPath(QPointF(4, 18))
    curve.cubicTo(QPointF(8, 4), QPointF(16, 20), QPointF(20, 6))
    p.setPen(_pen(fg, 1.5))
    p.drawPath(curve)
    p.setPen(_pen(fg, 1.2))
    p.setBrush(QBrush(ac))
    for x, y in ((4, 18), (12, 12), (20, 6)):
        p.drawRect(QRectF(x - 2, y - 2, 4, 4))
    p.setBrush(NO_BRUSH)


def _add(p, fg, ac):
    p.setPen(_pen(fg, 2.0))
    p.drawLine(QPointF(12, 5), QPointF(12, 19))
    p.drawLine(QPointF(5, 12), QPointF(19, 12))


def _remove(p, fg, ac):
    p.setPen(_pen(fg, 2.0))
    p.drawLine(QPointF(5, 12), QPointF(19, 12))


_ICONS = {
    "zoom": _zoom, "hand": _hand, "operation": _operation, "move": _move,
    "selection": _selection, "autoselect": _autoselect, "eyedropper": _eyedropper,
    "pen": _pen_nib, "pencil": _pencil, "brush": _brush, "airbrush": _airbrush,
    "decoration": _decoration, "eraser": _eraser, "blend": _blend, "fill": _fill,
    "gradient": _gradient, "figure": _figure, "frame": _frame, "ruler": _ruler,
    "text": _text, "correct": _correct, "add": _add, "remove": _remove,
}

_cache = {}


def make_icon(name, fg, accent, sizes=(24, 48)):
    """Return a QIcon for `name`, drawn in the given colors."""
    key = (name, fg.rgba(), accent.rgba())
    if key in _cache:
        return _cache[key]
    draw = _ICONS.get(name)
    icon = QIcon()
    for size in sizes:
        pm = QPixmap(size, size)
        pm.fill(QColor(TRANSPARENT))
        if draw is not None:
            painter = QPainter(pm)
            painter.setRenderHint(ANTIALIAS, True)
            painter.scale(size / 24.0, size / 24.0)
            draw(painter, fg, accent)
            painter.end()
        icon.addPixmap(pm)
    _cache[key] = icon
    return icon


def clear_cache():
    _cache.clear()
