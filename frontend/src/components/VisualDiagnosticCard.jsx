import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Camera, AlertTriangle, ShieldCheck, Wrench, Clock, MessageSquare, Stethoscope, CheckCircle2, Smartphone } from "lucide-react";

export default function VisualDiagnosticCard({ diag, imagePreview, onSendMessage }) {
  if (!diag) return null;

  const severityColors = {
    Low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    Medium: "bg-amber-50 text-amber-700 border-amber-200",
    High: "bg-rose-50 text-rose-700 border-rose-200",
    Critical: "bg-purple-50 text-purple-700 border-purple-200",
  };

  const badgeStyle = severityColors[diag.severity] || severityColors.High;

  // Clean any leftover <think> blocks, metadata, or unclosed thinking tokens
  const cleanAnalysis = (diag.analysis || "")
    .replace(/<think>[\s\S]*?(?:<\/think>|$)/gi, "")
    .replace(/<\/?think>/gi, "")
    .replace(/^(?:The user wants me to|I need to act as|Based on the image, I will|As a Samsung technician)[\s\S]*?\n\n/gi, "")
    .trim();

  return (
    <div className="my-3 rounded-2xl p-4 sm:p-5 border border-slate-200/90 bg-gradient-to-br from-white via-slate-50/80 to-blue-50/20 backdrop-blur-md shadow-xs transition-all">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-200/80 pb-3 mb-3.5 flex-wrap">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-600/10 flex items-center justify-center text-blue-600 shrink-0">
            <Stethoscope className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 font-heading flex items-center gap-2">
              Vision AI Hardware Diagnostic Report
            </h4>
            <p className="text-[11px] text-slate-500 font-medium">
              Image analysis & verified technical recommendations
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {diag.device_detected && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 flex items-center gap-1">
              <Smartphone className="w-3 h-3 text-slate-500" />
              {diag.device_detected}
            </span>
          )}
          <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded-full border uppercase tracking-wider ${badgeStyle}`}>
            {diag.severity || "High"} Severity Fault
          </span>
        </div>
      </div>

      {/* Main content grid */}
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        {imagePreview && (
          <div className="sm:w-1/3 shrink-0">
            <div className="relative rounded-xl overflow-hidden border border-slate-200 shadow-xs bg-slate-100 aspect-square max-h-56 sm:max-h-none">
              <img
                src={imagePreview}
                alt="Analyzed defect"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-2 left-2 px-2 py-0.5 bg-slate-900/80 text-white rounded text-[9px] font-bold backdrop-blur-xs flex items-center gap-1">
                <Camera className="w-2.5 h-2.5 text-blue-400" /> Photo Analyzed
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col justify-between space-y-3">
          <div className="text-xs text-slate-800 bg-white p-3.5 rounded-xl border border-slate-200/70 shadow-xs">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h3: ({ children }) => (
                  <h5 className="text-[11.5px] font-bold text-blue-900 uppercase tracking-wider mt-2.5 first:mt-0 mb-1 pb-0.5 border-b border-slate-100 flex items-center gap-1.5">
                    {children}
                  </h5>
                ),
                p: ({ children }) => (
                  <p className="text-[12px] text-slate-700 leading-relaxed mb-1.5 last:mb-0">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-4 space-y-1 my-1 text-[12px] text-slate-700">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-4 space-y-1 my-1 text-[12px] text-slate-700">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed pl-0.5">{children}</li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-slate-900">{children}</strong>
                ),
              }}
            >
              {cleanAnalysis}
            </ReactMarkdown>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            <div className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 flex items-start gap-2 text-emerald-900 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div className="text-[10.5px] leading-tight">
                <span className="font-bold block text-emerald-950 mb-0.5">Warranty & Care:</span>
                <span>{diag.warranty_covered}</span>
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-blue-50/70 border border-blue-200/80 flex items-start gap-2 text-blue-900 font-medium">
              <Clock className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <div className="text-[10.5px] leading-tight">
                <span className="font-bold block text-blue-950 mb-0.5">Service Turnaround:</span>
                <span>{diag.turnaround}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Suggested Follow-up Quick Chips */}
      {diag.suggested_followups && diag.suggested_followups.length > 0 && (
        <div className="pt-2.5 border-t border-slate-200/60">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
            Recommended Action Steps:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {diag.suggested_followups.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onSendMessage && onSendMessage(suggestion)}
                className="text-[11px] font-semibold text-slate-700 bg-white hover:bg-blue-50 hover:text-blue-700 px-2.5 py-1 rounded-lg border border-slate-200/90 shadow-xs transition active:scale-95 cursor-pointer flex items-center gap-1"
              >
                <span>{suggestion}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
