"""
Filtering engine for job vacancies (Remote, Blacklist, Instant Search).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import re

from models import Vacancy

MANUAL_BLOCK_REASON = "Приховано вручну"


@dataclass
class FilterResult:
    """Encapsulates the result of filtering a list of vacancies."""
    displayed_vacancies: List[Vacancy]
    total_loaded: int
    total_displayed: int
    blacklisted_count: int
    blocked_stats: Dict[str, int] = field(default_factory=dict)
    blocked_vacancies: List[Tuple[Vacancy, str]] = field(default_factory=list)


class VacancyFilterEngine:
    """Applies remote, blacklist, and live text search filtering to vacancies."""

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        """
        Check if text contains the phrase.
        Handles case-insensitivity and punctuation normalization.
        """
        if not phrase or not text:
            return False
        
        # Simple substring search in lowercase
        norm_text = text.lower()
        norm_phrase = phrase.lower().strip()
        
        return norm_phrase in norm_text

    @classmethod
    def is_blacklisted(cls, vacancy: Vacancy, blacklist: List[str]) -> Optional[str]:
        """
        Checks if the vacancy contains any blacklisted word or phrase.
        Returns the matching phrase if found, or None.
        """
        if not blacklist:
            return None

        # Build searchable string combining title, company, and description
        searchable_parts = [
            vacancy.name,
            vacancy.company_name,
            vacancy.short_description,
            vacancy.full_description,
        ]
        combined_text = " ".join(p for p in searchable_parts if p).lower()

        for phrase in blacklist:
            clean_phrase = phrase.strip().lower()
            if not clean_phrase:
                continue
            
            # Match word boundary or substring
            if clean_phrase in combined_text:
                return phrase

        return None

    @classmethod
    def matches_search_query(cls, vacancy: Vacancy, query: str) -> bool:
        """
        Check if vacancy matches instant search query.
        Splits multiple words (all words must match).
        """
        if not query or not query.strip():
            return True

        words = [w.lower() for w in query.strip().split() if w]
        if not words:
            return True

        searchable_text = f"{vacancy.name} {vacancy.company_name} {vacancy.city_name} {vacancy.formatted_salary} {vacancy.clean_description}".lower()

        return all(w in searchable_text for w in words)

    @classmethod
    def apply_filters(
        cls,
        vacancies: List[Vacancy],
        blacklist: List[str],
        manually_blocked_ids: Optional[Set[int]] = None,
        instant_search_query: str = "",
        remote_only: bool = True
    ) -> FilterResult:
        """
        Filter vacancies according to remote status, blacklist, and instant search query.
        """
        displayed: List[Vacancy] = []
        blocked_vacancies: List[Tuple[Vacancy, str]] = []
        blocked_stats: Dict[str, int] = {}
        total_loaded = len(vacancies)
        manually_blocked_ids = manually_blocked_ids or set()

        for v in vacancies:
            # 1. Check remote filter
            if remote_only and not v.is_remote:
                continue

            # 2. Check manually hidden vacancies before word matching.
            if v.id in manually_blocked_ids:
                blocked_vacancies.append((v, MANUAL_BLOCK_REASON))
                blocked_stats[MANUAL_BLOCK_REASON] = blocked_stats.get(MANUAL_BLOCK_REASON, 0) + 1
                continue

            # 3. Check blacklist filter
            matched_word = cls.is_blacklisted(v, blacklist)
            if matched_word:
                blocked_vacancies.append((v, matched_word))
                blocked_stats[matched_word] = blocked_stats.get(matched_word, 0) + 1
                continue

            # 4. Check instant search query filter
            if instant_search_query and not cls.matches_search_query(v, instant_search_query):
                continue

            displayed.append(v)

        return FilterResult(
            displayed_vacancies=displayed,
            total_loaded=total_loaded,
            total_displayed=len(displayed),
            blacklisted_count=len(blocked_vacancies),
            blocked_stats=blocked_stats,
            blocked_vacancies=blocked_vacancies
        )
