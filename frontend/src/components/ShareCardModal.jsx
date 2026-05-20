import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  Download,
  Facebook,
  Instagram,
  Link as LinkIcon,
  Share2,
  Loader2,
} from "lucide-react";
import html2canvas from "html2canvas";
import { toast } from "sonner";
import { timeRemaining } from "../lib/format";

// Lucide doesn't ship X/TikTok marks — inline tiny SVGs.
const XMark = ({ className = "w-4 h-4" }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
    <path d="M18.244 2H21l-6.52 7.45L22 22h-6.785l-4.78-6.45L4.8 22H2.044l6.97-7.96L2 2h6.91l4.32 5.86L18.244 2Zm-2.38 18h2.04L7.97 4H5.86l10.005 16Z" />
  </svg>
);
const TikTokMark = ({ className = "w-4 h-4" }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
    <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5.8 20.1a6.34 6.34 0 0 0 10.86-4.43V8.42a8.16 8.16 0 0 0 4.77 1.53V6.5a4.85 4.85 0 0 1-1.84-.2Z" />
  </svg>
);

const TOPIC_COLORS = {
  crypto: "#F7931A",
  sports: "#34C759",
  memes: "#FFCC00",
  "mental-health": "#FF6B9D",
  "tell-anything": "#00F0FF",
  rant: "#00F0FF",
  stories: "#B026FF",
  confession: "#FF3B30",
  music: "#7B61FF",
};

/**
 * Off-screen 1080x1350 "pluck card" that gets rasterized via html2canvas,
 * and exposes Download / native-share / Twitter / Facebook compose actions.
 */
export const ShareCardModal = ({ open, onClose, post }) => {
  const cardRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [blob, setBlob] = useState(null);
  const [busy, setBusy] = useState(false);
  const [remaining, setRemaining] = useState(
    post ? timeRemaining(post.expires_at) : ""
  );

  // Tick the expiry timer while open
  useEffect(() => {
    if (!open || !post) return;
    setRemaining(timeRemaining(post.expires_at));
    const id = setInterval(
      () => setRemaining(timeRemaining(post.expires_at)),
      30 * 1000
    );
    return () => clearInterval(id);
  }, [open, post]);

  // When modal opens, auto-render the share card to a PNG so the user
  // sees a real preview of what they'll download/share.
  useEffect(() => {
    let cancelled = false;
    if (!open || !post) {
      setPreviewUrl((u) => {
        if (u) URL.revokeObjectURL(u);
        return null;
      });
      setBlob(null);
      return;
    }
    const t = setTimeout(async () => {
      setBusy(true);
      try {
        // Give the off-screen card a tick to mount
        await new Promise((r) => requestAnimationFrame(r));
        if (!cardRef.current) return;
        const canvas = await html2canvas(cardRef.current, {
          backgroundColor: null,
          scale: 1,
          useCORS: true,
          logging: false,
          width: 1080,
          height: 1350,
          windowWidth: 1080,
          windowHeight: 1350,
        });
        const b = await new Promise((resolve) =>
          canvas.toBlob((bb) => resolve(bb), "image/png", 0.95)
        );
        if (cancelled || !b) return;
        const url = URL.createObjectURL(b);
        setBlob(b);
        setPreviewUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
      } catch (e) {
        console.error("share card render failed", e);
        if (!cancelled) toast.error("Couldn't render share card");
      } finally {
        if (!cancelled) setBusy(false);
      }
    }, 60);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [open, post, remaining]);

  if (!post) return null;
  const color = TOPIC_COLORS[post.topic] || "#00F0FF";
  const author = post.sudo_name || `anon · ${post.device_id?.slice(-6) || ""}`;
  // Direct link to the specific post — anyone with this URL can open it
  // even if they aren't running the app yet.
  const shareUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/post/${post.id}`
      : "";

  const handleDownload = () => {
    if (!blob || !previewUrl) {
      toast.message("Still rendering — try again in a sec");
      return;
    }
    const a = document.createElement("a");
    a.href = previewUrl;
    a.download = `pluto-${post.id?.slice(0, 8) || "post"}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast.success("Saved to your device");
  };

  // Internal: download the PNG silently (used by Instagram/TikTok flow)
  const silentDownload = () => {
    if (!blob || !previewUrl) return false;
    const a = document.createElement("a");
    a.href = previewUrl;
    a.download = `pluto-${post.id?.slice(0, 8) || "post"}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    return true;
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  };

  const handleNativeShare = async () => {
    if (!blob) {
      toast.message("Still rendering — try again in a sec");
      return;
    }
    const file = new File([blob], `pluto-${post.id?.slice(0, 8)}.png`, {
      type: "image/png",
    });
    const shareData = {
      title: "Pluto",
      text: "Saw this on Pluto. Vanishes in 24h.",
      url: shareUrl,
      files: [file],
    };
    try {
      if (navigator.canShare && navigator.canShare(shareData)) {
        await navigator.share(shareData);
        return;
      }
      if (navigator.share) {
        await navigator.share({
          title: "Pluto",
          text: "Saw this on Pluto. Vanishes in 24h.",
          url: shareUrl,
        });
        return;
      }
      toast.message(
        "Native share unavailable — use Download or the compose buttons"
      );
    } catch {
      /* user dismissed */
    }
  };

  const handleCopyLink = async () => {
    const ok = await copyToClipboard(shareUrl);
    if (ok) toast.success("Post link copied — paste it anywhere");
    else toast.error("Couldn't copy link");
  };

  const handleX = () => {
    const text = encodeURIComponent("Saw this on Pluto. Vanishes in 24h.");
    const url = encodeURIComponent(shareUrl);
    window.open(
      `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      "_blank",
      "noopener,noreferrer"
    );
  };

  const handleFacebook = () => {
    const url = encodeURIComponent(shareUrl);
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      "_blank",
      "noopener,noreferrer"
    );
  };

  // Instagram & TikTok don't expose a web compose endpoint — best UX is to
  // download the PNG, copy the post link, and open the platform so the user
  // can paste/upload in one go.
  const handleInstagram = async () => {
    if (!blob) {
      toast.message("Still rendering — try again in a sec");
      return;
    }
    silentDownload();
    await copyToClipboard(shareUrl);
    toast.success("PNG saved + link copied. Upload it as your Story.");
    setTimeout(() => {
      window.open("https://www.instagram.com/", "_blank", "noopener,noreferrer");
    }, 350);
  };

  const handleTikTok = async () => {
    if (!blob) {
      toast.message("Still rendering — try again in a sec");
      return;
    }
    silentDownload();
    await copyToClipboard(shareUrl);
    toast.success("PNG saved + link copied. Upload it on TikTok.");
    setTimeout(() => {
      window.open("https://www.tiktok.com/upload", "_blank", "noopener,noreferrer");
    }, 350);
  };

  // Render: createPortal wraps the WHOLE AnimatePresence so the modal
  // escapes the framer-motion transformed parent (PostCard's motion.article)
  // that was previously trapping it inside a sub-stacking-context. The
  // earlier `<AnimatePresence>{createPortal(...)}</AnimatePresence>` shape
  // confused AnimatePresence's child tracking and the modal never mounted.
  if (typeof document === "undefined") return null;
  return createPortal(
    <AnimatePresence>
      {open ? (
        <motion.div
          className="fixed inset-0 z-[9999] flex items-end sm:items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          data-testid="share-card-modal"
        >
          {/* Off-screen full-size card for html2canvas */}
          <div
            aria-hidden
            style={{
              position: "fixed",
              left: "-100000px",
              top: 0,
              width: 1080,
              height: 1350,
              pointerEvents: "none",
            }}
          >
            <ShareCardCanvas
              refEl={cardRef}
              post={post}
              color={color}
              author={author}
              remaining={remaining}
            />
          </div>

          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 30, opacity: 0 }}
            transition={{ type: "spring", damping: 26, stiffness: 240 }}
            className="relative w-full sm:max-w-md glass-strong rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 m-0 sm:m-4 border border-white/10 max-h-[94vh] overflow-y-auto"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <h2 className="font-display text-2xl">Share this pluck</h2>
                <p className="text-sm text-zinc-400 mt-0.5">
                  Story-ready 1080×1350. Branded for $PNF.
                </p>
              </div>
              <button
                onClick={onClose}
                data-testid="close-share-modal"
                className="p-2 rounded-full hover:bg-white/5 text-zinc-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Live preview from rasterized blob */}
            <div
              className="mt-3 rounded-2xl overflow-hidden border border-white/10 bg-black aspect-[4/5] flex items-center justify-center"
              data-testid="share-card-preview"
            >
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Share card preview"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex flex-col items-center gap-2 text-zinc-500">
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span className="text-xs font-mono uppercase tracking-widest">
                    Rendering pluck card…
                  </span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4">
              <button
                onClick={handleDownload}
                disabled={busy || !blob}
                data-testid="share-download-btn"
                className="inline-flex items-center justify-center gap-2 rounded-full py-3 text-sm font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30 disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                Download PNG
              </button>
              <button
                onClick={handleNativeShare}
                disabled={busy || !blob}
                data-testid="share-native-btn"
                className="inline-flex items-center justify-center gap-2 rounded-full py-3 text-sm font-medium text-white bg-white/[0.06] border border-white/10 hover:bg-white/[0.1] transition disabled:opacity-50"
              >
                <Share2 className="w-4 h-4" />
                Share…
              </button>
            </div>

            <div className="mt-3">
              <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-zinc-500 mb-2">
                Share to
              </div>
              <div className="grid grid-cols-4 gap-2">
                <button
                  onClick={handleX}
                  data-testid="share-x-btn"
                  title="Post on X"
                  className="flex flex-col items-center justify-center gap-1 py-3 rounded-2xl bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] hover:border-white/25 text-white transition active:scale-95"
                >
                  <XMark className="w-5 h-5" />
                  <span className="text-[10px] font-mono uppercase tracking-wider">
                    X
                  </span>
                </button>
                <button
                  onClick={handleInstagram}
                  disabled={!blob}
                  data-testid="share-instagram-btn"
                  title="Share to Instagram"
                  className="flex flex-col items-center justify-center gap-1 py-3 rounded-2xl border transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed text-white"
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(225,48,108,0.20) 0%, rgba(245,133,41,0.18) 50%, rgba(64,93,230,0.20) 100%)",
                    borderColor: "rgba(225,48,108,0.45)",
                  }}
                >
                  <Instagram className="w-5 h-5" />
                  <span className="text-[10px] font-mono uppercase tracking-wider">
                    Instagram
                  </span>
                </button>
                <button
                  onClick={handleTikTok}
                  disabled={!blob}
                  data-testid="share-tiktok-btn"
                  title="Share to TikTok"
                  className="flex flex-col items-center justify-center gap-1 py-3 rounded-2xl bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] hover:border-white/25 text-white transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TikTokMark className="w-5 h-5" />
                  <span className="text-[10px] font-mono uppercase tracking-wider">
                    TikTok
                  </span>
                </button>
                <button
                  onClick={handleFacebook}
                  data-testid="share-facebook-btn"
                  title="Share to Facebook"
                  className="flex flex-col items-center justify-center gap-1 py-3 rounded-2xl bg-[rgba(24,119,242,0.12)] border border-[rgba(24,119,242,0.35)] hover:bg-[rgba(24,119,242,0.22)] text-white transition active:scale-95"
                >
                  <Facebook className="w-5 h-5" />
                  <span className="text-[10px] font-mono uppercase tracking-wider">
                    Facebook
                  </span>
                </button>
              </div>
            </div>

            <button
              onClick={handleCopyLink}
              data-testid="share-copy-link"
              className="mt-3 w-full inline-flex items-center justify-between gap-2 rounded-2xl px-4 py-3 text-xs font-mono text-zinc-300 bg-white/[0.04] border border-white/10 hover:text-white hover:border-purple-400/40 hover:bg-purple-500/10 transition"
            >
              <span className="flex items-center gap-2">
                <LinkIcon className="w-3.5 h-3.5" />
                <span className="uppercase tracking-wider">Copy post link</span>
              </span>
              <span className="truncate max-w-[60%] text-zinc-500 text-[10px]">
                {shareUrl.replace(/^https?:\/\//, "")}
              </span>
            </button>

            <p className="mt-3 text-[11px] leading-relaxed text-zinc-500">
              Instagram & TikTok don't allow auto-uploads from the web —
              we'll save the PNG and copy the post link so you can paste it
              into your Story or video caption.
            </p>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>,
    document.body,
  );
};

/** Off-screen, fixed-dimension card rendered to PNG by html2canvas. */
const ShareCardCanvas = ({ refEl, post, color, author, remaining }) => {
  return (
    <div
      ref={refEl}
      style={{
        width: 1080,
        height: 1350,
        position: "relative",
        overflow: "hidden",
        background:
          "radial-gradient(120% 80% at 15% 10%, rgba(176,38,255,0.55) 0%, rgba(176,38,255,0) 55%)," +
          "radial-gradient(120% 80% at 90% 90%, rgba(0,240,255,0.35) 0%, rgba(0,240,255,0) 60%)," +
          "linear-gradient(180deg, #0a0014 0%, #160030 50%, #07000f 100%)",
        color: "#ffffff",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
        padding: 72,
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Brand + expiry */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: "50%",
              background:
                "radial-gradient(circle at 30% 30%, #e9c2ff 0%, #b026ff 45%, #4a0080 100%)",
              boxShadow:
                "0 0 40px rgba(176,38,255,0.7), inset 0 0 18px rgba(255,255,255,0.35)",
            }}
          />
          <div
            style={{
              fontFamily:
                "ui-monospace, SFMono-Regular, Menlo, monospace",
              fontSize: 30,
              letterSpacing: 6,
              textTransform: "uppercase",
              color: "rgba(255,255,255,0.92)",
            }}
          >
            PLUTO
          </div>
        </div>
        <div
          style={{
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            fontSize: 22,
            padding: "10px 18px",
            borderRadius: 999,
            border: "1px solid rgba(255,255,255,0.18)",
            background: "rgba(255,255,255,0.04)",
            color: "rgba(255,255,255,0.8)",
            letterSpacing: 2,
          }}
        >
          {remaining ? `vanishes in ${remaining}` : "vanishes soon"}
        </div>
      </div>

      {/* Topic pill */}
      <div style={{ marginTop: 56 }}>
        <span
          style={{
            display: "inline-block",
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            fontSize: 26,
            letterSpacing: 4,
            textTransform: "uppercase",
            padding: "12px 24px",
            borderRadius: 999,
            color: color,
            background: `${color}1a`,
            border: `1px solid ${color}66`,
          }}
        >
          #{post.topic}
        </span>
      </div>

      {/* Body */}
      <div
        style={{
          marginTop: 44,
          flex: 1,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            fontSize: clampFontSize(post.content || ""),
            lineHeight: 1.25,
            fontWeight: 600,
            letterSpacing: -0.5,
            color: "#ffffff",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {truncate(post.content || "", 360)}
        </div>

        {post.image ? (
          <div
            style={{
              marginTop: 36,
              borderRadius: 28,
              overflow: "hidden",
              border: "1px solid rgba(255,255,255,0.1)",
              maxHeight: 460,
            }}
          >
            <img
              src={post.image}
              alt=""
              crossOrigin="anonymous"
              style={{
                display: "block",
                width: "100%",
                maxHeight: 460,
                objectFit: "cover",
              }}
            />
          </div>
        ) : null}
      </div>

      {/* Stats */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
          marginTop: 32,
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
          fontSize: 26,
        }}
      >
        <div
          style={{
            padding: "10px 20px",
            borderRadius: 999,
            border: "1px solid rgba(236,72,153,0.45)",
            background: "rgba(236,72,153,0.12)",
            color: "#fbcfe8",
          }}
        >
          ♥ {post.hugs ?? 0} HUG
        </div>
        <div
          style={{
            padding: "10px 20px",
            borderRadius: 999,
            border: "1px solid rgba(161,161,170,0.45)",
            background: "rgba(63,63,70,0.4)",
            color: "#e4e4e7",
          }}
        >
          ⏷ {post.fugs ?? 0} FUG
        </div>
        <div
          style={{
            marginLeft: "auto",
            color: "rgba(255,255,255,0.7)",
            fontSize: 24,
          }}
        >
          {author}
        </div>
      </div>

      {/* Divider */}
      <div
        style={{
          marginTop: 28,
          height: 1,
          background:
            "linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent)",
        }}
      />

      {/* Footer */}
      <div
        style={{
          marginTop: 18,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
          fontSize: 18,
          letterSpacing: 3,
          textTransform: "uppercase",
          color: "rgba(255,255,255,0.55)",
        }}
      >
        <span>🪐 A PAGE NOT FOUND · $PNF PRODUCT</span>
        <span>pluto.app</span>
      </div>
    </div>
  );
};

function clampFontSize(text) {
  const n = text.length;
  if (n <= 80) return 84;
  if (n <= 160) return 68;
  if (n <= 260) return 56;
  if (n <= 360) return 46;
  return 38;
}

function truncate(text, max) {
  if (text.length <= max) return text;
  return text.slice(0, max - 1).trimEnd() + "…";
}

export default ShareCardModal;
