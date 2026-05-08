import React from "react";

// Real PNG asset extracted from the brand reference.
const ORB_SRC = "/assets/pluto-orb.png";

// Small header / inline logo — gentle breathing glow
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
      className="pluto-logo-breath"
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        userSelect: "none",
      }}
    />
  </div>
);

// Big hero sphere — uses the brand PNG with a breathing dim/bright glow.
export const PlutoSphere = ({ size = 180 }) => {
  const w = size;
  const h = size * 1.45; // extra room for the halo glow beneath
  return (
    <div
      className="relative inline-block"
      style={{ width: w, height: h }}
      data-testid="pluto-sphere"
    >
      {/* Strong cyan halo glow underneath the orb (breathing) */}
      <div
        className="absolute pluto-breath"
        style={{
          left: "50%",
          top: size * 0.78,
          width: w * 0.95,
          height: size * 0.45,
          background:
            "radial-gradient(ellipse at center, rgba(60,180,255,0.65) 0%, rgba(60,180,255,0.20) 40%, transparent 70%)",
          filter: "blur(18px)",
          pointerEvents: "none",
        }}
      />
      {/* Soft purple ambient halo behind the orb (slower breathing) */}
      <div
        className="absolute pluto-breath"
        style={{
          left: "50%",
          top: 0,
          width: w * 1.05,
          height: size * 1.05,
          background:
            "radial-gradient(circle at 50% 45%, rgba(140,90,240,0.45), transparent 60%)",
          filter: "blur(22px)",
          pointerEvents: "none",
          animationDuration: "5s",
          animationDelay: "0.8s",
        }}
      />
      {/* The actual orb image — drop-shadow breathes between dim and bright */}
      <img
        src={ORB_SRC}
        alt="Pluto"
        draggable={false}
        className="absolute left-1/2 top-0 pluto-orb-breath"
        style={{
          width: size,
          height: size,
          transform: "translateX(-50%)",
          objectFit: "contain",
          userSelect: "none",
        }}
      />
    </div>
  );
};

export default Logo;
