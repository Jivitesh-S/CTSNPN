import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Plus, 
  Sparkles, 
  MessageSquare, 
  Smartphone, 
  Laptop, 
  Headphones, 
  ShieldCheck as PolicyIcon, 
  Trash2, 
  ChevronRight, 
  Search, 
  X, 
  ShieldCheck,
  Cpu,
  Wrench,
  ShoppingBag,
  Store,
  ArrowLeft
} from "lucide-react";

export function Sidebar({ 
  isOpen, 
  onClose, 
  history, 
  onSelectQuery, 
  onNewChat, 
  onClearHistory,
  onShopClick,
  page = "chat"
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  const filteredHistory = history.filter(item => 
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const quickTopics = [
    { icon: Smartphone, title: "Phone Prices & Specs", query: "Phone Prices & Specs" },
    { icon: Laptop, title: "Laptop Buying Advice", query: "Laptop Buying Advice" },
    { icon: Headphones, title: "Accessories in Stock", query: "Accessories in Stock" },
    { icon: PolicyIcon, title: "Warranty & Returns", query: "Warranty & Returns" },
    { icon: Wrench, title: "Troubleshooting", query: "Troubleshooting" },
    { icon: ShoppingBag, title: "Best Sellers", query: "Best Sellers" }
  ];

  return (
    <>
      {/* Backdrop overlay */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40 transition-opacity" 
        />
      )}

      <aside className={`
        fixed top-0 bottom-0 left-0 z-50
        w-80 h-full
        bg-white border-r border-slate-200 shadow-2xl
        flex flex-col
        transition-transform duration-300 ease-out
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
        {/* Top Header */}
        <div className="p-5 border-b border-slate-100 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-blue-900 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white" />
              </div>

              <div>
                <h2 className="font-heading text-base font-bold text-slate-900 tracking-wide flex items-center gap-1.5">
                  TechStore AI
                  <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                    Pro
                  </span>
                </h2>
                <p className="text-xs text-slate-500">Gadget Support Hub</p>
              </div>
            </div>

            {/* Close button */}
            <button 
              onClick={onClose}
              className="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={() => {
              onNewChat();
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-blue-900 hover:bg-blue-800 text-white font-medium text-sm transition-all transform active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>

          {/* Search History */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input 
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-lg bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:ring-2 focus:ring-blue-100 transition"
            />
          </div>
        </div>

        {/* Middle Scrollable Section */}
        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          
          {/* Quick Topics */}
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-2">
              Featured Topics
            </span>
            <div className="mt-2 space-y-1">
              {quickTopics.map((topic, i) => {
                const Icon = topic.icon;
                return (
                  <button
                    key={i}
                    onClick={() => {
                      onSelectQuery(topic.query);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-100 text-slate-600 transition group text-left"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="p-1.5 rounded-lg bg-blue-50 text-blue-900 border border-blue-100">
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-xs truncate font-medium">{topic.title}</span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-900 group-hover:translate-x-0.5 transition" />
                  </button>
                );
              })}
            </div>
          </div>

          {/* History List */}
          <div>
            <div className="flex items-center justify-between px-2 mb-2">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Recent Queries
              </span>
              {history.length > 0 && (
                <button
                  onClick={onClearHistory}
                  title="Clear history"
                  className="text-slate-400 hover:text-rose-600 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {filteredHistory.length === 0 ? (
              <div className="py-6 px-3 text-center rounded-xl bg-slate-50 border border-slate-100">
                <MessageSquare className="w-6 h-6 text-slate-400 mx-auto mb-1.5" />
                <p className="text-xs text-slate-500">No past questions yet</p>
              </div>
            ) : (
              <div className="space-y-1">
                {filteredHistory.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectQuery(item.title);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-100 text-slate-600 transition group text-left"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-2 h-2 rounded-full bg-blue-700/50 group-hover:bg-blue-700 group-hover:scale-125 transition flex-shrink-0" />
                      <span className="text-xs truncate">{item.title}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 flex-shrink-0 ml-2">
                      {item.time}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer System Badges */}
        <div className="p-4 border-t border-slate-100 space-y-2">
          <button
            onClick={() => {
              if (page === "shop") {
                navigate("/");
              } else if (onShopClick) {
                onShopClick();
              } else {
                navigate("/shop");
              }
              onClose();
            }}
            className="w-full flex items-center gap-2 p-2.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white text-xs font-medium transition-all transform active:scale-[0.98]"
            title={page === "shop" ? "Back to assistant" : "Manage your shop dataset (admin only)"}
          >
            {page === "shop" ? (
              <ArrowLeft className="w-4 h-4" />
            ) : (
              <Store className="w-4 h-4" />
            )}
            <span>{page === "shop" ? "Back to Assistant" : "Shop / My Store"}</span>
          </button>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-2 text-xs text-slate-700 font-medium mb-1">
              <Cpu className="w-3.5 h-3.5 text-blue-900" />
              <span>TechStore AI Assistant</span>
            </div>
            <p className="text-[11px] text-slate-500 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Covering the full TechStore catalog & policies
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
