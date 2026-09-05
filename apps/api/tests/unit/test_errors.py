"""Unit tests for the CanaryError hierarchy."""

from __future__ import annotations

from canary_api.core.errors import (
    CanaryError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def test_canary_error_message():
    err = CanaryError("something went wrong")
    assert err.message == "something went wrong"
    assert err.details == {}


def test_canary_error_with_details():
    err = CanaryError("oops", details={"field": "email"})
    assert err.details == {"field": "email"}


def test_subclasses_are_canary_errors():
    for cls in [NotFoundError, ValidationError, ConflictError, UnauthorizedError, ForbiddenError]:
        err = cls("msg")
        assert isinstance(err, CanaryError)


def test_not_found_error():
    err = NotFoundError("Project 123 not found.")
    assert "123" in err.message
