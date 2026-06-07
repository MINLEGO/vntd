from dataclasses import dataclass


@dataclass
class User:
    id: int
    login: str
    profile_url: str | None
    business: bool | None
    feedback_count: int | None
    feedback_reputation: float | None
    item_count: int | None
    total_items_count: int | None
    followers_count: int | None
    following_count: int | None
    country_code: str | None
    city: str | None
    about: str | None
    photo_url: str | None

    @staticmethod
    def _build(raw: dict) -> "User":
        photo = raw.get("photo", {}) or {}
        return User(
            id=raw.get("id"),
            login=raw.get("login"),
            profile_url=raw.get("profile_url"),
            business=raw.get("business"),
            feedback_count=raw.get("feedback_count"),
            feedback_reputation=raw.get("feedback_reputation"),
            item_count=raw.get("item_count"),
            total_items_count=raw.get("total_items_count"),
            followers_count=raw.get("followers_count"),
            following_count=raw.get("following_count"),
            country_code=raw.get("country_code"),
            city=raw.get("city"),
            about=raw.get("about"),
            photo_url=photo.get("url"),
        )

    @property
    def name(self) -> str:
        return self.login

    @property
    def is_pro(self) -> bool:
        return self.business

    @property
    def feedback_score(self) -> float | None:
        return self.feedback_reputation * 5 if self.feedback_reputation else None
