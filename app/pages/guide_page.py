"""
Guide page — placeholder for the Guide Me sub-page.
Override _build_content to add guide-specific UI.
"""

from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.pages.base_page import BasePage


class GuidePage(BasePage):
    """Guide Me sub-page — 'Step-by-step assistance'."""

    PAGE_TITLE = "Guide Me"

    def _build_content(self, layout: QVBoxLayout):
        """Add guide-specific placeholder content."""
        label = QLabel("📖  Step-by-step guide coming soon…", self)
        label.setStyleSheet("color: rgba(255,255,255,100); background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont(".AppleSystemUIFont", 12))
        label.setWordWrap(True)
        layout.addWidget(label)
