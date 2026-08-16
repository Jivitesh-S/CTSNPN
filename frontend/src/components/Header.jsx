import { Menu, Sparkles, Radio, Plus } from "lucide-react";

export function Header({ onMenuClick, onNewChat, onVoiceClick }) {
  return (
    <header className="h-16 px-4 sm:px-6 bg-white border-b border-slate-200 flex items-center justify-between flex-shrink-0 z-20">
      <div className="flex items-center gap-3">
        {/* Sidebar toggle */}
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
            title="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Title with Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-4 h-4 text-white" />
          </div>

          <div>
            <h1 className="font-heading font-bold text-sm sm:text-base text-slate-900 tracking-wide flex items-center gap-2">
              TechStore Assistant
              <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] border border-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Online
              </span>
            </h1>
            <p className="text-[11px] text-slate-500 hidden sm:block">
              Product prices • Stock • Repairs • Buying advice
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 bg-white text-slate-600 text-xs font-medium transition hover:border-blue-900 hover:text-blue-900"
            title="Open voice mode"
          >
            <Radio className="w-3.5 h-3.5 text-blue-900" />
            <span className="hidden sm:inline">Voice</span>
          </button>
        )}

        {/* New Chat Button */}
        {onNewChat && (
          <button
            onClick={onNewChat}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
            title="Start fresh conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        )}
      </div>
    </header>
  );
}
