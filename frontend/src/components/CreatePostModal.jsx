import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, ImagePlus, Send, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { fileToDataUrl } from "../lib/format";

const MAX_LEN = 1000;

export const CreatePostModal = ({ open, onClose, topics, onCreated, defaultTopic }) => {
  const [content, setContent] = useState("");
  const [topic, setTopic] = useState(defaultTopic || "rant");
  const [sudoName, setSudoName] = useState("");
  const [image, setImage] = useState(null);
  const [isLyrics, setIsLyrics] = useState(false);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef();

  useEffect(() => {
    if (open) {
      setContent("");
      setSudoName("");
      setImage(null);
      setIsLyrics(false);
      setTopic(defaultTopic || "rant");
    }
  }, [open, defaultTopic]);

  // is_lyrics is only meaningful for the #music topic — auto-clear if user
  // picks a different topic so they can't bypass moderation by accident.
  useEffect(() => {
    if (topic !== "music" && isLyrics) setIsLyrics(false);
  }, [topic, isLyrics]);

  const onFile = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 4 * 1024 * 1024) {
      toast.error("Max image size is 4MB");
      e.target.value = "";
      return;
    }
    if (!/^image\/(png|jpe?g|webp)$/i.test(f.type)) {
      toast.error("Use a JPEG, PNG or WEBP image");
      e.target.value = "";
      return;
    }
    setImage(await fileToDataUrl(f));
    e.target.value = "";
  };

  const submit = async () => {
    if (!content.trim()) {
      toast.error("Write something first");
      return;
    }
    setBusy(true);
    try {
      const post = await api.createPost({
        content,
        topic,
        image,
        sudo_name: sudoName.trim() || null,
        is_lyrics: topic === "music" ? isLyrics : false,
      });
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
            className="absolute inset-0 bg-black/75 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 30, opacity: 0 }}
            transition={{ type: "spring", damping: 26, stiffness: 240 }}
            className="relative w-full sm:max-w-lg glass-strong rounded-t-3xl sm:rounded-3xl p-5 sm:p-7 m-0 sm:m-4 border border-white/10 max-h-[94vh] overflow-y-auto"
          >
            <div className="flex items-start justify-between mb-1">
              <div>
                <h2 className="font-display text-2xl">Drop a thought</h2>
                <p className="text-sm text-zinc-400 mt-0.5">
                  Anonymous. Disappears in 24 hours.
                </p>
              </div>
              <button
                onClick={onClose}
                data-testid="close-create-modal"
                className="p-2 rounded-full hover:bg-white/5 text-zinc-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-5">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
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
                        ? "text-white"
                        : "border-white/10 text-zinc-400 hover:text-white hover:border-white/20"
                    }`}
                    style={
                      topic === t.slug
                        ? {
                            background:
                              "linear-gradient(135deg, rgba(176,38,255,0.35), rgba(0,240,255,0.25))",
                            borderColor: `${t.color}80`,
                          }
                        : {}
                    }
                  >
                    #{t.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Your thought
              </label>
              <div className="mt-2 relative">
                <textarea
                  autoFocus
                  placeholder="Say anything anonymously..."
                  value={content}
                  onChange={(e) =>
                    setContent(e.target.value.slice(0, MAX_LEN))
                  }
                  rows={5}
                  data-testid="create-post-textarea"
                  className="w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-3 text-[15px] resize-none focus:border-purple-400/60 focus:bg-white/[0.05] focus:outline-none transition"
                />
                <div className="absolute bottom-3 right-3 flex items-center gap-1.5">
                  <span
                    className={`text-[10px] font-mono ${
                      content.length > MAX_LEN * 0.9
                        ? "text-fuchsia-300"
                        : "text-zinc-500"
                    }`}
                    data-testid="post-char-count"
                  >
                    {content.length}/{MAX_LEN}
                  </span>
                  <span
                    className={`w-2 h-2 rounded-full transition ${
                      content.length === 0
                        ? "bg-zinc-700"
                        : content.length > MAX_LEN * 0.9
                          ? "bg-fuchsia-400"
                          : "bg-emerald-400"
                    }`}
                  />
                </div>
              </div>
            </div>

            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Sudo name (optional)
              </label>
              <input
                type="text"
                value={sudoName}
                maxLength={24}
                onChange={(e) => setSudoName(e.target.value)}
                placeholder="Pick a temporary name..."
                data-testid="create-post-sudo-name"
                className="mt-2 w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-2.5 focus:border-purple-400/60 focus:outline-none transition"
              />
            </div>

            {topic === "music" && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setIsLyrics((v) => !v)}
                  data-testid="lyrics-toggle"
                  className={`w-full text-left rounded-2xl px-4 py-3 border transition ${
                    isLyrics
                      ? "bg-black border-white/40"
                      : "bg-white/[0.03] border-white/10 hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-5 rounded-full relative transition ${
                        isLyrics ? "bg-white" : "bg-white/15"
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-black transition-all ${
                          isLyrics ? "left-[18px]" : "left-0.5 bg-white/80"
                        }`}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="text-[12px] font-mono uppercase tracking-wider text-white flex items-center gap-2">
                        I'm posting lyrics
                        {isLyrics && (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-white text-black text-[9px] font-bold">
                            PA · EXPLICIT
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-zinc-400 mt-0.5">
                        Toggling this on shows a "Parental Advisory" badge
                        and allows explicit language for lyrics. Hate,
                        doxxing, self-harm and other rules still apply.
                      </div>
                    </div>
                  </div>
                </button>
              </div>
            )}

            <div className="mt-4">
              <label className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">
                Image (optional)
              </label>
              <input
                ref={fileRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={onFile}
                data-testid="create-post-image-input"
              />
              {image ? (
                <div className="mt-2 relative rounded-2xl overflow-hidden border border-white/10">
                  <img
                    src={image}
                    alt=""
                    className="w-full max-h-64 object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => setImage(null)}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-black/70 text-white hover:bg-black/90"
                    data-testid="remove-image"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  data-testid="create-post-image-btn"
                  className="mt-2 w-full rounded-2xl border border-dashed border-white/15 py-6 flex flex-col items-center gap-1.5 text-zinc-400 hover:text-white hover:border-purple-400/40 transition"
                >
                  <ImagePlus className="w-6 h-6" />
                  <span className="text-sm">Tap to add an image</span>
                  <span className="text-[10px] text-zinc-600 font-mono">
                    PNG · JPEG · WEBP · max 4MB
                  </span>
                </button>
              )}
            </div>

            <p className="mt-5 text-[11px] leading-relaxed text-zinc-500">
              Posts vanish in 24h. No links. Images are scanned — nudity,
              violence, hate symbols, drugs, weapons, and self-harm imagery
              are blocked. Other blocked text: hate/harassment, doxxing,
              misinformation, content involving minors, piracy,
              scams/wallet-drainers, terror promotion, sexual content,
              self-harm. Same content max 5×/24h.
            </p>

            <button
              onClick={submit}
              disabled={busy}
              data-testid="create-post-submit"
              className="mt-4 w-full inline-flex items-center justify-center gap-2 rounded-full py-3.5 font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {busy ? "Posting..." : "Post anonymously"}
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CreatePostModal;
