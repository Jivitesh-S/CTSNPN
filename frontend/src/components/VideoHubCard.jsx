import React from "react";
import { Play, ExternalLink, Compass, Sparkles } from "lucide-react";

export function VideoHubCard({ hub }) {
  if (!hub || !hub.title) return null;

  const { title, subtitle, main_url, tags = [] } = hub;

  return (
    <div className="my-4 rounded-2xl bg-gradient-to-br from-white/95 via-slate-50/90 to-blue-50/30 backdrop-blur-md border border-slate-200/90 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
      {/* Top Header */}
      <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3.5">
        <div className="min-w-0 flex-1">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-50 border border-rose-200/80 text-rose-700 text-[11px] font-semibold tracking-wide mb-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-600 animate-pulse" />
            <span>YouTube Review & Benchmark Hub</span>
          </div>

          <h4 className="text-base sm:text-[17px] font-heading font-bold text-slate-900 tracking-tight truncate">
            {title}
          </h4>

          {subtitle && (
            <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>

        {main_url && (
          <a
            href={main_url}
            target="_blank"
            rel="noopener noreferrer"
            className="self-start sm:self-center inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 active:scale-95 text-white text-xs font-semibold shadow-xs hover:shadow-sm transition-all flex-shrink-0 cursor-pointer"
          >
            <Play className="w-3 h-3 fill-current" />
            <span>Watch Top Reviews</span>
            <ExternalLink className="w-3 h-3 opacity-80" />
          </a>
        )}
      </div>

      {/* Interactive Search Topics Bar */}
      {tags.length > 0 && (
        <div className="p-3.5 sm:p-4 bg-slate-50/60">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-blue-600" />
            <span>Explore Specific Tests & Unboxings:</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {tags.map((tag, idx) => (
              <a
                key={idx}
                href={tag.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white hover:bg-rose-50/80 border border-slate-200 hover:border-rose-300 text-slate-700 hover:text-rose-700 text-xs font-medium shadow-2xs hover:shadow-xs transition-all duration-200 group/tag"
              >
                <span>{tag.label}</span>
                <ExternalLink className="w-2.5 h-2.5 opacity-40 group-hover/tag:opacity-80 transition" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
