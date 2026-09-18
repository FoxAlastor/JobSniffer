"""
Settings and state persistence manager for the Robota.ua application.
"""

from __future__ import annotations
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_BLACKLIST = [
    "будівельні послуги",
    "касир",
    "водій",
    "вантажник",
    "охоронець",
    "прибиральник",
    "оператор call-центру",
    "оператор колл-центру",
    "кухар",
    "офіціант",
    "бариста",
    "швачка",
    "фасувальник",
]

DEFAULT_SETTINGS: Dict[str, Any] = {
    "blacklist": DEFAULT_BLACKLIST,
    "last_search_query": "",
    "remote_only": True,
    "items_to_fetch": 100,
    "auto_refresh_on_startup": True,
    "theme": "light",
}


class SettingsManager:
    """Manages reading and writing application settings to settings.json."""

    def __init__(self, file_path: Optional[str | Path] = None):
        if file_path is None:
            # In a PyInstaller build, keep editable state beside the exe
            # rather than inside the temporary unpacked _MEIPASS folder.
            if getattr(sys, "frozen", False):
                base_dir = Path(sys.executable).resolve().parent
            else:
                base_dir = Path(__file__).resolve().parent
            self.file_path = base_dir / "settings.json"
        else:
            self.file_path = Path(file_path)

        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load settings from the JSON file or populate with defaults."""
        loaded_from_disk = False

        if self.file_path.exists():
            try:
                # Use utf-8-sig to handle possible Windows UTF-8 BOM
                with open(self.file_path, "r", encoding="utf-8-sig") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        self._data = dict(content)
                        loaded_from_disk = True
                    else:
                        logger.warning("settings.json content is not a dict, initializing defaults")
                        self._data = {}
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {self.file_path}: {e}")
                # Create a backup of corrupt file before replacing
                try:
                    bak_path = self.file_path.with_suffix(".json.bak")
                    shutil.copy2(self.file_path, bak_path)
                    logger.info(f"Backup created at {bak_path}")
                except Exception:
                    pass
                self._data = {}
            except Exception as e:
                logger.error(f"Error reading settings from {self.file_path}: {e}")
                self._data = {}
        else:
            self._data = {}

        # Merge defaults ONLY for missing keys, preserving all user values
        for key, default_val in DEFAULT_SETTINGS.items():
            if key not in self._data:
                self._data[key] = default_val

        # Ensure blacklist contains clean string items
        if not isinstance(self._data.get("blacklist"), list):
            self._data["blacklist"] = list(DEFAULT_BLACKLIST)
        else:
            cleaned = []
            seen = set()
            for item in self._data["blacklist"]:
                if isinstance(item, str) and item.strip():
                    norm = item.strip()
                    lower = norm.lower()
                    if lower not in seen:
                        seen.add(lower)
                        cleaned.append(norm)
            self._data["blacklist"] = cleaned

        # If file didn't exist initially, create it
        if not loaded_from_disk:
            self.save()

    def save(self) -> bool:
        """Save settings safely to the JSON file using atomic write."""
        try:
            temp_path = self.file_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            temp_path.replace(self.file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings to {self.file_path}: {e}")
            return False

    # --- Blacklist helpers ---

    @property
    def blacklist(self) -> List[str]:
        return list(self._data.get("blacklist", []))

    def add_to_blacklist(self, phrase: str) -> bool:
        """Add a new phrase or word to the blacklist."""
        clean = phrase.strip()
        if not clean:
            return False
        
        current = self.blacklist
        lower_clean = clean.lower()
        if any(item.lower() == lower_clean for item in current):
            return False  # Already exists
        
        current.append(clean)
        self._data["blacklist"] = current
        self.save()
        return True

    def remove_from_blacklist(self, phrase: str) -> bool:
        """Remove a phrase from the blacklist."""
        clean = phrase.strip().lower()
        current = self.blacklist
        new_list = [item for item in current if item.strip().lower() != clean]
        if len(new_list) != len(current):
            self._data["blacklist"] = new_list
            self.save()
            return True
        return False

    def clear_blacklist(self) -> None:
        """Clear all items from blacklist."""
        self._data["blacklist"] = []
        self.save()

    def reset_blacklist_to_default(self) -> None:
        """Reset blacklist to the default built-in list."""
        self._data["blacklist"] = list(DEFAULT_BLACKLIST)
        self.save()

    # --- Search & UI state helpers ---

    @property
    def last_search_query(self) -> str:
        return self._data.get("last_search_query", "")

    @last_search_query.setter
    def last_search_query(self, value: str) -> None:
        if self._data.get("last_search_query") != value.strip():
            self._data["last_search_query"] = value.strip()
            self.save()

    @property
    def remote_only(self) -> bool:
        return self._data.get("remote_only", True)

    @remote_only.setter
    def remote_only(self, value: bool) -> None:
        if self._data.get("remote_only") != bool(value):
            self._data["remote_only"] = bool(value)
            self.save()

    @property
    def items_to_fetch(self) -> int:
        return self._data.get("items_to_fetch", 100)

    @items_to_fetch.setter
    def items_to_fetch(self, value: int) -> None:
        val = max(20, min(500, int(value)))
        if self._data.get("items_to_fetch") != val:
            self._data["items_to_fetch"] = val
            self.save()

    @property
    def theme(self) -> str:
        return self._data.get("theme", "light")

    @theme.setter
    def theme(self, value: str) -> None:
        if self._data.get("theme") != value:
            self._data["theme"] = value
            self.save()


class BlockedVacanciesStore:
    """Persists manually hidden vacancies independently of word settings."""

    def __init__(self, file_path: Optional[str | Path] = None):
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).resolve().parent
        else:
            base_dir = Path(__file__).resolve().parent
        self.file_path = Path(file_path) if file_path else base_dir / "blocked_vacancies.json"
        self._vacancies: Dict[int, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        try:
            if not self.file_path.exists():
                return
            with open(self.file_path, "r", encoding="utf-8-sig") as file:
                data = json.load(file)
            records = data.get("vacancies", []) if isinstance(data, dict) else []
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, dict) and isinstance(record.get("id"), int) and record["id"]:
                        self._vacancies[record["id"]] = record
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Could not load manually blocked vacancies: %s", error)

    @property
    def ids(self) -> set[int]:
        return set(self._vacancies)

    def add(self, vacancy: Any) -> bool:
        """Store a vacancy identifier and useful context for later reference."""
        if not getattr(vacancy, "id", 0) or vacancy.id in self._vacancies:
            return False
        self._vacancies[vacancy.id] = {
            "id": vacancy.id,
            "name": vacancy.name,
            "company_name": vacancy.company_name,
            "url": vacancy.url,
        }
        return self.save()

    def remove(self, vacancy_id: int) -> bool:
        if vacancy_id not in self._vacancies:
            return False
        del self._vacancies[vacancy_id]
        return self.save()

    def save(self) -> bool:
        try:
            temp_path = self.file_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump({"vacancies": list(self._vacancies.values())}, file, ensure_ascii=False, indent=2)
            temp_path.replace(self.file_path)
            return True
        except OSError as error:
            logger.error("Could not save manually blocked vacancies: %s", error)
            return False
