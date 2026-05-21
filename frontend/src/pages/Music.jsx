import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Music as MusicIcon, Plus } from "lucide-react";
import { api } from "../lib/api";
import { CosmicBg } from "../components/CosmicBg";
import { MusicCard } from "../components/MusicCard";
import { UploadMusicModal } from "../components/UploadMusicModal";

export const MusicPage = () => {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setTracks(await api.music());
    } finally {
      setLoading(false);
    }
  };

  // Silent refresh — used by the polling loop so engagement-loop hugs/fugs
  // bumps from the backend show up without a manual page refresh.
  const refresh = async () => {
    try {
      setTracks(await api.music());
    } catch {
      /* keep current state */
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const tick = () => {
      if (document.visibilityState === "visible") refresh();
    };
    const id = setInterval(tick, 12000);
    const onVis = () => {
      if (document.visibilityState === "visible") refresh();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      clearInterval(id);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  return (
    <div className="relative" data-testid="music-page">
      <CosmicBg variant="music" />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 pb-32">
        <div className="flex items-end justify-between mb-6 gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-purple-300 font-mono">
              support underground artists
            </p>
            <h1 className="font-display text-3xl sm:text-4xl mt-1">
              Trending Music
            </h1>
            <p className="mt-1 text-sm text-zinc-500">
              Hug it. Fug it. Vanishes in 24 hours.
            </p>
          </div>
          <button
            onClick={() => setOpen(true)}
            data-testid="open-upload-music"
            className="inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Drop track</span>
            <span className="sm:hidden">Drop</span>
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
            <Loader2 className="w-6 h-6 animate-spin" />
            <p className="mt-3 text-sm font-mono">tuning frequencies...</p>
          </div>
        ) : tracks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass rounded-3xl p-10 text-center"
            data-testid="empty-music"
          >
            <MusicIcon className="w-10 h-10 mx-auto text-zinc-600" />
            <h3 className="mt-4 font-display text-xl">Silence...</h3>
            <p className="mt-2 text-sm text-zinc-500">
              Be the first to drop a track from Spotify or YouTube.
            </p>
            <button
              onClick={() => setOpen(true)}
              className="mt-5 inline-flex items-center gap-2 rounded-full px-4 py-2 text-white bg-gradient-to-r from-purple-500 to-fuchsia-500 hover:opacity-95 transition"
            >
              <Plus className="w-4 h-4" /> Drop the first track
            </button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {tracks.map((t, i) => (
              <MusicCard key={t.id} track={t} index={i} />
            ))}
          </div>
        )}
      </div>

      <UploadMusicModal
        open={open}
        onClose={() => setOpen(false)}
        onCreated={(t) => setTracks((arr) => [t, ...arr])}
      />
    </div>
  );
};

export default MusicPage;
