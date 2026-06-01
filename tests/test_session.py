"""Unit tests for vntd.mixin.session — Proxy property setter."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.model.proxy import Proxy

from tests.helpers import _mock_response


class TestProxySetter(unittest.TestCase):
    """Test the SessionMixin.proxy property setter."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_proxy_setter_updates_session_proxies(self):
        proxy = Proxy(host="10.0.0.1", port=9090)
        self.client.proxy = proxy
        self.assertEqual(
            self.client.session.proxies,
            {"http": "http://10.0.0.1:9090", "https": "http://10.0.0.1:9090"},
        )
        self.assertEqual(self.client.proxy, proxy)

    def test_proxy_setter_none_clears_proxies(self):
        self.client.proxy = Proxy(host="10.0.0.1", port=9090)
        self.client.proxy = None
        self.assertEqual(self.client.session.proxies, {})
        self.assertIsNone(self.client.proxy)

    def test_proxy_setter_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.client.proxy = "not a proxy"

    def test_initial_proxy_applied_to_session(self):
        proxy = Proxy(host="1.1.1.1", port=3128)
        client = Client(base_url="https://www.vinted.fr", proxy=proxy)
        self.assertIn("http", client.session.proxies)
        self.assertIn("https", client.session.proxies)


if __name__ == "__main__":
    unittest.main()
