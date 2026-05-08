import React from "react";
import { motion } from "framer-motion";
import { TimeRemainingBadge } from "./TimeRemainingBadge";
import { ReportButton } from "./ReportButton";
import { relativeTime } from "../lib/format";

const TOPIC_COLORS = {
  crypto: "#F7931A",
  sports: "#34C759",
  memes: "#FFCC00",
  "mental-health": "#FF6B9D",
  "tell-anything": "#00F0FF",
  stories: "#B026FF",
  confession: "#FF3B30",
  music: "#7B61FF",
};

export const PostCard = ({ post, index = 0 }) => {
  const color = TOPIC_COLORS[post.topic] || "#00F0FF";
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
          {post.is_bot && (
            <span
              className="text-[9px] px-1.5 py-0.5 rounded-full font-mono uppercase tracking-wider border border-cyan-400/40 text-cyan-300 bg-cyan-300/5"
              title={post.source ? `Auto-feed · ${post.source}` : "Auto-feed"}
              data-testid={`post-bot-badge-${post.id}`}
            >
              · bot
            </span>
          )}
          <span className="text-xs text-zinc-500">
            {relativeTime(post.created_at)}
          </span>
        </div>
        <TimeRemainingBadge expiresAt={post.expires_at} />
      </div>

      <p className="text-[15px] sm:text-base leading-relaxed text-zinc-100 whitespace-pre-wrap break-words">
        {post.content}
      </p>

      {post.image && (
        <div className="mt-4 rounded-2xl overflow-hidden border border-white/5">
          <img
            src={post.image}
            alt=""
            className="w-full max-h-[60vh] object-cover"
            loading="lazy"
          />
        </div>
      )}

      <div className="mt-4 flex items-center justify-between text-xs text-zinc-500">
        <span className="font-mono">
          {post.sudo_name ? (
            <>
              <span className="text-zinc-300">{post.sudo_name}</span>
              <span className="text-zinc-600 ml-1">· anon</span>
            </>
          ) : (
            <>anon · {post.device_id.slice(-6)}</>
          )}
        </span>
        <ReportButton targetType="post" targetId={post.id} />
      </div>
    </motion.article>
  );
};

export default PostCard;
