import json
import re

from ..model import Ad
from ..exceptions import InvalidValue, ParseError

# The item page ships its data as JSON strings pushed into `self.__next_f`.
_FLIGHT_CHUNK = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
_DECODER = json.JSONDecoder()


class AdMixin:
    def get_ad(self, ad_id: str | int) -> Ad:
        """
        Retrieve detailed information about a Vinted item using its ID or URL.
        """
        item_id = self._extract_item_id(ad_id)
        url = f"{self.base_url}/items/{item_id}"

        html = self._fetch_text(url)
        raw = self._extract_item_page(html, item_id)
        return Ad._build_from_item_page(raw=raw, url=url, client=self)

    def _extract_item_id(self, ad_id: str | int) -> int:
        if isinstance(ad_id, int):
            return ad_id

        if isinstance(ad_id, str):
            match = re.search(r"/items/(\d+)", ad_id)
            if match:
                return int(match.group(1))
            match = re.search(r"^(\d+)", ad_id)
            if match:
                return int(match.group(1))

        raise InvalidValue("ad_id must be a Vinted item ID or item URL.")

    def _extract_item_page(self, html: str, item_id: int) -> dict:
        """Collect the item data embedded in an item page (sold items included)."""
        try:
            text = "".join(json.loads(chunk) for chunk in _FLIGHT_CHUNK.findall(html))
        except ValueError as e:
            raise ParseError("Unable to decode the item page data.") from e

        item = self._find_object(text, f'{{"id":"{item_id}","seller_id"', "id", item_id)
        if not item:
            raise ParseError("Unable to find item details.")

        attributes = self._find_object(text, '{"attributes":[', "item_id", item_id)
        description = self._find_object(text, '{"description":"', "item_id", item_id)
        favourites = self._find_object(text, '{"favourite_count":', "item_id", item_id)

        category = None
        crumbs = re.search(r'"breadcrumbs":(\[)', text)
        if crumbs:
            # The last crumb is a brand shortcut (".../brand/..."), not a category.
            titles = [
                crumb["title"]
                for crumb in _DECODER.raw_decode(text, crumbs.start(1))[0]
                if "/brand/" not in crumb.get("url", "")
            ]
            category = titles[-1] if titles else None

        return {
            "item": item,
            "attributes": {
                attribute["code"]: attribute["data"].get("value")
                for attribute in (attributes or {}).get("attributes", [])
            },
            "description": (description or {}).get("description"),
            "favourite_count": (favourites or {}).get("favourite_count"),
            "category": category,
        }

    @staticmethod
    def _find_object(text: str, prefix: str, key: str, item_id: int) -> dict | None:
        """Decode the first JSON object starting with `prefix` whose `key` is `item_id`."""
        for match in re.finditer(re.escape(prefix), text):
            try:
                obj, _ = _DECODER.raw_decode(text, match.start())
            except ValueError:
                continue
            if str(obj.get(key)) == str(item_id):
                return obj
        return None
