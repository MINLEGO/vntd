from ..model import User


class UserMixin:
    def get_user(self, user_id: str | int) -> User:
        """
        Retrieve information about a Vinted user based on their user ID.
        """
        user_data = self._fetch(
            method="GET",
            url=f"{self.base_url}/api/v2/users/{user_id}",
        )
        return User._build(raw=user_data.get("user", {}))
