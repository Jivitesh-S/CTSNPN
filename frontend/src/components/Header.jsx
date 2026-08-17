import { Menu, Sparkles, Radio } from "lucide-react";

export function Header({ onMenuClick, onVoiceClick }) {
  return (
    <header className="h-16 px-4 sm:px-6 bg-white/40 backdrop-blur-xl border-b border-white/50 flex items-center justify-between flex-shrink-0 z-20 transition-all duration-300">
      <div className="flex items-center gap-3">
        {/* Sidebar toggle */}
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="p-2 rounded-xl text-slate-700 hover:text-blue-900 hover:bg-white/60 backdrop-blur-md transition-all active:scale-95 border border-transparent hover:border-white/60"
            title="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Title with Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20 ring-1 ring-white/50">
            <Sparkles className="w-5 h-5 text-white" />
          </div>

          <div>
            <h1 className="font-heading font-bold text-base sm:text-lg text-slate-900 tracking-tight">
              Tech Store Assistant
            </h1>
          </div>
        </div>
      </div>

      {/* Right Action Buttons */}
      <div className="flex items-center">
        {/* Voice Assistant Button styled with Logo Gradient */}
        {onVoiceClick && (
          <button
            onClick={onVoiceClick}
            className="flex items-center gap-2.5 px-4 sm:px-5 py-2 sm:py-2.5 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-semibold transition-all duration-200 shadow-md shadow-blue-500/25 ring-1 ring-white/40 hover:shadow-lg hover:shadow-blue-500/30 hover:scale-[1.02] active:scale-95 cursor-pointer"
            title="Open voice mode"
          >
            <Radio className="w-4.5 h-4.5 text-white animate-pulse" />
            <span>Voice Assistant</span>
          </button>
        )}
      </div>
    </header>
  );
}

