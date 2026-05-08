import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, ImagePlus, Clock, Send } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { fileToDataUrl } from "../lib/format";

export const CreatePostModal = ({ open, onClose, topics, onCreated, defaultTopic }) => {
  const [content, setContent] = useState("");
  const [topic, setTopic] = useState(defaultTopic || "tell-anything");
  const [image, setImage] = useState(null);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef();

  useEffect(() => {
    if (open) {
      setContent("");
      setImage(null);
      setTopic(defaultTopic || "tell-anything");
    }
  }, [open, defaultTopic]);

  const onFile = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 4 * 1024 * 1024) {
      toast.error("Max image size is 4MB");
      return;
    }
    setImage(await fileToDataUrl(f));
  };

  const submit = async () => {
    if (!content.trim()) {
      toast.error("Write something first");
      return;
    }
    setBusy(true);
    try {
      const post = await api.createPost({ content, topic, image });
      toast.success("Posted. It vanishes in 24h.");
      onCreated?.(post);
      onClose();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to post");
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
          data-testid="create-post-modal"
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
            className="relative w-full sm:max-w-lg glass-strong rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 m-0 sm:m-4 border border-white/10"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-xl">Drop a thought</h2>
              <button
                onClick={onClose}
                data-testid="close-create-modal"
                className="p-2 rounded-full hover:bg-white/5 text-zinc-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <textarea
              autoFocus
              placeholder="Say it. It vanishes in 24h..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              maxLength={2000}
              rows={5}
              data-testid="create-post-textarea"
              className="w-full bg-transparent border border-white/10 rounded-2xl px-4 py-3 text-[15px] resize-none focus:border-cyan-300/50 focus:outline-none transition"
            />

            <div className="mt-3">
              <label className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">
                Topic
              </label>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {topics.map((t) => (
                  <button
                    key={t.slug}
                    onClick={() => setTopic(t.slug)}
                    data-testid={`topic-pick-${t.slug}`}
                    className={`text-xs px-3 py-1.5 rounded-full border transition ${
                      topic === t.slug
                        ? "bg-white/10 border-white/30 text-white"
                        : "border-white/10 text-zinc-400 hover:text-white hover:border-white/20"
                    }`}
                    style={
                      topic === t.slug
                        ? { borderColor: `${t.color}80`, color: t.color }
                        : {}
                    }
                  >
                    #{t.name}
                  </button>
                ))}
              </div>
            </div>

            {image && (
              <div className="mt-3 relative rounded-2xl overflow-hidden border border-white/10">
                <img src={image} alt="" className="w-full max-h-64 object-cover" />
                <button
                  onClick={() => setImage(null)}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-black/70 text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onFile}
              data-testid="create-post-image-input"
            />

            <div className="mt-4 flex items-center justify-between gap-3">
              <button
                onClick={() => fileRef.current?.click()}
                className="inline-flex items-center gap-2 px-3 py-2 rounded-full border border-white/10 text-zinc-300 hover:border-cyan-300/40 hover:text-cyan-200 transition text-sm"
                data-testid="create-post-image-btn"
              >
                <ImagePlus className="w-4 h-4" />
                {image ? "Change image" : "Add image"}
              </button>
              <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-mono uppercase tracking-wider">
                <Clock className="w-3 h-3" /> Disappears in 24h
              </div>
            </div>

            <button
              onClick={submit}
              disabled={busy}
              data-testid="create-post-submit"
              className="mt-4 w-full inline-flex items-center justify-center gap-2 rounded-full bg-cyan-300 text-black py-3 font-medium hover:bg-cyan-200 transition glow-cyan disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {busy ? "Posting..." : "Send into the void"}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CreatePostModal;
