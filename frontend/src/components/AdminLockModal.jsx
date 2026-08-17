import React, { useState } from "react";
import { Lock, X, Loader2, ShieldCheck } from "lucide-react";

export function AdminLockModal({ isOpen, onClose, onUnlock }) {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (busy) return;
    if (!pin.trim()) {
      setError("Enter the admin password.");
      return;
    }
    setBusy(true);
    setError("");
    const ok = await onUnlock(pin.trim());
    setBusy(false);
    if (ok) {
      setPin("");
    } else {
      setError("Incorrect password. Please try again.");
    }
  };

  const handleClose = () => {
    if (busy) return;
    setPin("");
    setError("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md transition-all">
      <div className="relative w-full max-w-sm glass-panel-deep rounded-3xl p-7 shadow-2xl text-center">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-xl hover:bg-white/70 text-slate-500 hover:text-slate-900 transition active:scale-95"
          title="Close"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-blue-500/25 ring-1 ring-white/70">
          <Lock className="w-7 h-7 text-white" />
        </div>

        <h3 className="mt-4 font-heading text-xl font-bold text-slate-900 tracking-tight">
          Admin Access
        </h3>
        <p className="mt-1.5 text-xs text-slate-600 font-normal leading-relaxed">
          The Shop / Admin page is restricted.
          Enter the PIN password to manage datasets and catalogs.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-3.5">
          <input
            type="password"
            value={pin}
            onChange={(e) => {
              setPin(e.target.value);
              setError("");
            }}
            placeholder="Enter admin PIN"
            autoFocus
            disabled={busy}
            className="w-full px-4 py-2.5 text-sm rounded-xl bg-white/80 border border-white/90 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition disabled:opacity-50 text-center tracking-widest shadow-xs"
          />

          {error && (
            <p className="text-xs text-rose-700 bg-rose-500/10 border border-rose-500/20 backdrop-blur-md rounded-xl px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-semibold transition-all transform active:scale-[0.98] shadow-md shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {busy ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ShieldCheck className="w-4 h-4" />
            )}
            {busy ? "Authenticating..." : "Unlock Dashboard"}
          </button>
        </form>

        <p className="mt-4 text-[11px] text-slate-400">
          Once unlocked, access stays open for this browser session.
        </p>
      </div>
    </div>
  );
}

export default AdminLockModal;
