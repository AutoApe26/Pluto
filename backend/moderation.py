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
# Extremism / dehumanization / genocide slogans — these are NEVER relaxed,
# not even under is_lyrics+#music. These aren't "artistic expression" — they
# are organizing language for political violence and are criminalized in most
# of Pluto's likely markets (DE §86a/§130, FR Loi Gayssot, UK OSA, AU eSafety).
_EXTREMISM = {
    # white-supremacist organizing slogans / codes
    "kkk", "white power", "white pride", "white genocide is real",
    "heil hitler", "sieg heil", "hail hitler", "hail victory",
    "1488", "14/88", "14 words", "fourteen words",
    "blood and soil", "blut und boden",
    "jews will not replace us", "jews wont replace us",
    "great replacement is real", "the great replacement",
    "rahowa", "racial holy war",
    # explicit eliminationist calls (these duplicate-protect _TERROR)
    "gas the jews", "gas the blacks", "gas the kikes",
    "race war now", "race traitor must die",
    "death to the jews", "death to muslims", "death to blacks",
    "death to whites", "death to gays", "death to trans",
    # Islamist eliminationist
    "death to america", "death to israel",
    # other org slogans
    "ss honour", "totenkopf glory",
}
# Slurs + abusive insults. These appear in mainstream lyrics (rap, punk,
# metal) and are relaxed under lyrics mode. Eliminationist/organizing
# slogans live in _EXTREMISM above and stay blocked even in lyrics mode.
_HATE = {
    # racial/ethnic slurs
    "kike", "kikes", "nigger", "niggers", "nigga", "niggas", "n1gger", "n1gga",
    "chink", "chinks", "spic", "spics", "gook", "gooks", "wetback", "wetbacks",
    "towelhead", "sandnigger", "sand nigger", "raghead", "beaner", "beaners",
    "race traitor",
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
    # threats — kill / murder / hurt
    "i will kill you", "i'll kill you", "ill kill you", "imma kill you",
    "gonna kill you", "going to kill you", "i will murder you",
    "i'll murder you", "ill murder you", "imma murder you",
    "gonna murder you", "i'll hurt you", "ill hurt you", "imma hurt you",
    "i'll find you", "ill find you and", "i will find you and",
    "i'll come for you", "ill come for you", "coming for you",
    "i'll rape", "ill rape", "i will rape", "gonna rape", "imma rape",
    "i'll torture you", "ill torture you", "torture you slowly",
    # violent threats — physical harm
    "i'll beat", "ill beat the shit", "gonna beat the shit",
    "beat the shit out of you", "beat the crap out of you",
    "kick your ass", "kick ur ass", "ill kick your ass",
    "i'll punch", "ill punch you", "punch your face", "punch ur face",
    "smash your face", "smash ur face", "break your face", "break ur face",
    "break your bones", "break ur bones", "break your neck",
    "snap your neck", "snap ur neck", "wring your neck",
    "choke you out", "choke u out", "strangle you",
    "stab you", "stab u", "i'll stab", "ill stab you", "gonna stab",
    "shoot you", "ill shoot you", "i'll shoot you", "gonna shoot you",
    "blow your brains", "blow ur brains", "put a bullet in you",
    "put a bullet in your", "i'll put a bullet",
    "slit your throat", "slit ur throat", "slice your throat",
    "cut you up", "cut u up", "i'll cut you", "ill cut you",
    "burn your house", "burn ur house", "burn down your", "torch your",
    "burn you alive", "burn u alive",
    "bury you", "i'll bury you", "ill bury you", "putting you in the ground",
    "put you in the ground", "in a body bag", "body-bag you",
    "make you bleed", "watch you bleed", "drown you",
    "run you over", "running you over",
    # violent threats — toward groups
    "lynch them", "lynch him", "lynch her", "lynching them",
    "string them up", "string him up", "string her up",
    "hang them all", "hang them high", "hang em all",
    # gendered abuse aimed AT another person (not generic profanity)
    "stupid bitch", "dumb bitch", "fucking whore", "stupid whore",
    "you cunt", "u cunt", "fucking cunt",
    # abusive insults directed at a person
    "you're a piece of shit", "youre a piece of shit", "ur a piece of shit",
    "you piece of shit", "u piece of shit",
    "you are trash", "youre trash", "ur trash", "you trash",
    "you are garbage", "youre garbage", "ur garbage",
    "go fuck yourself", "go fuck urself", "fuck off and die",
    "eat shit and die", "eat shit", "rot in hell", "burn in hell",
    "i hate you and hope", "i hate your existence",
    "subhuman scum", "subhuman trash", "you're subhuman", "youre subhuman",
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
    # bomb-making (generic)
    "make a bomb", "build a bomb", "build pipe bomb", "pipe bomb tutorial",
    "how to make a bomb", "how to build a bomb", "homemade bomb",
    "ied tutorial", "explosive vest", "suicide vest", "suicide bomber",
    "improvised explosive", "build an ied", "make an ied",
    # specific explosive materials — tutorial/construction context only,
    # not bare nouns (avoids false positives on song titles like BTS
    # "Dynamite" or AC/DC "TNT" and slang "you're dynamite tonight").
    "make dynamite", "made dynamite", "making dynamite", "build dynamite",
    "homemade dynamite", "diy dynamite", "rig dynamite", "rigging dynamite",
    "stick of dynamite", "case of dynamite", "crate of dynamite",
    "pack of dynamite", "bundle of dynamite",
    "make tnt", "homemade tnt", "diy tnt", "rig tnt", "rigging tnt",
    "stick of tnt", "case of tnt", "crate of tnt", "block of tnt",
    "make c4", "make c-4", "homemade c4", "homemade c-4", "diy c4",
    "rig c4", "rig c-4", "pack of c4", "block of c4", "block of c-4",
    "make semtex", "homemade semtex", "rig semtex",
    "make thermite", "homemade thermite", "diy thermite", "thermite charge",
    "make napalm", "homemade napalm", "diy napalm",
    "make anfo", "homemade anfo", "anfo bomb", "anfo charge",
    "make tatp", "homemade tatp", "diy tatp",
    "make hmtd", "homemade hmtd", "diy hmtd",
    "ammonium nitrate bomb", "fertilizer bomb", "fertiliser bomb",
    "pressure cooker bomb", "pressure-cooker bomb",
    "nail bomb tutorial", "shrapnel bomb", "shrapnel charge",
    "blasting cap tutorial", "detonator tutorial",
    "plastic explosive tutorial",
    # bomb / explosive / arson threats (directed at a place or person)
    "i'll bomb", "ill bomb", "i will bomb", "imma bomb",
    "gonna bomb", "going to bomb", "we'll bomb", "well bomb",
    "bomb that place", "bomb this place", "bomb the place",
    "bomb that building", "bomb this building", "bomb the building",
    "bomb that school", "bomb the school", "bomb that mall", "bomb the mall",
    "bomb that mosque", "bomb that church", "bomb that synagogue",
    "bomb that station", "bomb the airport", "bomb that airport",
    "bomb that office", "bomb the office", "bomb their house",
    "plant a bomb", "planting a bomb", "set off a bomb",
    "detonate a bomb", "detonate the bomb",
    "blow up that", "blow up this", "blow up the", "blow up their",
    "blow it up", "im gonna blow", "i'm gonna blow up",
    "imma blow up", "going to blow up", "gonna blow up",
    "explode that", "explode this", "explode the",
    "burn down that", "burn down this", "burn down the",
    "burn it down tonight", "torch the building", "torch their place",
    "set fire to that", "set fire to the", "set on fire tonight",
    # firearms / weapons threats
    "bring a gun to", "bringing a gun to", "bring my gun to",
    "i have a gun and", "i got a gun and",
    "shoot up the", "shoot up this", "shoot up that",
    "shoot up a mall", "shoot up the mall", "shoot up the office",
    "shoot up the church", "shoot up the mosque", "shoot up the synagogue",
    "open fire on", "open fire at",
    "gun down them", "mow them down",
    "spray bullets", "drive-by shooting plan", "drive by shooting plan",
    "stab them all", "knife them all",
    "behead them", "behead him", "behead her",
    # chemical / biological
    "anthrax attack", "ricin attack", "sarin attack",
    "release sarin", "release anthrax", "weaponize anthrax",
    "nerve agent attack",
    # vehicular
    "drive into a crowd", "ram into a crowd", "ramming attack",
    "vehicle ramming",
    # mass-casualty plans
    "shoot up a school", "shoot up school", "shoot up the school",
    "mass shooting plan", "mass shooting tutorial", "school shooting plan",
    "school shooting tomorrow", "school shooting today",
    "mass casualty event", "kill everyone at",
    "wipe them out", "wipe out that",
    # genocide / ethnic violence
    "kill all jews", "kill all muslims", "kill all blacks", "kill all whites",
    "kill all christians", "kill all asians", "kill all hindus",
    "kill all gays", "kill all trans", "kill all immigrants",
    "ethnic cleansing of", "genocide against",
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
    ("extremism/dehumanization", _EXTREMISM),
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


# ---------------------------------------------------------------------------
# Morse code detection — long runs of dot/dash characters (with optional
# slash word separators) are not legitimate posts and are commonly used to
# smuggle blocked words past plain-text filters. We block anything that
# *looks* like morse: at least 3 morse "letters" (dot/dash groups separated
# by whitespace, optionally with '/' word separators).
# ---------------------------------------------------------------------------
_MORSE_GROUP_RE = re.compile(r"[.\-·–—_]{1,6}")  # single morse letter
_MORSE_SEQUENCE_RE = re.compile(
    r"(?:[.\-·–—_]{1,6}[ \t/]+){2,}[.\-·–—_]{1,6}"
)


def detect_morse_code(text: str) -> bool:
    if not text:
        return False
    # Quick reject if text doesn't have enough morse characters
    if sum(1 for c in text if c in ".-·–—_") < 6:
        return False
    for match in _MORSE_SEQUENCE_RE.finditer(text):
        seq = match.group(0)
        groups = [g for g in re.split(r"[ \t/]+", seq) if g]
        # Need at least 3 morse letters that are *only* dots/dashes
        if len(groups) >= 3 and all(_MORSE_GROUP_RE.fullmatch(g) for g in groups):
            return True
    return False


def detect_link(text: str) -> bool:
    return bool(_URL_RE.search(text))


# ---------------------------------------------------------------------------
# Context-aware violent-intent regex detector.
#
# Catches threats that aren't in the curated phrase list, like:
#   "I will bomb the office"  /  "I'm gonna shoot her tomorrow"
#   "we'll murder them all"  /  "imma blow up that place"
#   "I have a bomb"  /  "I've got an explosive"  /  "bringing a gun in"
#   "should kill them"  /  "need to bomb that"  /  "let's shoot them up"
#
# Patterns are tight — they require BOTH a personal intent/possession
# stem AND a violent action+verb to fire — so safe lookalikes
# ("I bombed my exam", "that show was the bomb", "explosive performance",
# "gun show this weekend", "shoot for the stars") are NOT blocked.
# ---------------------------------------------------------------------------

# Subject pronouns/groups that can carry an intent
_SUBJ = r"(?:i|we|they|y'?all|you|he|she|imma|i'?m|im)"
# Combined subject+intent contractions ("i'll", "we'll", "i've", "im gonna")
_SUBJ_INTENT_COMBO = (
    r"(?:i'?ll|we'?ll|they'?ll|you'?ll|he'?ll|she'?ll|"
    r"i'?ve|we'?ve|they'?ve|you'?ve|ive|weve|theyve|youve|"
    r"imma|ima|i'?m\s+gonna|im\s+gonna|i'?m\s+going\s+to|im\s+going\s+to|"
    r"i'?m\s+finna|im\s+finna|"
    r"i'?m\s+about\s+to|im\s+about\s+to)"
)
# Future / intent modal phrases ("will", "'ll", "am going to", "gonna",
# "imma", "going to", "want to", "wanna", "plan to", "should", "need to",
# "have to", "must", "let's", "going")
_INTENT = (
    r"(?:'?ll|will|wanna|want\s+to|gonna|going\s+to|"
    r"am\s+going\s+to|am\s+gonna|plan(?:ning)?\s+to|"
    r"should|need\s+to|have\s+to|gotta|gotsta|must|"
    r"about\s+to|finna|fixin\s+to|fixing\s+to|tryna|trying\s+to)"
)
# Violent verbs — must be at the verb position (not a noun like "gun show").
# Includes past-tense / -ing / plural inflections so "be killed", "be murdered",
# "got shot up", "is being bombed" also match.
_VIOLENT_VERBS = (
    r"(?:bomb(?:ed|ing|s)?|nuke[ds]?|blow\s+up|blown\s+up|blow\s+it\s+up|"
    r"blow\s+them\s+up|"
    r"detonate[ds]?|detonating|explode[ds]?|exploding|set\s+off|"
    r"set\s+on\s+fire|burn\s+down|burning\s+down|burnt\s+down|"
    r"burn\s+alive|burned\s+alive|torch(?:ed|ing|es)?|firebomb(?:ed|ing)?|"
    r"shoot|shot|shooting|shoots|shoot\s+up|shot\s+up|"
    r"gun\s+down|gunned\s+down|gunning\s+down|mow\s+down|mowed\s+down|spray|"
    r"open\s+fire(?:\s+on|\s+at)?|"
    r"stab(?:bed|bing|s)?|slash(?:ed|ing|es)?|slice(?:d|s)?|slicing|"
    r"cut\s+up|cut\s+them\s+up|knife(?:d|s)?|knifing|gut(?:ted|ting|s)?|"
    r"kill(?:ed|ing|s)?|murder(?:ed|ing|s)?|"
    r"massacre[ds]?|massacring|slaughter(?:ed|ing|s)?|"
    r"exterminate[ds]?|exterminating|wipe\s+out|wiped\s+out|wiping\s+out|"
    r"behead(?:ed|ing|s)?|decapitate[ds]?|decapitating|"
    r"hang(?:ed|ing|s)?|hung|lynch(?:ed|ing|es)?|string\s+up|strung\s+up|"
    r"strangle[ds]?|strangling|choke(?:d|s)?|choking|choke\s+out|choked\s+out|"
    r"suffocate[ds]?|suffocating|drown(?:ed|ing|s)?|"
    r"beat\s+up|beat\s+to\s+death|beating\s+up|beaten\s+up|"
    r"pummel(?:ed|ing|s)?|pummelled|"
    r"break\s+(?:your|ur|his|her|their)\s+(?:bones?|neck|face|legs?|arms?|skull|jaw|teeth)|"
    r"snap\s+(?:your|ur|his|her|their)\s+neck|"
    r"smash\s+(?:your|ur|his|her|their)\s+(?:face|skull|head)|"
    r"punch\s+(?:your|ur|his|her|their)\s+(?:face|teeth|lights\s+out)|"
    r"crush\s+(?:your|ur|his|her|their)\s+(?:skull|head|throat)|"
    r"poison(?:ed|ing|s)?|gas\s+them|gas\s+him|gas\s+her|gas\s+the|"
    r"rape[ds]?|raping|sexually\s+assault(?:ed|ing|s)?|"
    r"hunt\s+(?:you|him|her|them)\s+down|hunted\s+down|"
    r"find\s+(?:you|him|her|them)\s+and\s+(?:kill|hurt|murder|beat|harm)|"
    r"come\s+for\s+(?:you|him|her|them)|"
    r"end\s+(?:you|him|her|them|their\s+life|her\s+life|his\s+life)|"
    r"put\s+(?:a\s+)?bullet\s+in|"
    r"slit\s+(?:your|his|her|their)\s+throat|"
    r"bury\s+(?:you|him|her|them)|"
    r"erase\s+(?:you|him|her|them)\s+from\s+(?:this|the)\s+(?:earth|world|planet))"
)

# Weapons/explosives that signal intent when paired with possession
_WEAPON_NOUNS = (
    r"(?:bomb|pipe\s+bomb|nail\s+bomb|car\s+bomb|nuke|nuclear\s+weapon|"
    r"explosive(?:s)?|grenade(?:s)?|ied|"
    r"automatic\s+rifle|assault\s+rifle|ak[\s-]?47|"
    r"machete|sawed[\s-]off|"
    r"sarin|anthrax|ricin|nerve\s+agent|biological\s+weapon|chemical\s+weapon|"
    r"molotov(?:\s+cocktail)?|"
    # Unambiguous explosive materials. Note: 'dynamite' and 'tnt' are NOT
    # in this regex on purpose — both are widely used in song titles,
    # band names, and as slang for "great". They're covered by high-signal
    # phrases in _TERROR ('stick of dynamite', 'homemade tnt', etc).
    r"c[\s-]?4|c[\s-]?4\s+(?:charge|brick|block)|semtex|pe[\s-]?4|"
    r"nitroglycerin(?:e)?|nitroglycerine|"
    r"ammonium\s+nitrate|anfo|tatp|hmtd|"
    r"thermite\s+(?:charge|grenade|bomb)|"
    r"napalm\s+(?:bomb|grenade|charge|round)|"
    r"det\s+cord|detcord|detonating\s+cord|"
    r"detonator(?:s)?|blasting\s+cap(?:s)?|"
    r"plastic\s+explosive(?:s)?|shaped\s+charge(?:s)?|"
    r"pressure[\s-]?cooker\s+bomb|fertili[sz]er\s+bomb)"
)

# "I will / we'll / I'm gonna ..." + violent verb
_VIOLENT_INTENT_RE = re.compile(
    rf"\b{_SUBJ}\s+{_INTENT}\s+{_VIOLENT_VERBS}\b",
    re.IGNORECASE,
)
# Contraction form: "i'll / we'll / imma / i'm gonna" + violent verb
_VIOLENT_INTENT_COMBO_RE = re.compile(
    rf"\b{_SUBJ_INTENT_COMBO}\s+{_VIOLENT_VERBS}\b",
    re.IGNORECASE,
)
# "let's kill / let's bomb / let's burn down ..."
_LETS_VIOLENT_RE = re.compile(
    rf"\blet\s*'?s\s+{_VIOLENT_VERBS}\b",
    re.IGNORECASE,
)
# "should kill / need to bomb / gotta murder ..."
_ADVOCACY_RE = re.compile(
    rf"\b(?:should|needs?\s+to|gotta|must|deserves?\s+to)\s+(?:be\s+)?{_VIOLENT_VERBS}\b",
    re.IGNORECASE,
)
# "I have a bomb / I've got an explosive / he has a grenade ..." (possession + intent context word)
_POSSESS_WEAPON_RE = re.compile(
    rf"\b{_SUBJ}\s+(?:'?ve\s+)?(?:has|have|had|got|own|bringing|carrying|holding|"
    rf"made|making|built|building|planted|setting\s+up)\s+"
    rf"(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|"
    rf"four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|"
    rf"working|functional|operational|\d+)\s+){{0,5}}{_WEAPON_NOUNS}\b",
    re.IGNORECASE,
)
# Subject-less possession of a weapon: "carrying a loaded ak-47",
# "bringing a grenade to school", "got a bomb", "planting an ied" —
# inherently threatening regardless of whether a subject is stated.
_POSSESS_WEAPON_BARE_RE = re.compile(
    rf"\b(?:bringing|carrying|holding|smuggling|smuggle|stashing|stash|"
    rf"hidden|hiding|loading\s+up|loaded\s+up|"
    rf"got|gotten|grabbed|grabbing|"
    rf"made|making|built|building|planted|planting|plant|"
    rf"placing|place|setting\s+up|set\s+up|"
    rf"acquired|acquiring|sourced|sourcing)\s+"
    rf"(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|"
    rf"four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|"
    rf"working|functional|operational|\d+)\s+){{0,5}}{_WEAPON_NOUNS}\b",
    re.IGNORECASE,
)
# "ive got a bomb" / "weve got grenades" — possession contraction without apostrophe
_POSSESS_WEAPON_COMBO_RE = re.compile(
    rf"\b{_SUBJ_INTENT_COMBO}\s+"
    rf"(?:got|gotten|carried|carrying|holding|bringing|made|making|built|"
    rf"building|planted|planting|stashed|stashing|hidden|hiding)\s+"
    rf"(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|"
    rf"four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|"
    rf"working|functional|operational|\d+)\s+){{0,5}}{_WEAPON_NOUNS}\b",
    re.IGNORECASE,
)
# Direct violent action toward people (no subject required) —
# "kill them all", "shoot her", "rape them", "stab him", "behead them",
# "exterminate every immigrant", "drown all of them"
_VERB_PERSON_THREAT_RE = re.compile(
    r"\b(?:bomb|nuke|shoot|stab|kill|murder|rape|behead|decapitate|"
    r"strangle|drown|poison|gas|hang|lynch|string\s+up|"
    r"massacre|slaughter|exterminate|eliminate|eradicate|destroy|"
    r"torture|mutilate)\s+"
    r"(?:them|him|her|y'?all|you\s+all|all\s+of\s+(?:you|them|us)|"
    r"those|these|everyone|every\s+one\s+of\s+(?:them|us|you)|"
    r"(?:the|every|all|those|these|those\s+filthy|all\s+the|some)\s+"
    r"(?:kids?|children|jews?|muslims?|christians?|hindus?|sikhs?|"
    r"buddhists?|gays?|lesbians?|trans|trannies|queers?|"
    r"blacks?|whites?|asians?|arabs?|latinos?|mexicans?|"
    r"immigrants?|refugees?|migrants?|"
    r"cops?|police|infidels?|kafirs?|gentiles?|goyim|"
    r"liberals?|conservatives?|democrats?|republicans?|"
    r"women|men|girls?|boys?|babies|infants?))\b",
    re.IGNORECASE,
)
# Body-part attack ("break his bones", "smash her face", "crush his skull")
_BODY_PART_ATTACK_RE = re.compile(
    r"\b(?:break|snap|smash|crush|punch|crack|shatter|destroy)\s+"
    r"(?:your|ur|his|her|their|my|the|that|this)\s+"
    r"(?:bones?|neck|face|legs?|arms?|skull|jaw|teeth|throat|head|"
    r"spine|knees?|ribs?|nose|kneecaps?)\b",
    re.IGNORECASE,
)
# "put a bullet in him / between her eyes / through their head"
_BULLET_THREAT_RE = re.compile(
    r"\bput\s+(?:a\s+)?bullet(?:s)?\s+(?:in|into|through|between)\s+"
    r"(?:you|him|her|them|his|her|their|the|that)\b",
    re.IGNORECASE,
)
# Mass-attack on a population / village / group
_WIPE_OUT_RE = re.compile(
    r"\b(?:wipe\s+out|exterminate|eliminate|eradicate|cleanse|purge|"
    r"end\s+the\s+existence\s+of)\s+"
    r"(?:the|that|this|their|all|every|every\s+single|those|these)\s+"
    r"(?:village|town|city|tribe|race|nation|people|peoples|family|families|"
    r"community|communities|kids?|children|men|women|jews?|muslims?|"
    r"christians?|hindus?|gays?|blacks?|whites?|asians?|immigrants?)\b",
    re.IGNORECASE,
)
# Direct "shoot up the X" / "bomb the X" / "burn down the X" — even without
# subject/intent, this construction is essentially always a threat or call
# to violence against a place.
_ACTION_PLACE_RE = re.compile(
    r"\b(?:bomb|nuke|burn\s+down|torch|firebomb|blow\s+up|shoot\s+up|"
    r"attack|raid|destroy|massacre|storm|level)\s+"
    r"(?:the|that|this|their|every|all|some)\s+"
    r"(?:school|college|university|mall|church|mosque|synagogue|temple|"
    r"office|building|airport|station|store|shop|hospital|club|bar|"
    r"theater|theatre|cinema|stadium|arena|concert|festival|"
    r"home|house|apartment|crowd|class|classroom|street|neighborhood|"
    r"neighbourhood|town|city|village|place|venue|embassy|government|"
    r"capitol|capital|parliament|courthouse|police\s+station)\b",
    re.IGNORECASE,
)


def detect_violent_intent(text: str) -> bool:
    """Return True if ``text`` contains a violent-intent construction.

    Combines several context-aware regex passes:
      - subject + intent + violent verb ("I will bomb the office")
      - subject+intent contractions ("i'll murder", "we'll bomb", "imma shoot")
      - "let's / should / need to / gotta + violent verb"
      - weapon possession (with or without explicit subject)
      - direct violent verb targeting people / body parts / places
      - "put a bullet in", mass-attack on populations, body-part attacks

    Safe lookalikes ("song is the bomb", "I bombed my exam", "gun show",
    "explosive performance", "shoot for the stars", "killing it at work")
    do NOT match — every pattern requires either a violent
    subject+intent scaffold, a weapon noun, or a body-part/people object.
    """
    if not text:
        return False
    collapsed = _collapse(text)
    return bool(
        _VIOLENT_INTENT_RE.search(collapsed)
        or _VIOLENT_INTENT_COMBO_RE.search(collapsed)
        or _LETS_VIOLENT_RE.search(collapsed)
        or _ADVOCACY_RE.search(collapsed)
        or _POSSESS_WEAPON_RE.search(collapsed)
        or _POSSESS_WEAPON_BARE_RE.search(collapsed)
        or _POSSESS_WEAPON_COMBO_RE.search(collapsed)
        or _VERB_PERSON_THREAT_RE.search(collapsed)
        or _BODY_PART_ATTACK_RE.search(collapsed)
        or _BULLET_THREAT_RE.search(collapsed)
        or _WIPE_OUT_RE.search(collapsed)
        or _ACTION_PLACE_RE.search(collapsed)
    )


# Categories that get RELAXED under Parental-Advisory / lyrics mode.
# This is the "artistic expression" set — explicit lyrics on Pluto can
# carry sexual content, hate-style aggression (a lot of rap/punk uses
# slurs/insults for effect), and exaggerated/false claims (lyrics are
# hyperbolic by nature). Everything OUTSIDE this set — extremism/
# dehumanization slogans, doxxing, minors, piracy, scams, terror, self-
# harm, links, morse code — stays blocked because none of those are
# "lyrical expression", they are illegal or unsafe content full-stop.
# NOTE: extremism/dehumanization is the NEW never-relaxed slice carved
# out of the old _HATE list — Nazi/KKK slogans, genocide chants, and
# eliminationist calls now stay blocked even with is_lyrics=true.
_LYRICS_RELAXED_CATEGORIES = {
    "sexual content",
    "hate/harassment",
    "misinformation",
}


def detect_blocked_category(text: str, allow_sexual: bool = False) -> Optional[str]:
    """Return the human label of the first blocked category found, or None.

    When ``allow_sexual`` is true (used as the legacy name for "lyrics mode"),
    the categories in ``_LYRICS_RELAXED_CATEGORIES`` are skipped. The
    illegal/extreme categories (doxxing, minors, piracy, scams, terror,
    self-harm) are still enforced even in lyrics mode.
    """
    collapsed = _collapse(text)
    squashed = _squash(text)
    for label, prepped in _CATEGORIES_PREP:
        if allow_sexual and label in _LYRICS_RELAXED_CATEGORIES:
            continue
        for pattern, sq in prepped:
            if pattern.search(collapsed):
                return label
            if sq and len(sq) >= 3 and sq in squashed:
                return label
    return None


_FRIENDLY_LABELS = {
    "extremism/dehumanization": "extremist or dehumanizing language (Nazi/KKK slogans, genocide calls)",
    "hate/harassment": "hate speech, threats or abusive language",
    "doxxing": "personal information / doxxing",
    "content involving minors": "content involving minors",
    "piracy": "piracy",
    "scams/wallet-drainers": "scams or wallet-drainer content",
    "terror promotion": "violent extremism or terror promotion",
    "sexual content": "sexual content",
    "self-harm": "self-harm content",
    "misinformation": "misinformation",
}


def violation_for(text: str, allow_sexual: bool = False) -> Optional[str]:
    """Return a user-facing reason if ``text`` violates the posting rules.
    Returns None if the post is OK to publish.

    ``allow_sexual`` is intended for the #music topic lyrics path — explicit
    lyrics are tolerated there but every other hard-block category (hate,
    self-harm, doxxing, terror, minors, scams, piracy, misinformation,
    links, morse code) is still enforced.
    """
    if not text or not text.strip():
        return None
    if detect_link(text):
        return "Your post can't be published — links aren't allowed on Pluto."
    if detect_morse_code(text):
        return "Your post can't be published — morse code isn't allowed on Pluto."
    # Context-aware violent-intent (regex) — runs before the curated phrase
    # categories so dynamically-phrased threats ("I will bomb the office")
    # are caught even if the exact phrase isn't in the static lists.
    if detect_violent_intent(text):
        friendly = _FRIENDLY_LABELS.get("terror promotion", "violent threats")
        return (
            f"Your post was blocked for {friendly}. "
            "Pluto doesn't allow threats, hate speech, abuse, or other harmful content."
        )
    cat = detect_blocked_category(text, allow_sexual=allow_sexual)
    if cat:
        friendly = _FRIENDLY_LABELS.get(cat, cat)
        return (
            f"Your post was blocked for {friendly}. "
            "Pluto doesn't allow threats, hate speech, abuse, or other harmful content."
        )
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
