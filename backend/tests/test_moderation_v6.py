"""Moderation feature tests for v6 — strict harmful-content blocking on POST /api/posts.

Verifies:
  - Unsafe inputs return HTTP 400 with detail starting with 'Your post was blocked for '
    and mentioning hate/threats/abuse/harmful keywords.
  - Safe inputs return HTTP 200 with a valid Post object.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")

UNSAFE = [
    "i will kill you",
    "i'll punch your face",
    "shoot up a school",
    "you're a piece of shit",
    "break your bones tonight",
    "nigger",
    "kill all jews",
    "shoot you tomorrow",
]

SAFE = [
    "hello world",
    "crypto looks bullish today",
    "love that midnight playlist!",
]


def _fresh_device():
    return f"test-mod-{uuid.uuid4().hex[:12]}"


def _post(content, device_id=None):
    device_id = device_id or _fresh_device()
    return requests.post(
        f"{BASE_URL}/api/posts",
        json={"content": content, "topic": "rant", "device_id": device_id},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )


class TestUnsafeBlocked:
    @pytest.mark.parametrize("phrase", UNSAFE)
    def test_unsafe_returns_400_with_friendly_detail(self, phrase):
        r = _post(phrase)
        assert r.status_code == 400, f"Expected 400 for {phrase!r}, got {r.status_code}: {r.text}"
        body = r.json()
        detail = body.get("detail", "")
        assert isinstance(detail, str) and detail, f"missing detail for {phrase!r}: {body}"
        assert detail.startswith("Your post was blocked for "), (
            f"detail must start with 'Your post was blocked for ' — got: {detail!r}"
        )
        lower = detail.lower()
        # must mention at least one of the friendly categories
        assert any(k in lower for k in ("hate", "threats", "abuse", "harmful")), (
            f"detail should mention hate/threats/abuse/harmful — got: {detail!r}"
        )


class TestSafeAllowed:
    @pytest.mark.parametrize("phrase", SAFE)
    def test_safe_returns_200_with_post_object(self, phrase):
        r = _post(phrase)
        assert r.status_code == 200, f"Expected 200 for {phrase!r}, got {r.status_code}: {r.text}"
        post = r.json()
        # validate response structure
        assert "id" in post and isinstance(post["id"], str)
        assert post.get("content") == phrase
        assert post.get("topic") == "rant"
        assert "created_at" in post
        assert "expires_at" in post
        # Mongo _id must not leak
        assert "_id" not in post
