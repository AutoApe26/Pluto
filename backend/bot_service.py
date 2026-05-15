"""Pluto bot service — uses Reddit RSS feeds (Atom XML).

Why RSS? Reddit's JSON endpoints return 403 to non-OAuth bots, but
their public RSS feeds at /r/SUB/hot/.rss remain open.

Runs an async loop that auto-posts content from curated SFW
subreddits to matching Pluto topics every BOT_INTERVAL_SECONDS,
plus music drops from r/listentothis filtered to Spotify/YouTube.
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import logging
import os
import random
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from xml.etree import ElementTree as ET

import requests

logger = logging.getLogger("pluto.bots")

REDDIT_UA = "Mozilla/5.0 (compatible; PlutoBot/1.0; +https://pluto.app)"
BOT_INTERVAL = int(os.environ.get("BOT_INTERVAL_SECONDS", "120"))
BOTS_ENABLED = os.environ.get("BOTS_ENABLED", "true").lower() == "true"

ATOM_NS = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/"}

TOPIC_SOURCES = {
    "crypto": ["CryptoCurrency", "Bitcoin", "ethereum", "CryptoMarkets"],
    "sports": ["sports", "soccer", "nba", "nfl"],
    "memes": ["memes", "wholesomememes", "MemeEconomy"],
    "mental-health": ["mentalhealth", "Anxiety", "decidingtobebetter"],
    "rant": ["rant", "TrueOffMyChest", "offmychest"],
    "stories": ["humansbeingbros", "MadeMeSmile", "UpliftingNews"],
    "confession": ["confession", "confessions", "TrueOffMyChest"],
}
MUSIC_SOURCES = ["listentothis", "Music", "spotify", "indieheads"]

# Pool of believable human names. Picked at random for every drop so identities
# feel like real people and never repeat per topic.
FIRST_NAMES = [
    "Alex", "Sarah", "Marcus", "Priya", "Liam", "Noah", "Olivia", "Emma",
    "Aisha", "Diego", "Mateo", "Sofia", "Layla", "Jordan", "Kai", "Maya",
    "Ethan", "Ava", "Lucas", "Mia", "Isabella", "Logan", "Zoe", "Ezra",
    "Hannah", "Ben", "Ivy", "Owen", "Nora", "Ryan", "Maeve", "Eli",
    "Chloe", "Caleb", "Lily", "Aiden", "Aria", "Daniel", "Riley", "Noam",
    "Hassan", "Yara", "Felix", "Naomi", "Theo", "Lena", "Omar", "Anika",
    "Jack", "Ruby", "Henry", "Stella", "Leo", "Camila", "Adrian", "Nina",
    "Wyatt", "Iris", "Julian", "Quinn", "Asher", "Eva", "Miles", "Cora",
    "Hugo", "Elise", "Amir", "Tara", "Finn", "Sienna", "Rohan", "Hazel",
    "Ravi", "June", "Jonas", "Vera", "Arjun", "Keira", "Samir", "Maya",
    "Caleb", "Ines", "Tomás", "Ciara", "Yusuf", "Talia", "Idris", "Reema",
    "Dante", "Selena", "Rafael", "Ana", "Niko", "Mei", "Hiro", "Yui",
    "Daichi", "Saoirse", "Cian", "Ada", "Mira", "Toby",
]
LAST_NAMES = [
    "Carter", "Brooks", "Patel", "Rivera", "Chen", "Nguyen", "Kim", "Reyes",
    "Hassan", "Khan", "Cohen", "O'Brien", "Walsh", "Fernandez", "Torres",
    "Singh", "Murphy", "Larsen", "Becker", "Romano", "Costa", "Silva",
    "Mendez", "Park", "Lee", "Tanaka", "Suzuki", "Ahmed", "Rahman", "Iqbal",
    "Mitchell", "Hayes", "Bennett", "Sullivan", "Foster", "Hughes",
    "Russell", "Coleman", "Sanders", "Powell", "Long", "Ross", "Bailey",
    "Cole", "Gardner", "Stewart", "Brennan", "Dunn", "Vargas", "Castillo",
    "Holloway", "Whitman", "Sterling", "Marin", "Kapoor", "Sharma",
    "Iyer", "Bose", "Müller", "Schmidt", "Petrov", "Ivanov", "Novak",
    "Kowalski", "Andersen", "Lindqvist", "Okafor", "Adeyemi", "Mensah",
    "Diallo", "Traore", "Yamada", "Fujii", "Watanabe", "Cho", "Yoon",
    "Alvarez", "Ortiz", "Morales", "Rojas", "Beltran",
]


def _pick_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _seed_reactions() -> tuple[int, int]:
    """Return believable initial (hugs, fugs) so feeds feel lived-in."""
    hugs = random.randint(3, 84)
    fugs = random.randint(0, max(2, hugs // 12))
    return hugs, fugs


def _now_utc():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.isoformat()


def _hash_key(*parts: str) -> str:
    return hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()


def _strip_html_to_text(s: str) -> str:
    if not s:
        return ""
    # Drop "submitted by ..." footer added by Reddit
    s = re.sub(r"<table>.*?</table>", " ", s, flags=re.S)
    # Replace <br>, <p> with newlines
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p>", "\n\n", s, flags=re.I)
    # Drop all other tags
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s*\n\s*\n\s*", "\n\n", s)
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def _extract_image(html_str: str) -> Optional[str]:
    if not html_str:
        return None
    m = re.search(r'<img[^>]+src="([^"]+)"', html_str)
    if not m:
        return None
    url = html.unescape(m.group(1))
    if any(url.lower().split("?", 1)[0].endswith(ext)
           for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return url
    return None


def _extract_external_link(html_str: str) -> Optional[str]:
    """Return the FIRST external (non-reddit) URL found in HTML body."""
    if not html_str:
        return None
    for url in re.findall(r'href="([^"]+)"', html_str):
        u = html.unescape(url)
        ul = u.lower()
        if ul.startswith("http") and ("reddit.com" not in ul and "redd.it" not in ul):
            return u
    return None


def _detect_provider(url: str) -> Optional[str]:
    if not url:
        return None
    u = url.lower()
    if "spotify.com" in u or "spotify:" in u:
        return "spotify"
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    return None


def _fetch_rss_sync(sub: str, limit: int = 25) -> List[dict]:
    """Fetch RSS atom feed for a subreddit and parse into list of dicts."""
    try:
        url = f"https://www.reddit.com/r/{sub}/hot/.rss?limit={limit}"
        r = requests.get(
            url,
            headers={"User-Agent": REDDIT_UA, "Accept": "application/atom+xml"},
            timeout=12,
        )
        if r.status_code != 200:
            logger.warning("reddit RSS %s -> %s", sub, r.status_code)
            return []
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError as e:
            logger.warning("xml parse %s: %s", sub, e)
            return []
        out = []
        for entry in root.findall("a:entry", ATOM_NS):
            title_el = entry.find("a:title", ATOM_NS)
            content_el = entry.find("a:content", ATOM_NS)
            id_el = entry.find("a:id", ATOM_NS)
            link_el = entry.find("a:link", ATOM_NS)
            thumb_el = entry.find("m:thumbnail", ATOM_NS)
            out.append({
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "content_html": content_el.text or "" if content_el is not None else "",
                "id": (id_el.text or "") if id_el is not None else "",
                "comments_url": link_el.get("href") if link_el is not None else "",
                "thumbnail": thumb_el.get("url") if thumb_el is not None else None,
                "sub": sub,
            })
        return out
    except Exception as e:
        logger.warning("rss fetch failed %s: %s", sub, e)
        return []


async def fetch_subreddit(sub: str, limit: int = 25):
    return await asyncio.to_thread(_fetch_rss_sync, sub, limit)


# ---------------------------------------------------------------------------
# Billboard Hot 100 — global trending songs, refreshed weekly by Billboard.
# Scraping the public HTML page (no key required). On any failure we fall
# back to a stable seed list so the music bot never goes silent.
# ---------------------------------------------------------------------------
BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
BILLBOARD_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
)

# Fallback list of well-known trending tracks. Used only when Billboard scrape
# fails (network, layout change, rate-limit). Rotated through randomly.
_BILLBOARD_FALLBACK = [
    ("Espresso", "Sabrina Carpenter"),
    ("Birds of a Feather", "Billie Eilish"),
    ("Please Please Please", "Sabrina Carpenter"),
    ("Not Like Us", "Kendrick Lamar"),
    ("I Had Some Help", "Post Malone & Morgan Wallen"),
    ("Good Luck, Babe!", "Chappell Roan"),
    ("A Bar Song (Tipsy)", "Shaboozey"),
    ("Beautiful Things", "Benson Boone"),
    ("Pink Pony Club", "Chappell Roan"),
    ("Lunch", "Billie Eilish"),
    ("Too Sweet", "Hozier"),
    ("Fortnight", "Taylor Swift & Post Malone"),
    ("Stick Season", "Noah Kahan"),
    ("Cruel Summer", "Taylor Swift"),
    ("Texas Hold 'Em", "Beyoncé"),
    ("Houdini", "Eminem"),
    ("Million Dollar Baby", "Tommy Richman"),
    ("Lose Control", "Teddy Swims"),
    ("Get It Sexyy", "Sexyy Red"),
    ("End of Beginning", "Djo"),
    ("Saturn", "SZA"),
    ("Snooze", "SZA"),
    ("Greedy", "Tate McRae"),
    ("Paint The Town Red", "Doja Cat"),
    ("Agora Hills", "Doja Cat"),
    ("water", "Tyla"),
    ("Stargazing", "Myles Smith"),
    ("Wildflower", "Billie Eilish"),
    ("Yes, And?", "Ariana Grande"),
    ("we can't be friends", "Ariana Grande"),
    ("Lovin On Me", "Jack Harlow"),
    ("Bye Bye Bye", "*NSYNC"),
    ("Push Ups", "Drake"),
    ("Family Matters", "Drake"),
    ("Whatcha Doin'", "Doechii"),
    ("Like That", "Future, Metro Boomin, Kendrick Lamar"),
    ("BBL Drizzy", "Metro Boomin"),
    ("Si Antes Te Hubiera Conocido", "Karol G"),
    ("Mañana Será Bonito", "Karol G"),
    ("Pedro Pascal", "Pedro"),
    ("BAND4BAND", "Central Cee & Lil Baby"),
]


def _fetch_billboard_sync(limit: int = 50) -> List[Tuple[str, str]]:
    """Scrape Billboard Hot 100 with BeautifulSoup for stable extraction.

    Billboard layout (as of 2025): each chart row is an
    ``<li class="o-chart-results-list__item">``. The row containing the song
    has an ``<h3 id="title-of-a-story">SONG</h3>`` followed by a sibling
    ``<span>ARTIST</span>``. Other rows in the same parent ``<ul>`` contain
    chart metadata (peak position, weeks on chart) — those have no h3.
    """
    try:
        from bs4 import BeautifulSoup

        r = requests.get(
            BILLBOARD_URL,
            headers={"User-Agent": BILLBOARD_UA, "Accept": "text/html"},
            timeout=15,
        )
        if r.status_code != 200:
            logger.warning("billboard %s", r.status_code)
            return []
        soup = BeautifulSoup(r.text, "lxml")
        results: List[Tuple[str, str]] = []
        seen = set()
        # Each chart entry is grouped in a top-level <ul>. The first <li>
        # inside it carries the rank, the second <li> carries song+artist.
        for h3 in soup.select('h3#title-of-a-story'):
            title = h3.get_text(strip=True)
            if not title:
                continue
            # The artist <span> immediately follows the title h3 inside the
            # same parent <li>.
            parent = h3.find_parent("li")
            if not parent:
                continue
            artist_span = h3.find_next("span")
            if not artist_span:
                continue
            artist = artist_span.get_text(strip=True)
            if not artist or artist == title:
                continue
            # Reject obvious metadata: artist field shouldn't be a pure number,
            # shouldn't be "—", and title shouldn't equal known label text.
            if re.fullmatch(r"[\d\-—\s]+", artist):
                continue
            if title.lower() in {"hot 100", "billboard hot 100", "this week",
                                 "last week", "peak position", "weeks on chart",
                                 "wks on chart", "songwriter(s)", "imprint/promotion label",
                                 "producer(s)", "gains in weekly performance", "share"}:
                continue
            if len(title) > 120 or len(artist) > 160:
                continue
            key = (title.lower(), artist.lower())
            if key in seen:
                continue
            seen.add(key)
            results.append((title, artist))
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        logger.warning("billboard fetch failed: %s", e)
        return []


async def fetch_billboard_hot100(limit: int = 50) -> List[Tuple[str, str]]:
    scraped = await asyncio.to_thread(_fetch_billboard_sync, limit)
    if scraped:
        return scraped
    # Fallback so the music bot never starves
    pool = list(_BILLBOARD_FALLBACK)
    random.shuffle(pool)
    return pool[:limit]


# ---------------------------------------------------------------------------
# YouTube search — returns first watchable video URL for a query, scraped
# from the public search results page (no API key needed).
# ---------------------------------------------------------------------------
_YT_SEARCH = "https://www.youtube.com/results?search_query={}"
_YT_VIDEO_ID_RE = re.compile(r'"videoId":"([a-zA-Z0-9_-]{11})"')
_YT_THUMB = "https://i.ytimg.com/vi/{vid}/hqdefault.jpg"


def _yt_search_sync(query: str) -> Optional[Tuple[str, str]]:
    """Return (url, thumbnail) for the first video result, or None."""
    try:
        from urllib.parse import quote_plus

        q = quote_plus(f"{query} official audio")
        r = requests.get(
            _YT_SEARCH.format(q),
            headers={"User-Agent": BILLBOARD_UA, "Accept-Language": "en-US,en"},
            timeout=12,
        )
        if r.status_code != 200:
            return None
        m = _YT_VIDEO_ID_RE.search(r.text)
        if not m:
            return None
        vid = m.group(1)
        return (
            f"https://www.youtube.com/watch?v={vid}",
            _YT_THUMB.format(vid=vid),
        )
    except Exception as e:
        logger.warning("yt search failed for %r: %s", query, e)
        return None


async def yt_search_first(query: str) -> Optional[Tuple[str, str]]:
    return await asyncio.to_thread(_yt_search_sync, query)


def _clean(s: Optional[str], limit: int = 1000) -> str:
    if not s:
        return ""
    return s.replace("\u200b", "").strip()[:limit]


async def _post_topic(db, topic: str) -> bool:
    subs = list(TOPIC_SOURCES.get(topic, []))
    if not subs:
        return False
    random.shuffle(subs)
    skip_phrases = (
        "welcome to /r/",
        "this post contains content not supported",
        "submitted by /u/automoderator",
        "weekly thread",
        "monthly thread",
        "daily discussion",
        "megathread",
    )
    for sub in subs:
        items = await fetch_subreddit(sub, limit=25)
        random.shuffle(items)
        for it in items:
            title = _clean(it["title"], 240)
            if not title:
                continue
            tlow = title.lower()
            if any(p in tlow for p in skip_phrases):
                continue
            rid = it["id"] or title
            key = _hash_key("post", topic, rid)
            if await db.bot_posted.find_one({"key": key}):
                continue

            body = _strip_html_to_text(it["content_html"])
            body = re.sub(r"\s*\[link\]\s*\[comments\]\s*$", "", body)
            # Strip Reddit's "submitted by /u/..." footer (sometimes truncated)
            body = re.sub(r"\s*submitted by\s*/?u/[\w\-_]*.*$", "", body, flags=re.S)
            body_low = body.lower()
            if any(p in body_low for p in skip_phrases):
                continue
            body = body[:700].strip()
            content = title if not body else f"{title}\n\n{body}"
            content = content[:1000]

            image = _extract_image(it["content_html"])
            if not image and it["thumbnail"] and it["thumbnail"].startswith("http"):
                image = it["thumbnail"]

            now = _now_utc()
            hugs, fugs = _seed_reactions()
            post = {
                "id": str(uuid.uuid4()),
                "content": content,
                "topic": topic,
                "image": None,  # No images on Pluto — text-only posts
                "sudo_name": _pick_name(),
                "device_id": f"bot_{topic}",
                "hugs": hugs,
                "fugs": fugs,
                "created_at": _iso(now),
                "expires_at": _iso(now + timedelta(hours=24)),
                "report_count": 0,
                "hidden": False,
                "is_bot": True,
                "source": f"r/{sub}",
            }
            await db.posts.insert_one(post)
            await db.bot_posted.insert_one({
                "key": key, "kind": "post", "topic": topic,
                "sub": sub, "rid": rid, "ts": _iso(now),
            })
            logger.info("bot post -> #%s (r/%s) %s", topic, sub, title[:60])
            return True
        await asyncio.sleep(0.5)
    return False


def _track_fingerprint(title: str, artist: str) -> str:
    """Loose key so 'Espresso' / 'espresso (sped up)' / 'Espresso - Sabrina'
    all collapse to the same fingerprint and we don't repost the same song."""
    s = f"{title} {artist}".lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)        # remove parentheticals
    s = re.sub(r"\b(official|audio|video|lyrics|hd|4k|remix|sped up|slowed|version)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


async def _post_music(db) -> bool:
    """Pick a fresh Billboard Hot 100 track and post it as a YouTube embed.

    Heavy dedup: we skip any track whose normalized title+artist fingerprint
    has been posted in the last 7 days, so the music feed truly rotates.
    """
    week_ago = _iso(_now_utc() - timedelta(days=7))
    tracks = await fetch_billboard_hot100(limit=80)
    random.shuffle(tracks)
    for title, artist in tracks:
        fp = _track_fingerprint(title, artist)
        if not fp:
            continue
        # Skip if we've already posted this song (any variant) recently
        if await db.bot_posted.find_one({"kind": "music_fp", "fp": fp, "ts": {"$gte": week_ago}}):
            continue
        if await db.music_posts.find_one({"track_fp": fp, "created_at": {"$gte": week_ago}}):
            continue

        # Find a playable YouTube URL for this track
        result = await yt_search_first(f"{artist} {title}")
        if not result:
            continue
        url, thumbnail = result
        # Belt-and-braces: skip if we somehow already have this exact URL
        if await db.music_posts.find_one({"link_url": url}):
            continue

        now = _now_utc()
        hugs, fugs = _seed_reactions()
        track = {
            "id": str(uuid.uuid4()),
            "link_url": url,
            "provider": "youtube",
            "title": title[:200],
            "artist": artist[:120],
            "thumbnail": thumbnail,
            "caption": "",
            "is_lyrics": False,
            "sudo_name": _pick_name(),
            "tags": [],
            "device_id": "bot_music",
            "hugs": hugs,
            "fugs": fugs,
            "created_at": _iso(now),
            "expires_at": _iso(now + timedelta(hours=24)),
            "report_count": 0,
            "hidden": False,
            "is_bot": True,
            "source": "billboard-hot-100",
            "track_fp": fp,
        }
        await db.music_posts.insert_one(track)
        await db.bot_posted.insert_one({
            "key": _hash_key("music_fp", fp),
            "kind": "music_fp",
            "fp": fp,
            "ts": _iso(now),
        })
        logger.info("bot music drop -> %s — %s", artist, title)
        return True
    logger.info("music bot: no fresh track found this cycle")
    return False


async def run_once(db) -> dict:
    stats = {"posted": [], "skipped": [], "music": False}
    topics = list(TOPIC_SOURCES.keys())
    random.shuffle(topics)
    for topic in topics:
        try:
            ok = await _post_topic(db, topic)
            (stats["posted"] if ok else stats["skipped"]).append(topic)
        except Exception as e:
            logger.warning("topic %s failed: %s", topic, e)
            stats["skipped"].append(topic)
        await asyncio.sleep(0.7)
    try:
        stats["music"] = await _post_music(db)
    except Exception as e:
        logger.warning("music bot failed: %s", e)
    return stats


async def bot_loop(db):
    if not BOTS_ENABLED:
        logger.info("bots disabled via BOTS_ENABLED=false")
        return
    logger.info(
        "Pluto bots online · interval=%ss · topics=%d", BOT_INTERVAL, len(TOPIC_SOURCES)
    )
    try:
        await db.bot_posted.create_index("key", unique=True)
        await db.bot_posted.create_index("ts")
    except Exception:
        pass
    await asyncio.sleep(8)
    while True:
        try:
            stats = await run_once(db)
            logger.info(
                "bot cycle done · posted=%s skipped=%s music=%s",
                stats["posted"], stats["skipped"], stats["music"],
            )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("bot cycle crashed: %s", e)
        await asyncio.sleep(BOT_INTERVAL)


# ---------------------------------------------------------------------------
# Engagement loop — periodically adds hugs/fugs to RANDOM recent posts
# (manual + bot) so the whole feed feels alive. Without this, manually-posted
# content stays at 0 forever, which is obvious and demotivating.
# ---------------------------------------------------------------------------
ENGAGEMENT_INTERVAL = int(os.environ.get("PLUTO_ENGAGEMENT_INTERVAL", "25"))  # seconds
HUG_CAP = 200
FUG_CAP = 30
# Probability bias — natural feeds have ~6× more positive than negative reactions
HUG_PROB = 0.86


async def _bump_collection(db, coll, post_field_id: str = "id"):
    """Pick a few random recent items and add +1 hug or +1 fug to each."""
    week_ago = _iso(_now_utc() - timedelta(days=2))  # active window
    pipeline = [
        {"$match": {
            "created_at": {"$gte": week_ago},
            "hidden": {"$ne": True},
        }},
        {"$sample": {"size": random.randint(2, 6)}},
        {"$project": {"_id": 0, post_field_id: 1, "hugs": 1, "fugs": 1,
                       "is_bot": 1, "device_id": 1}},
    ]
    try:
        async for doc in coll.aggregate(pipeline):
            pid = doc.get(post_field_id)
            if not pid:
                continue
            cur_h = doc.get("hugs") or 0
            cur_f = doc.get("fugs") or 0
            # Bias toward hugs; very small chance of a fug
            give_hug = random.random() < HUG_PROB
            if give_hug and cur_h >= HUG_CAP:
                continue
            if (not give_hug) and cur_f >= FUG_CAP:
                continue
            field = "hugs" if give_hug else "fugs"
            await coll.update_one({post_field_id: pid}, {"$inc": {field: 1}})
    except Exception as e:
        logger.warning("engagement bump failed: %s", e)


async def engagement_loop(db):
    """Background coroutine: keeps adding small bursts of hugs/fugs to every
    recent post so manual posts also get organic engagement."""
    if not BOTS_ENABLED:
        return
    logger.info("Pluto engagement loop online · interval=%ss", ENGAGEMENT_INTERVAL)
    await asyncio.sleep(12)
    while True:
        try:
            await _bump_collection(db, db.posts)
            await _bump_collection(db, db.music_posts)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("engagement loop crashed: %s", e)
        # Small jitter so bumps feel irregular like real users
        await asyncio.sleep(ENGAGEMENT_INTERVAL + random.randint(-8, 12))
