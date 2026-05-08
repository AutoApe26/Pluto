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
from datetime import datetime, timezone, timedelta


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

MOD_KEY = os.environ.get('MOD_KEY', 'pluto-mod-2026')
REPORT_HIDE_THRESHOLD = 3

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
    {"slug": "tell-anything", "name": "Tell Anything", "icon": "MessageSquare", "color": "#00F0FF"},
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
    content: str = Field(min_length=1, max_length=2000)
    topic: str
    image: Optional[str] = None  # base64 data url
    device_id: str

class Post(BaseModel):
    id: str
    content: str
    topic: str
    image: Optional[str] = None
    device_id: str
    created_at: str
    expires_at: str
    report_count: int = 0
    hidden: bool = False

class MusicCreate(BaseModel):
    artist: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    caption: Optional[str] = ""
    audio: str  # base64 data url
    cover: Optional[str] = None
    tags: List[str] = []
    device_id: str

class MusicPost(BaseModel):
    id: str
    artist: str
    title: str
    caption: str = ""
    audio: str
    cover: Optional[str] = None
    tags: List[str] = []
    device_id: str
    hugs: int = 0
    fugs: int = 0
    created_at: str
    report_count: int = 0
    hidden: bool = False

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
        content=payload.content.strip(),
        topic=payload.topic,
        image=payload.image,
        device_id=payload.device_id,
        created_at=iso(created),
        expires_at=iso(expires),
    )
    await db.posts.insert_one(post.model_dump())
    return post

@api_router.delete("/posts/{post_id}")
async def delete_post(post_id: str, x_device_id: str = Header(...)):
    res = await db.posts.delete_one({"id": post_id, "device_id": x_device_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Post not found or not yours")
    return {"ok": True}

# ============================================================
# Music
# ============================================================
@api_router.get("/music")
async def list_music(limit: int = 30, skip: int = 0):
    cursor = db.music_posts.find({"hidden": False}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

@api_router.get("/music/featured")
async def featured_music(limit: int = 3):
    cursor = db.music_posts.find({"hidden": False}, {"_id": 0}).sort("hugs", -1).limit(limit)
    return await cursor.to_list(length=limit)

@api_router.post("/music", response_model=MusicPost)
async def upload_music(payload: MusicCreate):
    if not payload.audio.startswith("data:audio"):
        raise HTTPException(400, "Audio must be a base64 data URL")
    # Spam protection
    one_hour_ago = iso(now_utc() - timedelta(hours=1))
    recent_count = await db.music_posts.count_documents({
        "device_id": payload.device_id,
        "created_at": {"$gte": one_hour_ago}
    })
    if recent_count >= 5:
        raise HTTPException(429, "Slow down — too many uploads.")
    track = MusicPost(
        id=str(uuid.uuid4()),
        artist=payload.artist.strip(),
        title=payload.title.strip(),
        caption=(payload.caption or "").strip(),
        audio=payload.audio,
        cover=payload.cover,
        tags=[t.strip() for t in payload.tags if t.strip()][:8],
        device_id=payload.device_id,
        created_at=iso(now_utc()),
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
    await db.music_posts.create_index("created_at")
    await db.music_reactions.create_index([("music_id", 1), ("device_id", 1)], unique=True)
    await db.reports.create_index([("target_type", 1), ("target_id", 1), ("device_id", 1)], unique=True)

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
