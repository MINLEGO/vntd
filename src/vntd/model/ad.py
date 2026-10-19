from dataclasses import dataclass, field
import re
from typing import Any
from urllib.parse import urljoin

from .user import User


@dataclass
class Ad:
    id: int
    title: str
    description: str | None
    price: float | None
    currency: str | None
    brand: str | None
    size: str | None
    status: str | None
    condition: str | None
    url: str
    images: list[str]
    favorite_count: int | None
    view_count: int | None
    category: str | None
    color: str | None

    _client: Any = field(repr=False)
    _user_id: int | None = field(repr=False)
    _user: User | None = field(default=None, repr=False)

    @staticmethod
    def _build_from_search(raw: dict, client: Any) -> "Ad":
        raw_price = raw.get("price", {})
        price_amount = raw_price.get("amount")
        price = float(price_amount) if price_amount is not None else None

        photos = raw.get("photos", [])
        images = [photo.get("url") for photo in photos if photo.get("url")]
        if not images and raw.get("photo", {}).get("url"):
            images = [raw.get("photo", {}).get("url")]

        # item_box is the only place the search gives brand, size and condition.
        item_box = raw.get("item_box") or {}
        first_line = item_box.get("first_line") or ""
        # first_line is the brand only if the label lists it, else it is the title.
        has_brand = re.search(
            r", [^,:]+: " + re.escape(first_line) + r"(?=, |$)",
            item_box.get("accessibility_label") or "",
        )
        # second_line is "<size> · <condition>", the size being optional.
        parts = [p for p in (item_box.get("second_line") or "").split(" · ") if p]

        url = raw.get("url")
        raw_user = raw.get("user", {})
        return Ad(
            id=raw.get("id"),
            title=raw.get("title"),
            description=None,
            price=price,
            currency=raw_price.get("currency_code"),
            brand=first_line if first_line and has_brand else None,
            size=parts[0] if len(parts) > 1 else None,
            status="active",  # shortcut: search only lists items still for sale, rechecked if Vinted lists sold items
            condition=parts[-1] if parts else None,
            url=urljoin(client.base_url + "/", url) if url else None,
            images=images,
            favorite_count=raw.get("favourite_count"),
            view_count=raw.get("view_count"),
            category=None,
            color=None,
            _client=client,
            _user_id=raw_user.get("id"),
            _user=User._build(raw_user) if raw_user.get("id") else None,
        )

    @staticmethod
    def _build_from_item_page(raw: dict, url: str, client: Any) -> "Ad":
        item = raw["item"]
        attributes = raw["attributes"]

        raw_price = item.get("price") or {}
        price_amount = raw_price.get("amount")
        price = float(price_amount) if price_amount is not None else None

        # shortcut: "sold" is any item that cannot be bought, rechecked if Vinted adds a state
        if item.get("is_reserved"):
            status = "reserved"
        elif item.get("can_buy"):
            status = "active"
        else:
            status = "sold"

        seller_id = item.get("seller_id")
        return Ad(
            id=int(item["id"]),
            title=item.get("title"),
            description=raw.get("description"),
            price=price,
            currency=raw_price.get("currency_code"),
            brand=attributes.get("brand"),
            size=attributes.get("size_familiar") or attributes.get("size"),
            status=status,
            condition=attributes.get("status"),
            url=url,
            images=[p["url"] for p in item.get("photos", []) if p.get("url")],
            favorite_count=raw.get("favourite_count"),
            view_count=None,
            category=raw.get("category"),
            color=attributes.get("color"),
            _client=client,
            _user_id=int(seller_id) if seller_id else None,
            _user=None,
        )

    @property
    def subject(self) -> str:
        return self.title

    @property
    def body(self) -> str | None:
        return self.description

    @property
    def favorites(self) -> int | None:
        return self.favorite_count

    @property
    def user(self) -> User | None:
        if self._user is None and self._user_id is not None:
            self._user = self._client.get_user(user_id=self._user_id)
        return self._user
