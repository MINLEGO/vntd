"""Unit tests for vntd.exceptions — Exception class hierarchy."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.exceptions import (
    AccessDeniedError,
    InvalidValue,
    NotFoundError,
    RequestError,
    VintedError,
)


class TestExceptionHierarchy(unittest.TestCase):
    """Verify the exception class hierarchy is correct."""

    def test_access_denied_is_request_error(self):
        self.assertTrue(issubclass(AccessDeniedError, RequestError))

    def test_request_error_is_vinted_error(self):
        self.assertTrue(issubclass(RequestError, VintedError))

    def test_not_found_is_vinted_error(self):
        self.assertTrue(issubclass(NotFoundError, VintedError))

    def test_invalid_value_is_vinted_error(self):
        self.assertTrue(issubclass(InvalidValue, VintedError))

    def test_access_denied_is_also_vinted_error(self):
        self.assertTrue(issubclass(AccessDeniedError, VintedError))

    def test_all_exceptions_are_base_exceptions(self):
        for exc_cls in (VintedError, RequestError, AccessDeniedError, NotFoundError, InvalidValue):
            self.assertTrue(issubclass(exc_cls, Exception))


if __name__ == "__main__":
    unittest.main()
