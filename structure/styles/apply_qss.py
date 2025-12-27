import os
from PyQt5.QtWidgets import QApplication, QWidget


# ==================================================
# Global QSS Style Manager
# ==================================================

class StyleManager:
    """
    Centralized manager for QSS (Qt Style Sheets).
    """

    # Internal cache to store already loaded QSS files
    # Key: file path | Value: QSS content
    _cached_styles = {}


    # ==================================================
    # QSS Loading
    # ==================================================

    @staticmethod
    def load_qss(path: str) -> str:

        # Validate file existence
        if not os.path.exists(path):
            raise FileNotFoundError(f"QSS file not found: {path}")

        # Load and cache QSS only once
        if path not in StyleManager._cached_styles:
            with open(path, "r", encoding="utf-8") as f:
                StyleManager._cached_styles[path] = f.read()

        return StyleManager._cached_styles[path]


    # ==================================================
    # Global Style Application
    # ==================================================

    @staticmethod
    def apply_to_app(app: QApplication, qss_path: str):

        style = StyleManager.load_qss(qss_path)
        app.setStyleSheet(style)


    # ==================================================
    # Widget-Specific Style Application
    # ==================================================

    @staticmethod
    def apply_to_widget(widget: QWidget, qss_path: str):

        style = StyleManager.load_qss(qss_path)
        widget.setStyleSheet(style)


    # ==================================================
    # Style Reset
    # ==================================================

    @staticmethod
    def clear_app_style(app: QApplication):
        app.setStyleSheet("")