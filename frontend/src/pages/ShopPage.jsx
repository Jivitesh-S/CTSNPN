import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Store,
  MapPin,
  Phone,
  Clock,
  Package,
  Upload,
  Trash2,
  Search,
  Loader2,
  CheckCircle2,
  XCircle,
  Info,
  FileDown,
  Ticket,
  ShoppingBag,
  PhoneCall,
  MessageCircle,
  Calendar,
  RefreshCw,
  Send,
  AlertCircle
} from "lucide-react";

import { Header } from "../components/Header";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const CSV_TEMPLATE =
  "name,brand,category,price,stock,warranty_months,description,processor,ram,display\n" +
  "MacBook Air M3,Apple,laptop,114900,In stock,12,Ultra-portable laptop with Apple Silicon M3,Apple M3 8-core,8GB Unified,13.6-inch Liquid Retina\n" +
  "Samsung Galaxy S24,Samsung,phone,79999,In stock,12,Flagship AI smartphone with Dynamic AMOLED,Snapdragon 8 Gen 3,8GB,6.2-inch FHD+ 120Hz\n" +
  "Sony WH-1000XM5,Sony,accessory,29990,In stock,12,Industry-leading noise cancelling wireless headphones,V1 Integrated Processor,-,30mm Driver\n";

export function ShopPage() {
  const navigate = useNavigate();

  const [shop, setShop] = useState(null);
  const [products, setProducts] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loadingShop, setLoadingShop] = useState(true);
  const [shopError, setShopError] = useState("");

  const [activeTab, setActiveTab] = useState("tickets");

  // Manage state
  const [productFilter, setProductFilter] = useState("");
  const [ticketFilter, setTicketFilter] = useState("all");
  const [savingDelete, setSavingDelete] = useState(null);
  const [updatingTicket, setUpdatingTicket] = useState(null);
  const [rejectModalToken, setRejectModalToken] = useState(null);
  const [rejectionReason, setRejectionReason] = useState("");
  const [submittingReject, setSubmittingReject] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null);
  const fileInputRef = useRef(null);

  const loadShop = async () => {
    setLoadingShop(true);
    setShopError("");
    try {
      const res = await fetch(`${API_BASE}/shops`);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setShop(data[0]);
        return data[0];
      } else {
        setShop(null);
        return null;
      }
    } catch (error) {
      console.error("Failed to fetch shop:", error);
      setShopError("Could not load shop information. Make sure the backend is running.");
      return null;
    } finally {
      setLoadingShop(false);
    }
  };

  const loadProducts = async (shopId) => {
    const targetShopId = shopId || (shop && shop.id) || "S001";
    try {
      const res = await fetch(`${API_BASE}/shops/${targetShopId}/products`);
      if (!res.ok) return;
      const data = await res.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    }
  };

  const getAdminHeaders = () => {
    const token = sessionStorage.getItem("admin_token") || "1234";
    return {
      "Content-Type": "application/json",
      "X-Admin-Token": token,
    };
  };

  const loadTickets = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/service-tokens`, {
        headers: getAdminHeaders(),
      });
      if (!res.ok) return;
      const data = await res.json();
      setTickets(data.tokens || []);
    } catch (error) {
      console.error("Failed to fetch tickets:", error);
    }
  };

  const loadOrders = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/orders`, {
        headers: getAdminHeaders(),
      });
      if (!res.ok) return;
      const data = await res.json();
      setOrders(data.orders || []);
    } catch (error) {
      console.error("Failed to fetch orders:", error);
    }
  };

  useEffect(() => {
    if (sessionStorage.getItem("shop_unlocked") !== "1") {
      navigate("/", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const init = async () => {
      const loadedShop = await loadShop();
      await loadProducts(loadedShop ? loadedShop.id : "S001");
      await loadTickets();
      await loadOrders();
    };
    init();
  }, []);

  useEffect(() => {
    if (shop) loadProducts(shop.id);
  }, [shop]);


  const handleDeleteProduct = async (product) => {
    if (!window.confirm(`Delete "${product.name}" from the catalog?`)) return;
    setSavingDelete(product.id);
    setStatus(null);
    try {
      const res = await fetch(`${API_BASE}/shops/${shop.id}/products/${product.id}`, {
        method: "DELETE",
        headers: getAdminHeaders(),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setStatus({ type: "success", message: `"${product.name}" was removed.` });
      await loadProducts(shop.id);
      await loadShop();
    } catch (error) {
      console.error("Failed to delete product:", error);
      setStatus({ type: "error", message: "Could not delete the product." });
    } finally {
      setSavingDelete(null);
    }
  };

  const handleUpdateTicketStatus = async (tokenId, newStatus, ticketObj = null) => {
    if (newStatus === "Rejected") {
      const target = ticketObj || tickets.find((t) => t.token_id === tokenId);
      setRejectModalToken(target);
      setRejectionReason("");
      return;
    }
    setUpdatingTicket(tokenId);
    try {
      const res = await fetch(`${API_BASE}/admin/service-tokens/${tokenId}`, {
        method: "PATCH",
        headers: getAdminHeaders(),
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error("Failed to update status");
      setStatus({ type: "success", message: `Ticket #${tokenId} marked as ${newStatus}.` });
      await loadTickets();
      await loadOrders();
    } catch (error) {
      console.error("Error updating ticket status:", error);
      setStatus({ type: "error", message: "Failed to update ticket status." });
    } finally {
      setUpdatingTicket(null);
    }
  };

  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      const res = await fetch(`${API_BASE}/admin/orders/${orderId}/status`, {
        method: "PATCH",
        headers: getAdminHeaders(),
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error("Failed to update order status");
      const data = await res.json();
      setStatus({
        type: "success",
        message: `Order #${orderId} marked as ${newStatus}. ${data.telegram_sent ? "(Telegram customer notification dispatched)" : ""}`
      });
      await loadOrders();
    } catch (error) {
      console.error("Error updating order status:", error);
      setStatus({ type: "error", message: "Could not update order status." });
    }
  };


  const handleConfirmReject = async () => {
    if (!rejectModalToken) return;
    if (!rejectionReason.trim()) {
      alert("Please enter a rejection reason.");
      return;
    }
    setSubmittingReject(true);
    try {
      const res = await fetch(`${API_BASE}/admin/service-tokens/${rejectModalToken.token_id}/reject`, {
        method: "POST",
        headers: getAdminHeaders(),
        body: JSON.stringify({ rejection_reason: rejectionReason.trim() }),
      });
      if (!res.ok) throw new Error("Failed to reject service token");
      setStatus({
        type: "success",
        message: `Cancellation for #${rejectModalToken.token_id} rejected & Telegram notice sent to customer. Token removed from requests and Order #${rejectModalToken.order_id} restored to Customer Catalog.`,
      });
      setRejectModalToken(null);
      setRejectionReason("");
      await loadTickets();
      await loadOrders();
      setActiveTab("orders");
    } catch (error) {
      console.error("Error submitting rejection:", error);
      setStatus({ type: "error", message: "Failed to reject ticket." });
    } finally {
      setSubmittingReject(false);
    }
  };


  const handleUpload = async (file) => {

    if (!file) return;
    setUploading(true);
    setStatus(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/shops/${shop.id}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        const detail = data.detail || `Server returned ${res.status}`;
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }
      const errorCount = (data.errors || []).length;
      setStatus({
        type: errorCount > 0 ? "warn" : "success",
        message: `Upload complete: ${data.added} product(s) added, ${data.skipped} skipped${errorCount ? `, ${errorCount} row(s) had errors.` : "."}`,
      });
      await loadProducts(shop.id);
      await loadShop();
    } catch (error) {
      console.error("Failed to upload:", error);
      setStatus({ type: "error", message: error.message });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const downloadTemplate = () => {
    const blob = new Blob([CSV_TEMPLATE], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "techstore_catalog_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredProducts = products.filter((p) => {
    if (!productFilter) return true;
    const query = productFilter.toLowerCase();
    return (
      (p.name && p.name.toLowerCase().includes(query)) ||
      (p.brand && p.brand.toLowerCase().includes(query)) ||
      (p.category && p.category.toLowerCase().includes(query))
    );
  });

  const filteredTickets = tickets.filter((t) => {
    if (t.status === "Rejected") return false;
    if (ticketFilter === "all") return true;
    if (ticketFilter === "pending") return t.status === "Pending Contact";
    if (ticketFilter === "contacted") return t.status === "Contacted";
    if (ticketFilter === "resolved") return t.status === "Resolved";
    return true;
  });


  const pendingCount = tickets.filter((t) => t.status === "Pending Contact").length;

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-900/[0.02]">
      <Header />

      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {/* Top bar with back button & shop switcher */}
        <div className="border-b border-white/60 bg-white/40 backdrop-blur-md px-4 sm:px-8 py-3 flex items-center justify-between gap-4 flex-wrap shadow-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-white/80 bg-white/60 hover:bg-white text-slate-700 text-xs font-semibold shadow-xs transition active:scale-95 cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Chat</span>
            </button>
            <div className="h-4 w-px bg-slate-300" />
            <h2 className="font-heading text-sm font-bold text-slate-800 flex items-center gap-2">
              <Store className="w-4 h-4 text-blue-600" />
              Store Admin Hub
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                loadShop();
                loadProducts(shop ? shop.id : "S001");
                loadTickets();
                loadOrders();
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/60 hover:bg-white text-slate-700 text-xs font-semibold shadow-xs border border-white/80 transition active:scale-95 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5 text-blue-600" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Global status alert */}
        {status && (
          <div className="px-4 sm:px-8 pt-3">
            <div
              className={`p-3 rounded-2xl text-xs font-medium flex items-center justify-between gap-2 shadow-xs ${
                status.type === "success"
                  ? "bg-emerald-500/10 text-emerald-800 border border-emerald-500/20"
                  : status.type === "warn"
                  ? "bg-amber-500/10 text-amber-800 border border-amber-500/20"
                  : "bg-rose-500/10 text-rose-800 border border-rose-500/20"
              }`}
            >
              <div className="flex items-center gap-2">
                {status.type === "success" && <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />}
                {status.type === "warn" && <Info className="w-4 h-4 text-amber-600 flex-shrink-0" />}
                {status.type === "error" && <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />}
                <span>{status.message}</span>
              </div>
              <button
                onClick={() => setStatus(null)}
                className="text-xs font-bold opacity-60 hover:opacity-100 px-2 py-0.5 cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Store Overview Bar */}
        {shop && (
          <div className="px-4 sm:px-8 pt-3">
            <div className="glass-panel-deep rounded-2xl p-4 flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-heading font-extrabold shadow-md shadow-blue-500/20">
                  {shop.name ? shop.name.charAt(0) : "T"}
                </div>
                <div>
                  <h3 className="font-heading font-bold text-slate-900 text-sm">{shop.name}</h3>
                  <p className="text-xs text-slate-500 flex items-center gap-2">
                    <MapPin className="w-3 h-3 text-slate-400" /> {shop.address}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-600 font-medium flex-wrap">
                <span className="flex items-center gap-1">
                  <Phone className="w-3 h-3 text-emerald-600" /> {shop.phone}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-blue-600" /> {shop.opening_hours}
                </span>
                <span className="flex items-center gap-1 bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg border border-blue-200/60 font-semibold">
                  <Package className="w-3.5 h-3.5" /> {products.length} Products
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="px-4 sm:px-8 pt-4 flex items-center gap-2 border-b border-slate-200/80">
          <button
            onClick={() => setActiveTab("tickets")}
            className={`pb-3 px-3 text-xs font-bold flex items-center gap-2 border-b-2 transition cursor-pointer ${
              activeTab === "tickets"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Ticket className="w-4 h-4" />
            <span>Service Tokens &amp; Requests</span>
            {pendingCount > 0 && (
              <span className="px-1.5 py-0.2 bg-rose-500 text-white rounded-full text-[10px] font-extrabold animate-pulse">
                {pendingCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("orders")}
            className={`pb-3 px-3 text-xs font-bold flex items-center gap-2 border-b-2 transition cursor-pointer ${
              activeTab === "orders"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <ShoppingBag className="w-4 h-4" />
            <span>Customer Orders ({orders.length})</span>
          </button>

          <button
            onClick={() => {
              setActiveTab("products");
              loadProducts(shop ? shop.id : "S001");
            }}
            className={`pb-3 px-3 text-xs font-bold flex items-center gap-2 border-b-2 transition cursor-pointer ${
              activeTab === "products"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Package className="w-4 h-4" />
            <span>Product Catalog ({products.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("upload")}
            className={`pb-3 px-3 text-xs font-bold flex items-center gap-2 border-b-2 transition cursor-pointer ${
              activeTab === "upload"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Upload Dataset</span>
          </button>
        </div>

        {/* ============ SERVICE TOKENS TAB ============ */}
        {activeTab === "tickets" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-5">
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <h3 className="font-heading text-base font-bold text-slate-900 flex items-center gap-2">
                    <Ticket className="w-4.5 h-4.5 text-blue-600" />
                    Support Requests &amp; Cancellation Log
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Tokens raised by customer 2FA verification in the chatbot
                  </p>
                </div>

                {/* Filter buttons */}
                <div className="flex items-center gap-1.5 bg-white/70 backdrop-blur-md p-1 rounded-xl border border-white/80 shadow-xs">
                  {["all", "pending", "contacted", "resolved"].map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setTicketFilter(filter)}
                      className={`text-xs font-semibold px-3 py-1 rounded-lg capitalize transition cursor-pointer ${
                        ticketFilter === filter
                          ? "bg-blue-600 text-white shadow-xs"
                          : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/50"
                      }`}
                    >
                      {filter}
                    </button>
                  ))}
                </div>

              </div>

              {filteredTickets.length === 0 ? (
                <div className="py-12 text-center glass-panel rounded-2xl p-6">
                  <Ticket className="w-10 h-10 text-slate-400 mx-auto mb-2 opacity-60" />
                  <p className="text-sm text-slate-600 font-medium">No service tickets matching this filter.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredTickets.map((t) => {
                    const cleanPhone = (t.phone || "").replace(/[^0-9]/g, "");
                    const isPending = t.status === "Pending Contact";
                    return (
                      <div
                        key={t.token_id}
                        className={`glass-card rounded-2xl p-4 sm:p-5 border-l-4 transition-all ${
                          t.status === "Rejected"
                            ? "border-l-rose-500 bg-rose-500/[0.02]"
                            : isPending
                            ? "border-l-amber-500 bg-amber-500/[0.02]"
                            : "border-l-blue-500"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4 flex-wrap">
                          <div className="min-w-0 flex-1 space-y-2">
                            <div className="flex items-center gap-2.5 flex-wrap">
                              <span className="font-heading font-extrabold text-base text-slate-900 bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-lg border border-blue-200">
                                #{t.token_id}
                              </span>
                              <span className="font-semibold text-slate-800 text-sm">{t.customer_name}</span>
                              <span
                                className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                                  t.request_type === "Cancellation"
                                    ? "bg-rose-100 text-rose-700 border-rose-200"
                                    : "bg-purple-100 text-purple-700 border-purple-200"
                                }`}
                              >
                                {t.request_type}
                              </span>
                              <span
                                className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                                  t.status === "Pending Contact"
                                    ? "bg-amber-100 text-amber-800 border-amber-300 animate-pulse"
                                    : t.status === "Contacted"
                                    ? "bg-blue-100 text-blue-800 border-blue-300"
                                    : t.status === "Rejected"
                                    ? "bg-rose-100 text-rose-800 border-rose-300 font-bold"
                                    : "bg-emerald-100 text-emerald-800 border-emerald-300"
                                }`}
                              >
                                {t.status}
                              </span>
                            </div>

                            <div className="flex items-center gap-4 text-xs text-slate-600 font-medium flex-wrap">
                              <span className="flex items-center gap-1">
                                <ShoppingBag className="w-3.5 h-3.5 text-blue-600" />
                                Order: <strong className="text-slate-800">{t.order_id}</strong> ({t.model_name})
                              </span>
                              <span className="flex items-center gap-1">
                                <Phone className="w-3.5 h-3.5 text-emerald-600" />
                                {t.phone}
                              </span>
                              {t.created_at && (
                                <span className="flex items-center gap-1 text-slate-400">
                                  <Calendar className="w-3.5 h-3.5" />
                                  {new Date(t.created_at).toLocaleString()}
                                </span>
                              )}
                            </div>

                            {t.reason && (
                              <p className="text-xs text-slate-600 bg-white/50 p-2.5 rounded-xl border border-white/80">
                                <span className="font-semibold text-slate-700">Reason:</span> {t.reason}
                              </p>
                            )}

                            {/* Rejection Notification Banner */}
                            {t.status === "Rejected" && (
                              <div className="p-3 rounded-xl bg-rose-50/90 border border-rose-200 text-xs text-rose-950 space-y-1.5 mt-2 shadow-xs">
                                <div className="flex items-center gap-1.5 font-bold text-rose-700">
                                  <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                                  <span>Cancellation Rejected &amp; Order Restored to Active</span>
                                </div>
                                <p className="italic bg-white/90 p-2.5 rounded-lg border border-rose-200/60 text-slate-800 font-medium leading-relaxed">
                                  "Hey {t.customer_name?.split(" ")[0] || "Customer"}, your order cancellation for #{t.order_id} was rejected due to: <strong className="text-rose-700 not-italic">{t.admin_notes || "Order dispatch in progress"}</strong>. Contact us for further information. Thank you."
                                </p>
                              </div>
                            )}
                          </div>

                          {/* Quick Admin Actions */}
                          <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2 flex-shrink-0">
                            {t.phone && (
                              <a
                                href={`tel:${t.phone}`}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition active:scale-95"
                                title="Call Customer"
                              >
                                <PhoneCall className="w-3.5 h-3.5" />
                                <span>Call</span>
                              </a>
                            )}
                            {cleanPhone && (
                              <a
                                href={`https://wa.me/${cleanPhone}?text=Hello%20${encodeURIComponent(t.customer_name)}%2C%20regarding%20your%20Service%20Token%20%23${t.token_id}%20at%20TechStore...`}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 text-xs font-semibold transition active:scale-95"
                                title="WhatsApp Customer"
                              >
                                <MessageCircle className="w-3.5 h-3.5" />
                                <span>WhatsApp</span>
                              </a>
                            )}

                            {/* Status Changer */}
                            <select
                              value={t.status}
                              disabled={updatingTicket === t.token_id}
                              onChange={(e) => handleUpdateTicketStatus(t.token_id, e.target.value, t)}
                              className={`text-xs font-semibold px-2.5 py-1.5 rounded-xl bg-white border shadow-xs focus:outline-none focus:ring-1 cursor-pointer ${
                                t.status === "Rejected"
                                  ? "border-rose-300 text-rose-700 focus:ring-rose-500"
                                  : "border-slate-300 text-slate-700 focus:ring-blue-500"
                              }`}
                            >
                              <option value="Pending Contact">Pending Contact</option>
                              <option value="Contacted">Mark Contacted</option>
                              <option value="Resolved">Mark Resolved</option>
                              <option value="Rejected">Reject</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </main>
        )}

        {/* ============ ORDERS TAB ============ */}
        {activeTab === "orders" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <h3 className="font-heading text-base font-bold text-slate-900 flex items-center gap-2">
                    <ShoppingBag className="w-4.5 h-4.5 text-blue-600" />
                    Customer Orders ({orders.length})
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Orders eligible for status inquiry, cancellation, and warranty replacements
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {orders.map((o) => (
                  <div key={o.order_id} className="glass-card rounded-2xl p-4 sm:p-5">
                    <div className="flex items-start justify-between gap-3 flex-wrap">
                      <div className="min-w-0 space-y-1.5">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <span className="font-heading font-extrabold text-sm text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                            #{o.order_id}
                          </span>
                          <span className="font-bold text-slate-900 text-sm">{o.model_bought}</span>
                          <span
                            className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                              o.status === "Cancelled"
                                ? "bg-rose-100 text-rose-700 border-rose-200"
                                : o.status === "Delivered"
                                ? "bg-emerald-100 text-emerald-700 border-emerald-200"
                                : o.status === "Shipped"
                                ? "bg-sky-100 text-sky-700 border-sky-200"
                                : "bg-amber-100 text-amber-700 border-amber-200"
                            }`}
                          >
                            {o.status}
                          </span>
                        </div>

                        <div className="flex items-center gap-4 text-xs text-slate-600 font-medium flex-wrap">
                          <span>👤 {o.customer_name}</span>
                          <span>📱 {o.phone}</span>
                          <span>📅 Purchased: {o.purchase_date}</span>
                          <span className="font-bold text-blue-700">Rs. {Number(o.price || 0).toLocaleString()}</span>
                          <span>🛡️ Warranty: {o.warranty_months}m</span>
                        </div>
                      </div>

                      {/* Order Status Controller with Telegram Dispatch */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <select
                          value={o.status}
                          onChange={(e) => handleUpdateOrderStatus(o.order_id, e.target.value)}
                          className="text-xs font-semibold px-2.5 py-1.5 rounded-xl bg-white border border-slate-300 text-slate-700 shadow-xs focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                        >
                          <option value="Processing">Processing</option>
                          <option value="Confirmed">Confirmed</option>
                          <option value="Shipped">Shipped (Telegram Alert)</option>
                          <option value="Out for Delivery">Out for Delivery</option>
                          <option value="Delivered">Delivered</option>
                          <option value="Cancelled">Cancelled</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </main>
        )}

        {/* ============ PRODUCTS TAB ============ */}
        {activeTab === "products" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <h3 className="font-heading text-base font-bold text-slate-900 flex items-center gap-2">
                  <Package className="w-4 h-4 text-blue-600" />
                  Store Products ({filteredProducts.length})
                </h3>
                <div className="relative w-full sm:w-72">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={productFilter}
                    onChange={(e) => setProductFilter(e.target.value)}
                    placeholder="Filter products by name or category..."
                    className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-white/70 backdrop-blur-md border border-white/80 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition shadow-xs"
                  />
                </div>
              </div>

              {filteredProducts.length === 0 ? (
                <div className="py-12 text-center glass-panel rounded-2xl p-6">
                  <Package className="w-10 h-10 text-slate-400 mx-auto mb-2 opacity-60" />
                  <p className="text-sm text-slate-600 font-medium">
                    {products.length === 0
                      ? "No products yet. Upload a dataset in the 'Upload Dataset' tab."
                      : "No products match your search query."}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredProducts.map((product) => (
                    <div key={product.id} className="glass-card rounded-2xl p-4 sm:p-5">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-heading font-bold text-slate-900 text-sm sm:text-base">
                              {product.name}
                            </span>
                            {product.brand && (
                              <span className="text-xs text-slate-500 font-medium">by {product.brand}</span>
                            )}
                            <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-blue-100/70 text-blue-700 border border-blue-200/50">
                              {product.category}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center gap-3 flex-wrap text-xs text-slate-600 font-medium">
                            <span className="font-heading font-bold text-blue-700 text-sm">
                              Rs. {Number(product.price || 0).toLocaleString()}
                            </span>
                            <span
                              className={`px-2.5 py-0.5 rounded-full font-medium ${
                                product.stock === "In stock"
                                  ? "bg-emerald-500/10 text-emerald-700 border border-emerald-500/20"
                                  : product.stock === "Low stock"
                                  ? "bg-amber-500/10 text-amber-700 border border-amber-500/20"
                                  : "bg-rose-500/10 text-rose-700 border border-rose-500/20"
                              }`}
                            >
                              {product.stock}
                            </span>
                            <span>Warranty: {product.warranty_months || 0} months</span>
                          </div>
                          {product.description && (
                            <p className="text-xs text-slate-600 mt-2 font-normal leading-relaxed">
                              {product.description}
                            </p>
                          )}
                          {Object.keys(product.specs || {}).length > 0 && (
                            <div className="mt-2.5 flex flex-wrap gap-1.5">
                              {Object.entries(product.specs).map(([key, value]) => (
                                <span
                                  key={key}
                                  className="text-[11px] px-2.5 py-0.5 rounded-lg bg-white/70 border border-white/80 text-slate-700 shadow-xs"
                                >
                                  <span className="font-semibold text-slate-800">{key.replace(/_/g, " ")}:</span>{" "}
                                  {value}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteProduct(product)}
                          disabled={savingDelete === product.id}
                          className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-500/10 transition flex-shrink-0 disabled:opacity-40 active:scale-95 cursor-pointer"
                          title={`Delete ${product.name}`}
                        >
                          {savingDelete === product.id ? (
                            <Loader2 className="w-4 h-4 animate-spin text-rose-600" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </main>
        )}

        {/* ============ UPLOAD TAB ============ */}
        {activeTab === "upload" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <section className="glass-panel-deep rounded-3xl p-6 sm:p-7 space-y-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-md shadow-blue-500/20 ring-1 ring-white/60">
                    <Upload className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-heading text-base font-bold text-slate-900 tracking-tight">
                      Upload Product Dataset
                    </h3>
                    <p className="text-xs text-slate-500">
                      Sync inventory and technical manuals directly to RAG ChromaDB
                    </p>
                  </div>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  Upload a <span className="font-semibold text-slate-800">CSV</span> or{" "}
                  <span className="font-semibold text-slate-800">JSON</span> file. Each row/item is one product.
                  Required columns: <span className="font-semibold text-blue-700">name</span>. Optional: brand, category
                  (phone/laptop/accessory), price, stock, warranty_months, description - any extra
                  columns become specifications.
                </p>

                <div className="flex items-center gap-3 pt-2 flex-wrap">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.json"
                    disabled={uploading}
                    onChange={(e) => handleUpload(e.target.files[0])}
                    className="text-xs text-slate-700 file:mr-3 file:px-4 file:py-2.5 file:rounded-xl file:border file:border-white/80 file:bg-white/80 file:text-slate-800 file:text-xs file:font-semibold hover:file:bg-white transition cursor-pointer shadow-xs"
                  />
                  {uploading && (
                    <span className="flex items-center gap-2 text-xs font-semibold text-blue-700">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      Uploading &amp; re-indexing into vector store...
                    </span>
                  )}
                </div>

                <div className="pt-2">
                  <button
                    onClick={downloadTemplate}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-white/80 bg-white/70 backdrop-blur-md text-slate-700 text-xs font-semibold transition hover:bg-white hover:text-blue-700 shadow-xs active:scale-95 cursor-pointer"
                  >
                    <FileDown className="w-3.5 h-3.5 text-blue-600" />
                    Download CSV Template
                  </button>
                </div>
              </section>

              <div className="pb-4 text-center">
                <p className="text-[11px] text-slate-500">
                  After upload, the assistant answers queries regarding these products instantly with live embeddings.
                </p>
              </div>
            </div>
          </main>
        )}
      </div>

      {/* ============ REJECTION MODAL ============ */}
      {rejectModalToken && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in">
          <div className="glass-panel-deep rounded-3xl max-w-md w-full p-6 shadow-2xl border border-white/80 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2 text-rose-600 font-heading font-bold text-base">
                <XCircle className="w-5 h-5" />
                Reject Cancellation Request
              </div>
              <button
                onClick={() => setRejectModalToken(null)}
                className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1">
              <p className="text-slate-700">
                <strong>Token:</strong> <span className="font-mono text-blue-700 font-bold">#{rejectModalToken.token_id}</span> • <strong>Order:</strong> <span className="font-mono font-bold">#{rejectModalToken.order_id}</span>
              </p>
              <p className="text-slate-700">
                <strong>Customer:</strong> {rejectModalToken.customer_name} ({rejectModalToken.phone})
              </p>
              <p className="text-slate-700">
                <strong>Product:</strong> {rejectModalToken.model_name}
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                Rejection Reason / Message: <span className="text-rose-500">*</span>
              </label>
              <textarea
                rows={3}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g. Order already packed and dispatched from central warehouse / Beyond return window."
                className="w-full text-xs p-3 rounded-xl bg-white border border-slate-300 focus:outline-none focus:ring-2 focus:ring-rose-500/30 resize-none font-normal"
              />
              <p className="text-[11px] text-slate-500">
                Submitting this will notify the customer via Telegram &amp; restore the Order back to active state in the database.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setRejectModalToken(null)}
                disabled={submittingReject}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReject}
                disabled={submittingReject || !rejectionReason.trim()}
                className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 active:scale-95 text-white text-xs font-semibold shadow-md transition disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
              >
                {submittingReject ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Sending Report...
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    Send Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ShopPage;
