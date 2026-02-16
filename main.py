"""
Sentinel - macOS Floating Assistant Application

Entry point for the Sentinel application.
A floating button application with a popup menu for quick access to
Chat, Guide, and Action functionalities.

Usage:
    python main.py --model gpt-4 --api_key sk-xxx

    # Or via Makefile:
    make up MODEL=gpt-4 API_KEY=sk-xxx
"""

import sys
import argparse

from PyQt6.QtWidgets import QApplication

try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    HAS_APPKIT = True
except ImportError:
    print("Warning: AppKit not found. macOS specific features will be disabled.")
    HAS_APPKIT = False

from app.floating_button import FloatingButton


def main():
    """Main entry point for the Sentinel application."""
    parser = argparse.ArgumentParser(description="Sentinel - macOS Floating Assistant")
    parser.add_argument("--model", type=str, default="AI",
                        help="Model name to display (e.g. gpt-4, claude-3)")
    parser.add_argument("--api_key", type=str, default="",
                        help="API key for the model provider")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    if HAS_APPKIT:
        NSApplication.sharedApplication().setActivationPolicy_(
            NSApplicationActivationPolicyAccessory
        )

    ex = FloatingButton(model=args.model, api_key=args.api_key)
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
