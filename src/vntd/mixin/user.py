from ..model import Search, Sort, User


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

    def get_user_ads(
        self,
        user_id: str | int,
        page: int = 1,
        limit: int = 24,
        sort: Sort = Sort.RELEVANCE,
    ) -> Search:
        """
        Retrieve the ads a Vinted user currently has on sale.

        Only live listings are returned (sold ones are not, but `get_ad` still
        works on them). An unknown user ID gives an empty `Search`.
        """
        body = self._fetch(
            method="GET",
            url=f"{self.base_url}/api/v2/wardrobe/{user_id}/items",
            params={"page": page, "per_page": limit, "order": sort.value},
            headers=dict(self.session.headers),
        )
        return Search._build(raw=body, client=self)
