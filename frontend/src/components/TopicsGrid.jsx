import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Bitcoin,
  Zap,
  Globe2,
  Moon,
  Sparkle,
  Sparkles,
  CircleDot,
  Music as MusicIcon,
} from "lucide-react";

// 8 topic cards mirroring the lovable.app design — tinted backgrounds,
// big mono name, "ENTER →" CTA at bottom-left.
const TOPICS = [
  { slug: "crypto", name: "Crypto", icon: Bitcoin, color: "#F7931A" },
  { slug: "sports", name: "Sports", icon: Zap, color: "#FF6A2D" },
  { slug: "memes", name: "Memes", icon: Globe2, color: "#FF7AB6" },
  { slug: "mental-health", name: "Mental Health", icon: Moon, color: "#7BD7E0" },
  { slug: "rant", name: "Rant", icon: Sparkle, color: "#9B7BFF" },
  { slug: "stories", name: "Stories", icon: Sparkles, color: "#B89BFF" },
  { slug: "confession", name: "Confession", icon: CircleDot, color: "#FF5470" },
  { slug: "music", name: "Music", icon: MusicIcon, color: "#5DD3D8" },
];

export const TopicsGrid = () => {
  return (
    <section
      className="max-w-5xl mx-auto px-5 sm:px-8 py-16"
      data-testid="topics-grid-section"
    >
      <div className="mb-7">
        <h2 className="font-display text-4xl sm:text-5xl tracking-tight">
          Topics
        </h2>
        <p className="mt-2 text-[10px] uppercase tracking-[0.32em] text-zinc-400 font-mono">
          Pick your orbit
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        {TOPICS.map((t, i) => {
          const Icon = t.icon;
          return (
            <motion.div
              key={t.slug}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.04, duration: 0.4 }}
              data-testid={`topic-card-${t.slug}`}
            >
              <Link
                to={`/topics?topic=${t.slug}`}
                className="group relative block rounded-3xl p-5 sm:p-6 aspect-square overflow-hidden border transition-all hover:-translate-y-0.5"
                style={{
                  background: `
                    radial-gradient(120% 90% at 100% 0%, ${t.color}26 0%, transparent 60%),
                    linear-gradient(180deg, ${t.color}1c 0%, ${t.color}08 60%, rgba(8,4,28,0.55) 100%)
                  `,
                  borderColor: `${t.color}26`,
                  boxShadow: `inset 0 1px 0 ${t.color}14`,
                }}
              >
                {/* Hover glow */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                  style={{
                    background: `radial-gradient(60% 60% at 50% 100%, ${t.color}24, transparent 70%)`,
                  }}
                />

                {/* Icon */}
                <div
                  className="relative w-9 h-9 sm:w-11 sm:h-11 flex items-center justify-center"
                  style={{ color: t.color }}
                >
                  <Icon className="w-7 h-7 sm:w-8 sm:h-8" strokeWidth={2} />
                </div>

                {/* Spacer */}
                <div className="flex-1" />

                {/* Title + Enter */}
                <div className="absolute bottom-5 sm:bottom-6 left-5 sm:left-6 right-5 sm:right-6">
                  <h3 className="font-mono font-bold text-lg sm:text-2xl text-white leading-tight">
                    {t.name}
                  </h3>
                  <div className="mt-3 flex items-center gap-1.5 text-[10px] uppercase tracking-[0.28em] text-zinc-400 font-mono group-hover:text-white transition">
                    Enter
                    <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition" />
                  </div>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};

export default TopicsGrid;
