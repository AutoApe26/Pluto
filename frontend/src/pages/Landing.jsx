import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Headphones, ArrowRight, Send } from "lucide-react";
import { Logo } from "../components/Logo";
import { CosmicBg } from "../components/CosmicBg";
import { TimeRemainingBadge } from "../components/TimeRemainingBadge";
import { api } from "../lib/api";
import { relativeTime } from "../lib/format";

const HERO_BG =
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/3dd9c5de0452a0478d75402ce1a1e81d6413c355789dd2a87d4ba3ebbe6e0cc3.png";

const FALLBACK_COVERS = [
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/d0a9d09aec04baea11248d881ee3e510f44a976c4db80243bef23e8e7c42b8bb.png",
  "https://images.unsplash.com/photo-1774132221866-9e6c2275b700?crop=entropy&cs=srgb&fm=jpg&w=600&q=70",
  "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/c8cf273ab43d9cecad200f4ff4c2787881f84f1f2ed48ed02617d136a5174162.png",
];

export const Landing = ({ onCreate }) => {
  const [trending, setTrending] = useState([]);
  const [music, setMusic] = useState([]);

  useEffect(() => {
    api.trendingPosts().then(setTrending).catch(() => {});
    api.featuredMusic().then(setMusic).catch(() => {});
  }, []);

  return (
    <div className="relative" data-testid="landing-page">
      <CosmicBg />

      {/* HERO */}
      <section className="relative max-w-6xl mx-auto px-5 sm:px-8 pt-10 sm:pt-20 pb-16">
        <div className="absolute -z-10 inset-0 overflow-hidden rounded-[3rem] opacity-50">
          <img src={HERO_BG} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#05050A]/60 to-[#05050A]" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="grid lg:grid-cols-12 gap-10 items-center"
        >
          <div className="lg:col-span-7">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-zinc-300 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-300 pulse-soft" />
              $PNF · anonymous, ephemeral
            </div>
            <h1 className="font-display mt-5 text-5xl sm:text-6xl lg:text-7xl leading-[0.95] tracking-tight">
              Post it.
              <br />
              <span className="text-glow-cyan text-cyan-300">Let it</span>{" "}
              <span className="text-glow-purple text-purple-400 italic">
                vanish.
              </span>
            </h1>
            <p className="mt-5 text-zinc-400 text-base sm:text-lg max-w-xl leading-relaxed">
              Where lost thoughts land. Pluto is the underground anonymous
              social network for the $PNF ecosystem — every post evaporates in
              24 hours, no profile, no judgment, just pure signal.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <button
                onClick={onCreate}
                data-testid="landing-cta-post"
                className="group inline-flex items-center gap-2 rounded-full bg-cyan-300 text-black px-5 py-3 font-medium hover:bg-cyan-200 transition glow-cyan"
              >
                <Send className="w-4 h-4" />
                Post anonymously
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </button>
              <Link
                to="/feed"
                data-testid="landing-cta-feed"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 px-5 py-3 hover:border-cyan-300/50 hover:text-cyan-200 transition"
              >
                <Sparkles className="w-4 h-4" />
                Explore feed
              </Link>
              <Link
                to="/music"
                data-testid="landing-cta-music"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 px-5 py-3 hover:border-purple-400/50 hover:text-purple-200 transition"
              >
                <Headphones className="w-4 h-4" />
                Underground music
              </Link>
            </div>

            <div className="mt-10 flex items-center gap-6 text-xs text-zinc-500 font-mono">
              <div>
                <div className="text-cyan-300 text-2xl font-display">24h</div>
                <div>auto-vanish</div>
              </div>
              <div className="w-px h-10 bg-white/10" />
              <div>
                <div className="text-purple-300 text-2xl font-display">8</div>
                <div>topic channels</div>
              </div>
              <div className="w-px h-10 bg-white/10" />
              <div>
                <div className="text-pink-300 text-2xl font-display">0</div>
                <div>accounts needed</div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <div className="relative">
              <div className="absolute -inset-2 rounded-[2rem] bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-transparent blur-2xl" />
              <div className="relative glass-strong rounded-[2rem] p-6 border border-white/10">
                <div className="flex items-center justify-between mb-4">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-zinc-500">
                    live · trending
                  </span>
                  <Logo size={28} />
                </div>
                <div className="space-y-3">
                  {(trending.length
                    ? trending
                    : [
                        {
                          id: "p1",
                          content:
                            "anyone else feel like the market is just vibes at this point?",
                          topic: "crypto",
                          created_at: new Date().toISOString(),
                          expires_at: new Date(
                            Date.now() + 1000 * 60 * 60 * 14
                          ).toISOString(),
                        },
                        {
                          id: "p2",
                          content: "told my crush I love them. ghosted. RIP me.",
                          topic: "confession",
                          created_at: new Date(
                            Date.now() - 1000 * 60 * 30
                          ).toISOString(),
                          expires_at: new Date(
                            Date.now() + 1000 * 60 * 60 * 23
                          ).toISOString(),
                        },
                        {
                          id: "p3",
                          content: "therapist said i'm doing great. lol.",
                          topic: "mental-health",
                          created_at: new Date(
                            Date.now() - 1000 * 60 * 90
                          ).toISOString(),
                          expires_at: new Date(
                            Date.now() + 1000 * 60 * 60 * 22
                          ).toISOString(),
                        },
                      ]
                  )
                    .slice(0, 3)
                    .map((p, i) => (
                      <motion.div
                        key={p.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + i * 0.1 }}
                        className="rounded-2xl bg-white/5 border border-white/10 p-3.5"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-300">
                            #{p.topic}
                          </span>
                          <TimeRemainingBadge expiresAt={p.expires_at} />
                        </div>
                        <p className="text-sm line-clamp-2 text-zinc-200">
                          {p.content}
                        </p>
                        <p className="mt-1.5 text-[10px] text-zinc-500 font-mono">
                          {relativeTime(p.created_at)}
                        </p>
                      </motion.div>
                    ))}
                </div>
                <Link
                  to="/feed"
                  className="mt-4 w-full inline-flex items-center justify-center gap-2 rounded-full border border-white/10 py-2.5 text-sm hover:border-cyan-300/50 hover:text-cyan-200 transition"
                >
                  See all whispers
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* FEATURED MUSIC */}
      <section className="max-w-6xl mx-auto px-5 sm:px-8 pb-24" data-testid="featured-music">
        <div className="flex items-end justify-between mb-6">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-purple-300 font-mono">
              underground
            </p>
            <h2 className="font-display text-3xl sm:text-4xl mt-1">
              Featured tracks
            </h2>
          </div>
          <Link
            to="/music"
            className="text-sm text-zinc-400 hover:text-purple-200 transition inline-flex items-center gap-1"
          >
            All tracks <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          {(music.length ? music : [0, 1, 2]).slice(0, 3).map((m, i) => {
            const isReal = typeof m === "object";
            const cover = isReal && m.cover ? m.cover : FALLBACK_COVERS[i % 3];
            return (
              <motion.div
                key={isReal ? m.id : i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group glass rounded-3xl overflow-hidden hover:-translate-y-1 transition-all"
              >
                <div className="relative">
                  <img
                    src={cover}
                    alt=""
                    className="w-full aspect-square object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                  <div className="absolute bottom-3 left-4 right-4">
                    <p className="text-[10px] font-mono uppercase tracking-wider text-cyan-200">
                      {isReal ? `${m.hugs} hugs` : "no fugs allowed"}
                    </p>
                    <h3 className="font-display text-lg truncate">
                      {isReal ? m.title : ["void calling", "neon shadows", "lost frequency"][i]}
                    </h3>
                    <p className="text-xs text-zinc-400 truncate">
                      {isReal ? m.artist : ["anon-77", "ghost.fm", "moonlit"][i]}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* CTA STRIP */}
      <section className="max-w-6xl mx-auto px-5 sm:px-8 pb-24">
        <div className="relative glass-strong rounded-[2rem] p-8 sm:p-12 overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-purple-500/30 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-64 h-64 rounded-full bg-cyan-500/30 blur-3xl" />
          <div className="relative">
            <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-400 font-mono">
              tagline
            </p>
            <h2 className="font-display text-4xl sm:text-5xl mt-2 max-w-2xl leading-tight">
              Where lost thoughts <span className="text-glow-purple text-purple-300">land.</span>
            </h2>
            <p className="mt-3 text-zinc-400 max-w-lg">
              No follower counts. No likes that haunt you. Just raw signals
              floating through the orbit of $PNF — and gone before sunrise.
            </p>
            <button
              onClick={onCreate}
              data-testid="landing-cta-bottom"
              className="mt-6 inline-flex items-center gap-2 rounded-full bg-white text-black px-5 py-3 font-medium hover:bg-zinc-200 transition"
            >
              Drop your first thought
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
