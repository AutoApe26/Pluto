import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Send, Heart, ThumbsDown, ShieldAlert } from "lucide-react";
import { CosmicBg } from "../components/CosmicBg";
import { PlutoSphere } from "../components/Logo";

export const InfoPage = ({ onCreate }) => {
  const cards = [
    {
      title: "What is Pluto?",
      icon: <PlutoSphere size={44} />,
      body:
        "An anonymous social app where every post disappears after 24 hours. No usernames. No followers. Just thoughts in orbit.",
    },
    {
      title: "Hug or Fug",
      icon: (
        <div className="flex gap-1">
          <Heart className="w-7 h-7 text-pink-300" />
          <ThumbsDown className="w-7 h-7 text-zinc-400" />
        </div>
      ),
      body: (
        <>
          For music drops, react with{" "}
          <span className="text-pink-300 font-semibold">HUG</span> to support an
          artist or <span className="text-zinc-200 font-semibold">FUG</span> if
          it's not for you.
        </>
      ),
    },
    {
      title: "Anonymous, but not free-for-all",
      icon: <ShieldAlert className="w-9 h-9 text-cyan-300" />,
      body:
        "Reports go to mods. Be human. Don't be weird. Don't be cruel.",
    },
    {
      title: "A Page Not Found · $PNF product",
      icon: (
        <div className="font-mono text-[10px] text-yellow-300 leading-tight">
          <span className="block">404</span>
          <span className="block text-cyan-300">$PNF</span>
        </div>
      ),
      body: "Pluto is part of the Page Not Found universe.",
    },
  ];

  return (
    <div className="relative" data-testid="info-page">
      <CosmicBg />
      <section className="relative max-w-3xl mx-auto px-5 sm:px-8 pt-12 pb-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col items-center"
        >
          <PlutoSphere size={140} />
          <p className="mt-6 text-[10px] uppercase tracking-[0.4em] text-zinc-500 font-mono">
            a page not found · $pnf product
          </p>
          <h1 className="font-display text-6xl sm:text-7xl mt-2">
            <span
              className="bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  "linear-gradient(180deg, #ffffff 0%, #c9c4ff 60%, #8a73ff 100%)",
              }}
            >
              pluto
            </span>
          </h1>
          <p className="mt-3 text-zinc-400 text-base">
            Where lost thoughts land.
          </p>
        </motion.div>
      </section>

      <section className="max-w-3xl mx-auto px-5 sm:px-8 pb-12 space-y-4">
        {cards.map((c, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08 }}
            className="glass rounded-3xl p-5 sm:p-6 flex gap-5 items-start"
            data-testid={`info-card-${i}`}
          >
            <div className="shrink-0 w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
              {c.icon}
            </div>
            <div>
              <h2 className="font-display text-xl sm:text-2xl">{c.title}</h2>
              <div className="mt-2 text-sm sm:text-base text-zinc-300 leading-relaxed">
                {c.body}
              </div>
            </div>
          </motion.div>
        ))}
      </section>

      <section className="max-w-3xl mx-auto px-5 sm:px-8 pb-32">
        <button
          onClick={onCreate}
          data-testid="info-cta-post"
          className="w-full inline-flex items-center justify-center gap-2 rounded-full py-4 font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-xl shadow-purple-500/30"
        >
          <Send className="w-4 h-4" />
          Post anonymously
          <ArrowRight className="w-4 h-4" />
        </button>
        <Link
          to="/topics"
          className="mt-3 w-full block text-center text-sm text-zinc-500 hover:text-white transition"
        >
          Or browse topics →
        </Link>
      </section>
    </div>
  );
};

export default InfoPage;
