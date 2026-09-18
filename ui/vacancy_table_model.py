"""
QAbstractTableModel for rendering job vacancies in a modern QTableView.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, List, Optional
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QBrush, QColor, QFont

from models import Vacancy


class VacancyTableModel(QAbstractTableModel):
    """Table model for vacancies list."""

    COLUMNS = [
        "Посада",
        "Компанія",
        "Зарплата",
        "Місто / Формат",
        "Дата публікації"
    ]

    def __init__(self, vacancies: Optional[List[Vacancy]] = None, parent=None):
        super().__init__(parent)
        self._vacancies: List[Vacancy] = vacancies or []
        self.is_dark: bool = False

    def set_dark_theme(self, is_dark: bool) -> None:
        self.is_dark = is_dark
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._vacancies)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section]
        return QVariant()

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._vacancies)):
            return QVariant()

        vacancy = self._vacancies[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                hot_prefix = "🔥 " if vacancy.hot else ""
                return f"{hot_prefix}{vacancy.name}"
            elif col == 1:
                return vacancy.company_name
            elif col == 2:
                return vacancy.formatted_salary
            elif col == 3:
                city = vacancy.city_name or "Україна"
                remote_tag = " [Remote]" if vacancy.is_remote else ""
                return f"{city}{remote_tag}"
            elif col == 4:
                return vacancy.formatted_date

        elif role == Qt.ItemDataRole.FontRole:
            if col == 0:
                font = QFont()
                font.setBold(True)
                return font
            elif col == 2 and (vacancy.salary_from > 0 or vacancy.salary_to > 0 or vacancy.salary > 0):
                font = QFont()
                font.setBold(True)
                return font

        elif role == Qt.ItemDataRole.ForegroundRole:
            if col == 2:
                if vacancy.salary_from > 0 or vacancy.salary_to > 0 or vacancy.salary > 0:
                    return QBrush(QColor("#34d399") if self.is_dark else QColor("#059669"))  # Emerald Green
                else:
                    return QBrush(QColor("#64748b") if self.is_dark else QColor("#94a3b8"))  # Slate Gray
            elif col == 1:
                return QBrush(QColor("#cbd5e1") if self.is_dark else QColor("#475569"))
            elif col == 3:
                return QBrush(QColor("#60a5fa") if self.is_dark else QColor("#2563eb"))
            elif col == 4:
                return QBrush(QColor("#94a3b8") if self.is_dark else QColor("#64748b"))

        elif role == Qt.ItemDataRole.ToolTipRole:
            hot_info = "Гаряча вакансія! " if vacancy.hot else ""
            return (
                f"<b>{hot_info}{vacancy.name}</b><br/>"
                f"<b>Компанія:</b> {vacancy.company_name}<br/>"
                f"<b>Зарплата:</b> {vacancy.formatted_salary}<br/>"
                f"<b>Місто:</b> {vacancy.city_name or 'Віддалено'}<br/>"
                f"<b>Дата:</b> {vacancy.formatted_date}<br/>"
                f"<hr/><i>Двічі клікніть, щоб відкрити на robota.ua</i>"
            )

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (3, 4):
                return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return QVariant()

    def set_vacancies(self, vacancies: List[Vacancy]) -> None:
        """Update the dataset."""
        self.beginResetModel()
        self._vacancies = list(vacancies)
        self.endResetModel()

    def get_vacancy(self, row: int) -> Optional[Vacancy]:
        """Get Vacancy object at given row index."""
        if 0 <= row < len(self._vacancies):
            return self._vacancies[row]
        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Sort model by column."""
        self.beginResetModel()
        reverse = order == Qt.SortOrder.DescendingOrder

        if column == 0:
            self._vacancies.sort(key=lambda v: v.name.lower(), reverse=reverse)
        elif column == 1:
            self._vacancies.sort(key=lambda v: v.company_name.lower(), reverse=reverse)
        elif column == 2:
            self._vacancies.sort(
                key=lambda v: (v.salary_from or v.salary or v.salary_to or 0),
                reverse=reverse
            )
        elif column == 3:
            self._vacancies.sort(key=lambda v: v.city_name.lower(), reverse=reverse)
        elif column == 4:
            self._vacancies.sort(
                key=lambda v: (v.date.replace(tzinfo=None) if v.date else datetime.min),
                reverse=reverse
            )

        self.endResetModel()
