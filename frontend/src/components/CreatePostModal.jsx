import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, ImagePlus, Send, Loader2, AlertTriangle, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { fileToDataUrl } from "../lib/format";
import { screenContent } from "../lib/safety";

const MAX_LEN = 1000;

export const CreatePostModal = ({ open, onClose, topics, onCreated, defaultTopic }) => {
  const [content, setContent] = useState("");
  const [topic, setTopic] = useState(defaultTopic || "rant");
  const [sudoName, setSudoName] = useState("");
  const [image, setImage] = useState(null);
  const [isLyrics, setIsLyrics] = useState(false);
  const [busy, setBusy] = useState(false);
  // Sticky moderation banner state — when the backend rejects a post we
  // surface the *exact* server reason here so the user can't miss it.
  // Cleared when they edit the textarea (they're addressing the issue).
  const [serverError, setServerError] = useState("");
  // Increments every time a blocked user clicks the disabled button —
  // used to shake the warning banner so the rejection is unmissable.
  const [shakeTick, setShakeTick] = useState(0);
  const bannerRef = useRef();
  const textareaRef = useRef();
  const fileRef = useRef();

  useEffect(() => {
    if (open) {
      setContent("");
      setSudoName("");
      setImage(null);
      setIsLyrics(false);
      setTopic(defaultTopic || "rant");
      setServerError("");
      setShakeTick(0);
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
    const screen = screenContent(content);
    if (!screen.ok) {
      // Surface the block reason in the sticky banner + shake it so
      // the user understands their post is NOT going through.
      setServerError(screen.reason);
      setShakeTick((n) => n + 1);
      bannerRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      toast.error("Post blocked — see the red banner above");
      return;
    }
    setBusy(true);
    setServerError("");
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
      // Show the *server* reason in the sticky banner — the toast alone
      // is easy to miss on mobile. Also shake + scroll to make it obvious
      // the post was NOT published.
      const reason =
        e.response?.data?.detail ||
        "Failed to post. Please check your connection and try again.";
      setServerError(reason);
      setShakeTick((n) => n + 1);
      bannerRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      toast.error(reason);
    } finally {
      setBusy(false);
    }
  };

  // Inline warning derived from current content. Computed every render —
  // cheap (single normalize + substring loop). Disables the submit button
  // and renders a red banner below the textarea so the user sees the
  // issue immediately, before they even press Post.
  const screen = screenContent(content);
  const isUnsafe = !screen.ok && content.trim().length > 0;
  // The sticky banner shows EITHER the inline-screen reason OR the last
  // backend-server rejection reason. As soon as the user edits content
  // the backend-server reason clears (they're addressing it).
  const bannerReason = isUnsafe ? screen.reason : serverError;
  const showBanner = !!bannerReason && (isUnsafe || !!serverError);

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
            className="relative w-full sm:max-w-lg glass-strong rounded-t-3xl sm:rounded-3xl m-0 sm:m-4 border border-white/10 max-h-[94vh] sm:max-h-[88vh] flex flex-col overflow-hidden"
            style={{ paddingBottom: "max(env(safe-area-inset-bottom), 0px)" }}
          >
            {/* Drag handle on mobile */}
            <div className="sm:hidden flex justify-center pt-2.5 pb-1 shrink-0">
              <span className="block w-10 h-1 rounded-full bg-white/20" />
            </div>

            {/* Header (sticky) */}
            <div className="flex items-start justify-between px-5 sm:px-7 pt-3 sm:pt-6 pb-2 shrink-0">
              <div>
                <h2 className="font-display text-xl sm:text-2xl">Drop a thought</h2>
                <p className="text-xs sm:text-sm text-zinc-400 mt-0.5">
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

            {/* Scrollable body */}
            <div className="flex-1 overflow-y-auto px-5 sm:px-7 pb-4">
              {/* Sticky moderation banner. Shows the EXACT block reason
                  (inline screen or backend rejection) so the user knows
                  their post did NOT go through. Shakes on submit-while-
                  blocked so it's impossible to miss. */}
              <AnimatePresence>
                {showBanner && (
                  <motion.div
                    ref={bannerRef}
                    key={shakeTick}
                    data-testid="moderation-banner"
                    initial={{ opacity: 0, y: -8 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      x: shakeTick > 0 ? [0, -8, 8, -6, 6, -3, 3, 0] : 0,
                    }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{
                      opacity: { duration: 0.18 },
                      x: { duration: 0.45 },
                    }}
                    className="mt-3 rounded-2xl border border-red-400/50 bg-gradient-to-br from-red-500/[0.18] to-red-600/[0.10] px-4 py-3 shadow-lg shadow-red-500/10"
                  >
                    <div className="flex items-start gap-3">
                      <div className="shrink-0 mt-0.5 w-7 h-7 rounded-full bg-red-500/30 flex items-center justify-center">
                        <ShieldAlert className="w-4 h-4 text-red-200" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-[11px] uppercase tracking-[0.18em] font-mono text-red-300/90 font-bold">
                          Post blocked · not published
                        </div>
                        <div className="mt-1 text-[13px] leading-snug text-red-100">
                          {bannerReason}
                        </div>
                        <div className="mt-1.5 text-[11px] text-red-200/70">
                          Edit your message below to continue.
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="mt-3">
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
                    ref={textareaRef}
                    placeholder="Say anything anonymously..."
                    value={content}
                    onChange={(e) => {
                      setContent(e.target.value.slice(0, MAX_LEN));
                      // User is addressing the issue — clear server error
                      // so the banner reflects only the live inline check.
                      if (serverError) setServerError("");
                    }}
                    rows={5}
                    data-testid="create-post-textarea"
                    className="w-full bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-3 pb-9 text-[15px] resize-none focus:border-purple-400/60 focus:bg-white/[0.05] focus:outline-none transition"
                  />
                  <div className="absolute bottom-3 right-3 flex items-center gap-1.5 pointer-events-none">
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

                {/* Inline safety warning — fires the moment content matches
                    a threat / hate / abuse phrase. Submit is also locked. */}
                {isUnsafe && (
                  <div
                    data-testid="unsafe-warning"
                    className="mt-2 flex items-start gap-2 rounded-2xl border border-red-400/40 bg-red-500/[0.08] px-3 py-2.5 text-[12px] leading-snug text-red-200"
                  >
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-red-300" />
                    <span>{screen.reason}</span>
                  </div>
                )}
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
                        className={`w-9 h-5 rounded-full relative transition shrink-0 ${
                          isLyrics ? "bg-white" : "bg-white/15"
                        }`}
                      >
                        <span
                          className={`absolute top-0.5 w-4 h-4 rounded-full bg-black transition-all ${
                            isLyrics ? "left-[18px]" : "left-0.5 bg-white/80"
                          }`}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-[12px] font-mono uppercase tracking-wider text-white flex items-center gap-2 flex-wrap">
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

              <p className="mt-4 text-[11px] leading-relaxed text-zinc-500">
                Posts vanish in 24h. No links. Images are scanned — nudity,
                violence, hate symbols, drugs, weapons, and self-harm imagery
                are blocked. Other blocked text: hate/harassment, doxxing,
                misinformation, content involving minors, piracy,
                scams/wallet-drainers, terror promotion, sexual content,
                self-harm. Same content max 5×/24h.
              </p>
            </div>

            {/* Sticky bottom action */}
            <div className="shrink-0 border-t border-white/10 bg-[#0b0218]/85 backdrop-blur-xl px-5 sm:px-7 pt-3 pb-3">
              <button
                onClick={submit}
                disabled={busy}
                data-testid="create-post-submit"
                aria-label={
                  isUnsafe
                    ? "Can't post — content blocked. Tap to see why."
                    : "Post anonymously"
                }
                className={`w-full inline-flex items-center justify-center gap-2 rounded-full py-3.5 font-medium text-white transition shadow-lg disabled:opacity-50 ${
                  isUnsafe
                    ? "bg-red-500/70 shadow-red-500/20 cursor-not-allowed hover:bg-red-500/80"
                    : "bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 shadow-purple-500/30"
                }`}
              >
                {busy ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isUnsafe ? (
                  <AlertTriangle className="w-4 h-4" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                {busy
                  ? "Posting..."
                  : isUnsafe
                    ? "Can't post — content blocked"
                    : "Post anonymously"}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CreatePostModal;
