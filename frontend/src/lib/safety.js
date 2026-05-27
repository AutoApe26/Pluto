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
  "kill all jews", "kill all muslims", "kill all blacks", "kill all whites",
  "gas the jews", "race war now", "white power", "white pride",
  "heil hitler", "sieg heil",
  // terror / mass violence
  "shoot up a school", "shoot up the school", "shoot up the mall",
  "shoot up the office", "shoot up this", "shoot up that",
  "make a bomb", "build a bomb", "build a pipe bomb", "pipe bomb",
  "how to make a bomb", "homemade bomb", "ied tutorial",
  "explosive vest", "suicide vest", "improvised explosive",
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

// Cheap normalizer that mirrors backend's `_collapse` semantics enough
// for the unambiguous phrases above. Lowercase + collapse whitespace.
const normalize = (text) => (text || "").toLowerCase().replace(/\s+/g, " ").trim();

export const screenContent = (text) => {
  if (!text) return { ok: true };
  const norm = normalize(text);
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
  return { ok: true };
};
