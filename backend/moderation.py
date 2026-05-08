"""Pluto content moderation — enforces the posting rules surfaced in the UI:

  Posts vanish in 24h. No links. Blocked: illegal content, hate/harassment,
  doxxing, misinformation, content involving minors, piracy, scams/wallet-
  drainers, terror promotion, sexual content, and self-harm.
  Same content max 5x/24h.

These are first-pass keyword/regex filters. They are intentionally conservative
— meant to block the obvious cases. A user-driven report flow handles the rest.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Link / URL detection (rule: "No links")
# ---------------------------------------------------------------------------
_URL_RE = re.compile(
    r"""(?ix)
    \b(?:
        https?://[^\s<>]+              # http(s)://something
      | www\.[^\s<>]+                  # www.something
      | (?:[a-z0-9-]+\.)+              # foo.bar.baz.
        (?:com|net|org|io|co|gg|app|dev|xyz|me|info|biz|ai|so|us|uk|de|fr|in|tv|cn|ru|jp|tech|live|stream|link|store|cash|finance|crypto|nft|wallet|exchange|bet|casino|porn|xxx|adult|onlyfans|fans|tiktok|instagram|fb|facebook|telegram|t|discord|whatsapp|wa|tg|signal|reddit|x|twitter|onion|i2p)
        (?:/[^\s<>]*)?                 # optional path
    )
    """
)

# ---------------------------------------------------------------------------
# Blocked-category keyword sets. Lowercase whole-word matches.
# Kept narrow on purpose so we don't over-block organic chatter.
# ---------------------------------------------------------------------------
_HATE = {
    # racial/ethnic slurs and slogans (intentionally redacted patterns)
    "kike", "kikes", "nigger", "niggers", "n1gger", "chink", "chinks",
    "spic", "spics", "gook", "gooks", "kkk", "white power", "heil hitler",
    "sieg heil", "1488", "14/88", "14 words",
    # anti-LGBT slurs
    "faggot", "faggots", "fag", "fags", "tranny", "trannies", "dyke", "dykes",
    # ableist
    "retard", "retards",
}
_HARASSMENT = {
    "kill yourself", "kys", "kill urself", "kill ur self", "go die", "off yourself",
}
_DOXXING = {
    "ssn", "social security number",
    "home address", "her address is", "his address is", "lives at",
    "leak his", "leak her", "leaked her", "leaked his",
}
_MINORS_SEXUAL = {
    "cp", "child porn", "underage porn", "loli", "lolicon", "shota", "shotacon",
    "minor nudes", "child nudes", "kid nudes", "preteen porn",
    # specific predator-grooming language
    "send nudes kid", "groom a child", "grooming kids",
}
_PIRACY = {
    "piratebay", "thepiratebay", "1337x", "rarbg", "yts.mx",
    "free movie download", "free crack download", "warez", "torrent crack",
    "iptv crack", "stream nflx free",
}
_SCAMS = {
    "wallet drainer", "drain your wallet", "drainer kit", "send eth to",
    "double your btc", "double your eth", "free airdrop claim",
    "claim airdrop here", "validate your wallet", "connect wallet to receive",
    "seed phrase here", "verify seed phrase", "send your seed",
    "private key here", "send private key",
}
_TERROR = {
    "isis recruit", "isis recruiter", "join isis", "join al-qaeda", "join al qaeda",
    "make a bomb", "build a bomb", "build pipe bomb", "pipe bomb tutorial",
    "shoot up a school", "shoot up school", "mass shooting plan",
}
_SEXUAL = {
    "porn", "porno", "pornhub", "xvideos", "xnxx", "redtube", "onlyfans link",
    "send nudes", "nude pics", "nudes pls", "nude photos",
    "horny dm", "sext me", "hot sex", "fuck me", "rape", "raping",
    "blowjob", "blow job", "handjob", "hand job", "anal sex", "deepthroat",
    "cum tribute", "cum on me", "jerk off",
}
_SELF_HARM = {
    "i want to die", "i wanna die", "want to kill myself", "want to kms",
    "going to kill myself", "gonna kms", "gonna kill myself", "end my life tonight",
    "cut myself", "cutting myself", "self harm tutorial", "how to slit",
    "how to overdose", "best way to die", "painless way to die",
    "noose tutorial", "hanging tutorial",
}
_MISINFO = {
    "vaccines cause autism", "vaccine causes autism", "5g causes covid",
    "covid is a hoax", "covid hoax", "moon landing was fake",
    "election was stolen 2020", "stop the steal", "qanon truth",
    "earth is flat fact",
}

_CATEGORIES: list[Tuple[str, set[str]]] = [
    ("hate/harassment", _HATE),
    ("hate/harassment", _HARASSMENT),
    ("doxxing", _DOXXING),
    ("content involving minors", _MINORS_SEXUAL),
    ("piracy", _PIRACY),
    ("scams/wallet-drainers", _SCAMS),
    ("terror promotion", _TERROR),
    ("sexual content", _SEXUAL),
    ("self-harm", _SELF_HARM),
    ("misinformation", _MISINFO),
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_link(text: str) -> bool:
    return bool(_URL_RE.search(text))


def detect_blocked_category(text: str) -> Optional[str]:
    """Return the human label of the first blocked category found, or None."""
    norm = _normalize(text)
    for label, terms in _CATEGORIES:
        for t in terms:
            # whole-phrase match for multi-word, word-boundary for single
            if " " in t:
                if t in norm:
                    return label
            else:
                if re.search(rf"\b{re.escape(t)}\b", norm):
                    return label
    return None


def violation_for(text: str) -> Optional[str]:
    """Return a user-facing reason if `text` violates the posting rules.
    Returns None if the post is OK to publish.
    """
    if detect_link(text):
        return "Links aren't allowed on Pluto."
    cat = detect_blocked_category(text)
    if cat:
        return f"Blocked: {cat}."
    return None


def normalized_for_dedup(text: str) -> str:
    """A loose normalization used to detect 'same content' for the 5x/24h rule."""
    s = text.lower()
    # collapse punctuation/whitespace so trivial variations still match
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
