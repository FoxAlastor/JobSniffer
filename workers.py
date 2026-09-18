"""
Background QThread workers for non-blocking asynchronous operations.
"""

from __future__ import annotations
import logging
from typing import List, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from api import RobotaApiClient
from models import Vacancy

logger = logging.getLogger(__name__)


class FetchVacanciesWorker(QThread):
    """Worker thread for loading vacancy lists from robota.ua with auto-replenish."""
    
    # Signals: (valid_found, target_count, raw_scanned)
    progress = pyqtSignal(int, int, int)
    # Signals: (List[Vacancy], server_total, next_page)
    finished = pyqtSignal(list, int, int)
    error = pyqtSignal(str)

    def __init__(
        self,
        keywords: str = "",
        remote_only: bool = True,
        target_valid_count: int = 100,
        blacklist: Optional[List[str]] = None,
        start_page: int = 0,
        existing_vacancies: Optional[List[Vacancy]] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self.keywords = keywords
        self.remote_only = remote_only
        self.target_valid_count = target_valid_count
        self.blacklist = list(blacklist or [])
        self.start_page = start_page
        self.existing_vacancies = list(existing_vacancies or [])
        self.client = RobotaApiClient()
        self._is_cancelled = False

    def cancel(self) -> None:
        """Request cancellation."""
        self._is_cancelled = True
        try:
            self.client.session.close()
        except Exception:
            pass

    def run(self) -> None:
        try:
            def on_progress(valid_cnt: int, target_cnt: int, raw_cnt: int):
                if not self._is_cancelled:
                    self.progress.emit(valid_cnt, target_cnt, raw_cnt)

            new_vacancies, server_total, next_page = self.client.fetch_multiple_pages(
                keywords=self.keywords,
                remote_only=self.remote_only,
                target_valid_count=self.target_valid_count,
                blacklist=self.blacklist,
                start_page=self.start_page,
                progress_callback=on_progress
            )

            # Combine with existing if any (avoid duplicates by ID)
            combined = list(self.existing_vacancies)
            existing_ids = {v.id for v in combined}
            for v in new_vacancies:
                if v.id not in existing_ids:
                    combined.append(v)
                    existing_ids.add(v.id)

            if not self._is_cancelled:
                self.finished.emit(combined, server_total, next_page)

        except Exception as e:
            if not self._is_cancelled:
                logger.exception("Error in FetchVacanciesWorker")
                self.error.emit(str(e))


class FetchVacancyDetailWorker(QThread):
    """Worker thread for fetching full details for a single vacancy."""
    
    detail_ready = pyqtSignal(object)  # (Optional[Vacancy])

    def __init__(self, vacancy_id: int, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.vacancy_id = vacancy_id
        self.client = RobotaApiClient()

    def run(self) -> None:
        try:
            detail = self.client.get_vacancy_detail(self.vacancy_id)
            self.detail_ready.emit(detail)
        except Exception as e:
            logger.warning(f"Error fetching details for {self.vacancy_id}: {e}")
            self.detail_ready.emit(None)
