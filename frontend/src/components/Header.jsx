import { Menu, Sparkles, Radio, Plus, Bot } from "lucide-react";

export function Header({ onMenuClick, onNewChat, onVoiceClick }) {
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

        {/* Title with Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20 ring-1 ring-white/50">
            <Bot className="w-5 h-5 text-white" />
          </div>

          <div>
            <h1 className="font-heading font-bold text-sm sm:text-base text-slate-900 tracking-tight flex items-center gap-2">
              <span>Tech Store Assistant</span>
              <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/70 backdrop-blur-md text-slate-700 text-[10px] font-medium border border-white/80 shadow-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                AI Support Concierge
              </span>
            </h1>
            <p className="text-[11px] text-slate-500 hidden sm:block font-normal">
              Instant Troubleshooting • Product Specs • Live Inventory
            </p>
          </div>
        </div>
      </div>

      {/* Right Action Buttons */}
      <div className="flex items-center gap-2">
        {/* Voice Orb Mode Trigger Button */}
        {onVoiceClick && (
          <button
            onClick={onVoiceClick}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-white/80 bg-white/60 backdrop-blur-md text-slate-700 text-xs font-medium transition hover:border-blue-500/50 hover:bg-white/90 hover:text-blue-700 shadow-xs active:scale-95"
            title="Open voice mode"
          >
            <Radio className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden sm:inline">Voice Assistant</span>
          </button>
        )}

        {/* New Chat Button */}
        {onNewChat && (
          <button
            onClick={onNewChat}
            className="p-2 rounded-xl text-slate-700 hover:text-blue-900 hover:bg-white/60 backdrop-blur-md transition-all active:scale-95 border border-transparent hover:border-white/60"
            title="Start fresh conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        )}
      </div>
    </header>
  );
}

