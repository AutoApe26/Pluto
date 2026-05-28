// Frontend pre-check for posting safety. Mirrors a SUBSET of the backend
// moderation phrases for instant inline feedback — the backend remains
// the authoritative enforcer (every post round-trips through
// moderation.violation_for() before being stored).
//
// We deliberately keep this list smaller and tuned to high-signal
// threats / hate / violent threats so the inline warning is fast and
// avoids false positives on edgy-but-allowed content. Anything missed
// here will still be rejected server-side with a clear error message.

const PHRASES = [
  // threats — kill / harm
  "kill yourself", "kill urself", "kys",
  "i'll kill you", "ill kill you", "imma kill you", "gonna kill you",
  "i will kill you", "i'll murder you", "ill murder you",
  "i'll hurt you", "ill hurt you", "i'll find you",
  "i'll rape", "ill rape", "i will rape", "gonna rape",
  // physical violence
  "i'll beat", "beat the shit out of you",
  "kick your ass", "punch your face", "smash your face",
  "break your bones", "break your neck", "snap your neck",
  "choke you out", "strangle you",
  "stab you", "i'll stab", "ill stab", "gonna stab",
  "shoot you", "i'll shoot", "ill shoot", "gonna shoot you",
  "blow your brains", "put a bullet in",
  "slit your throat", "burn your house", "burn you alive",
  "bury you", "in a body bag",
  // abusive directed-at-you insults
  "piece of shit", "go fuck yourself", "fuck off and die",
  "eat shit and die", "rot in hell", "burn in hell",
  "you're trash", "youre trash", "ur trash", "you're garbage",
  "you're subhuman", "youre subhuman", "subhuman scum",
  // hate / slurs (only the most unambiguous)
  "nigger", "kike", "faggot", "tranny",
  // extremism / dehumanization — NEVER relaxed (mirrors backend _EXTREMISM)
  "kill all jews", "kill all muslims", "kill all blacks", "kill all whites",
  "gas the jews", "gas the blacks", "race war now",
  "white power", "white pride", "white genocide is real",
  "heil hitler", "hail hitler", "sieg heil", "hail victory",
  "1488", "14/88", "14 words", "fourteen words",
  "blood and soil", "jews will not replace us", "jews wont replace us",
  "great replacement is real", "rahowa", "racial holy war",
  "death to the jews", "death to muslims", "death to blacks",
  "death to whites", "death to gays", "death to trans",
  "death to america", "death to israel",
  "kkk",
  // terror / mass violence
  "shoot up a school", "shoot up the school", "shoot up the mall",
  "shoot up the office", "shoot up this", "shoot up that",
  "make a bomb", "build a bomb", "build a pipe bomb", "pipe bomb",
  "how to make a bomb", "homemade bomb", "ied tutorial",
  "explosive vest", "suicide vest", "improvised explosive",
  // explosive materials (high-signal phrases — mirrors backend _TERROR)
  "make dynamite", "made dynamite", "making dynamite", "build dynamite",
  "homemade dynamite", "diy dynamite", "rig dynamite",
  "stick of dynamite", "case of dynamite", "crate of dynamite",
  "pack of dynamite", "bundle of dynamite",
  "make tnt", "homemade tnt", "diy tnt", "rig tnt",
  "stick of tnt", "case of tnt", "crate of tnt", "block of tnt",
  "make c4", "make c-4", "homemade c4", "homemade c-4",
  "diy c4", "rig c4", "rig c-4", "pack of c4", "block of c4", "block of c-4",
  "make semtex", "homemade semtex", "rig semtex",
  "make thermite", "homemade thermite", "thermite charge",
  "make napalm", "homemade napalm",
  "napalm bomb tutorial", "napalm bomb instructions", "napalm bomb guide",
  "napalm tutorial", "napalm instructions", "napalm recipe",
  "make anfo", "homemade anfo", "anfo bomb",
  "make tatp", "homemade tatp",
  "make hmtd", "homemade hmtd",
  "ammonium nitrate bomb", "fertilizer bomb", "fertiliser bomb",
  "pressure cooker bomb", "pressure-cooker bomb",
  "nail bomb tutorial", "blasting cap tutorial", "detonator tutorial",
  "plastic explosive tutorial",
  // direct bomb / explosive / arson threats
  "i'll bomb", "ill bomb", "i will bomb", "imma bomb",
  "gonna bomb", "going to bomb",
  "bomb that place", "bomb this place", "bomb the place",
  "bomb that building", "bomb the building",
  "bomb that school", "bomb the school", "bomb that mall",
  "bomb that mosque", "bomb that church", "bomb the airport",
  "plant a bomb", "set off a bomb", "detonate a bomb",
  "blow up that", "blow up this", "blow up the", "blow up their",
  "blow it up", "gonna blow up", "going to blow up",
  "burn down that", "burn down this", "burn down the",
  "torch their place", "torch the building",
  "bring a gun to", "bringing a gun to", "i have a gun and",
  "open fire on", "open fire at", "spray bullets",
  "behead them", "behead him", "behead her",
  "anthrax attack", "ricin attack", "sarin attack",
  "drive into a crowd", "ram into a crowd",
  "school shooting", "mass shooting plan",
];

// CSAM-specific phrase list — checked BEFORE generic PHRASES so the user
// gets the accurate zero-tolerance message rather than the generic
// threat/hate message. Mirrors a subset of backend _MINORS_SEXUAL.
const CSAM_PHRASES = [
  // Direct CSAM acronyms / explicit phrases
  "csam", "child sexual abuse material",
  "kiddie porn", "kiddy porn", "kiddie sex", "kiddy sex",
  "child porn", "child p0rn", "underage porn", "underage nude",
  "loli", "lolicon", "shota", "shotacon",
  "child rape", "kid rape", "minor rape",
  "pedo content", "pedo material", "pedo videos", "pedo pics",
  // CSAM-trafficker glorification
  "i love epstein", "love epstein",
  "epstein was right", "epstein did nothing wrong",
  "free epstein", "epstein is my hero", "epstein was a hero",
  "epstein was a legend", "team epstein", "respect epstein",
  "i love epstien", "love epstien", "epstien was right",
  "epstien did nothing wrong", "free epstien", "rip epstien",
  "epstien is my hero", "i love eptsein", "love eptsein",
  "i love epsteen", "love epsteen", "i love epstine", "love epstine",
  "i love ghislaine maxwell", "free ghislaine", "free maxwell",
  "ghislaine is innocent", "maxwell was right",
  "i love jimmy savile", "savile did nothing wrong",
  "i love jerry sandusky", "sandusky did nothing wrong",
  "i love roman polanski", "polanski did nothing wrong",
  // MAP / pedo self-identification glorification
  "i am a map", "im a map", "proud map", "proud pedo",
  "proud pedophile", "pedo pride", "map pride", "pedo rights",
  "map rights", "maps are valid",
];

// Cheap normalizer that mirrors backend's `_collapse` semantics enough
// for the unambiguous phrases above. Lowercase + collapse whitespace.
const normalize = (text) => (text || "").toLowerCase().replace(/\s+/g, " ").trim();

// -------------------------------------------------------------------------
// Context-aware violent-intent regexes — MIRROR of backend
// `detect_violent_intent` in /app/backend/moderation.py. Keep these two
// lists in lock-step: anything added to the backend regex must be added
// here too so the inline warning stays accurate.
// -------------------------------------------------------------------------
const SUBJ = "(?:i|we|they|y'?all|you|he|she|imma|i'?m|im)";
const SUBJ_INTENT_COMBO =
  "(?:i'?ll|we'?ll|they'?ll|you'?ll|he'?ll|she'?ll|" +
  "i'?ve|we'?ve|they'?ve|you'?ve|ive|weve|theyve|youve|" +
  "imma|ima|i'?m\\s+gonna|im\\s+gonna|i'?m\\s+going\\s+to|im\\s+going\\s+to|" +
  "i'?m\\s+finna|im\\s+finna|i'?m\\s+about\\s+to|im\\s+about\\s+to)";
const INTENT =
  "(?:'?ll|will|wanna|want\\s+to|gonna|going\\s+to|am\\s+going\\s+to|" +
  "am\\s+gonna|plan(?:ning)?\\s+to|should|need\\s+to|have\\s+to|gotta|" +
  "must|about\\s+to|finna|fixin\\s+to|fixing\\s+to|tryna|trying\\s+to)";
const VIOLENT_VERBS =
  "(?:bomb(?:ed|ing|s)?|nuke[ds]?|blow\\s+up|blown\\s+up|blow\\s+it\\s+up|" +
  "blow\\s+them\\s+up|detonate[ds]?|detonating|explode[ds]?|exploding|" +
  "set\\s+off|set\\s+on\\s+fire|burn\\s+down|burning\\s+down|burnt\\s+down|" +
  "burn\\s+alive|burned\\s+alive|torch(?:ed|ing|es)?|firebomb(?:ed|ing)?|" +
  "shoot|shot|shooting|shoots|shoot\\s+up|shot\\s+up|" +
  "gun\\s+down|gunned\\s+down|gunning\\s+down|mow\\s+down|mowed\\s+down|spray|" +
  "open\\s+fire(?:\\s+on|\\s+at)?|" +
  "stab(?:bed|bing|s)?|slash(?:ed|ing|es)?|slice(?:d|s)?|slicing|" +
  "cut\\s+up|cut\\s+them\\s+up|knife(?:d|s)?|knifing|gut(?:ted|ting|s)?|" +
  "kill(?:ed|ing|s)?|murder(?:ed|ing|s)?|" +
  "massacre[ds]?|massacring|slaughter(?:ed|ing|s)?|" +
  "exterminate[ds]?|exterminating|wipe\\s+out|wiped\\s+out|wiping\\s+out|" +
  "behead(?:ed|ing|s)?|decapitate[ds]?|decapitating|" +
  "hang(?:ed|ing|s)?|hung|lynch(?:ed|ing|es)?|string\\s+up|strung\\s+up|" +
  "strangle[ds]?|strangling|choke(?:d|s)?|choking|choke\\s+out|choked\\s+out|" +
  "suffocate[ds]?|suffocating|drown(?:ed|ing|s)?|" +
  "beat\\s+up|beat\\s+to\\s+death|beating\\s+up|beaten\\s+up|" +
  "pummel(?:ed|ing|s)?|pummelled|" +
  "break\\s+(?:your|ur|his|her|their)\\s+(?:bones?|neck|face|legs?|arms?|skull|jaw|teeth)|" +
  "snap\\s+(?:your|ur|his|her|their)\\s+neck|" +
  "smash\\s+(?:your|ur|his|her|their)\\s+(?:face|skull|head)|" +
  "punch\\s+(?:your|ur|his|her|their)\\s+(?:face|teeth|lights\\s+out)|" +
  "crush\\s+(?:your|ur|his|her|their)\\s+(?:skull|head|throat)|" +
  "poison(?:ed|ing|s)?|gas\\s+them|gas\\s+him|gas\\s+her|gas\\s+the|" +
  "rape[ds]?|raping|sexually\\s+assault(?:ed|ing|s)?|" +
  "hunt\\s+(?:you|him|her|them)\\s+down|hunted\\s+down|" +
  "come\\s+for\\s+(?:you|him|her|them)|" +
  "end\\s+(?:you|him|her|them|their\\s+life|her\\s+life|his\\s+life)|" +
  "put\\s+(?:a\\s+)?bullet\\s+in|" +
  "slit\\s+(?:your|his|her|their)\\s+throat|" +
  "bury\\s+(?:you|him|her|them))";
const WEAPON_NOUNS =
  "(?:bomb|pipe\\s+bomb|nail\\s+bomb|car\\s+bomb|nuke|nuclear\\s+weapon|" +
  "explosive(?:s)?|grenade(?:s)?|ied|automatic\\s+rifle|assault\\s+rifle|" +
  "ak[\\s-]?47|machete|sawed[\\s-]off|sarin|anthrax|ricin|nerve\\s+agent|" +
  "biological\\s+weapon|chemical\\s+weapon|molotov(?:\\s+cocktail)?|" +
  // Mirrors backend _WEAPON_NOUNS: unambiguous explosive materials.
  // 'dynamite' and 'tnt' are intentionally excluded (heavy metaphor/
  // song-title overlap) — covered by phrase list instead.
  "c[\\s-]?4|c[\\s-]?4\\s+(?:charge|brick|block)|semtex|pe[\\s-]?4|" +
  "nitroglycerin(?:e)?|nitroglycerine|" +
  "ammonium\\s+nitrate|anfo|tatp|hmtd|" +
  "thermite\\s+(?:charge|grenade|bomb)|" +
  "napalm\\s+(?:bomb|grenade|charge|round)|" +
  "det\\s+cord|detcord|detonating\\s+cord|" +
  "detonator(?:s)?|blasting\\s+cap(?:s)?|" +
  "plastic\\s+explosive(?:s)?|shaped\\s+charge(?:s)?|" +
  "pressure[\\s-]?cooker\\s+bomb|fertili[sz]er\\s+bomb)";

const INTENT_RE = new RegExp(`\\b${SUBJ}\\s+${INTENT}\\s+${VIOLENT_VERBS}\\b`, "i");
const INTENT_COMBO_RE = new RegExp(
  `\\b${SUBJ_INTENT_COMBO}\\s+${VIOLENT_VERBS}\\b`,
  "i"
);
const LETS_RE = new RegExp(`\\blet\\s*'?s\\s+${VIOLENT_VERBS}\\b`, "i");
const ADVOCACY_RE = new RegExp(
  `\\b(?:should|needs?\\s+to|gotta|must|deserves?\\s+to)\\s+(?:be\\s+)?${VIOLENT_VERBS}\\b`,
  "i"
);
const POSSESS_RE = new RegExp(
  `\\b${SUBJ}\\s+(?:'?ve\\s+)?` +
    `(?:has|have|had|got|own|bringing|carrying|holding|made|making|` +
    `built|building|planted|setting\\s+up)\\s+` +
    `(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|` +
    `four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|` +
    `working|functional|operational|\\d+)\\s+){0,5}` +
    WEAPON_NOUNS +
    `\\b`,
  "i"
);
const POSSESS_BARE_RE = new RegExp(
  "\\b(?:bringing|carrying|holding|smuggling|smuggle|stashing|stash|" +
    "hidden|hiding|loading\\s+up|loaded\\s+up|got|gotten|grabbed|grabbing|" +
    "made|making|built|building|planted|planting|plant|" +
    "placing|place|setting\\s+up|set\\s+up|" +
    "acquired|acquiring|sourced|sourcing)\\s+" +
    "(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|" +
    "four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|" +
    "working|functional|operational|\\d+)\\s+){0,5}" +
    WEAPON_NOUNS +
    "\\b",
  "i"
);
const POSSESS_COMBO_RE = new RegExp(
  `\\b${SUBJ_INTENT_COMBO}\\s+` +
    `(?:got|gotten|carried|carrying|holding|bringing|made|making|built|` +
    `building|planted|planting|stashed|stashing|hidden|hiding)\\s+` +
    `(?:(?:a|an|the|my|some|several|multiple|loaded|live|real|another|two|three|` +
    `four|five|fully|semi|brand|new|fresh|powerful|deadly|big|huge|small|tiny|` +
    `working|functional|operational|\\d+)\\s+){0,5}` +
    WEAPON_NOUNS +
    `\\b`,
  "i"
);
const VERB_PERSON_THREAT_RE = new RegExp(
  "\\b(?:bomb|nuke|shoot|stab|kill|murder|rape|behead|decapitate|" +
    "strangle|drown|poison|gas|hang|lynch|string\\s+up|" +
    "massacre|slaughter|exterminate|eliminate|eradicate|destroy|" +
    "torture|mutilate)\\s+" +
    "(?:them|him|her|y'?all|you\\s+all|all\\s+of\\s+(?:you|them|us)|" +
    "those|these|everyone|every\\s+one\\s+of\\s+(?:them|us|you)|" +
    "(?:the|every|all|those|these|those\\s+filthy|all\\s+the|some)\\s+" +
    "(?:kids?|children|jews?|muslims?|christians?|hindus?|sikhs?|" +
    "buddhists?|gays?|lesbians?|trans|trannies|queers?|" +
    "blacks?|whites?|asians?|arabs?|latinos?|mexicans?|" +
    "immigrants?|refugees?|migrants?|" +
    "cops?|police|infidels?|kafirs?|gentiles?|goyim|" +
    "liberals?|conservatives?|democrats?|republicans?|" +
    "women|men|girls?|boys?|babies|infants?))\\b",
  "i"
);
const BODY_PART_ATTACK_RE = new RegExp(
  "\\b(?:break|snap|smash|crush|punch|crack|shatter|destroy)\\s+" +
    "(?:your|ur|his|her|their|my|the|that|this)\\s+" +
    "(?:bones?|neck|face|legs?|arms?|skull|jaw|teeth|throat|head|" +
    "spine|knees?|ribs?|nose|kneecaps?)\\b",
  "i"
);
const BULLET_THREAT_RE = new RegExp(
  "\\bput\\s+(?:a\\s+)?bullet(?:s)?\\s+(?:in|into|through|between)\\s+" +
    "(?:you|him|her|them|his|her|their|the|that)\\b",
  "i"
);
const WIPE_OUT_RE = new RegExp(
  "\\b(?:wipe\\s+out|exterminate|eliminate|eradicate|cleanse|purge)\\s+" +
    "(?:the|that|this|their|all|every|every\\s+single|those|these)\\s+" +
    "(?:village|town|city|tribe|race|nation|people|peoples|family|families|" +
    "community|communities|kids?|children|men|women|jews?|muslims?|" +
    "christians?|hindus?|gays?|blacks?|whites?|asians?|immigrants?)\\b",
  "i"
);
const ACTION_PLACE_RE = new RegExp(
  "\\b(?:bomb|nuke|burn\\s+down|torch|firebomb|blow\\s+up|shoot\\s+up|" +
    "attack|raid|destroy|massacre|storm|level)\\s+" +
    "(?:the|that|this|their|every|all|some)\\s+" +
    "(?:school|college|university|mall|church|mosque|synagogue|temple|" +
    "office|building|airport|station|store|shop|hospital|club|bar|" +
    "theater|theatre|cinema|stadium|arena|concert|festival|home|house|" +
    "apartment|crowd|class|classroom|street|neighborhood|neighbourhood|" +
    "town|city|village|place|venue|embassy|government|capitol|capital|" +
    "parliament|courthouse|police\\s+station)\\b",
  "i"
);

// --- Child Sexual Abuse Material (CSAM) detector — mirrors backend
// detect_minor_sexual_abuse(). NEVER relaxed under lyrics mode. ---
const ABUSE_VERBS =
  "(?:rape(?:d|s|r|rs)?|raping|" +
  "fuck(?:ed|ing|s|er|ers)?|fucken|fukn|" +
  "screw(?:ed|ing|s)?|" +
  "bang(?:ed|ing|s)?|bone(?:d|s)?|boning|" +
  "smash(?:ed|ing|es)?|" +
  "hump(?:ed|ing|s)?|" +
  "molest(?:ed|ing|s|er|ers)?|" +
  "abuse(?:d|s|r|rs)?|abusing|" +
  "grope(?:d|s|r|rs)?|groping|" +
  "finger(?:ed|ing|s)?|" +
  "diddle(?:d|s|r|rs)?|diddling|" +
  "violate(?:d|s|r|rs)?|violating|" +
  "assault(?:ed|ing|s)?|" +
  "have\\s+sex\\s+with|having\\s+sex\\s+with|had\\s+sex\\s+with|sex\\s+with|" +
  "sleep\\s+with|sleeping\\s+with|slept\\s+with|" +
  "hook\\s+up\\s+with|hooking\\s+up\\s+with|hooked\\s+up\\s+with|" +
  "date|dating|dated|" +
  "penetrate(?:d|s)?|penetrating|" +
  "go\\s+down\\s+on|going\\s+down\\s+on|went\\s+down\\s+on|" +
  "touch(?:ed|ing|es)?|" +
  "jerk\\s+off\\s+(?:to|with|on)|jerking\\s+off\\s+(?:to|with|on)|" +
  "masturbate\\s+(?:to|with)|masturbating\\s+(?:to|with)|" +
  "cum\\s+(?:on|in|with)|cumming\\s+(?:on|in|with))";

const MINOR_REF =
  "(?:kid(?:s|do|dos)?|kiddie(?:s)?|kiddo(?:s)?|" +
  "child|children|" +
  "minor(?:s)?|" +
  "toddler(?:s)?|infant(?:s)?|bab(?:y|ies)|newborn(?:s)?|" +
  "preteen(?:s)?|pre[\\s-]?teen(?:s)?|" +
  "underage(?:d)?|under[\\s-]?18|under\\s+eighteen|" +
  "(?:a\\s+)?\\d{1,2}[\\s-]?(?:yo|yr[\\s-]?old|year[\\s-]?old|y\\.o\\.)|" +
  "(?:little|small|tiny|baby|young|smol)\\s+(?:girl|boy|kid|child|one)s?|" +
  "little\\s+ones?|young\\s+ones?|" +
  "(?:school|grade|elementary|middle\\s+school|primary\\s+school|" +
  "kindergarten|nursery|daycare)\\s+(?:kid|child|girl|boy|student)s?|" +
  "(?:5|6|7|8|9|10|11|12|13|14|15)\\s+(?:yo|yr|year|y[\\.\\s]o))";

const DESIRE =
  "(?:i\\s+(?:like|love|want|wanna|enjoy|prefer|crave|need|gotta|" +
  "have\\s+to|wish\\s+to|dream\\s+about|fantasize\\s+about|" +
  "think\\s+about|get\\s+off\\s+(?:to|on)|jerk\\s+off\\s+to)\\s+" +
  "(?:to\\s+)?)";

const ARTICLE =
  "(?:(?:a|an|the|some|any|my|all|every|those|these|young|little|" +
  "small|tiny|innocent|cute|hot|pretty|fresh|brand[\\s-]new)\\s+){0,5}";

// Optional preposition between verb and minor referent — catches "rape TO
// kids", "fuck WITH children", "sex AT minors" where the user inserts an
// erroneous preposition. Mirrors backend _ABUSE_PREP.
const ABUSE_PREP =
  "(?:\\s+(?:to|with|on|at|of|into|onto|toward(?:s)?|against|" +
  "upon|over|around|near|among))?";

const MINOR_ABUSE_DIRECT_RE = new RegExp(
  `\\b${ABUSE_VERBS}${ABUSE_PREP}\\s+${ARTICLE}${MINOR_REF}\\b`,
  "i"
);
const MINOR_ABUSE_DESIRE_RE = new RegExp(
  `\\b${DESIRE}${ABUSE_VERBS}${ABUSE_PREP}\\s+${ARTICLE}${MINOR_REF}\\b`,
  "i"
);
const MINOR_ABUSE_ATTRACT_RE = new RegExp(
  `\\b(?:attracted\\s+to|aroused\\s+by|turned\\s+on\\s+by|` +
    `horny\\s+for|lust(?:ing|ful)?\\s+(?:for|after)|` +
    `obsessed\\s+with|crushing\\s+on|in\\s+love\\s+with|` +
    `want\\s+to\\s+touch|wanna\\s+touch|wanna\\s+see|` +
    `want\\s+nudes\\s+(?:from|of)|wanna\\s+see\\s+nudes\\s+of)\\s+` +
    `${ARTICLE}${MINOR_REF}\\b`,
  "i"
);
const MINOR_ABUSE_PREP_RE = new RegExp(
  `\\b(?:sex|sexual|sexually|intimate|romantic|romance)` +
    `(?:\\s+\\w+){0,3}\\s+` +
    `(?:with|of|around|involving|between|toward(?:s)?)\\s+` +
    `${ARTICLE}${MINOR_REF}\\b`,
  "i"
);

const detectMinorSexualAbuse = (norm) =>
  MINOR_ABUSE_DIRECT_RE.test(norm) ||
  MINOR_ABUSE_DESIRE_RE.test(norm) ||
  MINOR_ABUSE_ATTRACT_RE.test(norm) ||
  MINOR_ABUSE_PREP_RE.test(norm);

// --- Hard-blocked standalone terms (mirrors backend
// _HARD_BLOCKED_WORDS_RE). "rape" / "molest" and their inflections are
// categorically not allowed on Pluto in any context — including lyrics
// mode, survivor framings, news references. Word-boundary protected so
// "grape", "drape", "scraped", "rapeseed" do NOT match. ---
const HARD_BLOCKED_WORDS_RE = new RegExp(
  "\\b(?:rape(?:[ds]|rs?)?|raping|rapist(?:s)?|" +
    "molest(?:ed|ing|s|er|ers|ation|ations)?)\\b",
  "i"
);

const detectHardBlockedWords = (norm) => HARD_BLOCKED_WORDS_RE.test(norm);

const detectViolentIntent = (norm) =>
  INTENT_RE.test(norm) ||
  INTENT_COMBO_RE.test(norm) ||
  LETS_RE.test(norm) ||
  ADVOCACY_RE.test(norm) ||
  POSSESS_RE.test(norm) ||
  POSSESS_BARE_RE.test(norm) ||
  POSSESS_COMBO_RE.test(norm) ||
  VERB_PERSON_THREAT_RE.test(norm) ||
  BODY_PART_ATTACK_RE.test(norm) ||
  BULLET_THREAT_RE.test(norm) ||
  WIPE_OUT_RE.test(norm) ||
  ACTION_PLACE_RE.test(norm);

export const screenContent = (text) => {
  if (!text) return { ok: true };
  const norm = normalize(text);
  // 0) Hard-blocked standalone terms — categorical block on the exact
  //    words 'rape' / 'molest' (and inflections). Runs first so the
  //    user gets the precise reason rather than a generic threat msg.
  if (detectHardBlockedWords(norm)) {
    return {
      ok: false,
      reason:
        "Pluto doesn't allow the words 'rape' or 'molest' (or their variants) in any context. Please rewrite without these terms.",
      match: "hard-blocked-word",
    };
  }
  // 1) Highest-priority: child sexual abuse material (CSAM). Zero-tolerance,
  //    never relaxed under lyrics mode. Runs first so the message is accurate.
  if (detectMinorSexualAbuse(norm)) {
    return {
      ok: false,
      reason:
        "This post was blocked for sexual content involving minors (child sexual abuse material). This is a zero-tolerance violation.",
      match: "minor-sexual-abuse",
    };
  }
  // 1b) CSAM-specific phrase list (kiddie porn, Epstein-glorification,
  //     pedo-pride etc.) — also surfaces the zero-tolerance message.
  for (const phrase of CSAM_PHRASES) {
    if (norm.includes(phrase)) {
      return {
        ok: false,
        reason:
          "This post was blocked for sexual content involving minors (child sexual abuse material). This is a zero-tolerance violation.",
        match: phrase,
      };
    }
  }
  // 2) Generic phrase list (high-signal threats/hate/abuse verbatim)
  for (const phrase of PHRASES) {
    if (norm.includes(phrase)) {
      return {
        ok: false,
        reason:
          "This post looks like it contains threats, hate speech, or abusive language. Pluto doesn't allow this kind of content — please rewrite before posting.",
        match: phrase,
      };
    }
  }
  // 3) Context-aware violent intent (regex)
  if (detectViolentIntent(norm)) {
    return {
      ok: false,
      reason:
        "This post looks like a violent threat or call to harm. Pluto blocks content that targets people or places — please rewrite before posting.",
      match: "violent-intent",
    };
  }
  return { ok: true };
};
