from fastapi import FastAPI, APIRouter, HTTPException, Header, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid
import asyncio
from datetime import datetime, timezone, timedelta

from bot_service import bot_loop, run_once, engagement_loop
from moderation import violation_for, normalized_for_dedup
from image_moderation import moderate_image_data_url, category_label

# Language detection — used to flag posts so frontend can offer translation.
try:
    from langdetect import detect as _lang_detect, DetectorFactory
    DetectorFactory.seed = 0  # deterministic
except Exception:  # pragma: no cover
    _lang_detect = None

# Emergent LLM (Gemini) — for on-demand post translation.
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except Exception:  # pragma: no cover
    LlmChat = None
    UserMessage = None


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

MOD_KEY = os.environ.get('MOD_KEY', 'pluto-mod-2026')
REPORT_HIDE_THRESHOLD = 3
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')


def _detect_lang(text: str) -> str:
    """Best-effort language code (ISO 639-1) for a post body. Falls back
    to 'en' on any failure. Very short text (< 8 chars) is assumed English
    since detectors are unreliable on tiny strings."""
    if not text or len(text.strip()) < 8 or _lang_detect is None:
        return "en"
    # If the body is dominated by ASCII letters and looks like English-ish
    # script, langdetect can still confidently misclassify slang. Keep the
    # raw guess and let the frontend decide whether to surface the
    # "see translation" affordance.
    try:
        code = _lang_detect(text)
        return (code or "en").split("-", 1)[0].lower()
    except Exception:
        return "en"

app = FastAPI(title="Pluto API")
api_router = APIRouter(prefix="/api")

# ============================================================
# TOPICS (seeded on startup)
# ============================================================
TOPICS_SEED = [
    {"slug": "crypto", "name": "Crypto", "icon": "Bitcoin", "color": "#F7931A"},
    {"slug": "sports", "name": "Sports", "icon": "Trophy", "color": "#34C759"},
    {"slug": "memes", "name": "Memes", "icon": "Laugh", "color": "#FFCC00"},
    {"slug": "mental-health", "name": "Mental Health", "icon": "HeartPulse", "color": "#FF6B9D"},
    {"slug": "rant", "name": "Rant", "icon": "Zap", "color": "#00F0FF"},
    {"slug": "stories", "name": "Stories", "icon": "BookOpen", "color": "#B026FF"},
    {"slug": "confession", "name": "Confession", "icon": "Eye", "color": "#FF3B30"},
    {"slug": "music", "name": "Music", "icon": "Music", "color": "#7B61FF"},
]

# ============================================================
# Models
# ============================================================
def now_utc():
    return datetime.now(timezone.utc)

def iso(dt: datetime) -> str:
    return dt.isoformat()

class Topic(BaseModel):
    slug: str
    name: str
    icon: str
    color: str

class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    topic: str
    image: Optional[str] = None  # base64 data url
    sudo_name: Optional[str] = None
    device_id: str

class Post(BaseModel):
    id: str
    content: str
    topic: str
    image: Optional[str] = None
    sudo_name: Optional[str] = None
    device_id: str
    hugs: int = 0
    fugs: int = 0
    created_at: str
    expires_at: str
    report_count: int = 0
    hidden: bool = False
    is_bot: bool = False
    lang: str = "en"

class MusicCreate(BaseModel):
    link_url: str = Field(min_length=8, max_length=600)
    provider: Optional[str] = None  # spotify | youtube
    title: Optional[str] = None
    artist: Optional[str] = None
    thumbnail: Optional[str] = None
    caption: Optional[str] = ""
    is_lyrics: bool = False
    sudo_name: Optional[str] = None
    tags: List[str] = []
    device_id: str

class MusicPost(BaseModel):
    id: str
    link_url: str
    provider: str = "youtube"
    title: str = ""
    artist: str = ""
    thumbnail: Optional[str] = None
    caption: str = ""
    is_lyrics: bool = False
    sudo_name: Optional[str] = None
    tags: List[str] = []
    device_id: str
    hugs: int = 0
    fugs: int = 0
    created_at: str
    expires_at: str
    report_count: int = 0
    hidden: bool = False
    is_bot: bool = False

class ReactionCreate(BaseModel):
    device_id: str
    type: Literal["hug", "fug"]

class ReportCreate(BaseModel):
    target_type: Literal["post", "music"]
    target_id: str
    device_id: str
    reason: Optional[str] = ""

# ============================================================
# Helpers
# ============================================================
async def cleanup_expired():
    """Delete posts past expires_at (24h auto-delete)."""
    now_iso = iso(now_utc())
    await db.posts.delete_many({"expires_at": {"$lt": now_iso}})

def strip_id(doc):
    if doc and "_id" in doc:
        doc.pop("_id", None)
    return doc

# ============================================================
# Topics
# ============================================================
@api_router.get("/topics")
async def list_topics():
    return TOPICS_SEED

# ============================================================
# Posts
# ============================================================
@api_router.get("/posts")
async def list_posts(
    topic: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    await cleanup_expired()
    q = {"hidden": False}
    if topic and topic != "all":
        q["topic"] = topic
    cursor = db.posts.find(q, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

@api_router.get("/posts/trending")
async def trending_posts(limit: int = 5):
    await cleanup_expired()
    cursor = db.posts.find({"hidden": False}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)

@api_router.post("/posts", response_model=Post)
async def create_post(payload: PostCreate):
    valid_slugs = {t["slug"] for t in TOPICS_SEED}
    if payload.topic not in valid_slugs:
        raise HTTPException(400, "Invalid topic")

    content = payload.content.strip()

    # Rule: text content must pass moderation (no links, blocked categories)
    reason = violation_for(content)
    if reason:
        raise HTTPException(400, reason)

    # Rule: image (if attached) must pass Gemini Vision moderation
    image_to_store: Optional[str] = None
    if payload.image:
        verdict = await moderate_image_data_url(payload.image)
        if not verdict.safe:
            label = category_label(verdict.category)
            extra = f" — {verdict.reason}" if verdict.reason else ""
            raise HTTPException(400, f"Image blocked: {label}.{extra}")
        image_to_store = payload.image

    # Rule: same content max 5x / 24h (per device) + global anti-spam cap
    one_day_ago = iso(now_utc() - timedelta(hours=24))
    norm = normalized_for_dedup(content)
    same_count = await db.posts.count_documents({
        "device_id": payload.device_id,
        "content_norm": norm,
        "created_at": {"$gte": one_day_ago},
    })
    if same_count >= 5:
        raise HTTPException(429, "Same content max 5×/24h.")
    # Global cap: nobody can flood the platform with the same content even
    # across multiple device IDs (catches device-id rotation bypass).
    global_same = await db.posts.count_documents({
        "content_norm": norm,
        "is_bot": {"$ne": True},
        "created_at": {"$gte": one_day_ago},
    })
    if global_same >= 25:
        raise HTTPException(429, "This content has been posted too many times today.")

    # Spam protection: max 10 posts per device per hour
    one_hour_ago = iso(now_utc() - timedelta(hours=1))
    recent_count = await db.posts.count_documents({
        "device_id": payload.device_id,
        "created_at": {"$gte": one_hour_ago}
    })
    if recent_count >= 10:
        raise HTTPException(429, "You're posting too fast. Try again later.")

    created = now_utc()
    expires = created + timedelta(hours=24)
    post = Post(
        id=str(uuid.uuid4()),
        content=content,
        topic=payload.topic,
        image=image_to_store,
        sudo_name=(payload.sudo_name or "").strip()[:24] or None,
        device_id=payload.device_id,
        created_at=iso(created),
        expires_at=iso(expires),
        lang=_detect_lang(content),
    )
    doc = post.model_dump()
    doc["content_norm"] = norm  # for dedup queries — not exposed in response
    await db.posts.insert_one(doc)
    return post

@api_router.delete("/posts/{post_id}")
async def delete_post(post_id: str, x_device_id: str = Header(...)):
    res = await db.posts.delete_one({"id": post_id, "device_id": x_device_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Post not found or not yours")
    return {"ok": True}

# Post reactions (Hug / Fug) — mirrors music reactions
@api_router.post("/posts/{post_id}/reaction")
async def react_post(post_id: str, payload: ReactionCreate):
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Post not found")
    existing = await db.post_reactions.find_one(
        {"post_id": post_id, "device_id": payload.device_id}
    )
    if existing:
        if existing["type"] == payload.type:
            await db.post_reactions.delete_one(
                {"post_id": post_id, "device_id": payload.device_id}
            )
            await db.posts.update_one(
                {"id": post_id}, {"$inc": {f"{existing['type']}s": -1}}
            )
            return {"ok": True, "action": "removed", "type": existing["type"]}
        else:
            await db.post_reactions.update_one(
                {"post_id": post_id, "device_id": payload.device_id},
                {"$set": {"type": payload.type, "updated_at": iso(now_utc())}},
            )
            await db.posts.update_one(
                {"id": post_id},
                {"$inc": {f"{existing['type']}s": -1, f"{payload.type}s": 1}},
            )
            return {"ok": True, "action": "switched", "type": payload.type}
    else:
        await db.post_reactions.insert_one({
            "id": str(uuid.uuid4()),
            "post_id": post_id,
            "device_id": payload.device_id,
            "type": payload.type,
            "created_at": iso(now_utc()),
        })
        await db.posts.update_one(
            {"id": post_id}, {"$inc": {f"{payload.type}s": 1}}
        )
        return {"ok": True, "action": "added", "type": payload.type}

@api_router.get("/posts/{post_id}/my-reaction")
async def my_post_reaction(post_id: str, device_id: str):
    rec = await db.post_reactions.find_one(
        {"post_id": post_id, "device_id": device_id}, {"_id": 0}
    )
    return {"type": rec["type"] if rec else None}


@api_router.post("/posts/{post_id}/translate")
async def translate_post(post_id: str):
    """On-demand translation of a post to English via Gemini 2.5 Flash.
    Cached on the post document after first call so repeat clicks are free."""
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Post not found")
    content = (post.get("content") or "").strip()
    if not content:
        return {"translation": "", "lang": post.get("lang", "en"), "cached": False}

    # Return cached translation if we have one
    cached = post.get("translation_en")
    if cached:
        return {
            "translation": cached,
            "lang": post.get("lang", "en"),
            "cached": True,
        }

    if not EMERGENT_LLM_KEY or LlmChat is None:
        raise HTTPException(503, "Translation service unavailable.")

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"translate-{post_id}",
            system_message=(
                "You are a translation engine. Translate the user's text to "
                "natural, casual English. Preserve emojis, slang vibe, and "
                "line breaks. If the text is already in English, return it "
                "unchanged. Do NOT add any explanation, prefix, suffix, or "
                "quotes — output the translation only."
            ),
        ).with_model("gemini", "gemini-2.5-flash")
        msg = UserMessage(text=content)
        result = await chat.send_message(msg)
        translation = (result or "").strip()
        # Defensive: strip any wrapping quotes the model may add
        if len(translation) >= 2 and translation[0] in '"“' and translation[-1] in '"”':
            translation = translation[1:-1].strip()
    except Exception as e:
        logger.exception("translation failed: %s", e)
        raise HTTPException(502, "Translation failed. Try again later.")

    # Cache on the post so we don't burn tokens on every click
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"translation_en": translation}},
    )
    return {
        "translation": translation,
        "lang": post.get("lang", "en"),
        "cached": False,
    }

# ============================================================
# Music
# ============================================================
async def cleanup_expired_music():
    """Delete music posts past expires_at (24h)."""
    now_iso = iso(now_utc())
    await db.music_posts.delete_many({"expires_at": {"$lt": now_iso}})

@api_router.get("/music")
async def list_music(limit: int = 30, skip: int = 0):
    await cleanup_expired_music()
    cursor = db.music_posts.find({"hidden": False, "link_url": {"$exists": True}}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

@api_router.get("/music/featured")
async def featured_music(limit: int = 4):
    await cleanup_expired_music()
    cursor = db.music_posts.find({"hidden": False, "link_url": {"$exists": True}}, {"_id": 0}).sort([("hugs", -1), ("created_at", -1)]).limit(limit)
    return await cursor.to_list(length=limit)

def detect_provider(url: str) -> Optional[str]:
    u = url.lower()
    if "spotify.com" in u or "spotify:" in u:
        return "spotify"
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    return None

@api_router.post("/music", response_model=MusicPost)
async def upload_music(payload: MusicCreate):
    provider = payload.provider or detect_provider(payload.link_url)
    if not provider:
        raise HTTPException(400, "Only Spotify or YouTube links are supported.")

    # Apply content rules to caption only (link is whitelisted spotify/youtube)
    caption = (payload.caption or "").strip()
    if caption:
        reason = violation_for(caption)
        if reason:
            raise HTTPException(400, reason)

    one_hour_ago = iso(now_utc() - timedelta(hours=1))
    recent_count = await db.music_posts.count_documents({
        "device_id": payload.device_id,
        "created_at": {"$gte": one_hour_ago}
    })
    if recent_count >= 5:
        raise HTTPException(429, "Slow down — too many uploads.")
    created = now_utc()
    track = MusicPost(
        id=str(uuid.uuid4()),
        link_url=payload.link_url.strip(),
        provider=provider,
        title=(payload.title or "").strip()[:200],
        artist=(payload.artist or "").strip()[:120],
        thumbnail=payload.thumbnail,
        caption=(payload.caption or "").strip()[:800],
        is_lyrics=bool(payload.is_lyrics),
        sudo_name=(payload.sudo_name or "").strip()[:24] or None,
        tags=[t.strip().lstrip("#") for t in payload.tags if t.strip()][:8],
        device_id=payload.device_id,
        created_at=iso(created),
        expires_at=iso(created + timedelta(hours=24)),
    )
    await db.music_posts.insert_one(track.model_dump())
    return track

@api_router.post("/music/{music_id}/reaction")
async def react_music(music_id: str, payload: ReactionCreate):
    track = await db.music_posts.find_one({"id": music_id}, {"_id": 0})
    if not track:
        raise HTTPException(404, "Track not found")
    existing = await db.music_reactions.find_one({"music_id": music_id, "device_id": payload.device_id})
    if existing:
        if existing["type"] == payload.type:
            # Toggle off
            await db.music_reactions.delete_one({"music_id": music_id, "device_id": payload.device_id})
            await db.music_posts.update_one({"id": music_id}, {"$inc": {f"{existing['type']}s": -1}})
            return {"ok": True, "action": "removed", "type": existing["type"]}
        else:
            # Switch reaction
            await db.music_reactions.update_one(
                {"music_id": music_id, "device_id": payload.device_id},
                {"$set": {"type": payload.type, "updated_at": iso(now_utc())}}
            )
            await db.music_posts.update_one(
                {"id": music_id},
                {"$inc": {f"{existing['type']}s": -1, f"{payload.type}s": 1}}
            )
            return {"ok": True, "action": "switched", "type": payload.type}
    else:
        await db.music_reactions.insert_one({
            "id": str(uuid.uuid4()),
            "music_id": music_id,
            "device_id": payload.device_id,
            "type": payload.type,
            "created_at": iso(now_utc()),
        })
        await db.music_posts.update_one({"id": music_id}, {"$inc": {f"{payload.type}s": 1}})
        return {"ok": True, "action": "added", "type": payload.type}

@api_router.get("/music/{music_id}/my-reaction")
async def my_reaction(music_id: str, device_id: str):
    rec = await db.music_reactions.find_one({"music_id": music_id, "device_id": device_id}, {"_id": 0})
    return {"type": rec["type"] if rec else None}

# ============================================================
# Reports
# ============================================================
@api_router.post("/reports")
async def create_report(payload: ReportCreate):
    coll = "posts" if payload.target_type == "post" else "music_posts"
    target = await db[coll].find_one({"id": payload.target_id})
    if not target:
        raise HTTPException(404, "Target not found")
    # one report per device per target
    existing = await db.reports.find_one({
        "target_type": payload.target_type,
        "target_id": payload.target_id,
        "device_id": payload.device_id,
    })
    if existing:
        return {"ok": True, "already": True}
    await db.reports.insert_one({
        "id": str(uuid.uuid4()),
        "target_type": payload.target_type,
        "target_id": payload.target_id,
        "device_id": payload.device_id,
        "reason": payload.reason or "",
        "created_at": iso(now_utc()),
        "resolved": False,
    })
    new_count = (target.get("report_count", 0) + 1)
    update = {"$inc": {"report_count": 1}}
    if new_count >= REPORT_HIDE_THRESHOLD:
        update["$set"] = {"hidden": True}
    await db[coll].update_one({"id": payload.target_id}, update)
    return {"ok": True}

# ============================================================
# Moderation (header-gated)
# ============================================================
def check_mod(x_mod_key: Optional[str]):
    if x_mod_key != MOD_KEY:
        raise HTTPException(401, "Unauthorized")

@api_router.get("/mod/reported")
async def mod_reported(x_mod_key: Optional[str] = Header(None)):
    check_mod(x_mod_key)
    posts = await db.posts.find({"report_count": {"$gt": 0}}, {"_id": 0}).sort("report_count", -1).to_list(200)
    music = await db.music_posts.find({"report_count": {"$gt": 0}}, {"_id": 0}).sort("report_count", -1).to_list(200)
    return {"posts": posts, "music": music}

@api_router.post("/mod/{target_type}/{target_id}/delete")
async def mod_delete(target_type: str, target_id: str, x_mod_key: Optional[str] = Header(None)):
    check_mod(x_mod_key)
    coll = "posts" if target_type == "post" else "music_posts"
    res = await db[coll].delete_one({"id": target_id})
    await db.reports.update_many(
        {"target_type": target_type, "target_id": target_id},
        {"$set": {"resolved": True}}
    )
    return {"ok": True, "deleted": res.deleted_count}

@api_router.post("/mod/{target_type}/{target_id}/safe")
async def mod_safe(target_type: str, target_id: str, x_mod_key: Optional[str] = Header(None)):
    check_mod(x_mod_key)
    coll = "posts" if target_type == "post" else "music_posts"
    await db[coll].update_one({"id": target_id}, {"$set": {"hidden": False, "report_count": 0}})
    await db.reports.update_many(
        {"target_type": target_type, "target_id": target_id},
        {"$set": {"resolved": True}}
    )
    return {"ok": True}

@api_router.get("/mod/bots/status")
async def mod_bots_status(x_mod_key: Optional[str] = Header(None)):
    check_mod(x_mod_key)
    bot_posts = await db.posts.count_documents({"is_bot": True})
    bot_music = await db.music_posts.count_documents({"is_bot": True})
    dedup_count = await db.bot_posted.count_documents({})
    last = await db.bot_posted.find({}, {"_id": 0}).sort("ts", -1).limit(5).to_list(5)
    return {
        "bot_posts_active": bot_posts,
        "bot_music_active": bot_music,
        "dedup_records": dedup_count,
        "recent": last,
    }

@api_router.post("/mod/bots/run-now")
async def mod_bots_run_now(x_mod_key: Optional[str] = Header(None)):
    """Manually trigger one bot cycle (useful for testing / first-time seeding)."""
    check_mod(x_mod_key)
    stats = await run_once(db)
    return {"ok": True, "stats": stats}

@api_router.get("/")
async def root():
    return {"app": "Pluto", "tagline": "Post it. Let it vanish."}

# ============================================================
# Indexes & startup
# ============================================================
@app.on_event("startup")
async def startup():
    await db.posts.create_index("created_at")
    await db.posts.create_index("expires_at")
    await db.posts.create_index("topic")
    await db.posts.create_index([("device_id", 1), ("content_norm", 1), ("created_at", -1)])
    await db.music_posts.create_index("created_at")
    await db.music_posts.create_index("expires_at")
    await db.music_reactions.create_index([("music_id", 1), ("device_id", 1)], unique=True)
    await db.post_reactions.create_index([("post_id", 1), ("device_id", 1)], unique=True)
    await db.reports.create_index([("target_type", 1), ("target_id", 1), ("device_id", 1)], unique=True)
    # One-time cleanup: drop legacy music posts that don't have link_url
    await db.music_posts.delete_many({"link_url": {"$exists": False}})
    # Backfill hugs/fugs + content_norm + lang on legacy posts so all rules apply
    import random as _rnd
    legacy_cursor = db.posts.find(
        {
            "$or": [
                {"hugs": {"$exists": False}},
                {"fugs": {"$exists": False}},
                {"content_norm": {"$exists": False}},
                {"lang": {"$exists": False}},
            ]
        },
        {"_id": 1, "is_bot": 1, "content": 1, "hugs": 1, "fugs": 1,
         "content_norm": 1, "lang": 1},
    )
    async for p in legacy_cursor:
        update: dict = {}
        if p.get("hugs") is None or p.get("fugs") is None:
            is_bot = bool(p.get("is_bot"))
            hugs = _rnd.randint(3, 84) if is_bot else 0
            fugs = _rnd.randint(0, max(2, hugs // 12)) if is_bot else 0
            update["hugs"] = hugs
            update["fugs"] = fugs
        if not p.get("content_norm") and p.get("content"):
            update["content_norm"] = normalized_for_dedup(p["content"])
        if not p.get("lang") and p.get("content"):
            update["lang"] = _detect_lang(p["content"])
        if update:
            await db.posts.update_one({"_id": p["_id"]}, {"$set": update})
    # Launch background bot loops
    app.state.bot_task = asyncio.create_task(bot_loop(db))
    app.state.engage_task = asyncio.create_task(engagement_loop(db))

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
