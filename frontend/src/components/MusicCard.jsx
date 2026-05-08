import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Play, Pause, Heart, ThumbsDown } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { ReportButton } from "./ReportButton";
import { relativeTime } from "../lib/format";

const FALLBACK_COVERS = [
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/d0a9d09aec04baea11248d881ee3e510f44a976c4db80243bef23e8e7c42b8bb.png",
  "https://images.unsplash.com/photo-1774132221866-9e6c2275b700?crop=entropy&cs=srgb&fm=jpg&w=600&q=70",
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/c8cf273ab43d9cecad200f4ff4c2787881f84f1f2ed48ed02617d136a5174162.png",
];

export const MusicCard = ({ track, index = 0, onPlay, isPlaying, audioRef }) => {
  const [hugs, setHugs] = useState(track.hugs);
  const [fugs, setFugs] = useState(track.fugs);
  const [my, setMy] = useState(null);
  const cover =
    track.cover || FALLBACK_COVERS[index % FALLBACK_COVERS.length];

  useEffect(() => {
    api.myReaction(track.id).then((r) => setMy(r.type)).catch(() => {});
  }, [track.id]);

  const react = async (type) => {
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
          />
          <button
            onClick={() => onPlay(track)}
            data-testid={`play-${track.id}`}
            className="absolute inset-0 flex items-center justify-center rounded-2xl bg-black/40 opacity-0 hover:opacity-100 transition-opacity"
          >
            <span className="w-12 h-12 rounded-full bg-cyan-300 text-black flex items-center justify-center glow-cyan">
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </span>
          </button>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3
                className="font-display text-base sm:text-lg truncate"
                data-testid={`music-title-${track.id}`}
              >
                {track.title}
              </h3>
              <p className="text-sm text-zinc-400 truncate">
                by <span className="text-white/80">{track.artist}</span>
              </p>
            </div>
            <span className="text-[10px] text-zinc-500 font-mono whitespace-nowrap">
              {relativeTime(track.created_at)}
            </span>
          </div>

          {track.caption && (
            <p className="mt-1 text-sm text-zinc-400 line-clamp-2">
              {track.caption}
            </p>
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

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => react("hug")}
            data-testid={`hug-${track.id}`}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border text-sm transition-all ${
              my === "hug"
                ? "bg-pink-500/20 border-pink-400/50 text-pink-200 glow-purple"
                : "border-white/10 text-zinc-300 hover:border-pink-400/40 hover:text-pink-200"
            }`}
          >
            <Heart
              className={`w-4 h-4 ${my === "hug" ? "fill-pink-300" : ""}`}
            />
            <span className="font-mono">{hugs}</span>
            <span className="text-[10px] uppercase tracking-wider opacity-70">
              hug
            </span>
          </button>
          <button
            onClick={() => react("fug")}
            data-testid={`fug-${track.id}`}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border text-sm transition-all ${
              my === "fug"
                ? "bg-zinc-700/50 border-zinc-500/60 text-zinc-100"
                : "border-white/10 text-zinc-400 hover:border-zinc-400 hover:text-zinc-100"
            }`}
          >
            <ThumbsDown
              className={`w-4 h-4 ${my === "fug" ? "fill-zinc-300" : ""}`}
            />
            <span className="font-mono">{fugs}</span>
            <span className="text-[10px] uppercase tracking-wider opacity-70">
              fug
            </span>
          </button>
        </div>
        <ReportButton targetType="music" targetId={track.id} />
      </div>
    </motion.div>
  );
};

export default MusicCard;
