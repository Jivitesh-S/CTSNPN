import React, { useState, useEffect } from "react";
import { Sparkles, ArrowRight } from "lucide-react";

export function TvIntroPortal({ onComplete }) {
  const [phase, setPhase] = useState("loading"); // 'loading' -> 'complete-fade' -> 'done'
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Smooth progress increment from 0 to 100%
    const startTime = Date.now();
    const duration = 2600; // 2.6 seconds total

    const timer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const rawProgress = Math.min(100, (elapsed / duration) * 100);
      
      // Natural ease-out progress curve
      const eased = Math.min(100, Math.round(100 * (1 - Math.pow(1 - rawProgress / 100, 1.6))));
      setProgress(eased);

      if (rawProgress >= 100) {
        clearInterval(timer);
        setProgress(100);
        
        // Brief pause at 100% before transition
        setTimeout(() => {
          setPhase("complete-fade");
          setTimeout(() => {
            setPhase("done");
            if (onComplete) onComplete();
          }, 600);
        }, 350);
      }
    }, 25);

    return () => clearInterval(timer);
  }, [onComplete]);

  const handleSkip = () => {
    setPhase("complete-fade");
    setTimeout(() => {
      setPhase("done");
      if (onComplete) onComplete();
    }, 200);
  };

  if (phase === "done") return null;

  // Normalized progress fractions for staggered stroke reveals
  const p = progress / 100;

  // Calculate stroke visibility and assembly transforms for letter fragments
  const getFragmentStyle = (startThreshold, endThreshold, initialTransform) => {
    if (p < startThreshold) {
      return {
        opacity: 0,
        transform: initialTransform,
        filter: "blur(6px)"
      };
    }
    const localP = Math.min(1, Math.max(0, (p - startThreshold) / (endThreshold - startThreshold)));
    return {
      opacity: localP,
      transform: `translate(${initialTransform.x * (1 - localP)}px, ${initialTransform.y * (1 - localP)}px) rotate(${initialTransform.rot * (1 - localP)}deg) scale(${initialTransform.scale + (1 - initialTransform.scale) * localP})`,
      filter: `blur(${(1 - localP) * 4}px)`,
      transition: "all 0.12s cubic-bezier(0.16, 1, 0.3, 1)"
    };
  };

  return (
    <div
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-between bg-[#070b14] overflow-hidden select-none transition-all duration-700 ${
        phase === "complete-fade" ? "opacity-0 scale-105 pointer-events-none" : "opacity-100 scale-100"
      }`}
    >
      {/* Ambient background glows matching application's blue / indigo / purple design system */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-blue-600/20 via-indigo-600/20 to-purple-600/15 blur-[140px] pointer-events-none animate-pulse" />
      <div className="absolute top-1/4 left-1/3 w-[350px] h-[350px] rounded-full bg-cyan-500/15 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-[400px] h-[400px] rounded-full bg-purple-600/15 blur-[130px] pointer-events-none" />

      {/* Subtle background tech grid */}
      <div className="absolute inset-0 opacity-[0.04] bg-[radial-gradient(#60a5fa_1px,transparent_1px)] [background-size:24px_24px] pointer-events-none" />

      {/* Top Header Placeholder / Brand Badge */}
      <div className="w-full pt-8 sm:pt-12 flex justify-center items-center z-10">
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] backdrop-blur-md">
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          <span className="text-[11px] sm:text-xs font-semibold tracking-wider text-slate-300 uppercase font-['Space_Grotesk']">
            AI Assistant Engine
          </span>
        </div>
      </div>

      {/* Center: Dynamic Fragment & Stroke Assembly Wordmark (Functional Inspiration from Image 2 & 3) */}
      <div className="relative my-auto flex flex-col items-center justify-center z-10 w-full max-w-2xl px-6">
        
        {/* Brand Icon Core that unlocks and glows as progress increases */}
        <div 
          className="relative mb-6 flex items-center justify-center transition-all duration-500"
          style={{
            opacity: Math.min(1, p * 1.4),
            transform: `scale(${0.6 + p * 0.4})`,
          }}
        >
          <div className="absolute -inset-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 opacity-60 blur-xl animate-pulse" />
          <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-[2px] shadow-2xl shadow-blue-500/30 flex items-center justify-center ring-1 ring-white/30">
            <div className="w-full h-full rounded-[14px] bg-[#0c1222]/90 backdrop-blur-md flex items-center justify-center">
              <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-white drop-shadow-[0_0_12px_rgba(255,255,255,0.8)]" />
            </div>
          </div>
        </div>

        {/* Dynamic Stroke Assembly SVG & Script Wordmark */}
        <div className="relative w-full max-w-md sm:max-w-lg h-24 sm:h-32 flex items-center justify-center">
          <svg
            viewBox="0 0 540 120"
            className="w-full h-full overflow-visible"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="brandLinearGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#60a5fa" />
                <stop offset="50%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#c084fc" />
              </linearGradient>
              <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Fragment 1: First Initial Letter 'T' Stem & Swash (Appears 0% - 35%) */}
            <g style={getFragmentStyle(0, 0.35, { x: -35, y: -20, rot: -18, scale: 0.6 })}>
              <path
                d="M 45 35 C 65 30, 95 30, 115 35 M 80 35 C 80 55, 78 80, 75 95"
                stroke="url(#brandLinearGrad)"
                strokeWidth="10"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="180"
                strokeDashoffset={Math.max(0, 180 * (1 - p / 0.4))}
                filter="url(#glowEffect)"
              />
            </g>

            {/* Fragment 2: 'e' Loop & Arch (Appears 15% - 48%) */}
            <g style={getFragmentStyle(0.15, 0.48, { x: -20, y: 25, rot: 25, scale: 0.7 })}>
              <path
                d="M 125 70 C 120 50, 145 45, 150 62 C 150 78, 125 88, 155 88"
                stroke="url(#brandLinearGrad)"
                strokeWidth="9"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="150"
                strokeDashoffset={Math.max(0, 150 * (1 - Math.max(0, p - 0.15) / 0.35))}
                filter="url(#glowEffect)"
              />
            </g>

            {/* Fragment 3: 'c' Arc & 'h' Ascender (Appears 28% - 62%) */}
            <g style={getFragmentStyle(0.28, 0.62, { x: 15, y: -30, rot: -15, scale: 0.65 })}>
              <path
                d="M 195 55 C 175 50, 168 85, 192 88 M 215 25 L 215 88 M 215 58 C 228 48, 245 50, 245 88"
                stroke="url(#brandLinearGrad)"
                strokeWidth="9"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="220"
                strokeDashoffset={Math.max(0, 220 * (1 - Math.max(0, p - 0.28) / 0.35))}
                filter="url(#glowEffect)"
              />
            </g>

            {/* Fragment 4: 'S' Dynamic Curve & Tail (Appears 42% - 75%) */}
            <g style={getFragmentStyle(0.42, 0.75, { x: 30, y: 20, rot: 22, scale: 0.7 })}>
              <path
                d="M 305 45 C 285 35, 270 52, 288 66 C 308 80, 290 95, 270 88"
                stroke="url(#brandLinearGrad)"
                strokeWidth="9.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="180"
                strokeDashoffset={Math.max(0, 180 * (1 - Math.max(0, p - 0.42) / 0.35))}
                filter="url(#glowEffect)"
              />
            </g>

            {/* Fragment 5: 't' Cross & 'o' Loop (Appears 55% - 88%) */}
            <g style={getFragmentStyle(0.55, 0.88, { x: -15, y: -25, rot: 14, scale: 0.75 })}>
              <path
                d="M 330 38 L 330 88 M 320 52 L 342 52 M 355 68 C 355 50, 385 50, 385 68 C 385 88, 355 88, 355 68"
                stroke="url(#brandLinearGrad)"
                strokeWidth="9"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="190"
                strokeDashoffset={Math.max(0, 190 * (1 - Math.max(0, p - 0.55) / 0.35))}
                filter="url(#glowEffect)"
              />
            </g>

            {/* Fragment 6: 'r' & 'e' Finish Swash (Appears 68% - 98%) */}
            <g style={getFragmentStyle(0.68, 0.98, { x: 40, y: -15, rot: -20, scale: 0.7 })}>
              <path
                d="M 405 52 L 405 88 M 405 62 C 415 50, 428 52, 432 58 M 445 70 C 440 50, 465 45, 470 62 C 470 78, 445 88, 485 88"
                stroke="url(#brandLinearGrad)"
                strokeWidth="9"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="210"
                strokeDashoffset={Math.max(0, 210 * (1 - Math.max(0, p - 0.68) / 0.3))}
                filter="url(#glowEffect)"
              />
            </g>
          </svg>
        </div>

        {/* Subtitle / Brand Typography */}
        <div 
          className="mt-2 text-center transition-all duration-700 ease-out"
          style={{
            opacity: Math.max(0, (p - 0.5) / 0.5),
            transform: `translateY(${(1 - Math.max(0, (p - 0.5) / 0.5)) * 12}px)`,
          }}
        >
          <h2 className="font-['Space_Grotesk'] text-lg sm:text-xl md:text-2xl font-bold tracking-tight text-white drop-shadow-md">
            Tech Store <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">Assistant</span>
          </h2>
          <p className="text-[12px] sm:text-xs text-slate-400 font-['Lexend'] mt-1 font-normal tracking-wide">
            Intelligent Product Support & Concierge
          </p>
        </div>

      </div>

      {/* Bottom Progress Counter & Slim Minimalist Progress Bar (Functional Inspiration from Image 2 & 3) */}
      <div className="w-full pb-10 sm:pb-14 flex flex-col items-center justify-center z-20 px-6">
        
        {/* Percentage Counter with `%` space formatting */}
        <div className="mb-3 text-center">
          <span className="font-['Space_Grotesk'] font-extrabold text-2xl sm:text-3xl tracking-widest text-slate-100 drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">
            {Math.min(100, Math.round(progress))} %
          </span>
        </div>

        {/* Sleek Minimal Progress Bar Line */}
        <div className="w-48 sm:w-64 md:w-80 h-[3px] sm:h-[4px] rounded-full bg-white/[0.12] overflow-hidden p-0 backdrop-blur-sm">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 transition-all duration-75 ease-out shadow-[0_0_12px_rgba(96,165,250,0.8)]"
            style={{ width: `${progress}%` }}
          />
        </div>

      </div>

      {/* Skip Button in Bottom Corner */}
      <button
        onClick={handleSkip}
        className="absolute bottom-6 right-6 z-50 flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/[0.06] hover:bg-white/[0.12] border border-white/[0.1] hover:border-white/25 text-slate-400 hover:text-white text-xs font-medium backdrop-blur-md transition-all duration-200 shadow-lg group cursor-pointer"
      >
        <span>Skip</span>
        <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
      </button>

    </div>
  );
}

