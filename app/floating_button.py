"""
FloatingButton widget for Sentinel application.
A draggable floating button that shows a popup menu on click.
"""

import os
import sys

from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPixmap

from app.popup_menu import PopupMenu
from app.utils import _apply_macos_top, MACOS_ON_TOP_LEVEL


class FloatingButton(QWidget):
    """Draggable floating button with popup menu."""

    DRAG_THRESHOLD = 5

    def __init__(self, model: str = "AI", api_key: str = ""):
        """Initialize the floating button.
        
        Args:
            model: Model name to display in the footer.
            api_key: API key for the model provider.
        """
        super().__init__()
        self._ns_window = None
        self._model = model
        self._api_key = api_key
        self._popup = PopupMenu(model=model, api_key=api_key)
        self._popup_visible = False
        self.oldPos = None
        self._dragged = False
        # Sync toggle state when popup hides itself (e.g. Cancel button)
        self._popup._opacity_anim.finished.connect(self._on_popup_hidden)
        self.initUI()

    def initUI(self):
        """Initialize the UI components."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        image_path = os.path.join("assets", "icon.png")
        if not os.path.exists(image_path):
            print(f"Error: {image_path} not found")
            sys.exit(1)

        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print("Failed to load image data")
                sys.exit(1)

            if pixmap.width() > 100 or pixmap.height() > 100:
                pixmap = pixmap.scaled(
                    100, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

            self.label.setPixmap(pixmap)
            self.label.resize(pixmap.width(), pixmap.height())
            self.resize(pixmap.width(), pixmap.height())
        except Exception as e:
            print(f"Error initializing image: {e}")
            sys.exit(1)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - self.width() - 50, screen.height() - self.height() - 50)

        self._level_timer = QTimer(self)
        self._level_timer.timeout.connect(self._reassert_on_top)
        self._level_timer.start(500)

    # ── macOS native setup ─────────────────────────────────────────
    def showEvent(self, event):
        """Handle show event to apply macOS window behavior."""
        super().showEvent(event)
        self._ns_window = _apply_macos_top(self, MACOS_ON_TOP_LEVEL)

    def _reassert_on_top(self):
        """Periodically reassert the window on top level."""
        if self._ns_window is not None:
            try:
                self._ns_window.setLevel_(MACOS_ON_TOP_LEVEL)
                self._ns_window.orderFrontRegardless()
            except Exception:
                pass
        else:
            self._ns_window = _apply_macos_top(self, MACOS_ON_TOP_LEVEL)

        # Also reassert the popup if visible
        if self._popup_visible and self._popup._ns_window is not None:
            try:
                self._popup._ns_window.setLevel_(MACOS_ON_TOP_LEVEL + 1)
                self._popup._ns_window.orderFrontRegardless()
            except Exception:
                pass

    # ── Mouse interaction ──────────────────────────────────────────
    def mousePressEvent(self, event):
        """Handle mouse press event for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            self._dragged = False

    def mouseMoveEvent(self, event):
        """Handle mouse move event for dragging."""
        if self.oldPos and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            if abs(delta.x()) > self.DRAG_THRESHOLD or abs(delta.y()) > self.DRAG_THRESHOLD:
                self._dragged = True
            if self._dragged:
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.oldPos = event.globalPosition().toPoint()
                if self._popup_visible:
                    self._toggle_popup()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event for click detection."""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._dragged:
                self._toggle_popup()
            self.oldPos = None
            self._dragged = False

    def _toggle_popup(self):
        """Toggle the popup menu visibility."""
        if self._popup_visible:
            self._popup.animate_hide()
            self._popup_visible = False
        else:
            # Send button's top-center as anchor
            anchor = self.mapToGlobal(QPoint(self.width() // 2, 0))
            self._popup.animate_show(anchor, self.width())
            self._popup_visible = True

    def contextMenuEvent(self, event):
        """Handle context menu event to quit application."""
        QApplication.quit()

    def _on_popup_hidden(self):
        """Reset toggle state when popup hides itself."""
        if not self._popup.isVisible():
            self._popup_visible = False
