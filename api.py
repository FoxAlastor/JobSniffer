"""
Robota.ua API client implementation.
"""

from __future__ import annotations
import logging
from typing import Callable, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models import Vacancy

logger = logging.getLogger(__name__)


class RobotaApiClient:
    """Client for interacting with Robota.ua public API endpoints."""

    BASE_URL = "https://api.rabota.ua"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://robota.ua",
        "Referer": "https://robota.ua/",
    }

    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        
        # Configure automatic retries for transient network glitches
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def search_vacancies(
        self,
        keywords: str = "",
        remote_only: bool = True,
        page: int = 0,
        count: int = 40,
        city_id: Optional[int] = None
    ) -> Tuple[List[Vacancy], int]:
        """
        Search for vacancies on Robota.ua.
        
        :param keywords: Search query term (e.g. "Python", "QA", "Менеджер")
        :param remote_only: If True, filters for remote work (scheduleId=3)
        :param page: 0-indexed page number
        :param count: Number of items per page (max 50)
        :param city_id: Optional city ID filter
        :return: (List of Vacancy models, total matching items count)
        """
        url = f"{self.BASE_URL}/vacancy/search"
        params = {
            "page": max(0, page),
            "count": min(50, max(1, count)),
        }
        
        if keywords and keywords.strip():
            params["keyWords"] = keywords.strip()
            
        if remote_only:
            params["scheduleId"] = 3  # 3 = Remote in Robota.ua dictionary
            
        if city_id is not None:
            params["cityId"] = city_id

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            raw_docs = data.get("documents", [])
            total = data.get("total", 0)
            
            vacancies = [
                Vacancy.from_api_dict(doc, is_remote=True if remote_only else None)
                for doc in raw_docs
            ]
            return vacancies, total

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching vacancies: {e}")
            raise RuntimeError(f"Помилка при з'єднанні з robota.ua: {e}") from e

    def fetch_multiple_pages(
        self,
        keywords: str = "",
        remote_only: bool = True,
        target_valid_count: int = 80,
        blacklist: Optional[List[str]] = None,
        start_page: int = 0,
        max_raw_limit: int = 2500,
        progress_callback: Optional[Callable[[int, int, int], None]] = None
    ) -> Tuple[List[Vacancy], int, int]:
        """
        Fetch multiple pages of vacancies until target_valid_count of non-blacklisted items is reached.
        
        :param keywords: Search query string
        :param remote_only: Whether to filter for remote vacancies
        :param target_valid_count: Target number of valid/displayed items to collect (e.g., 50, 100, 200)
        :param blacklist: Active blacklist to filter during pagination
        :param start_page: Starting page number (0-indexed)
        :param max_raw_limit: Maximum total raw vacancies to scan as safety guard
        :param progress_callback: Callback(valid_count, target_valid_count, raw_scanned_count)
        :return: (List of all retrieved Vacancies, server reported total, next page index)
        """
        all_vacancies: List[Vacancy] = []
        valid_count = 0
        page = max(0, start_page)
        per_page = 40
        server_total = 0
        seen_ids = set()
        active_blacklist = [w.strip().lower() for w in (blacklist or []) if w.strip()]

        while valid_count < target_valid_count and len(all_vacancies) < max_raw_limit:
            vacancies, total = self.search_vacancies(
                keywords=keywords,
                remote_only=remote_only,
                page=page,
                count=per_page
            )
            
            server_total = total
            if not vacancies:
                break
                
            new_items_in_page = 0
            for v in vacancies:
                if v.id not in seen_ids:
                    seen_ids.add(v.id)
                    all_vacancies.append(v)
                    new_items_in_page += 1
                    
                    # Check if vacancy matches remote and blacklist criteria
                    is_valid = True
                    if remote_only and not v.is_remote:
                        is_valid = False
                    
                    if is_valid and active_blacklist:
                        combined = f"{v.name} {v.company_name} {v.short_description} {v.full_description}".lower()
                        if any(phrase in combined for phrase in active_blacklist):
                            is_valid = False
                            
                    if is_valid:
                        valid_count += 1
                        if valid_count >= target_valid_count:
                            break
            
            if progress_callback:
                progress_callback(valid_count, target_valid_count, len(all_vacancies))

            if valid_count >= target_valid_count:
                page += 1
                break
                
            # If server returned fewer items than requested or exhausted total or no new items
            if len(vacancies) < per_page or len(all_vacancies) >= server_total or new_items_in_page == 0:
                page += 1
                break
                
            page += 1

        return all_vacancies, server_total, page

    def get_vacancy_detail(self, vacancy_id: int) -> Optional[Vacancy]:
        """
        Fetch full details for a single vacancy.
        
        :param vacancy_id: Robota.ua vacancy ID
        :return: Updated Vacancy object or None
        """
        url = f"{self.BASE_URL}/vacancy"
        params = {"id": vacancy_id}
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return Vacancy.from_api_dict(data)
        except Exception as e:
            logger.warning(f"Failed to fetch detail for vacancy {vacancy_id}: {e}")
            return None
