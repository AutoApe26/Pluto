import React from "react";

/**
 * Compact red badge used to mark posts flagged as Explicit (confession
 * topic, lyrics-toggled posts, or auto-detected profanity/drug/sexual
 * content). Visually distinct from the Parental Advisory lyrics badge
 * so a single post with both flags reads correctly.
 */
export const ExplicitBadge = ({ size = "sm", testId }) => {
  const px = size === "lg" ? "px-2 py-0.5 text-[10px]" : "px-1.5 py-0.5 text-[9px]";
  return (
    <span
      data-testid={testId || "explicit-badge"}
      title="Auto-flagged: contains explicit or 18+ language."
      className={`inline-flex items-center gap-1 rounded-md font-mono uppercase tracking-widest font-bold text-white bg-red-600/95 border border-red-300/40 shadow-sm shadow-red-500/30 ${px}`}
    >
      <span className="px-1 py-[1px] bg-white text-red-600 rounded-sm font-extrabold">
        18+
      </span>
      Explicit
    </span>
  );
};

export default ExplicitBadge;
