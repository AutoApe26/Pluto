import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Send,
  Headphones,
  ChevronRight,
  Bitcoin,
  Trophy,
  Laugh,
  HeartPulse,
  Zap,
  BookOpen,
  Eye,
  Music as MusicIcon,
  Play,
  Heart,
  ThumbsDown,
  MoreHorizontal,
} from "lucide-react";
import { CosmicBg } from "../components/CosmicBg";
import { PlutoSphere } from "../components/Logo";
import { TimeRemainingBadge } from "../components/TimeRemainingBadge";
import { TopicsGrid } from "../components/TopicsGrid";
import { api } from "../lib/api";
import { timeRemaining } from "../lib/format";

const FALLBACK_COVERS = [
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/d0a9d09aec04baea11248d881ee3e510f44a976c4db80243bef23e8e7c42b8bb.png",
  "https://images.unsplash.com/photo-1774132221866-9e6c2275b700?crop=entropy&cs=srgb&fm=jpg&w=600&q=70",
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/c8cf273ab43d9cecad200f4ff4c2787881f84f1f2ed48ed02617d136a5174162.png",
];

const TOPIC_ICONS = {
  crypto: Bitcoin,
  sports: Trophy,
  memes: Laugh,
  "mental-health": HeartPulse,
  rant: Zap,
  stories: BookOpen,
  confession: Eye,
  music: MusicIcon,
};
const TOPIC_COLORS = {
  crypto: "#F7931A",
  sports: "#34C759",
  memes: "#FFCC00",
  "mental-health": "#FF6B9D",
  rant: "#00F0FF",
  stories: "#B026FF",
  confession: "#FF3B30",
  music: "#7B61FF",
};
const TOPIC_LABEL = {
  crypto: "Crypto",
  sports: "Sports",
  memes: "Memes",
  "mental-health": "Mental Health",
  rant: "Rant",
  stories: "Stories",
  confession: "Confession",
  music: "Music",
};

const FALLBACK_POSTS = [
  { id: "f1", topic: "crypto", content: "anyone else feel like the market is just vibes at this point?" },
  { id: "f2", topic: "sports", content: "watched my team blow a 3-0 lead. i'm done with sports." },
  { id: "f3", topic: "memes", content: "this is the funniest meme of the year and you can't change my mind" },
  { id: "f4", topic: "mental-health", content: "therapist said i'm doing great. lol." },
  { id: "f5", topic: "rant", content: "my neighbor plays the SAME song on loop. send help." },
  { id: "f6", topic: "stories", content: "got stuck in an elevator with my crush for 40 minutes." },
  { id: "f7", topic: "confession", content: "told my crush I love them. ghosted. RIP me." },
  { id: "f8", topic: "music", content: "midnight playlists hit different in winter." },
];

// Deterministic key-phrase highlighter — picks 2–3 longer words (or 2-word phrases)
// from the content and wraps them in a purple span. Stable for the same input.
const STOP_WORDS = new Set([
  "the","and","for","with","from","that","this","they","them","their","there",
  "have","has","had","but","not","you","your","are","was","were","will","would",
  "could","should","just","like","than","then","what","when","where","which",
  "into","over","also","after","before","about","again","still","some","such",
  "very","much","more","most","only","even","being","because","while","since",
  "every","always","never","often","really","actually","anyone","everyone",
  "something","anything","nothing","someone","another","other","these","those",
]);

const highlightContent = (content, color) => {
  if (!content) return null;
  const words = content.split(/(\s+)/); // keep whitespace tokens
  // candidates: meaningful words length >= 5, not stopwords
  const candidates = [];
  words.forEach((w, idx) => {
    const clean = w.toLowerCase().replace(/[^a-z0-9']/g, "");
    if (clean.length >= 5 && !STOP_WORDS.has(clean)) {
      candidates.push({ idx, score: clean.length + (clean.length > 7 ? 3 : 0) });
    }
  });
  // deterministic pick: top by score, evenly spaced
  candidates.sort((a, b) => b.score - a.score);
  const picked = new Set(candidates.slice(0, 3).map((c) => c.idx));
  return words.map((w, idx) =>
    picked.has(idx) ? (
      <span key={idx} style={{ color, textShadow: `0 0 12px ${color}55` }}>
        {w}
      </span>
    ) : (
      <React.Fragment key={idx}>{w}</React.Fragment>
    )
  );
};

export const Landing = ({ onCreate }) => {
  const [trending, setTrending] = useState([]);
  const [music, setMusic] = useState([]);

  useEffect(() => {
    api.trendingPosts().then(setTrending).catch(() => {});
    api.featuredMusic().then(setMusic).catch(() => {});
  }, []);

  const trendList = (trending.length ? trending : FALLBACK_POSTS).slice(0, 8);

  return (
    <div className="relative" data-testid="landing-page">
      <CosmicBg />

      {/* HERO — centered with sphere */}
      <section className="relative max-w-3xl mx-auto px-5 sm:px-8 pt-10 sm:pt-16 pb-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="flex flex-col items-center"
        >
          {/* Sphere */}
          <PlutoSphere size={170} />

          {/* Tagline above logo */}
          <p className="mt-7 text-[10px] uppercase tracking-[0.4em] text-zinc-500 font-mono">
            a page not found · $pnf product
          </p>

          {/* Big logo */}
          <h1 className="font-display text-7xl sm:text-8xl mt-2 leading-none">
            <span
              className="bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  "linear-gradient(180deg, #ffffff 0%, #d2cbff 55%, #8a73ff 100%)",
                filter: "drop-shadow(0 0 24px rgba(176,38,255,0.25))",
              }}
            >
              pluto
            </span>
          </h1>

          {/* Tagline */}
          <p className="mt-4 text-zinc-300 text-base sm:text-lg">
            Post it. Let it vanish.
          </p>
          <p className="mt-1 text-sm text-zinc-500">
            Anonymous for 24 hours. Lost thoughts. Found here.
          </p>

          {/* CTAs */}
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={onCreate}
              data-testid="landing-cta-post"
              className="group inline-flex items-center gap-2 rounded-full px-5 py-3 font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-xl shadow-purple-500/30"
            >
              <Send className="w-4 h-4" />
              Post anonymously
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
            </button>
            <Link
              to="/music"
              data-testid="landing-cta-music"
              className="inline-flex items-center gap-2 rounded-full px-5 py-3 font-medium text-purple-100 bg-purple-900/50 border border-purple-500/30 hover:bg-purple-900/70 transition"
            >
              <Headphones className="w-4 h-4" />
              Discover music
            </Link>
          </div>
        </motion.div>
      </section>

      {/* TRENDING — large monospace cards */}
      <section className="max-w-3xl mx-auto px-5 sm:px-8 pb-12" data-testid="trending-section">
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="font-display text-4xl sm:text-5xl leading-none">Trending</h2>
            <p className="mt-2 text-[10px] uppercase tracking-[0.3em] text-zinc-500 font-mono">
              latest lost thoughts
            </p>
          </div>
          <Link
            to="/topics"
            className="text-sm text-purple-300 hover:text-purple-200 transition inline-flex items-center gap-1 font-mono"
            data-testid="trending-see-all"
          >
            See all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="space-y-4">
          {trendList.map((p, i) => {
            const Icon = TOPIC_ICONS[p.topic] || Eye;
            const color = TOPIC_COLORS[p.topic] || "#00F0FF";
            const label = TOPIC_LABEL[p.topic] || p.topic;
            return (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="group relative glass rounded-3xl px-5 sm:px-7 py-5 sm:py-6 hover:bg-white/[0.04] transition cursor-pointer border border-white/5 hover:border-white/10"
                data-testid={`trending-row-${p.id}`}
                onClick={() =>
                  (window.location.href = `/topics?topic=${p.topic}`)
                }
              >
                {/* Top row: category pill + arrow */}
                <div className="flex items-center justify-between gap-3">
                  <div
                    className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 border bg-black/30"
                    style={{
                      color,
                      borderColor: `${color}40`,
                    }}
                  >
                    <Icon className="w-3 h-3" />
                    <span className="text-[10px] font-mono uppercase tracking-wider">
                      {label}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {p.expires_at && (
                      <span className="hidden sm:inline-block">
                        <TimeRemainingBadge expiresAt={p.expires_at} />
                      </span>
                    )}
                    <ArrowRight className="w-4 h-4 text-zinc-500 group-hover:text-white group-hover:translate-x-0.5 transition" />
                  </div>
                </div>

                {/* Big monospace content with key-phrase highlights */}
                <p className="mt-4 sm:mt-5 font-mono text-white text-xl sm:text-3xl leading-snug tracking-tight whitespace-pre-wrap break-words">
                  {highlightContent(p.content, "#B026FF")}
                </p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* TRENDING MUSIC (2-col grid) */}
      <section
        className="max-w-3xl mx-auto px-5 sm:px-8 pb-16"
        data-testid="trending-music-section"
      >
        <div className="flex items-end justify-between mb-5">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-purple-300 font-mono">
              support underground artists
            </p>
            <h2 className="font-display text-3xl sm:text-4xl mt-1">
              Trending Music
            </h2>
          </div>
          <Link
            to="/music"
            className="text-sm text-zinc-400 hover:text-purple-200 transition inline-flex items-center gap-1"
            data-testid="music-see-all"
          >
            See all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {music.length === 0 ? (
          <div className="glass rounded-3xl p-8 text-center">
            <MusicIcon className="w-8 h-8 mx-auto text-zinc-600" />
            <p className="mt-3 text-sm text-zinc-400">
              No tracks yet. Be the first to drop one.
            </p>
            <Link
              to="/music"
              className="mt-3 inline-flex items-center gap-1.5 text-sm text-purple-300 hover:text-purple-200"
            >
              Drop a track <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {music.slice(0, 4).map((m, i) => {
              const cover =
                m.thumbnail || FALLBACK_COVERS[i % FALLBACK_COVERS.length];
              return (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.07 }}
                  className="glass rounded-3xl p-4 hover:-translate-y-0.5 transition-all"
                  data-testid={`landing-music-${m.id}`}
                >
                  <div className="flex gap-3">
                    <img
                      src={cover}
                      alt=""
                      className="w-16 h-16 rounded-2xl object-cover border border-white/10"
                      onError={(e) => (e.currentTarget.src = FALLBACK_COVERS[0])}
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-1">
                        <div className="min-w-0">
                          <div className="flex items-center gap-1 text-zinc-300">
                            <MusicIcon className="w-3 h-3 shrink-0" />
                            <h3 className="text-sm font-medium truncate">
                              {m.title || "Untitled"}
                            </h3>
                          </div>
                          {m.artist && (
                            <p className="text-xs text-zinc-500 truncate">
                              {m.artist}
                            </p>
                          )}
                        </div>
                        <button className="text-zinc-500 hover:text-white shrink-0">
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                      </div>
                      {m.caption && (
                        <p
                          className={`mt-1 text-[11px] line-clamp-2 ${
                            m.is_lyrics ? "italic text-purple-200/70" : "text-zinc-500"
                          }`}
                        >
                          {m.caption}
                        </p>
                      )}
                    </div>
                  </div>
                  <Link
                    to="/music"
                    className="mt-3 w-full inline-flex items-center justify-center gap-1.5 rounded-full py-2 text-xs font-medium text-white bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:opacity-95 transition"
                  >
                    <Play className="w-3 h-3 fill-white" /> Play
                  </Link>
                  <div className="mt-2.5 flex items-center justify-between text-[10px] font-mono text-zinc-500">
                    <div className="flex items-center gap-2.5">
                      <span className="inline-flex items-center gap-1 text-pink-300">
                        <Heart className="w-3 h-3" />
                        {m.hugs} HUG
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <ThumbsDown className="w-3 h-3" />
                        {m.fugs} FUG
                      </span>
                    </div>
                    {m.expires_at && (
                      <span className="uppercase">
                        {timeRemaining(m.expires_at)} LEFT
                      </span>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </section>

      {/* TOPICS GRID — pick your orbit (bottom of home) */}
      <TopicsGrid />

      <section className="max-w-3xl mx-auto px-5 sm:px-8 pb-32 text-center">
        <button
          onClick={onCreate}
          data-testid="landing-cta-bottom"
          className="inline-flex items-center gap-2 rounded-full px-6 py-3 font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-xl shadow-purple-500/30"
        >
          <Send className="w-4 h-4" />
          Drop your thought
          <ArrowRight className="w-4 h-4" />
        </button>
        <p className="mt-3 text-[11px] text-zinc-600 font-mono uppercase tracking-[0.25em]">
          where lost thoughts land
        </p>
      </section>
    </div>
  );
};

export default Landing;
