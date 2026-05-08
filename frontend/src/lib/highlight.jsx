// Deterministic purple-keyword highlighter used by the home Trending list.
// Picks 2–3 stable spans of meaningful words from the post content and
// wraps them in a coloured <span>. Same input + seed always returns the
// same highlights so it doesn't flicker between renders.
import React from "react";

function seededRand(seed) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 15), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  };
}

export function highlightWords(text, seed = "x") {
  if (!text) return text;
  const tokens = text.split(/(\s+)/); // keep whitespace tokens
  const candidateIdx = [];
  tokens.forEach((tok, i) => {
    if (/^\s+$/.test(tok)) return;
    const clean = tok.replace(/[^A-Za-z0-9']/g, "");
    if (clean.length < 4) return;
    if (/^(this|that|with|from|have|been|they|their|there|about|just|like|will|over|into|when|then|some|than|what|here|were|while|because|which|where|after|before|without|every|never|more|most|less|even|also|only)$/i.test(clean)) return;
    candidateIdx.push(i);
  });
  if (candidateIdx.length === 0) return text;

  const rand = seededRand(seed);
  const targetCount = Math.min(3, Math.max(2, Math.floor(candidateIdx.length / 8) + 2));
  const chosen = new Set();
  let tries = 0;
  while (chosen.size < targetCount && tries < 50) {
    tries++;
    const idx = candidateIdx[Math.floor(rand() * candidateIdx.length)];
    // avoid overlap with existing picks (by 2 token positions)
    let ok = true;
    for (const c of chosen) if (Math.abs(c - idx) <= 2) ok = false;
    if (!ok) continue;
    chosen.add(idx);
    // 35% chance to extend to a 2-word phrase
    if (rand() < 0.35 && idx + 2 < tokens.length && /^\s+$/.test(tokens[idx + 1])) {
      const next = tokens[idx + 2];
      if (next && !/^\s+$/.test(next) && next.replace(/[^A-Za-z0-9']/g, "").length >= 3) {
        chosen.add(idx + 2);
      }
    }
  }

  return tokens.map((tok, i) =>
    chosen.has(i) ? (
      <span key={i} className="text-purple-300">
        {tok}
      </span>
    ) : (
      <React.Fragment key={i}>{tok}</React.Fragment>
    )
  );
}

export default highlightWords;
