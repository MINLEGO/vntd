from dataclasses import dataclass
from typing import Any

from .ad import Ad


@dataclass
class Pagination:
    current_page: int
    total_pages: int
    total_entries: int
    per_page: int


@dataclass
class Search:
    pagination: Pagination
    ads: list[Ad]

    @property
    def total(self) -> int:
        return self.pagination.total_entries

    @staticmethod
    def _build(raw: dict, client: Any) -> "Search":
        ads: list[Ad] = [
            Ad._build_from_search(raw=ad, client=client)
            for ad in raw.get("items", [])
        ]

        pagination = raw.get("pagination", {})
        return Search(
            pagination=Pagination(
                current_page=pagination.get("current_page"),
                total_pages=pagination.get("total_pages"),
                total_entries=pagination.get("total_entries"),
                per_page=pagination.get("per_page"),
            ),
            ads=ads,
        )
