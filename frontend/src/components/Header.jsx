import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Plus } from "lucide-react";
import { Logo } from "./Logo";

export const Header = ({ onCreate }) => {
  const loc = useLocation();
  const navItems = [
    { to: "/feed", label: "Feed" },
    { to: "/music", label: "Music" },
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
          <span className="font-display text-lg sm:text-xl tracking-tight">
            pluto<span className="text-glow-cyan text-cyan-300">.</span>
          </span>
        </Link>

        <nav className="hidden sm:flex items-center gap-1">
          {navItems.map((it) => {
            const active = loc.pathname.startsWith(it.to);
            return (
              <Link
                key={it.to}
                to={it.to}
                data-testid={`nav-${it.label.toLowerCase()}`}
                className={`px-4 py-2 rounded-full text-sm transition-all ${
                  active
                    ? "bg-white/10 text-white border border-white/15"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                {it.label}
              </Link>
            );
          })}
        </nav>

        <button
          onClick={onCreate}
          data-testid="header-create-btn"
          className="inline-flex items-center gap-2 rounded-full px-3.5 py-2 text-sm font-medium text-black bg-cyan-300 hover:bg-cyan-200 transition glow-cyan"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Drop a thought</span>
          <span className="sm:hidden">Post</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
