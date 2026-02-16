"""
Sentinel - macOS Floating Assistant Application

A floating button application with a popup menu for quick access to
Chat, Guide, and Action functionalities.
"""

from app.floating_button import FloatingButton
from app.popup_menu import PopupMenu
from app.menu_option import MenuOption
from app.icons import draw_icon
from app.openrouter import OpenRouterClient, ChatWorker
from app.constants import COLORS, MENU_ITEMS, MENU_WIDTH, MENU_ITEM_HEIGHT

__all__ = [
    "FloatingButton",
    "PopupMenu",
    "MenuOption",
    "draw_icon",
    "OpenRouterClient",
    "ChatWorker",
    "COLORS",
    "MENU_ITEMS",
    "MENU_WIDTH",
    "MENU_ITEM_HEIGHT",
]
