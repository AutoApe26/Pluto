"""Pluto backend API tests (V2 redesign) — link-based music, sudo_name, rant topic, 1000 char limit."""
import os
import uuid
import pytest
import requests
from datetime import datetime

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
MOD_KEY = "pluto-mod-2026"
YT_URL = "https://youtu.be/dQw4w9WgXcQ"
SPOTIFY_URL = "https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8"


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


def new_device():
    return f"TEST_{uuid.uuid4().hex[:12]}"


# ---------------- Topics ----------------
class TestTopics:
    def test_list_topics_returns_8_with_rant(self, s):
        r = s.get(f"{API}/topics")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 8
        slugs = {t["slug"] for t in data}
        expected = {"crypto", "sports", "memes", "mental-health", "rant", "stories", "confession", "music"}
        assert slugs == expected
        assert "tell-anything" not in slugs
        for t in data:
            assert {"slug", "name", "icon", "color"} <= t.keys()


# ---------------- Posts ----------------
class TestPosts:
    def test_create_post_with_sudo_name(self, s):
        device = new_device()
        payload = {
            "content": "TEST_post hello world",
            "topic": "rant",
            "sudo_name": "ghost42",
            "device_id": device,
        }
        r = s.post(f"{API}/posts", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["content"] == "TEST_post hello world"
        assert data["topic"] == "rant"
        assert data["sudo_name"] == "ghost42"
        assert data["device_id"] == device
        assert "_id" not in data
        # 24h expiry
        c = datetime.fromisoformat(data["created_at"])
        e = datetime.fromisoformat(data["expires_at"])
        delta = (e - c).total_seconds()
        assert 23.99 * 3600 <= delta <= 24.01 * 3600

    def test_create_post_without_sudo_name(self, s):
        device = new_device()
        r = s.post(f"{API}/posts", json={"content": "TEST_no sudo", "topic": "crypto", "device_id": device})
        assert r.status_code == 200
        d = r.json()
        assert d["sudo_name"] is None

    def test_create_post_invalid_topic(self, s):
        r = s.post(f"{API}/posts", json={"content": "bad", "topic": "tell-anything", "device_id": new_device()})
        assert r.status_code == 400

    def test_post_max_1000_chars_accepted(self, s):
        device = new_device()
        content = "a" * 1000
        r = s.post(f"{API}/posts", json={"content": content, "topic": "memes", "device_id": device})
        assert r.status_code == 200
        assert len(r.json()["content"]) == 1000

    def test_post_over_1000_chars_rejected(self, s):
        device = new_device()
        content = "a" * 1001
        r = s.post(f"{API}/posts", json={"content": content, "topic": "memes", "device_id": device})
        assert r.status_code == 422

    def test_list_posts_filter_rant(self, s):
        device = new_device()
        s.post(f"{API}/posts", json={"content": "TEST_rant post", "topic": "rant", "device_id": device})
        r = s.get(f"{API}/posts", params={"topic": "rant"})
        assert r.status_code == 200
        for p in r.json():
            assert p["topic"] == "rant"
            assert "_id" not in p

    def test_spam_protection_429(self, s):
        device = new_device()
        last_status = None
        for i in range(11):
            r = s.post(f"{API}/posts", json={"content": f"TEST_spam {i}", "topic": "crypto", "device_id": device})
            last_status = r.status_code
            if r.status_code == 429:
                break
        assert last_status == 429


# ---------------- Music (V2 link-based) ----------------
class TestMusic:
    def test_upload_music_invalid_url_rejected(self, s):
        r = s.post(f"{API}/music", json={
            "link_url": "https://soundcloud.com/foo/bar",
            "device_id": new_device(),
        })
        assert r.status_code == 400

    def test_upload_youtube(self, s):
        device = new_device()
        payload = {
            "link_url": YT_URL,
            "title": "TEST_YT Title",
            "artist": "TEST_Rick",
            "caption": "classic",
            "is_lyrics": False,
            "sudo_name": "ytfan",
            "tags": ["#chill", "test"],
            "device_id": device,
        }
        r = s.post(f"{API}/music", json=payload)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["provider"] == "youtube"
        assert d["link_url"] == YT_URL
        assert d["title"] == "TEST_YT Title"
        assert d["sudo_name"] == "ytfan"
        assert d["is_lyrics"] is False
        assert "chill" in d["tags"]  # # stripped
        assert d["hugs"] == 0 and d["fugs"] == 0
        assert "expires_at" in d
        assert "_id" not in d

    def test_upload_spotify(self, s):
        r = s.post(f"{API}/music", json={
            "link_url": SPOTIFY_URL,
            "title": "TEST_Spot",
            "is_lyrics": True,
            "device_id": new_device(),
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["provider"] == "spotify"
        assert d["is_lyrics"] is True

    def test_list_music_only_with_link_url(self, s):
        # Seed one
        s.post(f"{API}/music", json={"link_url": YT_URL, "title": "TEST_listing", "device_id": new_device()})
        r = s.get(f"{API}/music")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for m in data:
            assert "link_url" in m and m["link_url"]
            assert "expires_at" in m
            assert "_id" not in m

    def test_featured_music_sort(self, s):
        r = s.get(f"{API}/music/featured")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 4
        if len(data) > 1:
            for i in range(len(data) - 1):
                assert data[i]["hugs"] >= data[i + 1]["hugs"]

    def test_reaction_hug_fug_toggle_switch(self, s):
        device_owner = new_device()
        r = s.post(f"{API}/music", json={"link_url": YT_URL, "title": "TEST_reaction", "device_id": device_owner})
        mid = r.json()["id"]
        d1 = new_device()
        # add hug
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": d1, "type": "hug"})
        assert r.json()["action"] == "added"
        # toggle off
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": d1, "type": "hug"})
        assert r.json()["action"] == "removed"
        # add then switch
        s.post(f"{API}/music/{mid}/reaction", json={"device_id": d1, "type": "hug"})
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": d1, "type": "fug"})
        assert r.json()["action"] == "switched"
        # confirm counts
        tracks = s.get(f"{API}/music").json()
        track = next(t for t in tracks if t["id"] == mid)
        assert track["fugs"] == 1
        assert track["hugs"] == 0

    def test_music_spam_429(self, s):
        device = new_device()
        last = None
        for i in range(6):
            r = s.post(f"{API}/music", json={"link_url": YT_URL, "title": f"TEST_spam{i}", "device_id": device})
            last = r.status_code
            if r.status_code == 429:
                break
        assert last == 429


# ---------------- Reports ----------------
class TestReports:
    def test_report_post_dedup_and_hide(self, s):
        owner = new_device()
        r = s.post(f"{API}/posts", json={"content": "TEST_report me", "topic": "memes", "device_id": owner})
        pid = r.json()["id"]
        d1 = new_device()
        r1 = s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": d1})
        assert r1.status_code == 200
        # dup
        r1b = s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": d1})
        assert r1b.json().get("already") is True
        # 2 more
        s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        listed = s.get(f"{API}/posts", params={"topic": "memes"}).json()
        assert not any(p["id"] == pid for p in listed)

    def test_report_invalid_target(self, s):
        r = s.post(f"{API}/reports", json={"target_type": "post", "target_id": "nonexistent", "device_id": new_device()})
        assert r.status_code == 404


# ---------------- Moderation ----------------
class TestModeration:
    def test_mod_unauthorized(self, s):
        r = s.get(f"{API}/mod/reported")
        assert r.status_code == 401
        r2 = s.get(f"{API}/mod/reported", headers={"X-Mod-Key": "wrong"})
        assert r2.status_code == 401

    def test_mod_reported_authorized(self, s):
        r = s.get(f"{API}/mod/reported", headers={"X-Mod-Key": MOD_KEY})
        assert r.status_code == 200
        d = r.json()
        assert isinstance(d.get("posts"), list)
        assert isinstance(d.get("music"), list)

    def test_mod_safe_then_delete_post(self, s):
        owner = new_device()
        r = s.post(f"{API}/posts", json={"content": "TEST_modflow", "topic": "stories", "device_id": owner})
        pid = r.json()["id"]
        for _ in range(3):
            s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        rs = s.post(f"{API}/mod/post/{pid}/safe", headers={"X-Mod-Key": MOD_KEY})
        assert rs.status_code == 200
        listed = s.get(f"{API}/posts").json()
        assert any(p["id"] == pid for p in listed)
        rd = s.post(f"{API}/mod/post/{pid}/delete", headers={"X-Mod-Key": MOD_KEY})
        assert rd.status_code == 200
        assert rd.json().get("deleted") == 1

    def test_mod_delete_music(self, s):
        owner = new_device()
        r = s.post(f"{API}/music", json={"link_url": SPOTIFY_URL, "title": "TEST_modmusic", "device_id": owner})
        mid = r.json()["id"]
        rd = s.post(f"{API}/mod/music/{mid}/delete", headers={"X-Mod-Key": MOD_KEY})
        assert rd.status_code == 200
        listed = s.get(f"{API}/music").json()
        assert not any(m["id"] == mid for m in listed)
