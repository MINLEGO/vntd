"""Unit tests for vntd.model.proxy — Proxy dataclass url property."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.proxy import Proxy


class TestProxyModel(unittest.TestCase):
    """Test Proxy dataclass url property."""

    def test_url_without_auth(self):
        proxy = Proxy(host="1.2.3.4", port=8080)
        self.assertEqual(proxy.url, "http://1.2.3.4:8080")

    def test_url_with_auth(self):
        proxy = Proxy(host="1.2.3.4", port=8080, username="user", password="pass")
        self.assertEqual(proxy.url, "http://user:pass@1.2.3.4:8080")

    def test_url_with_https_scheme(self):
        proxy = Proxy(host="1.2.3.4", port=443, scheme="https")
        self.assertEqual(proxy.url, "https://1.2.3.4:443")

    def test_url_with_https_and_auth(self):
        proxy = Proxy(
            host="proxy.example.com", port=3128, scheme="https",
            username="admin", password="secret",
        )
        self.assertEqual(proxy.url, "https://admin:secret@proxy.example.com:3128")

    def test_url_with_partial_auth_username_only(self):
        """Only username, no password — no auth embedded in URL."""
        proxy = Proxy(host="1.2.3.4", port=8080, username="user")
        self.assertEqual(proxy.url, "http://1.2.3.4:8080")


if __name__ == "__main__":
    unittest.main()
