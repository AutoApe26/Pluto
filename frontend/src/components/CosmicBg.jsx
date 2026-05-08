import React from "react";

export const CosmicBg = ({ variant = "default" }) => {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="aurora-blob"
        style={{
          width: 520,
          height: 520,
          background:
            "radial-gradient(closest-side, rgba(0,240,255,0.55), transparent)",
          top: -120,
          left: -120,
        }}
      />
      <div
        className="aurora-blob"
        style={{
          width: 600,
          height: 600,
          background:
            "radial-gradient(closest-side, rgba(176,38,255,0.45), transparent)",
          top: "30%",
          right: -180,
          animationDelay: "-6s",
        }}
      />
      {variant === "default" && (
        <div
          className="aurora-blob"
          style={{
            width: 480,
            height: 480,
            background:
              "radial-gradient(closest-side, rgba(123,97,255,0.35), transparent)",
            bottom: -160,
            left: "30%",
            animationDelay: "-10s",
          }}
        />
      )}
      <div className="grain absolute inset-0" />
    </div>
  );
};

export default CosmicBg;
