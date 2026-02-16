"""
Icon drawing utilities for Sentinel application.
Clean, minimalistic line icons matching the reference design.
"""

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor

from app.constants import COLORS


def draw_icon(painter: QPainter, icon_id: str, rect: QRectF, color: QColor = None):
    """
    Draw a minimalistic vector icon inside the given rect.

    Args:
        painter: Active QPainter.
        icon_id: One of 'chat', 'guide', 'action'.
        rect: The bounding rectangle to draw inside.
        color: Stroke color (defaults to COLORS['icon_stroke']).
    """
    color = color or COLORS["icon_stroke"]
    painter.save()

    # Inset so the icon has padding inside its container
    inset = rect.width() * 0.24
    r = rect.adjusted(inset, inset, -inset, -inset)

    if icon_id == "chat":
        _draw_chat(painter, r, color)
    elif icon_id == "guide":
        _draw_guide(painter, r, color)
    elif icon_id == "action":
        _draw_action(painter, r, color)

    painter.restore()


def _make_pen(color: QColor, width: float = 1.6) -> QPen:
    """Create a rounded-cap/join pen for clean icon strokes."""
    pen = QPen(color, width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _draw_chat(painter: QPainter, r: QRectF, color: QColor):
    """Simple speech bubble outline — clean and minimal."""
    painter.setPen(_make_pen(color))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    x, y, w, h = r.x(), r.y(), r.width(), r.height()

    # Bubble body (rounded rect, shorter to leave room for tail)
    bubble_h = h * 0.70
    bubble = QRectF(x, y, w, bubble_h)

    path = QPainterPath()
    path.addRoundedRect(bubble, 3.5, 3.5)
    painter.drawPath(path)

    # Small tail at bottom-left
    tail = QPainterPath()
    tx = x + w * 0.22
    ty = y + bubble_h
    tail.moveTo(tx, ty - 0.5)
    tail.lineTo(tx - 1.5, y + h)
    tail.lineTo(tx + 4, ty - 0.5)
    painter.drawPath(tail)


def _draw_guide(painter: QPainter, r: QRectF, color: QColor):
    """Simple compass outline — circle with a diamond pointer inside."""
    painter.setPen(_make_pen(color))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cx, cy = r.center().x(), r.center().y()
    w, h = r.width(), r.height()

    # Outer circle
    painter.drawEllipse(r)

    # Small diamond pointer in center
    d = w * 0.22
    diamond = QPainterPath()
    diamond.moveTo(cx, cy - d)       # top
    diamond.lineTo(cx + d, cy)       # right
    diamond.lineTo(cx, cy + d)       # bottom
    diamond.lineTo(cx - d, cy)       # left
    diamond.closeSubpath()

    # Fill top-right and bottom-left quadrants
    painter.setBrush(color)
    tr = QPainterPath()
    tr.moveTo(cx, cy)
    tr.lineTo(cx, cy - d)
    tr.lineTo(cx + d, cy)
    tr.closeSubpath()
    painter.drawPath(tr)

    bl = QPainterPath()
    bl.moveTo(cx, cy)
    bl.lineTo(cx, cy + d)
    bl.lineTo(cx - d, cy)
    bl.closeSubpath()
    painter.drawPath(bl)

    # Outline the other two quadrants
    painter.setBrush(Qt.BrushStyle.NoBrush)
    tl = QPainterPath()
    tl.moveTo(cx, cy)
    tl.lineTo(cx, cy - d)
    tl.lineTo(cx - d, cy)
    tl.closeSubpath()
    painter.drawPath(tl)

    br = QPainterPath()
    br.moveTo(cx, cy)
    br.lineTo(cx, cy + d)
    br.lineTo(cx + d, cy)
    br.closeSubpath()
    painter.drawPath(br)


def _draw_action(painter: QPainter, r: QRectF, color: QColor):
    """Simple lightning bolt — filled, clean shape."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)

    x, y = r.x(), r.y()
    w, h = r.width(), r.height()

    bolt = QPainterPath()
    bolt.moveTo(x + w * 0.52, y)
    bolt.lineTo(x + w * 0.18, y + h * 0.50)
    bolt.lineTo(x + w * 0.46, y + h * 0.46)
    bolt.lineTo(x + w * 0.38, y + h)
    bolt.lineTo(x + w * 0.82, y + h * 0.44)
    bolt.lineTo(x + w * 0.54, y + h * 0.48)
    bolt.closeSubpath()
    painter.drawPath(bolt)
