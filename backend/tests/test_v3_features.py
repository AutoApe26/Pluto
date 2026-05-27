"""Pluto V3 feature tests: topic count, music chatter bot posts, trending order."""
import os
import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


class TestTopicsOrderAndCount:
    def test_topics_returns_8(self, s):
        r = s.get(f"{API}/topics")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8
        slugs = {t["slug"] for t in data}
        assert {"crypto", "music", "mental-health", "confession",
                "sports", "memes", "rant", "stories"} == slugs


class TestMusicChatterBot:
    def test_music_chatter_posts_exist(self, s):
        r = s.get(f"{API}/posts", params={"topic": "music"})
        assert r.status_code == 200
        posts = r.json()
        chatter = [p for p in posts if p.get("device_id") == "bot_music_chatter"]
        assert len(chatter) >= 1, "expected at least one music chatter bot post"
        for p in chatter:
            assert p["topic"] == "music"
            assert (p.get("source") or "").startswith("music-chatter:")
            # Seeded hugs should be non-zero
            assert p["hugs"] > 0

    def test_trending_may_include_music_chatter(self, s):
        r = s.get(f"{API}/posts/trending")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        for p in items:
            assert "_id" not in p


class TestMusicEndpointsRegression:
    def test_music_list(self, s):
        r = s.get(f"{API}/music")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_music_featured(self, s):
        r = s.get(f"{API}/music/featured")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 4
