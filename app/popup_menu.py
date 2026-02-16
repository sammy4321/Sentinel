"""
PopupMenu widget for Sentinel application.
Multi-page popup: main menu (3 options) → sub-pages (Chat, Guide, Action).
Uses QStackedWidget for smooth page switching.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget,
)
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QFont,
)

from app.constants import (
    COLORS, MENU_ITEMS, MENU_WIDTH, MENU_ITEM_HEIGHT,
    MENU_RADIUS, MENU_PADDING, HEADER_TITLE, FOOTER_TEXT,
    ICON_CHAT, ICON_GUIDE, ICON_ACTION,
)
from app.menu_option import MenuOption
from app.pages import ChatPage, GuidePage, ActionPage
from app.utils import _apply_macos_top, MACOS_ON_TOP_LEVEL


class PopupMenu(QWidget):
    """Multi-page dark card popup with main menu and sub-pages."""

    HEADER_HEIGHT = 44
    FOOTER_HEIGHT = 34

    # Sub-page dimensions: ~2x the main menu
    SUBPAGE_WIDTH = MENU_WIDTH * 2
    SUBPAGE_HEIGHT = 520

    def __init__(self, model: str = "AI", api_key: str = "", parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(MENU_WIDTH)

        self._model = model
        self._api_key = api_key
        self._footer_text = f"Powered by {model}"

        self._ns_window = None
        self._anchor_pos = None
        self._button_width = 0

        # Extra vertical padding for main menu
        self._extra_pad = 6

        # Calculate main menu height
        items_h = MENU_ITEM_HEIGHT * len(MENU_ITEMS) + 2 * (len(MENU_ITEMS) - 1)
        self._main_menu_height = (
            (MENU_PADDING + self._extra_pad) * 2
            + self.HEADER_HEIGHT
            + 1 + 4
            + items_h
            + 4 + 1
            + self.FOOTER_HEIGHT
        )

        self._build_ui()
        self._setup_animation()

    # ── UI construction ───────────────────────────────────────────

    def _build_ui(self):
        self.setFixedHeight(self._main_menu_height)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Stacked widget holds main menu (index 0) and sub-pages (1, 2, 3)
        self._stack = QStackedWidget(self)
        root.addWidget(self._stack)

        # ── Page 0: Main Menu ─────────────────────────────────────
        main_page = QWidget()
        self._build_main_menu(main_page)
        self._stack.addWidget(main_page)

        # ── Page 1: Chat ──────────────────────────────────────────
        self._chat_page = ChatPage(model=self._model, api_key=self._api_key)
        self._chat_page.back_clicked.connect(self._go_back)
        self._chat_page.cancel_clicked.connect(self.animate_hide)
        self._stack.addWidget(self._chat_page)

        # ── Page 2: Guide Me ──────────────────────────────────────
        self._guide_page = GuidePage()
        self._guide_page.back_clicked.connect(self._go_back)
        self._guide_page.cancel_clicked.connect(self.animate_hide)
        self._stack.addWidget(self._guide_page)

        # ── Page 3: Take Action ───────────────────────────────────
        self._action_page = ActionPage()
        self._action_page.back_clicked.connect(self._go_back)
        self._action_page.cancel_clicked.connect(self.animate_hide)
        self._stack.addWidget(self._action_page)

        # Map icon_id → stack index
        self._page_map = {
            ICON_CHAT: 1,
            ICON_GUIDE: 2,
            ICON_ACTION: 3,
        }

        self._stack.setCurrentIndex(0)

    def _build_main_menu(self, page: QWidget):
        pad_v = MENU_PADDING + self._extra_pad
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            MENU_PADDING, pad_v,
            MENU_PADDING, pad_v,
        )
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        header_widget = QWidget(page)
        header_widget.setFixedHeight(self.HEADER_HEIGHT)
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(10, 6, 10, 6)
        h_layout.setSpacing(7)

        dot = _DotWidget(COLORS["dot_active"], size=8, parent=header_widget)
        h_layout.addWidget(dot)

        title = QLabel(HEADER_TITLE, header_widget)
        title_font = QFont(".AppleSystemUIFont", 15)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: rgba(255,255,255,240); background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        h_layout.addWidget(title)
        h_layout.addStretch()

        layout.addWidget(header_widget)

        # ── Separator ─────────────────────────────────────────────
        layout.addWidget(_make_separator())
        layout.addSpacing(4)

        # ── Menu items ────────────────────────────────────────────
        for i, item in enumerate(MENU_ITEMS):
            option = MenuOption(
                item["icon"],
                item["label"],
                item.get("desc", ""),
                parent=page,
            )
            option.clicked.connect(self._on_option_clicked)
            layout.addWidget(option)
            if i < len(MENU_ITEMS) - 1:
                layout.addSpacing(2)

        # ── Bottom separator ──────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_make_separator())

        # ── Footer ────────────────────────────────────────────────
        footer = QLabel(self._footer_text, page)
        footer.setFixedHeight(self.FOOTER_HEIGHT)
        footer_font = QFont(".AppleSystemUIFont", 10)
        footer_font.setItalic(True)
        footer.setFont(footer_font)
        c = COLORS["text_footer"]
        footer.setStyleSheet(
            f"color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()});"
            " background: transparent; padding-left: 8px;"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(footer)

    # ── Page navigation ───────────────────────────────────────────

    def _on_option_clicked(self, icon_id: str):
        idx = self._page_map.get(icon_id, 0)
        if idx:
            self._stack.setCurrentIndex(idx)
            self.setFixedWidth(self.SUBPAGE_WIDTH)
            self.setFixedHeight(self.SUBPAGE_HEIGHT)
            self._reposition()

    def _go_back(self):
        self._stack.setCurrentIndex(0)
        self.setFixedWidth(MENU_WIDTH)
        self.setFixedHeight(self._main_menu_height)
        self._reposition()

    def _reposition(self):
        """Re-position popup after size change so it stays anchored above the button."""
        if self._anchor_pos is not None:
            # Keep right edge aligned with the button's right edge
            target_x = self._anchor_pos.x() - self.width() + self._button_width // 2
            target_y = self._anchor_pos.y() - self.height() - 12
            self.move(target_x, target_y)

    # ── Animation setup ───────────────────────────────────────────

    def _setup_animation(self):
        from PyQt6.QtWidgets import QGraphicsOpacityEffect

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._opacity_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._opacity_anim.setDuration(180)
        self._opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._geom_anim = QPropertyAnimation(self, b"geometry")
        self._geom_anim.setDuration(200)
        self._geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── Custom paint — three-zone background ──────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        rad = float(MENU_RADIUS)

        # Drop shadow
        shadow = QPainterPath()
        shadow.addRoundedRect(3.0, 5.0, w - 6, h - 6, rad, rad)
        p.fillPath(shadow, COLORS["shadow"])

        # Clip to rounded rect
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, w, h, rad, rad)
        p.setClipPath(clip)

        if self._stack.currentIndex() == 0:
            # Main menu — three zones
            pad_v = MENU_PADDING + self._extra_pad
            header_zone = self.HEADER_HEIGHT + pad_v + 1 + 4
            items_h = MENU_ITEM_HEIGHT * len(MENU_ITEMS) + 2 * (len(MENU_ITEMS) - 1)
            footer_top = header_zone + items_h + 4 + 1

            p.fillRect(QRectF(0, 0, w, header_zone), COLORS["bg_header"])
            p.fillRect(QRectF(0, header_zone, w, items_h + 4), COLORS["bg_middle"])
            p.fillRect(QRectF(0, footer_top, w, h - footer_top), COLORS["bg_footer"])
        else:
            # Sub-page — two zones: lighter header, darker body
            subpage_header_h = 56.0  # header + separator area
            p.fillRect(QRectF(0, 0, w, subpage_header_h), COLORS["bg_subpage_header"])
            p.fillRect(QRectF(0, subpage_header_h, w, h - subpage_header_h), COLORS["bg_subpage_body"])

        p.setClipping(False)

        # Border
        border = QPainterPath()
        border.addRoundedRect(0.5, 0.5, w - 1, h - 1, rad, rad)
        p.setPen(QPen(COLORS["border"], 1.0))
        p.drawPath(border)

        p.end()

    # ── Show / hide ───────────────────────────────────────────────

    def animate_show(self, anchor_pos: QPoint, button_width: int = 0):
        self._anchor_pos = anchor_pos
        self._button_width = button_width

        # Always start on main menu
        self._stack.setCurrentIndex(0)
        self.setFixedHeight(self._main_menu_height)

        target_x = anchor_pos.x() - self.width() + button_width // 2
        target_y = anchor_pos.y() - self.height() - 12

        start = QRect(target_x, target_y + 10, self.width(), self.height())
        end = QRect(target_x, target_y, self.width(), self.height())

        self.setGeometry(start)
        self.show()

        self._ns_window = _apply_macos_top(self, MACOS_ON_TOP_LEVEL + 1)

        self._geom_anim.stop()
        self._geom_anim.setStartValue(start)
        self._geom_anim.setEndValue(end)
        self._geom_anim.start()

        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(0.0)
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.start()

    def animate_hide(self):
        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(1.0)
        self._opacity_anim.setEndValue(0.0)
        self._opacity_anim.finished.connect(self._on_hide_done)
        self._opacity_anim.start()

    def _on_hide_done(self):
        self.hide()
        # Reset to main menu dimensions for next open
        self._stack.setCurrentIndex(0)
        self.setFixedWidth(MENU_WIDTH)
        self.setFixedHeight(self._main_menu_height)
        try:
            self._opacity_anim.finished.disconnect(self._on_hide_done)
        except TypeError:
            pass


# ── Helper widgets ────────────────────────────────────────────────

def _make_separator():
    sep = QWidget()
    sep.setFixedHeight(1)
    c = COLORS["separator"]
    sep.setStyleSheet(
        f"background-color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()});"
    )
    return sep


class _DotWidget(QWidget):
    """Painted blue status dot."""

    def __init__(self, color: QColor, size: int = 8, parent=None):
        super().__init__(parent)
        self._color = color
        self._size = size
        self.setFixedSize(size + 4, size + 4)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._color)
        x = (self.width() - self._size) / 2
        y = (self.height() - self._size) / 2
        p.drawEllipse(QRectF(x, y, self._size, self._size))
        p.end()
