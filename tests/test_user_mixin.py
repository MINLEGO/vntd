"""Unit tests for vntd.mixin.user — get_user integration with mocked HTTP."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.model.user import User

from tests.helpers import _mock_response, _sample_user_raw


class TestGetUserIntegration(unittest.TestCase):
    """Test get_user() end-to-end with mocked HTTP."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_get_user_returns_user_object(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={"user": _sample_user_raw()}
        )
        user = self.client.get_user(123)
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.login, "testuser")

    def test_get_user_calls_correct_endpoint(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={"user": _sample_user_raw()}
        )
        self.client.get_user(42)
        url = self.mock_session.request.call_args.kwargs["url"]
        self.assertEqual(url, "https://www.vinted.fr/api/v2/users/42")


if __name__ == "__main__":
    unittest.main()
