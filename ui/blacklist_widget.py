"""
Blacklist management widget for filtering unwanted job listings.
"""

from __future__ import annotations
from typing import List, Optional
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from storage import SettingsManager


class BlacklistWidget(QWidget):
    """Widget for managing blacklisted keywords and phrases."""

    blacklist_changed = pyqtSignal()

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings = settings_manager
        self.is_dark = self.settings.theme == "dark"
        self._init_ui()
        self.reload_list()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header Title and Count
        header_layout = QHBoxLayout()
        self.title_label = QLabel("🚫 Чорний список слів і фраз")
        self.title_label.setStyleSheet("font-weight: 700; font-size: 15px;")
        
        self.count_badge = QLabel("0 слів")
        self.count_badge.setStyleSheet(
            "background-color: #fee2e2; color: #b91c1c; border-radius: 10px; "
            "padding: 2px 8px; font-weight: 600; font-size: 11px;"
        )
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.count_badge)
        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(
            "Будь-яка вакансія, що містить ці слова в назві чи описі, "
            "автоматично приховується з результатів."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(desc_label)

        # Add item row
        add_layout = QHBoxLayout()
        add_layout.setSpacing(6)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Додати слово/фразу (напр. 'касир', 'водій')...")
        self.input_field.returnPressed.connect(self._on_add_clicked)
        add_layout.addWidget(self.input_field)

        self.add_btn = QPushButton("+ Додати")
        self.add_btn.setProperty("class", "primaryButton")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self._on_add_clicked)
        add_layout.addWidget(self.add_btn)

        layout.addLayout(add_layout)

        # Fast local search in blacklist
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 Пошук у списку заборонених слів...")
        self.filter_input.textChanged.connect(self._filter_list_items)
        layout.addWidget(self.filter_input)

        # Blacklist items list widget
        self.list_widget = QListWidget()
        # Each item has its own row widget.  Alternating item backgrounds would
        # otherwise show through that widget as light stripes in the dark theme.
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setStyleSheet(
            "QListWidget { outline: none; }"
            "QListWidget::item { padding: 0px; margin: 0px; }"
        )
        layout.addWidget(self.list_widget)

        # Bottom Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        self.delete_selected_btn = QPushButton("🗑️ Видалити обране")
        self.delete_selected_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_selected_btn.clicked.connect(self._on_delete_selected)
        actions_layout.addWidget(self.delete_selected_btn)

        self.reset_btn = QPushButton("↺ Скинути до стандартних")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        actions_layout.addWidget(self.reset_btn)

        self.clear_btn = QPushButton("Очистити все")
        self.clear_btn.setProperty("class", "dangerButton")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        actions_layout.addWidget(self.clear_btn)

        layout.addLayout(actions_layout)

    def set_dark_theme(self, is_dark: bool) -> None:
        """Update widget theme."""
        self.is_dark = is_dark
        self.reload_list()

    def reload_list(self) -> None:
        """Reload words from settings into the list widget."""
        self.list_widget.clear()
        words = self.settings.blacklist
        self.count_badge.setText(f"{len(words)} слів")

        text_color = "#f8fafc" if self.is_dark else "#1e293b"

        for phrase in sorted(words, key=lambda s: s.lower()):
            item = QListWidgetItem(self.list_widget)
            # Do not set the visible item text: it would be painted underneath
            # the QLabel below, producing a duplicated/overlapping phrase.
            # Keep the phrase as item data for filtering and bulk deletion.
            item.setData(Qt.ItemDataRole.UserRole, phrase)
            
            # Create a row widget with text and a quick remove button
            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent; margin: 0px; padding: 0px;")
            # QListWidget cannot reliably infer a row-widget height when its
            # native text is intentionally empty.  Keep every row tall enough
            # for the label, button and vertical margins.
            row_widget.setMinimumHeight(34)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(6, 0, 6, 0)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            lbl = QLabel(phrase)
            lbl.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {text_color}; background: transparent;")
            lbl.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            lbl.setMinimumHeight(34)
            row_layout.addWidget(lbl)
            row_layout.addStretch()

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(22, 22)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setToolTip(f"Видалити '{phrase}' з чорного списку")
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    border: none;
                    font-size: 13px;
                    font-weight: bold;
                    border-radius: 11px;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                    color: #dc2626;
                }
            """)
            del_btn.clicked.connect(lambda checked=False, p=phrase: self._remove_phrase(p))
            row_layout.addWidget(del_btn)

            item.setSizeHint(QSize(0, 34))
            self.list_widget.setItemWidget(item, row_widget)

        self._filter_list_items(self.filter_input.text())

    def _filter_list_items(self, text: str) -> None:
        """Filter visible items in the list widget based on search text."""
        query = text.strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            phrase = item.data(Qt.ItemDataRole.UserRole) or ""
            if not query or query in phrase.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def _on_add_clicked(self) -> None:
        phrase = self.input_field.text().strip()
        if not phrase:
            return

        if self.settings.add_to_blacklist(phrase):
            self.input_field.clear()
            self.reload_list()
            self.blacklist_changed.emit()
        else:
            QMessageBox.information(
                self,
                "Слово вже є",
                f"Фраза '{phrase}' вже присутня в чорному списку."
            )

    def add_phrase_external(self, phrase: str) -> bool:
        """Add phrase from outside (e.g. right-click menu in table)."""
        clean = phrase.strip()
        if not clean:
            return False
        if self.settings.add_to_blacklist(clean):
            self.reload_list()
            self.blacklist_changed.emit()
            return True
        return False

    def _remove_phrase(self, phrase: str) -> None:
        if self.settings.remove_from_blacklist(phrase):
            self.reload_list()
            self.blacklist_changed.emit()

    def _on_delete_selected(self) -> None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            phrase = item.data(Qt.ItemDataRole.UserRole)
            if phrase:
                self.settings.remove_from_blacklist(phrase)
        self.reload_list()
        self.blacklist_changed.emit()

    def _on_clear_clicked(self) -> None:
        if not self.settings.blacklist:
            return
        reply = QMessageBox.question(
            self,
            "Підтвердження очищення",
            "Ви дійсно бажаєте повністю очистити чорний список?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear_blacklist()
            self.reload_list()
            self.blacklist_changed.emit()

    def _on_reset_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Скидання до стандартного",
            "Відновити стандартний список небажаних слів?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_blacklist_to_default()
            self.reload_list()
            self.blacklist_changed.emit()
