"""v7 moderation tests — bomb/threat/extremism phrases must be blocked.

Verifies:
  - 15 specific unsafe phrases return HTTP 400 with detail starting with
    'Your post was blocked for ' and mentioning 'violent extremism or terror promotion'
    OR 'hate speech, threats or abusive language'.
  - Safe lookalikes ('bomb diggity', 'bombed my exam', etc.) still return HTTP 200.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")

UNSAFE_V7 = [
    "i will bomb that place",
    "i'll bomb the building",
    "gonna blow up the office",
    "burn down that mosque",
    "bringing a gun to school",
    "im going to bomb that mall",
    "behead them all",
    "release sarin in the subway",
    "build an ied",
    "drive into a crowd",
    "plant a bomb in the airport",
    "detonate a bomb tomorrow",
    "open fire on the crowd",
    "shoot up the mall",
    "kill all immigrants",
]

SAFE_V7 = [
    "that show was the bomb diggity",
    "i bombed my exam last week",
    "this album goes hard",
    "crypto is up today",
]

ALLOWED_FRIENDLY_PHRASES = (
    "violent extremism or terror promotion",
    "hate speech, threats or abusive language",
)


def _fresh_device():
    return f"test-v7-{uuid.uuid4().hex[:12]}"


def _post(content):
    return requests.post(
        f"{BASE_URL}/api/posts",
        json={"content": content, "topic": "rant", "device_id": _fresh_device()},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )


class TestUnsafeTerrorPhrasesBlocked:
    @pytest.mark.parametrize("phrase", UNSAFE_V7)
    def test_phrase_returns_400_with_friendly_terror_or_hate_detail(self, phrase):
        r = _post(phrase)
        assert r.status_code == 400, (
            f"Expected 400 for {phrase!r}, got {r.status_code}: {r.text}"
        )
        body = r.json()
        detail = body.get("detail", "")
        assert isinstance(detail, str) and detail, f"missing detail for {phrase!r}: {body}"
        assert detail.startswith("Your post was blocked for "), (
            f"detail must start with 'Your post was blocked for ' — got: {detail!r}"
        )
        assert any(p in detail for p in ALLOWED_FRIENDLY_PHRASES), (
            f"detail for {phrase!r} must mention terror promotion or hate/threats — got: {detail!r}"
        )


class TestSafeLookalikesAllowed:
    @pytest.mark.parametrize("phrase", SAFE_V7)
    def test_safe_phrase_returns_200_with_post(self, phrase):
        r = _post(phrase)
        assert r.status_code == 200, (
            f"Expected 200 for {phrase!r}, got {r.status_code}: {r.text}"
        )
        post = r.json()
        assert "id" in post and isinstance(post["id"], str)
        assert post.get("content") == phrase
        assert "_id" not in post
