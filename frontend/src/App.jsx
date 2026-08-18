import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Sparkles,
  Send,
  Mic,
  MicOff,
  PackageCheck,
  Wrench,
  ShieldCheck,
  Camera,
  X,
  Image as ImageIcon
} from "lucide-react";

import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MessageItem } from "./components/MessageItem";
import { CategoryCard } from "./components/CategoryCard";
import { VoiceModal } from "./components/VoiceModal";
import { AdminLockModal } from "./components/AdminLockModal";
import { TvIntroPortal } from "./components/TvIntroPortal";
import ReservationModal from "./components/ReservationModal";
import { generateServiceTokenPdf } from "./utils/pdfGenerator";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";




const SAMPLE_CATEGORIES = [
  {
    icon: PackageCheck,
    title: "Track or Cancel Order",
    description: "Check delivery status, request cancellation, or get replacement.",
    query:
      "Act as a dedicated TechStore Order Support Specialist. I need assistance with managing an existing order (such as checking delivery status, requesting an order cancellation, or processing a warranty replacement). Please introduce your role, greet me, and ask me to provide my Order Number so you can look up my order details and guide me through the secure 2FA authentication process."
  },

  {
    icon: Wrench,
    title: "Device Troubleshooting",
    description: "Diagnostic support for battery, overheating, screen, or connectivity.",
    query:
      "Act as a certified hardware & tech support diagnostic specialist. I am experiencing technical issues with my device (e.g., battery drain, overheating, WiFi/Bluetooth, slow charging, or display glitches). Before providing solutions, ask me 2-3 specific diagnostic questions (such as my device model/OS and when the issue occurs) to give me exact, step-by-step troubleshooting instructions."
  },
  {
    icon: Sparkles,
    title: "Smartphone & Laptop Advisor",
    description: "Find the best device based on budget, use case, and preferences.",
    query:
      "Act as an expert smartphone and laptop consultant. I want you to help me find the best device for my specific needs from the TechStore catalog, but do not give me recommendations yet. Instead, ask me the following questions one by one (or in small, logical groups) to gather my preferences:\n1. Budget: What is my maximum budget?\n2. Usage Cases: What will be the primary use (e.g., gaming, photography, work/productivity, daily use)?\n3. Brand & OS: Which brands (Apple, Samsung, Sony, etc.) or OS (iOS/Android/macOS/Windows) do I prefer?\nAfter I answer, analyze my responses and recommend the top 3 matching models from the store catalog with clear rationale."
  },
  {
    icon: ShieldCheck,
    title: "Warranty & Return Policy",
    description: "Check warranty duration, replacement eligibility, and return terms.",
    query:
      "Act as a TechStore Warranty & Customer Protection Advisor. I want to understand the warranty coverage, claim process, and return/replacement eligibility for devices at TechStore. Please provide a clear overview of the store's return window, warranty duration, and what qualifies for replacement, and ask me if I have a specific device or order I'd like you to check policies for."
  }
];



function App() {
  const navigate = useNavigate();
  const [introComplete, setIntroComplete] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);
  const [showShopLock, setShowShopLock] = useState(false);
  const [inlineListening, setInlineListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("");
  const [shopId, setShopId] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [reserveProduct, setReserveProduct] = useState(null);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("chat_history");
    return saved ? JSON.parse(saved) : [];
  });

  const chatEndRef = useRef(null);
  const inlineRecogRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const focusInput = () => {
      textareaRef.current?.focus();
    };
    focusInput();
    const timeout = setTimeout(focusInput, 300);
    return () => clearTimeout(timeout);
  }, [introComplete]);

  useEffect(() => {
    const loadShop = async () => {
      try {
        const res = await fetch(`${API_BASE}/shops`);
        if (!res.ok) return;
        const data = await res.json();
        const shops = data.shops || [];
        if (shops.length > 0) setShopId(shops[0].id);
      } catch (error) {
        console.error("Failed to load shop:", error);
      }
    };
    loadShop();
  }, []);

  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      if (inlineRecogRef.current) {
        try {
          inlineRecogRef.current.stop();
        } catch (e) { }
      }
    };
  }, []);

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setSelectedImage(reader.result);
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleClearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const sendMessage = async (queryToSend) => {
    const query = (queryToSend || question).trim();
    const attachedImage = selectedImage;
    const attachedPreview = imagePreview;

    if ((!query && !attachedImage) || loading) return;

    if (inlineListening && inlineRecogRef.current) {
      try {
        inlineRecogRef.current.stop();
      } catch (e) { }
      setInlineListening(false);
    }

    const userMessageContent = query || "Attached image for hardware defect diagnosis";
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessageContent,
        image_preview: attachedPreview,
      },
    ]);
    setQuestion("");
    handleClearImage();
    setVoiceStatus("");
    setLoading(true);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);

    setHistory((prev) => {
      const filtered = prev.filter((item) => item.title.toLowerCase() !== userMessageContent.toLowerCase());
      return [
        { id: Date.now().toString(), title: userMessageContent, time: "Just now" },
        ...filtered.slice(0, 15),
      ];
    });

    try {
      if (attachedImage) {
        // Use Vision AI Diagnostic Endpoint
        const res = await fetch(`${API_BASE}/diagnose-image`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            image_base64: attachedImage,
            question: query || "Diagnose the hardware defect shown in this image.",
          }),
        });

        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const diagData = await res.json();

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Here is the Vision AI Hardware Diagnostic Report for your device:",
            visual_diagnostic: diagData,
            image_preview: attachedPreview,
            suggested_followups: diagData.suggested_followups || [],
          },
        ]);
      } else {
        // Standard Chat / Streaming
        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: query,
            shop_id: shopId,
            history: messages
              .slice(-6)
              .map((m) => ({ role: m.role, content: m.content })),
          }),
        });

        if (!response.ok) throw new Error(`Server returned ${response.status}`);
        const data = await response.json();

        // Automatically trigger PDF Receipt Download on receiving authenticated Service Token
        if (data.action === "token_created" || data.token_id) {
          try {
            generateServiceTokenPdf(
              {
                token_id: data.token_id,
                order_id: data.order_id,
                customer_name: data.customer_name,
                phone: data.phone,
                model_name: data.model_name,
                request_type: data.request_type,
                price: data.price,
                purchase_date: data.purchase_date,
                token_status: data.token_status,
              },
              true
            );
          } catch (pdfErr) {
            console.error("Auto PDF generation error:", pdfErr);
          }
        }

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.answer,
            similarity_score: data.similarity_score,
            relevant: data.relevant,
            intent: data.intent,
            action: data.action,
            token_id: data.token_id,
            order_id: data.order_id,
            customer_name: data.customer_name,
            phone: data.phone || (data.intent === "human_assistance" ? "+91 9087086182" : null),
            model_name: data.model_name,
            request_type: data.request_type,
            price: data.price,
            purchase_date: data.purchase_date,
            token_status: data.token_status,
            video: data.video,
            video_hub: data.video_hub,
            comparison_data: data.comparison_data,
            product: data.product,
            reservation_available: data.reservation_available || data.product,
            suggested_followups: data.suggested_followups || [],
            email: data.email || (data.intent === "human_assistance" ? "support@techstore.com" : null),
            hours: data.hours,
            location: data.location,
            sources: data.sources || [],
          },
        ]);
      }

    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I'm having trouble connecting right now. Please verify backend is running on port 8000.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);
    }

  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleToggleInlineMic = () => {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      alert("Voice input is not supported in this browser. Please use Chrome.");
      return;
    }

    if (inlineListening) {
      if (inlineRecogRef.current) {
        try {
          inlineRecogRef.current.stop();
        } catch (e) { }
      }
      setInlineListening(false);
      setVoiceStatus("");
      return;
    }

    try {
      const recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setInlineListening(true);
        setVoiceStatus("Listening... speak your query");
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((res) => res[0].transcript)
          .join("");
        setQuestion(transcript);
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        setInlineListening(false);
        setVoiceStatus("");
      };

      recognition.onend = () => {
        setInlineListening(false);
        setVoiceStatus("");
      };

      inlineRecogRef.current = recognition;
      recognition.start();
    } catch (e) {
      console.warn(e);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem("chat_history");
  };

  const handleShopClick = () => {
    setShowShopLock(true);
  };

  const handleUnlock = async (pin) => {
    try {
      const res = await fetch(`${API_BASE}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      sessionStorage.setItem("admin_token", data.token || pin);
      sessionStorage.setItem("shop_unlocked", "1");
      navigate("/shop");
      return true;
    } catch (error) {
      console.error("Failed to verify password:", error);
      return false;
    }
  };


  return (
    <div className="relative flex h-screen w-screen overflow-hidden font-sans">

      {!introComplete && (
        <TvIntroPortal onComplete={() => setIntroComplete(true)} />
      )}

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        history={history}
        onSelectQuery={(q) => sendMessage(q)}
        onNewChat={handleNewChat}
        onClearHistory={handleClearHistory}
        onShopClick={handleShopClick}
      />

      <div className="flex-1 flex flex-col h-full relative z-10 overflow-hidden">

        <Header
          onMenuClick={() => setSidebarOpen(true)}
          onNewChat={handleNewChat}
          onVoiceClick={() => setVoiceModalOpen(true)}
        />

        <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-6 relative">
          {/* Ambient Scattered Background Chat Pops (Visible when no chat active) */}
          {messages.length === 0 && (
            <div className="absolute inset-0 pointer-events-none overflow-hidden z-0 hidden lg:block opacity-65 select-none">
              {/* Top Left Pop */}
              <div className="absolute top-8 left-[3%] max-w-[260px] animate-float-1">
                <div className="glass-panel rounded-2xl p-3.5 space-y-2 border border-white/60 shadow-lg shadow-blue-500/5">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                    <span className="text-[11px] font-semibold text-slate-700">Troubleshooting</span>
                  </div>
                  <div className="bg-white/90 rounded-xl rounded-tl-xs p-2.5 shadow-xs text-xs text-slate-800 font-medium">
                    How do I reset my device to factory settings?
                  </div>
                  <div className="bg-blue-50/80 rounded-xl rounded-tr-xs p-2 text-[11px] text-blue-900 border border-blue-100/50">
                    Hold Power + Vol Up for 10s to open Recovery Mode.
                  </div>
                </div>
              </div>

              {/* Top Right Pop */}
              <div className="absolute top-10 right-[3%] max-w-[260px] animate-float-2">
                <div className="glass-panel rounded-2xl p-3.5 space-y-2 border border-white/60 shadow-lg shadow-purple-500/5">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[11px] font-semibold text-slate-700">Product Advice</span>
                    <span className="w-2 h-2 rounded-full bg-purple-500" />
                  </div>
                  <div className="bg-white/90 rounded-xl rounded-tr-xs p-2.5 shadow-xs text-xs text-slate-800 font-medium">
                    Which laptop is best for coding & battery life?
                  </div>
                  <div className="bg-purple-50/80 rounded-xl rounded-tl-xs p-2 text-[11px] text-purple-900 border border-purple-100/50">
                    M3 MacBook Air or ThinkPad T14 with 18h battery.
                  </div>
                </div>
              </div>

              {/* Bottom Left Pop */}
              <div className="absolute bottom-20 left-[4%] max-w-[240px] animate-float-3">
                <div className="glass-panel rounded-2xl p-3.5 space-y-2 border border-white/60 shadow-lg shadow-indigo-500/5">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-500" />
                    <span className="text-[11px] font-semibold text-slate-700">Live Inventory</span>
                  </div>
                  <div className="bg-white/90 rounded-xl rounded-tl-xs p-2.5 shadow-xs text-xs text-slate-800 font-medium">
                    Are iPhone 16 Pro 256GB models in stock?
                  </div>
                  <div className="bg-indigo-50/80 rounded-xl rounded-tr-xs p-2 text-[11px] text-indigo-900 border border-indigo-100/50">
                    In Stock at Main Store • 4 units ready today.
                  </div>
                </div>
              </div>

              {/* Bottom Right Pop */}
              <div className="absolute bottom-24 right-[4%] max-w-[250px] animate-float-1">
                <div className="glass-panel rounded-2xl p-3.5 space-y-2 border border-white/60 shadow-lg shadow-emerald-500/5">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[11px] font-semibold text-slate-700">Warranty Support</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  </div>
                  <div className="bg-white/90 rounded-xl rounded-tr-xs p-2.5 shadow-xs text-xs text-slate-800 font-medium">
                    What is the return window for opened items?
                  </div>
                  <div className="bg-emerald-50/80 rounded-xl rounded-tl-xs p-2 text-[11px] text-emerald-900 border border-emerald-100/50">
                    14-day hassle-free replacement with store receipt.
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="max-w-4xl mx-auto w-full relative z-10">

            {messages.length === 0 && (
              <div className="py-8 space-y-8">
                {/* Hero Title and Badge */}
                <div className="text-center space-y-3.5">
                  <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/70 backdrop-blur-md border border-white/80 text-blue-700 text-xs font-semibold shadow-xs">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-spin" style={{ animationDuration: "3s" }} />
                    <span>Intelligent AI Support Concierge</span>
                  </div>
                  
                  <h2 className="font-heading text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight leading-tight max-w-2xl mx-auto">
                    Get Instant Technical Support &amp; Product Advice
                  </h2>
                  
                  <p className="text-sm sm:text-base text-slate-600 max-w-lg mx-auto leading-relaxed font-normal">
                    Expert troubleshooting, verified catalog specs, and personalized recommendations at your fingertips.
                  </p>
                </div>

                {/* 2x2 Feature Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  {SAMPLE_CATEGORIES.map((cat, index) => (
                    <CategoryCard
                      key={index}
                      icon={cat.icon}
                      title={cat.title}
                      description={cat.description}
                      query={cat.query}
                      onClick={(q) => sendMessage(q)}
                    />
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, index) => (
              <MessageItem
                key={index}
                message={msg}
                onSendMessage={(q) => sendMessage(q)}
                onReserve={(prod) => setReserveProduct(prod)}
                onRetry={
                  msg.role === "assistant" && index === messages.length - 1
                    ? () => {
                        const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
                        if (lastUserMsg) sendMessage(lastUserMsg.content);
                      }
                    : null
                }
              />
            ))}

            {loading && (
              <div className="flex items-start gap-3 my-4">
                <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20 ring-1 ring-white/60">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="glass-panel-deep rounded-2xl rounded-tl-sm px-5 py-4 space-y-2.5">
                  <div className="flex items-center gap-2 text-blue-700 text-xs font-semibold">
                    <div className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
                    <span>Searching catalog & generating response...</span>
                  </div>
                  <div className="h-1.5 w-52 rounded-full overflow-hidden bg-white/60">
                    <div className="w-full h-full typing-shimmer" />
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </main>

        <footer className="p-4 sm:pb-6 flex-shrink-0 relative z-20">
          <div className="max-w-4xl mx-auto space-y-2">
            {/* Attached Image Preview */}
            {imagePreview && (
              <div className="flex items-center gap-2 p-2 bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200 shadow-sm max-w-fit animate-in fade-in slide-in-from-bottom-2">
                <div className="w-10 h-10 rounded-lg overflow-hidden border border-slate-200">
                  <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
                </div>
                <div className="text-xs font-semibold text-slate-700">
                  Photo Attached for Vision Diagnosis
                </div>
                <button
                  onClick={handleClearImage}
                  className="w-6 h-6 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition cursor-pointer"
                  title="Remove image"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {voiceStatus && (
              <div className="flex items-center justify-center gap-2 py-1.5 px-4 rounded-full bg-white/80 backdrop-blur-md border border-white/90 text-blue-700 text-xs font-semibold max-w-fit mx-auto shadow-xs">
                <div className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
                <span>{voiceStatus}</span>
              </div>
            )}

            {/* Floating Glass Input Container */}
            <div className={`relative flex items-center gap-2 p-2 rounded-2xl glass-panel-deep transition-all duration-300 ${
              inlineListening ? "ring-2 ring-blue-500/50 border-blue-500" : ""
            }`}>
              {/* Photo Upload Attachment Button */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageChange}
                accept="image/*"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="p-3 rounded-xl text-slate-500 hover:text-blue-700 hover:bg-white/70 transition transform active:scale-95 flex-shrink-0 cursor-pointer"
                title="Attach device photo for hardware / error code diagnostic"
              >
                <Camera className="w-5 h-5" />
              </button>

              <button
                onClick={handleToggleInlineMic}
                className={`p-3 rounded-xl transition transform active:scale-95 flex-shrink-0 ${
                  inlineListening 
                    ? "bg-gradient-to-br from-blue-600 to-purple-600 text-white scale-105 shadow-md shadow-blue-500/25" 
                    : "text-slate-500 hover:text-blue-700 hover:bg-white/70"
                }`}
                title={inlineListening ? "Click to stop listening" : "Click to speak directly"}
              >
                {inlineListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>

              <textarea
                ref={textareaRef}
                autoFocus
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={inlineListening ? "Listening to your voice... Speak now" : (imagePreview ? "Describe the issue or click Send for Vision AI Diagnosis..." : "Ask about troubleshooting, specs, or product advice...")}
                rows={1}
                disabled={loading}
                className="flex-1 bg-transparent text-slate-900 placeholder-slate-400 text-sm outline-none resize-none py-2.5 px-2 max-h-24 disabled:opacity-50 font-normal"
              />

              <button
                onClick={() => sendMessage()}
                disabled={loading || (!question.trim() && !imagePreview)}
                className="p-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md shadow-blue-500/25 disabled:opacity-30 disabled:cursor-not-allowed transition-all transform active:scale-95 flex-shrink-0 cursor-pointer"
                title="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>

            <p className="text-center text-[11px] text-slate-500 max-w-2xl mx-auto leading-relaxed">
              Prices provided by the assistant may vary. Final price set by the store is definitive, and Tech Store Assistant is not responsible for sudden price hikes or fluctuations. • Press Enter to send
            </p>
          </div>
        </footer>
      </div>

      <VoiceModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        shopId={shopId}
        initialMessages={messages}
        onSyncConversation={(userQuery, data) => {
          setMessages((prev) => [
            ...prev,
            { role: "user", content: userQuery },
            {
              role: "assistant",
              content: data.answer,
              similarity_score: data.similarity_score,
              relevant: data.relevant,
              intent: data.intent,
              action: data.action,
              phone: data.phone || (data.intent === "human_assistance" ? "+91 9087086182" : null),
              email: data.email || (data.intent === "human_assistance" ? "support@techstore.com" : null),
              hours: data.hours,
              location: data.location,
              sources: data.sources || [],
            },
          ]);
          setHistory((prev) => {
            const filtered = prev.filter((item) => item.title.toLowerCase() !== userQuery.toLowerCase());
            return [
              { id: Date.now().toString(), title: userQuery, time: "Just now" },
              ...filtered.slice(0, 15),
            ];
          });
        }}
      />

      <AdminLockModal
        isOpen={showShopLock}
        onClose={() => setShowShopLock(false)}
        onUnlock={handleUnlock}
      />

      <ReservationModal
        product={reserveProduct}
        onClose={() => setReserveProduct(null)}
      />
    </div>
  );
}

export default App;

