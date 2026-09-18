"""
Entry point for the Robota.ua Remote Vacancies Explorer desktop application.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure application root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def resource_path(name: str) -> Path:
    """Resolve a bundled resource both in source and PyInstaller builds."""
    bundle_dir = Path(getattr(sys, "_MEIPASS", BASE_DIR))
    return bundle_dir / name

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

from storage import SettingsManager
from ui.main_window import MainWindow
from ui.styles import get_theme_stylesheet


def main() -> None:
    # Set Windows App ID for proper taskbar grouping
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "robotaua.vacancyexplorer.desktop.v1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Robota.ua Remote Vacancies Explorer")
    app.setApplicationDisplayName("Robota.ua Remote Vacancies Explorer")
    app.setOrganizationName("Antigravity")
    icon_path = resource_path("JobSniffer.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Set modern default font
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Load settings and apply saved theme
    settings = SettingsManager()
    app.setStyleSheet(get_theme_stylesheet(settings.theme))

    # Launch main window
    window = MainWindow(settings_manager=settings)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
