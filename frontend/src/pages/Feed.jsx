import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Inbox } from "lucide-react";
import { api } from "../lib/api";
import { CosmicBg } from "../components/CosmicBg";
import { PostCard } from "../components/PostCard";

export const Feed = ({ topics }) => {
  const [active, setActive] = useState("all");
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async (t) => {
    setLoading(true);
    try {
      const data = await api.posts(t);
      setPosts(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(active);
  }, [active]);

  return (
    <div className="relative" data-testid="feed-page">
      <CosmicBg />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-6 pb-32">
        <div className="mb-5">
          <p className="text-[10px] uppercase tracking-[0.3em] text-cyan-300 font-mono">
            Browse all topics
          </p>
          <h1 className="font-display text-3xl sm:text-4xl mt-1">
            Topics
          </h1>
          <p className="mt-1 text-sm text-zinc-500">
            Anonymous whispers across 8 topics. Every post auto-vanishes in 24h.
          </p>
        </div>

        {/* Topic filters */}
        <div
          className="flex gap-2 overflow-x-auto no-scrollbar pb-3 -mx-4 px-4"
          data-testid="topic-filter-row"
        >
          {[{ slug: "all", name: "All", color: "#FFFFFF" }, ...topics].map(
            (t) => {
              const isActive = active === t.slug;
              return (
                <button
                  key={t.slug}
                  onClick={() => setActive(t.slug)}
                  data-testid={`topic-filter-${t.slug}`}
                  className={`shrink-0 px-4 py-1.5 rounded-full text-sm border transition-all ${
                    isActive
                      ? "bg-white/10 text-white"
                      : "border-white/10 text-zinc-400 hover:text-white hover:border-white/25"
                  }`}
                  style={
                    isActive
                      ? {
                          borderColor: `${t.color}80`,
                          color: t.color,
                          boxShadow: `0 0 18px ${t.color}30`,
                        }
                      : {}
                  }
                >
                  {t.slug === "all" ? "All" : `#${t.name}`}
                </button>
              );
            }
          )}
        </div>

        {/* Posts list */}
        <div className="mt-6 space-y-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
              <Loader2 className="w-6 h-6 animate-spin" />
              <p className="mt-3 text-sm font-mono">summoning whispers...</p>
            </div>
          ) : posts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass rounded-3xl p-10 text-center"
              data-testid="empty-feed"
            >
              <Inbox className="w-10 h-10 mx-auto text-zinc-600" />
              <h3 className="mt-4 font-display text-xl">It's quiet here</h3>
              <p className="mt-2 text-sm text-zinc-500">
                Be the first to drop a thought into the void.
              </p>
            </motion.div>
          ) : (
            posts.map((p, i) => <PostCard key={p.id} post={p} index={i} />)
          )}
        </div>
      </div>
    </div>
  );
};

export default Feed;
