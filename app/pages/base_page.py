"""
BasePage — shared layout for all Sentinel popup sub-pages.
Header: ← Back (left) + Title (center) + ✕ Close (right)
Content area below for subclass to fill.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from app.constants import COLORS, MENU_WIDTH, MENU_PADDING


class BasePage(QWidget):
    """
    Base class for sub-pages. Subclass and override `_build_content`
    to add page-specific widgets.

    Signals:
        back_clicked: emitted when user presses ←.
        cancel_clicked: emitted when user presses ✕.
    """

    back_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()

    PAGE_TITLE = "Page"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_layout()

    def _build_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(MENU_PADDING, MENU_PADDING + 4,
                                  MENU_PADDING, MENU_PADDING + 4)
        layout.setSpacing(0)

        # ── Header: ← Back  |  Title  |  ✕ ───────────────────────
        header = QWidget(self)
        header.setFixedHeight(42)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(4, 4, 4, 4)
        h_layout.setSpacing(6)

        # Back button (transparent bg)
        self._back_btn = QPushButton("←", header)
        self._back_btn.setFixedSize(28, 28)
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.setStyleSheet(self._icon_button_style())
        self._back_btn.clicked.connect(self.back_clicked.emit)
        h_layout.addWidget(self._back_btn)

        # Title
        title = QLabel(self.PAGE_TITLE, header)
        title_font = QFont(".AppleSystemUIFont", 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: rgba(255,255,255,235); background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        h_layout.addWidget(title)

        h_layout.addStretch()

        # Cancel / Close button (✕, transparent bg)
        self._cancel_btn = QPushButton("✕", header)
        self._cancel_btn.setFixedSize(28, 28)
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.setStyleSheet(self._icon_button_style())
        self._cancel_btn.clicked.connect(self.cancel_clicked.emit)
        h_layout.addWidget(self._cancel_btn)

        layout.addWidget(header)

        # ── Separator ─────────────────────────────────────────────
        sep = QWidget(self)
        sep.setFixedHeight(1)
        c = COLORS["separator"]
        sep.setStyleSheet(
            f"background-color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()});"
        )
        layout.addWidget(sep)
        layout.addSpacing(12)

        # ── Content area (subclass fills this) ────────────────────
        self._content_widget = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(8, 0, 8, 0)
        self._content_layout.setSpacing(8)

        # Let subclass populate content
        self._build_content(self._content_layout)

        self._content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding,
        )
        layout.addWidget(self._content_widget)
        layout.addStretch()

    def _build_content(self, layout: QVBoxLayout):
        """Override in subclass to add page-specific content."""
        placeholder = QLabel("Coming soon…", self)
        placeholder.setStyleSheet("color: rgba(255,255,255,100); background: transparent;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_font = QFont(".AppleSystemUIFont", 12)
        placeholder.setFont(placeholder_font)
        layout.addWidget(placeholder)

    # ── Styles ────────────────────────────────────────────────────

    @staticmethod
    def _icon_button_style() -> str:
        """Transparent background icon button style."""
        return """
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,180);
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: rgba(255,255,255,255);
                background: rgba(255,255,255,10);
            }
            QPushButton:pressed {
                color: rgba(50,120,240,255);
                background: rgba(50,120,240,15);
            }
        """
