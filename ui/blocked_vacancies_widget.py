"""
Widget displaying vacancies hidden by the blacklist with reasons.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QSizePolicy,
    QWidget,
)

from models import Vacancy
from filter_engine import MANUAL_BLOCK_REASON


class BlockedVacanciesWidget(QWidget):
    """Shows vacancies that were filtered out by the blacklist."""

    unblock_word_requested = pyqtSignal(str)
    unblock_vacancy_requested = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.blocked_items: List[Tuple[Vacancy, str]] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header Info
        header_layout = QHBoxLayout()
        self.title_label = QLabel("🛡️ Приховані вакансії")
        self.title_label.setStyleSheet("font-weight: 700; font-size: 15px;")
        
        self.count_badge = QLabel("0 приховано")
        self.count_badge.setStyleSheet(
            "background-color: #fee2e2; color: #b91c1c; border-radius: 10px; "
            "padding: 2px 8px; font-weight: 600; font-size: 11px;"
        )
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.count_badge)
        layout.addLayout(header_layout)

        desc = QLabel(
            "Тут відображаються вакансії з поточного завантаження, "
            "які не потрапили в основний список через чорний список або ручне приховування."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(desc)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Причина (Заборонене слово)",
            "Посада",
            "Компанія",
            "Дія"
        ])
        # Let the user adjust every list column instead of locking widths to
        # the current content or viewport.
        for column in range(4):
            self.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.Interactive
            )
        self.table.horizontalHeader().resizeSection(0, 220)
        self.table.horizontalHeader().resizeSection(1, 320)
        self.table.horizontalHeader().resizeSection(2, 180)
        self.table.horizontalHeader().resizeSection(3, 240)
        self.table.setAlternatingRowColors(True)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table)

    def set_blocked(self, blocked_items: List[Tuple[Vacancy, str]]) -> None:
        """Update blocked list."""
        self.blocked_items = blocked_items
        self.count_badge.setText(f"{len(blocked_items)} приховано")
        self.table.setRowCount(len(blocked_items))

        for row, (v, reason) in enumerate(blocked_items):
            # Leave enough room for the button's font metrics and border so
            # the cell never clips the lower half of the label.
            self.table.setRowHeight(row, 36)
            # Reason item with red tag style
            reason_item = QTableWidgetItem(f"🚫 {reason}")
            reason_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 0, reason_item)

            name_item = QTableWidgetItem(v.name)
            name_item.setToolTip("Подвійний клік відкриє вакансію у браузері")
            self.table.setItem(row, 1, name_item)

            comp_item = QTableWidgetItem(v.company_name)
            self.table.setItem(row, 2, comp_item)

            # Action buttons
            actions = QWidget()
            # QTableWidget embeds this widget as a cell editor-like wrapper;
            # make its palette explicit so it cannot paint a light rectangle
            # over the dark table background.
            actions.setStyleSheet(
                "QWidget { background-color: transparent; border: none; }"
            )
            actions.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            actions_layout = QHBoxLayout(actions)
            # Keep the button inside the cell; negative insets can push the
            # embedded widget completely outside the visible row in Qt.
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            # The wrapper fills the row; pin the compact button to the upper
            # half of the cell so the label cannot be covered by the next row.
            actions_layout.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
            )

            open_btn = QPushButton("Відкрити")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setFixedSize(88, 26)
            open_btn.setStyleSheet(
                "padding: 0px 10px; margin: 0px; line-height: 1.2; "
                "font-size: 12px; font-weight: 600;"
            )
            open_btn.clicked.connect(lambda checked=False, url=v.url: QDesktopServices.openUrl(QUrl(url)))
            actions_layout.addWidget(open_btn)

            if reason == MANUAL_BLOCK_REASON:
                restore_btn = QPushButton("Повернути")
                restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                restore_btn.setFixedSize(98, 26)
                restore_btn.setStyleSheet(
                    "padding: 0px 10px; margin: 0px; line-height: 1.2; "
                    "font-size: 12px; font-weight: 600;"
                )
                restore_btn.clicked.connect(
                    lambda checked=False, vacancy_id=v.id: self.unblock_vacancy_requested.emit(vacancy_id)
                )
                actions_layout.addWidget(restore_btn)

            self.table.setCellWidget(row, 3, actions)

    def _on_cell_double_clicked(self, row: int, col: int) -> None:
        if 0 <= row < len(self.blocked_items):
            v, _ = self.blocked_items[row]
            QDesktopServices.openUrl(QUrl(v.url))
