import React from "react";

export const CosmicBg = ({ variant = "default" }) => {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="aurora-blob"
        style={{
          width: 560,
          height: 560,
          background:
            "radial-gradient(closest-side, rgba(140,80,230,0.35), transparent)",
          top: -160,
          right: "10%",
        }}
      />
      <div
        className="aurora-blob"
        style={{
          width: 640,
          height: 640,
          background:
            "radial-gradient(closest-side, rgba(80,30,160,0.30), transparent)",
          top: "30%",
          right: -240,
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
              "radial-gradient(closest-side, rgba(60,25,120,0.30), transparent)",
            bottom: -200,
            left: "-10%",
            animationDelay: "-10s",
          }}
        />
      )}
      <div className="grain absolute inset-0" />
    </div>
  );
};

export default CosmicBg;
