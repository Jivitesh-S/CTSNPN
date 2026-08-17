import React, { useState } from "react";
import { Play, ExternalLink, Video as VideoIcon, X } from "lucide-react";

export function VideoCard({ video }) {
  const [isPlaying, setIsPlaying] = useState(false);

  if (!video || !video.video_id) return null;

  const { video_id, video_url, title, channel, duration } = video;
  const thumbnailUrl = `https://img.youtube.com/vi/${video_id}/hqdefault.jpg`;
  const cleanUrl = video_url || `https://www.youtube.com/watch?v=${video_id}`;

  return (
    <div className="my-4 max-w-lg rounded-2xl overflow-hidden bg-white border border-slate-200/80 shadow-md hover:shadow-lg transition-all duration-300">
      {/* Video Preview / Inline Player Container */}
      <div className="relative aspect-video w-full bg-slate-950 overflow-hidden group">
        {isPlaying ? (
          <div className="relative w-full h-full">
            <iframe
              src={`https://www.youtube-nocookie.com/embed/${video_id}?autoplay=1&rel=0`}
              title={title || "YouTube Video Preview"}
              className="w-full h-full border-0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
            <button
              onClick={() => setIsPlaying(false)}
              className="absolute top-2 right-2 p-1.5 rounded-full bg-black/70 hover:bg-black text-white transition-all shadow-md active:scale-95 z-10"
              title="Close Player"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div
            onClick={() => setIsPlaying(true)}
            className="relative w-full h-full cursor-pointer overflow-hidden"
          >
            {/* Thumbnail Image */}
            <img
              src={thumbnailUrl}
              alt={title || "Video Thumbnail"}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              loading="lazy"
            />

            {/* Dark Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-black/10 group-hover:via-black/30 transition-colors" />

            {/* Center Play Button Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-blue-600/90 group-hover:bg-blue-600 text-white flex items-center justify-center shadow-xl shadow-blue-900/40 transform group-hover:scale-110 active:scale-95 transition-all duration-300 ring-4 ring-white/30">
                <Play className="w-6 h-6 sm:w-7 sm:h-7 fill-current ml-1 text-white" />
              </div>
            </div>

            {/* Duration Pill in Bottom Right */}
            {duration && (
              <div className="absolute bottom-2.5 right-2.5 px-2 py-0.5 rounded-md bg-black/80 backdrop-blur-xs text-white text-[11px] font-mono font-medium shadow-sm">
                {duration}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Metadata Bar Beneath Thumbnail */}
      <div className="p-3.5 bg-slate-50/70 flex items-start justify-between gap-3 border-t border-slate-100">
        <div className="min-w-0 flex-1">
          <a
            href={cleanUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs sm:text-[13.5px] font-semibold text-blue-600 hover:text-blue-700 hover:underline leading-snug line-clamp-2 block transition"
          >
            {title || "Watch Video Review"}
          </a>
          <p className="text-[11.5px] text-slate-500 mt-0.5 truncate font-medium">
            {channel || "Official Tech Channel"}
          </p>
        </div>

        <a
          href={cleanUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition"
          title="Open in YouTube"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
