"""
Modern styles and palettes for the Robota.ua desktop application (Light & Dark themes).
"""

MODERN_LIGHT_STYLE = """
/* Global styling */
QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
    color: #1e293b;
    background-color: #f8fafc;
}

QMainWindow {
    background-color: #f1f5f9;
}

/* ToolBar & Top Header */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
    spacing: 10px;
}

/* Group Boxes & Frames */
QGroupBox {
    font-weight: 600;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 14px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #334155;
}

QFrame.cardFrame {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

/* Input Fields */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 12px;
    color: #0f172a;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1.5px solid #3b82f6;
    background-color: #ffffff;
}

QLineEdit:placeholder {
    color: #94a3b8;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
    color: #334155;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton:disabled {
    background-color: #f8fafc;
    border-color: #e2e8f0;
    color: #94a3b8;
}

/* Primary Action Buttons */
QPushButton.primaryButton {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    color: #ffffff;
    font-weight: 600;
}

QPushButton.primaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton.primaryButton:pressed {
    background-color: #1e40af;
}

QPushButton.successButton {
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
    font-weight: 600;
}

QPushButton.successButton:hover {
    background-color: #059669;
}

QPushButton.dangerButton {
    background-color: #fee2e2;
    border: 1px solid #fca5a5;
    color: #b91c1c;
    font-weight: 500;
}

QPushButton.dangerButton:hover {
    background-color: #fecaca;
    color: #991b1b;
}

/* Table View */
QTableView {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: #dbeafe;
    selection-color: #1e3a8a;
    outline: none;
}

QTableView::item {
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
}

QTableView::item:selected {
    background-color: #dbeafe;
    color: #1e3a8a;
}

QTableView::item:hover:!selected {
    background-color: #f8fafc;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    border-right: 1px solid #f1f5f9;
    padding: 8px 10px;
}

QHeaderView::section:hover {
    background-color: #f1f5f9;
}

/* List Widget */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #eff6ff;
    selection-color: #1e40af;
}

QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #f8fafc;
}

QListWidget::item:selected {
    background-color: #e0e7ff;
    color: #3730a3;
    font-weight: 500;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    color: #64748b;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-color: #e2e8f0;
    border-bottom: 1px solid #ffffff;
    color: #2563eb;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #334155;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 12px;
    color: #0f172a;
}

QComboBox:hover {
    border-color: #94a3b8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #e2e8f0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    padding: 4px;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    color: #334155;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #94a3b8;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #f1f5f9;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f1f5f9;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Splitter */
QSplitter::handle {
    background-color: #e2e8f0;
}

QSplitter::handle:hover {
    background-color: #3b82f6;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #475569;
    font-size: 12px;
    padding: 4px 8px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    text-align: center;
    background-color: #f1f5f9;
    height: 14px;
    font-size: 10px;
    color: #334155;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

/* TextBrowser (Details Pane) */
QTextBrowser {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    color: #1e293b;
    line-height: 1.5;
}
"""

MODERN_DARK_STYLE = """
/* Global styling - Dark Theme */
QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
    color: #f1f5f9;
    background-color: #1e293b;
}

QMainWindow {
    background-color: #090d16;
}

/* ToolBar & Top Header */
QToolBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 8px 12px;
    spacing: 10px;
}

/* Group Boxes & Frames */
QGroupBox {
    font-weight: 600;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 14px;
    background-color: #1e293b;
    color: #f8fafc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #94a3b8;
}

QFrame.cardFrame {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

/* Input Fields */
QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
    color: #f8fafc;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1.5px solid #3b82f6;
    background-color: #1e293b;
}

QLineEdit:placeholder {
    color: #64748b;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
    color: #e2e8f0;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1e293b;
}

QPushButton:disabled {
    background-color: #1e293b;
    border-color: #1e293b;
    color: #475569;
}

/* Primary Action Buttons */
QPushButton.primaryButton {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-weight: 600;
}

QPushButton.primaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton.primaryButton:pressed {
    background-color: #1e40af;
}

QPushButton.successButton {
    background-color: #065f46;
    border: 1px solid #059669;
    color: #6ee7b7;
    font-weight: 600;
}

QPushButton.successButton:hover {
    background-color: #047857;
}

QPushButton.dangerButton {
    background-color: #450a0a;
    border: 1px solid #991b1b;
    color: #fca5a5;
    font-weight: 500;
}

QPushButton.dangerButton:hover {
    background-color: #7f1d1d;
    color: #fecaca;
}

/* Table View */
QTableView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #1e293b;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
    alternate-background-color: #172033;
    outline: none;
}

QTableView::item {
    padding: 8px 10px;
    border-bottom: 1px solid #27354a;
    color: #f1f5f9;
}

QTableView::item:selected {
    background-color: #1e3a8a;
    color: #ffffff;
}

QTableView::item:hover:!selected {
    background-color: #27354a;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #334155;
    border-right: 1px solid #1e293b;
    padding: 8px 10px;
}

QHeaderView::section:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

/* List Widget */
QListWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
}

QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
    margin-bottom: 2px;
    color: #f1f5f9;
}

QListWidget::item:hover {
    background-color: #27354a;
}

QListWidget::item:selected {
    background-color: #1e3a8a;
    color: #ffffff;
    font-weight: 500;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #1e293b;
    top: -1px;
}

QTabBar::tab {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    color: #94a3b8;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    border-color: #334155;
    border-bottom: 1px solid #1e293b;
    color: #60a5fa;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #1b263b;
    color: #e2e8f0;
}

/* ComboBox */
QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f8fafc;
}

QComboBox:hover {
    border-color: #475569;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #334155;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
    color: #f8fafc;
    padding: 4px;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #475569;
    border-radius: 4px;
    background-color: #1e293b;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #3b82f6;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #1e293b;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #1e293b;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Splitter */
QSplitter::handle {
    background-color: #334155;
}

QSplitter::handle:hover {
    background-color: #3b82f6;
}

/* Status Bar */
QStatusBar {
    background-color: #1e293b;
    border-top: 1px solid #334155;
    color: #94a3b8;
    font-size: 12px;
    padding: 4px 8px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    background-color: #1e293b;
    height: 14px;
    font-size: 10px;
    color: #e2e8f0;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}

/* TextBrowser (Details Pane) */
QTextBrowser {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    color: #e2e8f0;
    line-height: 1.5;
}
"""


def get_theme_stylesheet(theme_name: str) -> str:
    """Return the QSS stylesheet for the given theme name."""
    if theme_name.lower() == "dark":
        return MODERN_DARK_STYLE
    return MODERN_LIGHT_STYLE
