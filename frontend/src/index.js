import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Silence noisy errors from browser extensions (MetaMask, Phantom, etc.)
// that auto-inject scripts into every page. They have nothing to do with
// the Pluto app but otherwise trip React's dev error overlay.
const isExtensionError = (msg, src) => {
  const s = `${msg || ""} ${src || ""}`;
  return (
    s.includes("chrome-extension://") ||
    s.includes("moz-extension://") ||
    /Failed to connect to MetaMask/i.test(s)
  );
};
window.addEventListener(
  "error",
  (e) => {
    if (isExtensionError(e.message, e.filename)) {
      e.stopImmediatePropagation();
      e.preventDefault();
    }
  },
  true,
);
window.addEventListener(
  "unhandledrejection",
  (e) => {
    const reason = e?.reason;
    const msg = typeof reason === "string" ? reason : reason?.message;
    const stack = reason?.stack || "";
    if (isExtensionError(msg, stack)) {
      e.stopImmediatePropagation();
      e.preventDefault();
    }
  },
  true,
);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
