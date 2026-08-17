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
  Bot,
  Download,
  Printer,
  FileCheck,
  ShieldCheck,
  Play,
  ExternalLink,
  Video,
  ShoppingBag,
} from "lucide-react";
import { generateServiceTokenPdf } from "../utils/pdfGenerator";
import { VideoHubCard } from "./VideoHubCard";
import ComparisonCard from "./ComparisonCard";
import VisualDiagnosticCard from "./VisualDiagnosticCard";






export function MessageItem({ message, onRetry, onSendMessage, onReserve }) {

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

  // Detect Service Token Receipt generated in this message
  const hasToken = Boolean(
    message.token_id ||
    message.action === "token_created" ||
    (message.content && /#(?:CAN|REP)-\d{4}/i.test(message.content))
  );

  const rawTokenMatch = message.content?.match(/#(CAN-\d{4}|REP-\d{4})/i);
  const rawOrderMatch = message.content?.match(/#(ORD-\d{3,5})/i);
  const rawCustomerMatch = message.content?.match(/Customer:\*{0,2}\s*([^\n\r*]+)/i);
  const rawPhoneMatch = message.content?.match(/Phone:\*{0,2}\s*([^\n\r*]+)/i);
  const rawModelMatch = message.content?.match(/for Order [^(\n]*\(([^)]+)\)/i);

  const currentTokenId = message.token_id || rawTokenMatch?.[1] || "CAN-8968";
  const currentOrderId = message.order_id || rawOrderMatch?.[1] || "ORD-1003";
  const currentCustomer = message.customer_name || rawCustomerMatch?.[1]?.trim() || "Customer";
  const currentPhone = message.phone || rawPhoneMatch?.[1]?.trim() || "+91 98401 23456";
  const currentModel = message.model_name || rawModelMatch?.[1]?.trim() || "Samsung Galaxy Device";
  const currentReqType = message.request_type || (currentTokenId.startsWith("REP") ? "Replacement" : "Cancellation");

  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleDownloadPdf = () => {
    setDownloadingPdf(true);
    try {
      generateServiceTokenPdf(
        {
          token_id: currentTokenId,
          order_id: currentOrderId,
          customer_name: currentCustomer,
          phone: currentPhone,
          model_name: currentModel,
          request_type: currentReqType,
          price: message.price,
          purchase_date: message.purchase_date,
        },
        true
      );
    } catch (e) {
      console.error("PDF download error:", e);
    }
    setTimeout(() => setDownloadingPdf(false), 1500);
  };

  const handlePrintPdf = () => {
    try {
      const doc = generateServiceTokenPdf(
        {
          token_id: currentTokenId,
          order_id: currentOrderId,
          customer_name: currentCustomer,
          phone: currentPhone,
          model_name: currentModel,
          request_type: currentReqType,
          price: message.price,
          purchase_date: message.purchase_date,
        },
        false
      );
      doc.autoPrint();
      window.open(doc.output("bloburl"), "_blank");
    } catch (e) {
      console.error("PDF print error:", e);
    }
  };

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
      const isYouTube = href && (href.includes("youtube.com") || href.includes("youtu.be"));
      if (isYouTube) {
        return (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3 py-1.5 my-1.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 active:scale-95 text-white text-xs font-semibold shadow-sm transition-all border border-red-400/40 group/yt"
            {...props}
          >
            <span className="w-4 h-4 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 group-hover/yt:bg-white/30 transition">
              <Play className="w-2.5 h-2.5 fill-current ml-0.5" />
            </span>
            <span>{children}</span>
            <ExternalLink className="w-3 h-3 opacity-75 ml-0.5" />
          </a>
        );
      }
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline font-medium inline-flex items-center gap-1"
          {...props}
        >
          {children}
          <ExternalLink className="w-3 h-3 opacity-60" />
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
              {(message.video_hub || message.video)
                ? message.content
                    .replace(/(?:🎥\s*)?\*{0,2}Watch Video Review:?\*{0,2}\s*\[.*?\]\(https?:\/\/.*?\)/gi, "")
                    .replace(/You can also watch a detailed unboxing and review here:?\s*/gi, "")
                    .trim()
                : message.content}
            </ReactMarkdown>
          </div>

          {/* Visual AI Hardware Diagnostic Card */}
          {message.visual_diagnostic && (
            <VisualDiagnosticCard
              diag={message.visual_diagnostic}
              imagePreview={message.image_preview}
              onSendMessage={onSendMessage}
            />
          )}

          {/* Side-by-Side Product Comparison Matrix */}
          {message.comparison_data && (
            <ComparisonCard
              data={message.comparison_data}
              onReserve={onReserve}
            />
          )}

          {/* Single Product In-Store Reservation Action Card */}
          {(message.product || message.reservation_available) && !message.comparison_data && onReserve && (
            <div className="my-3 p-3.5 rounded-2xl bg-gradient-to-r from-blue-50/90 via-indigo-50/80 to-purple-50/90 border border-blue-200/80 shadow-xs flex items-center justify-between gap-3 flex-wrap">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-blue-600/10 flex items-center justify-center text-blue-600 shrink-0">
                  <ShoppingBag className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900 font-heading">
                    Reserve {(message.product || message.reservation_available).name}
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium">
                    Rs. {Number((message.product || message.reservation_available).price || 0).toLocaleString("en-IN")} • 24-Hour Free In-Store Hold (Surapet, Chennai)
                  </div>
                </div>
              </div>
              <button
                onClick={() => onReserve(message.product || message.reservation_available)}
                className="py-1.5 px-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition active:scale-95 flex items-center gap-1.5 cursor-pointer"
              >
                <ShoppingBag className="w-3.5 h-3.5" />
                <span>Reserve in Store</span>
              </button>
            </div>
          )}

          {/* Interactive YouTube Video & Benchmark Hub Card */}
          {message.video_hub && (
            <VideoHubCard hub={message.video_hub} />
          )}





          {/* E-Invoice & Service Token Receipt Card */}
          {hasToken && (
            <div className="my-4 p-4 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-blue-950 text-white shadow-lg border border-indigo-500/30 overflow-hidden relative">
              {/* Top Decorative Glow */}
              <div className="absolute -top-12 -right-12 w-32 h-32 bg-blue-500/20 rounded-full blur-2xl pointer-events-none" />

              <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-3 border-b border-white/10">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-blue-500/20 border border-blue-400/40 flex items-center justify-center text-blue-400">
                    <FileCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-200">
                      Official E-Invoice & Service Receipt
                    </h4>
                    <p className="text-[11px] text-slate-300">
                      Token: <span className="font-mono font-bold text-amber-300">#{currentTokenId}</span> • Auth: Telegram 2FA
                    </p>
                  </div>
                </div>

                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-medium border border-emerald-500/30">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Verified & Auto-Downloaded</span>
                </div>
              </div>

              {/* Quick Details Pill Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3.5 text-xs">
                <div className="p-2 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] text-slate-400 block">Customer</span>
                  <span className="font-semibold text-slate-100 truncate block">{currentCustomer}</span>
                </div>
                <div className="p-2 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] text-slate-400 block">Order ID</span>
                  <span className="font-semibold text-slate-100 truncate block">#{currentOrderId}</span>
                </div>
                <div className="p-2 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] text-slate-400 block">Device</span>
                  <span className="font-semibold text-slate-100 truncate block">{currentModel}</span>
                </div>
                <div className="p-2 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] text-slate-400 block">Request</span>
                  <span className="font-semibold text-rose-300 truncate block">{currentReqType}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 pt-1">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs font-semibold shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Download className={`w-3.5 h-3.5 ${downloadingPdf ? 'animate-bounce' : ''}`} />
                  {downloadingPdf ? "Downloading Receipt..." : "Download PDF Receipt"}
                </button>

                <button
                  onClick={handlePrintPdf}
                  className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 active:scale-95 text-slate-200 text-xs font-semibold border border-white/15 transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Printer className="w-3.5 h-3.5" />
                  Print Receipt
                </button>
              </div>
            </div>
          )}


          {/* Smart Contextual Follow-up Suggestions */}
          {!isUser && message.suggested_followups && message.suggested_followups.length > 0 && onSendMessage && (
            <div className="mt-4 pt-3.5 border-t border-slate-200/70">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-blue-600" />
                <span>Suggested Follow-ups:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {message.suggested_followups.map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onSendMessage(suggestion)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/90 hover:bg-blue-50/90 active:scale-95 border border-slate-200 hover:border-blue-300 text-slate-700 hover:text-blue-700 text-xs font-medium shadow-2xs hover:shadow-xs transition-all duration-200 text-left cursor-pointer group"
                  >
                    <span>{suggestion}</span>
                    <span className="text-slate-400 group-hover:text-blue-600 transition ml-0.5 font-bold">↗</span>
                  </button>
                ))}
              </div>
            </div>
          )}

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

