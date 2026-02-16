"""
MenuOption widget for Sentinel popup menu.
Each option has an icon container, title, subtitle, and a right arrow (›).
Clicking emits a signal so the popup can navigate to the sub-page.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QFont, QColor

from app.constants import COLORS, MENU_ITEM_HEIGHT
from app.icons import draw_icon


class MenuOption(QWidget):
    """Menu option row — icon + title/subtitle + right arrow ›."""

    clicked = pyqtSignal(str)  # emits the icon_id when clicked

    def __init__(self, icon_id: str, label: str, desc: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(MENU_ITEM_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hovered = False
        self._pressed = False
        self._icon_id = icon_id
        self._label = label
        self._desc = desc

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Hover / Press background ──────────────────────────────
        if self._hovered or self._pressed:
            bg = QPainterPath()
            r = self.rect().adjusted(3, 2, -3, -2)
            bg.addRoundedRect(
                float(r.x()), float(r.y()),
                float(r.width()), float(r.height()), 10, 10,
            )
            if self._pressed:
                p.fillPath(bg, QColor(50, 120, 240, 35))
            else:
                p.fillPath(bg, QColor(255, 255, 255, 8))

        # ── Icon container ────────────────────────────────────────
        container_size = 38
        icon_x = 12.0
        icon_y = float((self.height() - container_size) // 2)
        icon_rect = QRectF(icon_x, icon_y, container_size, container_size)

        bg_path = QPainterPath()
        bg_path.addRoundedRect(icon_rect, 9, 9)
        p.fillPath(bg_path, COLORS["icon_container_bg"])

        draw_icon(p, self._icon_id, icon_rect, COLORS["icon_stroke"])

        # ── Text ──────────────────────────────────────────────────
        text_x = int(icon_x) + container_size + 14
        arrow_space = 28  # space reserved for right arrow

        # Title
        title_font = QFont(".AppleSystemUIFont", 13)
        title_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(title_font)

        if self._pressed:
            p.setPen(QColor(255, 255, 255, 255))
        else:
            p.setPen(COLORS["text_primary"])

        if self._desc:
            p.drawText(
                text_x, 8,
                self.width() - text_x - arrow_space, 20,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                self._label,
            )
            # Subtitle
            desc_font = QFont(".AppleSystemUIFont", 11)
            desc_font.setWeight(QFont.Weight.Normal)
            p.setFont(desc_font)
            p.setPen(COLORS["text_secondary"])
            p.drawText(
                text_x, 30,
                self.width() - text_x - arrow_space, 18,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                self._desc,
            )
        else:
            p.drawText(
                text_x, 0,
                self.width() - text_x - arrow_space, self.height(),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self._label,
            )

        # ── Right arrow › ────────────────────────────────────────
        arrow_font = QFont(".AppleSystemUIFont", 16)
        arrow_font.setWeight(QFont.Weight.Normal)
        p.setFont(arrow_font)
        p.setPen(COLORS["text_secondary"])
        p.drawText(
            self.width() - arrow_space, 0,
            arrow_space - 6, self.height(),
            Qt.AlignmentFlag.AlignCenter,
            "›",
        )

        p.end()

    # ── Mouse events ──────────────────────────────────────────────

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self._pressed = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.clicked.emit(self._icon_id)
            self.update()
