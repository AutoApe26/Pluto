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

// Big hero sphere - dark with glowing blue core, used on landing/info hero sections
export const PlutoSphere = ({ size = 180 }) => (
  <div
    className="relative inline-block"
    style={{ width: size, height: size }}
    data-testid="pluto-sphere"
  >
    {/* Outer halo */}
    <div
      className="absolute inset-0 rounded-full"
      style={{
        background:
          "radial-gradient(circle, rgba(0,240,255,0.25), transparent 60%)",
        filter: "blur(20px)",
      }}
    />
    {/* Sphere body */}
    <div
      className="absolute rounded-full"
      style={{
        inset: size * 0.12,
        background:
          "radial-gradient(circle at 35% 30%, #1a1d2b 0%, #0a0a14 60%, #02020a 100%)",
        boxShadow:
          "inset -10px -14px 30px rgba(0,0,0,0.9), inset 8px 10px 24px rgba(0,240,255,0.05)",
      }}
    />
    {/* Glowing blue core - top-right inner highlight */}
    <div
      className="absolute rounded-full pulse-soft"
      style={{
        width: size * 0.22,
        height: size * 0.22,
        top: size * 0.18,
        left: size * 0.52,
        background:
          "radial-gradient(circle, #00F0FF 0%, rgba(0,240,255,0.55) 35%, transparent 70%)",
        filter: "blur(2px)",
      }}
    />
    {/* Crater accents */}
    <div
      className="absolute rounded-full"
      style={{
        width: size * 0.08,
        height: size * 0.08,
        top: size * 0.55,
        left: size * 0.32,
        background: "rgba(0,0,0,0.6)",
        boxShadow: "inset 1px 1px 2px rgba(255,255,255,0.05)",
      }}
    />
    <div
      className="absolute rounded-full"
      style={{
        width: size * 0.05,
        height: size * 0.05,
        top: size * 0.7,
        left: size * 0.5,
        background: "rgba(0,0,0,0.5)",
      }}
    />
    {/* Subtle ring */}
    <div
      className="absolute"
      style={{
        width: size * 1.4,
        height: size * 0.28,
        top: size * 0.42,
        left: -size * 0.2,
        border: "1px solid rgba(0,240,255,0.18)",
        borderRadius: "50%",
        transform: "rotate(-14deg)",
        boxShadow: "0 0 18px rgba(0,240,255,0.15)",
      }}
    />
  </div>
);

export default Logo;
