from urllib.parse import parse_qs, urlparse, urlsplit, urlunsplit

from .model import Sort, SellerType
from .exceptions import InvalidValue


LEGACY_SEARCH_FILTERS = {
    "catalog_ids": "attribute_ids[catalog]",
    "status_ids": "attribute_ids[status]",
    "brand_ids": "attribute_ids[brand]",
    "size_ids": "attribute_ids[size]",
}


def normalize_base_url(base_url: str) -> str:
    """Normalize a Vinted base URL to its ``www`` site host."""
    base_url = base_url.rstrip("/")
    parsed = urlsplit(base_url)
    if not parsed.scheme or not parsed.hostname:
        return base_url

    hostname = parsed.hostname.lower()
    if not hostname.startswith("www."):
        hostname = f"www.{hostname}"

    if parsed.port is not None:
        hostname = f"{hostname}:{parsed.port}"

    return urlunsplit((parsed.scheme, hostname, "", "", ""))


def derive_api_base_url(base_url: str) -> str:
    """Derive the Vinted ``api`` host from a site URL."""
    parsed = urlsplit(base_url.rstrip("/"))
    if not parsed.scheme or not parsed.hostname:
        return base_url.rstrip("/")

    hostname = parsed.hostname.lower()
    if hostname.startswith("www."):
        hostname = f"api.{hostname[4:]}"
    elif not hostname.startswith("api."):
        hostname = f"api.{hostname}"

    if parsed.port is not None:
        hostname = f"{hostname}:{parsed.port}"

    return urlunsplit((parsed.scheme, hostname, "", "", ""))


def _translate_search_filter_names(params: dict) -> dict:
    """Translate the legacy public filter names to catalogue attributes."""
    translated = dict(params)
    for legacy_name, catalogue_name in LEGACY_SEARCH_FILTERS.items():
        if legacy_name in translated:
            translated.setdefault(catalogue_name, translated[legacy_name])
            del translated[legacy_name]
    return translated


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
    return _translate_search_filter_names(params)


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
        raise InvalidValue("Max item index exceeds 960, ")
    if limit > 96:
        print("Warning: limit exceeds 96, vinted will automaticly cap at 96.")

    for key, value in filters.items():
        if value is None:
            continue
        params[key] = _normalize_list(value)

    return _translate_search_filter_names(params)
