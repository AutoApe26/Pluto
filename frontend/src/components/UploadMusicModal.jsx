import React, { useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Music, ImagePlus, Upload } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { fileToDataUrl } from "../lib/format";

export const UploadMusicModal = ({ open, onClose, onCreated }) => {
  const [artist, setArtist] = useState("");
  const [title, setTitle] = useState("");
  const [caption, setCaption] = useState("");
  const [tags, setTags] = useState("");
  const [audio, setAudio] = useState(null);
  const [audioName, setAudioName] = useState("");
  const [cover, setCover] = useState(null);
  const [busy, setBusy] = useState(false);
  const aRef = useRef();
  const cRef = useRef();

  const reset = () => {
    setArtist("");
    setTitle("");
    setCaption("");
    setTags("");
    setAudio(null);
    setAudioName("");
    setCover(null);
  };

  const onAudio = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 8 * 1024 * 1024) {
      toast.error("Max audio size is 8MB");
      return;
    }
    setAudio(await fileToDataUrl(f));
    setAudioName(f.name);
  };

  const onCover = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 3 * 1024 * 1024) {
      toast.error("Max cover size is 3MB");
      return;
    }
    setCover(await fileToDataUrl(f));
  };

  const submit = async () => {
    if (!artist.trim() || !title.trim() || !audio) {
      toast.error("Artist, title, and audio are required");
      return;
    }
    setBusy(true);
    try {
      const tagList = tags
        .split(/[, ]+/)
        .map((t) => t.replace("#", "").trim())
        .filter(Boolean);
      const t = await api.uploadMusic({
        artist,
        title,
        caption,
        audio,
        cover,
        tags: tagList,
      });
      toast.success("Track dropped underground");
      onCreated?.(t);
      reset();
      onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          data-testid="upload-music-modal"
        >
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 30, opacity: 0 }}
            transition={{ type: "spring", damping: 26, stiffness: 240 }}
            className="relative w-full sm:max-w-lg glass-strong rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 m-0 sm:m-4 border border-white/10 max-h-[92vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-xl">Drop a track</h2>
              <button
                onClick={onClose}
                data-testid="close-upload-music"
                className="p-2 rounded-full hover:bg-white/5 text-zinc-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                  Artist
                </label>
                <input
                  value={artist}
                  onChange={(e) => setArtist(e.target.value)}
                  placeholder="anon producer"
                  data-testid="music-artist-input"
                  className="mt-1 w-full bg-transparent border border-white/10 rounded-2xl px-4 py-2.5 focus:border-cyan-300/50 focus:outline-none transition"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                  Song title
                </label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="midnight static"
                  data-testid="music-title-input"
                  className="mt-1 w-full bg-transparent border border-white/10 rounded-2xl px-4 py-2.5 focus:border-cyan-300/50 focus:outline-none transition"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                  Caption (optional)
                </label>
                <textarea
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  rows={2}
                  placeholder="Made at 3am with a dying laptop..."
                  className="mt-1 w-full bg-transparent border border-white/10 rounded-2xl px-4 py-2.5 resize-none focus:border-cyan-300/50 focus:outline-none transition"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                  Tags (comma separated)
                </label>
                <input
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="lofi, synthwave, ambient"
                  data-testid="music-tags-input"
                  className="mt-1 w-full bg-transparent border border-white/10 rounded-2xl px-4 py-2.5 focus:border-cyan-300/50 focus:outline-none transition"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <input
                    ref={aRef}
                    type="file"
                    accept="audio/*"
                    className="hidden"
                    onChange={onAudio}
                    data-testid="music-audio-input"
                  />
                  <button
                    onClick={() => aRef.current?.click()}
                    className={`w-full rounded-2xl border px-3 py-4 flex flex-col items-center gap-1 transition ${
                      audio
                        ? "border-cyan-300/40 text-cyan-200"
                        : "border-white/10 text-zinc-400 hover:border-white/30"
                    }`}
                    data-testid="music-audio-btn"
                  >
                    <Music className="w-5 h-5" />
                    <span className="text-[11px] truncate max-w-full">
                      {audioName || "Pick audio"}
                    </span>
                  </button>
                </div>
                <div>
                  <input
                    ref={cRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={onCover}
                  />
                  <button
                    onClick={() => cRef.current?.click()}
                    className={`w-full rounded-2xl border px-3 py-4 flex flex-col items-center gap-1 transition relative overflow-hidden ${
                      cover
                        ? "border-purple-400/50"
                        : "border-white/10 text-zinc-400 hover:border-white/30"
                    }`}
                    data-testid="music-cover-btn"
                  >
                    {cover ? (
                      <img
                        src={cover}
                        alt=""
                        className="absolute inset-0 w-full h-full object-cover"
                      />
                    ) : (
                      <>
                        <ImagePlus className="w-5 h-5" />
                        <span className="text-[11px]">Cover (optional)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            <button
              onClick={submit}
              disabled={busy}
              data-testid="music-upload-submit"
              className="mt-5 w-full inline-flex items-center justify-center gap-2 rounded-full bg-purple-500 text-white py-3 font-medium hover:bg-purple-400 transition glow-purple disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              {busy ? "Uploading..." : "Release into the underground"}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default UploadMusicModal;
