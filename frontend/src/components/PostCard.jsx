import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Heart, ThumbsDown, Share2, Languages, Loader2 } from "lucide-react";
import { TimeRemainingBadge } from "./TimeRemainingBadge";
import { ReportButton } from "./ReportButton";
import { ShareCardModal } from "./ShareCardModal";
import { relativeTime } from "../lib/format";
import { api } from "../lib/api";

const TOPIC_COLORS = {
  crypto: "#F7931A",
  sports: "#34C759",
  memes: "#FFCC00",
  "mental-health": "#FF6B9D",
  "tell-anything": "#00F0FF",
  rant: "#00F0FF",
  stories: "#B026FF",
  confession: "#FF3B30",
  music: "#7B61FF",
};

export const PostCard = ({ post, index = 0 }) => {
  const color = TOPIC_COLORS[post.topic] || "#00F0FF";
  const [hugs, setHugs] = useState(post.hugs ?? 0);
  const [fugs, setFugs] = useState(post.fugs ?? 0);
  const [myReaction, setMyReaction] = useState(null);
  const [busy, setBusy] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  // Translation state — only relevant if the post isn't already English.
  const isForeign = post.lang && post.lang !== "en";
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
      const res = await api.translatePost(post.id);
      const t = (res?.translation || "").trim();
      setTranslation(t || post.content);
      setShowTranslation(true);
    } catch (err) {
      setTranslateErr(true);
    } finally {
      setTranslating(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    api
      .myPostReaction(post.id)
      .then((r) => !cancelled && setMyReaction(r?.type ?? null))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [post.id]);

  const react = async (e, type) => {
    e.stopPropagation();
    if (busy) return;
    setBusy(true);
    // optimistic
    const prev = { hugs, fugs, myReaction };
    if (myReaction === type) {
      // toggle off
      if (type === "hug") setHugs((n) => Math.max(0, n - 1));
      else setFugs((n) => Math.max(0, n - 1));
      setMyReaction(null);
    } else if (myReaction && myReaction !== type) {
      // switch
      if (myReaction === "hug") setHugs((n) => Math.max(0, n - 1));
      else setFugs((n) => Math.max(0, n - 1));
      if (type === "hug") setHugs((n) => n + 1);
      else setFugs((n) => n + 1);
      setMyReaction(type);
    } else {
      // add
      if (type === "hug") setHugs((n) => n + 1);
      else setFugs((n) => n + 1);
      setMyReaction(type);
    }
    try {
      await api.reactPost(post.id, type);
    } catch (err) {
      // revert on error
      setHugs(prev.hugs);
      setFugs(prev.fugs);
      setMyReaction(prev.myReaction);
    } finally {
      setBusy(false);
    }
  };

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.4) }}
      data-testid={`post-card-${post.id}`}
      className="glass rounded-3xl p-5 sm:p-6 group hover:-translate-y-0.5 transition-all"
      style={{
        boxShadow: `0 1px 0 rgba(255,255,255,0.04) inset, 0 0 0 1px rgba(255,255,255,0.06)`,
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="text-[10px] px-2.5 py-1 rounded-full font-mono uppercase tracking-wider border"
            style={{
              color,
              borderColor: `${color}55`,
              background: `${color}10`,
            }}
            data-testid={`post-topic-${post.id}`}
          >
            #{post.topic}
          </span>
          <span className="text-xs text-zinc-500">
            {relativeTime(post.created_at)}
          </span>
        </div>
        <TimeRemainingBadge expiresAt={post.expires_at} />
      </div>

      <p className="text-[15px] sm:text-base leading-relaxed text-zinc-100 whitespace-pre-wrap break-words">
        {post.content}
      </p>

      {isForeign && (
        <div className="mt-2 flex flex-col gap-2">
          <button
            type="button"
            onClick={onTranslate}
            disabled={translating}
            data-testid={`translate-btn-${post.id}`}
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
              {post.lang}
            </span>
          </button>
          {translateErr && (
            <span className="text-[11px] text-rose-300/80">
              Couldn't translate — try again in a sec.
            </span>
          )}
          {showTranslation && translation && (
            <div
              data-testid={`translation-${post.id}`}
              className="rounded-2xl border border-purple-400/20 bg-purple-500/[0.06] px-3 py-2.5 text-[14px] sm:text-[15px] leading-relaxed text-zinc-100 whitespace-pre-wrap break-words"
            >
              <div className="text-[10px] font-mono uppercase tracking-wider text-purple-300/80 mb-1">
                English translation
              </div>
              {translation}
            </div>
          )}
        </div>
      )}

      {post.image ? (
        <div
          className="mt-4 rounded-2xl overflow-hidden border border-white/10 bg-black/40"
          data-testid={`post-image-${post.id}`}
        >
          <img
            src={post.image}
            alt=""
            loading="lazy"
            className="w-full max-h-[480px] object-cover"
          />
        </div>
      ) : null}

      {/* Reaction strip — Hug / Fug / Share */}
      <div className="mt-4 flex items-center gap-2 flex-wrap">
        <button
          type="button"
          disabled={busy}
          onClick={(e) => react(e, "hug")}
          data-testid={`hug-btn-${post.id}`}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono border transition active:scale-95 ${
            myReaction === "hug"
              ? "bg-pink-500/20 border-pink-400/60 text-pink-200 shadow-[0_0_18px_rgba(236,72,153,0.35)]"
              : "bg-pink-500/5 border-pink-500/25 text-pink-300 hover:bg-pink-500/10"
          }`}
        >
          <Heart
            className={`w-3.5 h-3.5 ${myReaction === "hug" ? "fill-current" : ""}`}
          />
          <span className="font-semibold">{hugs}</span>
          <span className="opacity-70 uppercase">Hug</span>
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={(e) => react(e, "fug")}
          data-testid={`fug-btn-${post.id}`}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono border transition active:scale-95 ${
            myReaction === "fug"
              ? "bg-zinc-700 border-zinc-500 text-zinc-100"
              : "bg-zinc-800/40 border-zinc-700/60 text-zinc-300 hover:bg-zinc-800/70"
          }`}
        >
          <ThumbsDown
            className={`w-3.5 h-3.5 ${myReaction === "fug" ? "fill-current" : ""}`}
          />
          <span className="font-semibold">{fugs}</span>
          <span className="opacity-70 uppercase">Fug</span>
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setShareOpen(true);
          }}
          data-testid={`share-btn-${post.id}`}
          className="ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono border bg-white/[0.04] border-white/15 text-zinc-300 hover:text-white hover:border-purple-400/40 hover:bg-purple-500/10 transition active:scale-95"
          title="Share as pluck card"
        >
          <Share2 className="w-3.5 h-3.5" />
          <span className="uppercase">Share</span>
        </button>
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-zinc-500">
        <span className="font-mono">
          {post.sudo_name ? (
            <span className="text-zinc-300">{post.sudo_name}</span>
          ) : (
            <>anon · {post.device_id.slice(-6)}</>
          )}
        </span>
        <ReportButton targetType="post" targetId={post.id} />
      </div>

      <ShareCardModal
        open={shareOpen}
        onClose={() => setShareOpen(false)}
        post={{ ...post, hugs, fugs }}
      />
    </motion.article>
  );
};

export default PostCard;
