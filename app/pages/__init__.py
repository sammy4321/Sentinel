"""
Pages package for Sentinel popup sub-pages.
Each page is a separate screen navigable from the main menu.
"""

from app.pages.base_page import BasePage
from app.pages.chat_page import ChatPage
from app.pages.guide_page import GuidePage
from app.pages.action_page import ActionPage

__all__ = ["BasePage", "ChatPage", "GuidePage", "ActionPage"]
