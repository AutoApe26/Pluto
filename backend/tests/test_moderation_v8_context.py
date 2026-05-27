"""Iteration 8 — context-aware violent-intent detector test contract.

Tests POST /api/posts:
  - 26 block phrases must return HTTP 400 with friendly "Your post was blocked for ..."
  - 13 safe lookalikes must return HTTP 200.
"""
import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL not set", allow_module_level=True)

BLOCK_PHRASES = [
    "I will Bomb that place",
    "I'm gonna shoot her tomorrow",
    "we'll murder them all",
    "I have a bomb in my bag",
    "Ive got an explosive ready",
    "bringing a grenade to school",
    "imma blow up the office",
    "should kill all of them",
    "let's burn down that mosque",
    "need to bomb the airport",
    "I will rape her",
    "snap your neck tonight",
    "break his bones",
    "open fire on the crowd",
    "put a bullet in him",
    "shoot up the school",
    "carrying a loaded ak-47",
    "going to torch their place",
    "wipe out the village",
    "decapitate them all",
    "exterminate the immigrants",
    "I have explosives",
    "got a pipe bomb",
    "everyone deserves to be killed",
    "we should kill them",
    "fuck this im gonna blow up everything",
]

SAFE_PHRASES = [
    "that song is the bomb",
    "I bombed my exam",
    "explosive performance tonight",
    "gun show was great",
    "killing it at work today",
    "shoot for the stars",
    "AK-47 is the name of my new track",
    "this beat is killing",
    "they killed the dog",
    "killed the presentation",
    "shot the perfect basketball",
    "killing it at work",
    "i'm shooting hoops later",
]


def _post(text: str):
    device_id = f"TEST_{uuid.uuid4().hex[:12]}"
    return requests.post(
        f"{BASE_URL}/api/posts",
        json={"content": text, "topic": "rant", "device_id": device_id},
        timeout=15,
    )


@pytest.mark.parametrize("phrase", BLOCK_PHRASES)
def test_block_phrase(phrase):
    r = _post(phrase)
    assert r.status_code == 400, (
        f"Expected 400 for {phrase!r}, got {r.status_code}: {r.text[:200]}"
    )
    data = r.json()
    detail = data.get("detail", "") if isinstance(data, dict) else ""
    assert "blocked for" in detail.lower(), (
        f"Detail missing 'blocked for' phrasing: {detail!r}"
    )


@pytest.mark.parametrize("phrase", SAFE_PHRASES)
def test_safe_phrase(phrase):
    r = _post(phrase)
    assert r.status_code == 200, (
        f"Expected 200 for {phrase!r}, got {r.status_code}: {r.text[:200]}"
    )
