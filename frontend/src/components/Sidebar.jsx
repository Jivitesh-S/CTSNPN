import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Plus, 
  Sparkles, 
  MessageSquare, 
  Trash2, 
  Search, 
  X, 
  Store, 
  ArrowLeft,
  Phone,
  MessageCircle,
  MapPin,
  Clock,
  Check,
  Navigation,
  ExternalLink
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
  const [copiedPhone, setCopiedPhone] = useState(false);
  const [showMapConfirm, setShowMapConfirm] = useState(false);
  const navigate = useNavigate();

  const storeAddress = "Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Greater Chennai, Tamil Nadu 600066";
  const gmapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(storeAddress)}`;

  const filteredHistory = history.filter(item => 
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCopyPhone = () => {
    const phone = "+91 9087086182";
    if (navigator.clipboard) {
      navigator.clipboard.writeText(phone).catch(() => {});
    }
    setCopiedPhone(true);
    setTimeout(() => {
      setCopiedPhone(false);
    }, 2500);

    window.location.href = "tel:+919087086182";
  };

  const handleAddressClick = () => {
    setShowMapConfirm(true);
  };

  const handleConfirmNavigation = () => {
    window.open(gmapsUrl, "_blank", "noopener,noreferrer");
    setShowMapConfirm(false);
  };

  return (
    <>
      {/* Backdrop overlay */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-md z-40 transition-opacity duration-300" 
        />
      )}

      {/* Google Maps Confirmation Modal */}
      {showMapConfirm && (
        <div 
          onClick={() => setShowMapConfirm(false)}
          className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md animate-fade-in"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-sm rounded-3xl bg-white/95 backdrop-blur-2xl border border-white/80 p-6 shadow-2xl space-y-4 text-center transform transition-all animate-scale-up"
          >
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center mx-auto shadow-md shadow-blue-500/20 text-white">
              <Navigation className="w-6 h-6 animate-pulse" />
            </div>

            <div className="space-y-1.5">
              <h3 className="font-heading font-bold text-base text-slate-900">
                Google Maps Navigation
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Do you want to start Google Maps navigation to TechStore?
              </p>
              <div className="p-2.5 rounded-xl bg-blue-50/80 border border-blue-100 text-[11px] text-blue-900 text-left flex items-start gap-2 mt-2">
                <MapPin className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span className="leading-snug">{storeAddress}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setShowMapConfirm(false)}
                className="w-full py-2.5 px-4 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-700 font-medium text-xs transition active:scale-95 cursor-pointer"
              >
                No, Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmNavigation}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold text-xs shadow-md shadow-blue-500/25 flex items-center justify-center gap-1.5 transition active:scale-95 cursor-pointer"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Yes, Navigate</span>
              </button>
            </div>
          </div>
        </div>
      )}

      <aside className={`
        fixed top-0 bottom-0 left-0 z-50
        w-80 h-full
        bg-white/75 backdrop-blur-2xl border-r border-white/60 shadow-2xl
        flex flex-col
        transition-transform duration-300 ease-out
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
        {/* Top Header */}
        <div className="p-5 border-b border-white/50 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-md shadow-blue-500/20 ring-1 ring-white/60">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>

              <div>
                <h2 className="font-heading text-base font-bold text-slate-900 tracking-tight">
                  Tech Store Assistant
                </h2>
              </div>
            </div>

            {/* Close button */}
            <button 
              onClick={onClose}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-white/60 transition active:scale-95 cursor-pointer"
              title="Close menu"
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
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium text-sm shadow-md shadow-blue-500/20 transition-all transform active:scale-[0.98] cursor-pointer"
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
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-white/70 backdrop-blur-md border border-white/80 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition shadow-xs"
            />
          </div>
        </div>

        {/* Middle Scrollable Section: Recent Queries Brought Straight Up */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <div className="flex items-center justify-between px-2 mb-2.5">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Recent Queries
              </span>
              {history.length > 0 && (
                <button
                  onClick={onClearHistory}
                  title="Clear history"
                  className="text-slate-400 hover:text-rose-600 transition cursor-pointer p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {filteredHistory.length === 0 ? (
              <div className="py-8 px-3 text-center rounded-2xl bg-white/40 border border-white/50 backdrop-blur-md">
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
                    className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-white/70 text-slate-700 transition group text-left border border-transparent hover:border-white/60 cursor-pointer"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-2 h-2 rounded-full bg-blue-500/70 group-hover:bg-blue-600 group-hover:scale-125 transition flex-shrink-0" />
                      <span className="text-xs truncate font-normal">{item.title}</span>
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

        {/* Footer Actions, Contact, Admin Panel & Store Info */}
        <div className="p-4 border-t border-white/50 space-y-2.5">
          
          {/* Customer Care & WhatsApp Support Buttons */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between px-1">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Support & Contact
              </span>
              {copiedPhone && (
                <span className="text-[10px] font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 animate-fade-in">
                  Copied +91 9087086182
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2">
              {/* Connect with Call (Copies phone to clipboard & triggers call) */}
              <button
                onClick={handleCopyPhone}
                className="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-blue-50/90 hover:bg-blue-100/90 border border-blue-200/80 text-blue-700 text-xs font-semibold transition-all active:scale-95 shadow-xs cursor-pointer"
                title="Click to copy & call customer care (+91 9087086182)"
              >
                {copiedPhone ? (
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                ) : (
                  <Phone className="w-3.5 h-3.5 text-blue-600" />
                )}
                <span>{copiedPhone ? "Copied" : "Customer Care"}</span>
              </button>

              {/* Connect with WhatsApp */}
              <a
                href="https://wa.me/919087086182?text=Hello%20TechStore%2C%20I%20need%20human%20assistance"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-emerald-50/90 hover:bg-emerald-100/90 border border-emerald-200/80 text-emerald-700 text-xs font-semibold transition-all active:scale-95 shadow-xs cursor-pointer"
                title="Chat with TechStore on WhatsApp"
              >
                <MessageCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>WhatsApp</span>
              </a>
            </div>
          </div>

          {/* Admin Panel Button */}
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
            className="w-full flex items-center gap-2 p-2.5 rounded-xl bg-white/75 hover:bg-white/95 border border-white/80 text-slate-800 text-xs font-semibold transition-all transform active:scale-[0.98] shadow-xs cursor-pointer"
            title={page === "shop" ? "Back to assistant" : "Manage your shop dataset (admin only)"}
          >
            {page === "shop" ? (
              <ArrowLeft className="w-4 h-4 text-blue-600" />
            ) : (
              <Store className="w-4 h-4 text-blue-600" />
            )}
            <span>{page === "shop" ? "Back to Assistant" : "Shop / Admin Dashboard"}</span>
          </button>

          {/* Store Name and Address Box (Clickable for GMap Navigation) */}
          <div 
            onClick={handleAddressClick}
            className="p-3 rounded-2xl bg-white/55 hover:bg-white/90 border border-white/80 hover:border-blue-300 backdrop-blur-md space-y-1.5 shadow-xs hover:shadow-md transition-all duration-200 cursor-pointer group"
            title="Click to get Google Maps navigation"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs text-slate-900 font-bold">
                <Store className="w-3.5 h-3.5 text-blue-600" />
                <span>TechStore</span>
              </div>
              <span className="text-[10px] text-blue-600 group-hover:text-blue-700 font-semibold flex items-center gap-1 opacity-80 group-hover:opacity-100">
                <span>Directions</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </span>
            </div>
            
            <p className="text-[11px] text-slate-600 group-hover:text-slate-900 flex items-start gap-1.5 leading-snug transition-colors">
              <MapPin className="w-3.5 h-3.5 text-blue-500 group-hover:scale-110 transition-transform shrink-0 mt-0.5" />
              <span>Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Greater Chennai, Tamil Nadu 600066</span>
            </p>
            
            <p className="text-[10px] text-slate-500 flex items-center gap-1.5 pl-5 pt-0.5">
              <Clock className="w-3 h-3 text-slate-400" />
              <span>10:00 AM - 9:00 PM (All Days)</span>
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}

