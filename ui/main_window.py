"""
Main Application Window for Robota.ua Vacancy Manager.
"""

from __future__ import annotations
import logging
from typing import List, Optional
from PyQt6.QtCore import QModelIndex, QPoint, Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QAction, QDesktopServices, QGuiApplication, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from filter_engine import FilterResult, VacancyFilterEngine
from models import Vacancy
from storage import BlockedVacanciesStore, SettingsManager
from ui.blacklist_widget import BlacklistWidget
from ui.blocked_vacancies_widget import BlockedVacanciesWidget
from ui.styles import get_theme_stylesheet
from ui.vacancy_detail_widget import VacancyDetailWidget
from ui.vacancy_table_model import VacancyTableModel
from workers import FetchVacanciesWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window of the Robota.ua Vacancy Explorer desktop app."""

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings = settings_manager
        self.blocked_vacancies_store = BlockedVacanciesStore()
        self.all_loaded_vacancies: List[Vacancy] = []
        self.current_filter_result: Optional[FilterResult] = None
        self.fetch_worker: Optional[FetchVacanciesWorker] = None
        self.next_page: int = 0
        self.server_total_available: int = 0

        self.setWindowTitle("Robota.ua Remote Vacancies Explorer")
        self.resize(1250, 780)
        self.setMinimumSize(850, 500)

        self._init_ui()
        self._setup_shortcuts()
        self._connect_signals()

        # Apply saved theme
        self._apply_current_theme()

        # Load initial vacancies based on saved settings
        self.refresh_vacancies()

    def _init_ui(self) -> None:
        """Construct the UI widgets and layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 10, 12, 8)
        main_layout.setSpacing(10)

        # Top Control Bar (Search & Filters)
        top_bar = self._create_top_control_bar()
        main_layout.addWidget(top_bar)

        # Central Splitter (Left: Table, Right: Tabs)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)

        # Left Panel (Table & Quick Count Info)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Sub-header with live count info and quick replenish action
        info_header_layout = QHBoxLayout()
        self.table_info_label = QLabel("Завантаження списку вакансій...")
        self.table_info_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        info_header_layout.addWidget(self.table_info_label)
        info_header_layout.addStretch()

        self.replenish_btn = QPushButton("➕ Добрати до ліміту")
        self.replenish_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.replenish_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecfdf5;
                color: #065f46;
                border: 1px solid #a7f3d0;
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #d1fae5;
                color: #047857;
            }
        """)
        self.replenish_btn.setToolTip("Добрати додаткові вакансії з Robota.ua, щоб заповнити список рівно до обраного ліміту")
        self.replenish_btn.clicked.connect(self.replenish_to_limit)
        info_header_layout.addWidget(self.replenish_btn)

        left_layout.addLayout(info_header_layout)

        # Vacancies Table View
        self.table_model = VacancyTableModel([], parent=self)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        
        # Configure column resize modes
        header = self.table_view.horizontalHeader()
        # Keep every column user-resizable.  Stretching the title and
        # ResizeToContents on the other columns made the table fight the user
        # when the window width changed.
        for column in range(self.table_model.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(0, 320)  # Job title
        header.resizeSection(1, 180)  # Company
        header.resizeSection(2, 120)  # Salary
        header.resizeSection(3, 120)  # Format/Remote
        header.resizeSection(4, 110)  # Date

        # Enable custom context menu
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_table_context_menu)

        left_layout.addWidget(self.table_view)
        splitter.addWidget(left_panel)

        # Right Panel (Tabs: Details, Blacklist, Blocked)
        self.right_tabs = QTabWidget()
        self.right_tabs.setMinimumWidth(380)

        # Tab 1: Details
        self.detail_widget = VacancyDetailWidget()
        self.right_tabs.addTab(self.detail_widget, "📄 Деталі вакансії")

        # Tab 2: Blacklist Manager
        self.blacklist_widget = BlacklistWidget(self.settings)
        self.right_tabs.addTab(self.blacklist_widget, "🚫 Чорний список")

        # Tab 3: Blocked items viewer
        self.blocked_widget = BlockedVacanciesWidget()
        self.right_tabs.addTab(self.blocked_widget, "🛡️ Заблоковані (0)")

        splitter.addWidget(self.right_tabs)

        # Set initial splitter ratio (62% left, 38% right)
        splitter.setStretchFactor(0, 62)
        splitter.setStretchFactor(1, 38)
        main_layout.addWidget(splitter, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Готово")
        self.status_bar.addWidget(self.status_label, stretch=1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #64748b; font-size: 11px; margin-right: 8px;")
        self.status_bar.addPermanentWidget(self.stats_label)

    def _create_top_control_bar(self) -> QWidget:
        """Create the top controls row containing search inputs, refresh button, filters and theme toggle."""
        top_frame = QFrame()
        top_frame.setProperty("class", "cardFrame")
        top_layout = QVBoxLayout(top_frame)
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(8)

        # Row 1: Search Query + Remote + Count + Refresh + Load More + Theme Toggle
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        # Server Query Input
        query_icon = QLabel("🔍")
        query_icon.setStyleSheet("font-size: 14px;")
        row1.addWidget(query_icon)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Пошук на robota.ua (напр. Python, React, Дизайнер, Бухгалтер)...")
        self.query_input.setText(self.settings.last_search_query)
        self.query_input.returnPressed.connect(self.refresh_vacancies)
        row1.addWidget(self.query_input, stretch=3)

        # Remote only checkbox
        self.remote_checkbox = QCheckBox("Лише віддалені (Remote)")
        self.remote_checkbox.setChecked(self.settings.remote_only)
        self.remote_checkbox.setToolTip("Фільтрувати виключно вакансії з віддаленим форматом роботи")
        self.remote_checkbox.toggled.connect(self._on_remote_toggled)
        row1.addWidget(self.remote_checkbox)

        # Items count combobox
        count_label = QLabel("Ліміт:")
        count_label.setStyleSheet("font-weight: 500;")
        count_label.setToolTip("Бажана кількість дійсних вакансій у списку")
        row1.addWidget(count_label)

        self.count_combo = QComboBox()
        self.count_combo.blockSignals(True)
        self.count_combo.addItems(["50", "100", "200", "300", "500"])
        saved_count = str(self.settings.items_to_fetch)
        idx = self.count_combo.findText(saved_count)
        if idx >= 0:
            self.count_combo.setCurrentIndex(idx)
        else:
            self.count_combo.setCurrentText("100")
        self.count_combo.blockSignals(False)
        self.count_combo.currentTextChanged.connect(self._on_count_changed)
        row1.addWidget(self.count_combo)

        # Refresh / Search Button
        self.refresh_btn = QPushButton("🔄 Оновити")
        self.refresh_btn.setProperty("class", "primaryButton")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setToolTip("Завантажити свіжі вакансії з добором до повного списку (F5)")
        self.refresh_btn.clicked.connect(self.refresh_vacancies)
        row1.addWidget(self.refresh_btn)

        # Load More Button
        self.load_more_btn = QPushButton("➕ Добрати ще")
        self.load_more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_more_btn.setToolTip("Підвантажити наступну порцію вакансій (+50)")
        self.load_more_btn.clicked.connect(self.load_more_vacancies)
        row1.addWidget(self.load_more_btn)

        # Dark / Light Theme Toggle Button
        self.theme_btn = QPushButton("🌙 Темна тема" if self.settings.theme != "dark" else "☀️ Світла тема")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setToolTip("Перемкнути між світлою та темною темою оформлення")
        self.theme_btn.clicked.connect(self._toggle_theme)
        row1.addWidget(self.theme_btn)

        top_layout.addLayout(row1)

        # Row 2: Instant Local Search Filter
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        instant_label = QLabel("⚡ Миттєвий фільтр:")
        instant_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        row2.addWidget(instant_label)

        self.instant_filter_input = QLineEdit()
        self.instant_filter_input.setPlaceholderText("Фільтрувати поточний список за назвою, зарплатою, описом...")
        self.instant_filter_input.setClearButtonEnabled(True)
        self.instant_filter_input.textChanged.connect(self._on_instant_filter_changed)
        row2.addWidget(self.instant_filter_input, stretch=1)

        top_layout.addLayout(row2)

        return top_frame

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for fast operation."""
        QShortcut(QKeySequence("F5"), self, self.refresh_vacancies)
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh_vacancies)
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.instant_filter_input.setFocus())
        QShortcut(QKeySequence("Ctrl+K"), self, lambda: self.query_input.setFocus())

    def _connect_signals(self) -> None:
        """Connect UI signals to handler slots."""
        # Table selection changes
        self.table_view.selectionModel().selectionChanged.connect(self._on_table_selection_changed)
        
        # Double click opens in browser
        self.table_view.doubleClicked.connect(self._on_table_double_clicked)

        # Blacklist changes trigger re-filtering without re-downloading
        self.blacklist_widget.blacklist_changed.connect(self._on_blacklist_changed)
        self.blocked_widget.unblock_vacancy_requested.connect(self._unblock_specific_vacancy)

        # Quick blacklist from detail pane
        self.detail_widget.request_blacklist_word.connect(self._add_to_blacklist_from_detail)
        self.detail_widget.request_block_vacancy.connect(self._block_specific_vacancy)

    # --- Theme Management ---

    def _apply_current_theme(self) -> None:
        """Apply the currently chosen theme (light or dark)."""
        is_dark = self.settings.theme == "dark"
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_theme_stylesheet(self.settings.theme))

        self.detail_widget.set_dark_theme(is_dark)
        self.table_model.set_dark_theme(is_dark)
        self.blacklist_widget.set_dark_theme(is_dark)
        self.theme_btn.setText("☀️ Світла тема" if is_dark else "🌙 Темна тема")

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        new_theme = "light" if self.settings.theme == "dark" else "dark"
        self.settings.theme = new_theme
        self._apply_current_theme()

    # --- Actions and Slots ---

    @pyqtSlot()
    def refresh_vacancies(self) -> None:
        """Initiate network request to fetch vacancies from robota.ua with auto-replenish."""
        if self.fetch_worker and self.fetch_worker.isRunning():
            self.fetch_worker.cancel()

        query = self.query_input.text().strip()
        self.settings.last_search_query = query
        remote_only = self.remote_checkbox.isChecked()
        target_count = int(self.count_combo.currentText())
        blacklist = self.settings.blacklist

        self.refresh_btn.setEnabled(False)
        self.load_more_btn.setEnabled(False)
        self.replenish_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Добір...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Завантаження вакансій з robota.ua (ціль: {target_count} дійсних, запит: '{query or 'Всі свіжі'}')...")

        self.next_page = 0
        self.fetch_worker = FetchVacanciesWorker(
            keywords=query,
            remote_only=remote_only,
            target_valid_count=target_count,
            blacklist=blacklist,
            start_page=0,
            existing_vacancies=[],
            parent=self
        )
        self.fetch_worker.progress.connect(self._on_fetch_progress)
        self.fetch_worker.finished.connect(self._on_fetch_finished)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.start()

    @pyqtSlot()
    def replenish_to_limit(self) -> None:
        """Replenish ONLY the missing number of vacancies to reach the target limit."""
        if self.fetch_worker and self.fetch_worker.isRunning():
            return

        target_limit = int(self.count_combo.currentText())
        current_valid = len(self.current_filter_result.displayed_vacancies) if self.current_filter_result else 0
        needed = target_limit - current_valid
        
        if needed <= 0:
            needed = 50  # If already full, fetch a small batch

        query = self.query_input.text().strip()
        remote_only = self.remote_checkbox.isChecked()
        blacklist = self.settings.blacklist

        self.refresh_btn.setEnabled(False)
        self.load_more_btn.setEnabled(False)
        self.replenish_btn.setEnabled(False)
        self.replenish_btn.setText("⏳ Добираємо...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Добір {needed} відсутніх вакансій до ліміту {target_limit} (зі сторінки {self.next_page})...")

        self.fetch_worker = FetchVacanciesWorker(
            keywords=query,
            remote_only=remote_only,
            target_valid_count=needed,
            blacklist=blacklist,
            start_page=self.next_page,
            existing_vacancies=self.all_loaded_vacancies,
            parent=self
        )
        self.fetch_worker.progress.connect(self._on_fetch_progress)
        self.fetch_worker.finished.connect(self._on_fetch_finished)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.start()

    @pyqtSlot()
    def load_more_vacancies(self) -> None:
        """Fetch additional 50 vacancies to expand list."""
        if self.fetch_worker and self.fetch_worker.isRunning():
            return

        query = self.query_input.text().strip()
        remote_only = self.remote_checkbox.isChecked()
        batch_to_add = 50
        blacklist = self.settings.blacklist

        self.refresh_btn.setEnabled(False)
        self.load_more_btn.setEnabled(False)
        self.replenish_btn.setEnabled(False)
        self.load_more_btn.setText("⏳ Добираємо...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Добір наступних {batch_to_add} вакансій зі сторінки {self.next_page}...")

        self.fetch_worker = FetchVacanciesWorker(
            keywords=query,
            remote_only=remote_only,
            target_valid_count=batch_to_add,
            blacklist=blacklist,
            start_page=self.next_page,
            existing_vacancies=self.all_loaded_vacancies,
            parent=self
        )
        self.fetch_worker.progress.connect(self._on_fetch_progress)
        self.fetch_worker.finished.connect(self._on_fetch_finished)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.start()

    def _on_fetch_progress(self, valid_cnt: int, target_cnt: int, raw_cnt: int) -> None:
        pct = int((valid_cnt / max(1, target_cnt)) * 100)
        self.progress_bar.setValue(min(100, pct))
        self.status_label.setText(f"Дібрано {valid_cnt} з {target_cnt} дійсних вакансій (проскановано: {raw_cnt} з урахуванням ЧС)...")

    def _on_fetch_finished(self, vacancies: List[Vacancy], server_total: int, next_page: int) -> None:
        self.refresh_btn.setEnabled(True)
        self.load_more_btn.setEnabled(True)
        self.replenish_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Оновити")
        self.load_more_btn.setText("➕ Добрати ще")
        self.progress_bar.setVisible(False)
        
        self.all_loaded_vacancies = vacancies
        self.server_total_available = server_total
        self.next_page = next_page
        
        self._reapply_filters()
        
        shown = len(self.current_filter_result.displayed_vacancies) if self.current_filter_result else len(vacancies)
        blocked = self.current_filter_result.blacklisted_count if self.current_filter_result else 0
        self.status_label.setText(
            f"Готово. У списку {shown} дійсних вакансій (проскановано всього {len(vacancies)}, "
            f"приховано чорним списком: {blocked}, доступно на сайті: {server_total})"
        )

    def _on_fetch_error(self, error_msg: str) -> None:
        self.refresh_btn.setEnabled(True)
        self.load_more_btn.setEnabled(True)
        self.replenish_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Оновити")
        self.load_more_btn.setText("➕ Добрати ще")
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Помилка завантаження")
        
        QMessageBox.warning(
            self,
            "Помилка з'єднання",
            f"Не вдалося завантажити вакансії з robota.ua:\n\n{error_msg}\n\n"
            "Перевірте підключення до Інтернету або спробуйте пізніше."
        )

    def _reapply_filters(self) -> None:
        """Apply remote, blacklist, and instant text filters to in-memory vacancies."""
        instant_text = self.instant_filter_input.text()
        remote_only = self.remote_checkbox.isChecked()
        blacklist = self.settings.blacklist

        self.current_filter_result = VacancyFilterEngine.apply_filters(
            vacancies=self.all_loaded_vacancies,
            blacklist=blacklist,
            manually_blocked_ids=self.blocked_vacancies_store.ids,
            instant_search_query=instant_text,
            remote_only=remote_only
        )

        # Update table model
        self.table_model.set_vacancies(self.current_filter_result.displayed_vacancies)
        
        # Update blocked tab
        self.blocked_widget.set_blocked(self.current_filter_result.blocked_vacancies)
        self.right_tabs.setTabText(2, f"🛡️ Заблоковані ({self.current_filter_result.blacklisted_count})")

        # Update UI count labels
        shown_count = self.current_filter_result.total_displayed
        total_count = self.current_filter_result.total_loaded
        blocked_count = self.current_filter_result.blacklisted_count
        target_limit = int(self.count_combo.currentText())

        if shown_count < target_limit:
            missing = target_limit - shown_count
            self.replenish_btn.setText(f"➕ Добрати до {target_limit} (ще {missing})")
            self.replenish_btn.setVisible(True)
        else:
            self.replenish_btn.setText("➕ Добрати ще (+50)")
            self.replenish_btn.setVisible(True)

        self.table_info_label.setText(
            f"Показано: <b>{shown_count}</b> дійсних вакансій "
            f"(всього проскановано: {total_count}, приховано чорним списком: <b><font color='#dc2626'>{blocked_count}</font></b>)"
        )
        self.stats_label.setText(
            f"Ціль: {target_limit} | Показано: {shown_count} | Проскановано: {total_count} | Приховано: {blocked_count}"
        )

        # Select first row if available and nothing selected
        if shown_count > 0:
            current_idx = self.table_view.currentIndex()
            if not current_idx.isValid() or current_idx.row() >= shown_count:
                first_idx = self.table_model.index(0, 0)
                self.table_view.selectRow(0)
                self.detail_widget.set_vacancy(self.table_model.get_vacancy(0))
        else:
            self.detail_widget.set_vacancy(None)

    def _on_blacklist_changed(self) -> None:
        """Handler for when blacklist items are added or removed."""
        self._reapply_filters()
        target_limit = int(self.count_combo.currentText())
        shown_count = self.current_filter_result.total_displayed if self.current_filter_result else 0
        if shown_count < target_limit:
            self.status_label.setText(
                f"Чорний список оновлено. Показано {shown_count} з {target_limit}. "
                f"Натисніть 'Добрати до ліміту', щоб дозавантажити свіжі вакансії."
            )

    def _on_instant_filter_changed(self, text: str) -> None:
        self._reapply_filters()

    def _on_remote_toggled(self, checked: bool) -> None:
        self.settings.remote_only = checked
        self._reapply_filters()

    def _on_count_changed(self, count_str: str) -> None:
        try:
            val = int(count_str)
            self.settings.items_to_fetch = val
            self._reapply_filters()
        except ValueError:
            pass

    def _on_table_selection_changed(self) -> None:
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            v = self.table_model.get_vacancy(row)
            self.detail_widget.set_vacancy(v)
        else:
            self.detail_widget.set_vacancy(None)

    def _on_table_double_clicked(self, index: QModelIndex) -> None:
        if index.isValid():
            v = self.table_model.get_vacancy(index.row())
            if v:
                QDesktopServices.openUrl(QUrl(v.url))

    def _add_to_blacklist_from_detail(self, word: str) -> None:
        if self.blacklist_widget.add_phrase_external(word):
            self.status_label.setText(f"Додано '{word}' до чорного списку")
            self._on_blacklist_changed()

    def _block_specific_vacancy(self, vacancy: Vacancy) -> None:
        """Hide one vacancy by its identifier without changing the word blacklist."""
        if self.blocked_vacancies_store.add(vacancy):
            self._reapply_filters()
            self.status_label.setText(f"Вакансію '{vacancy.name}' приховано")
        else:
            self.status_label.setText("Ця вакансія вже прихована або не має ідентифікатора")

    def _unblock_specific_vacancy(self, vacancy_id: int) -> None:
        """Restore a vacancy that was hidden by its individual identifier."""
        if self.blocked_vacancies_store.remove(vacancy_id):
            self._reapply_filters()
            self.status_label.setText("Вакансію повернуто до списку")

    def _show_table_context_menu(self, pos: QPoint) -> None:
        """Context menu for vacancy table rows."""
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        vacancy = self.table_model.get_vacancy(row)
        if not vacancy:
            return

        menu = QMenu(self)

        open_action = QAction("🌐 Відкрити на robota.ua", self)
        open_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(vacancy.url)))
        menu.addAction(open_action)

        copy_link_action = QAction("📋 Скопіювати посилання", self)
        copy_link_action.triggered.connect(lambda: self._copy_to_clipboard(vacancy.url, "Посилання скопійовано"))
        menu.addAction(copy_link_action)

        copy_title_action = QAction("📋 Скопіювати назву", self)
        copy_title_action.triggered.connect(lambda: self._copy_to_clipboard(vacancy.name, "Назву скопійовано"))
        menu.addAction(copy_title_action)

        menu.addSeparator()

        block_vacancy_action = QAction("🚫 Приховати лише цю вакансію", self)
        block_vacancy_action.triggered.connect(lambda: self._block_specific_vacancy(vacancy))
        menu.addAction(block_vacancy_action)

        block_title_action = QAction(f"🚫 Заблокувати назву: '{vacancy.name}'", self)
        block_title_action.triggered.connect(lambda: self._add_to_blacklist_from_detail(vacancy.name))
        menu.addAction(block_title_action)

        if vacancy.company_name and vacancy.company_name != "Невідома компанія":
            block_company_action = QAction(f"🚫 Заблокувати компанію: '{vacancy.company_name}'", self)
            block_company_action.triggered.connect(lambda: self._add_to_blacklist_from_detail(vacancy.company_name))
            menu.addAction(block_company_action)

        menu.exec(self.table_view.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str, msg: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            self.status_label.setText(f"✓ {msg}")

    def closeEvent(self, event) -> None:
        """Handle window close event and save settings."""
        self.settings.save()
        if self.fetch_worker and self.fetch_worker.isRunning():
            self.fetch_worker.cancel()
            self.fetch_worker.wait(1000)
        if hasattr(self, "detail_widget") and self.detail_widget._detail_worker and self.detail_widget._detail_worker.isRunning():
            self.detail_widget._detail_worker.wait(1000)
        super().closeEvent(event)
