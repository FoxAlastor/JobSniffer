"""
Detailed vacancy view pane with rich preview and action buttons.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices, QGuiApplication, QPalette
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from models import Vacancy
from workers import FetchVacancyDetailWorker


class VacancyDetailWidget(QWidget):
    """Widget displaying full details and description of the selected vacancy."""

    request_blacklist_word = pyqtSignal(str)
    request_block_vacancy = pyqtSignal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_vacancy: Optional[Vacancy] = None
        self._detail_worker: Optional[FetchVacancyDetailWorker] = None
        self.is_dark: bool = False
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Info Card
        self.header_card = QFrame()
        self.header_card.setProperty("class", "cardFrame")
        self._apply_card_styles()

        header_layout = QVBoxLayout(self.header_card)
        header_layout.setSpacing(6)

        # Vacancy Title
        self.title_label = QLabel("Оберіть вакансію для перегляду")
        self.title_label.setWordWrap(True)
        self._set_title_color("#1e293b")
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        header_layout.addWidget(self.title_label)

        # Subtitle: Company & Location
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(8)

        self.company_label = QLabel("")
        self.company_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #3b82f6;")
        self.company_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        sub_layout.addWidget(self.company_label)

        self.remote_badge = QLabel("🌐 Remote")
        self.remote_badge.setStyleSheet(
            "background-color: #dbeafe; color: #1d4ed8; border-radius: 4px; "
            "padding: 2px 6px; font-weight: 600; font-size: 11px;"
        )
        sub_layout.addWidget(self.remote_badge)

        self.hot_badge = QLabel("🔥 Гаряча")
        self.hot_badge.setStyleSheet(
            "background-color: #ffedd5; color: #c2410c; border-radius: 4px; "
            "padding: 2px 6px; font-weight: 600; font-size: 11px;"
        )
        sub_layout.addWidget(self.hot_badge)

        sub_layout.addStretch()

        self.date_label = QLabel("")
        self.date_label.setStyleSheet("color: #64748b; font-size: 12px;")
        sub_layout.addWidget(self.date_label)

        header_layout.addLayout(sub_layout)

        # Salary Highlight Banner
        self.salary_banner = QFrame()
        self._apply_salary_banner_style()

        salary_layout = QHBoxLayout(self.salary_banner)
        salary_layout.setContentsMargins(8, 4, 8, 4)
        
        self.salary_icon = QLabel("💰 Зарплата:")
        self.salary_icon.setStyleSheet("color: #065f46; font-weight: 600; font-size: 13px;")
        salary_layout.addWidget(self.salary_icon)

        self.salary_text = QLabel("Не вказано")
        self.salary_text.setStyleSheet("color: #047857; font-weight: 700; font-size: 14px;")
        salary_layout.addWidget(self.salary_text)
        salary_layout.addStretch()

        header_layout.addWidget(self.salary_banner)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.open_btn = QPushButton("🌐 Відкрити")
        self.open_btn.setProperty("class", "primaryButton")
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn.clicked.connect(self._open_in_browser)
        self.open_btn.setEnabled(False)
        btn_layout.addWidget(self.open_btn)

        self.copy_btn = QPushButton("📋 Скопіювати")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_link)
        self.copy_btn.setEnabled(False)
        btn_layout.addWidget(self.copy_btn)

        self.blacklist_word_btn = QPushButton("🚫 Додати в ЧС")
        self.blacklist_word_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.blacklist_word_btn.setToolTip("Додати слово з цієї вакансії в чорний список")
        self.blacklist_word_btn.clicked.connect(self._on_quick_blacklist)
        self.blacklist_word_btn.setEnabled(False)
        btn_layout.addWidget(self.blacklist_word_btn)

        self.block_vacancy_btn = QPushButton("🚫 Приховати")
        self.block_vacancy_btn.setProperty("class", "dangerButton")
        self.block_vacancy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.block_vacancy_btn.setToolTip("Приховати лише цю вакансію, не блокуючи слова")
        self.block_vacancy_btn.clicked.connect(self._on_block_vacancy)
        self.block_vacancy_btn.setEnabled(False)
        btn_layout.addWidget(self.block_vacancy_btn)

        header_layout.addLayout(btn_layout)
        layout.addWidget(self.header_card)

        # Description Header & Loading indicator
        desc_header_layout = QHBoxLayout()
        self.desc_title = QLabel("Опис вакансії:")
        self.desc_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        desc_header_layout.addWidget(self.desc_title)
        desc_header_layout.addStretch()

        self.loading_indicator = QLabel("⏳ Завантаження повного опису...")
        self.loading_indicator.setStyleSheet("color: #3b82f6; font-size: 12px; font-style: italic;")
        self.loading_indicator.setVisible(False)
        desc_header_layout.addWidget(self.loading_indicator)

        layout.addLayout(desc_header_layout)

        # Full Description Browser
        self.desc_browser = QTextBrowser()
        self.desc_browser.setOpenExternalLinks(True)
        self.desc_browser.setPlaceholderText("Оберіть вакансію у таблиці ліворуч для перегляду її повного опису.")
        layout.addWidget(self.desc_browser, stretch=1)

        self._reset_view()

    def set_dark_theme(self, is_dark: bool) -> None:
        """Update widget sub-styles for dark or light theme."""
        self.is_dark = is_dark
        # Match the base foreground colour from the application theme exactly.
        title_color = "#f1f5f9" if is_dark else "#1e293b"
        self._set_title_color(title_color)
        self._apply_card_styles()
        self._apply_salary_banner_style()
        if self.current_vacancy:
            self._render_description(self.current_vacancy)

    def _set_title_color(self, color: str) -> None:
        """Force the vacancy title colour instead of inheriting a frame palette."""
        self.title_label.setStyleSheet(
            f"QLabel {{ font-size: 16px; font-weight: 700; color: {color}; }}"
        )
        palette = self.title_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color))
        self.title_label.setPalette(palette)

    def _apply_card_styles(self) -> None:
        if self.is_dark:
            self.header_card.setStyleSheet("""
                QFrame.cardFrame {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
        else:
            self.header_card.setStyleSheet("""
                QFrame.cardFrame {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)

    def _apply_salary_banner_style(self) -> None:
        if self.is_dark:
            self.salary_banner.setStyleSheet("""
                QFrame {
                    background-color: #064e3b;
                    border: 1px solid #059669;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
            """)
            if hasattr(self, "salary_icon"):
                self.salary_icon.setStyleSheet("color: #a7f3d0; font-weight: 600; font-size: 13px;")
                self.salary_text.setStyleSheet("color: #6ee7b7; font-weight: 700; font-size: 14px;")
        else:
            self.salary_banner.setStyleSheet("""
                QFrame {
                    background-color: #ecfdf5;
                    border: 1px solid #a7f3d0;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
            """)
            if hasattr(self, "salary_icon"):
                self.salary_icon.setStyleSheet("color: #065f46; font-weight: 600; font-size: 13px;")
                self.salary_text.setStyleSheet("color: #047857; font-weight: 700; font-size: 14px;")

    def _reset_view(self) -> None:
        """Reset view when nothing is selected."""
        self.title_label.setText("Оберіть вакансію для перегляду")
        self.company_label.setText("")
        self.remote_badge.setVisible(False)
        self.hot_badge.setVisible(False)
        self.date_label.setText("")
        self.salary_text.setText("—")
        self.open_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.blacklist_word_btn.setEnabled(False)
        self.block_vacancy_btn.setEnabled(False)
        self.desc_browser.clear()
        self.loading_indicator.setVisible(False)

    def set_vacancy(self, vacancy: Optional[Vacancy]) -> None:
        """Display details for the selected vacancy."""
        self.current_vacancy = vacancy
        if not vacancy:
            self._reset_view()
            return

        self.title_label.setText(vacancy.name)
        self.company_label.setText(f"🏢 {vacancy.company_name} ({vacancy.city_name or 'Україна'})")
        self.remote_badge.setVisible(vacancy.is_remote)
        self.hot_badge.setVisible(vacancy.hot)
        self.date_label.setText(f"📅 {vacancy.formatted_date}")
        self.salary_text.setText(vacancy.formatted_salary)

        self.open_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.blacklist_word_btn.setEnabled(True)
        self.block_vacancy_btn.setEnabled(True)

        # Initial render of short description or existing description
        self._render_description(vacancy)

        # If full description is not loaded yet, fetch in background
        if not vacancy.full_description and vacancy.id:
            if self._detail_worker and self._detail_worker.isRunning():
                try:
                    self._detail_worker.detail_ready.disconnect()
                except Exception:
                    pass
            self.loading_indicator.setVisible(True)
            self._detail_worker = FetchVacancyDetailWorker(vacancy.id, parent=self)
            self._detail_worker.detail_ready.connect(self._on_detail_fetched)
            self._detail_worker.start()
        else:
            self.loading_indicator.setVisible(False)

    def _on_detail_fetched(self, detailed_vacancy: Optional[Vacancy]) -> None:
        self.loading_indicator.setVisible(False)
        if detailed_vacancy and self.current_vacancy and detailed_vacancy.id == self.current_vacancy.id:
            self.current_vacancy.full_description = detailed_vacancy.full_description
            if detailed_vacancy.salary_comment and not self.current_vacancy.salary_comment:
                self.current_vacancy.salary_comment = detailed_vacancy.salary_comment
                self.salary_text.setText(self.current_vacancy.formatted_salary)
            self._render_description(self.current_vacancy)

    def _render_description(self, vacancy: Vacancy) -> None:
        """Format and set HTML in text browser."""
        content = vacancy.full_description or vacancy.short_description or "Опис відсутній."
        
        bg_color = "#1e293b" if self.is_dark else "#ffffff"
        text_color = "#e2e8f0" if self.is_dark else "#1e293b"
        heading_color = "#f8fafc" if self.is_dark else "#0f172a"
        link_color = "#60a5fa" if self.is_dark else "#2563eb"
        
        html_styled = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', -apple-system, sans-serif;
                    font-size: 13px;
                    color: {text_color};
                    line-height: 1.6;
                    background-color: {bg_color};
                }}
                h1, h2, h3, h4 {{
                    color: {heading_color};
                    margin-top: 14px;
                    margin-bottom: 6px;
                }}
                p {{
                    margin-bottom: 8px;
                }}
                ul, ol {{
                    margin-top: 4px;
                    margin-bottom: 10px;
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 4px;
                }}
                strong, b {{
                    color: {heading_color};
                }}
                a {{
                    color: {link_color};
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        self.desc_browser.setHtml(html_styled)

    def _open_in_browser(self) -> None:
        if self.current_vacancy:
            QDesktopServices.openUrl(QUrl(self.current_vacancy.url))

    def _copy_link(self) -> None:
        if self.current_vacancy:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(self.current_vacancy.url)
            self.copy_btn.setText("✓ Скопійовано!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋 Скопіювати"))

    def _on_quick_blacklist(self) -> None:
        if not self.current_vacancy:
            return
        
        title = self.current_vacancy.name
        word, ok = QInputDialog.getText(
            self,
            "Додати в чорний список",
            "Введіть слово або фразу для додавання в чорний список:",
            text=title
        )
        if ok and word.strip():
            self.request_blacklist_word.emit(word.strip())

    def _on_block_vacancy(self) -> None:
        """Request hiding the current vacancy without adding words to the blacklist."""
        if self.current_vacancy:
            self.request_block_vacancy.emit(self.current_vacancy)

    def hideEvent(self, event) -> None:
        if self._detail_worker and self._detail_worker.isRunning():
            self._detail_worker.wait(500)
        super().hideEvent(event)
