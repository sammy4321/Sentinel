"""
Action page — placeholder for the Take Action sub-page.
Override _build_content to add action-specific UI.
"""

from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.pages.base_page import BasePage


class ActionPage(BasePage):
    """Take Action sub-page — 'Automate this task'."""

    PAGE_TITLE = "Take Action"

    def _build_content(self, layout: QVBoxLayout):
        """Add action-specific placeholder content."""
        label = QLabel("⚡  Automation interface coming soon…", self)
        label.setStyleSheet("color: rgba(255,255,255,100); background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont(".AppleSystemUIFont", 12))
        label.setWordWrap(True)
        layout.addWidget(label)
