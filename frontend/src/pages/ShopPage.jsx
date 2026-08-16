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
      <div className="flex h-screen w-screen items-center justify-center bg-[#f8fafc] text-slate-600 font-sans">
        <Loader2 className="w-5 h-5 animate-spin text-blue-900" /> &nbsp; Loading shop...
      </div>
    );
  }

  if (shopError) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#f8fafc] text-slate-600 font-sans">
        <div className="text-center space-y-3">
          <p className="text-sm text-rose-600">{shopError}</p>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 bg-white text-slate-600 text-xs font-medium transition hover:border-blue-900 hover:text-blue-900 mx-auto"
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
    <div className="relative flex h-screen w-screen bg-[#f8fafc] text-slate-800 overflow-hidden font-sans">

      <div className="flex-1 flex flex-col h-full relative z-10 overflow-hidden">

        <Header />

        {/* Shop banner */}
        <div className="border-b border-slate-200 bg-white px-4 sm:px-8 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-11 h-11 rounded-xl bg-blue-900 flex items-center justify-center flex-shrink-0">
                  <Store className="w-5 h-5 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="font-heading font-bold text-lg text-slate-900">
                      {shopName}
                    </h2>
                    {shop?.category && (
                      <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-900 border border-blue-100">
                        {shop.category}
                      </span>
                    )}
                  </div>
                  {shop?.description && (
                    <p className="text-xs text-slate-500 mt-1">{shop.description}</p>
                  )}
                  <div className="mt-1.5 flex items-center gap-3 flex-wrap text-xs text-slate-500">
                    {(shop?.address || shop?.city) && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {[shop.address, shop.city].filter(Boolean).join(", ")}
                      </span>
                    )}
                    {shop?.phone && (
                      <span className="flex items-center gap-1">
                        <Phone className="w-3 h-3" />
                        {shop.phone}
                      </span>
                    )}
                    {shop?.timings && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {shop.timings}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Package className="w-3 h-3" />
                      {products.length} product(s)
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => navigate("/")}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 bg-white text-slate-600 text-xs font-medium transition hover:border-blue-900 hover:text-blue-900 flex-shrink-0"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Back to Assistant
              </button>
            </div>

            {/* Tabs */}
            <div className="mt-4 flex gap-1.5">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition ${
                    activeTab === tab.key
                      ? "bg-blue-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
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
            <div className={`max-w-4xl mx-auto flex items-start gap-2.5 px-4 py-3 rounded-xl border text-sm ${
              status.type === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : status.type === "warn"
                ? "bg-amber-50 border-amber-200 text-amber-800"
                : "bg-rose-50 border-rose-200 text-rose-800"
            }`}>
              {status.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
              ) : status.type === "warn" ? (
                <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              )}
              <span>{status.message}</span>
            </div>
          </div>
        )}

        {/* ============ PRODUCTS TAB ============ */}
        {activeTab === "products" && (
          <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
            <div className="max-w-4xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <h3 className="font-heading text-base font-bold text-slate-900 flex items-center gap-2">
                  <Package className="w-4 h-4 text-blue-900" />
                  Catalog products ({filteredProducts.length})
                </h3>
                <div className="relative w-full sm:w-64">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={productFilter}
                    onChange={(e) => setProductFilter(e.target.value)}
                    placeholder="Search products..."
                    className="w-full pl-9 pr-3 py-2 text-xs rounded-lg bg-white border border-slate-300 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:ring-2 focus:ring-blue-100 transition"
                  />
                </div>
              </div>

              {filteredProducts.length === 0 ? (
                <div className="py-8 text-center">
                  <Package className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">
                    {products.length === 0
                      ? "No products yet. Upload a dataset in the 'Upload Dataset' tab."
                      : "No products match your search."}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredProducts.map((product) => (
                    <div key={product.id} className="rounded-xl border border-slate-200 bg-white p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-semibold text-slate-900 text-sm">{product.name}</span>
                            {product.brand && <span className="text-xs text-slate-500">{product.brand}</span>}
                            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-900 border border-blue-100">
                              {product.category}
                            </span>
                          </div>
                          <div className="mt-1.5 flex items-center gap-3 flex-wrap text-xs text-slate-600">
                            <span className="font-semibold text-slate-800">
                              Rs. {Number(product.price || 0).toLocaleString()}
                            </span>
                            <span className={`px-2 py-0.5 rounded-full ${
                              product.stock === "In stock"
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                : product.stock === "Low stock"
                                ? "bg-amber-50 text-amber-700 border border-amber-200"
                                : "bg-rose-50 text-rose-700 border border-rose-200"
                            }`}>
                              {product.stock}
                            </span>
                            <span>Warranty: {product.warranty_months || 0} months</span>
                          </div>
                          {product.description && (
                            <p className="text-xs text-slate-500 mt-1.5">{product.description}</p>
                          )}
                          {Object.keys(product.specs || {}).length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {Object.entries(product.specs).map(([key, value]) => (
                                <span key={key} className="text-[11px] px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200 text-slate-600">
                                  <span className="font-medium text-slate-700">{key.replace(/_/g, " ")}:</span> {value}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteProduct(product)}
                          disabled={savingDelete === product.id}
                          className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition flex-shrink-0 disabled:opacity-40"
                          title={`Delete ${product.name}`}
                        >
                          {savingDelete === product.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
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
              <section className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6">
                <h3 className="font-heading text-base font-bold text-slate-900 flex items-center gap-2">
                  <Upload className="w-4 h-4 text-blue-900" />
                  Upload product dataset
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Upload a <span className="font-medium">CSV</span> or{" "}
                  <span className="font-medium">JSON</span> file. Each row/item is one product.
                  Required columns: <span className="font-medium">name</span>. Optional: brand, category
                  (phone/laptop/accessory), price, stock, warranty_months, description - any extra
                  columns become specifications.
                </p>

                <div className="flex items-center gap-3 mt-4 flex-wrap">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.json"
                    disabled={uploading}
                    onChange={(e) => handleUpload(e.target.files[0])}
                    className="text-xs text-slate-600 file:mr-3 file:px-3 file:py-2 file:rounded-lg file:border file:border-slate-300 file:bg-white file:text-slate-700 file:text-xs file:font-medium hover:file:bg-slate-50 transition"
                  />
                  {uploading && (
                    <span className="flex items-center gap-2 text-xs text-blue-900">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Uploading & re-indexing...
                    </span>
                  )}
                </div>

                <button
                  onClick={downloadTemplate}
                  className="mt-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 text-xs font-medium transition hover:border-blue-900 hover:text-blue-900"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  Download CSV template
                </button>
              </section>

              <div className="pb-4 text-center">
                <p className="text-[11px] text-slate-400">
                  After upload, the assistant answers about these products instantly - no restart, no LLM cost for indexing.
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
