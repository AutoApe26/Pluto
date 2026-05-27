import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Play,
  Heart,
  ThumbsDown,
  ExternalLink,
  Music as MusicIcon,
  Languages,
  Loader2,
  Share2,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { ReportButton } from "./ReportButton";
import { TimeRemainingBadge } from "./TimeRemainingBadge";
import { ShareCardModal } from "./ShareCardModal";
import { ExplicitBadge } from "./ExplicitBadge";
import { isExplicitTrack } from "../lib/explicit";

const FALLBACK_COVERS = [
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/d0a9d09aec04baea11248d881ee3e510f44a976c4db80243bef23e8e7c42b8bb.png",
  "https://images.unsplash.com/photo-1774132221866-9e6c2275b700?crop=entropy&cs=srgb&fm=jpg&w=600&q=70",
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/c8cf273ab43d9cecad200f4ff4c2787881f84f1f2ed48ed02617d136a5174162.png",
];

// Convert a Spotify or YouTube link into an embed URL
const buildEmbedUrl = (track) => {
  if (!track.link_url) return null;
  if (track.provider === "spotify") {
    // open.spotify.com/track/ID -> open.spotify.com/embed/track/ID
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
    if (id) return `https://www.youtube.com/embed/${id}`;
  }
  return null;
};

export const MusicCard = ({ track, index = 0 }) => {
  const [hugs, setHugs] = useState(track.hugs || 0);
  const [fugs, setFugs] = useState(track.fugs || 0);
  const [my, setMy] = useState(null);
  const [showEmbed, setShowEmbed] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  // Caption translation state (Gemini 2.5 Flash, same as posts)
  const captionForeign =
    !!track.caption && track.lang && track.lang !== "en";
  const [translation, setTranslation] = useState(null);
  const [showTranslation, setShowTranslation] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [translateErr, setTranslateErr] = useState(false);

  const onTranslate = async (e) => {
    e.stopPropagation();
    if (translating) return;
    if (translation) {
      setShowTranslation((v) => !v);
      return;
    }
    setTranslating(true);
    setTranslateErr(false);
    try {
      const res = await api.translateMusic(track.id);
      const t = (res?.translation || "").trim();
      setTranslation(t || track.caption);
      setShowTranslation(true);
    } catch {
      setTranslateErr(true);
    } finally {
      setTranslating(false);
    }
  };

  const cover =
    track.thumbnail || FALLBACK_COVERS[index % FALLBACK_COVERS.length];
  const embedUrl = buildEmbedUrl(track);
  const displayName = track.sudo_name || `anon · ${track.device_id?.slice(-6)}`;

  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.myReaction(track.id).then((r) => setMy(r.type)).catch(() => {});
  }, [track.id]);

  // Sync server-side hugs/fugs (from MusicPage polling) into local state
  // so engagement-loop bumps actually appear without a refresh.
  useEffect(() => {
    if (busy) return;
    const inc = track.hugs ?? 0;
    if (inc >= hugs) setHugs(inc);
  }, [track.hugs, busy]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (busy) return;
    const inc = track.fugs ?? 0;
    if (inc >= fugs) setFugs(inc);
  }, [track.fugs, busy]); // eslint-disable-line react-hooks/exhaustive-deps

  const react = async (type) => {
    if (busy) return;
    setBusy(true);
    try {
      const res = await api.reactMusic(track.id, type);
      if (res.action === "added") {
        if (type === "hug") setHugs((v) => v + 1);
        else setFugs((v) => v + 1);
        setMy(type);
      } else if (res.action === "removed") {
        if (type === "hug") setHugs((v) => v - 1);
        else setFugs((v) => v - 1);
        setMy(null);
      } else if (res.action === "switched") {
        if (type === "hug") {
          setHugs((v) => v + 1);
          setFugs((v) => v - 1);
        } else {
          setFugs((v) => v + 1);
          setHugs((v) => v - 1);
        }
        setMy(type);
      }
    } catch {
      toast.error("Reaction failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: Math.min(index * 0.05, 0.5) }}
      className="glass rounded-3xl p-4 sm:p-5"
      data-testid={`music-card-${track.id}`}
    >
      <div className="flex gap-4">
        <div className="relative shrink-0">
          <img
            src={cover}
            alt=""
            className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl object-cover border border-white/10"
            onError={(e) => {
              e.currentTarget.src = FALLBACK_COVERS[0];
            }}
          />
          <div className="absolute top-1.5 left-1.5">
            <span
              className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded-full ${
                track.provider === "spotify"
                  ? "bg-emerald-500/20 text-emerald-200 border border-emerald-400/40"
                  : "bg-red-500/20 text-red-200 border border-red-400/40"
              }`}
            >
              {track.provider}
            </span>
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 text-zinc-300">
                <MusicIcon className="w-3.5 h-3.5 shrink-0" />
                <h3
                  className="font-display text-base sm:text-lg truncate"
                  data-testid={`music-title-${track.id}`}
                >
                  {track.title || "Untitled track"}
                </h3>
              </div>
              {track.artist && (
                <p className="text-sm text-zinc-400 truncate mt-0.5">
                  by <span className="text-white/80">{track.artist}</span>
                </p>
              )}
              <p className="text-[10px] text-zinc-500 font-mono mt-0.5">
                drop by {displayName}
              </p>
            </div>
            <TimeRemainingBadge expiresAt={track.expires_at} />
          </div>

          {track.caption && (
            <p
              className={`mt-2 text-sm leading-snug line-clamp-3 ${
                track.is_lyrics ? "italic text-purple-200/80" : "text-zinc-400"
              }`}
            >
              {track.is_lyrics ? "♫ " : ""}
              {track.caption}
            </p>
          )}

          {track.is_lyrics && (
            <div
              data-testid={`music-lyrics-badge-${track.id}`}
              className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-black border border-white/40 text-[10px] font-mono uppercase tracking-widest text-white"
              title="This track caption contains explicit lyrics."
            >
              <span className="px-1 py-[1px] bg-white text-black font-bold">PA</span>
              Parental Advisory · Explicit
            </div>
          )}

          {/* Auto-flagged explicit content (profanity / sexual / drugs).
              Renders alongside (or instead of) the PA Lyrics badge. */}
          {!track.is_lyrics && isExplicitTrack(track) && (
            <div className="mt-2">
              <ExplicitBadge testId={`music-explicit-${track.id}`} />
            </div>
          )}

          {captionForeign && (
            <div className="mt-2 flex flex-col gap-2">
              <button
                type="button"
                onClick={onTranslate}
                disabled={translating}
                data-testid={`translate-music-btn-${track.id}`}
                className="inline-flex items-center gap-1.5 self-start text-[11px] font-mono uppercase tracking-wider text-zinc-400 hover:text-purple-300 transition disabled:opacity-60"
              >
                {translating ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Languages className="w-3 h-3" />
                )}
                {translating
                  ? "translating…"
                  : translation
                    ? showTranslation
                      ? "hide translation"
                      : "show translation"
                    : "see translation"}
                <span className="px-1.5 py-0.5 rounded-full bg-white/[0.05] border border-white/10 text-[9px] text-zinc-300">
                  {track.lang}
                </span>
              </button>
              {translateErr && (
                <span className="text-[11px] text-rose-300/80">
                  Couldn't translate — try again in a sec.
                </span>
              )}
              {showTranslation && translation && (
                <div
                  data-testid={`music-translation-${track.id}`}
                  className="rounded-2xl border border-purple-400/20 bg-purple-500/[0.06] px-3 py-2 text-[13px] leading-relaxed text-zinc-100 whitespace-pre-wrap break-words"
                >
                  <div className="text-[10px] font-mono uppercase tracking-wider text-purple-300/80 mb-1">
                    English translation
                  </div>
                  {translation}
                </div>
              )}
            </div>
          )}

          {track.tags?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {track.tags.map((t) => (
                <span
                  key={t}
                  className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-zinc-300 border border-white/10"
                >
                  #{t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Play button + embed */}
      <div className="mt-4">
        {showEmbed && embedUrl ? (
          <div
            className="rounded-2xl overflow-hidden border border-white/10"
            data-testid={`embed-${track.id}`}
          >
            <iframe
              src={embedUrl}
              title={track.title || "track"}
              loading="lazy"
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              className={`w-full ${track.provider === "youtube" ? "aspect-video" : "h-[152px]"}`}
            />
          </div>
        ) : (
          <button
            onClick={() => setShowEmbed(true)}
            data-testid={`play-${track.id}`}
            className="w-full inline-flex items-center justify-center gap-2 rounded-full py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:opacity-95 transition shadow-lg shadow-purple-500/20"
          >
            <Play className="w-4 h-4 fill-white" />
            Play
          </button>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => react("hug")}
            data-testid={`hug-${track.id}`}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border text-sm transition-all ${
              my === "hug"
                ? "bg-pink-500/20 border-pink-400/50 text-pink-200"
                : "border-white/10 text-zinc-300 hover:border-pink-400/40 hover:text-pink-200"
            }`}
          >
            <Heart
              className={`w-4 h-4 ${my === "hug" ? "fill-pink-300" : ""}`}
            />
            <span className="font-mono">{hugs}</span>
            <span className="text-[10px] uppercase tracking-wider opacity-70">
              HUG
            </span>
          </button>
          <button
            onClick={() => react("fug")}
            data-testid={`fug-${track.id}`}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border text-sm transition-all ${
              my === "fug"
                ? "bg-zinc-700/60 border-zinc-500/60 text-zinc-100"
                : "border-white/10 text-zinc-400 hover:border-zinc-400 hover:text-zinc-100"
            }`}
          >
            <ThumbsDown
              className={`w-4 h-4 ${my === "fug" ? "fill-zinc-300" : ""}`}
            />
            <span className="font-mono">{fugs}</span>
            <span className="text-[10px] uppercase tracking-wider opacity-70">
              FUG
            </span>
          </button>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setShareOpen(true);
            }}
            data-testid={`music-share-btn-${track.id}`}
            title="Share as Pluto pluck card"
            className="inline-flex items-center gap-1 text-xs text-zinc-300 hover:text-white px-2.5 py-1 rounded-full border border-white/10 hover:border-purple-400/40 hover:bg-purple-500/10 transition active:scale-95"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span className="font-mono uppercase tracking-wider">Share</span>
          </button>
          {track.provider !== "youtube" && track.link_url && (
            <a
              href={track.link_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-white px-2 py-1 rounded-full"
              data-testid={`open-${track.id}`}
              title="Open original"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <ReportButton targetType="music" targetId={track.id} />
        </div>
      </div>

      <ShareCardModal
        open={shareOpen}
        onClose={() => setShareOpen(false)}
        track={{ ...track, hugs, fugs, cover }}
      />
    </motion.div>
  );
};

export default MusicCard;
