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

# Pool of organic-sounding anonymous handles. Picked at random for every drop
# so identities feel human and never repeat per topic.
RANDOM_NAMES = [
    "voidkitten", "lonelyfox", "midnight42", "ghostnova", "lostmoth",
    "neonpetal", "palewren", "hollowdream", "softecho", "craterwolf",
    "dawnglitch", "indigo_owl", "mossy_orbit", "lavaskies", "bluerot",
    "stargrime", "atlasdust", "faded.fern", "embertide", "glasshare",
    "lunarmoth", "cobaltdrift", "satin_fade", "hush.kid", "plumdust",
    "velvetwave", "nimbus07", "blursparrow", "slatehush", "paperowl",
    "candledrift", "ochre.echo", "marblekoi", "dusk_otter", "frostlilac",
    "willow_gh", "palmrust", "glowleaf", "wax_drift", "junebug88",
    "cottoncomet", "peridot.wave", "oxbloodfern", "cobwebkoi", "gloamfawn",
    "maybeghost", "suedebloom", "brassnebula", "smolderfox", "salt.bird",
    "plumtide", "indigo.dust", "palmoth", "glowdrift", "lichendrift",
    "twilightfern", "slatebloom", "moonwax", "briarsalt", "foggyowl",
    "candlerot", "lichenpetal", "dustyhalo", "ironcloud", "brassdrift",
    "vesper42", "etherfern", "paperhush", "stormvelvet", "dustprism",
    "mauvedrift", "peachwax", "suedeghost", "atlasecho", "lavendervoid",
    "nightonyx", "weeping.fern", "gauzy.tide", "cinder.bloom", "fogdust",
    "palebriar", "ashrose", "lacquerdrift", "paperraven", "morrowfox",
    "thistlecat", "copperdream", "glassthrush", "whisperjade", "softrust",
    "blueberry.os", "tinyhalo", "mintforge", "coral.99", "sodadream",
]


def _pick_name() -> str:
    return random.choice(RANDOM_NAMES)


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
            post = {
                "id": str(uuid.uuid4()),
                "content": content,
                "topic": topic,
                "image": image,
                "sudo_name": _pick_name(),
                "device_id": f"bot_{topic}",
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


async def _post_music(db) -> bool:
    subs = list(MUSIC_SOURCES)
    random.shuffle(subs)
    for sub in subs:
        items = await fetch_subreddit(sub, limit=30)
        random.shuffle(items)
        for it in items:
            url = _extract_external_link(it["content_html"]) or ""
            provider = _detect_provider(url)
            if not provider:
                continue
            rid = it["id"] or url
            key = _hash_key("music", rid)
            if await db.bot_posted.find_one({"key": key}):
                continue
            if await db.music_posts.find_one({"link_url": url}):
                continue

            raw_title = _clean(it["title"], 240)
            title, artist = raw_title, ""
            if " - " in raw_title:
                left, right = raw_title.split(" - ", 1)
                artist = left.strip()
                right_clean = re.sub(r"\s*[\[\(].*$", "", right).strip()
                if right_clean:
                    title = right_clean

            thumbnail = (
                _extract_image(it["content_html"])
                or (it["thumbnail"] if (it["thumbnail"] or "").startswith("http") else None)
            )

            now = _now_utc()
            track = {
                "id": str(uuid.uuid4()),
                "link_url": url,
                "provider": provider,
                "title": title[:200],
                "artist": artist[:120],
                "thumbnail": thumbnail,
                "caption": "",
                "is_lyrics": False,
                "sudo_name": _pick_name(),
                "tags": [],
                "device_id": "bot_music",
                "hugs": 0,
                "fugs": 0,
                "created_at": _iso(now),
                "expires_at": _iso(now + timedelta(hours=24)),
                "report_count": 0,
                "hidden": False,
                "is_bot": True,
                "source": f"r/{sub}",
            }
            await db.music_posts.insert_one(track)
            await db.bot_posted.insert_one({
                "key": key, "kind": "music",
                "sub": sub, "rid": rid, "ts": _iso(now),
            })
            logger.info("bot music drop -> %s · %s", provider, raw_title[:80])
            return True
        await asyncio.sleep(0.5)
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
