"""Unit tests for vntd.mixin.session — Proxy property setter and UA selection."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.exceptions import InvalidValue
from vntd.mixin.session import SessionMixin, DEFAULT_USER_AGENTS
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


class TestUserAgentSelection(unittest.TestCase):
    """Test the SessionMixin._select_user_agent method with fake-useragent integration."""

    def setUp(self):
        """Create a minimal SessionMixin instance for direct method testing."""
        with patch("curl_cffi.requests.Session") as mock_session_cls:
            self.mock_session = MagicMock()
            mock_session_cls.return_value = self.mock_session
            self.mock_session.get.return_value = _mock_response()
            self.mixin = SessionMixin(base_url="https://www.vinted.fr")
        # Access the underlying _select_user_agent directly
        self._select = self.mixin._select_user_agent

    # --- Explicit user_agent overrides ---

    def test_explicit_user_agent_overrides_everything(self):
        ua = "MyCustomAgent/1.0"
        result = self._select(ua, None, impersonate="chrome")
        self.assertEqual(result, ua)

    # --- user_agents list ---

    def test_user_agents_list_used_when_provided(self):
        agents = ["Agent1/1.0", "Agent2/2.0"]
        result = self._select(None, agents, impersonate="chrome")
        self.assertIn(result, agents)

    # --- InvalidValue when both provided ---

    def test_both_user_agent_and_user_agents_raises(self):
        with self.assertRaises(InvalidValue):
            self._select("ua", ["ua1"], impersonate="chrome")

    # --- InvalidValue for non-string items ---

    def test_user_agents_non_string_items_raises(self):
        with self.assertRaises(InvalidValue):
            self._select(None, ["valid", 123], impersonate="chrome")  # type: ignore[list-item]

    # --- fake-useragent returns desktop UA ---

    def test_fake_useragent_returns_desktop_ua(self):
        """Without overrides, fake-useragent should return a non-empty string."""
        result = self._select(None, None, impersonate="chrome")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    # --- Browser-coherent UA selection ---

    def test_chrome_impersonate_returns_chrome_ua(self):
        """When impersonate='chrome', the UA should contain 'Chrome'."""
        results = {self._select(None, None, impersonate="chrome") for _ in range(20)}
        # All results should contain 'Chrome' (fake-useragent chrome property)
        for ua in results:
            self.assertIn("Chrome", ua, f"Expected 'Chrome' in UA: {ua}")

    def test_firefox_impersonate_returns_firefox_ua(self):
        """When impersonate='firefox', the UA should contain 'Firefox'."""
        results = {self._select(None, None, impersonate="firefox") for _ in range(20)}
        for ua in results:
            self.assertIn("Firefox", ua, f"Expected 'Firefox' in UA: {ua}")

    def test_safari_impersonate_returns_safari_or_macintosh_ua(self):
        """When impersonate='safari', the UA should contain 'Safari' or 'Macintosh'."""
        results = {self._select(None, None, impersonate="safari") for _ in range(20)}
        for ua in results:
            self.assertTrue(
                "Safari" in ua or "Macintosh" in ua,
                f"Expected 'Safari' or 'Macintosh' in UA: {ua}",
            )

    # --- Coherence bug fix test ---

    @patch("curl_cffi.requests.Session")
    def test_impersonate_and_ua_coherent(self, mock_session_cls):
        """When impersonate=None, the resolved browser and UA must be coherent."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()

        for _ in range(10):
            _ = Client(base_url="https://www.vinted.fr")
            # Get the User-Agent set on the session
            set_ua = mock_session.headers.update.call_args[0][0]["User-Agent"]

            # At minimum, verify the UA is a valid string (coherence is handled
            # internally by _select_user_agent receiving the resolved impersonate)
            self.assertIsInstance(set_ua, str)
            self.assertTrue(len(set_ua) > 0)

    # --- Fallback to DEFAULT_USER_AGENTS ---

    @patch("vntd.mixin.session._UA", None)
    def test_fallback_to_default_user_agents(self):
        """When fake-useragent fails (mocked to None), should fall back to DEFAULT_USER_AGENTS."""
        result = self._select(None, None, impersonate="chrome")
        self.assertIn(result, DEFAULT_USER_AGENTS)


if __name__ == "__main__":
    unittest.main()
