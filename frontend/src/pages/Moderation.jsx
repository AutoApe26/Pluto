import React, { useEffect, useState } from "react";
import { Shield, Trash2, ShieldCheck, KeyRound, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { MOD_KEY_STORAGE } from "../lib/device";
import { CosmicBg } from "../components/CosmicBg";
import { relativeTime } from "../lib/format";

export const Moderation = () => {
  const [authed, setAuthed] = useState(
    !!localStorage.getItem(MOD_KEY_STORAGE)
  );
  const [keyInput, setKeyInput] = useState("");
  const [data, setData] = useState({ posts: [], music: [] });
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const d = await api.modReported();
      setData(d);
    } catch (e) {
      if (e.response?.status === 401) {
        localStorage.removeItem(MOD_KEY_STORAGE);
        setAuthed(false);
        toast.error("Invalid mod key");
      } else {
        toast.error("Failed to load");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authed) load();
  }, [authed]);

  const submit = () => {
    if (!keyInput.trim()) return;
    localStorage.setItem(MOD_KEY_STORAGE, keyInput.trim());
    setAuthed(true);
  };

  const act = async (kind, type, id) => {
    try {
      if (kind === "delete") await api.modDelete(type, id);
      else await api.modSafe(type, id);
      toast.success(kind === "delete" ? "Deleted" : "Marked safe");
      load();
    } catch {
      toast.error("Action failed");
    }
  };

  if (!authed) {
    return (
      <div className="relative min-h-screen flex items-center justify-center px-4">
        <CosmicBg />
        <div className="glass-strong rounded-3xl p-8 max-w-sm w-full" data-testid="mod-auth-card">
          <div className="flex items-center gap-2 text-purple-300 mb-3">
            <Shield className="w-5 h-5" />
            <span className="text-[10px] uppercase tracking-[0.3em] font-mono">
              moderator only
            </span>
          </div>
          <h1 className="font-display text-2xl">Enter the orbit</h1>
          <p className="mt-1 text-sm text-zinc-400">
            This area is restricted. Provide your moderation key to continue.
          </p>
          <div className="mt-5 relative">
            <KeyRound className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="password"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              placeholder="mod key"
              data-testid="mod-key-input"
              className="w-full bg-transparent border border-white/10 rounded-2xl pl-9 pr-4 py-2.5 focus:border-purple-400/50 focus:outline-none transition"
            />
          </div>
          <button
            onClick={submit}
            data-testid="mod-key-submit"
            className="mt-4 w-full rounded-full bg-purple-500 text-white py-2.5 hover:bg-purple-400 transition glow-purple"
          >
            Unlock
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen" data-testid="moderation-page">
      <CosmicBg />
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 pb-24">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-red-300 font-mono">
              control room
            </p>
            <h1 className="font-display text-3xl mt-1">Moderation</h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={load}
              data-testid="mod-refresh"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm hover:border-cyan-300/50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <button
              onClick={() => {
                localStorage.removeItem(MOD_KEY_STORAGE);
                setAuthed(false);
              }}
              className="text-sm text-zinc-500 hover:text-white px-3"
            >
              Logout
            </button>
          </div>
        </div>

        <Section
          title="Reported posts"
          items={data.posts}
          renderItem={(p) => (
            <div key={p.id} className="glass rounded-2xl p-4">
              <div className="flex items-center justify-between text-xs text-zinc-500 mb-2">
                <span className="font-mono">
                  #{p.topic} · {relativeTime(p.created_at)}
                </span>
                <span className="text-red-300 font-mono">
                  {p.report_count} reports
                </span>
              </div>
              <p className="text-sm text-zinc-200 whitespace-pre-wrap line-clamp-4">
                {p.content}
              </p>
              {p.image && (
                <img
                  src={p.image}
                  alt=""
                  className="mt-2 max-h-40 rounded-xl object-cover"
                />
              )}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => act("delete", "post", p.id)}
                  data-testid={`mod-delete-post-${p.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/20 border border-red-400/40 text-red-200 text-xs hover:bg-red-500/30"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
                <button
                  onClick={() => act("safe", "post", p.id)}
                  data-testid={`mod-safe-post-${p.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-200 text-xs hover:bg-emerald-500/25"
                >
                  <ShieldCheck className="w-3.5 h-3.5" /> Mark safe
                </button>
              </div>
            </div>
          )}
        />

        <Section
          title="Reported tracks"
          items={data.music}
          renderItem={(m) => (
            <div key={m.id} className="glass rounded-2xl p-4">
              <div className="flex items-center justify-between text-xs text-zinc-500 mb-2">
                <span className="font-mono">{relativeTime(m.created_at)}</span>
                <span className="text-red-300 font-mono">
                  {m.report_count} reports
                </span>
              </div>
              <p className="font-display">{m.title}</p>
              <p className="text-xs text-zinc-400">by {m.artist}</p>
              {m.caption && (
                <p className="text-xs text-zinc-500 mt-1 line-clamp-2">
                  {m.caption}
                </p>
              )}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => act("delete", "music", m.id)}
                  data-testid={`mod-delete-music-${m.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/20 border border-red-400/40 text-red-200 text-xs hover:bg-red-500/30"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
                <button
                  onClick={() => act("safe", "music", m.id)}
                  data-testid={`mod-safe-music-${m.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-200 text-xs hover:bg-emerald-500/25"
                >
                  <ShieldCheck className="w-3.5 h-3.5" /> Mark safe
                </button>
              </div>
            </div>
          )}
        />
      </div>
    </div>
  );
};

const Section = ({ title, items, renderItem }) => (
  <div className="mb-8">
    <h2 className="font-display text-xl mb-3">{title}</h2>
    {items.length === 0 ? (
      <div className="glass rounded-2xl p-6 text-sm text-zinc-500 text-center">
        Nothing to review. The orbit is calm.
      </div>
    ) : (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{items.map(renderItem)}</div>
    )}
  </div>
);

export default Moderation;
