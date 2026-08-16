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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm">
      <div className="relative w-full max-w-sm bg-white rounded-3xl p-7 shadow-2xl border border-slate-200 text-center">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition"
          title="Close"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="w-14 h-14 rounded-2xl bg-blue-900 flex items-center justify-center mx-auto">
          <Lock className="w-7 h-7 text-white" />
        </div>

        <h3 className="mt-4 font-heading text-lg font-bold text-slate-900">
          Admin Access
        </h3>
        <p className="mt-1 text-xs text-slate-500">
          The Shop / My Store page is for the admin only.
          Enter the password to continue.
        </p>

        <form onSubmit={handleSubmit} className="mt-5 space-y-3">
          <input
            type="password"
            value={pin}
            onChange={(e) => {
              setPin(e.target.value);
              setError("");
            }}
            placeholder="Enter admin password"
            autoFocus
            disabled={busy}
            className="w-full px-3 py-2.5 text-sm rounded-lg bg-white border border-slate-300 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:ring-2 focus:ring-blue-100 transition disabled:opacity-50 text-center tracking-widest"
          />

          {error && (
            <p className="text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white text-sm font-medium transition transform active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {busy ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ShieldCheck className="w-4 h-4" />
            )}
            {busy ? "Checking..." : "Unlock"}
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
