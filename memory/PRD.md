# Pluto — Product Requirement Document

## Original Problem Statement
Build a modern mobile-first anonymous social app called **Pluto** for the **$PNF ecosystem**.
User uploaded a demo video and asked: *"I want the whole UI exact to this and all the features as attached in the video."*

## Architecture
- **Stack**: React 19 + Tailwind + React Router + Framer Motion + FastAPI + MongoDB
- **Database**: MongoDB (Supabase keys not provisioned). Schema fully implemented.
- **Anonymous identity**: `device_id` in `localStorage` (`pluto.device_id`)
- **Music storage strategy**: switched from base64 file uploads to **Spotify/YouTube link** sharing with client-side oEmbed metadata fetch + iframe embed playback.

## Pages
- `/` — Landing (centered Pluto sphere, $PNF tagline, list-style Trending, 2-col Trending Music grid)
- `/topics` — Topic-filtered anonymous feed (also `/feed` alias)
- `/music` — Music feed with iframe embeds + Hug/Fug
- `/info` — 4-card explainer page
- `/mod-station` — Hidden moderation dashboard (X-Mod-Key gated)

## Topics (8)
Crypto, Sports, Memes, Mental Health, **Rant**, Stories, Confession, Music

## API (under `/api`)
- `GET /topics` · `GET /posts[?topic=]` · `GET /posts/trending` · `POST /posts` (sudo_name, 1000-char limit) · `DELETE /posts/{id}`
- `GET /music` (cleanups expired) · `GET /music/featured` · `POST /music` (link_url + auto-detected provider + is_lyrics + sudo_name) · `POST /music/{id}/reaction` · `GET /music/{id}/my-reaction`
- `POST /reports` (auto-hide at 3) · Mod endpoints w/ X-Mod-Key header

## Implementation Status

### V1 (initial) — 2026-02-08
- [x] Backend MongoDB schema + 24h cleanup + spam protection
- [x] Anonymous post + image, music upload (file-based)
- [x] Hug/Fug, Reports + auto-hide, Mod page
- [x] Mobile floating bottom nav, glassmorphic dark UI

### V2 (video-match redesign) — 2026-02-08
- [x] Centered hero with Pluto sphere graphic + "A PAGE NOT FOUND $PNF PRODUCT"
- [x] Big gradient pluto logo, "Post it. Let it vanish." + sub-tagline
- [x] Dual CTA: "Post anonymously" (purple-pink) + "Discover music" (muted purple)
- [x] List-style trending rows with topic icons
- [x] Trending Music 2-col grid with Hug/Fug + time-remaining
- [x] Header: Home / Topics / Music / Info — Bottom nav: 5 items including Info
- [x] Topic rename: tell-anything → **Rant**
- [x] CreatePostModal: Sudo name (optional), 0/1000 counter, "Tap to add an image", content rules disclaimer
- [x] UploadMusicModal: switched to **link-based** (Spotify/YouTube oEmbed preview)
- [x] "I'm posting lyrics" toggle for caption profanity allowance
- [x] MusicCard with Spotify/YouTube iframe embed playback
- [x] New Info page with 4 cards (What is Pluto? / Hug or Fug / Anonymous, but not free-for-all / $PNF product)
- [x] Tested via testing_agent_v3 → **100% backend (21/21) / 100% frontend pass**

### V3 (Pluto UI polish + music chatter) — 2026-02-27
- [x] Pluto logo scroll-shine animation (useScrollShine hook + .pluto-logo-shining class + diagonal shimmer sweep) on Logo & PlutoSphere
- [x] Trending feed re-sorted by topic priority: **Crypto → Music → Mental Health → Confession**, then others (Landing.jsx)
- [x] TopicsGrid card order updated to match priority
- [x] ShareCardModal redesigned as responsive **bottom sheet**: scrollable preview/copy-link body + sticky bottom action bar with horizontally scrollable social icons (X, Instagram, TikTok, Facebook, More). Removed old vertical "Share to…" dropdown.
- [x] CreatePostModal refactored: flex-column with overflow-y body + sticky submit bar; safe-area-inset-bottom; mobile drag handle; sticky header.
- [x] Music: YouTube external "Open original" link removed (Spotify external link preserved).
- [x] Music bots now post **trending music news, artist updates, lyric snippets, and viral discussion prompts** to the #music topic via curated rotating templates (`_post_music_chatter` in bot_service.py). Each chatter post seeds believable hugs/fugs and is bumped by the engagement loop.
- [x] Added "music" subreddits to TOPIC_SOURCES so #music also pulls real Reddit content alongside chatter.
- [x] Tested via testing_agent_v3_fork → **100% backend (26/26) / 100% frontend pass**

## Backlog (P1)
- TTL index on `posts.expires_at` and `music_posts.expires_at` for native expiry
- Infinite scroll pagination
- Music link dedup (same URL only once per N hours)
- Server-side oEmbed fallback if client CORS fails
- Topics page → grid of topic cards landing pattern (currently uses pill filter)

## Backlog (P2)
- $PNF wallet connect for token-gated leaderboard
- Real-time updates (WebSockets / SSE)
- AI moderation pre-screen
- Push notifications
