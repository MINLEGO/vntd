from dataclasses import dataclass, field
from typing import Any

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

        raw_user = raw.get("user", {})
        return Ad(
            id=raw.get("id"),
            title=raw.get("title"),
            description=None,
            price=price,
            currency=raw_price.get("currency_code"),
            brand=raw.get("brand_title"),
            size=raw.get("size_title"),
            status=raw.get("status"),
            url=raw.get("url"),
            images=images,
            favorite_count=raw.get("favourite_count"),
            view_count=raw.get("view_count"),
            category=None,
            color=None,
            _client=client,
            _user_id=raw_user.get("id"),
            _user=None,
        )

    @staticmethod
    def _build_from_item_page(
        raw: dict, item_id: int, url: str, seller_id: int | None, client: Any
    ) -> "Ad":
        images = raw.get("image") or []
        if isinstance(images, str):
            images = [images]

        offers = raw.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        price_value = offers.get("price")
        price = float(price_value) if price_value is not None else None

        brand = raw.get("brand", {})
        if isinstance(brand, dict):
            brand = brand.get("name")
        elif isinstance(brand, list):
            brand = brand[0].get("name") if brand else None

        return Ad(
            id=item_id,
            title=raw.get("name"),
            description=raw.get("description"),
            price=price,
            currency=offers.get("priceCurrency"),
            brand=brand,
            size=None,
            status=offers.get("itemCondition"),
            url=url,
            images=images,
            favorite_count=None,
            view_count=None,
            category=raw.get("category"),
            color=raw.get("color"),
            _client=client,
            _user_id=seller_id,
            _user=None,
        )

    @property
    def subject(self) -> str:
        return self.title

    @property
    def user(self) -> User | None:
        if self._user is None and self._user_id is not None:
            self._user = self._client.get_user(user_id=self._user_id)
        return self._user
