import React from "react";

export function GlowingOrb({ isListening = false, isThinking = false, size = "md" }) {
  const sizeClasses = {
    sm: "w-24 h-24",
    md: "w-48 h-48 sm:w-56 sm:h-56",
    lg: "w-64 h-64 sm:w-80 sm:h-80"
  };

  return (
    <div className={`relative flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}`}>
      {/* Soft ambient halo */}
      <div
        className={`absolute inset-0 rounded-full bg-blue-100 opacity-80 transition-all duration-700 ${
          isThinking || isListening ? "scale-110" : "scale-100"
        }`}
      />

      {/* Subtle rotating rings */}
      <div
        className="absolute -inset-3 rounded-full border border-blue-200 animate-spin"
        style={{ animationDuration: "30s" }}
      />
      <div
        className="absolute -inset-6 rounded-full border border-blue-100 animate-spin"
        style={{ animationDuration: "45s", animationDirection: "reverse" }}
      />

      {/* Active wave ring during voice or thinking */}
      {(isListening || isThinking) && (
        <div className="absolute inset-0 rounded-full border border-blue-400 animate-ping opacity-50" />
      )}

      {/* Solid orb core */}
      <div className="relative w-full h-full rounded-full bg-gradient-to-br from-blue-800 to-blue-950 shadow-xl flex items-center justify-center overflow-hidden">
        <div className="absolute top-3 left-4 w-1/3 h-1/3 rounded-full bg-white/20 blur-md transform -rotate-45 pointer-events-none" />

        <div className="relative z-10 text-white">
          {isListening ? (
            <div className="flex gap-1.5 items-end">
              <span className="w-1.5 h-6 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-10 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-7 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="w-1.5 h-11 bg-white rounded-full animate-bounce" style={{ animationDelay: '450ms' }} />
              <span className="w-1.5 h-5 bg-white rounded-full animate-bounce" style={{ animationDelay: '600ms' }} />
            </div>
          ) : isThinking ? (
            <div className="w-8 h-8 rounded-full border-2 border-white border-t-transparent animate-spin" />
          ) : (
            <div className="w-4 h-4 rounded-full bg-white/90" />
          )}
        </div>
      </div>
    </div>
  );
}
