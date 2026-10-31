from dataclasses import dataclass, field


@dataclass
class Feedback:
    overall_score: float | None
    received_count: int | None

    @property
    def score(self) -> float | None:
        return self.overall_score * 5 if self.overall_score else None


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
    # The JSON read to build the user: the user object embedded in a search item, or for get_user the `user` of /users/{id}.
    raw: dict = field(repr=False, compare=False)

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
            raw=raw,
        )

    @property
    def name(self) -> str:
        return self.login

    @property
    def is_pro(self) -> bool:
        return bool(self.business)

    @property
    def account_type(self) -> str:
        return "pro" if self.is_pro else "private"

    @property
    def profile_picture(self) -> str | None:
        return self.photo_url

    @property
    def description(self) -> str | None:
        return self.about

    @property
    def location(self) -> str | None:
        if self.city and self.country_code:
            return f"{self.city}, {self.country_code}"
        return self.city or self.country_code or None

    @property
    def feedback(self) -> Feedback:
        return Feedback(
            overall_score=self.feedback_reputation,
            received_count=self.feedback_count,
        )

    @property
    def feedback_score(self) -> float | None:
        return self.feedback.score
