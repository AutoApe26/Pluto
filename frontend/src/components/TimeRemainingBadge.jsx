import React, { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { timeRemaining } from "../lib/format";

export const TimeRemainingBadge = ({ expiresAt }) => {
  const [t, setT] = useState(timeRemaining(expiresAt));
  useEffect(() => {
    const id = setInterval(() => setT(timeRemaining(expiresAt)), 30000);
    return () => clearInterval(id);
  }, [expiresAt]);
  const danger = t.includes("m") && !t.includes("h") && parseInt(t) < 60;
  return (
    <div
      data-testid="time-remaining-badge"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider pulse-soft border ${
        danger
          ? "border-red-500/40 text-red-300 bg-red-500/10"
          : "border-cyan-300/30 text-cyan-200 bg-cyan-300/5"
      }`}
    >
      <Clock className="w-3 h-3" />
      {t}
    </div>
  );
};

export default TimeRemainingBadge;
