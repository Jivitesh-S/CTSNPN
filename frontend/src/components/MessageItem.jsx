import React, { useState } from "react";
import { 
  Sparkles, 
  Copy, 
  Check, 
  ThumbsUp, 
  ThumbsDown, 
  Volume2, 
  VolumeX, 
  RotateCw,
  Store,
  CheckCircle2,
  FileText
} from "lucide-react";

export function MessageItem({ message, onRetry }) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState(null); // 'like' | 'dislike' | null
  const [speaking, setSpeaking] = useState(false);

  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if (!('speechSynthesis' in window)) return;

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  // Helper to format assistant response with bold highlights and numbered steps
  const formatContent = (text) => {
    if (!text) return null;

    const lines = text.split('\n');
    return lines.map((line, index) => {
      // Step line e.g., "1. Go to Settings"
      const stepMatch = line.match(/^(\d+\.)\s*(.*)$/);
      if (stepMatch) {
        return (
          <div key={index} className="flex items-start gap-2.5 my-1.5 pl-1">
            <span className="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-900 text-xs font-semibold border border-blue-200">
              {stepMatch[1].replace('.', '')}
            </span>
            <span className="text-slate-800 text-[14.5px] leading-relaxed">
              {stepMatch[2]}
            </span>
          </div>
        );
      }

      // Note line e.g., "Note: Make sure..."
      if (line.toLowerCase().startsWith('note:')) {
        return (
          <div key={index} className="my-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2">
            <FileText className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <span>{line}</span>
          </div>
        );
      }

      // Empty line
      if (!line.trim()) {
        return <div key={index} className="h-2" />;
      }

      return (
        <p key={index} className="text-slate-800 text-[14.5px] leading-relaxed">
          {line}
        </p>
      );
    });
  };

  if (isUser) {
    return (
      <div className="flex justify-end items-end gap-2.5 my-3.5 group">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-br-lg user-bubble-gradient px-5 py-3.5 text-white">
          <p className="text-[14.5px] leading-relaxed font-normal whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
        <div className="w-7 h-7 rounded-full bg-blue-900 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mb-0.5">
          U
        </div>
      </div>
    );
  }

  const similarityScore = message.similarity_score 
    ? Math.round(message.similarity_score * 100) 
    : null;

  return (
    <div className="flex justify-start items-start gap-3 my-4 group">
      {/* Bot Icon */}
      <div className="w-8 h-8 rounded-full bg-blue-900 flex items-center justify-center flex-shrink-0">
        <Sparkles className="w-4 h-4 text-white" />
      </div>

      <div className="max-w-[90%] sm:max-w-[82%] space-y-2">
        {/* Assistant Content Card */}
        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-lg p-5 shadow-sm transition-all">
          
          {/* Metadata Grounding Badge */}
          <div className="flex items-center justify-between gap-2 mb-3 pb-2.5 border-b border-slate-100 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 text-slate-700 font-medium">
              <Store className="w-3.5 h-3.5 text-blue-900" />
              <span>TechStore Assistant</span>
            </div>

            {similarityScore && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[11px] border border-emerald-200">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                {similarityScore}% Match
              </span>
            )}
          </div>

          {/* Formatted Text Body */}
          <div className="space-y-1.5">
            {formatContent(message.content)}
          </div>

          {/* Bottom Action Toolbar */}
          <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-slate-100 text-slate-400 text-xs">
            <div className="flex items-center gap-1">
              {/* Copy Button */}
              <button
                onClick={handleCopy}
                title="Copy response"
                className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-900 transition flex items-center gap-1 text-[11px]"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">Copied</span>
                  </>
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Text-to-Speech Button */}
              <button
                onClick={handleSpeak}
                title={speaking ? "Stop reading" : "Read aloud"}
                className={`p-1.5 rounded-lg hover:bg-slate-100 transition flex items-center gap-1 text-[11px] ${
                  speaking ? "text-blue-900 bg-blue-50 font-medium" : "hover:text-slate-900"
                }`}
              >
                {speaking ? (
                  <>
                    <VolumeX className="w-3.5 h-3.5" />
                    <span>Listening...</span>
                  </>
                ) : (
                  <Volume2 className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Thumbs Up / Down */}
              <div className="flex items-center border-l border-slate-200 ml-1 pl-1">
                <button
                  onClick={() => setLiked(liked === 'like' ? null : 'like')}
                  className={`p-1.5 rounded-lg hover:bg-slate-100 transition ${
                    liked === 'like' ? 'text-blue-900' : 'hover:text-slate-900'
                  }`}
                  title="Good answer"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setLiked(liked === 'dislike' ? null : 'dislike')}
                  className={`p-1.5 rounded-lg hover:bg-slate-100 transition ${
                    liked === 'dislike' ? 'text-rose-600' : 'hover:text-slate-900'
                  }`}
                  title="Needs improvement"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Retry Button */}
            {onRetry && (
              <button
                onClick={onRetry}
                className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-900 transition flex items-center gap-1 text-[11px]"
                title="Regenerate answer"
              >
                <RotateCw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Retry</span>
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
