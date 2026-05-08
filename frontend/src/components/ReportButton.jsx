import React, { useState } from "react";
import { Flag } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";

export const ReportButton = ({ targetType, targetId }) => {
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const handle = async (e) => {
    e.stopPropagation();
    if (busy || done) return;
    setBusy(true);
    try {
      await api.report(targetType, targetId);
      setDone(true);
      toast.success("Report submitted. Thank you.");
    } catch {
      toast.error("Couldn't submit report");
    } finally {
      setBusy(false);
    }
  };
  return (
    <button
      onClick={handle}
      disabled={busy || done}
      data-testid={`report-${targetType}-${targetId}`}
      className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full transition-all ${
        done
          ? "text-zinc-500"
          : "text-zinc-400 hover:text-red-300 hover:bg-red-500/10"
      }`}
      title="Report"
    >
      <Flag className="w-3.5 h-3.5" />
      <span className="hidden sm:inline">{done ? "Reported" : "Report"}</span>
    </button>
  );
};

export default ReportButton;
