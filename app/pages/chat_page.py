"""
Chat page — polished chat interface matching the reference design.
Dark chat with proper message bubbles, compact input area, file attachment.
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea,
    QTextEdit, QPushButton, QSizePolicy, QFileDialog, QFrame, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QRectF, QBuffer, QIODevice
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath
import time

from app.pages.base_page import BasePage
from app.constants import COLORS
from app.openrouter import OpenRouterClient, ChatWorker
from app.icons import draw_icon


class ChatPage(BasePage):
    """Chat sub-page — polished dark chat matching reference design."""

    PAGE_TITLE = "Chat"

    def __init__(self, model: str = "AI", api_key: str = "", parent=None):
        self._model = model
        self._api_key = api_key
        self._client = OpenRouterClient(api_key, model) if api_key else None
        self._messages = []
        self._attached_file = None
        self._worker = None
        self._typing_indicator = None
        self._request_start = 0
        super().__init__(parent)

        # ── Refresh button in header (before ✕) ──────────────────
        self._refresh_btn = QPushButton("↻")
        self._refresh_btn.setFixedSize(28, 28)
        self._refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_btn.setToolTip("New conversation")
        self._refresh_btn.setStyleSheet(self._icon_button_style())
        self._refresh_btn.clicked.connect(self._reset_conversation)
        # Insert before the ✕ button (last widget in header)
        cancel_idx = self._header_layout.indexOf(self._cancel_btn)
        self._header_layout.insertWidget(cancel_idx, self._refresh_btn)

    # ── Content ───────────────────────────────────────────────────

    def _build_content(self, layout: QVBoxLayout):
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Message scroll area ───────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent; width: 5px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,15); border-radius: 2px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)

        self._msg_container = QWidget()
        self._msg_container.setStyleSheet("background: transparent;")
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setContentsMargins(14, 14, 14, 10)
        self._msg_layout.setSpacing(16)
        self._msg_layout.addStretch()

        self._scroll.setWidget(self._msg_container)
        layout.addWidget(self._scroll, 1)

        # ── Input area ────────────────────────────────────────────
        layout.addWidget(self._build_input_area())

    # ── Input area — unified bar with buttons inside ────────────

    def _build_input_area(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        w_layout = QVBoxLayout(wrapper)
        w_layout.setContentsMargins(14, 6, 14, 14)
        w_layout.setSpacing(4)

        # File indicator (shown above input when file is attached)
        self._file_label = QLabel("")
        self._file_label.setFixedHeight(0)  # hidden initially
        self._file_label.setStyleSheet(
            "color: rgba(50,140,255,200); font-size: 11px;"
            " background: transparent; padding-left: 8px;"
        )
        w_layout.addWidget(self._file_label)

        # ── Unified input bar ─────────────────────────────────────
        # One rounded container holding: [+ attach] [text input] [↑ send]
        bar = QWidget()
        bar.setFixedHeight(46)
        bar.setStyleSheet("""
            QWidget#inputBar {
                background: rgba(255,255,255,5);
                border: 1px solid rgba(255,255,255,8);
                border-radius: 23px;
            }
        """)
        bar.setObjectName("inputBar")

        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(6, 4, 6, 4)
        bar_layout.setSpacing(4)

        # ── Attach button (+ icon) ────────────────────────────────
        self._file_btn = QPushButton("+")
        self._file_btn.setFixedSize(32, 32)
        self._file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._file_btn.setToolTip("Attach a file")
        self._file_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,6);
                color: rgba(255,255,255,150);
                border: none;
                border-radius: 16px;
                font-size: 22px;
                font-weight: 300;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,14);
                color: rgba(255,255,255,220);
            }
            QPushButton:pressed {
                background: rgba(50,120,240,30);
            }
        """)
        self._file_btn.clicked.connect(self._attach_file)
        bar_layout.addWidget(self._file_btn)

        # ── Screenshot button (camera icon) ──────────────────────
        self._screen_btn = _VectorButton("camera")
        self._screen_btn.setFixedSize(32, 32)
        self._screen_btn.setToolTip("Take screenshot")
        self._screen_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,6);
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,14);
            }
            QPushButton:pressed {
                background: rgba(50,120,240,30);
            }
        """)
        self._screen_btn.clicked.connect(self._initiate_screenshot)
        bar_layout.addWidget(self._screen_btn)

        # ── Text input (borderless, transparent) ──────────────────
        self._input = QTextEdit()
        self._input.setPlaceholderText("Ask Sentinel anything...")
        self._input.setAcceptRichText(False)
        self._input.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._input.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: rgba(255,255,255,210);
                border: none;
                padding: 6px 8px;
                font-size: 13px;
                font-family: '.AppleSystemUIFont';
            }
        """)
        self._input.installEventFilter(self)
        bar_layout.addWidget(self._input, 1)

        # ── Send button (blue circle ↑) ───────────────────────────
        self._send_btn = QPushButton("↑")
        self._send_btn.setFixedSize(34, 34)
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(55,140,255,255),
                    stop:1 rgba(40,110,240,255)
                );
                color: white; border: none;
                border-radius: 17px;
                font-size: 19px; font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(70,155,255,255),
                    stop:1 rgba(50,125,250,255)
                );
            }
            QPushButton:pressed { background: rgba(30,90,210,255); }
            QPushButton:disabled {
                background: rgba(50,120,240,50);
                color: rgba(255,255,255,50);
            }
        """)
        self._send_btn.clicked.connect(self._send_message)
        bar_layout.addWidget(self._send_btn)

        w_layout.addWidget(bar)
        return wrapper

    # ── Events ────────────────────────────────────────────────────

    def eventFilter(self, obj, event):
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if (event.key() == Qt.Key.Key_Return
                    and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _attach_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Attach File", "",
            "All Files (*);;Text (*.txt);;Python (*.py);;Markdown (*.md)",
        )
        if path:
            filename = path.rsplit("/", 1)[-1]
            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

            try:
                if ext in ["png", "jpg", "jpeg", "webp"]:
                    import base64
                    with open(path, "rb") as f:
                        data = base64.b64encode(f.read()).decode("utf-8")
                    content = f"data:image/{ext};base64,{data}"
                    is_image = True
                else:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read(50_000)
                    is_image = False

                self._attached_file = {
                    "name": filename,
                    "content": content,
                    "is_image": is_image
                }
                self._file_label.setText(f"{filename}")
                self._file_label.setFixedHeight(16)
            except Exception as e:
                self._file_label.setText(f"Error: {e}")
                self._file_label.setFixedHeight(16)

    def _initiate_screenshot(self):
        """Hide app and schedule screenshot."""
        self._windows_to_restore = []
        # Find all top-level widgets of the application
        for widget in QApplication.topLevelWidgets():
            if not widget.isHidden() and widget.isVisible():
                self._windows_to_restore.append(widget)
                widget.hide()
        
        # Wait for the window manager to process the hide
        QTimer.singleShot(300, self._capture_and_restore)

    def _capture_and_restore(self):
        """Capture screen and restore app visibility."""
        screen = self.screen()
        if not screen:
            screen = QApplication.primaryScreen()
        
        # Grab the entire screen (window=0)
        pixmap = screen.grabWindow(0)
        
        # Restore windows
        for widget in self._windows_to_restore:
            widget.show()
            # Try to re-assert "on top" if relevant (Mac-specific fix)
            if hasattr(widget, '_reassert_on_top'):
                try:
                    widget._reassert_on_top()
                except Exception:
                    pass
        
        self._process_screenshot(pixmap)

    def _process_screenshot(self, pixmap):
        """Convert pixmap to base64 and attach."""
        if pixmap.isNull():
            self._file_label.setText("Error: Screenshot failed")
            self._file_label.setFixedHeight(16)
            return

        ba = QBuffer()
        ba.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(ba, "PNG") 
        data = ba.data().toBase64().data().decode("utf-8")
        
        filename = f"screenshot_{int(time.time())}.png"
        
        self._attached_file = {
            "name": filename,
            "content": f"data:image/png;base64,{data}",
            "is_image": True
        }
        self._file_label.setText(filename)
        self._file_label.setFixedHeight(16)

    # ── Send / receive ────────────────────────────────────────────

    def _send_message(self):
        text = self._input.toPlainText().strip()
        if not text and not self._attached_file:
            return

        # ── Build display text (for bubble) vs API text (for model) ──
        display_text = text
        api_content = text
        attached_name = None

        if self._attached_file:
            attached_name = self._attached_file["name"]
            
            if self._attached_file.get("is_image"):
                # Multimodal payload for images
                api_content = [
                    {"type": "text", "text": text or "What is in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": self._attached_file["content"]}
                    }
                ]
            else:
                # Text file: append content
                api_content = (
                    f"[File: {attached_name}]\n"
                    f"```\n{self._attached_file['content']}\n```\n\n"
                    + text
                )
            
            self._attached_file = None
            self._file_label.setText("")
            self._file_label.setFixedHeight(0)

        # Show clean bubble — file appears as a badge, not raw content
        self._add_message("user", display_text, attached_name=attached_name)
        self._input.clear()
        self._messages.append({"role": "user", "content": api_content})

        if self._client and self._api_key:
            self._set_loading(True)
            self._request_start = time.time()
            self._worker = ChatWorker(self._client, list(self._messages))
            self._worker.response_ready.connect(self._on_response)
            self._worker.error_occurred.connect(self._on_error)
            self._worker.start()
        else:
            self._add_message(
                "assistant",
                "⚠️ No API key configured.\n"
                "Start with: make up MODEL=gpt-4 API_KEY=sk-xxx",
            )

    def _on_response(self, text: str):
        self._set_loading(False)
        self._messages.append({"role": "assistant", "content": text})
        
        latency = time.time() - self._request_start
        self._add_message("assistant", text, latency=latency)

    def _on_error(self, error: str):
        self._set_loading(False)
        self._add_message("assistant", f"⚠️ {error}")

    def _set_loading(self, loading: bool):
        self._send_btn.setEnabled(not loading)
        self._send_btn.setText("…" if loading else "↑")
        if loading:
            self._show_typing_indicator()
        else:
            self._hide_typing_indicator()

    # ── Typing indicator ──────────────────────────────────────────

    def _show_typing_indicator(self):
        if self._typing_indicator is None:
            self._typing_indicator = _TypingIndicator()
            idx = self._msg_layout.count() - 1
            self._msg_layout.insertWidget(idx, self._typing_indicator)
            QTimer.singleShot(50, self._scroll_to_bottom)

    def _hide_typing_indicator(self):
        if self._typing_indicator is not None:
            self._typing_indicator.stop()
            self._typing_indicator.setParent(None)
            self._typing_indicator.deleteLater()
            self._typing_indicator = None

    def _add_message(self, role: str, content: str,
                     attached_name: str = None, latency: float = None):
        idx = self._msg_layout.count() - 1
        bubble = _ChatBubble(
            role, content, attached_name=attached_name, latency=latency
        )
        self._msg_layout.insertWidget(idx, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _reset_conversation(self):
        """Clear all messages and start a fresh conversation."""
        # Remove all bubble widgets (keep the stretch at the end)
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reset state
        self._messages.clear()
        self._hide_typing_indicator()
        self._attached_file = None
        self._file_label.setText("")
        self._file_label.setFixedHeight(0)
        self._input.clear()
        self._send_btn.setEnabled(True)
        self._send_btn.setText("↑")


# ══════════════════════════════════════════════════════════════════
#  Custom-painted chat bubble for proper rounded corners
# ══════════════════════════════════════════════════════════════════

class _ChatBubble(QWidget):
    """
    Custom-painted message bubble.
    Uses QPainter for pixel-perfect rounded corners (no CSS bleeding).
    """

    # colors
    _AI_BG = QColor(28, 34, 48)       # richer dark blue-gray
    _USER_BG = QColor(37, 99, 235)
    _AI_TEXT = QColor(195, 205, 218)   # slightly warmer
    _USER_TEXT = QColor(255, 255, 255)
    _TS_COLOR = QColor(255, 255, 255, 55)

    def __init__(self, role: str, content: str,
                 attached_name: str = None, latency: float = None, parent=None):
        super().__init__(parent)
        self._role = role
        self._content = content
        self._is_user = role == "user"
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # ── Bubble row ────────────────────────────────────────────
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        if self._is_user:
            bubble = _BubbleBody(
                content, self._USER_BG, self._USER_TEXT,
                is_rich=False, file_name=attached_name,
            )
        else:
            html = _md_to_html(content)
            bubble = _BubbleBody(
                html, self._AI_BG, self._AI_TEXT, is_rich=True,
            )
        bubble.setMaximumWidth(420)

        if self._is_user:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()

        layout.addLayout(row)

        # ── Timestamp / Metadata row ──────────────────────────────
        ts_text = datetime.now().strftime("%I:%M %p")
        if latency is not None:
            ts_text += f" • {latency:.2f}s"

        ts_row = QHBoxLayout()
        ts_row.setContentsMargins(4, 0, 4, 0)
        ts_row.setSpacing(8)

        # Timestamp label
        ts = QLabel(ts_text)
        ts.setFont(QFont(".AppleSystemUIFont", 10))
        ts.setStyleSheet("color: rgba(255,255,255,40); background: transparent;")

        if self._is_user:
            ts_row.addStretch()
            ts_row.addWidget(ts)
        else:
            # For AI: [Timestamp] [Copy Button]
            ts_row.addWidget(ts)
            
            # Copy button
            self._copy_btn = QPushButton("⧉")
            self._copy_btn.setFixedSize(60, 20)
            self._copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._copy_btn.setToolTip("Copy to clipboard")
            self._copy_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: rgba(255,255,255,40); font-size: 14px;
                    text-align: left;
                }
                QPushButton:hover { color: rgba(255,255,255,180); }
            """)
            self._copy_btn.clicked.connect(self._copy_content)
            ts_row.addWidget(self._copy_btn)
            
            ts_row.addStretch()

        layout.addLayout(ts_row)

    def _copy_content(self):
        cb = QApplication.clipboard()
        cb.setText(self._content)
        
        # Feedback animation
        self._copy_btn.setText("✓ Copied!")
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: rgba(255,255,255,220); font-size: 11px; font-weight: bold;
                text-align: left;
            }
        """)
        QTimer.singleShot(2000, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self._copy_btn.setText("⧉")
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: rgba(255,255,255,40); font-size: 14px;
                text-align: left;
            }
            QPushButton:hover { color: rgba(255,255,255,180); }
        """)


# ══════════════════════════════════════════════════════════════════
#  Bubble body — QPainter bg + QLabel rich text
# ══════════════════════════════════════════════════════════════════

class _BubbleBody(QWidget):
    """Rounded-rect bg (QPainter) + QLabel child for text/HTML."""

    RADIUS = 14
    PAD_H = 14
    PAD_V = 10

    def __init__(self, content: str, bg: QColor, text_color: QColor,
                 is_rich: bool = False, file_name: str = None, parent=None):
        super().__init__(parent)
        self._bg = bg
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.PAD_H, self.PAD_V, self.PAD_H, self.PAD_V)
        layout.setSpacing(6)

        # ── File Chip (if attached) ───────────────────────────────
        if file_name:
            chip = QFrame()
            chip.setStyleSheet("""
                QFrame {
                    background: rgba(0,0,0,0.2);
                    border-radius: 6px;
                }
            """)
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(8, 6, 8, 6)
            chip_layout.setSpacing(6)

            name = QLabel(file_name)
            name.setStyleSheet("color: rgba(255,255,255,220); font-weight: 500;")
            chip_layout.addWidget(name)
            chip_layout.addStretch()

            layout.addWidget(chip)

        self._label = QLabel(content)
        self._label.setWordWrap(True)
        self._label.setTextFormat(
            Qt.TextFormat.RichText if is_rich else Qt.TextFormat.PlainText
        )
        self._label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self._label.setOpenExternalLinks(True)
        self._label.setFont(QFont(".AppleSystemUIFont", 13))
        c = text_color
        self._label.setStyleSheet(
            f"color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()});"
            " background: transparent; line-height: 140%;"
        )
        self._label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum,
        )
        layout.addWidget(self._label)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0, 0, self.width(), self.height()),
            self.RADIUS, self.RADIUS,
        )
        p.fillPath(path, self._bg)
        p.end()


# ══════════════════════════════════════════════════════════════════
#  Markdown → Qt-compatible HTML
# ══════════════════════════════════════════════════════════════════

import re
import html as _html_mod


def _md_to_html(md: str) -> str:
    """Convert markdown to Qt rich-text HTML."""
    # Step 1: extract fenced code blocks
    segs = []
    last = 0
    for m in re.finditer(r'```(\w*)\n?(.*?)```', md, re.DOTALL):
        segs.append(("t", md[last:m.start()]))
        code = _html_mod.escape(m.group(2).rstrip())
        segs.append(("c", code))
        last = m.end()
    segs.append(("t", md[last:]))

    parts = []
    for kind, content in segs:
        if kind == "c":
            parts.append(
                '<pre style="background:rgba(0,0,0,0.35);'
                'padding:8px 10px;border-radius:6px;'
                'font-family:Menlo,monospace;font-size:11px;'
                f'color:#c0cad6;margin:6px 0;">{content}</pre>'
            )
        else:
            parts.append(_md_blocks(content))
    return "".join(parts)


def _md_blocks(text: str) -> str:
    """Process block-level markdown."""
    lines = text.split("\n")
    out = []
    in_ul = in_ol = False

    for line in lines:
        s = line.strip()
        if in_ul and not (s.startswith("- ") or s.startswith("* ")):
            out.append("</ul>"); in_ul = False
        if in_ol and not re.match(r"^\d+\.\s", s):
            out.append("</ol>"); in_ol = False
        if not s:
            out.append("<br>"); continue

        # headers
        for lvl, pfx in [(3, "### "), (2, "## "), (1, "# ")]:
            if s.startswith(pfx):
                sz = 13 + (3 - lvl)
                out.append(f'<b style="font-size:{sz}px;color:#e8ecf0;">'
                           f'{_inl(s[len(pfx):])}</b><br>')
                break
        else:
            # bullet list
            if s.startswith("- ") or s.startswith("* "):
                if not in_ul:
                    out.append('<ul style="margin:2px 0;padding-left:18px;">')
                    in_ul = True
                out.append(f"<li>{_inl(s[2:])}</li>")
            # numbered list
            elif (m := re.match(r"^\d+\.\s(.*)", s)):
                if not in_ol:
                    out.append('<ol style="margin:2px 0;padding-left:18px;">')
                    in_ol = True
                out.append(f"<li>{_inl(m.group(1))}</li>")
            else:
                out.append(f"{_inl(s)}<br>")

    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    return "".join(out)


def _inl(text: str) -> str:
    """Inline markdown: bold, italic, code."""
    parts = re.split(r"(`[^`]+`)", text)
    res = []
    for p in parts:
        if p.startswith("`") and p.endswith("`"):
            c = _html_mod.escape(p[1:-1])
            res.append(
                '<code style="background:rgba(0,0,0,0.3);padding:1px 5px;'
                'border-radius:3px;font-family:Menlo,monospace;'
                f'font-size:11px;color:#c0cad6;">{c}</code>'
            )
        else:
            p = re.sub(r"\*\*(.+?)\*\*", r'<b style="color:#e8ecf0;">\1</b>', p)
            p = re.sub(r"__(.+?)__", r'<b style="color:#e8ecf0;">\1</b>', p)
            p = re.sub(r"\*(.+?)\*", r"<i>\1</i>", p)
            res.append(p)
    return "".join(res)


# ══════════════════════════════════════════════════════════════════
#  Animated typing indicator (three pulsing dots)
# ══════════════════════════════════════════════════════════════════

class _TypingIndicator(QWidget):
    """Three animated dots inside a dark rounded bubble."""

    _BG = QColor(28, 34, 48)
    _DOT_COLOR = QColor(140, 150, 165)
    _DOT_R = 4.0
    _GAP = 14.0
    _W = 70
    _H = 38
    _CR = 14.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self._W + 8, self._H + 8)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(150)

    def stop(self):
        self._timer.stop()

    def _tick(self):
        self._phase = (self._phase + 1) % 12
        self.update()

    def _alpha(self, i: int) -> float:
        import math
        t = ((self._phase + i * 3) % 12) / 12.0
        return 0.3 + 0.7 * abs(math.sin(t * math.pi))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bx, by = 0.0, 4.0
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(bx, by, self._W, self._H), self._CR, self._CR,
        )
        p.fillPath(path, self._BG)
        cx, cy = bx + self._W / 2.0, by + self._H / 2.0
        sx = cx - self._GAP
        for i in range(3):
            c = QColor(self._DOT_COLOR)
            c.setAlphaF(self._alpha(i))
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            dx = sx + i * self._GAP
            p.drawEllipse(QRectF(
                dx - self._DOT_R, cy - self._DOT_R,
                self._DOT_R * 2, self._DOT_R * 2,
            ))
        p.end()


class _VectorButton(QPushButton):
    """Button that draws a vector icon using app.icons.draw_icon."""

    def __init__(self, icon_id: str, parent=None):
        super().__init__(parent)
        self._icon_id = icon_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        # Draw standard background (stylesheet)
        super().paintEvent(event)

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Color based on state (matching other chat buttons)
        if self.isDown():
            c = QColor(255, 255, 255, 255)
        elif self.underMouse():
            c = QColor(255, 255, 255, 220)
        else:
            c = QColor(255, 255, 255, 150)

        # Center the icon (size 18 seems appropriate for 32x32 button)
        s = 18
        off_x = (self.width() - s) / 2
        off_y = (self.height() - s) / 2
        
        draw_icon(p, self._icon_id, QRectF(off_x, off_y, s, s), c)
        p.end()

