from urllib.parse import parse_qs, urlparse

from .model import Sort, SellerType
from .exceptions import InvalidValue


def _normalize_list(value) -> str:
    if isinstance(value, (list, tuple, set)):
        return ",".join(str(item) for item in value)
    return str(value)


def build_search_params_with_url(url: str, limit: int = 24, page: int = 1) -> dict:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    params = {}
    for key, values in query.items():
        if not values:
            continue
        params[key] = ",".join(values) if len(values) > 1 else values[0]

    params["page"] = page
    params["per_page"] = limit
    return params


def build_search_params_with_args(
    text: str | None = None,
    sort: Sort = Sort.RELEVANCE,
    page: int = 1,
    limit: int = 24,
    seller_type: SellerType = SellerType.ALL,
    user_id: int | None = None,
    price: tuple[int | None, int | None] | list[int | None] | None = None,
    **filters,
) -> dict:
    params: dict = {
        "page": page,
        "per_page": limit,
    }

    if text:
        params["search_text"] = text

    if sort:
        params["order"] = sort.value

    if seller_type == SellerType.BUSINESS:
        params["is_business"] = 1
    elif seller_type == SellerType.INDIVIDUAL:
        params["is_business"] = 0

    if user_id is not None:
        params["user_id"] = user_id

    if price is not None:
        if not isinstance(price, (list, tuple)) or len(price) != 2:
            raise InvalidValue("price must be a (min, max) tuple.")
        min_price, max_price = price
        if min_price is not None:
            params["price_from"] = min_price
        if max_price is not None:
            params["price_to"] = max_price
    if limit*page > 960:
        print("Warning: max item index exceeds 960, which seems to be the maximum provided by the Vinted API. You may receive an error")

    for key, value in filters.items():
        if value is None:
            continue
        params[key] = _normalize_list(value)

    return params
