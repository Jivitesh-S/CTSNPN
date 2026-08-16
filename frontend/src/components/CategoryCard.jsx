import React from "react";
import { ArrowUpRight } from "lucide-react";

export function CategoryCard({ icon: Icon, title, description, query, onClick }) {
  return (
    <button
      onClick={() => onClick(query)}
      className="group flex flex-col justify-between p-5 rounded-2xl bg-white border border-slate-200 text-left w-full h-full transition-all duration-300 hover:border-blue-900 hover:shadow-md hover:-translate-y-0.5"
    >
      <div className="flex items-start justify-between w-full mb-3">
        <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-900 group-hover:scale-110 transition-all duration-300">
          <Icon className="w-5 h-5" />
        </div>
        <div className="w-7 h-7 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-blue-900 transition-all duration-300 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5">
          <ArrowUpRight className="w-4 h-4" />
        </div>
      </div>

      <div>
        <h3 className="font-heading text-base font-semibold text-slate-900 group-hover:text-blue-900 transition-colors">
          {title}
        </h3>
        <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
          {description}
        </p>
      </div>
    </button>
  );
}
