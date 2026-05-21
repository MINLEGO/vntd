from html import unescape
import json
import re

from ..model import Ad
from ..exceptions import InvalidValue, NotFoundError


class AdMixin:
    def get_ad(self, ad_id: str | int) -> Ad:
        """
        Retrieve detailed information about a Vinted item using its ID or URL.
        """
        item_id = self._extract_item_id(ad_id)
        url = f"{self.base_url}/items/{item_id}"

        html = self._fetch_text(url)
        ld_data = self._extract_json_ld(html)
        if not ld_data:
            raise NotFoundError("Unable to find item details.")

        seller_id = self._extract_seller_id(html)
        return Ad._build_from_item_page(
            raw=ld_data, item_id=item_id, url=url, seller_id=seller_id, client=self
        )

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

    def _extract_json_ld(self, html: str) -> dict | None:
        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        if not match:
            return None
        raw_json = unescape(match.group(1)).strip()
        return json.loads(raw_json)

    def _extract_seller_id(self, html: str) -> int | None:
        match = re.search(r'\\"seller_id\\":(\d+)', html)
        return int(match.group(1)) if match else None
