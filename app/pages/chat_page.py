"""
Chat page — placeholder for the Chat sub-page.
Override _build_content to add chat-specific UI.
"""

from PyQt6.QtWidgets import QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.pages.base_page import BasePage


class ChatPage(BasePage):
    """Chat sub-page — 'Ask me anything'."""

    PAGE_TITLE = "Chat"

    def _build_content(self, layout: QVBoxLayout):
        """Add chat-specific placeholder content."""
        label = QLabel("💬  Chat interface coming soon…", self)
        label.setStyleSheet("color: rgba(255,255,255,100); background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont(".AppleSystemUIFont", 12))
        label.setWordWrap(True)
        layout.addWidget(label)
