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
    # Camera feels smaller visually, so we give it less padding
    inset_factor = 0.17 if icon_id == "camera" else 0.24
    inset = rect.width() * inset_factor
    r = rect.adjusted(inset, inset, -inset, -inset)

    if icon_id == "chat":
        _draw_chat(painter, r, color)
    elif icon_id == "guide":
        _draw_guide(painter, r, color)
    elif icon_id == "action":
        _draw_action(painter, r, color)
    elif icon_id == "camera":
        _draw_camera(painter, r, color)

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


def _draw_camera(painter: QPainter, r: QRectF, color: QColor):
    """Minimalistic camera outline."""
    painter.setPen(_make_pen(color))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    x, y, w, h = r.x(), r.y(), r.width(), r.height()

    # Camera body dimensions (occupies most of the rect)
    body_h = h * 0.75
    body_w = w
    body_x = x
    body_y = y + (h - body_h)

    # Viewfinder/bump on top
    bump_w = w * 0.50
    bump_h = h * 0.20
    bump_x = x + (w - bump_w) / 2
    # Slight overlap with body so they merge
    bump_y = body_y - (bump_h * 0.7)

    # Create paths
    body_path = QPainterPath()
    body_path.addRoundedRect(QRectF(body_x, body_y, body_w, body_h), w * 0.12, w * 0.12)

    bump_path = QPainterPath()
    bump_path.addRoundedRect(QRectF(bump_x, bump_y, bump_w, bump_h), w * 0.06, w * 0.06)

    # Merge for a single continuous outline
    outline = body_path.united(bump_path)
    painter.drawPath(outline)

    # Lens
    lens_d = min(body_w, body_h) * 0.50
    lens_cx, lens_cy = body_x + body_w / 2, body_y + body_h / 2
    lens_rect = QRectF(0, 0, lens_d, lens_d)
    lens_rect.moveCenter(QPointF(lens_cx, lens_cy))
    painter.drawEllipse(lens_rect)

    # Small flash dot
    dot_d = w * 0.08
    dot_cx = body_x + body_w * 0.82
    dot_cy = body_y + body_h * 0.18
    painter.drawEllipse(QRectF(dot_cx - dot_d / 2, dot_cy - dot_d / 2, dot_d, dot_d))
