from ..model import Sort, SellerType, Search
from ..utils import build_search_params_with_args, build_search_params_with_url


class SearchMixin:
    def search(
        self,
        url: str | None = None,
        text: str | None = None,
        sort: Sort = Sort.RELEVANCE,
        page: int = 1,
        limit: int = 24,
        seller_type: SellerType = SellerType.ALL,
        user_id: int | None = None,
        price: tuple[int | None, int | None] | list[int | None] | None = None,
        **filters,
    ) -> Search:
        """
        Perform an item search on Vinted with the specified criteria.

        You can either:
        - Provide a full `url` from a Vinted search to replicate the search directly.
        - Or use the individual parameters (`text`, `sort`, `price`, etc.) to construct a custom search.
        """
        if url:
            params = build_search_params_with_url(url=url, limit=limit, page=page)
        else:
            params = build_search_params_with_args(
                text=text,
                sort=sort,
                page=page,
                limit=limit,
                seller_type=seller_type,
                user_id=user_id,
                price=price,
                **filters,
            )

        body = self._fetch(
            method="GET",
            url=f"{self.base_url}/api/v2/catalog/items",
            params=params,
        )
        return Search._build(raw=body, client=self)
