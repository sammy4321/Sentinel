"""
Design system constants for Sentinel application.
Matching the reference design exactly.
"""

from PyQt6.QtGui import QColor

# ── Window Configuration ───────────────────────────────────────────────
MACOS_ON_TOP_LEVEL = 1000

# ── Menu Dimensions ─────────────────────────────────────────────────────
MENU_WIDTH = 310
MENU_ITEM_HEIGHT = 58
MENU_RADIUS = 10            # tighter rounded corners
MENU_PADDING = 8

# ── Color Palette (matches reference image exactly) ────────────────────
COLORS = {
    # Three-zone card background (main menu)
    "bg_header": QColor(46, 46, 52, 255),       # Header — slightly lighter
    "bg_middle": QColor(36, 36, 42, 255),       # Items area — darker
    "bg_footer": QColor(46, 46, 52, 255),       # Footer — slightly lighter (same as header)

    # Sub-page backgrounds (two-zone: header lighter, content darker)
    "bg_subpage_header": QColor(44, 44, 50, 255),  # Sub-page header bar
    "bg_subpage_body": QColor(32, 32, 38, 255),    # Sub-page content area

    # Text
    "text_primary": QColor(255, 255, 255, 240),    # White for titles
    "text_secondary": QColor(160, 165, 175, 255),  # Gray for subtitles
    "text_footer": QColor(120, 125, 135, 255),      # Dimmer gray for footer

    # Icons
    "icon_stroke": QColor(50, 120, 240),            # Darker blue for icon lines
    "icon_container_bg": QColor(50, 120, 240, 30),  # Light blue tint for icon bg

    # Accents
    "dot_active": QColor(50, 120, 240),             # Blue status dot
    "separator": QColor(255, 255, 255, 12),         # Separator line
    "shadow": QColor(0, 0, 0, 80),                  # Drop shadow
    "border": QColor(255, 255, 255, 8),             # Card border
}

# ── Header / Footer ────────────────────────────────────────────────────
HEADER_TITLE = "Sentinel"
FOOTER_TEXT = "Powered by AI"

# ── Icon identifiers (drawn programmatically) ─────────────────────────
ICON_CHAT = "chat"
ICON_GUIDE = "guide"
ICON_ACTION = "action"

# ── Menu Items ─────────────────────────────────────────────────────────
MENU_ITEMS = [
    {"icon": ICON_CHAT,   "label": "Chat",        "desc": "Ask me anything"},
    {"icon": ICON_GUIDE,  "label": "Guide Me",    "desc": "Step-by-step assistance"},
    {"icon": ICON_ACTION, "label": "Take Action",  "desc": "Automate this task"},
]
