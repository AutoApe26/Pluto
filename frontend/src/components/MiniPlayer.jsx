import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronUp, ChevronDown, X as XIcon, Music as MusicIcon } from "lucide-react";
import { useMusicPlayer } from "../lib/MusicPlayerContext";

// Re-implementing the embed URL helper locally so MiniPlayer doesn't
// have to import from MusicCard (avoids cyclic dependency once we wire
// things up).
const buildEmbedUrl = (track) => {
  if (!track?.link_url) return null;
  if (track.provider === "spotify") {
    return track.link_url.replace(
      /open\.spotify\.com\/(track|album|playlist|episode)\//,
      "open.spotify.com/embed/$1/"
    );
  }
  if (track.provider === "youtube") {
    let id = "";
    const m1 = track.link_url.match(/youtu\.be\/([\w-]+)/);
    const m2 = track.link_url.match(/[?&]v=([\w-]+)/);
    const m3 = track.link_url.match(/youtube\.com\/shorts\/([\w-]+)/);
    id = (m1 && m1[1]) || (m2 && m2[1]) || (m3 && m3[1]) || "";
    // autoplay=1 so playback starts the moment the iframe is mounted —
    // Spotify's embed auto-plays when navigated to /embed/... so we
    // get parity across providers.
    if (id) return `https://www.youtube.com/embed/${id}?autoplay=1`;
  }
  return null;
};

/**
 * Persistent mini music player. Mounted ONCE in the app shell so its
 * <iframe/> survives route changes — that's what gives us uninterrupted
 * audio while the user navigates between Home / Topics / Info / etc.
 *
 * Two states:
 *   - collapsed (default): thin pill at the bottom showing cover + title +
 *     expand/close buttons. The iframe stays mounted with display:none so
 *     audio keeps playing.
 *   - expanded: full embed visible above the pill (Spotify 152px /
 *     YouTube aspect-video) so the user can scrub, pause, etc.
 */
export const MiniPlayer = () => {
  const { track, stopPlayback } = useMusicPlayer();
  const [expanded, setExpanded] = useState(true);

  if (!track) return null;

  const embedUrl = buildEmbedUrl(track);
  const title = track.title || "Untitled track";
  const artist = track.artist || "";
  const cover = track.cover || track.thumbnail;

  // We park the mini player just above the mobile bottom nav (which
  // sits at bottom-3) and at the screen edge on desktop. Z-index 60
  // keeps it above feed content but below modals (z-[9999]).
  return (
    <AnimatePresence>
      <motion.div
        key="mini-player"
        initial={{ y: 80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 80, opacity: 0 }}
        transition={{ type: "spring", damping: 26, stiffness: 240 }}
        className="fixed left-1/2 -translate-x-1/2 z-50 w-[94%] max-w-2xl"
        style={{
          // Sit above the mobile floating bottom nav (bottom-3 + ~64px tall).
          // On desktop, sit at the bottom of the viewport with some breathing room.
          bottom: "calc(env(safe-area-inset-bottom, 0px) + 84px)",
        }}
        data-testid="mini-player"
      >
        <div className="glass-strong rounded-3xl border border-white/10 shadow-2xl shadow-purple-500/20 overflow-hidden">
          {/*
            Single, always-mounted iframe. We never unmount it on
            collapse — that would restart audio. Instead we animate the
            wrapper's height and toggle visibility/pointer-events with
            CSS. The iframe element identity stays stable across
            collapse, expand, AND route navigation.
          */}
          {embedUrl && (
            <motion.div
              key="embed"
              initial={false}
              animate={{
                height: expanded
                  ? track.provider === "youtube"
                    ? "auto"
                    : 152
                  : 0,
                opacity: expanded ? 1 : 0,
              }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden"
              data-testid="mini-player-embed"
              style={{
                // When collapsed, the height animates to 0 — but we keep
                // the iframe mounted; visibility:hidden suspends paint
                // without killing the media element.
                visibility: expanded ? "visible" : "hidden",
                pointerEvents: expanded ? "auto" : "none",
              }}
            >
              <iframe
                title={title}
                src={embedUrl}
                loading="lazy"
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                className={`w-full ${
                  track.provider === "youtube" ? "aspect-video" : "h-[152px]"
                }`}
                data-testid="mini-player-iframe"
              />
            </motion.div>
          )}

          {/* Pill bar */}
          <div className="flex items-center gap-3 px-3 py-2.5">
            <div className="relative shrink-0">
              {cover ? (
                <img
                  src={cover}
                  alt=""
                  className="w-11 h-11 rounded-xl object-cover border border-white/10"
                />
              ) : (
                <div className="w-11 h-11 rounded-xl bg-purple-500/20 border border-white/10 flex items-center justify-center">
                  <MusicIcon className="w-5 h-5 text-purple-200" />
                </div>
              )}
              {/* Equalizer-style "now playing" pulse dot */}
              <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-purple-400 ring-2 ring-[#0b0218] animate-pulse" />
            </div>

            <div className="flex-1 min-w-0">
              <div
                className="text-[13px] font-medium text-white truncate"
                data-testid="mini-player-title"
              >
                {title}
              </div>
              <div className="text-[11px] text-zinc-400 truncate font-mono">
                {artist ? `by ${artist}` : "now playing"}
                {track.provider && (
                  <span
                    className={`ml-2 px-1.5 py-[1px] rounded text-[9px] uppercase tracking-wider ${
                      track.provider === "spotify"
                        ? "bg-emerald-500/15 text-emerald-200"
                        : "bg-red-500/15 text-red-200"
                    }`}
                  >
                    {track.provider}
                  </span>
                )}
              </div>
            </div>

            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              data-testid="mini-player-toggle"
              aria-label={expanded ? "Collapse player" : "Expand player"}
              className="p-2 rounded-full text-zinc-300 hover:text-white hover:bg-white/5 transition"
            >
              {expanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronUp className="w-4 h-4" />
              )}
            </button>
            <button
              type="button"
              onClick={stopPlayback}
              data-testid="mini-player-close"
              aria-label="Stop playback"
              title="Stop playback"
              className="p-2 rounded-full text-zinc-300 hover:text-white hover:bg-red-500/20 transition"
            >
              <XIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default MiniPlayer;
