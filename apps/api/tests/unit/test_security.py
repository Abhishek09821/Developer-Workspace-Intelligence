"""Unit tests for password hashing and JWT helpers."""

from __future__ import annotations

import uuid
import pytest

from canary_api.application.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from canary_api.core.errors import UnauthorizedError


@pytest.fixture
def settings(test_settings):
    return test_settings


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        plain = "supersecret123"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        plain = "supersecret123"
        assert verify_password(plain, hash_password(plain)) is True

    def test_verify_wrong_password(self):
        assert verify_password("wrong", hash_password("correct")) is False

    def test_different_hashes_for_same_password(self):
        plain = "password123"
        # bcrypt uses a salt so two hashes of the same password differ
        assert hash_password(plain) != hash_password(plain)


class TestJWT:
    def test_create_and_decode(self, settings):
        user_id = uuid.uuid4()
        token = create_access_token(subject=user_id, settings=settings)
        decoded = decode_access_token(token, settings=settings)
        assert decoded == user_id

    def test_invalid_token_raises(self, settings):
        with pytest.raises(UnauthorizedError):
            decode_access_token("not.a.jwt", settings=settings)

    def test_tampered_token_raises(self, settings):
        user_id = uuid.uuid4()
        token = create_access_token(subject=user_id, settings=settings)
        tampered = token[:-4] + "XXXX"
        with pytest.raises(UnauthorizedError):
            decode_access_token(tampered, settings=settings)
