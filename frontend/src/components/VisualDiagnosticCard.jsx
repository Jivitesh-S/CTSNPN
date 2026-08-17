import React from "react";
import { Camera, AlertTriangle, ShieldCheck, Wrench, Clock, MessageSquare, Stethoscope, CheckCircle2 } from "lucide-react";

export default function VisualDiagnosticCard({ diag, imagePreview, onSendMessage }) {
  if (!diag) return null;

  const severityColors = {
    Low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    Medium: "bg-amber-50 text-amber-700 border-amber-200",
    High: "bg-rose-50 text-rose-700 border-rose-200",
    Critical: "bg-purple-50 text-purple-700 border-purple-200",
  };

  const badgeStyle = severityColors[diag.severity] || severityColors.Medium;

  return (
    <div className="my-3 rounded-2xl p-4 sm:p-5 border border-slate-200/90 bg-gradient-to-br from-white/95 via-slate-50/90 to-blue-50/30 backdrop-blur-md shadow-sm transition-all">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-200/80 pb-3 mb-3 flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-blue-600/10 flex items-center justify-center text-blue-600">
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

        <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded-full border uppercase tracking-wider ${badgeStyle}`}>
          {diag.severity} Severity Fault
        </span>
      </div>

      {/* Main content grid */}
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        {imagePreview && (
          <div className="sm:w-1/3 shrink-0">
            <div className="relative rounded-xl overflow-hidden border border-slate-200/80 shadow-xs bg-slate-100 aspect-square">
              <img
                src={imagePreview}
                alt="Analyzed defect"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-1.5 left-1.5 px-2 py-0.5 bg-slate-900/70 text-white rounded text-[9px] font-bold backdrop-blur-xs flex items-center gap-1">
                <Camera className="w-2.5 h-2.5" /> Photo Analyzed
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 space-y-2.5">
          <div className="text-xs text-slate-800 font-medium leading-relaxed whitespace-pre-line bg-white/80 p-3 rounded-xl border border-slate-200/60">
            {diag.analysis}
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 rounded-lg bg-emerald-50/60 border border-emerald-100 flex items-center gap-1.5 text-emerald-800 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{diag.warranty_covered}</span>
            </div>
            <div className="p-2 rounded-lg bg-blue-50/60 border border-blue-100 flex items-center gap-1.5 text-blue-800 font-medium">
              <Clock className="w-4 h-4 text-blue-600 shrink-0" />
              <span>{diag.turnaround}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Suggested Follow-up Quick Chips */}
      {diag.suggested_followups && diag.suggested_followups.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
            Recommended Action Steps:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {diag.suggested_followups.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onSendMessage && onSendMessage(suggestion)}
                className="text-[11px] font-semibold text-slate-700 bg-white/90 hover:bg-blue-50 hover:text-blue-700 px-2.5 py-1 rounded-lg border border-slate-200/80 shadow-xs transition active:scale-95 cursor-pointer flex items-center gap-1"
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
