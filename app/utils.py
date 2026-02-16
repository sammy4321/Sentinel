"""
Utility functions for Sentinel application.
Includes macOS-specific window configuration helpers.
"""

import sys
import ctypes

try:
    from AppKit import (
        NSWindowCollectionBehaviorCanJoinAllSpaces,
        NSWindowCollectionBehaviorFullScreenAuxiliary,
    )
    import objc
    HAS_APPKIT = True
except ImportError:
    print("Warning: AppKit/objc not found. macOS specific window features will be disabled.")
    HAS_APPKIT = False

from app.constants import MACOS_ON_TOP_LEVEL

# macOS-specific constants
_NSWindowCollectionBehaviorMoveToActiveSpace = 1 << 1
_NSWindowCollectionBehaviorIgnoresCycle = 1 << 6


def _apply_macos_top(widget, level: int = MACOS_ON_TOP_LEVEL):
    """
    Apply macOS always-on-top + all-Spaces behaviour to any QWidget.
    
    Args:
        widget: The QWidget to apply macOS window behavior to.
        level: The window level to set (default: MACOS_ON_TOP_LEVEL).
        
    Returns:
        The NSWindow object if successful, None otherwise.
    """
    if not HAS_APPKIT:
        return None
    try:
        win_id = widget.winId()
        ns_view = objc.objc_object(c_void_p=ctypes.c_void_p(int(win_id)))
        ns_window = ns_view.window()
        if ns_window:
            behavior = ns_window.collectionBehavior()
            behavior &= ~_NSWindowCollectionBehaviorMoveToActiveSpace
            behavior |= NSWindowCollectionBehaviorCanJoinAllSpaces
            behavior |= NSWindowCollectionBehaviorFullScreenAuxiliary
            behavior |= _NSWindowCollectionBehaviorIgnoresCycle
            ns_window.setCollectionBehavior_(behavior)
            ns_window.setLevel_(level)
            ns_window.setHidesOnDeactivate_(False)
            ns_window.orderFrontRegardless()
            return ns_window
    except Exception as e:
        print(f"Warning: macOS window setup failed – {e}")
    return None
