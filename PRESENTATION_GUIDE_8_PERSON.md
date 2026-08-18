# 🎤 TechStore AI — 8-Person Professional Presentation Guide & Scripts

A complete, slide-by-slide presentation breakdown for 8 team members, including **Roles**, **Slide Content**, **Exact Code Snippets**, **Line-by-Line Technical Explanations**, and **Word-for-Word Spoken Scripts with Seamless Handoff Cues**.

---

## 📊 Master Presentation Schedule & Time Allocation

| # | Speaker Role | Section Title | Code / Visual Focus | Time |
|---|---|---|---|---|
| **1** | **The Strategist** | Introduction & Problem Scoping | Anti-Hallucination Guardrail (`rag_service.py`) | ~1.5 min |
| **2** | **The Product Lead** | Proposed Solution & Multi-Shop Vision | Pydantic Request Schema (`main.py`) | ~1.5 min |
| **3** | **The Backend Architect** | FastAPI Core & Layered Security | Middleware & REST Endpoints (`main.py`) | ~2.0 min |
| **4** | **The AI / RAG Engineer** | Hybrid Search & Cross-Encoder Re-Ranking | ChromaDB + BM25 + RRF (`rag_service.py`) | ~2.0 min |
| **5** | **The Frontend Lead** | UI Architecture & Vision AI Diagnostics | Diagnostic Card Component (`VisualDiagnosticCard.jsx`) | ~2.0 min |
| **6** | **The Omnichannel Lead** | In-Store QR Holds & Telegram Alerts | Live Telegram Bot Integration (`telegram_service.py`) | ~1.5 min |
| **7** | **The QA & Data Lead** | Dynamic Ingestion & Automated Testing | ChromaDB Upsert & Benchmarks (`ingest.py` / `test_retrieval.py`) | ~1.5 min |
| **8** | **The Visionary** | Enterprise Scaling & Conclusion | Cloud-to-Edge Fallback Circuit Breaker (`future.md`) | ~1.5 min |

---

## 👤 Speaker 1: Introduction, Problem Statement & Architecture Vision
* **Role:** Project Lead / Strategist  
* **Slide Title:** *The Retail Friction: Why Traditional Product Support Fails*

### 📋 Slide Bullet Points:
* **The Manual Dilemma:** 50+ page technical manuals, fragmented FAQ databases, and dense warranty policies cause high customer drop-off.
* **Search Blind Spots:** Traditional keyword search ignores semantic synonyms (e.g., searching *"water error"* misses *"OE drainage fault"*).
* **AI Hallucination Liability:** Public LLMs guess specifications, return windows, and pricing when not strictly constrained.
* **Our Target Scope:** An enterprise-ready multi-shop assistant grounded exclusively on verified product documentation.

### 💻 Code Snippet for Slide:
```python
# Problem Guardrail Definition (backend/rag_service.py)
# When the query is outside verified product manuals, strict fallback is triggered

UNSUPPORTED_FALLBACK = (
    "I can only assist with verified product specifications, manuals, "
    "and troubleshooting guides for our catalog. I do not have verified "
    "data for this query in our approved documents."
)
```

### 🎙️ Spoken Script:
> "Good morning/afternoon everyone. When a customer buys modern tech—whether an OLED TV or a smart washer—they face a frustrating barrier: 50-page PDF manuals, confusing error codes, and rigid keyword search bars that fail if you don't type the exact technical terminology.
>
> Generic LLM chatbots try to solve this, but they introduce a dangerous risk: **hallucinations**. They make up refund terms and invent nonexistent ports or dimensions.
>
> In our project, we solved this by designing a strictly grounded conversational assistant. As you can see in our fallback guardrail snippet, if a query cannot be verified against our ingested store catalog, our system is constrained to prevent fabrication. 
> 
> To explain our solution and core value proposition, I'll hand over to **[Speaker 2's Name]**."

---

## 👤 Speaker 2: Proposed Solution & Multi-Shop Ecosystem
* **Role:** Product Specialist  
* **Slide Title:** *TechStore AI: Multi-Shop Grounded Concierge*

### 📋 Slide Bullet Points:
* **Multi-Branch Hierarchy:** Support for multiple store locations (e.g., Metro, Downtown, Airport branches) with live stock tracking.
* **Cross-Store Semantic Search:** Real-time semantic discovery across all branches.
* **Dual Access Model:** Public conversational interface for shoppers + PIN-secured admin endpoints for store managers.

### 💻 Code Snippet for Slide:
```python
# API Contract & Data Model (backend/main.py)
class ChatRequest(BaseModel):
    query: str = Field(..., description="User's product or troubleshooting question")
    shop_id: Optional[str] = Field("S001", description="Target store branch ID")
    product_id: Optional[str] = Field(None, description="Optional target product filter")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Chat context")
    image_data: Optional[str] = Field(None, description="Base64 photo for visual diagnostics")
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 1]**. Our solution is **TechStore AI**—an omnichannel platform tailored for both single stores and multi-branch retail networks.
>
> On the screen is our core `ChatRequest` schema. Notice how structured our conversational contract is:
> - It takes natural language queries along with an active `shop_id` to enforce store-level catalog isolation.
> - It accepts session-level `history` for contextual follow-up questions.
> - And crucially, it supports `image_data` for visual hardware diagnostics.
>
> This gives users accurate spec comparison, troubleshooting, and in-store stock availability across any registered branch.
>
> To walk us through how the backend and server architecture handle these requests, here is **[Speaker 3's Name]**."

---

## 👤 Speaker 3: System Architecture & FastAPI Core
* **Role:** Backend / System Architect  
* **Slide Title:** *FastAPI Backend & Security Middleware Architecture*

### 📋 Slide Bullet Points:
* **FastAPI Async Engine:** High-concurrency REST endpoints for `/chat`, `/shops`, and `/inventory`.
* **Layered Middleware:** Security headers (`X-Frame-Options`, `CSP`, `nosniff`) & dynamic CORS handling.
* **Rate Limiting & Memory Isolation:** Sliding-window rate limiters preventing API abuse.

### 💻 Code Snippet for Slide:
```python
# High-Performance FastAPI Engine & Security Headers (backend/main.py)
app = FastAPI(
    title="TechStore Assistant",
    description="Multi-shop support API with hybrid retrieval (ChromaDB + BM25Okapi)"
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    return await rag_service.generate_grounded_response(req)
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 2]**. Let's examine our backend architecture.
>
> We chose **FastAPI** because of its native asynchronous execution and strict Pydantic validation. As shown in our middleware snippet:
> 1. We enforce enterprise HTTP security headers—preventing clickjacking and MIME-type sniffing.
> 2. We use dynamic CORS origin detection, securing communications between our React client and the backend.
> 3. The `/chat` endpoint receives the incoming user payload and delegates it to our dedicated RAG service.
>
> Now, **[Speaker 4's Name]** will explain how the RAG service performs hybrid vector retrieval and enforces 0% hallucination."

---

## 👤 Speaker 4: Hybrid RAG Engine, ChromaDB & Re-ranking
* **Role:** AI & NLP Engineer  
* **Slide Title:** *Hybrid Retrieval (BM25 + ChromaDB) & Cross-Encoder Re-Ranking*

### 📋 Slide Bullet Points:
* **Dense + Sparse Hybrid Search:** Combines **ChromaDB** (`BAAI/bge-small-en-v1.5`) dense semantic vectors with **BM25Okapi** sparse keyword matching.
* **Reciprocal Rank Fusion (RRF):** Fuses scores ($RRF\_K = 60$) to balance exact model numbers with conceptual queries.
* **Cross-Encoder Re-Ranking:** Uses `ms-marco-MiniLM-L-6-v2` to score relevance before feeding top chunks to the Groq/Gemini LLM.

### 💻 Code Snippet for Slide:
```python
# Hybrid Vector + Keyword Retrieval & Grounding (backend/rag_service.py)
def _retrieve(self, query: str, shop_id: str, product_id: Optional[str] = None):
    # 1. Dense Semantic Vector Search via ChromaDB
    dense_results = self.chroma_collection.query(
        query_embeddings=[self.embed_model.encode(query).tolist()],
        n_results=TOP_K,
        where={"shop_id": shop_id}
    )
    # 2. Sparse Lexical Search via BM25Okapi
    bm25_scores = self.bm25_index.get_scores(tokenize(query))
    
    # 3. Reciprocal Rank Fusion & Cross-Encoder Re-Ranking
    fused_contexts = rrf_fuse(dense_results, bm25_scores, k=60)
    ranked_contexts = self.reranker.predict([[query, doc] for doc in fused_contexts])
    return ranked_contexts[:MAX_UNIQUE_CONTEXTS]
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 3]**. Standard RAG systems struggle with product search because dense vectors often miss exact model numbers (like *'QN90D'* vs *'QN85D'*), while keyword search misses conceptual queries (like *'tv for bright rooms'*).
>
> To solve this, we implemented a **3-stage Hybrid Retrieval Engine**:
> 1. **Dense Search:** We query **ChromaDB** using `BAAI/bge-small-en-v1.5` embeddings.
> 2. **Sparse Search:** Simultaneously, we run **BM25Okapi** lexical scoring.
> 3. **RRF & Re-ranking:** We fuse both candidate lists with Reciprocal Rank Fusion, then run a **Cross-Encoder model** (`ms-marco-MiniLM`) to re-rank the top contexts.
>
> Only the most relevant snippets are passed into the LLM system prompt with strict grounding constraints.
>
> Next, **[Speaker 5's Name]** will show how our frontend renders this rich data for the user."

---

## 👤 Speaker 5: Frontend UI & Interactive Vision Diagnostics
* **Role:** Frontend / UI-UX Engineer  
* **Slide Title:** *React Frontend: Voice Modal & Vision AI Diagnostics*

### 📋 Slide Bullet Points:
* **Glassmorphic React UI:** Built with Vite and Tailwind CSS for instant rendering and zero layout shift.
* **Visual Diagnostic Component:** Analyzes user-uploaded appliance photos and renders categorized severity cards.
* **Interactive Media:** Dynamic comparison tables, embedded troubleshooting video cards, and voice mode.

### 💻 Code Snippet for Slide:
```jsx
// Vision Diagnostic Card Component (frontend/src/components/VisualDiagnosticCard.jsx)
export default function VisualDiagnosticCard({ diag, imagePreview }) {
  const severityColors = {
    Low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    Medium: "bg-amber-50 text-amber-700 border-amber-200",
    High: "bg-rose-50 text-rose-700 border-rose-200",
    Critical: "bg-purple-50 text-purple-700 border-purple-200",
  };

  return (
    <div className="rounded-2xl p-4 border bg-gradient-to-br from-white/95 to-blue-50/30 backdrop-blur-md">
      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityColors[diag.severity]}`}>
        {diag.severity} Severity Fault
      </span>
      <p className="text-xs text-slate-800 mt-2">{diag.analysis}</p>
    </div>
  );
}
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 4]**. A great AI backend needs an intuitive interface. We built our frontend with **React, Vite, and Tailwind CSS**.
>
> Instead of just plain text responses, our UI dynamically mounts contextual micro-apps directly into the chat:
> - As shown in the `VisualDiagnosticCard` snippet, when a user uploads a photo of an error code or damaged cable, the backend Vision pipeline returns an analysis with a calculated severity score (*Low, Medium, High, Critical*).
> - Our component renders this with tailored color badges and verified troubleshooting steps.
> - We also built a **Voice Modal** for real-time speech input and a **Comparison Card** that renders side-by-side spec tables.
>
> Now, **[Speaker 6's Name]** will explain how we connect digital conversations to real in-store inventory and Telegram alerts."

---

## 👤 Speaker 6: In-Store Reservations & Telegram Integration
* **Role:** Omnichannel / Integration Lead  
* **Slide Title:** *Omnichannel Commerce: QR Hold Passes & Real-Time Telegram Alerts*

### 📋 Slide Bullet Points:
* **In-Store Reservation Flow:** Shoppers can reserve items at their nearest store branch directly from the chat.
* **Digital QR Hold Pass:** Generates a secure, scannable QR pass with a 48-hour hold window.
* **Instant Telegram Webhooks:** Automated alerts dispatched directly to store management upon reservation.

### 💻 Code Snippet for Slide:
```python
# Real-Time Telegram Alert Integration (backend/telegram_service.py)
def send_telegram_reservation_alert(order_id: str, product_name: str, customer_phone: str, store_name: str):
    masked_phone = mask_phone_number(customer_phone)
    message = (
        f"🚨 <b>NEW IN-STORE RESERVATION</b>\n"
        f"📦 <b>Item:</b> {product_name}\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>\n"
        f"🏬 <b>Store:</b> {store_name}\n"
        f"📞 <b>Customer:</b> {masked_phone}\n"
        f"⏱ <i>Status: 48-Hour Hold Active</i>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"})
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 5]**. A key strength of TechStore AI is converting support conversations into physical store sales.
>
> When a user wants to purchase a product, they can click **'Reserve in Store'**:
> 1. The frontend generates a unique Order ID and digital QR Pass for counter pick-up.
> 2. On the backend, as shown in our `telegram_service.py` snippet, an instant webhook formats a clean HTML notification with masked customer PII for privacy and sends it to the store manager's **Telegram channel**.
> 3. The store team immediately sets aside the inventory, ensuring the customer never arrives to an out-of-stock item.
>
> To explain how administrators ingest new catalogs and how we test the system, I'll pass the mic to **[Speaker 7's Name]**."

---

## 👤 Speaker 7: Dynamic Ingestion, Admin Portal & Testing Pipeline
* **Role:** Data & QA Lead  
* **Slide Title:** *Data Ingestion Pipeline & Automated Test Validation*

### 📋 Slide Bullet Points:
* **Admin Ingestion (`sync_index`):** Upload CSV/JSON catalogs to automatically chunk, embed, and update ChromaDB.
* **Test Suite Coverage:** Automated tests for retrieval precision (`test_retrieval.py`), QA grounding (`test_qa.py`), and system lifecycle (`test_full_system_final.py`).
* **Deterministic Verification:** Validates that retrieval latency is under 300ms and similarity scores exceed confidence thresholds.

### 💻 Code Snippet for Slide:
```python
# Dynamic Ingestion & Benchmark Verification (backend/ingest.py & test_retrieval.py)
def sync_index(catalog_items: list, shop_id: str):
    documents, metadatas, ids = [], [], []
    for item in catalog_items:
        chunk = f"Product: {item['name']} | Specs: {item['specs']} | Price: ${item['price']}"
        documents.append(chunk)
        metadatas.append({"shop_id": shop_id, "product_id": item["id"]})
        ids.append(f"{shop_id}_{item['id']}")
    
    # Batch upsert into ChromaDB vector collection
    chroma_collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

# Automated Benchmark Loop
for pid, name, question in tests:
    results = rag_service._retrieve(question, shop_id="S001", product_id=pid)
    assert len(results) > 0 and results[0]["similarity"] >= 0.30
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 6]**. Keeping an AI assistant up to date must be easy for store managers.
>
> - Through our **Admin Portal**, managers upload raw product catalogs in CSV or JSON. As shown in `sync_index`, the backend extracts structured specs, chunks them with store metadata, and upserts them directly into ChromaDB. There is zero downtime or need to restart the server.
> - On the right side of the slide is our automated testing harness. We test retrieval latency and accuracy across our entire catalog (`test_retrieval.py` and `test_qa.py`), ensuring that every query retrieves the correct product chunk with similarity scores consistently meeting our confidence thresholds.
>
> To share our future enterprise roadmap and conclude our presentation, I'll hand over to **[Speaker 8's Name]**."

---

## 👤 Speaker 8: Future Enterprise Roadmap & Conclusion
* **Role:** Strategy & Future Scaling Lead  
* **Slide Title:** *Enterprise Scaling Roadmap & Future Horizons*

### 📋 Slide Bullet Points:
* **Phase 1 (Multilingual):** Regional voice and text expansion (*Hindi, Tamil, Telugu*) with Whisper and Neural TTS.
* **Phase 2 (ERP Sync):** Bi-directional POS webhooks for SAP S/4HANA and Shopify inventory.
* **Phase 3 (Edge Resilience):** On-premise fallback using local **Ollama / vLLM** if cloud internet drops.
* **Phase 4 (WebXR AR):** 3D augmented reality projection for living room TV & appliance placement.

### 💻 Code Snippet for Slide:
```python
# Roadmap Architecture: Fallback Circuit Breaker (future.md architecture)
async def resilient_inference(query: str, context: str):
    try:
        # Primary: Cloud Groq / Gemini for high speed (<500ms)
        return await call_cloud_llm(query, context, timeout=3.0)
    except (TimeoutError, NetworkError):
        # Fallback: Local On-Premises Edge Model (Ollama Llama-3.2)
        return await call_local_edge_llm(query, context)
```

### 🎙️ Spoken Script:
> "Thank you, **[Speaker 7]**. To conclude, we have mapped out a 4-phase enterprise roadmap:
> 1. **Multilingual Regional Voice:** Expanding our STT/TTS pipeline into Hindi, Tamil, and Telugu to increase regional adoption by 65%.
> 2. **Live ERP Synchronization:** Implementing bidirectional webhooks to sync store POS systems (like SAP and Shopify) in real time.
> 3. **Edge AI Fallback:** As illustrated in our circuit breaker snippet, we are introducing local Ollama/vLLM fallbacks on store counters to guarantee 99.99% uptime during internet disruptions.
> 4. **Spatial WebXR:** Enabling shoppers to project true-to-scale 3D appliances directly into their homes via mobile camera AR.
>
> TechStore AI converts static, confusing manuals into an intelligent, grounded, and revenue-generating conversational platform.
>
> Thank you for your time. Our team is now ready for questions!"

---

## 💡 Quick Tips for the Presentation:
1. **Slide Layout:** Place bullet points on the left half of the slide and the formatted code snippet on the right half.
2. **Handoffs:** Practice the bolded handoff sentences so transitions between speakers take less than 2 seconds.
3. **Q&A Roles:**
   - Architecture & FastAPI $\rightarrow$ **Speaker 3**
   - RAG / Embeddings / Grounding $\rightarrow$ **Speaker 4**
   - UI / Components $\rightarrow$ **Speaker 5**
   - Reservations & Telegram $\rightarrow$ **Speaker 6**
   - Ingestion & Testing $\rightarrow$ **Speaker 7**
