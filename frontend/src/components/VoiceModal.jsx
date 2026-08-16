import React, { useState, useEffect, useRef } from "react";
import { Mic, X, RotateCw, Sparkles, Send, Volume2 } from "lucide-react";
import { GlowingOrb } from "./GlowingOrb";

export function VoiceModal({ isOpen, onClose, onSendVoiceQuery }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [statusMessage, setStatusMessage] = useState("Listening... Speak now");
  const [countdown, setCountdown] = useState(null);

  const transcriptRef = useRef("");
  const recognitionRef = useRef(null);
  const countdownTimerRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current);
      }
      setIsListening(false);
      setTranscript("");
      transcriptRef.current = "";
      setCountdown(null);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatusMessage("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    const recog = new SpeechRecognition();
    recog.continuous = false;
    recog.interimResults = true;
    recog.lang = "en-US";

    recog.onstart = () => {
      setIsListening(true);
      setStatusMessage("Listening to your voice...");
    };

    recog.onresult = (event) => {
      let currentTranscript = "";
      for (let i = 0; i < event.results.length; i++) {
        currentTranscript += event.results[i][0].transcript;
      }
      const trimmed = currentTranscript.trim();
      setTranscript(trimmed);
      transcriptRef.current = trimmed;
    };

    recog.onerror = (event) => {
      console.warn("Speech recognition warning/error:", event.error);
      if (event.error !== "no-speech") {
        setStatusMessage(`Microphone: ${event.error}. Click mic to retry.`);
      } else {
        setStatusMessage("No speech detected. Tap microphone to speak.");
      }
      setIsListening(false);
    };

    recog.onend = () => {
      setIsListening(false);
      const finalQuery = transcriptRef.current.trim();
      if (finalQuery) {
        setStatusMessage("Speech recognized!");
        // Trigger countdown before auto-sending
        let count = 1;
        setCountdown(count);
        countdownTimerRef.current = setInterval(() => {
          count -= 1;
          if (count <= 0) {
            clearInterval(countdownTimerRef.current);
            onSendVoiceQuery(transcriptRef.current.trim());
            onClose();
          } else {
            setCountdown(count);
          }
        }, 1000);
      } else {
        setStatusMessage("Tap the microphone to speak again.");
      }
    };

    recognitionRef.current = recog;

    try {
      recog.start();
    } catch (e) {
      console.warn("Auto-start error:", e);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current);
      }
    };
  }, [isOpen]);

  const handleToggleListening = () => {
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current);
      setCountdown(null);
    }

    if (!recognitionRef.current) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = "en-US";
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
    } else {
      setTranscript("");
      transcriptRef.current = "";
      setStatusMessage("Listening...");
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.warn(e);
      }
    }
  };

  const handleSendNow = () => {
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current);
    }
    const query = (transcriptRef.current || transcript).trim();
    if (query) {
      onSendVoiceQuery(query);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm">
      <div className="relative w-full max-w-md h-[560px] bg-white rounded-3xl p-7 flex flex-col justify-between items-center text-center shadow-2xl border border-slate-200 overflow-hidden">
        
        {/* Top Header */}
        <div className="w-full flex items-center justify-between text-slate-500">
          <button 
            onClick={onClose}
            className="p-2.5 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition"
            title="Close voice mode"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-900 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
            <Sparkles className="w-3.5 h-3.5 text-blue-800" />
            <span>TechStore Voice Assistant</span>
          </div>

          <button 
            onClick={() => {
              if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
              setCountdown(null);
              setTranscript("");
              transcriptRef.current = "";
              setStatusMessage("Cleared. Tap mic to speak.");
            }}
            className="p-2.5 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition"
            title="Reset"
          >
            <RotateCw className="w-5 h-5" />
          </button>
        </div>

        {/* Center Voice Orb Visualizer */}
        <div className="my-auto flex flex-col items-center w-full">
          <GlowingOrb isListening={isListening} isThinking={false} size="lg" />

          {/* Transcript / Instructions Display */}
          <div className="mt-8 px-4 w-full">
            {transcript ? (
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                <p className="text-slate-900 text-base font-semibold leading-relaxed">
                  "{transcript}"
                </p>
                {countdown !== null && (
                  <p className="text-xs text-blue-800 mt-2 font-medium">
                    Sending to Assistant...
                  </p>
                )}
              </div>
            ) : (
              <p className="text-slate-500 text-sm font-medium">
                {statusMessage}
              </p>
            )}
          </div>
        </div>

        {/* Bottom Voice Controls */}
        <div className="w-full flex items-center justify-center gap-4 pt-2">
          {/* Main Mic Button */}
          <button
            onClick={handleToggleListening}
            className={`relative p-5 rounded-full transition-all duration-300 transform active:scale-95 shadow-lg ${
              isListening 
                ? "bg-rose-600 text-white scale-110" 
                : "bg-blue-900 text-white hover:scale-105 hover:bg-blue-800"
            }`}
            title={isListening ? "Stop listening" : "Start speaking"}
          >
            <Mic className="w-7 h-7" />
          </button>

          {/* Send Now Button */}
          {transcript.trim() && (
            <button
              onClick={handleSendNow}
              className="flex items-center gap-1.5 px-5 py-3.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white font-semibold text-xs transition transform active:scale-95"
            >
              <span>Ask AI</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
