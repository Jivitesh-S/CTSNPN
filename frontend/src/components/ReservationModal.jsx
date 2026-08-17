import React, { useState, useEffect } from "react";
import { X, CheckCircle2, Shield, QrCode, Store, Clock, Phone, MapPin, Download, Printer, AlertCircle, KeyRound, RotateCw } from "lucide-react";
import QRCodeLib from "qrcode";
import { generateReservationInvoicePdf } from "../utils/pdfGenerator";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function ReservationModal({ product, onClose, onSuccess }) {
  const [step, setStep] = useState(1); // 1: details, 2: otp, 3: pass
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendTimer, setResendTimer] = useState(30);
  const [reservedPass, setReservedPass] = useState(null);
  const [qrDataUrl, setQrDataUrl] = useState("");

  useEffect(() => {
    let interval;
    if (step === 2 && resendTimer > 0) {
      interval = setInterval(() => setResendTimer((prev) => prev - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [step, resendTimer]);

  if (!product) return null;

  // Step 1: Send OTP
  const handleSendOtp = async (e) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim()) {
      setError("Please provide your name and contact phone number.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/store/reserve/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: name,
          phone: phone,
          product_id: product.id,
          shop_id: "S001"
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to send verification code.");
      setStep(2);
      setResendTimer(30);
    } catch (err) {
      setError(err.message || "Could not dispatch verification OTP.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP and create reservation
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (!otp.trim() || otp.length < 4) {
      setError("Please enter the 4-digit verification code sent to your Telegram / Phone.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/store/reserve/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: name,
          phone: phone,
          product_id: product.id,
          otp: otp.trim(),
          shop_id: "S001"
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Invalid or expired OTP.");
      
      setReservedPass(data);
      
      // Generate QR Code data URL for modal
      try {
        const qrUrl = await QRCodeLib.toDataURL(data.qr_data || `TECHSTORE:${data.token_id}:${phone}`, {
          margin: 1,
          width: 180
        });
        setQrDataUrl(qrUrl);
      } catch (e) {}

      // Auto-generate and download official E-Invoice PDF
      try {
        await generateReservationInvoicePdf(data, true);
      } catch (pdfErr) {
        console.error("Auto PDF generation error:", pdfErr);
      }

      setStep(3);
      if (onSuccess) onSuccess(data);
    } catch (err) {
      setError(err.message || "Failed to verify OTP.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!reservedPass) return;
    await generateReservationInvoicePdf(reservedPass, true);
  };

  const handlePrint = async () => {
    if (!reservedPass) return;
    const doc = await generateReservationInvoicePdf(reservedPass, false);
    doc.autoPrint();
    window.open(doc.output("bloburl"), "_blank");
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white/95 backdrop-blur-md rounded-3xl p-6 max-w-md w-full border border-slate-200/90 shadow-2xl transition-all my-8">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600">
              <Store className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 font-heading">
                In-Store Reservation Pass
              </h3>
              <p className="text-[11px] text-slate-500">24-Hour Free Device Hold • TechStore 🇮🇳</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-between mt-3 px-2 text-[10px] font-bold text-slate-400">
          <span className={step >= 1 ? "text-blue-600" : ""}>1. Details</span>
          <span>→</span>
          <span className={step >= 2 ? "text-blue-600" : ""}>2. 2FA Verification</span>
          <span>→</span>
          <span className={step === 3 ? "text-emerald-600" : ""}>3. Official E-Invoice</span>
        </div>

        {/* STEP 1: Name & Phone Form */}
        {step === 1 && (
          <form onSubmit={handleSendOtp} className="mt-4 space-y-3">
            <div className="p-3 bg-blue-50/50 rounded-xl border border-blue-100 text-xs">
              <div className="font-bold text-slate-900">{product.name}</div>
              <div className="text-blue-700 font-extrabold text-sm mt-0.5">
                Rs. {Number(product.price).toLocaleString("en-IN")}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                📍 Store: Ambattur Red Hills Rd, Surapet, Chennai
              </div>
            </div>

            {error && (
              <div className="p-2.5 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Your Full Name
              </label>
              <input
                type="text"
                placeholder="e.g. Rupika S"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:border-blue-500 bg-white"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Contact Mobile Number
              </label>
              <input
                type="tel"
                placeholder="e.g. +91 90870 86182"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:border-blue-500 bg-white"
                required
              />
              <p className="text-[10px] text-slate-400 mt-1">
                A 4-digit verification code will be sent to your Telegram / Phone.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition active:scale-95 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? "Sending Verification Code..." : "Send Verification OTP →"}
            </button>
          </form>
        )}

        {/* STEP 2: OTP Verification */}
        {step === 2 && (
          <form onSubmit={handleVerifyOtp} className="mt-4 space-y-3.5">
            <div className="p-3 bg-amber-50/60 rounded-xl border border-amber-200 text-xs">
              <div className="flex items-center gap-2 font-bold text-amber-800">
                <KeyRound className="w-4 h-4 text-amber-600" />
                <span>Enter 4-Digit Security OTP</span>
              </div>
              <p className="text-[11px] text-amber-700 mt-1">
                We sent a 4-digit code to your Telegram / Phone for <strong>{name}</strong> ({phone}).
              </p>
            </div>

            {error && (
              <div className="p-2.5 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <input
                type="text"
                maxLength={4}
                autoFocus
                placeholder="• • • •"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="w-full text-center tracking-widest text-lg font-mono font-bold px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-blue-500 bg-white"
                required
              />
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="hover:text-slate-800 text-[11px] underline cursor-pointer"
              >
                Change Number
              </button>

              <button
                type="button"
                disabled={resendTimer > 0}
                onClick={handleSendOtp}
                className="text-[11px] font-semibold text-blue-600 hover:text-blue-800 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer flex items-center gap-1"
              >
                <RotateCw className="w-3 h-3" />
                <span>{resendTimer > 0 ? `Resend in ${resendTimer}s` : "Resend OTP"}</span>
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || otp.length < 4}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition active:scale-95 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? "Verifying & Generating Pass..." : "Verify & Confirm 24h Hold"}
            </button>
          </form>
        )}

        {/* STEP 3: Confirmed Pass & E-Invoice Printing */}
        {step === 3 && reservedPass && (
          <div className="mt-4 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center shadow-xs">
              <CheckCircle2 className="w-6 h-6" />
            </div>

            <div>
              <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold mb-1">
                <span>🇮🇳 India Store Verification</span> • <span>2FA Verified</span>
              </div>
              <h4 className="text-sm font-bold text-slate-900 font-heading">
                Hold Confirmed • Token #{reservedPass.token_id}
              </h4>
              <p className="text-[11px] text-slate-500">
                Official E-Invoice &amp; In-Store Reservation Pass generated
              </p>
            </div>

            {/* Official QR Pass Card */}
            <div className="p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 rounded-2xl text-white text-center space-y-2.5 shadow-lg border border-slate-800">
              <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-slate-400 border-b border-white/10 pb-1.5">
                <span>TechStore Retail Pass</span>
                <span className="text-amber-300 font-mono">#{reservedPass.token_id}</span>
              </div>

              {qrDataUrl ? (
                <div className="w-28 h-28 bg-white rounded-xl mx-auto p-1.5 flex items-center justify-center shadow-md">
                  <img src={qrDataUrl} alt="QR Pass" className="w-full h-full object-contain" />
                </div>
              ) : (
                <div className="w-28 h-28 bg-white rounded-xl mx-auto p-2 flex items-center justify-center">
                  <QrCode className="w-24 h-24 text-slate-900" />
                </div>
              )}

              <div className="space-y-0.5">
                <div className="text-xs font-bold text-white line-clamp-1">
                  {reservedPass.product_name}
                </div>
                <div className="text-sm font-extrabold text-blue-400">
                  Rs. {Number(reservedPass.price || 0).toLocaleString("en-IN")}
                </div>
                <div className="text-[10px] text-slate-300">
                  Customer: <strong>{reservedPass.customer_name}</strong> • {reservedPass.phone}
                </div>
              </div>

              <div className="text-[10px] text-emerald-400 bg-emerald-950/60 py-1 rounded-lg border border-emerald-500/30">
                ⏳ Valid for 24 Hours • 10:00 AM – 9:00 PM
              </div>
            </div>

            {/* Action Buttons for Invoice PDF & Print */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                onClick={handleDownloadPdf}
                className="py-2.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-xs transition active:scale-95 flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF</span>
              </button>

              <button
                onClick={handlePrint}
                className="py-2.5 px-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-bold shadow-xs transition active:scale-95 flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Invoice</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition cursor-pointer"
            >
              Done &amp; Return to Chat
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
