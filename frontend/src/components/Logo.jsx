import React from "react";

// Real PNG asset extracted from the brand reference.
const ORB_SRC = "/assets/pluto-orb.png";

// Small header / inline logo
export const Logo = ({ size = 32 }) => (
  <div
    className="relative inline-flex items-center justify-center"
    style={{ width: size, height: size }}
    data-testid="pluto-logo"
  >
    <img
      src={ORB_SRC}
      alt="Pluto"
      draggable={false}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        filter: "drop-shadow(0 0 6px rgba(60,180,255,0.45))",
        userSelect: "none",
      }}
    />
  </div>
);

// Big hero sphere — uses the brand PNG with an extra cyan halo glow underneath
// to match the landing page reference.
export const PlutoSphere = ({ size = 180 }) => {
  const w = size;
  const h = size * 1.45; // extra room for the halo glow beneath
  return (
    <div
      className="relative inline-block"
      style={{ width: w, height: h }}
      data-testid="pluto-sphere"
    >
      {/* Strong cyan halo glow underneath the orb */}
      <div
        className="absolute"
        style={{
          left: "50%",
          top: size * 0.78,
          transform: "translateX(-50%)",
          width: w * 0.95,
          height: size * 0.45,
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
          top: 0,
          transform: "translate(-50%, -10%)",
          width: w * 1.05,
          height: size * 1.05,
          background:
            "radial-gradient(circle at 50% 45%, rgba(120,80,220,0.30), transparent 60%)",
          filter: "blur(22px)",
          pointerEvents: "none",
        }}
      />
      {/* The actual orb image */}
      <img
        src={ORB_SRC}
        alt="Pluto"
        draggable={false}
        className="absolute left-1/2 top-0"
        style={{
          width: size,
          height: size,
          transform: "translateX(-50%)",
          objectFit: "contain",
          filter: "drop-shadow(0 10px 28px rgba(60,180,255,0.35))",
          userSelect: "none",
        }}
      />
    </div>
  );
};

export default Logo;
