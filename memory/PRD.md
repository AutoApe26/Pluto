# Pluto — Product Requirement Document

## Original Problem Statement
Build a modern mobile-first anonymous social app called **Pluto** for the **$PNF ecosystem**.
Dark futuristic UI with premium Gen Z aesthetic. Black/graphite + neon blue + purple, glassmorphism, rounded-3xl cards, glow effects, smooth animations, cosmic visuals, floating bottom nav.
Core: anonymous posting auto-deletes after 24h, topic feeds, image uploads, music section with Hug/Fug reactions, report system, hidden moderation page.
Taglines: *"Post it. Let it vanish."* · *"Where lost thoughts land."*

## Architecture
- **Stack**: React 19 + Tailwind + React Router + Framer Motion + FastAPI + MongoDB
- **Database substitution**: User asked for Supabase but environment has MongoDB only. Implemented all schema requirements in MongoDB collections (functionally equivalent).
- **File storage**: Images & audio stored as base64 data URLs in Mongo documents (simple, no S3 setup).
- **Anonymous identity**: `device_id` generated client-side and persisted in `localStorage` (`pluto.device_id`).

## Collections
- `posts` — id, content, topic, image, device_id, created_at, expires_at (24h), report_count, hidden
- `music_posts` — id, artist, title, caption, audio, cover, tags, device_id, hugs, fugs, created_at, report_count, hidden
- `music_reactions` — unique compound index `(music_id, device_id)` for one reaction per device
- `reports` — unique compound index `(target_type, target_id, device_id)` for one report per device
- Topics seeded in code (8 topics)

## API (all under `/api`)
- `GET /topics` · `GET /posts[?topic=]` · `GET /posts/trending` · `POST /posts` · `DELETE /posts/{id}` (own)
- `GET /music` · `GET /music/featured` · `POST /music` · `POST /music/{id}/reaction` · `GET /music/{id}/my-reaction`
- `POST /reports` (auto-hide after 3)
- `GET /mod/reported` · `POST /mod/{type}/{id}/delete` · `POST /mod/{type}/{id}/safe` (header `X-Mod-Key`)

## Pages
- `/` Landing (hero, trending preview, featured tracks, CTA)
- `/feed` Anonymous feed with topic filters
- `/music` Underground music room with audio player
- `/mod-station` Hidden moderation dashboard (key-gated)

## Implementation Status (2026-02-08)
- [x] Backend MongoDB schema + indexes + 24h cleanup
- [x] Spam protection (10 posts/h, 5 music/h per device)
- [x] All 8 topics + filter pills
- [x] Create post + image upload (4MB max)
- [x] Music upload + audio (8MB) + cover + tags
- [x] Hug/Fug toggle + switch with unique per device
- [x] Report system + auto-hide threshold = 3
- [x] Mod page with X-Mod-Key gate
- [x] Mobile floating bottom nav + top header
- [x] Glassmorphic dark UI + framer-motion animations
- [x] Tested via testing_agent_v3 — 100% backend, 100% frontend pass

## Backlog (P1)
- TTL index on `posts.expires_at` for native expiry
- Infinite scroll pagination (currently single page of 50)
- $PNF wallet connect for token-gated features (e.g., leaderboard)
- Optional content warning labels on Confession/Mental Health
- Music playlist persistence across pages

## Backlog (P2)
- Real-time updates via WebSockets
- Push notifications for replies (if added)
- AI moderation pre-screen
- Server-side image compression & object storage migration
