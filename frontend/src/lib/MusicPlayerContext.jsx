import React, { createContext, useContext, useState, useCallback } from "react";

const MusicPlayerCtx = createContext(null);

export const useMusicPlayer = () => {
  const ctx = useContext(MusicPlayerCtx);
  if (!ctx) {
    throw new Error("useMusicPlayer must be used within MusicPlayerProvider");
  }
  return ctx;
};

/**
 * Holds the single currently-playing track in app-level state so the
 * persistent <MiniPlayer/> below the route outlet can keep its iframe
 * mounted while the user navigates between Home / Topics / Info / etc.
 *
 * The iframe lives in <MiniPlayer/> — not inside MusicCard — which is
 * what makes playback survive route changes. MusicCard.onPlay() simply
 * sets the current track here.
 */
export const MusicPlayerProvider = ({ children }) => {
  const [track, setTrack] = useState(null);

  const playTrack = useCallback((t) => {
    if (!t) return;
    // Re-clicking the same track shouldn't restart it — let the user
    // pause via the Spotify/YouTube embed controls. Only swap when the
    // track actually changes.
    setTrack((prev) => {
      if (prev && prev.id === t.id) return prev;
      return t;
    });
  }, []);

  const stopPlayback = useCallback(() => setTrack(null), []);

  return (
    <MusicPlayerCtx.Provider value={{ track, playTrack, stopPlayback }}>
      {children}
    </MusicPlayerCtx.Provider>
  );
};
