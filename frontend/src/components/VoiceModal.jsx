import React, { useState, useEffect, useRef } from "react";
import { 
  Mic, 
  MicOff, 
  X, 
  Sparkles, 
  Volume2, 
  VolumeX, 
  Pause,
  Play,
  RotateCcw,
  MessageSquare, 
  ArrowRight,
  Radio,
  Share2,
  Tv
} from "lucide-react";
import { GlowingOrb } from "./GlowingOrb";

const API_BASE = "http://127.0.0.1:8000";

const QUICK_SUGGESTIONS = [
  "Hi, can you hear me?",
  "What are the latest Galaxy phones?",
  "Where is your store located?",
  "Tell me about laptop exchange offers"
];

// Clean text for natural, human-like voice playback
function cleanSpeechText(text) {
  if (!text) return "";
  return text
    .replace(/[*_#`~>]/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/Rs\.\s?(\d+)/gi, "Rupees $1")
    .replace(/\|\s*([^|\n]+)\s*\|/g, "$1. ")
    .replace(/---/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function VoiceModal({ isOpen, onClose, shopId, onSyncConversation, initialMessages = [] }) {
  // States: 'idle' | 'listening' | 'thinking' | 'speaking'
  const [voiceState, setVoiceState] = useState("listening");
  const [userTranscript, setUserTranscript] = useState("");
  const [agentTranscript, setAgentTranscript] = useState("");
  const [displayedWords, setDisplayedWords] = useState("");
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [viewMode, setViewMode] = useState("live"); // 'live' | 'orb' | 'history'
  const [sessionLog, setSessionLog] = useState([]);
  const [statusSubtitle, setStatusSubtitle] = useState("Listening to your voice... Speak anytime");

  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const userTranscriptRef = useRef("");
  const voiceStateRef = useRef("listening");
  const soundEnabledRef = useRef(true);
  const wordIntervalRef = useRef(null);
  const isStartingRef = useRef(false);

  useEffect(() => {
    voiceStateRef.current = voiceState;
  }, [voiceState]);

  useEffect(() => {
    soundEnabledRef.current = soundEnabled;
  }, [soundEnabled]);

  // Clean shutdown
  const stopAll = () => {
    if (window.speechSynthesis) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onresult = null;
        recognitionRef.current.stop();
      } catch (e) {}
      recognitionRef.current = null;
    }
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    if (wordIntervalRef.current) clearInterval(wordIntervalRef.current);
    isStartingRef.current = false;
  };

  // Find natural speech synthesis voice
  const getBestVoice = () => {
    if (!window.speechSynthesis) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    const preferred = voices.find(v => 
      (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha") || v.name.includes("Jenny")) && 
      v.lang.startsWith("en")
    );
    if (preferred) return preferred;

    const anyEn = voices.find(v => v.lang.startsWith("en"));
    return anyEn || voices[0];
  };

  // Start / Resume Continuous Speech Recognition (Robust Lifecycle)
  const startListening = () => {
    stopAll();

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatusSubtitle("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      setVoiceState("idle");
      return;
    }

    try {
      const recog = new SpeechRecognition();
      recog.continuous = true;
      recog.interimResults = true;
      recog.lang = "en-US";

      recog.onstart = () => {
        isStartingRef.current = false;
        setVoiceState("listening");
        setStatusSubtitle("Listening... Speak your question");
      };

      recog.onresult = (event) => {
        let currentInterim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentInterim += event.results[i][0].transcript;
        }
        const text = currentInterim.trim();
        if (text) {
          setUserTranscript(text);
          userTranscriptRef.current = text;

          // Auto-silence detect: send query after 1.3s of pause
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = setTimeout(() => {
            if (userTranscriptRef.current.trim() && voiceStateRef.current === "listening") {
              handleSendQuery(userTranscriptRef.current.trim());
            }
          }, 1300);
        }
      };

      recog.onerror = (event) => {
        isStartingRef.current = false;
        if (event.error !== "no-speech" && event.error !== "aborted") {
          console.warn("Speech recognition error:", event.error);
        }
      };

      recog.onend = () => {
        isStartingRef.current = false;
        // Keep continuous listener alive if we are in listening mode
        if (voiceStateRef.current === "listening") {
          try {
            recog.start();
          } catch (e) {}
        }
      };

      recognitionRef.current = recog;
      isStartingRef.current = true;
      recog.start();
    } catch (e) {
      isStartingRef.current = false;
      console.warn("Speech recognition start error:", e);
    }
  };

  // Send Query to Backend & Handle Gemini Response
  const handleSendQuery = async (queryText) => {
    if (!queryText || !queryText.trim()) return;
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

    // Stop recognition while generating and speaking
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.stop();
      } catch (e) {}
    }

    const currentQuery = queryText.trim();
    setUserTranscript(currentQuery);
    setVoiceState("thinking");
    setStatusSubtitle("Finding answers & preparing voice...");

    // Record into session history
    setSessionLog((prev) => [
      ...prev,
      { role: "user", text: currentQuery, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
    ]);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: currentQuery,
          shop_id: shopId || "S001",
          history: [
            ...initialMessages.slice(-4).map(m => ({ role: m.role, content: m.content })),
            ...sessionLog.slice(-4).map(m => ({ role: m.role === "user" ? "user" : "assistant", content: m.text }))
          ]
        }),
      });

      if (!response.ok) throw new Error(`Server returned ${response.status}`);
      const data = await response.json();
      const answer = data.answer || "I found some details for you.";

      // Sync to main chat
      if (onSyncConversation) {
        onSyncConversation(currentQuery, data);
      }

      setSessionLog((prev) => [
        ...prev,
        { role: "assistant", text: answer, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
      ]);
      speakAgentResponse(answer);

    } catch (err) {
      console.error("Voice chat error:", err);
      const fallback = "I'm having trouble connecting right now. Please try asking again.";
      setSessionLog((prev) => [
        ...prev,
        { role: "assistant", text: fallback, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
      ]);
      speakAgentResponse(fallback);
    }
  };

  // Speak agent response & Stream Live Transcripts
  const speakAgentResponse = (rawAnswer) => {
    setAgentTranscript(rawAnswer);
    setVoiceState("speaking");
    setStatusSubtitle("Assistant is speaking...");
    userTranscriptRef.current = "";

    const cleanText = cleanSpeechText(rawAnswer);

    // Stream word-by-word closed caption transcript
    const words = cleanText.split(" ");
    let currentIdx = 0;
    setDisplayedWords("");
    if (wordIntervalRef.current) clearInterval(wordIntervalRef.current);

    const speed = Math.max(65, Math.min(170, (cleanText.length * 35) / Math.max(1, words.length)));
    wordIntervalRef.current = setInterval(() => {
      if (currentIdx < words.length) {
        setDisplayedWords(words.slice(0, currentIdx + 1).join(" "));
        currentIdx += 1;
      } else {
        clearInterval(wordIntervalRef.current);
      }
    }, speed);

    // Speech Synthesis TTS
    if (window.speechSynthesis && soundEnabledRef.current) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.voice = getBestVoice();
      utterance.rate = 1.02;
      utterance.pitch = 1.0;

      utterance.onend = () => {
        if (wordIntervalRef.current) clearInterval(wordIntervalRef.current);
        setDisplayedWords(cleanText);
        setVoiceState("listening");
        setStatusSubtitle("Listening... Speak your next question");
        // Automatically loop back to listening for continuous conversation
        startListening();
      };

      utterance.onerror = (e) => {
        console.warn("TTS Error:", e);
        setVoiceState("listening");
        setStatusSubtitle("Listening... Speak your next question");
        startListening();
      };

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    } else {
      // If sound is muted, display text for readable duration then resume listening
      const readDuration = Math.max(2500, cleanText.length * 40);
      setTimeout(() => {
        setVoiceState("listening");
        setStatusSubtitle("Listening... Speak your next question");
        startListening();
      }, readDuration);
    }
  };

  // Interrupt Current Speech
  const handleInterrupt = () => {
    stopAll();
    setVoiceState("listening");
    setStatusSubtitle("Interrupted. Listening for your question...");
    startListening();
  };

  // Toggle Mute Audio
  const handleToggleSound = () => {
    const nextSound = !soundEnabled;
    setSoundEnabled(nextSound);
    if (!nextSound && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  };

  // Pause / Resume Mic (Issue 1 fix: cleanly unbinds & re-initializes on toggle)
  const handleToggleMic = () => {
    if (voiceState === "speaking") {
      handleInterrupt();
      return;
    }

    if (voiceState === "listening") {
      stopAll();
      setVoiceState("idle");
      setStatusSubtitle("Microphone paused. Tap to resume talking.");
    } else {
      setUserTranscript("");
      userTranscriptRef.current = "";
      startListening();
    }
  };

  // Reset Session
  const handleResetSession = () => {
    stopAll();
    setUserTranscript("");
    setAgentTranscript("");
    setDisplayedWords("");
    setSessionLog([]);
    startListening();
  };

  // Mount / Unmount lifecycle
  useEffect(() => {
    if (isOpen) {
      setUserTranscript("");
      setAgentTranscript("");
      setDisplayedWords("");
      startListening();
    } else {
      stopAll();
    }
    return () => {
      stopAll();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/40 backdrop-blur-xl animate-fade-in">
      <div className="relative w-full max-w-lg min-h-[600px] max-h-[92vh] bg-white/85 backdrop-blur-3xl rounded-[36px] p-6 sm:p-7 flex flex-col justify-between items-center text-center shadow-2xl shadow-blue-500/15 border border-white/90 overflow-hidden ring-1 ring-white/70">
        
        {/* Soft Ambient Palette Lighting in Corners */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-gradient-to-br from-blue-400/20 via-indigo-400/20 to-purple-400/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-gradient-to-tr from-purple-400/20 via-pink-400/20 to-blue-400/20 rounded-full blur-3xl pointer-events-none" />

        {/* ============ TOP HEADER (GEMINI LIVE STYLE) ============ */}
        <div className="w-full flex items-center justify-between z-20">
          {/* Close button */}
          <button 
            onClick={onClose}
            className="p-2.5 rounded-2xl text-slate-500 hover:text-slate-900 bg-white/70 hover:bg-white border border-white/80 shadow-xs transition active:scale-95 cursor-pointer"
            title="Exit Voice Mode"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Gemini Voice Mode Pill */}
          <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/90 backdrop-blur-md border border-white shadow-xs text-xs font-semibold text-slate-800">
            <Radio className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent font-bold">
              Gemini Voice Live
            </span>
            <span className={`w-2 h-2 rounded-full transition-all duration-300 ${
              voiceState === "listening" 
                ? "bg-emerald-500 animate-ping" 
                : voiceState === "speaking" 
                ? "bg-blue-600 animate-pulse" 
                : voiceState === "thinking" 
                ? "bg-purple-500 animate-bounce" 
                : "bg-slate-400"
            }`} />
          </div>

          {/* Top Actions: Audio Mute & Reset */}
          <div className="flex items-center gap-1.5">
            <button
              onClick={handleToggleSound}
              className={`p-2.5 rounded-2xl border border-white/80 shadow-xs transition active:scale-95 cursor-pointer ${
                soundEnabled ? "bg-white/70 text-blue-600 hover:bg-white" : "bg-rose-50 text-rose-600 border-rose-200"
              }`}
              title={soundEnabled ? "Mute Voice Speech" : "Unmute Voice Speech"}
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </button>

            <button 
              onClick={handleResetSession}
              className="p-2.5 rounded-2xl text-slate-500 hover:text-slate-900 bg-white/70 hover:bg-white border border-white/80 shadow-xs transition active:scale-95 cursor-pointer"
              title="Reset Conversation"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* ============ CENTER STAGE: LIVE TRANSCRIPT & AURORA (IMAGES 2 & 3 INSPIRATION) ============ */}
        <div className="my-auto py-2 flex flex-col items-center w-full z-10 flex-1 justify-center max-h-[400px]">
          
          {/* VIEW MODE: LIVE TRANSCRIPT (IMAGE 3 REPLICATION) */}
          {viewMode === "live" && (
            <div className="w-full flex flex-col items-center justify-between h-full space-y-4 max-w-md">
              
              {/* User Speech Bubble Pill (Top right/center) */}
              {userTranscript ? (
                <div className="self-end max-w-[85%] px-4 py-2.5 rounded-3xl rounded-tr-md bg-slate-900/90 backdrop-blur-md text-white shadow-md text-left animate-fade-in">
                  <p className="text-xs sm:text-sm font-medium leading-relaxed">
                    {userTranscript}
                  </p>
                </div>
              ) : (
                <div className="py-2">
                  <span className="text-xs text-slate-400 font-medium">
                    {statusSubtitle}
                  </span>
                </div>
              )}

              {/* Agent Live Streaming Transcript (Large Typography below user speech) */}
              <div className="w-full flex-1 flex items-center justify-center px-2 min-h-[140px]">
                {voiceState === "speaking" ? (
                  <div className="w-full text-left space-y-2 animate-fade-in">
                    <p className="text-slate-900 text-lg sm:text-2xl font-bold font-heading leading-snug tracking-tight">
                      {displayedWords || agentTranscript}
                    </p>
                  </div>
                ) : voiceState === "thinking" ? (
                  <div className="flex flex-col items-center gap-2.5 animate-pulse">
                    <div className="w-8 h-8 rounded-full border-3 border-blue-600/30 border-t-blue-600 animate-spin" />
                    <span className="text-xs font-semibold text-blue-700">Thinking &amp; composing response...</span>
                  </div>
                ) : userTranscript ? (
                  <div className="text-center py-4">
                    <p className="text-xs text-slate-400 font-medium">Processing your question...</p>
                  </div>
                ) : (
                  /* Initial Suggestion Chips */
                  <div className="space-y-3 w-full">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Tap or speak a question
                    </p>
                    <div className="flex flex-wrap items-center justify-center gap-1.5">
                      {QUICK_SUGGESTIONS.map((chip, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendQuery(chip)}
                          className="text-[11px] px-3.5 py-1.5 rounded-full bg-white/70 hover:bg-white border border-white/80 text-slate-700 hover:text-blue-700 shadow-2xs transition active:scale-95 cursor-pointer flex items-center gap-1 group"
                        >
                          <span>{chip}</span>
                          <ArrowRight className="w-2.5 h-2.5 opacity-40 group-hover:opacity-100 transition" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Tap to Interrupt Floating Pill (When Agent is Speaking) */}
              {voiceState === "speaking" && (
                <button
                  onClick={handleInterrupt}
                  className="px-4 py-1.5 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white text-[11px] font-semibold shadow-md backdrop-blur-md transition active:scale-95 cursor-pointer animate-fade-in flex items-center gap-1.5"
                >
                  <span>Tap to interrupt</span>
                </button>
              )}
            </div>
          )}

          {/* VIEW MODE: ORB VIEW */}
          {viewMode === "orb" && (
            <div className="my-auto py-4 cursor-pointer" onClick={handleToggleMic} title="Tap to pause / resume">
              <GlowingOrb 
                isListening={voiceState === "listening"} 
                isSpeaking={voiceState === "speaking"} 
                isThinking={voiceState === "thinking"} 
                size="lg" 
              />
              <p className="text-xs text-slate-500 font-medium mt-6">
                {statusSubtitle}
              </p>
            </div>
          )}

          {/* VIEW MODE: FULL HISTORY LOG */}
          {viewMode === "history" && (
            <div className="w-full text-left p-3.5 rounded-2xl bg-white/60 backdrop-blur-md border border-white/80 max-h-[260px] overflow-y-auto space-y-2.5">
              {sessionLog.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-6">No voice conversation history yet.</p>
              ) : (
                sessionLog.map((item, idx) => (
                  <div key={idx} className={`p-3 rounded-2xl text-xs ${item.role === "user" ? "bg-slate-900 text-white ml-6" : "bg-white/90 text-slate-900 mr-6 border border-white/90 shadow-2xs"}`}>
                    <span className="font-bold text-[10px] uppercase tracking-wider block opacity-70 mb-1">
                      {item.role === "user" ? "You" : "Assistant"}
                    </span>
                    <p className="leading-relaxed font-medium">{item.text}</p>
                  </div>
                ))
              )}
            </div>
          )}

        </div>

        {/* ============ BOTTOM SECTION: FLUID AURORA ENERGY WAVE & CONTROLS ============ */}
        <div className="w-full flex flex-col items-center gap-4 pt-2 z-20">
          
          {/* Fluid Aurora Energy Wave (Styled in Project's Signature Palette) */}
          <div className="relative w-44 sm:w-56 h-12 flex items-center justify-center overflow-hidden rounded-full p-1">
            {/* Outer Glow Halo */}
            <div className={`absolute inset-0 rounded-full blur-lg transition-all duration-500 ${
              voiceState === "speaking"
                ? "bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 opacity-90 scale-110 animate-pulse"
                : voiceState === "listening"
                ? "bg-gradient-to-r from-blue-500 via-indigo-500 to-pink-500 opacity-75 animate-pulse"
                : voiceState === "thinking"
                ? "bg-gradient-to-r from-purple-500 to-indigo-500 opacity-70 animate-bounce"
                : "bg-slate-300/50 opacity-40"
            }`} />

            {/* Inner Fluid Aurora Wave Core */}
            <div className={`relative w-full h-full rounded-full flex items-center justify-center px-4 overflow-hidden border border-white/60 shadow-inner ${
              voiceState === "speaking"
                ? "bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600"
                : voiceState === "listening"
                ? "bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600"
                : voiceState === "thinking"
                ? "bg-gradient-to-r from-purple-600 to-indigo-600"
                : "bg-slate-200/80"
            }`}>
              {/* Dynamic Soundwave Equalizer Bars inside the Aurora Pill */}
              {voiceState === "speaking" ? (
                <div className="flex items-center gap-1.5">
                  <span className="w-1 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "14px", animationDuration: "0.4s" }} />
                  <span className="w-1 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "24px", animationDuration: "0.5s", animationDelay: "0.1s" }} />
                  <span className="w-1 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "28px", animationDuration: "0.45s", animationDelay: "0.2s" }} />
                  <span className="w-1 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "20px", animationDuration: "0.55s", animationDelay: "0.15s" }} />
                  <span className="w-1 bg-white rounded-full animate-bounce shadow-xs" style={{ height: "12px", animationDuration: "0.4s", animationDelay: "0.25s" }} />
                </div>
              ) : voiceState === "listening" ? (
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-white rounded-full animate-ping" />
                  <span className="w-1.5 h-1.5 bg-white rounded-full animate-ping" style={{ animationDelay: "0.2s" }} />
                  <span className="w-1.5 h-1.5 bg-white rounded-full animate-ping" style={{ animationDelay: "0.4s" }} />
                </div>
              ) : voiceState === "thinking" ? (
                <span className="text-[10px] font-bold text-white tracking-widest uppercase animate-pulse">Thinking</span>
              ) : (
                <span className="text-[10px] font-bold text-slate-500 tracking-wider uppercase">Paused</span>
              )}
            </div>
          </div>

          {/* Gemini Live Control Bar (Images 2 & 3 Replication) */}
          <div className="flex items-center justify-center gap-4 sm:gap-6 pt-1">
            
            {/* View Switcher Toggle */}
            <button
              onClick={() => {
                if (viewMode === "live") setViewMode("orb");
                else if (viewMode === "orb") setViewMode("history");
                else setViewMode("live");
              }}
              className="p-3.5 rounded-full bg-white/80 hover:bg-white text-slate-700 border border-white/90 shadow-md transition active:scale-95 cursor-pointer"
              title={`Current: ${viewMode} view. Click to toggle`}
            >
              <MessageSquare className="w-5 h-5" />
            </button>

            {/* Center Pause / Mic Action Button */}
            <button
              onClick={handleToggleMic}
              className={`p-4 rounded-full transition-all duration-300 transform active:scale-95 shadow-xl cursor-pointer ${
                voiceState === "listening" || voiceState === "speaking"
                  ? "bg-slate-900 hover:bg-slate-800 text-white shadow-slate-900/25 scale-105"
                  : "bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-blue-500/30 hover:scale-105"
              }`}
              title={
                voiceState === "speaking"
                  ? "Tap to pause speech"
                  : voiceState === "listening"
                  ? "Tap to pause microphone"
                  : "Tap to resume talking"
              }
            >
              {voiceState === "listening" || voiceState === "speaking" ? (
                <Pause className="w-6 h-6 fill-white" />
              ) : (
                <Mic className="w-6 h-6" />
              )}
            </button>

            {/* End Call / Close Button (Vibrant Red Accent Circle matching Image 2 & 3) */}
            <button
              onClick={onClose}
              className="p-3.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white shadow-lg shadow-rose-600/30 transition-all transform active:scale-95 hover:scale-105 cursor-pointer"
              title="End Voice Session"
            >
              <X className="w-5 h-5 stroke-[2.5]" />
            </button>
          </div>

          <p className="text-[10px] text-slate-400 font-medium pb-1">
            {voiceState === "speaking"
              ? "Tap the pause button or speak to interrupt"
              : voiceState === "listening"
              ? "Listening to your voice • Auto-sends when you pause"
              : "Microphone paused • Tap center button to talk"}
          </p>
        </div>

      </div>
    </div>
  );
}
