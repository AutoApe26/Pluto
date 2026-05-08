import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Music as MusicIcon, Plus, Pause, Play, X } from "lucide-react";
import { api } from "../lib/api";
import { CosmicBg } from "../components/CosmicBg";
import { MusicCard } from "../components/MusicCard";
import { UploadMusicModal } from "../components/UploadMusicModal";

export const MusicPage = () => {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [playing, setPlaying] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const load = async () => {
    setLoading(true);
    try {
      setTracks(await api.music());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onPlay = (track) => {
    if (playing?.id === track.id && isPlaying) {
      audioRef.current?.pause();
      setIsPlaying(false);
      return;
    }
    setPlaying(track);
    setIsPlaying(true);
    setTimeout(() => {
      if (audioRef.current) {
        audioRef.current.src = track.audio;
        audioRef.current.play().catch(() => setIsPlaying(false));
      }
    }, 50);
  };

  return (
    <div className="relative" data-testid="music-page">
      <CosmicBg variant="music" />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 pb-40">
        <div className="flex items-end justify-between mb-6">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-purple-300 font-mono">
              underground room
            </p>
            <h1 className="font-display text-3xl sm:text-4xl mt-1">
              Anon sounds
            </h1>
            <p className="mt-1 text-sm text-zinc-500">
              Hug it. Fug it. No one's watching.
            </p>
          </div>
          <button
            onClick={() => setOpen(true)}
            data-testid="open-upload-music"
            className="inline-flex items-center gap-2 rounded-full bg-purple-500 text-white px-4 py-2.5 hover:bg-purple-400 transition glow-purple text-sm"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Upload track</span>
            <span className="sm:hidden">Upload</span>
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
              Be the first to release into the underground.
            </p>
            <button
              onClick={() => setOpen(true)}
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-purple-500 text-white px-4 py-2 hover:bg-purple-400 transition"
            >
              <Plus className="w-4 h-4" /> Upload first track
            </button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {tracks.map((t, i) => (
              <MusicCard
                key={t.id}
                track={t}
                index={i}
                onPlay={onPlay}
                isPlaying={isPlaying && playing?.id === t.id}
              />
            ))}
          </div>
        )}
      </div>

      {/* Floating audio player */}
      {playing && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="fixed bottom-20 sm:bottom-4 left-1/2 -translate-x-1/2 z-40 w-[94%] max-w-2xl"
          data-testid="audio-player"
        >
          <div className="glass-strong rounded-3xl p-3 flex items-center gap-3 border border-white/10">
            <img
              src={
                playing.cover ||
                "https://static.prod-images.emergentagent.com/jobs/9e88d8f6-abc5-4041-b787-3d490a873302/images/d0a9d09aec04baea11248d881ee3e510f44a976c4db80243bef23e8e7c42b8bb.png"
              }
              alt=""
              className="w-12 h-12 rounded-2xl object-cover"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{playing.title}</p>
              <p className="text-xs text-zinc-400 truncate">{playing.artist}</p>
            </div>
            <div className="flex items-end gap-0.5 h-7 px-2">
              {[0, 1, 2, 3, 4].map((i) => (
                <span
                  key={i}
                  className="wave-bar"
                  style={{
                    animationDelay: `${i * 0.12}s`,
                    opacity: isPlaying ? 1 : 0.3,
                  }}
                />
              ))}
            </div>
            <button
              onClick={() => onPlay(playing)}
              className="w-10 h-10 rounded-full bg-cyan-300 text-black flex items-center justify-center"
              data-testid="player-toggle"
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4 ml-0.5" />
              )}
            </button>
            <button
              onClick={() => {
                audioRef.current?.pause();
                setPlaying(null);
                setIsPlaying(false);
              }}
              className="w-9 h-9 rounded-full hover:bg-white/5 text-zinc-400"
              data-testid="player-close"
            >
              <X className="w-4 h-4 mx-auto" />
            </button>
          </div>
          <audio
            ref={audioRef}
            onEnded={() => setIsPlaying(false)}
            onPause={() => setIsPlaying(false)}
            onPlay={() => setIsPlaying(true)}
            className="hidden"
          />
        </motion.div>
      )}

      <UploadMusicModal
        open={open}
        onClose={() => setOpen(false)}
        onCreated={(t) => setTracks((arr) => [t, ...arr])}
      />
    </div>
  );
};

export default MusicPage;
