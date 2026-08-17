import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Sparkles,
  Send,
  Mic,
  MicOff
} from "lucide-react";

import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MessageItem } from "./components/MessageItem";
import { CategoryCard } from "./components/CategoryCard";
import { VoiceModal } from "./components/VoiceModal";
import { AdminLockModal } from "./components/AdminLockModal";
import { TvIntroPortal } from "./components/TvIntroPortal";

const API_BASE = "http://127.0.0.1:8000";

const SAMPLE_CATEGORIES = [
  {
    icon: Sparkles,
    title: "Phone Prices & Specs",
    description: "Prices, specs and stock for all smartphones.",
    query: "What phones do you have and their prices?"
  },
  {
    icon: Sparkles,
    title: "Stock Check",
    description: "Is a product in stock right now? Ask about availability.",
    query: "What products are in stock right now?"
  },
  {
    icon: Sparkles,
    title: "Warranty & Policies",
    description: "Warranty, returns, delivery and repairs information.",
    query: "What is your return and warranty policy?"
  },
  {
    icon: Sparkles,
    title: "Buying Advice",
    description: "Get recommendations for any budget.",
    query: "Best phone under Rs. 25,000?"
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
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("chat_history");
    return saved ? JSON.parse(saved) : [];
  });

  const chatEndRef = useRef(null);
  const inlineRecogRef = useRef(null);

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

  const sendMessage = async (queryToSend) => {
    const query = (queryToSend || question).trim();
    if (!query || loading) return;

    if (inlineListening && inlineRecogRef.current) {
      try {
        inlineRecogRef.current.stop();
      } catch (e) { }
      setInlineListening(false);
    }

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setQuestion("");
    setVoiceStatus("");
    setLoading(true);

    setHistory((prev) => {
      const filtered = prev.filter((item) => item.title.toLowerCase() !== query.toLowerCase());
      return [
        { id: Date.now().toString(), title: query, time: "Just now" },
        ...filtered.slice(0, 15),
      ];
    });

    try {
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

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          similarity_score: data.similarity_score,
          relevant: data.relevant,
        },
      ]);
    } catch (error) {
      console.error("Failed to contact backend:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't reach the assistant service. Please ensure the backend is running.",
          similarity_score: 0.0,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleToggleInlineMic = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
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

    const recog = new SpeechRecognition();
    recog.continuous = false;
    recog.interimResults = true;
    recog.lang = "en-US";

    recog.onstart = () => {
      setInlineListening(true);
      setVoiceStatus("Listening to your voice... Speak now");
    };
    recog.onresult = (event) => {
      let currentText = "";
      for (let i = 0; i < event.results.length; i++) {
        currentText += event.results[i][0].transcript;
      }
      setQuestion(currentText);
    };
    recog.onerror = (event) => {
      console.warn("Inline speech recognition error:", event.error);
      setInlineListening(false);
      if (event.error !== "no-speech") {
        setVoiceStatus(`Microphone error: ${event.error}`);
      } else {
        setVoiceStatus("");
      }
    };
    recog.onend = () => {
      setInlineListening(false);
      setVoiceStatus("");
    };

    inlineRecogRef.current = recog;

    try {
      recog.start();
    } catch (e) {
      console.warn(e);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
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

        <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-6">
          <div className="max-w-4xl mx-auto w-full">

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

                {/* Expertise Filter Chips */}
                <div className="flex flex-wrap justify-center items-center gap-2.5 pt-1">
                  <span className="text-xs font-medium text-slate-500 mr-1">
                    Suggested topics:
                  </span>
                  {SAMPLE_CATEGORIES.map((cat, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendMessage(cat.query)}
                      className="px-3.5 py-1.5 rounded-full bg-white/60 hover:bg-white/90 backdrop-blur-md border border-white/80 text-slate-700 hover:text-blue-700 text-xs font-medium transition-all shadow-xs active:scale-95 cursor-pointer"
                    >
                      {cat.title}
                    </button>
                  ))}
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

        <footer className="p-4 sm:pb-6 flex-shrink-0">
          <div className="max-w-4xl mx-auto space-y-2">
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
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={inlineListening ? "Listening to your voice... Speak now" : "Ask about troubleshooting, specs, or product advice..."}
                rows={1}
                disabled={loading}
                className="flex-1 bg-transparent text-slate-900 placeholder-slate-400 text-sm outline-none resize-none py-2.5 px-2 max-h-24 disabled:opacity-50 font-normal"
              />

              <button
                onClick={() => sendMessage()}
                disabled={loading || !question.trim()}
                className="p-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md shadow-blue-500/25 disabled:opacity-30 disabled:cursor-not-allowed transition-all transform active:scale-95 flex-shrink-0"
                title="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>

            <p className="text-center text-[11px] text-slate-500">
              Grounded strictly on our catalog & verified support knowledge • Press Enter to send
            </p>
          </div>
        </footer>
      </div>

      <VoiceModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        onSendVoiceQuery={(transcript) => sendMessage(transcript)}
      />

      <AdminLockModal
        isOpen={showShopLock}
        onClose={() => setShowShopLock(false)}
        onUnlock={handleUnlock}
      />
    </div>
  );
}

export default App;
