"""Unit tests for vntd.client — Client init, fetch retry, and base_url handling."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.exceptions import (
    AccessDeniedError,
    InvalidValue,
    NotFoundError,
    RequestError,
)

from tests.helpers import _mock_response


# ---------------------------------------------------------------------------
# 1. Error & Resilience Tests
# ---------------------------------------------------------------------------


class TestFetchRetryAndErrors(unittest.TestCase):
    """Verify _fetch retry logic and exception mapping for HTTP error codes."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr", max_retries=3)

    # --- 403 / 429 ----------------------------------------------------------

    def test_403_retries_then_raises_access_denied(self):
        """403 responses are retried up to max_retries, then AccessDeniedError."""
        self.mock_session.request.return_value = _mock_response(status_code=403)

        with self.assertRaises(AccessDeniedError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

        # 1 initial + 3 retries = 4 total request calls
        self.assertEqual(self.mock_session.request.call_count, 4)
        # 1 from __init__ + 3 re-inits = 4 total get calls
        self.assertEqual(self.mock_session.get.call_count, 4)

    def test_429_retries_then_raises_access_denied(self):
        """429 responses follow the same retry path as 403."""
        self.mock_session.request.return_value = _mock_response(status_code=429)

        with self.assertRaises(AccessDeniedError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

        self.assertEqual(self.mock_session.request.call_count, 4)

    def test_403_succeeds_after_retry(self):
        """If a retry succeeds, _fetch returns the successful response."""
        fail_resp = _mock_response(status_code=403)
        ok_resp = _mock_response(json_data={"ok": True})
        self.mock_session.request.side_effect = [fail_resp, ok_resp]

        result = self.client._fetch("GET", "https://www.vinted.fr/api/test")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(self.mock_session.request.call_count, 2)

    def test_custom_max_retries_overrides_default(self):
        """Passing max_retries to _fetch overrides the client default."""
        self.mock_session.request.return_value = _mock_response(status_code=403)

        with self.assertRaises(AccessDeniedError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test", max_retries=1)

        # 1 initial + 1 retry = 2 total
        self.assertEqual(self.mock_session.request.call_count, 2)

    # --- 404 / 410 ----------------------------------------------------------

    def test_404_raises_not_found_error(self):
        """A 404 response raises NotFoundError immediately (no retry)."""
        self.mock_session.request.return_value = _mock_response(status_code=404)

        with self.assertRaises(NotFoundError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

        self.assertEqual(self.mock_session.request.call_count, 1)

    def test_410_raises_not_found_error(self):
        """A 410 response raises NotFoundError immediately (no retry)."""
        self.mock_session.request.return_value = _mock_response(status_code=410)

        with self.assertRaises(NotFoundError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

        self.assertEqual(self.mock_session.request.call_count, 1)

    # --- 500 ----------------------------------------------------------------

    def test_500_raises_request_error(self):
        """A 500 response raises RequestError immediately (no retry)."""
        self.mock_session.request.return_value = _mock_response(status_code=500)

        with self.assertRaises(RequestError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

        self.assertEqual(self.mock_session.request.call_count, 1)

    def test_422_raises_request_error(self):
        """Any other non-success, non-403/429/404/410 code raises RequestError."""
        self.mock_session.request.return_value = _mock_response(status_code=422)

        with self.assertRaises(RequestError):
            self.client._fetch("GET", "https://www.vinted.fr/api/test")

    # --- happy path ---------------------------------------------------------

    def test_200_returns_json(self):
        """A successful JSON response is parsed and returned."""
        self.mock_session.request.return_value = _mock_response(
            json_data={"items": [1, 2]}
        )
        result = self.client._fetch("GET", "https://www.vinted.fr/api/test")
        self.assertEqual(result, {"items": [1, 2]})

    def test_fetch_text_returns_text(self):
        """_fetch_text returns the response body as a string."""
        self.mock_session.request.return_value = _mock_response(text_data="<html>hi</html>")
        result = self.client._fetch_text("https://www.vinted.fr/items/1")
        self.assertEqual(result, "<html>hi</html>")


# ---------------------------------------------------------------------------
# 2. Input Validation Tests
# ---------------------------------------------------------------------------


class TestClientInitValidation(unittest.TestCase):
    """Verify Client rejects conflicting / invalid constructor arguments."""

    @patch("curl_cffi.requests.Session")
    def test_user_agent_and_user_agents_both_raises_invalid_value(self, mock_cls):
        mock_session = MagicMock()
        mock_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()

        with self.assertRaises(InvalidValue):
            Client(
                base_url="https://www.vinted.fr",
                user_agent="Agent-A",
                user_agents=["Agent-B"],
            )

    @patch("curl_cffi.requests.Session")
    def test_invalid_user_agents_type_raises_invalid_value(self, mock_cls):
        mock_session = MagicMock()
        mock_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()

        with self.assertRaises(InvalidValue):
            Client(
                base_url="https://www.vinted.fr",
                user_agents=[123, 456],  # not strings
            )


# ---------------------------------------------------------------------------
# 13. Client base_url trailing slash
# ---------------------------------------------------------------------------


class TestClientBaseUrl(unittest.TestCase):
    """Verify base_url trailing slash handling."""

    @patch("curl_cffi.requests.Session")
    def test_trailing_slash_stripped(self, mock_cls):
        mock_session = MagicMock()
        mock_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()
        client = Client(base_url="https://www.vinted.fr/")
        self.assertEqual(client.base_url, "https://www.vinted.fr")

    @patch("curl_cffi.requests.Session")
    def test_no_trailing_slash_preserved(self, mock_cls):
        mock_session = MagicMock()
        mock_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()
        client = Client(base_url="https://www.vinted.fr")
        self.assertEqual(client.base_url, "https://www.vinted.fr")


if __name__ == "__main__":
    unittest.main()
