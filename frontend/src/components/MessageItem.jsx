import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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
  FileText,
  Phone,
  PhoneCall,
  MessageCircle,
  Bot
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

  // ONLY show calling / WhatsApp options when explicitly asking for human assistance / contact details
  const isHumanAssistance = Boolean(
    message.intent === "human_assistance" ||
    message.action === "human_support" ||
    message.action === "call_store"
  );

  const phoneNumber = message.phone || "+91 9087086182";
  const telUrl = message.tel || "tel:+919087086182";
  const waUrl = message.whatsapp || "https://wa.me/919087086182?text=Hello%20TechStore%2C%20I%20need%20human%20assistance";

  const markdownComponents = {
    a: ({ node, href, children, ...props }) => {
      const isTel = href && href.startsWith("tel:");
      if (isTel) {
        return (
          <a
            href={href}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 my-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-semibold shadow-xs transition"
            {...props}
          >
            <PhoneCall className="w-3.5 h-3.5" />
            {children}
          </a>
        );
      }
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline font-medium"
          {...props}
        >
          {children}
        </a>
      );
    },
    table: ({ node, ...props }) => (
      <div className="my-3.5 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-xs">
        <table className="w-full text-left text-[13.5px] border-collapse" {...props} />
      </div>
    ),
    thead: ({ node, ...props }) => (
      <thead className="bg-slate-100/90 border-b border-slate-200 text-slate-800 font-semibold" {...props} />
    ),
    th: ({ node, ...props }) => (
      <th className="px-4 py-3 font-semibold text-slate-800 text-xs tracking-wider uppercase border-r border-slate-200 last:border-r-0 whitespace-nowrap" {...props} />
    ),
    tbody: ({ node, ...props }) => (
      <tbody className="divide-y divide-slate-100" {...props} />
    ),
    tr: ({ node, ...props }) => (
      <tr className="hover:bg-blue-50/50 transition-colors even:bg-slate-50/60" {...props} />
    ),
    td: ({ node, ...props }) => (
      <td className="px-4 py-2.5 text-slate-700 border-r border-slate-100 last:border-r-0 align-top text-[13.5px] leading-relaxed" {...props} />
    ),
    p: ({ node, ...props }) => (
      <p className="text-slate-800 text-[14.5px] leading-relaxed my-2 first:mt-0 last:mb-0" {...props} />
    ),
    ul: ({ node, ...props }) => (
      <ul className="my-2 space-y-1.5 list-disc list-outside pl-5 text-slate-800 text-[14.5px] leading-relaxed" {...props} />
    ),
    ol: ({ node, ...props }) => (
      <ol className="my-2 space-y-2 list-decimal list-outside pl-5 text-slate-800 text-[14.5px] leading-relaxed" {...props} />
    ),
    li: ({ node, ...props }) => (
      <li className="text-slate-800 leading-relaxed text-[14.5px] pl-1" {...props} />
    ),
    strong: ({ node, ...props }) => (
      <strong className="font-semibold text-slate-900" {...props} />
    ),
    blockquote: ({ node, ...props }) => (
      <div className="my-3 p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
        <FileText className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="leading-relaxed" {...props} />
      </div>
    ),
    code: ({ node, inline, ...props }) => (
      inline ? (
        <code className="px-1.5 py-0.5 rounded bg-slate-100 text-blue-900 text-xs font-mono border border-slate-200" {...props} />
      ) : (
        <pre className="my-2 p-3.5 rounded-xl bg-slate-900 text-slate-100 text-xs overflow-x-auto font-mono">
          <code {...props} />
        </pre>
      )
    ),
  };

  if (isUser) {
    return (
      <div className="flex justify-end items-end gap-2.5 my-4 group">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-br-sm user-bubble-gradient px-5 py-3.5 text-white">
          <p className="text-[14.5px] leading-relaxed font-normal whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-700 to-purple-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mb-0.5 shadow-md shadow-blue-500/20 ring-1 ring-white/60">
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
      <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20 ring-1 ring-white/60">
        <Bot className="w-5 h-5 text-white" />
      </div>

      <div className="max-w-[92%] sm:max-w-[84%] space-y-2">
        {/* Assistant Content Card */}
        <div className="glass-panel-deep rounded-2xl rounded-tl-sm p-5 sm:p-6 transition-all">

          {/* Metadata Grounding Badge */}
          <div className="flex items-center justify-between gap-2 mb-3.5 pb-2.5 border-b border-white/60 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 text-slate-700 font-medium">
              <Store className="w-3.5 h-3.5 text-blue-600" />
              <span className="font-heading font-semibold">Tech Store Assistant</span>
            </div>

            {similarityScore && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 text-[11px] font-medium border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                {similarityScore}% Match
              </span>
            )}
          </div>

          {/* Human Assistance Options Banner (ONLY shown on human_assistance intent) */}
          {isHumanAssistance && (
            <div className="my-3.5 p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white shadow-md border border-slate-700/60">
              <div className="flex items-center gap-3 mb-3 pb-2.5 border-b border-white/10">
                <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center flex-shrink-0">
                  <PhoneCall className="w-4 h-4 text-emerald-400" />
                </div>
                <div>
                  <p className="text-[11px] text-blue-200 uppercase tracking-wider font-semibold">Direct Human Support Options</p>
                  <p className="text-xs text-slate-300">Choose your preferred way to connect with our store team:</p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
                {/* Option 1: Call Button */}
                <a
                  href={telUrl}
                  className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs font-semibold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Phone className="w-3.5 h-3.5 text-white" />
                  Call {phoneNumber}
                </a>

                {/* Option 2: WhatsApp Button */}
                <a
                  href={waUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white text-xs font-semibold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <MessageCircle className="w-3.5 h-3.5 text-white" />
                  Chat on WhatsApp
                </a>
              </div>
            </div>
          )}

          {/* Formatted Text Body */}
          <div className="text-slate-800 text-[14.5px]">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Bottom Action Toolbar */}
          <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-white/60 text-slate-500 text-xs">
            <div className="flex items-center gap-1">
              {/* Copy Button */}
              <button
                onClick={handleCopy}
                title="Copy response"
                className="p-1.5 rounded-xl hover:bg-white/70 hover:text-slate-900 transition flex items-center gap-1 text-[11px] active:scale-95"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600 font-medium">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Copy</span>
                  </>
                )}
              </button>

              {/* Text-to-Speech Button */}
              <button
                onClick={handleSpeak}
                title={speaking ? "Stop reading" : "Read aloud"}
                className={`p-1.5 rounded-xl hover:bg-white/70 transition flex items-center gap-1 text-[11px] active:scale-95 ${speaking ? "text-blue-700 bg-white/80 font-medium" : "hover:text-slate-900"
                  }`}
              >
                {speaking ? (
                  <>
                    <VolumeX className="w-3.5 h-3.5" />
                    <span>Listening...</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Read Aloud</span>
                  </>
                )}
              </button>

              {/* Thumbs Up / Down */}
              <div className="flex items-center border-l border-white/60 ml-1 pl-1 gap-0.5">
                <button
                  onClick={() => setLiked(liked === 'like' ? null : 'like')}
                  className={`p-1.5 rounded-xl hover:bg-white/70 transition active:scale-95 ${liked === 'like' ? 'text-blue-700 bg-white/80' : 'hover:text-slate-900'
                    }`}
                  title="Good answer"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setLiked(liked === 'dislike' ? null : 'dislike')}
                  className={`p-1.5 rounded-xl hover:bg-white/70 transition active:scale-95 ${liked === 'dislike' ? 'text-rose-600 bg-white/80' : 'hover:text-slate-900'
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
                className="p-1.5 rounded-xl hover:bg-white/70 hover:text-slate-900 transition flex items-center gap-1 text-[11px] active:scale-95"
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

