"""Pluto content moderation — enforces the posting rules surfaced in the UI:

  Posts vanish in 24h. No links. Blocked: illegal content, hate/harassment,
  doxxing, misinformation, content involving minors, piracy, scams/wallet-
  drainers, terror promotion, sexual content, and self-harm.
  Same content max 5x/24h.

The matcher runs each phrase against TWO normalized variants of the input
text so simple bypass tricks (leetspeak, repeated chars, punctuation
between letters, mixed case, zero-width chars) cannot slip through:

  • collapsed = lowercase, whitespace collapsed (matches phrases verbatim)
  • squashed  = lowercase, leet→latin, every non-letter stripped
                (matches "k!ll y0urs3lf", "k.y.s", "kiiilll mysellfff")
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
# Normalization helpers
# ---------------------------------------------------------------------------
_LEET = str.maketrans({
    "0": "o", "1": "i", "!": "i", "|": "i", "3": "e", "4": "a", "@": "a",
    "5": "s", "$": "s", "7": "t", "+": "t", "8": "b", "9": "g", "2": "z",
    "€": "e", "£": "l", "¥": "y", "°": "o",
})


def _collapse(text: str) -> str:
    """Lowercase + whitespace collapsed. Keeps punctuation."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _squash(text: str) -> str:
    """Aggressive: lowercase → leet→latin → drop every non-letter →
    collapse repeated letters to 1 ("kiiilll" → "kil")."""
    s = text.lower().translate(_LEET)
    s = re.sub(r"[^a-z]+", "", s)
    s = re.sub(r"(.)\1+", r"\1", s)
    return s


# ---------------------------------------------------------------------------
# Blocked-category phrase sets. Each phrase is matched against BOTH the
# collapsed form (with word boundaries) and the squashed form (substring).
# ---------------------------------------------------------------------------
_HATE = {
    # racial/ethnic slurs and slogans
    "kike", "kikes", "nigger", "niggers", "nigga", "niggas", "n1gger", "n1gga",
    "chink", "chinks", "spic", "spics", "gook", "gooks", "wetback", "wetbacks",
    "towelhead", "sandnigger", "sand nigger", "raghead", "beaner", "beaners",
    "kkk", "white power", "white pride", "heil hitler", "sieg heil",
    "1488", "14/88", "14 words", "blood and soil", "jews will not replace us",
    "gas the jews", "gas the blacks", "race war now", "race traitor",
    # anti-LGBT slurs
    "faggot", "faggots", "fag", "fags", "tranny", "trannies", "dyke", "dykes",
    "homo trash", "queer trash",
    # ableist
    "retard", "retards", "retarded piece", "sped trash",
}
_HARASSMENT = {
    # direct "go die" attacks at others
    "kill yourself", "kill yourselves", "kys", "kysself",
    "kill urself", "kill ur self", "kill yrself", "kill yr self",
    "go die", "go and die", "go kys", "off yourself", "neck yourself",
    "neck urself", "rope yourself", "rope urself",
    "you should die", "u should die", "you deserve to die", "u deserve to die",
    "you're worthless", "youre worthless", "ur worthless",
    "nobody loves you", "no one loves you", "everyone hates you",
    "world without you", "world would be better without you",
    "the world would be better off without you",
    "i hope you die", "hope u die", "wish you were dead", "wish u were dead",
    # threats
    "i will kill you", "i'll kill you", "ill kill you", "imma kill you",
    "gonna kill you", "going to kill you", "i'll murder you", "ill murder you",
    "i'll hurt you", "ill hurt you", "i'll find you", "ill find you and",
    "i'll rape", "ill rape", "i will rape", "gonna rape",
    "i'll beat", "ill beat the shit", "gonna beat the shit",
    # gendered abuse aimed AT another person (not generic profanity)
    "stupid bitch", "dumb bitch", "fucking whore", "stupid whore",
    "you cunt", "u cunt", "fucking cunt",
}
_DOXXING = {
    "ssn", "social security number", "social security #",
    "home address is", "her address is", "his address is", "their address is",
    "lives at", "she lives at", "he lives at",
    "leak his", "leak her", "leak their", "leaked her", "leaked his",
    "doxxing", "dox him", "dox her", "dox them",
    "phone number is", "her number is", "his number is",
    "credit card number", "cc number is",
    "passport number", "license plate is",
}
_MINORS_SEXUAL = {
    "cp", "child porn", "child p0rn", "underage porn", "underage nude",
    "loli", "lolicon", "shota", "shotacon", "lolita porn",
    "minor nudes", "minor nude", "child nudes", "kid nudes", "preteen porn",
    "teen porn 13", "teen porn 14", "teen porn 15",
    "send nudes kid", "groom a child", "grooming kids", "groom kids",
    "child molest", "molest kids", "rape a kid", "rape children",
    "pedophile guide", "pedo guide", "pedo dating", "ageplay child",
}
_PIRACY = {
    "piratebay", "the pirate bay", "thepiratebay", "1337x", "rarbg",
    "yts.mx", "yts mx", "fitgirl repack", "fitgirl repacks",
    "free movie download", "free movies download",
    "free crack", "free cracks", "warez", "torrent crack",
    "iptv crack", "stream nflx free", "free netflix account",
    "leaked album download", "leaked album dl",
    "cracked office", "cracked photoshop", "cracked adobe",
    "keygen for", "license key generator",
}
_SCAMS = {
    "wallet drainer", "drain your wallet", "drainer kit", "send eth to",
    "send btc to", "send sol to", "send usdt to",
    "double your btc", "double your eth", "double your sol",
    "free airdrop claim", "claim airdrop here", "claim free airdrop",
    "validate your wallet", "validate wallet", "connect wallet to receive",
    "seed phrase here", "verify seed phrase", "send your seed",
    "send seed phrase", "share seed phrase",
    "private key here", "send private key", "share private key",
    "metamask support number", "ledger support number",
    "kyc bypass", "bypass kyc",
    "investment guaranteed return", "guaranteed 100x", "guaranteed 1000x",
    "ponzi opportunity",
}
_TERROR = {
    "isis recruit", "isis recruiter", "join isis", "join al-qaeda",
    "join al qaeda", "join hamas terror", "join boko haram",
    "make a bomb", "build a bomb", "build pipe bomb", "pipe bomb tutorial",
    "how to make a bomb", "how to build a bomb", "homemade bomb",
    "ied tutorial", "explosive vest", "suicide vest",
    "shoot up a school", "shoot up school", "shoot up the school",
    "mass shooting plan", "mass shooting tutorial", "school shooting plan",
    "kill all jews", "kill all muslims", "kill all blacks", "kill all whites",
    "kill all christians", "ethnic cleansing of",
}
_SEXUAL = {
    "porn", "pornhub", "xvideos", "xnxx", "redtube", "youporn",
    "spankbang", "chaturbate", "stripchat", "camsoda",
    "onlyfans link", "of link",
    "send nudes", "nude pics", "nudes pls", "nude photos",
    "horny dm", "sext me", "let's sext", "lets sext",
    "fuck me", "fuck me hard", "let me fuck", "wanna fuck",
    "let's fuck", "lets fuck", "wanna get fucked", "fuck me daddy",
    "rape porn", "raping",
    "blowjob", "blow job", "handjob", "hand job", "rimjob", "rim job",
    "anal sex", "anal porn", "deepthroat", "deep throat",
    "cum tribute", "cum on me", "cum on my", "jerk off", "jerking off",
    "jack off video", "edging tutorial",
    "incest porn", "rape video", "snuff video",
    "milf porn", "teen sex video", "amateur porn",
    "dick pic", "dickpic", "send dick", "show dick",
    "horny daddy", "horny mommy",
}
_SELF_HARM = {
    # bare suicide phrases
    "kill myself", "killing myself", "kms", "kms tonight", "kms tn",
    "die tonight", "die alone tonight", "want to die", "wanna die",
    # suicide intent / ideation
    "i want to die", "i wanna die", "i wana die", "wanna die rn",
    "want to kill myself", "wanna kill myself", "wanna kms",
    "want to kms", "going to kill myself", "gonna kill myself", "gonna kms",
    "imma kill myself", "im going to kill myself", "i'm killing myself",
    "im killing myself tonight",
    "end my life", "ending my life", "end it all", "ending it all",
    "end myself", "ending myself", "i'll end it", "ill end it tonight",
    "wish i was dead", "wish i were dead", "wish i didn't exist",
    "wish i didnt exist", "wish i was never born", "shouldn't be alive",
    "shouldnt be alive", "shouldnt exist",
    "tired of living", "tired of being alive", "no reason to live",
    "no point in living", "no point living anymore",
    "cant go on", "can't go on", "cant do this anymore",
    "cant take it anymore", "can't take it anymore",
    "ready to die", "ready to go", "today is the day", "tonight is the day",
    "it'll all be over soon", "ill all be over soon", "soon it'll be over",
    "goodbye forever", "this is goodbye", "won't be here tomorrow",
    "wont be here tomorrow", "won't see tomorrow",
    # methods
    "cut myself", "cutting myself", "i cut", "razor blade arm",
    "razor on my", "self harm", "self-harm", "selfharm",
    "harm myself", "harming myself", "hurt myself", "hurting myself",
    "self harm tutorial", "how to self harm", "ways to self harm",
    "how to slit", "slit my wrists", "slit my throat", "slit wrist",
    "how to overdose", "best way to overdose", "overdose on pills",
    "swallow pills", "swallow bleach", "drink bleach",
    "best way to die", "painless way to die", "least painful way to die",
    "easiest way to die", "fastest way to die",
    "noose tutorial", "how to make a noose", "hanging tutorial",
    "hang myself", "hung myself", "going to hang myself",
    "shoot myself", "blow my brains", "blow my brains out",
    "jump off bridge", "jump off building", "jump off roof",
    "step in front of train", "step in front of a train",
    "carbon monoxide suicide", "co poisoning suicide",
    "commit suicide", "suicide method", "suicide note", "suicide plan",
    "suicide pact", "suicide forum",
    # eating disorder pro-ana style (also self-harm)
    "thinspo", "pro-ana", "pro ana tips", "pro mia", "promia",
    "starve myself", "starving myself to be skinny",
}
_MISINFO = {
    "vaccines cause autism", "vaccine causes autism", "vaccines = autism",
    "5g causes covid", "5g spreads covid", "5g causes virus",
    "covid is a hoax", "covid hoax", "covid was fake",
    "moon landing was fake", "moon landing fake",
    "election was stolen 2020", "stop the steal", "election fraud 2020",
    "qanon truth", "the storm is coming q", "where we go one we go all qanon",
    "earth is flat fact", "flat earth proof",
    "great replacement theory", "white genocide is real",
    "9 11 inside job", "9/11 inside job", "9-11 inside job",
}

# Each tuple: (label-shown-to-user, phrase set)
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

# Pre-compute squashed forms of every phrase once at import time so
# matching at runtime is just an `in` check on a string.
_CATEGORIES_PREP: list[Tuple[str, list[Tuple[re.Pattern, str]]]] = []
for label, phrases in _CATEGORIES:
    prepped: list[Tuple[re.Pattern, str]] = []
    for ph in phrases:
        # collapsed form regex (word boundaries when possible)
        if " " in ph or "-" in ph or "/" in ph:
            # multi-word phrase — substring match on collapsed
            pattern = re.compile(re.escape(ph.lower()))
        else:
            pattern = re.compile(rf"\b{re.escape(ph.lower())}\b")
        # squashed form — letters only, repeats collapsed to 1
        squashed = re.sub(r"[^a-z]+", "", ph.lower().translate(_LEET))
        squashed = re.sub(r"(.)\1+", r"\1", squashed)
        prepped.append((pattern, squashed))
    _CATEGORIES_PREP.append((label, prepped))


def detect_link(text: str) -> bool:
    return bool(_URL_RE.search(text))


def detect_blocked_category(text: str) -> Optional[str]:
    """Return the human label of the first blocked category found, or None."""
    collapsed = _collapse(text)
    squashed = _squash(text)
    for label, prepped in _CATEGORIES_PREP:
        for pattern, sq in prepped:
            if pattern.search(collapsed):
                return label
            if sq and len(sq) >= 3 and sq in squashed:
                return label
    return None


def violation_for(text: str) -> Optional[str]:
    """Return a user-facing reason if `text` violates the posting rules.
    Returns None if the post is OK to publish.
    """
    if not text or not text.strip():
        return None
    if detect_link(text):
        return "Links aren't allowed on Pluto."
    cat = detect_blocked_category(text)
    if cat:
        return f"Blocked: {cat}."
    return None


def normalized_for_dedup(text: str) -> str:
    """A loose normalization used to detect 'same content' for the 5x/24h rule.

    Lowercase, strip all non-alphanumeric, collapse whitespace. Doesn't apply
    leet substitution here — copy-paste spam keeps its own form, and we want
    "Hello WORLD!" to match "hello world" without aliasing into other strings.
    """
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
