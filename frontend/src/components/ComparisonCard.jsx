import React from "react";
import { Scale, Check, ArrowRight, ShieldCheck, Sparkles, ShoppingBag } from "lucide-react";

export default function ComparisonCard({ data, onReserve }) {
  if (!data || !data.product_a || !data.product_b) return null;

  const { product_a: a, product_b: b } = data;

  const allSpecKeys = Array.from(
    new Set([...Object.keys(a.specs || {}), ...Object.keys(b.specs || {})])
  );

  return (
    <div className="my-3 rounded-2xl p-4 sm:p-5 border border-slate-200/90 bg-gradient-to-br from-white/95 via-slate-50/90 to-indigo-50/30 backdrop-blur-md shadow-sm transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-200/80 pb-3 mb-4 flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-600">
            <Scale className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-800 font-heading">
              Head-to-Head Specification Matrix
            </h4>
            <p className="text-[11px] text-slate-500 font-medium">
              Side-by-side comparison with verified store pricing
            </p>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200/60 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-indigo-600" />
          Live Spec Match
        </span>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-4">
        {/* Product A */}
        <div className="p-3.5 rounded-xl bg-white/90 border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
              Option 1
            </div>
            <h5 className="text-xs sm:text-sm font-bold text-slate-900 font-heading line-clamp-2">
              {a.name}
            </h5>
            <div className="mt-2 text-sm sm:text-base font-extrabold text-blue-700">
              Rs. {Number(a.price).toLocaleString("en-IN")}
            </div>
            <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              {a.warranty_months || 12}M Brand Warranty
            </div>
          </div>
          {onReserve && (
            <button
              onClick={() => onReserve(a)}
              className="mt-3 w-full py-1.5 px-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-[11px] font-bold shadow-xs transition active:scale-95 flex items-center justify-center gap-1 cursor-pointer"
            >
              <ShoppingBag className="w-3 h-3" />
              <span>Reserve Hold</span>
            </button>
          )}
        </div>

        {/* Product B */}
        <div className="p-3.5 rounded-xl bg-white/90 border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
              Option 2
            </div>
            <h5 className="text-xs sm:text-sm font-bold text-slate-900 font-heading line-clamp-2">
              {b.name}
            </h5>
            <div className="mt-2 text-sm sm:text-base font-extrabold text-indigo-700">
              Rs. {Number(b.price).toLocaleString("en-IN")}
            </div>
            <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              {b.warranty_months || 12}M Brand Warranty
            </div>
          </div>
          {onReserve && (
            <button
              onClick={() => onReserve(b)}
              className="mt-3 w-full py-1.5 px-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-[11px] font-bold shadow-xs transition active:scale-95 flex items-center justify-center gap-1 cursor-pointer"
            >
              <ShoppingBag className="w-3 h-3" />
              <span>Reserve Hold</span>
            </button>
          )}
        </div>
      </div>

      {/* Detailed Specs Table */}
      {allSpecKeys.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-slate-200/80 bg-white/80">
          <table className="w-full text-left text-[11px]">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200/80 text-slate-600 font-bold uppercase tracking-wider text-[9px]">
                <th className="py-2 px-3 w-1/3">Feature</th>
                <th className="py-2 px-3 w-1/3 text-slate-800">{a.name.split(" ")[0]} {a.name.split(" ")[1]}</th>
                <th className="py-2 px-3 w-1/3 text-slate-800">{b.name.split(" ")[0]} {b.name.split(" ")[1]}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {allSpecKeys.slice(0, 6).map((key) => (
                <tr key={key} className="hover:bg-slate-50/60 transition">
                  <td className="py-2 px-3 font-semibold text-slate-600 capitalize">
                    {key.replace(/_/g, " ")}
                  </td>
                  <td className="py-2 px-3 text-slate-800 font-medium">
                    {a.specs?.[key] || "—"}
                  </td>
                  <td className="py-2 px-3 text-slate-800 font-medium">
                    {b.specs?.[key] || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
