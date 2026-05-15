"""Image moderation for Pluto — uses Gemini 2.5 Flash (via emergentintegrations)
to classify uploaded images for nudity / gore / violence / drugs / hate /
self-harm / minors-in-unsafe-contexts.

Public API:
  moderate_image_data_url(data_url: str) -> ImageVerdict
  ImageVerdict.safe : bool
  ImageVerdict.reason : str   # short human-readable reason if unsafe
  ImageVerdict.category : str # one of CATEGORY names

The classifier is asked to return strict JSON so we can route on the
result deterministically. On any model error / parse failure we fail
SAFE-by-default (reject the image) rather than letting bad content through.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from typing import Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Lazy import so the module can still be imported in environments without
# the integration installed (it'll just refuse images at runtime).
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    _HAS_INTEGRATION = True
except Exception as e:  # pragma: no cover
    logger.warning("emergentintegrations missing: %s", e)
    _HAS_INTEGRATION = False

# Optional Pillow for image normalization (resize, strip-animation, recompress)
try:
    from PIL import Image as PILImage
    _HAS_PIL = True
except Exception:  # pragma: no cover
    _HAS_PIL = False


EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
MODEL_PROVIDER = "gemini"
MODEL_NAME = "gemini-2.5-flash"

# Hard size cap before we even ask the LLM
MAX_BYTES = 4 * 1024 * 1024          # 4MB
TARGET_MAX_EDGE = 1024               # downscale to fit in this box
ACCEPTED_MIME = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


# ---------------------------------------------------------------------------
@dataclass
class ImageVerdict:
    safe: bool
    reason: str = ""
    category: str = ""

    def to_dict(self) -> dict:
        return {"safe": self.safe, "reason": self.reason, "category": self.category}


# ---------------------------------------------------------------------------
_DATA_URL_RE = re.compile(r"^data:(?P<mime>[\w/+.-]+);base64,(?P<b64>.+)$", re.DOTALL)


def _parse_data_url(data_url: str) -> Optional[Tuple[str, bytes]]:
    """Returns (mime, raw_bytes) or None if not a valid data URL."""
    m = _DATA_URL_RE.match(data_url.strip())
    if not m:
        return None
    mime = m.group("mime").lower().split(";")[0]
    try:
        raw = base64.b64decode(m.group("b64"), validate=False)
    except Exception:
        return None
    return mime, raw


def _normalize_image(raw: bytes, mime: str) -> Tuple[str, bytes, str]:
    """Re-encode to JPEG, strip animation, downscale to <=TARGET_MAX_EDGE.
    Returns (new_mime, new_bytes, new_base64).
    Raises ValueError on unreadable images.
    """
    if not _HAS_PIL:
        # Can't normalize — return as-is so we at least try moderation
        return mime, raw, base64.b64encode(raw).decode("ascii")

    try:
        img = PILImage.open(io.BytesIO(raw))
    except Exception as e:
        raise ValueError(f"unreadable image: {e}")

    # Animated → first frame only
    if getattr(img, "is_animated", False):
        img.seek(0)

    img = img.convert("RGB")
    # Downscale
    w, h = img.size
    if max(w, h) > TARGET_MAX_EDGE:
        img.thumbnail((TARGET_MAX_EDGE, TARGET_MAX_EDGE), PILImage.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    new_raw = buf.getvalue()
    return "image/jpeg", new_raw, base64.b64encode(new_raw).decode("ascii")


# ---------------------------------------------------------------------------
_PROMPT = """\
You are an image safety classifier for Pluto, an anonymous text-sharing app.
Examine the image and decide whether it is SAFE to publish.

Return STRICT JSON only, in this exact schema (no markdown fences, no prose):
{
  "safe": true | false,
  "category": "<one of: ok | nudity | sexual | violence | gore | weapons | drugs | hate_symbols | self_harm | minors | other_unsafe>",
  "reason": "<short reason, 0 to 12 words>"
}

Mark as UNSAFE (safe=false) if the image contains ANY of:
- nudity, partial nudity, lingerie/underwear-only photography, sexual acts,
  sexually suggestive poses, fetish imagery
- explicit violence, gore, mutilation, dead bodies, severe injuries
- weapons being aimed/fired at people, or weapons in a threatening context
- drug use or paraphernalia in use (pills/needles/bongs/dealers)
- hate symbols (swastika, KKK insignia, white-supremacist flags, etc.)
- self-harm: cutting, blood, suicide imagery, hanging/noose
- any minor (under 18) in a sexual, abusive, or otherwise unsafe context

Mark as SAFE (safe=true) for: normal selfies (clothed), pets, food, landscapes,
art, memes, screenshots of text or chats, drawings/diagrams, plants, sports,
crowds, vehicles, abstract art, cosplay that isn't sexual, etc.

When ambiguous, lean toward UNSAFE.
"""


async def _classify_with_gemini(image_base64: str) -> ImageVerdict:
    """Send the image to Gemini Flash and parse a JSON verdict."""
    if not EMERGENT_LLM_KEY:
        logger.error("EMERGENT_LLM_KEY not set — cannot moderate")
        return ImageVerdict(safe=False, reason="moderation unavailable", category="error")
    if not _HAS_INTEGRATION:
        return ImageVerdict(safe=False, reason="moderation unavailable", category="error")

    session_id = f"mod-{uuid.uuid4().hex[:12]}"
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    msg = UserMessage(
        text="Classify this image. Return only the JSON.",
        file_contents=[ImageContent(image_base64=image_base64)],
    )

    try:
        raw = await chat.send_message(msg)
    except Exception as e:
        logger.warning("gemini moderation call failed: %s", e)
        return ImageVerdict(safe=False, reason="moderation failed", category="error")

    text = (raw or "").strip()
    # Strip possible markdown fences if model added them despite instructions
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()

    try:
        data = json.loads(text)
    except Exception:
        # Try to extract first JSON object via regex
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            logger.warning("gemini returned non-JSON: %r", text[:200])
            return ImageVerdict(safe=False, reason="unclassifiable", category="error")
        try:
            data = json.loads(m.group(0))
        except Exception:
            logger.warning("gemini JSON parse failed: %r", text[:200])
            return ImageVerdict(safe=False, reason="unclassifiable", category="error")

    safe = bool(data.get("safe"))
    category = str(data.get("category", "")).lower().strip() or ("ok" if safe else "other_unsafe")
    reason = str(data.get("reason", "")).strip()[:120]
    return ImageVerdict(safe=safe, reason=reason, category=category)


# ---------------------------------------------------------------------------
async def moderate_image_data_url(data_url: str) -> ImageVerdict:
    """Top-level entrypoint. Validates → normalizes → classifies → returns
    a verdict. Always fails-safe (rejects) on any error.
    """
    parsed = _parse_data_url(data_url)
    if not parsed:
        return ImageVerdict(safe=False, reason="not a valid image data URL", category="error")

    mime, raw = parsed

    if mime not in ACCEPTED_MIME:
        return ImageVerdict(safe=False, reason="only JPEG, PNG or WEBP allowed", category="error")

    if len(raw) > MAX_BYTES:
        return ImageVerdict(safe=False, reason="image too large (4MB max)", category="error")

    # Normalize to safe re-encoded JPEG (strips EXIF / animations / oversized)
    try:
        _new_mime, _new_raw, new_b64 = _normalize_image(raw, mime)
    except ValueError as e:
        return ImageVerdict(safe=False, reason=str(e), category="error")

    return await _classify_with_gemini(new_b64)


# Friendly category labels for user-facing rejection messages
CATEGORY_LABEL = {
    "nudity": "nudity",
    "sexual": "sexual content",
    "violence": "violence",
    "gore": "graphic violence",
    "weapons": "weapons",
    "drugs": "drugs",
    "hate_symbols": "hate symbols",
    "self_harm": "self-harm imagery",
    "minors": "content involving minors",
    "other_unsafe": "unsafe content",
    "error": "image moderation error",
    "ok": "ok",
}


def category_label(category: str) -> str:
    return CATEGORY_LABEL.get(category, category or "unsafe content")
