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
 *
 * Accepts EITHER a `post` prop (text post) OR a `track` prop (music). The
 * card layout adapts automatically — music cards show the cover art, title,
 * artist, provider badge and hugs/fugs; post cards keep the original
 * text-first layout.
 */
export const ShareCardModal = ({ open, onClose, post, track }) => {
  // Normalize: treat either prop uniformly. We keep `post` semantics
  // (id, hugs, fugs, expires_at, sudo_name, device_id, topic) and add
  // music-specific fields when a track is passed.
  const isMusic = !!track && !post;
  const item = isMusic
    ? {
        id: track.id,
        topic: "music",
        content: track.caption || "",
        title: track.title,
        artist: track.artist,
        provider: track.provider,
        cover: track.cover || track.thumbnail,
        hugs: track.hugs ?? 0,
        fugs: track.fugs ?? 0,
        expires_at: track.expires_at,
        sudo_name: track.sudo_name,
        device_id: track.device_id,
        is_lyrics: track.is_lyrics,
        lang: track.lang,
      }
    : post;

  const cardRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [blob, setBlob] = useState(null);
  const [busy, setBusy] = useState(false);
  const [remaining, setRemaining] = useState(
    item ? timeRemaining(item.expires_at) : ""
  );

  // Tick the expiry timer while open
  useEffect(() => {
    if (!open || !item) return;
    setRemaining(timeRemaining(item.expires_at));
    const id = setInterval(
      () => setRemaining(timeRemaining(item.expires_at)),
      30 * 1000
    );
    return () => clearInterval(id);
  }, [open, item]);

  // Reset cached PNG when modal closes
  useEffect(() => {
    if (open) return;
    setPreviewUrl((u) => {
      if (u) URL.revokeObjectURL(u);
      return null;
    });
    setBlob(null);
  }, [open]);

  // Lazy renderer — only runs when the user actually requests a
  // download or social share. The visual preview shown in the modal is
  // the live HTML card scaled with CSS, so opening the modal is INSTANT.
  // Caches the rendered blob so subsequent clicks don't re-rasterize.
  const ensureRendered = async () => {
    if (blob && previewUrl) return { blob, url: previewUrl };
    setBusy(true);
    try {
      // Give the (already-mounted) card one frame to settle
      await new Promise((r) => requestAnimationFrame(r));
      if (!cardRef.current) throw new Error("card not mounted");
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
      if (!b) throw new Error("blob render failed");
      const url = URL.createObjectURL(b);
      setBlob(b);
      setPreviewUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
      return { blob: b, url };
    } catch (e) {
      console.error("share card render failed", e);
      toast.error("Couldn't render share card");
      return null;
    } finally {
      setBusy(false);
    }
  };

  if (!item) return null;
  const color = TOPIC_COLORS[item.topic] || "#00F0FF";
  const author = item.sudo_name || `anon · ${item.device_id?.slice(-6) || ""}`;
  // Direct link to the specific post/track — anyone with this URL can open
  // it even if they aren't running the app yet.
  const shareUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}${isMusic ? "/music" : "/post/" + item.id}`
      : "";

  const safeId = item.id?.slice(0, 8) || (isMusic ? "track" : "post");

  const handleDownload = async () => {
    const r = blob && previewUrl ? { blob, url: previewUrl } : await ensureRendered();
    if (!r) return;
    const a = document.createElement("a");
    a.href = r.url;
    a.download = `pluto-${isMusic ? "track" : "post"}-${safeId}.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast.success("Saved to your device");
  };

  // Internal: download the PNG silently (used by Instagram/TikTok flow)
  const silentDownload = (b, url) => {
    if (!b || !url) return false;
    const a = document.createElement("a");
    a.href = url;
    a.download = `pluto-${isMusic ? "track" : "post"}-${safeId}.png`;
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

  const shareText = isMusic
    ? `${item.title ? `"${item.title}"` : "this track"}${item.artist ? ` by ${item.artist}` : ""} — found on Pluto.`
    : "Saw this on Pluto. Vanishes in 24h.";

  const handleNativeShare = async () => {
    const r = blob && previewUrl ? { blob, url: previewUrl } : await ensureRendered();
    if (!r) return;
    const file = new File([r.blob], `pluto-${safeId}.png`, {
      type: "image/png",
    });
    const shareData = {
      title: "Pluto",
      text: shareText,
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
          text: shareText,
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
    if (ok) toast.success("Link copied — paste it anywhere");
    else toast.error("Couldn't copy link");
  };

  const handleX = () => {
    const text = encodeURIComponent(shareText);
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
    const r = blob && previewUrl ? { blob, url: previewUrl } : await ensureRendered();
    if (!r) return;
    silentDownload(r.blob, r.url);
    await copyToClipboard(shareUrl);
    toast.success("PNG saved + link copied. Upload it as your Story.");
    setTimeout(() => {
      window.open("https://www.instagram.com/", "_blank", "noopener,noreferrer");
    }, 350);
  };

  const handleTikTok = async () => {
    const r = blob && previewUrl ? { blob, url: previewUrl } : await ensureRendered();
    if (!r) return;
    silentDownload(r.blob, r.url);
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
              item={item}
              isMusic={isMusic}
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
            className="relative w-full sm:max-w-md glass-strong rounded-t-3xl sm:rounded-3xl border border-white/10 m-0 sm:m-4 max-h-[94vh] flex flex-col overflow-hidden"
            style={{ paddingBottom: "max(env(safe-area-inset-bottom), 0px)" }}
          >
            {/* Drag handle on mobile */}
            <div className="sm:hidden flex justify-center pt-2.5 pb-1 shrink-0">
              <span className="block w-10 h-1 rounded-full bg-white/20" />
            </div>

            {/* Header */}
            <div className="flex items-start justify-between px-5 sm:px-6 pt-3 sm:pt-6 pb-2 shrink-0">
              <div>
                <h2 className="font-display text-xl sm:text-2xl">
                  {isMusic ? "Share this track" : "Share this pluck"}
                </h2>
                <p className="text-xs sm:text-sm text-zinc-400 mt-0.5">
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

            {/* Scrollable middle: preview + copy link */}
            <div className="flex-1 overflow-y-auto px-5 sm:px-6 pb-3">
              <div
                className="rounded-2xl overflow-hidden border border-white/10 bg-black aspect-[4/5] relative"
                data-testid="share-card-preview"
              >
                {/*
                  Live, scaled-down HTML preview of the share card.
                  Renders INSTANTLY (zero rasterization) so the modal
                  feels snappy. The actual PNG is generated lazily by
                  ensureRendered() when the user clicks Download or any
                  social share button.
                */}
                <ShareCardPreview
                  item={item}
                  isMusic={isMusic}
                  color={color}
                  author={author}
                  remaining={remaining}
                />
                {busy && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-[2px] text-zinc-200">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-xs font-mono uppercase tracking-widest">
                        Saving PNG…
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={handleCopyLink}
                data-testid="share-copy-link"
                className="mt-3 w-full inline-flex items-center justify-between gap-2 rounded-2xl px-4 py-3 text-xs font-mono text-zinc-300 bg-white/[0.04] border border-white/10 hover:text-white hover:border-purple-400/40 hover:bg-purple-500/10 transition"
              >
                <span className="flex items-center gap-2">
                  <LinkIcon className="w-3.5 h-3.5" />
                  <span className="uppercase tracking-wider">
                    {isMusic ? "Copy track link" : "Copy post link"}
                  </span>
                </span>
                <span className="truncate max-w-[55%] text-zinc-500 text-[10px]">
                  {shareUrl.replace(/^https?:\/\//, "")}
                </span>
              </button>

              <p className="mt-3 text-[11px] leading-relaxed text-zinc-500">
                Instagram & TikTok don't allow auto-uploads from the web —
                we'll save the PNG and copy the post link so you can paste it
                into your Story or video caption.
              </p>
            </div>

            {/* Sticky bottom action bar: Download + horizontally scrollable socials */}
            <div className="shrink-0 border-t border-white/10 bg-[#0b0218]/85 backdrop-blur-xl px-3 sm:px-4 pt-3 pb-3">
              <button
                onClick={handleDownload}
                disabled={busy}
                data-testid="share-download-btn"
                className="w-full inline-flex items-center justify-center gap-2 rounded-full py-3 text-sm font-medium text-white bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 hover:opacity-95 transition shadow-lg shadow-purple-500/30 disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                Download PNG
              </button>

              <div className="mt-3 flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-[0.25em] text-zinc-500 shrink-0 pl-1">
                  Share to
                </span>
                <div
                  className="flex-1 min-w-0 flex items-center gap-2 overflow-x-auto scrollbar-hide -mx-1 px-1 snap-x snap-mandatory"
                  data-testid="share-socials-row"
                  role="toolbar"
                  aria-label="Share to social networks"
                >
                  {[
                    {
                      key: "x",
                      label: "X",
                      icon: <XMark className="w-5 h-5" />,
                      onClick: handleX,
                      testid: "share-x-btn",
                      bg: "bg-black",
                      ring: "ring-white/25",
                    },
                    {
                      key: "instagram",
                      label: "Instagram",
                      icon: <Instagram className="w-5 h-5" />,
                      onClick: handleInstagram,
                      testid: "share-instagram-btn",
                      bg:
                        "bg-gradient-to-br from-[#feda77] via-[#d62976] to-[#4f5bd5]",
                      ring: "ring-pink-400/40",
                    },
                    {
                      key: "tiktok",
                      label: "TikTok",
                      icon: <TikTokMark className="w-5 h-5" />,
                      onClick: handleTikTok,
                      testid: "share-tiktok-btn",
                      bg: "bg-black",
                      ring: "ring-cyan-300/40",
                    },
                    {
                      key: "facebook",
                      label: "Facebook",
                      icon: <Facebook className="w-5 h-5" />,
                      onClick: handleFacebook,
                      testid: "share-facebook-btn",
                      bg: "bg-[#1877f2]",
                      ring: "ring-[#1877f2]/50",
                    },
                    {
                      key: "more",
                      label: "More",
                      icon: <Share2 className="w-5 h-5" />,
                      onClick: handleNativeShare,
                      testid: "share-native-btn",
                      bg: "bg-white/[0.08]",
                      ring: "ring-white/20",
                    },
                  ].map((opt) => (
                    <button
                      key={opt.key}
                      type="button"
                      onClick={opt.onClick}
                      data-testid={opt.testid}
                      className="snap-start shrink-0 flex flex-col items-center justify-center gap-1.5 px-1.5 py-1 rounded-2xl hover:bg-white/[0.04] transition group"
                      aria-label={`Share to ${opt.label}`}
                    >
                      <span
                        className={`flex items-center justify-center w-11 h-11 sm:w-12 sm:h-12 rounded-full text-white ring-1 ${opt.bg} ${opt.ring} group-hover:scale-105 group-active:scale-95 transition-transform shadow-md shadow-black/40`}
                      >
                        {opt.icon}
                      </span>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-300 group-hover:text-white transition">
                        {opt.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>,
    document.body,
  );
};

/** Live (non-rasterized) preview rendered directly with CSS. Uses the
 *  same internal layout as ShareCardCanvas but scales to fit the
 *  modal's preview slot via a CSS transform computed from a
 *  ResizeObserver — so the preview shows up INSTANTLY (no
 *  html2canvas wait) and stays crisp at any modal width.
 */
const ShareCardPreview = ({ item, isMusic, color, author, remaining }) => {
  const wrapRef = useRef(null);
  const [scale, setScale] = useState(0.3);

  useEffect(() => {
    if (!wrapRef.current) return;
    const el = wrapRef.current;
    const recompute = () => {
      const w = el.clientWidth;
      if (w > 0) setScale(w / 1080);
    };
    recompute();
    const ro = new ResizeObserver(recompute);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return (
    <div
      ref={wrapRef}
      className="absolute inset-0 overflow-hidden"
      data-testid="share-card-live-preview"
    >
      <div
        style={{
          width: 1080,
          height: 1350,
          transform: `scale(${scale})`,
          transformOrigin: "top left",
        }}
      >
        <ShareCardCanvas
          refEl={null}
          item={item}
          isMusic={isMusic}
          color={color}
          author={author}
          remaining={remaining}
        />
      </div>
    </div>
  );
};

/** Off-screen, fixed-dimension card rendered to PNG by html2canvas.
 *  Renders either a text-post layout or a music-track layout depending
 *  on the `isMusic` flag. */
const ShareCardCanvas = ({ refEl, item, isMusic, color, author, remaining }) => {
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
      <div style={{ marginTop: 56, display: "flex", gap: 14, flexWrap: "wrap" }}>
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
          #{item.topic}
        </span>
        {isMusic && item.provider && (
          <span
            style={{
              display: "inline-block",
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
              fontSize: 22,
              letterSpacing: 3,
              textTransform: "uppercase",
              padding: "12px 22px",
              borderRadius: 999,
              color:
                item.provider === "spotify" ? "#1ed760" : "#ff4d4d",
              background:
                item.provider === "spotify"
                  ? "rgba(30,215,96,0.12)"
                  : "rgba(255,77,77,0.12)",
              border:
                item.provider === "spotify"
                  ? "1px solid rgba(30,215,96,0.45)"
                  : "1px solid rgba(255,77,77,0.45)",
            }}
          >
            ♫ {item.provider}
          </span>
        )}
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
        {isMusic ? (
          <MusicCanvasBody item={item} />
        ) : (
          <PostCanvasBody item={item} />
        )}
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
          ♥ {item.hugs ?? 0} HUG
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
          ⏷ {item.fugs ?? 0} FUG
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

/** Text-post body — original layout. */
const PostCanvasBody = ({ item }) => (
  <>
    <div
      style={{
        fontSize: clampFontSize(item.content || ""),
        lineHeight: 1.25,
        fontWeight: 600,
        letterSpacing: -0.5,
        color: "#ffffff",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      {truncate(item.content || "", 360)}
    </div>

    {item.image ? (
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
          src={item.image}
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
  </>
);

/** Music-track body — cover art + song title + artist + optional caption. */
const MusicCanvasBody = ({ item }) => {
  const title = item.title || "Untitled track";
  const artist = item.artist || "";
  return (
    <>
      {item.cover ? (
        <div
          style={{
            borderRadius: 32,
            overflow: "hidden",
            border: "1px solid rgba(255,255,255,0.12)",
            boxShadow: "0 30px 80px rgba(0,0,0,0.5)",
            width: 420,
            height: 420,
            marginBottom: 28,
          }}
        >
          <img
            src={item.cover}
            alt=""
            crossOrigin="anonymous"
            style={{
              display: "block",
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      ) : null}

      <div
        style={{
          fontSize: clampSongTitleSize(title),
          lineHeight: 1.05,
          fontWeight: 800,
          letterSpacing: -1,
          color: "#ffffff",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          textShadow: "0 0 30px rgba(176,38,255,0.5)",
        }}
      >
        {truncate(title, 90)}
      </div>

      {artist ? (
        <div
          style={{
            marginTop: 12,
            fontSize: 36,
            color: "rgba(255,255,255,0.78)",
            fontWeight: 500,
            letterSpacing: -0.3,
          }}
        >
          by {truncate(artist, 70)}
        </div>
      ) : null}

      {item.content ? (
        <div
          style={{
            marginTop: 22,
            fontSize: 26,
            lineHeight: 1.35,
            color: "rgba(255,255,255,0.7)",
            fontStyle: item.is_lyrics ? "italic" : "normal",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {item.is_lyrics ? "♫ " : ""}
          {truncate(item.content, 220)}
        </div>
      ) : null}
    </>
  );
};

function clampSongTitleSize(text) {
  const n = (text || "").length;
  if (n <= 18) return 96;
  if (n <= 30) return 80;
  if (n <= 50) return 64;
  return 52;
}

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
