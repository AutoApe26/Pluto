// Lightweight explicit content detector. Used to auto-tag posts/music
// captions whose body contains profanity, slurs, drug references, sexual
// content or other adult themes. Designed to favour FALSE POSITIVES on
// confession-style content (the product spec wants confession posts to
// be flagged unconditionally — see isExplicitPost).
//
// This is intentionally a curated regex list, not an LLM, so detection
// is instant and zero-cost. Words are matched with word boundaries to
// avoid scunthorpe-style false positives ("class" / "passion" / etc.).

const EXPLICIT_WORDS = [
  // profanity
  "fuck", "fucking", "fucked", "fucker", "motherfucker", "mf", "wtf",
  "shit", "shitty", "bullshit", "bs", "crap",
  "bitch", "bitches", "bitchy",
  "ass", "asses", "asshole", "assholes", "arse",
  "damn", "dammit", "goddamn",
  "bastard", "bastards",
  "piss", "pissed", "pissing",
  "dick", "dicks", "cock", "cocks", "prick",
  "pussy", "cunt", "twat",
  "slut", "whore", "hoe",
  // sexual / nsfw
  "porn", "porno", "nsfw", "sex", "sexy", "horny", "boobs", "tits",
  "nudes", "naked", "blowjob", "handjob", "orgasm", "masturbat",
  "onlyfans",
  // drugs
  "weed", "blunt", "high af", "stoned", "cocaine", "coke",
  "meth", "heroin", "shrooms", "molly", "lsd", "acid trip",
  // self-harm / dark (we flag, not block)
  "kill myself", "kms", "suicide", "self harm", "self-harm", "cutting myself",
  // slurs (mild — heavy slurs are blocked at the moderation layer)
  "retard", "retarded", "fag", "faggot",
];

// Pre-compile a single case-insensitive regex with word boundaries.
// Multi-word entries are split on whitespace and joined with \s+ so
// "kill myself" matches even if the user used multiple spaces.
const EXPLICIT_REGEX = (() => {
  const parts = EXPLICIT_WORDS.map((w) => {
    const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const withFlex = escaped.replace(/\s+/g, "\\s+");
    return `\\b${withFlex}\\b`;
  });
  return new RegExp(`(${parts.join("|")})`, "i");
})();

export const containsExplicit = (text) => {
  if (!text || typeof text !== "string") return false;
  return EXPLICIT_REGEX.test(text);
};

// Returns true if a post should display the "Explicit" tag. Confession
// posts are always flagged (per product spec); other topics are flagged
// only when explicit content is detected in the post body, lyrics flag
// is set, or backend has stamped is_explicit=true.
export const isExplicitPost = (post) => {
  if (!post) return false;
  if (post.is_explicit === true) return true;
  if (post.is_lyrics === true) return true;
  if (post.topic === "confession") return true;
  return containsExplicit(post.content || "");
};

// Music tracks — checks both caption and title since either can carry
// explicit content. is_lyrics already flags PA tracks, this catches
// the rest.
export const isExplicitTrack = (track) => {
  if (!track) return false;
  if (track.is_explicit === true) return true;
  if (track.is_lyrics === true) return true;
  return (
    containsExplicit(track.caption || "") ||
    containsExplicit(track.title || "")
  );
};
