from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import vntd
from vntd.mixin.session import DEFAULT_USER_AGENTS

BASE_URL = os.getenv("VNTD_BASE_URL", "https://www.vinted.fr")


class VintedClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = vntd.Client(base_url=BASE_URL)
        cls.search_result = cls.client.search(
            text="robe",
            page=1,
            limit=2,
            sort=vntd.Sort.RELEVANCE,
        )
        if not cls.search_result.ads:
            raise AssertionError("Search returned no items.")

        cls.sample_ad = cls.search_result.ads[0]
        cls.sample_item_id = cls.sample_ad.id
        cls.sample_user_id = cls.sample_ad._user_id

    def test_search_returns_ads(self) -> None:
        self.assertGreater(len(self.search_result.ads), 0)
        self.assertIsNotNone(self.search_result.total)

    def test_search_with_url(self) -> None:
        result = self.client.search(
            url=(
                f"{BASE_URL}/catalog?search_text=robe&order=newest_first&price_from=5&price_to=20"
            ),
            page=1,
            limit=2,
        )
        self.assertGreater(len(result.ads), 0)

    def test_get_ad(self) -> None:
        ad = self.client.get_ad(self.sample_item_id)
        self.assertEqual(ad.id, self.sample_item_id)
        self.assertTrue(ad.title)

    def test_get_user(self) -> None:
        self.assertIsNotNone(self.sample_user_id)
        user = self.client.get_user(self.sample_user_id)
        self.assertEqual(user.id, self.sample_user_id)
        self.assertTrue(user.login)

    def test_ad_user_lookup(self) -> None:
        user = self.sample_ad.user
        self.assertIsNotNone(user)
        if user:
            self.assertEqual(user.id, self.sample_user_id)

    def test_proxy_assignment(self) -> None:
        proxy = vntd.Proxy(host="127.0.0.1", port=12345)
        client = vntd.Client(base_url=BASE_URL, proxy=proxy)
        self.assertIn("http", client.session.proxies)
        client.proxy = None
        self.assertEqual(client.session.proxies, {})

    def test_user_agent_list_selection(self) -> None:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        ]
        client = vntd.Client(base_url=BASE_URL, user_agents=user_agents)
        self.assertIn(client.session.headers.get("User-Agent"), user_agents)

    def test_user_agent_variants_work(self) -> None:
        self.assertGreater(len(DEFAULT_USER_AGENTS), 0)
        for user_agent in DEFAULT_USER_AGENTS:
            client = vntd.Client(base_url=BASE_URL, user_agent=user_agent)
            result = client.search(text="robe", page=1, limit=1)
            self.assertGreater(len(result.ads), 0)


if __name__ == "__main__":
    unittest.main()
