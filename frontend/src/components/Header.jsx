import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Plus, Home, Hash, Music as MusicIcon, Info } from "lucide-react";
import { Logo } from "./Logo";

export const Header = ({ onCreate }) => {
  const loc = useLocation();
  const navItems = [
    { to: "/", label: "Home", icon: Home, exact: true },
    { to: "/topics", label: "Topics", icon: Hash },
    { to: "/music", label: "Music", icon: MusicIcon },
    { to: "/info", label: "Info", icon: Info },
  ];
  return (
    <header
      className="sticky top-0 z-40 px-4 py-3 sm:py-4 glass-strong border-b border-white/5"
      data-testid="app-header"
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
        <Link
          to="/"
          className="flex items-center gap-2.5 group"
          data-testid="header-home-link"
        >
          <Logo size={28} />
          <div className="leading-tight">
            <div className="font-display text-lg sm:text-xl tracking-tight -mb-0.5">
              pluto<span className="text-glow-cyan text-cyan-300">.</span>
            </div>
            <div className="text-[8px] uppercase tracking-[0.22em] text-zinc-500 font-mono hidden sm:block">
              a page not found · $pnf product
            </div>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((it) => {
            const Icon = it.icon;
            const active = it.exact
              ? loc.pathname === it.to
              : loc.pathname.startsWith(it.to);
            return (
              <Link
                key={it.to}
                to={it.to}
                data-testid={`nav-${it.label.toLowerCase()}`}
                className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm transition-all ${
                  active
                    ? "bg-white/10 text-white border border-white/15"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {it.label}
              </Link>
            );
          })}
        </nav>

        <button
          onClick={onCreate}
          data-testid="header-create-btn"
          className="inline-flex items-center gap-2 rounded-full px-3.5 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:from-purple-400 hover:to-fuchsia-400 transition shadow-lg shadow-purple-500/30"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Post</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
