import React from "react";

export function GlowingOrb({ isListening = false, isSpeaking = false, isThinking = false, size = "lg" }) {
  const sizeClasses = {
    sm: "w-28 h-28",
    md: "w-44 h-44 sm:w-52 sm:h-52",
    lg: "w-56 h-56 sm:w-64 sm:h-64"
  };

  return (
    <div className={`relative flex items-center justify-center ${sizeClasses[size] || sizeClasses.lg}`}>
      {/* Outer ambient colored glow */}
      <div
        className={`absolute inset-0 rounded-full bg-gradient-to-tr from-blue-500/30 via-indigo-500/30 to-purple-500/30 blur-2xl transition-all duration-700 ${
          isSpeaking
            ? "scale-130 opacity-100 from-indigo-500/40 via-purple-500/40 to-pink-500/40"
            : isListening
            ? "scale-125 opacity-100"
            : isThinking
            ? "scale-110 opacity-80"
            : "scale-100 opacity-60"
        }`}
      />

      {/* Outer subtle concentric decorative rings */}
      <div
        className={`absolute -inset-4 rounded-full border border-blue-400/20 animate-spin ${isSpeaking ? "border-purple-400/30" : ""}`}
        style={{ animationDuration: isSpeaking ? "18s" : "35s" }}
      />
      <div
        className={`absolute -inset-8 rounded-full border border-indigo-400/15 animate-spin ${isSpeaking ? "border-indigo-400/30" : ""}`}
        style={{ animationDuration: isSpeaking ? "25s" : "50s", animationDirection: "reverse" }}
      />

      {/* Dynamic Soundwave Rings during active listening or speaking */}
      {(isListening || isSpeaking) && (
        <>
          <div
            className={`absolute -inset-2 rounded-full animate-ping opacity-40 ${
              isSpeaking ? "border border-purple-400/60" : "border border-indigo-400/50"
            }`}
            style={{ animationDuration: isSpeaking ? "1.5s" : "2s" }}
          />
          <div
            className={`absolute -inset-6 rounded-full animate-ping opacity-30 ${
              isSpeaking ? "border border-pink-400/50" : "border border-purple-400/40"
            }`}
            style={{ animationDuration: isSpeaking ? "2.2s" : "2.8s", animationDelay: "0.3s" }}
          />
        </>
      )}

      {/* Luminous Glass Orb Body */}
      <div
        className={`relative w-full h-full rounded-full bg-gradient-to-br shadow-2xl ring-4 ring-white/40 flex items-center justify-center overflow-hidden transform transition-all duration-500 ${
          isSpeaking
            ? "from-indigo-600 via-purple-600 to-pink-600 shadow-purple-500/40 scale-105"
            : "from-blue-600 via-indigo-600 to-purple-700 shadow-indigo-500/35 hover:scale-[1.02]"
        }`}
      >
        {/* Specular Highlight Gloss */}
        <div className="absolute top-2 left-4 w-1/2 h-1/3 rounded-full bg-gradient-to-b from-white/45 to-transparent blur-[2px] transform -rotate-30 pointer-events-none" />

        {/* Inner Radial Shimmer */}
        <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_30%_30%,rgba(255,255,255,0.35),transparent_70%)] pointer-events-none" />

        {/* Dynamic Center State */}
        <div className="relative z-10 text-white flex items-center justify-center">
          {isSpeaking ? (
            /* Speaking Waveform (Dynamic & Fluid) */
            <div className="flex gap-1.5 items-center h-16 px-4">
              <span className="w-1.5 bg-white rounded-full animate-pulse shadow-xs" style={{ height: "26px", animationDuration: "0.45s", animationDelay: "0ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-pulse shadow-xs" style={{ height: "46px", animationDuration: "0.55s", animationDelay: "120ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-pulse shadow-xs" style={{ height: "54px", animationDuration: "0.4s", animationDelay: "240ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-pulse shadow-xs" style={{ height: "38px", animationDuration: "0.5s", animationDelay: "360ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-pulse shadow-xs" style={{ height: "20px", animationDuration: "0.42s", animationDelay: "480ms" }} />
            </div>
          ) : isListening ? (
            /* Listening Equalizer Sound Waves */
            <div className="flex gap-1.5 items-center h-16 px-4">
              <span className="w-1.5 bg-white/90 rounded-full animate-bounce shadow-xs" style={{ height: "18px", animationDuration: "0.8s", animationDelay: "0ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "34px", animationDuration: "0.7s", animationDelay: "150ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "48px", animationDuration: "0.6s", animationDelay: "300ms" }} />
              <span className="w-1.5 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "30px", animationDuration: "0.75s", animationDelay: "450ms" }} />
              <span className="w-1.5 bg-white/90 rounded-full animate-bounce shadow-xs" style={{ height: "16px", animationDuration: "0.85s", animationDelay: "600ms" }} />
            </div>
          ) : isThinking ? (
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 rounded-full border-3 border-white/30 border-t-white animate-spin" />
              <span className="text-[11px] font-medium tracking-wide text-white/90">Thinking...</span>
            </div>
          ) : (
            /* Idle Ready Glow Pulse */
            <div className="relative flex items-center justify-center">
              <div className="w-5 h-5 rounded-full bg-white shadow-lg shadow-white/50" />
              <div className="absolute w-8 h-8 rounded-full bg-white/30 animate-ping" style={{ animationDuration: "2.5s" }} />
            </div>
          )}
        </div>

        {/* Ambient bottom light */}
        <div className="absolute bottom-0 inset-x-0 h-1/3 bg-gradient-to-t from-purple-900/60 to-transparent pointer-events-none" />
      </div>
    </div>
  );
}
