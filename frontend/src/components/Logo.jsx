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

// Big hero sphere — egg-shaped pluto orb with a magenta moon highlight,
// cyan crescent and a soft cyan halo glow underneath.
export const PlutoSphere = ({ size = 180 }) => {
  const w = size;
  const h = size * 1.05;
  return (
    <div
      className="relative inline-block"
      style={{ width: w, height: h * 1.45 }}
      data-testid="pluto-sphere"
    >
      {/* Strong cyan halo glow underneath the orb */}
      <div
        className="absolute"
        style={{
          left: "50%",
          top: h * 0.78,
          transform: "translateX(-50%)",
          width: w * 0.95,
          height: h * 0.45,
          background:
            "radial-gradient(ellipse at center, rgba(60,180,255,0.55) 0%, rgba(60,180,255,0.18) 40%, transparent 70%)",
          filter: "blur(18px)",
          pointerEvents: "none",
        }}
      />
      {/* Soft purple ambient halo behind the orb */}
      <div
        className="absolute"
        style={{
          left: "50%",
          top: h * 0.05,
          transform: "translate(-50%, -10%)",
          width: w * 0.95,
          height: h * 0.95,
          background:
            "radial-gradient(circle at 50% 45%, rgba(120,80,220,0.30), transparent 60%)",
          filter: "blur(22px)",
          pointerEvents: "none",
        }}
      />
      {/* Egg body — taller than wide, tilted slightly */}
      <div
        className="absolute left-1/2 top-0"
        style={{
          width: w * 0.62,
          height: h * 0.72,
          transform: "translateX(-50%) rotate(-10deg)",
          borderRadius: "50%",
          background:
            "radial-gradient(ellipse at 35% 35%, #1a1738 0%, #0c0a22 50%, #050416 100%)",
          boxShadow:
            "inset -10px -14px 28px rgba(0,0,0,0.95), inset 8px 10px 22px rgba(60,40,140,0.18), 0 12px 50px rgba(60,180,255,0.18)",
          overflow: "hidden",
        }}
      >
        {/* Pink/magenta moon highlight (top-right) */}
        <span
          className="absolute"
          style={{
            top: "26%",
            right: "22%",
            width: w * 0.07,
            height: w * 0.07,
            borderRadius: "50%",
            background:
              "radial-gradient(circle at 35% 35%, #ff6cb8 0%, #c84691 60%, transparent 80%)",
            boxShadow: "0 0 14px rgba(255,108,184,0.7)",
          }}
        />
        {/* Cyan crescent rim-light (bottom-left) */}
        <span
          className="absolute"
          style={{
            bottom: "12%",
            left: "8%",
            width: w * 0.32,
            height: w * 0.18,
            background:
              "radial-gradient(ellipse at 30% 60%, rgba(60,200,255,0.85) 0%, rgba(60,200,255,0.25) 40%, transparent 70%)",
            filter: "blur(2px)",
          }}
        />
        {/* Inner cyan glow at the very bottom edge */}
        <span
          className="absolute"
          style={{
            bottom: "-2%",
            left: "30%",
            width: w * 0.32,
            height: w * 0.06,
            background:
              "radial-gradient(ellipse at 50% 50%, rgba(80,220,255,0.9), transparent 70%)",
            filter: "blur(3px)",
          }}
        />
      </div>
    </div>
  );
};

export default Logo;
