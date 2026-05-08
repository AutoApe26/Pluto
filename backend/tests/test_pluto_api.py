"""Pluto backend API tests — covers topics, posts, music, reactions, reports, moderation."""
import os
import uuid
import time
import pytest
import requests
from datetime import datetime, timezone

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://ephemeral-vibes.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
MOD_KEY = "pluto-mod-2026"
TINY_AUDIO = "data:audio/mpeg;base64,SUQzBAAAAAAA"


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


def new_device():
    return f"TEST_{uuid.uuid4().hex[:12]}"


# ---------------- Topics ----------------
class TestTopics:
    def test_list_topics_returns_8(self, s):
        r = s.get(f"{API}/topics")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 8
        slugs = {t["slug"] for t in data}
        expected = {"crypto", "sports", "memes", "mental-health", "tell-anything", "stories", "confession", "music"}
        assert slugs == expected
        for t in data:
            assert {"slug", "name", "icon", "color"} <= t.keys()


# ---------------- Posts ----------------
class TestPosts:
    def test_create_post_success(self, s):
        device = new_device()
        payload = {"content": "TEST_post hello world", "topic": "crypto", "device_id": device}
        r = s.post(f"{API}/posts", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data and isinstance(data["id"], str)
        assert data["content"] == "TEST_post hello world"
        assert data["topic"] == "crypto"
        assert data["device_id"] == device
        assert "created_at" in data and "expires_at" in data
        # expires_at = created_at + 24h
        c = datetime.fromisoformat(data["created_at"])
        e = datetime.fromisoformat(data["expires_at"])
        delta = (e - c).total_seconds()
        assert 23.99 * 3600 <= delta <= 24.01 * 3600
        # _id excluded
        assert "_id" not in data

    def test_create_post_invalid_topic(self, s):
        r = s.post(f"{API}/posts", json={"content": "bad", "topic": "not-a-topic", "device_id": new_device()})
        assert r.status_code == 400

    def test_list_posts_filter(self, s):
        device = new_device()
        # create one in memes
        s.post(f"{API}/posts", json={"content": "TEST_meme post", "topic": "memes", "device_id": device})
        # all posts
        r = s.get(f"{API}/posts")
        assert r.status_code == 200
        all_posts = r.json()
        assert isinstance(all_posts, list)
        for p in all_posts:
            assert "_id" not in p
        # filter
        r2 = s.get(f"{API}/posts", params={"topic": "memes"})
        assert r2.status_code == 200
        memes = r2.json()
        for p in memes:
            assert p["topic"] == "memes"

    def test_trending_posts(self, s):
        # ensure at least one
        s.post(f"{API}/posts", json={"content": "TEST_trend", "topic": "stories", "device_id": new_device()})
        r = s.get(f"{API}/posts/trending")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for p in data:
            assert p["hidden"] is False
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


# ---------------- Music ----------------
@pytest.fixture(scope="class")
def music_track(s_session):
    device = new_device()
    payload = {
        "artist": "TEST_Artist",
        "title": "TEST_Track",
        "caption": "test cap",
        "audio": TINY_AUDIO,
        "tags": ["chill", "test"],
        "device_id": device,
    }
    r = s_session.post(f"{API}/music", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    return {"id": data["id"], "device_id": device, "data": data}


@pytest.fixture(scope="session")
def s_session():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


class TestMusic:
    def test_upload_music_invalid_audio(self, s):
        r = s.post(f"{API}/music", json={
            "artist": "x", "title": "y", "audio": "not-a-data-url", "device_id": new_device()
        })
        assert r.status_code == 400

    def test_upload_music_success(self, s, music_track):
        d = music_track["data"]
        assert d["artist"] == "TEST_Artist"
        assert d["title"] == "TEST_Track"
        assert d["hugs"] == 0 and d["fugs"] == 0
        assert d["audio"].startswith("data:audio")
        assert "_id" not in d

    def test_list_music(self, s, music_track):
        r = s.get(f"{API}/music")
        assert r.status_code == 200
        data = r.json()
        assert any(m["id"] == music_track["id"] for m in data)
        for m in data:
            assert "_id" not in m

    def test_featured_music(self, s):
        r = s.get(f"{API}/music/featured")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # sorted by hugs desc
        if len(data) > 1:
            for i in range(len(data) - 1):
                assert data[i]["hugs"] >= data[i + 1]["hugs"]

    def test_reaction_hug_then_toggle_then_switch(self, s, music_track):
        mid = music_track["id"]
        device = new_device()
        # hug
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": device, "type": "hug"})
        assert r.status_code == 200
        assert r.json()["action"] == "added"
        # my-reaction
        r = s.get(f"{API}/music/{mid}/my-reaction", params={"device_id": device})
        assert r.json()["type"] == "hug"
        # toggle off
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": device, "type": "hug"})
        assert r.json()["action"] == "removed"
        r = s.get(f"{API}/music/{mid}/my-reaction", params={"device_id": device})
        assert r.json()["type"] is None
        # add hug again
        s.post(f"{API}/music/{mid}/reaction", json={"device_id": device, "type": "hug"})
        # switch to fug
        r = s.post(f"{API}/music/{mid}/reaction", json={"device_id": device, "type": "fug"})
        assert r.json()["action"] == "switched"
        assert r.json()["type"] == "fug"

    def test_reaction_counts_update(self, s):
        # fresh track
        device_owner = new_device()
        r = s.post(f"{API}/music", json={
            "artist": "TEST_A2", "title": "TEST_T2", "audio": TINY_AUDIO, "device_id": device_owner
        })
        mid = r.json()["id"]
        d1, d2 = new_device(), new_device()
        s.post(f"{API}/music/{mid}/reaction", json={"device_id": d1, "type": "hug"})
        s.post(f"{API}/music/{mid}/reaction", json={"device_id": d2, "type": "hug"})
        # fetch
        tracks = s.get(f"{API}/music").json()
        track = next(t for t in tracks if t["id"] == mid)
        assert track["hugs"] == 2
        # switch d2 to fug
        s.post(f"{API}/music/{mid}/reaction", json={"device_id": d2, "type": "fug"})
        tracks = s.get(f"{API}/music").json()
        track = next(t for t in tracks if t["id"] == mid)
        assert track["hugs"] == 1
        assert track["fugs"] == 1


# ---------------- Reports ----------------
class TestReports:
    def test_report_post_dedup_and_hide(self, s):
        device_owner = new_device()
        r = s.post(f"{API}/posts", json={"content": "TEST_report me", "topic": "memes", "device_id": device_owner})
        assert r.status_code == 200
        pid = r.json()["id"]
        # 1st report
        d1 = new_device()
        r1 = s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": d1})
        assert r1.status_code == 200
        assert r1.json().get("ok") is True
        assert not r1.json().get("already")
        # duplicate
        r1b = s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": d1})
        assert r1b.json().get("already") is True
        # 2 more distinct reports → 3 total → hidden
        s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        # post should now be hidden — not in list
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
        r = s.get(f"{API}/mod/reported", headers={"X-Mod-Key": "wrong"})
        assert r.status_code == 401

    def test_mod_reported_authorized(self, s):
        r = s.get(f"{API}/mod/reported", headers={"X-Mod-Key": MOD_KEY})
        assert r.status_code == 200
        data = r.json()
        assert "posts" in data and "music" in data
        assert isinstance(data["posts"], list)
        assert isinstance(data["music"], list)

    def test_mod_safe_then_delete(self, s):
        # create post and report 3x to hide it
        owner = new_device()
        r = s.post(f"{API}/posts", json={"content": "TEST_modflow", "topic": "stories", "device_id": owner})
        pid = r.json()["id"]
        for _ in range(3):
            s.post(f"{API}/reports", json={"target_type": "post", "target_id": pid, "device_id": new_device()})
        # mark safe
        rs = s.post(f"{API}/mod/post/{pid}/safe", headers={"X-Mod-Key": MOD_KEY})
        assert rs.status_code == 200
        # should be visible again
        listed = s.get(f"{API}/posts").json()
        assert any(p["id"] == pid for p in listed)
        # now delete
        rd = s.post(f"{API}/mod/post/{pid}/delete", headers={"X-Mod-Key": MOD_KEY})
        assert rd.status_code == 200
        assert rd.json().get("deleted") == 1
        # gone
        listed = s.get(f"{API}/posts").json()
        assert not any(p["id"] == pid for p in listed)

    def test_mod_delete_music(self, s):
        owner = new_device()
        r = s.post(f"{API}/music", json={
            "artist": "TEST_modart", "title": "TEST_modtitle", "audio": TINY_AUDIO, "device_id": owner
        })
        mid = r.json()["id"]
        rd = s.post(f"{API}/mod/music/{mid}/delete", headers={"X-Mod-Key": MOD_KEY})
        assert rd.status_code == 200
        listed = s.get(f"{API}/music").json()
        assert not any(m["id"] == mid for m in listed)
