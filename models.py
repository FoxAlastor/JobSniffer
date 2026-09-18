"""
Data models for the Robota.ua vacancy desktop application.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import html
import re
from bs4 import BeautifulSoup


@dataclass
class Vacancy:
    """Represents a job listing from robota.ua."""
    id: int
    name: str
    company_name: str
    city_name: str
    salary: int = 0
    salary_from: int = 0
    salary_to: int = 0
    salary_comment: str = ""
    date_str: str = ""
    date: Optional[datetime] = None
    short_description: str = ""
    full_description: str = ""
    notebook_id: int = 0
    hot: bool = False
    is_remote: bool = False
    badges: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Direct URL to the vacancy on robota.ua."""
        if self.notebook_id and self.id:
            return f"https://robota.ua/company{self.notebook_id}/vacancy{self.id}"
        return f"https://robota.ua/vacancy/{self.id}"

    @property
    def formatted_salary(self) -> str:
        """Human-readable salary string in Ukrainian."""
        if self.salary_from > 0 and self.salary_to > 0:
            if self.salary_from == self.salary_to:
                val = f"{self.salary_from:,}".replace(",", " ")
                res = f"{val} грн"
            else:
                s_from = f"{self.salary_from:,}".replace(",", " ")
                s_to = f"{self.salary_to:,}".replace(",", " ")
                res = f"{s_from} – {s_to} грн"
        elif self.salary_from > 0:
            s_from = f"{self.salary_from:,}".replace(",", " ")
            res = f"від {s_from} грн"
        elif self.salary_to > 0:
            s_to = f"{self.salary_to:,}".replace(",", " ")
            res = f"до {s_to} грн"
        elif self.salary > 0:
            val = f"{self.salary:,}".replace(",", " ")
            res = f"{val} грн"
        else:
            res = "Не вказано"

        if self.salary_comment and self.salary_comment.strip():
            comm = self.salary_comment.strip()
            if res == "Не вказано":
                res = comm
            else:
                res = f"{res} ({comm})"

        return res

    @property
    def formatted_date(self) -> str:
        """Formatted publication date."""
        if not self.date:
            return self.date_str or "Нещодавно"
        
        dt = self.date
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
            
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            return f"Сьогодні, {dt.strftime('%H:%M')}"
        elif diff.days == 1:
            return f"Вчора, {dt.strftime('%H:%M')}"
        elif diff.days < 7:
            return f"{diff.days} дн. тому"
        else:
            return dt.strftime("%d.%m.%Y")

    @property
    def clean_description(self) -> str:
        """Clean plain text of the description."""
        text = self.full_description or self.short_description or ""
        if not text:
            return ""
        if "<" not in text:
            return text.strip()
        try:
            soup = BeautifulSoup(text, "html.parser")
            clean = soup.get_text(separator="\n").strip()
            clean = re.sub(r"\n{3,}", "\n\n", clean)
            return clean
        except Exception:
            return text.strip()

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any], is_remote: Optional[bool] = None) -> Vacancy:
        """Factory method to construct Vacancy from Robota.ua API JSON object."""
        v_id = data.get("id", 0)
        name = (data.get("name") or "").strip()
        company_name = (data.get("companyName") or "Невідома компанія").strip()
        city_name = (data.get("cityName") or "").strip()
        salary = data.get("salary") or 0
        salary_from = data.get("salaryFrom") or 0
        salary_to = data.get("salaryTo") or 0
        salary_comment = (data.get("salaryComment") or "").strip()
        
        date_raw = data.get("date") or ""
        parsed_date = None
        if date_raw:
            try:
                iso_clean = date_raw.split(".")[0]
                parsed_date = datetime.fromisoformat(iso_clean)
            except Exception:
                pass

        short_desc = data.get("shortDescription") or ""
        full_desc = data.get("description") or ""
        notebook_id = data.get("notebookId") or 0
        hot = bool(data.get("hot", False))
        
        badges_list = []
        raw_badges = data.get("badges") or []
        for b in raw_badges:
            if isinstance(b, dict) and b.get("name"):
                badges_list.append(b.get("name"))
            elif isinstance(b, str):
                badges_list.append(b)

        if is_remote is not None:
            remote_status = is_remote
        else:
            schedule_id = data.get("scheduleId")
            remote_status = schedule_id == 3
            if not remote_status:
                search_text = f"{name} {city_name} {' '.join(badges_list)} {short_desc}".lower()
                if any(w in search_text for w in ["remote", "віддален", "дистанційн", "віддалена робота"]):
                    remote_status = True

        return cls(
            id=v_id,
            name=name,
            company_name=company_name,
            city_name=city_name,
            salary=salary,
            salary_from=salary_from,
            salary_to=salary_to,
            salary_comment=salary_comment,
            date_str=date_raw,
            date=parsed_date,
            short_description=short_desc,
            full_description=full_desc,
            notebook_id=notebook_id,
            hot=hot,
            is_remote=remote_status,
            badges=badges_list,
            raw_data=data
        )
