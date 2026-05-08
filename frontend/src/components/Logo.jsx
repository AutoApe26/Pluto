import React from "react";

export const Logo = ({ size = 32 }) => (
  <div
    className="relative inline-flex items-center justify-center rounded-full"
    style={{ width: size, height: size }}
    data-testid="pluto-logo"
  >
    <div
      className="absolute inset-0 rounded-full"
      style={{
        background:
          "radial-gradient(circle at 30% 30%, #00F0FF, #B026FF 60%, #2A0844)",
        boxShadow:
          "0 0 18px rgba(0,240,255,0.55), inset -6px -8px 16px rgba(0,0,0,0.6)",
      }}
    />
    <div
      className="absolute"
      style={{
        width: size * 1.6,
        height: size * 0.32,
        border: "1px solid rgba(255,255,255,0.18)",
        borderRadius: "50%",
        transform: "rotate(-18deg)",
      }}
    />
  </div>
);

export default Logo;
