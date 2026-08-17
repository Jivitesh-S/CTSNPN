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
  FileDown
} from "lucide-react";

import { Header } from "../components/Header";

const API_BASE = "http://127.0.0.1:8000";

const CSV_TEMPLATE =
  "name,brand,category,price,stock,warranty_months,description,display,processor,ram,storage,camera,battery\n" +
  "Galaxy S25,Samsung,phone,84999,In stock,12,Latest flagship with great camera,6.2\" AMOLED,Snapdragon 8 Elite,12GB,256GB,50MP,~23h\n" +
  "Galaxy Book4,Samsung,laptop,54990,In stock,12,Ultra light laptop,15.6\" FHD,Core Ultra 5,16GB,512GB,-,~15h\n";

function ShopPage() {
  const navigate = useNavigate();
  const [shop, setShop] = useState(null);
  const [products, setProducts] = useState([]);
  const [loadingShop, setLoadingShop] = useState(true);
  const [shopError, setShopError] = useState("");

  const [activeTab, setActiveTab] = useState("products");

  // Manage state
  const [productFilter, setProductFilter] = useState("");
  const [savingDelete, setSavingDelete] = useState(null);
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
      const shops = data.shops || [];
      if (shops.length === 0) {
        setShopError("No shop found. The backend has no shop data yet.");
        return;
      }
      setShop(shops[0]);
    } catch (error) {
      console.error("Failed to fetch shop:", error);
      setShopError("Could not reach the backend. Is it running?");
    } finally {
      setLoadingShop(false);
    }
  };

  const loadProducts = async (shopId) => {
    try {
      const res = await fetch(`${API_BASE}/shops/${shopId}/products`);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error("Failed to fetch products:", error);
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
      await loadShop();
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
    const blob = new Blob([CSV_TEMPLATE], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "products_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredProducts = productFilter.trim()
    ? products.filter((p) =>
        `${p.name} ${p.brand} ${p.category}`.toLowerCase().includes(productFilter.trim().toLowerCase())
      )
    : products;

  const tabs = [
    { key: "products", label: "Products" },
    { key: "upload", label: "Upload Dataset" },
  ];

  if (loadingShop) {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-slate-700 font-sans">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600 mr-2" />
        <span className="font-medium text-sm">Loading shop details...</span>
      </div>
    );
  }

  if (shopError) {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-slate-700 font-sans p-4">
        <div className="text-center space-y-3 glass-panel-deep p-8 rounded-3xl max-w-md">
          <p className="text-sm text-rose-700 font-medium">{shopError}</p>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition hover:from-blue-700 hover:to-purple-700 mx-auto active:scale-95"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Assistant
          </button>
        </div>
      </div>
    );
  }

  const shopName = shop?.name || "My Store";

  return (
    <div className="relative flex h-screen w-screen overflow-hidden font-sans">

      <div className="flex-1 flex flex-col h-full relative z-10 overflow-hidden">

        <Header />

        {/* Shop banner */}
        <div className="border-b border-white/50 bg-white/40 backdrop-blur-xl px-4 sm:px-8 py-5">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div className="flex items-start gap-3.5 min-w-0">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20 ring-1 ring-white/60">
                  <Store className="w-6 h-6 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h2 className="font-heading font-bold text-xl text-slate-900 tracking-tight">
                      {shopName}
                    </h2>
                    {shop?.category && (
                      <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-blue-100/80 text-blue-700 border border-blue-200/60 shadow-xs">
                        {shop.category}
                      </span>
                    )}
                  </div>
                  {shop?.description && (
                    <p className="text-xs text-slate-600 mt-1 font-normal">{shop.description}</p>
                  )}
                  <div className="mt-2 flex items-center gap-3.5 flex-wrap text-xs text-slate-500 font-medium">
                    {(shop?.address || shop?.city) && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-blue-600" />
                        {[shop.address, shop.city].filter(Boolean).join(", ")}
                      </span>
                    )}
                    {shop?.phone && (
                      <span className="flex items-center gap-1">
                        <Phone className="w-3.5 h-3.5 text-blue-600" />
                        {shop.phone}
                      </span>
                    )}
                    {shop?.timings && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-blue-600" />
                        {shop.timings}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Package className="w-3.5 h-3.5 text-purple-600" />
                      {products.length} catalog items
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => navigate("/")}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-white/80 bg-white/70 backdrop-blur-md text-slate-700 text-xs font-semibold transition hover:bg-white hover:text-blue-700 shadow-xs active:scale-95 flex-shrink-0"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Back to Assistant
              </button>
            </div>

            {/* Tabs */}
            <div className="mt-5 flex gap-2">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all shadow-xs active:scale-95 cursor-pointer ${
                    activeTab === tab.key
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md shadow-blue-500/20"
                      : "bg-white/60 hover:bg-white/90 text-slate-700 border border-white/80"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Status banner */}
        {status && (
          <div className="px-4 sm:px-8 pt-4">
            <div className={`max-w-4xl mx-auto flex items-start gap-2.5 px-4 py-3 rounded-2xl border backdrop-blur-md text-xs sm:text-sm ${
              status.type === "success"
                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-800"
                : status.type === "warn"
                ? "bg-amber-500/10 border-amber-500/20 text-amber-800"
                : "bg-rose-500/10 border-rose-500/20 text-rose-800"
            }`}>
              {status.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-emerald-600" />
              ) : status.type === "warn" ? (
                <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
              ) : (
                <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-600" />
              )}
              <span className="font-medium">{status.message}</span>
            </div>
          </div>
        )}

        {/* ============ PRODUCTS TAB ============ */}
        {activeTab === "products" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
            <div className="max-w-4xl mx-auto w-full space-y-4">
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
                            <span className="font-heading font-bold text-slate-900 text-sm sm:text-base">{product.name}</span>
                            {product.brand && <span className="text-xs text-slate-500 font-medium">by {product.brand}</span>}
                            <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full bg-blue-100/70 text-blue-700 border border-blue-200/50">
                              {product.category}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center gap-3 flex-wrap text-xs text-slate-600 font-medium">
                            <span className="font-heading font-bold text-blue-700 text-sm">
                              Rs. {Number(product.price || 0).toLocaleString()}
                            </span>
                            <span className={`px-2.5 py-0.5 rounded-full font-medium ${
                              product.stock === "In stock"
                                ? "bg-emerald-500/10 text-emerald-700 border border-emerald-500/20"
                                : product.stock === "Low stock"
                                ? "bg-amber-500/10 text-amber-700 border border-amber-500/20"
                                : "bg-rose-500/10 text-rose-700 border border-rose-500/20"
                            }`}>
                              {product.stock}
                            </span>
                            <span>Warranty: {product.warranty_months || 0} months</span>
                          </div>
                          {product.description && (
                            <p className="text-xs text-slate-600 mt-2 font-normal leading-relaxed">{product.description}</p>
                          )}
                          {Object.keys(product.specs || {}).length > 0 && (
                            <div className="mt-2.5 flex flex-wrap gap-1.5">
                              {Object.entries(product.specs).map(([key, value]) => (
                                <span key={key} className="text-[11px] px-2.5 py-0.5 rounded-lg bg-white/70 border border-white/80 text-slate-700 shadow-xs">
                                  <span className="font-semibold text-slate-800">{key.replace(/_/g, " ")}:</span> {value}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteProduct(product)}
                          disabled={savingDelete === product.id}
                          className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-500/10 transition flex-shrink-0 disabled:opacity-40 active:scale-95"
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
            <div className="max-w-4xl mx-auto w-full space-y-4">
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
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-white/80 bg-white/70 backdrop-blur-md text-slate-700 text-xs font-semibold transition hover:bg-white hover:text-blue-700 shadow-xs active:scale-95"
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
    </div>
  );
}

export default ShopPage;
