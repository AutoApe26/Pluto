import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Music, Link2, Upload, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";

const detectProvider = (url) => {
  const u = url.toLowerCase();
  if (u.includes("spotify.com") || u.includes("spotify:")) return "spotify";
  if (u.includes("youtube.com") || u.includes("youtu.be")) return "youtube";
  return null;
};

// Fetch oEmbed metadata client-side (CORS-allowed for both providers)
async function fetchOEmbed(url) {
  const provider = detectProvider(url);
  if (!provider) return null;
  const endpoint =
    provider === "spotify"
      ? `https://open.spotify.com/oembed?url=${encodeURIComponent(url)}`
      : `https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`;
  try {
    const r = await fetch(endpoint);
    if (!r.ok) return { provider };
    const j = await r.json();
    return {
      provider,
      title: j.title || "",
      artist: j.author_name || "",
      thumbnail: j.thumbnail_url || null,
    };
  } catch {
    return { provider };
  }
}

export const UploadMusicModal = ({ open, onClose, onCreated }) => {
  const [link, setLink] = useState("");
  const [meta, setMeta] = useState(null);
  const [resolving, setResolving] = useState(false);
  const [caption, setCaption] = useState("");
  const [isLyrics, setIsLyrics] = useState(false);
  const [sudoName, setSudoName] = useState("");
  const [tags, setTags] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setLink("");
      setMeta(null);
      setCaption("");
      setIsLyrics(false);
      setSudoName("");
      setTags("");
    }
  }, [open]);

  // Debounced metadata fetch when link changes
  useEffect(() => {
    if (!link) {
      setMeta(null);
      return;
    }
    const provider = detectProvider(link);
    if (!provider) {
      setMeta(null);
      return;
    }
    const id = setTimeout(async () => {
      setResolving(true);
      const m = await fetchOEmbed(link);
      setMeta(m);
      setResolving(false);
    }, 600);
    return () => clearTimeout(id);
  }, [link]);

  const submit = async () => {
    const provider = detectProvider(link);
    if (!provider) {
      toast.error("Paste a Spotify or YouTube link");
      return;
    }
    setBusy(true);
    try {
      const tagList = tags
        .split(/[, ]+/)
        .map((t) => t.replace("#", "").trim())
        .filter(Boolean);
      const t = await api.uploadMusic({
        link_url: link.trim(),
        provider,
        title: meta?.title || "",
        artist: meta?.artist || "",
        thumbnail: meta?.thumbnail || null,
        caption,
        is_lyrics: isLyrics,
        sudo_name: sudoName.trim() || null,
        tags: tagList,
      });
      toast.success("Track dropped underground");
      onCreated?.(t);
      onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const provider = detectProvider(link);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          data-testid="upload-music-modal"
        >
          <div
            className="absolute inset-0 bg-black/75 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 30, opacity: 0 }}
            transition={{ type: "spring", damping: 26, stiffness: 240 }}
            className="relative w-full sm:max-w-lg glass-strong rounded-t-3xl sm:rounded-3xl p-5 sm:p-7 m-0 sm:m-4 border border-white/10 max-h-[94vh] overflow-y-auto"
          >
            <div className="flex items-start justify-between mb-1">
              <div>
                <h2 className="font-display text-2xl">Drop your track</h2>
                <p className="text-sm text-zinc-400 mt-0.5 leading-relaxed">
                  Just paste a Spotify or YouTube link — we'll grab the rest.
                  Vanishes in 24 hours.
                </p>
              </div>
              <button
                onClick={onClose}
                data-testid="close-upload-music"
                className="p-2 rounded-full hover:bg-white/5 text-zinc-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Music link */}
            <div className="mt-5">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Music link
              </label>
              <div className="mt-2 relative">
                <Link2 className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500" />
                <input
                  value={link}
                  onChange={(e) => setLink(e.target.value)}
                  placeholder="https://open.spotify.com/track/... or https://youtu.be/..."
                  data-testid="music-link-input"
                  className="w-full bg-white/[0.03] border border-white/10 rounded-2xl pl-10 pr-12 py-3 focus:border-purple-400/60 focus:bg-white/[0.05] focus:outline-none transition text-sm"
                />
                {resolving && (
                  <Loader2 className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 animate-spin" />
                )}
                {provider && !resolving && (
                  <span
                    className={`absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono uppercase px-2 py-0.5 rounded-full border ${
                      provider === "spotify"
                        ? "border-emerald-400/40 text-emerald-300"
                        : "border-red-400/40 text-red-300"
                    }`}
                  >
                    {provider}
                  </span>
                )}
              </div>
              <p className="mt-1.5 text-[11px] text-zinc-500">
                Spotify track/album/playlist or YouTube video/short.
              </p>

              {/* Resolved preview */}
              {meta && (meta.title || meta.thumbnail) && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-2.5"
                  data-testid="music-link-preview"
                >
                  {meta.thumbnail ? (
                    <img
                      src={meta.thumbnail}
                      alt=""
                      className="w-14 h-14 rounded-xl object-cover"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-xl bg-white/5 flex items-center justify-center">
                      <Music className="w-5 h-5 text-zinc-400" />
                    </div>
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm truncate">
                      {meta.title || "Track preview"}
                    </p>
                    {meta.artist && (
                      <p className="text-xs text-zinc-400 truncate">
                        {meta.artist}
                      </p>
                    )}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Caption */}
            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Caption (optional)
              </label>
              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value.slice(0, 800))}
                rows={3}
                placeholder="Tell us about the track..."
                data-testid="music-caption-input"
                className="mt-2 w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-3 text-sm resize-none focus:border-purple-400/60 focus:outline-none transition"
              />
            </div>

            {/* I'm posting lyrics toggle */}
            <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.02] p-3.5">
              <div className="flex items-start gap-3">
                <button
                  onClick={() => setIsLyrics(!isLyrics)}
                  data-testid="music-lyrics-toggle"
                  role="switch"
                  aria-checked={isLyrics}
                  className={`shrink-0 mt-0.5 relative w-11 h-6 rounded-full transition-colors ${
                    isLyrics ? "bg-purple-500" : "bg-white/10"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                      isLyrics ? "translate-x-5" : ""
                    }`}
                  />
                </button>
                <div>
                  <p className="text-sm font-medium">I'm posting lyrics</p>
                  <p className="text-[11px] text-zinc-500 mt-0.5 leading-relaxed">
                    Turn this on if your caption contains song lyrics. Profanity,
                    slurs and dark themes are allowed when flagged as lyrics.
                    Leave off for normal captions.
                  </p>
                </div>
              </div>
            </div>

            {/* Sudo name */}
            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Sudo name (optional)
              </label>
              <input
                value={sudoName}
                maxLength={24}
                onChange={(e) => setSudoName(e.target.value)}
                placeholder="Pick a temporary name..."
                data-testid="music-sudo-name"
                className="mt-2 w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-2.5 text-sm focus:border-purple-400/60 focus:outline-none transition"
              />
            </div>

            {/* Tags */}
            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Tags (optional, comma separated)
              </label>
              <input
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="lofi, hyperpop, sad"
                data-testid="music-tags-input"
                className="mt-2 w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-2.5 text-sm focus:border-purple-400/60 focus:outline-none transition"
              />
            </div>

            <button
              onClick={submit}
              disabled={busy || !provider}
              data-testid="music-upload-submit"
              className="mt-5 w-full inline-flex items-center justify-center gap-2 rounded-full py-3.5 font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Upload className="w-4 h-4" />
              {busy ? "Dropping..." : "Drop track"}
            </button>
            <p className="mt-2 text-[10px] text-zinc-500 text-center font-mono">
              Same link can be shared up to 1×/3h.
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default UploadMusicModal;
