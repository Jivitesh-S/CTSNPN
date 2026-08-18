# Intelligent Product Support Assistant (TechStore AI)

An intelligent, grounded conversational assistant designed to help customers obtain accurate, reliable, and understandable answers about electronic products and appliances. The assistant leverages authorized product knowledge (such as user manuals, specification sheets, FAQs, and troubleshooting guides) to provide instant customer support without hallucinating facts.

---

## 📌 Overview

Finding and interpreting product information across lengthy manuals (50+ pages), dense warranty policies, and fragmented FAQ pages is slow and frustrating. Traditional keyword searches frequently fail because they do not understand user intent or natural phrasing (e.g. searching *"water leaking"* misses *"OE drainage error code"*).

The **Intelligent Product Support Assistant** solves this by combining semantic retrieval (RAG) and conversational AI to provide direct, well-grounded answers.

### How It Solves The Problem
- **Semantic Retrieval:** Understands the *meaning* behind a user's question, ensuring relevant information is found even when phrased in colloquial terms.
- **Direct Answers, Not Just Links:** Synthesizes retrieved documentation chunks into a concise, easy-to-understand response with step-by-step guidance.
- **Strict Grounding (No Hallucination):** Factual claims are exclusively supported by retrieved authorized context. The assistant never invents prices, specifications, or policies.
- **Safe Fallback for Unsupported Queries:** When information is unavailable in the approved knowledge base, the assistant clearly states the limitation rather than fabricating plausible answers.
- **Dynamic Knowledge Ingestion:** Administrators can seamlessly upload and update product catalogs and support datasets (JSON/CSV), keeping pricing, stock, and specs current with zero server downtime.

---

## 🚀 Key Features

1. **Conversational Product Support:** Answers questions about features, specifications, pricing, setup, maintenance, and troubleshooting across the entire catalog.
2. **Vision AI Hardware Diagnostics (`VisualDiagnosticCard`):** Allows users to upload photos of hardware issues, damaged parts, or error lights, returning a verified fault analysis with severity ratings (*Low, Medium, High, Critical*).
3. **Voice Concierge (`VoiceModal`):** Live speech-to-text input and natural audio response synthesis for a hands-free customer experience.
4. **Side-by-Side Product Comparison:** Compares specifications, performance, and pricing across devices in structured comparison tables.
5. **Interactive Video Hub:** Delivers embedded video tutorials and setup guides directly in the chat stream for complex troubleshooting procedures.
6. **In-Store Reservation & Digital QR Passes:** Enables customers to place a 48-hour hold on products for in-store pickup with instant QR hold passes.
7. **Automated Telegram Store Alerts:** Sends instant real-time notifications to store staff via Telegram Bot upon reservation with masked customer PII for privacy.
8. **PIN-Protected Admin Portal:** Secure admin dashboard for uploading product datasets, modifying catalog specs, and managing live inventory.

---

## 🏗️ Architecture & Technology Stack

```text
┌─────────────────────────────────────────────────────────────┐
│                    React + Vite Frontend                    │
│   (Tailwind CSS, Glassmorphism, Voice Modal, Vision AI UI)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / Multipart)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Engine                   │
│   (Security Headers, Rate Limiting, Async REST Endpoints)   │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼───────────────┐ ┌────────────▼───────────────┐
│     Hybrid RAG Pipeline      │ │       Data Persistence     │
│ • ChromaDB (Dense Vectors)   │ │ • Product Catalog Database │
│ • BM25Okapi (Sparse Lexical) │ │ • Reservation Store        │
│ • Reciprocal Rank Fusion     │ │ • Telegram Notification    │
│ • Cross-Encoder Re-Ranker    │ │   Service                  │
│ • Groq / Gemini LLM Engine   │ └────────────────────────────┘
└──────────────────────────────┘
```

- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons.
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic.
- **Vector Database:** ChromaDB with `BAAI/bge-small-en-v1.5` embeddings.
- **Lexical Search:** BM25Okapi for exact model number and keyword matching.
- **Re-Ranking:** `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **LLM Inference:** Groq API (`openai/gpt-oss-20b` / LLaMA 3.3) & Google Gemini.
- **Notifications:** Telegram Bot API.

---

## 📁 Project Structure

```text
.
├── backend/
│   ├── main.py              # FastAPI application, routing, middleware & endpoints
│   ├── rag_service.py       # Hybrid RAG pipeline, ChromaDB retrieval & LLM generation
│   ├── db.py                # Catalog database and reservation persistence
│   ├── ingest.py            # Knowledge chunking, embedding and indexing logic
│   ├── telegram_service.py  # Telegram alert bot & OTP verification service
│   └── video_catalog.py     # Curated video tutorials and setup guides
├── frontend/
│   ├── src/
│   │   ├── components/      # VoiceModal, VisualDiagnosticCard, ComparisonCard, etc.
│   │   ├── pages/           # Main interactive assistant interface
│   │   ├── App.jsx          # Application root with theme and session state
│   │   └── index.css        # Tailwind design system and glassmorphic styles
│   └── vite.config.js       # Vite configuration and proxy rules
├── data/                    # Approved manuals, FAQs, catalog.json & support datasets
├── scripts/                 # Standalone indexing, evaluation and PDF generation scripts
├── test_qa.py               # Question-answering accuracy test suite
├── test_retrieval.py        # Vector retrieval benchmark and similarity scoring
└── requirements.txt         # Python backend dependencies
```

---

## ⚙️ Installation & Getting Started

### 1. Backend Setup
```bash
# Navigate to project directory
cd CTSNPN

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
# Set GEMINI_API_KEY, GROQ_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Run FastAPI backend server
uvicorn backend.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000`.

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vite development server
npm run dev
```
Frontend interface will be live at `http://localhost:5173`.

---

## 🔌 API Reference

### Public Customer Endpoints
* **`GET /health`** — System health and database connectivity check.
* **`POST /chat`** — Main conversational RAG endpoint; accepts query, history, and optional diagnostic image.
* **`GET /products`** — Retrieve all catalog products with current pricing and stock status.
* **`GET /products/{product_id}`** — Retrieve full technical specifications for a single product.
* **`POST /reservations`** — Place an in-store reservation and generate a digital QR Hold Pass.

### Admin Endpoints (PIN-Protected)
* **`POST /admin/login`** — Authenticate store administrator with secure PIN.
* **`POST /admin/catalog/upload`** — Upload and dynamically index a new CSV or JSON product catalog into ChromaDB.
* **`PATCH /admin/products/{product_id}`** — Update product price, specifications, or stock count.
* **`DELETE /admin/products/{product_id}`** — Remove an obsolete product from the knowledge base and vector store.

---

## 🧪 Testing & System Evaluation

Run automated test suites to verify retrieval precision and end-to-end grounding:

```bash
# 1. Test vector retrieval accuracy and similarity thresholds
python test_retrieval.py

# 2. Test RAG question-answering accuracy across known test queries
python test_qa.py
```