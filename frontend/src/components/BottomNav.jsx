import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Home, Hash, Music as MusicIcon, Plus, Info } from "lucide-react";

export const BottomNav = ({ onCreate }) => {
  const loc = useLocation();
  const items = [
    { to: "/", icon: Home, label: "Home", testid: "bottomnav-home" },
    { to: "/topics", icon: Hash, label: "Topics", testid: "bottomnav-topics" },
    {
      to: "#create",
      icon: Plus,
      label: "Post",
      testid: "bottomnav-create",
      action: true,
    },
    {
      to: "/music",
      icon: MusicIcon,
      label: "Music",
      testid: "bottomnav-music",
    },
    { to: "/info", icon: Info, label: "Info", testid: "bottomnav-info" },
  ];

  return (
    <div
      className="fixed bottom-3 left-1/2 -translate-x-1/2 z-50 md:hidden w-[94%] max-w-md"
      data-testid="bottom-nav"
    >
      <div className="glass-strong rounded-full px-2 py-2 flex items-center justify-around shadow-2xl">
        {items.map((it) => {
          const Icon = it.icon;
          const active = !it.action && loc.pathname === it.to;
          if (it.action) {
            return (
              <button
                key={it.label}
                onClick={onCreate}
                data-testid={it.testid}
                className="relative -mt-7 flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-fuchsia-500 text-white shadow-xl shadow-purple-500/40"
              >
                <Icon className="w-6 h-6" strokeWidth={2.5} />
              </button>
            );
          }
          return (
            <Link
              key={it.to}
              to={it.to}
              data-testid={it.testid}
              className={`flex flex-col items-center justify-center px-3 py-1.5 rounded-full transition-all ${
                active ? "text-purple-300" : "text-zinc-400"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5 font-medium">
                {it.label}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNav;
