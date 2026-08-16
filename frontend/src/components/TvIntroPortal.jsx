import React, { useState, useEffect } from "react";
import { Sparkles, Tv, ArrowRight, Zap, ShieldCheck } from "lucide-react";

export function TvIntroPortal({ onComplete }) {
  const [phase, setPhase] = useState("enter"); // 'enter' -> 'zoom' -> 'complete'
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 2.5;
      });
    }, 45);

    // Transition to zoom phase at ~1.9s
    const zoomTimer = setTimeout(() => {
      setPhase("zoom");
    }, 2000);

    // Complete intro at ~2.8s
    const completeTimer = setTimeout(() => {
      setPhase("complete");
      if (onComplete) onComplete();
    }, 2900);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(zoomTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  const handleSkip = () => {
    setPhase("complete");
    if (onComplete) onComplete();
  };

  if (phase === "complete") return null;

  return (
    <div 
      className={`fixed inset-0 z-[9999] flex items-center justify-center bg-[#05070c] overflow-hidden transition-all duration-700 ${
        phase === "zoom" ? "opacity-0 pointer-events-none scale-125" : "opacity-100"
      }`}
      style={{ perspective: "1400px" }}
    >
      {/* Deep Space Ambient Nebulas (Cyan / Electric Blue) */}
      <div className="absolute w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-cyan-500/25 via-sky-600/15 to-blue-800/25 blur-[160px] animate-pulse pointer-events-none" />
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] rounded-full bg-cyan-400/15 blur-[140px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[450px] h-[450px] rounded-full bg-blue-600/20 blur-[150px] pointer-events-none" />

      {/* Speed lines & particle warp during zoom */}
      {phase === "zoom" && (
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(56,189,248,0.3)_60%,#000_100%)] animate-ping pointer-events-none" />
      )}

      {/* Main TV Frame Container with 3D Warp Transform */}
      <div 
        className={`relative flex flex-col items-center justify-center transition-all ease-in-out ${
          phase === "zoom" 
            ? "duration-900 scale-[9] translate-z-[900px] opacity-0 filter blur-sm" 
            : "duration-1000 scale-100 opacity-100 animate-fadeIn"
        }`}
        style={{ transformStyle: "preserve-3d" }}
      >
        
        {/* Outer TV Glow & Neon Aura (Cyan / Sky-Blue) */}
        <div className="absolute -inset-6 rounded-[36px] bg-gradient-to-r from-cyan-400 via-sky-500 via-blue-600 to-teal-400 opacity-75 blur-2xl animate-pulse" />

        {/* TV Outer Bezel */}
        <div className="relative w-[340px] sm:w-[540px] md:w-[680px] h-[210px] sm:h-[330px] md:h-[410px] rounded-[28px] p-[3px] bg-gradient-to-tr from-cyan-400 via-sky-500 to-blue-600 shadow-[0_0_80px_rgba(56,189,248,0.5)] flex flex-col justify-between overflow-hidden">
          
          {/* Bezel border sweep highlight */}
          <div className="absolute inset-0 bg-[linear-gradient(110deg,transparent_20%,rgba(255,255,255,0.6)_50%,transparent_80%)] animate-tv-sweep pointer-events-none" />

          {/* TV Screen Display Glass */}
          <div className="relative w-full h-full rounded-[24px] bg-[#080d16] p-5 flex flex-col justify-between items-center text-center overflow-hidden border border-white/10 shadow-inner">
            
            {/* Screen Inner Quantum Matrix Grid */}
            <div 
              className="absolute inset-0 opacity-15 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" 
            />

            {/* Screen Top Status Bar */}
            <div className="w-full flex items-center justify-between z-10 text-[10px] sm:text-xs text-slate-400">
              <div className="flex items-center gap-1.5 text-cyan-400 font-semibold tracking-wider">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>NEO QLED 8K • AI ENGINE</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>2,300 Manuals Verified</span>
              </div>
            </div>

            {/* Center Quantum AI Core Animation */}
            <div className="relative my-auto flex flex-col items-center justify-center z-10 space-y-3">
              
              {/* Glowing pulsating energy rings */}
              <div className="relative flex items-center justify-center w-20 h-20 sm:w-28 sm:h-28">
                <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-cyan-400 via-sky-500 to-blue-600 blur-xl opacity-80 animate-pulse" />
                <div className="absolute -inset-3 rounded-full border border-cyan-400/40 animate-ping opacity-40" />
                <div className="absolute -inset-6 rounded-full border border-sky-400/25 animate-spin" style={{ animationDuration: "12s" }} />

                {/* Center Core Glass Disc */}
                <div className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-tr from-cyan-400 via-sky-500 to-blue-600 p-[2px] shadow-[0_0_30px_rgba(56,189,248,0.8)]">
                  <div className="w-full h-full rounded-full bg-[#09111e] flex items-center justify-center">
                    <Sparkles className="w-8 h-8 sm:w-10 sm:h-10 text-white drop-shadow-[0_0_15px_#fff] animate-bounce" />
                  </div>
                </div>
              </div>

              {/* Title inside the TV */}
              <div className="space-y-1">
                <h2 className="font-heading text-lg sm:text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                  Intelligent <span className="text-gradient-primary">Product Support</span>
                </h2>
                <p className="text-[11px] sm:text-xs text-slate-300 font-medium">
                  Entering Interactive Support Matrix...
                </p>
              </div>

            </div>

            {/* Bottom Progress Bar inside screen */}
            <div className="w-full max-w-xs sm:max-w-md z-10 space-y-1.5">
              <div className="h-1.5 w-full rounded-full bg-white/10 overflow-hidden p-[1px]">
                <div 
                  className="h-full rounded-full user-bubble-gradient transition-all duration-100 ease-out shadow-[0_0_12px_rgba(56,189,248,0.8)]"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-400 px-1 font-mono">
                <span>SYSTEM_BOOT</span>
                <span className="text-cyan-400 font-semibold">{Math.min(100, Math.round(progress))}%</span>
              </div>
            </div>

            {/* Screen Flash Flare on zoom */}
            {phase === "zoom" && (
              <div className="absolute inset-0 bg-white opacity-95 animate-ping z-50 pointer-events-none" />
            )}

          </div>

          {/* Bottom Bezel Samsung Emblem */}
          <div className="w-full py-1 bg-[#0c121e] flex items-center justify-center border-t border-white/5">
            <span className="text-[9px] sm:text-[10px] font-bold text-slate-400 tracking-[0.25em] uppercase">
              SAMSUNG
            </span>
          </div>

        </div>

        {/* TV Stand Base (Metallic / Glass Reflection) */}
        <div className="relative flex flex-col items-center z-0 -mt-1">
          {/* Stand Neck */}
          <div className="w-10 sm:w-16 h-3 sm:h-5 bg-gradient-to-b from-slate-700 to-slate-900 border-x border-white/10" />
          {/* Stand Foot Plate */}
          <div className="w-40 sm:w-64 md:w-80 h-2 sm:h-3 rounded-full bg-gradient-to-r from-slate-800 via-slate-600 to-slate-800 border border-white/20 shadow-[0_10px_30px_rgba(0,0,0,0.8)]" />
        </div>

      </div>

      {/* Skip Button in Bottom Corner */}
      <button
        onClick={handleSkip}
        className="absolute bottom-6 right-6 z-50 flex items-center gap-1.5 px-4 py-2 rounded-full glass-panel hover:border-cyan-500/50 text-slate-300 hover:text-white text-xs font-medium transition shadow-lg group"
      >
        <span>Skip Intro</span>
        <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
      </button>

    </div>
  );
}
