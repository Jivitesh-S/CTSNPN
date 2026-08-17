import React from "react";
import { ArrowUpRight } from "lucide-react";

export function CategoryCard({ icon: Icon, title, description, query, onClick }) {
  return (
    <button
      onClick={() => onClick(query)}
      className="group flex flex-col justify-between p-5 rounded-2xl bg-white/75 backdrop-blur-xl border-2 border-blue-200/90 hover:border-blue-500 text-left w-full h-full cursor-pointer relative overflow-hidden transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-blue-500/10 hover:-translate-y-0.5 ring-1 ring-white/60"
    >
      <div className="flex items-start justify-between w-full mb-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600/15 to-purple-600/15 border border-blue-200/60 flex items-center justify-center text-blue-700 group-hover:scale-110 group-hover:bg-gradient-to-br group-hover:from-blue-600 group-hover:to-purple-600 group-hover:text-white transition-all duration-300 shadow-xs">
          <Icon className="w-5 h-5 transition-transform duration-300" />
        </div>
        <div className="w-7 h-7 rounded-full bg-white/90 border border-blue-200/70 flex items-center justify-center text-slate-500 group-hover:text-white group-hover:bg-blue-600 group-hover:border-blue-600 transition-all duration-300 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 shadow-xs">
          <ArrowUpRight className="w-4 h-4" />
        </div>
      </div>

      <div>
        <h3 className="font-heading text-base font-bold text-slate-900 group-hover:text-blue-700 transition-colors tracking-tight">
          {title}
        </h3>
        <p className="text-xs text-slate-600 mt-1 line-clamp-2 leading-relaxed font-normal">
          {description}
        </p>
      </div>
    </button>
  );
}

