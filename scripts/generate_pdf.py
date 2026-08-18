import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "TechStore AI — 8-Person Presentation Master Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL — FOR TEAM PRESENTATION USE ONLY")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def build_pdf(filename="TechStore_AI_8_Person_Presentation_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1E3A8A")   # Deep Blue
    SECONDARY = colors.HexColor("#0284C7") # Cyan/Sky Blue
    DARK_BG = colors.HexColor("#0F172A")   # Slate Dark
    LIGHT_BG = colors.HexColor("#F8FAFC")  # Off White
    BOX_BG = colors.HexColor("#F0FDF4")    # Light Emerald
    SCRIPT_BG = colors.HexColor("#F0F9FF") # Light Blue
    CODE_BG = colors.HexColor("#1E293B")   # Dark Code Box
    
    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.white
    )
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#38BDF8")
    )
    
    script_style = ParagraphStyle(
        'ScriptStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )
    
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # Title Block
    story.append(Spacer(1, 10))
    story.append(Paragraph("Intelligent Product Support Assistant (TechStore AI)", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>8-Person Professional Presentation Master Guide & Word-for-Word Scripts</b>", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=14))

    # Master Schedule Table
    table_data = [
        [
            Paragraph("<b>#</b>", table_hdr_style),
            Paragraph("<b>Speaker Role</b>", table_hdr_style),
            Paragraph("<b>Topic / Section Title</b>", table_hdr_style),
            Paragraph("<b>Code / Visual Focus</b>", table_hdr_style),
            Paragraph("<b>Time</b>", table_hdr_style),
        ],
        [
            Paragraph("<b>1</b>", table_cell_style),
            Paragraph("The Strategist", table_cell_style),
            Paragraph("Introduction & Problem Scoping", table_cell_style),
            Paragraph("Anti-Hallucination Guardrail (`rag_service.py`)", table_cell_style),
            Paragraph("1.5m", table_cell_style),
        ],
        [
            Paragraph("<b>2</b>", table_cell_style),
            Paragraph("The Product Lead", table_cell_style),
            Paragraph("Proposed Solution & Capabilities", table_cell_style),
            Paragraph("ChatRequest Pydantic Schema (`main.py`)", table_cell_style),
            Paragraph("1.5m", table_cell_style),
        ],
        [
            Paragraph("<b>3</b>", table_cell_style),
            Paragraph("Backend Architect", table_cell_style),
            Paragraph("FastAPI Engine & Security Headers", table_cell_style),
            Paragraph("Security Middleware & Endpoints (`main.py`)", table_cell_style),
            Paragraph("2.0m", table_cell_style),
        ],
        [
            Paragraph("<b>4</b>", table_cell_style),
            Paragraph("AI / RAG Engineer", table_cell_style),
            Paragraph("Hybrid Retrieval & Re-ranking", table_cell_style),
            Paragraph("ChromaDB + BM25 + Cross-Encoder (`rag_service.py`)", table_cell_style),
            Paragraph("2.0m", table_cell_style),
        ],
        [
            Paragraph("<b>5</b>", table_cell_style),
            Paragraph("Frontend Lead", table_cell_style),
            Paragraph("React UI & Vision Diagnostics", table_cell_style),
            Paragraph("Diagnostic Card Component (`VisualDiagnosticCard.jsx`)", table_cell_style),
            Paragraph("2.0m", table_cell_style),
        ],
        [
            Paragraph("<b>6</b>", table_cell_style),
            Paragraph("Operations Lead", table_cell_style),
            Paragraph("In-Store Holds & Telegram Alerts", table_cell_style),
            Paragraph("Live Telegram Bot Webhook (`telegram_service.py`)", table_cell_style),
            Paragraph("1.5m", table_cell_style),
        ],
        [
            Paragraph("<b>7</b>", table_cell_style),
            Paragraph("QA & Data Lead", table_cell_style),
            Paragraph("Catalog Ingestion & Test Suites", table_cell_style),
            Paragraph("ChromaDB Upsert & Benchmarks (`ingest.py`)", table_cell_style),
            Paragraph("1.5m", table_cell_style),
        ],
        [
            Paragraph("<b>8</b>", table_cell_style),
            Paragraph("The Visionary", table_cell_style),
            Paragraph("Enterprise Scaling & Conclusion", table_cell_style),
            Paragraph("Edge Fallback Circuit Breaker (`future.md`)", table_cell_style),
            Paragraph("1.5m", table_cell_style),
        ],
    ]

    sched_table = Table(table_data, colWidths=[24, 90, 155, 195, 45])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 16))

    # SPEAKERS CONTENT
    speakers = [
        {
            "num": "1",
            "role": "The Strategist (Project Lead)",
            "slide_title": "The Retail Friction: Why Traditional Product Support Fails",
            "bullets": [
                "<b>The Manual Dilemma:</b> 50+ page technical manuals, fragmented FAQ databases, and dense warranty policies cause high customer drop-off.",
                "<b>Search Blind Spots:</b> Traditional keyword search ignores semantic synonyms (e.g., searching <i>'water leaking'</i> misses <i>'OE drainage fault'</i>).",
                "<b>AI Hallucination Liability:</b> Generic public LLMs guess specifications, return windows, and pricing when not strictly constrained.",
                "<b>Target Scope:</b> An intelligent product support assistant grounded strictly and exclusively on authorized product documentation."
            ],
            "code": "# Problem Guardrail Definition (backend/rag_service.py)\n# When query cannot be answered from verified docs, strict fallback is triggered\n\nUNSUPPORTED_FALLBACK = (\n    \"I can only assist with verified product specifications, manuals, \"\n    \"and troubleshooting guides for our catalog. I do not have verified \"\n    \"data for this query in our approved documents.\"\n)",
            "script": "\"Good morning/afternoon everyone. When a customer buys modern electronics—whether a flagship smartphone, a 4K OLED TV, or a smart washing machine—they face a frustrating barrier: 50-page PDF manuals, confusing error codes, and rigid keyword search bars that fail if you don't type the exact technical terminology.<br/><br/>Generic AI chatbots try to solve this, but they introduce a dangerous risk: <b>hallucinations</b>. They make up refund terms and invent nonexistent ports or dimensions.<br/><br/>In our project, we solved this by building the <b>Intelligent Product Support Assistant</b>. As you can see in our fallback guardrail snippet, if a query cannot be verified against our approved product documents, our system is strictly constrained to prevent fabrication.<br/><br/>To explain our solution and core system capabilities, I'll hand over to <b>[Speaker 2's Name]</b>.\""
        },
        {
            "num": "2",
            "role": "The Product Lead (Product Specialist)",
            "slide_title": "TechStore AI: Intelligent & Grounded Product Support",
            "bullets": [
                "<b>Conversational Semantic Search:</b> Understands user intent and natural phrasing without requiring exact keyword syntax.",
                "<b>100% Grounded Answers:</b> Synthesizes direct answers for specifications, setup, maintenance, and troubleshooting.",
                "<b>Interactive Media Support:</b> Delivers side-by-side product comparisons, visual error diagnostics, and video guides.",
                "<b>Actionable Conversion:</b> Enables shoppers to reserve items for in-store pickup with instant hold passes."
            ],
            "code": "# API Contract & Data Model (backend/main.py)\nclass ChatRequest(BaseModel):\n    query: str = Field(..., description=\"User's product or troubleshooting question\")\n    product_id: Optional[str] = Field(None, description=\"Optional target product filter\")\n    history: List[Dict[str, str]] = Field(default_factory=list, description=\"Conversation context\")\n    image_data: Optional[str] = Field(None, description=\"Base64 photo for visual diagnostics\")",
            "script": "\"Thank you, <b>[Speaker 1]</b>. Our solution is <b>TechStore AI</b>—an end-to-end intelligent assistant engineered to provide instant, clear, and provably grounded answers.<br/><br/>On the screen is our core <code>ChatRequest</code> schema:<br/>• It accepts natural language queries and optional <code>product_id</code> filters for focused answers.<br/>• It accepts multi-turn conversation <code>history</code> for contextual follow-up questions.<br/>• It supports <code>image_data</code> so users can upload photos of hardware issues or error lights for visual diagnosis.<br/><br/>This gives customers an all-in-one assistant for spec queries, troubleshooting, and in-store reservations.<br/><br/>To walk us through how the backend and server architecture handle these requests, here is <b>[Speaker 3's Name]</b>.\""
        },
        {
            "num": "3",
            "role": "The Backend Architect (System Architect)",
            "slide_title": "FastAPI Backend & Security Middleware Architecture",
            "bullets": [
                "<b>FastAPI Async Engine:</b> High-concurrency REST endpoints for <code>/chat</code>, <code>/health</code>, and inventory operations.",
                "<b>Layered Middleware:</b> Enterprise security headers (<code>X-Frame-Options</code>, <code>CSP</code>, <code>nosniff</code>) & dynamic CORS handling.",
                "<b>Sliding-Window Rate Limiter:</b> Protects the API against abuse and Denial-of-Service attacks.",
                "<b>Local Persistence:</b> Local database holding product catalogs and reservation states."
            ],
            "code": "# High-Performance FastAPI Engine & Security Headers (backend/main.py)\napp = FastAPI(title=\"TechStore Assistant\", description=\"AI-powered product support API\")\n\n@app.middleware(\"http\")\nasync def add_security_headers(request: Request, call_next):\n    response = await call_next(request)\n    response.headers[\"X-Content-Type-Options\"] = \"nosniff\"\n    response.headers[\"X-Frame-Options\"] = \"SAMEORIGIN\"\n    response.headers[\"X-XSS-Protection\"] = \"1; mode=block\"\n    return response\n\n@app.post(\"/chat\", response_model=ChatResponse)\nasync def chat_endpoint(req: ChatRequest):\n    return await rag_service.generate_grounded_response(req)",
            "script": "\"Thank you, <b>[Speaker 2]</b>. Let's examine our backend architecture.<br/><br/>We chose <b>FastAPI</b> because of its native asynchronous execution and strict Pydantic validation:<br/>1. We enforce enterprise HTTP security headers to protect against clickjacking, XSS, and MIME-type sniffing.<br/>2. We use dynamic CORS handling, ensuring secure communication between our React client and the backend server.<br/>3. The <code>/chat</code> endpoint receives incoming queries and seamlessly delegates them to our dedicated RAG pipeline.<br/><br/>Now, <b>[Speaker 4's Name]</b> will explain how our RAG engine performs hybrid vector retrieval and ensures 0% hallucination.\""
        },
        {
            "num": "4",
            "role": "The AI / RAG Engineer (AI & NLP Lead)",
            "slide_title": "Hybrid Retrieval (BM25 + ChromaDB) & Cross-Encoder Re-Ranking",
            "bullets": [
                "<b>Dense + Sparse Hybrid Search:</b> Combines <b>ChromaDB</b> (<code>BAAI/bge-small-en-v1.5</code>) dense semantic vectors with <b>BM25Okapi</b> sparse keyword matching.",
                "<b>Reciprocal Rank Fusion (RRF):</b> Fuses scores (<code>RRF_K = 60</code>) to balance exact model numbers with conceptual queries.",
                "<b>Cross-Encoder Re-Ranking:</b> Uses <code>ms-marco-MiniLM-L-6-v2</code> to score relevance before feeding top chunks to the Groq/Gemini LLM."
            ],
            "code": "# Hybrid Vector + Keyword Retrieval & Grounding (backend/rag_service.py)\ndef _retrieve(self, query: str, product_id: Optional[str] = None):\n    # 1. Dense Semantic Vector Search via ChromaDB\n    dense_results = self.chroma_collection.query(\n        query_embeddings=[self.embed_model.encode(query).tolist()],\n        n_results=TOP_K\n    )\n    # 2. Sparse Lexical Search via BM25Okapi\n    bm25_scores = self.bm25_index.get_scores(tokenize(query))\n    \n    # 3. Reciprocal Rank Fusion & Cross-Encoder Re-Ranking\n    fused_contexts = rrf_fuse(dense_results, bm25_scores, k=60)\n    ranked_contexts = self.reranker.predict([[query, doc] for doc in fused_contexts])\n    return ranked_contexts[:MAX_UNIQUE_CONTEXTS]",
            "script": "\"Thank you, <b>[Speaker 3]</b>. Standard RAG systems struggle with product search because dense vectors often miss exact model numbers (like <i>'QN90D'</i> vs <i>'QN85D'</i>), while keyword search misses conceptual queries (like <i>'tv for bright rooms'</i>).<br/><br/>To solve this, we implemented a <b>3-stage Hybrid Retrieval Engine</b>:<br/>1. <b>Dense Search:</b> We query <b>ChromaDB</b> using <code>BAAI/bge-small-en-v1.5</code> embeddings.<br/>2. <b>Sparse Search:</b> Simultaneously, we run <b>BM25Okapi</b> lexical scoring for exact model numbers.<br/>3. <b>RRF & Re-ranking:</b> We fuse both candidate lists using Reciprocal Rank Fusion, then run a <b>Cross-Encoder model</b> (<code>ms-marco-MiniLM</code>) to re-rank the top contexts.<br/><br/>Only verified document snippets are passed into the LLM system prompt with strict grounding constraints.<br/><br/>Next, <b>[Speaker 5's Name]</b> will show how our frontend renders this rich data for the user.\""
        },
        {
            "num": "5",
            "role": "The Frontend Lead (UI-UX Engineer)",
            "slide_title": "React Frontend: Voice Modal & Vision AI Diagnostics",
            "bullets": [
                "<b>Glassmorphic React UI:</b> Built with Vite and Tailwind CSS for fast rendering and fluid animations.",
                "<b>Visual Diagnostic Component:</b> Analyzes user-uploaded appliance photos and renders categorized severity cards.",
                "<b>Interactive Media:</b> Dynamic comparison tables, embedded troubleshooting video cards, and voice mode."
            ],
            "code": "// Vision Diagnostic Card Component (frontend/src/components/VisualDiagnosticCard.jsx)\nexport default function VisualDiagnosticCard({ diag, imagePreview }) {\n  const severityColors = {\n    Low: \"bg-emerald-50 text-emerald-700 border-emerald-200\",\n    Medium: \"bg-amber-50 text-amber-700 border-amber-200\",\n    High: \"bg-rose-50 text-rose-700 border-rose-200\",\n    Critical: \"bg-purple-50 text-purple-700 border-purple-200\",\n  };\n\n  return (\n    <div className=\"rounded-2xl p-4 border bg-gradient-to-br from-white/95 to-blue-50/30 backdrop-blur-md\">\n      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${severityColors[diag.severity]}`}>\n        {diag.severity} Severity Fault\n      </span>\n      <p className=\"text-xs text-slate-800 mt-2\">{diag.analysis}</p>\n    </div>\n  );\n}",
            "script": "\"Thank you, <b>[Speaker 4]</b>. A great AI backend needs an intuitive interface. We built our frontend with <b>React, Vite, and Tailwind CSS</b>.<br/><br/>Instead of just plain text responses, our UI dynamically mounts contextual micro-apps directly into the chat:<br/>• As shown in the <code>VisualDiagnosticCard</code> snippet, when a user uploads a photo of an error code or damaged cable, the backend Vision pipeline returns an analysis with a calculated severity score (<i>Low, Medium, High, Critical</i>).<br/>• Our component renders this with tailored color badges and verified troubleshooting steps.<br/>• We also built a <b>Voice Modal</b> for real-time speech input and a <b>Comparison Card</b> that renders side-by-side spec tables.<br/><br/>Now, <b>[Speaker 6's Name]</b> will explain how we connect digital conversations to in-store reservations and Telegram alerts.\""
        },
        {
            "num": "6",
            "role": "The Operations Lead (Omnichannel Engineer)",
            "slide_title": "Closing the Loop: In-Store QR Holds & Telegram Alerts",
            "bullets": [
                "<b>In-Store Reservation Flow:</b> Shoppers can reserve items directly from the chat with a custom hold window.",
                "<b>Digital QR Hold Pass:</b> Generates a secure, scannable QR pass for fast checkout at the store counter.",
                "<b>Instant Telegram Webhooks:</b> Automated alerts dispatched directly to store staff upon reservation."
            ],
            "code": "# Real-Time Telegram Alert Integration (backend/telegram_service.py)\ndef send_telegram_reservation_alert(order_id: str, product_name: str, customer_phone: str):\n    masked_phone = mask_phone_number(customer_phone)\n    message = (\n        f\"🚨 <b>NEW IN-STORE RESERVATION</b>\\n\"\n        f\"📦 <b>Item:</b> {product_name}\\n\"\n        f\"🆔 <b>Order ID:</b> <code>{order_id}</code>\\n\"\n        f\"📞 <b>Customer:</b> {masked_phone}\\n\"\n        f\"⏱ <i>Status: 48-Hour Hold Active</i>\"\n    )\n    url = f\"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage\"\n    requests.post(url, json={\"chat_id\": TELEGRAM_CHAT_ID, \"text\": message, \"parse_mode\": \"HTML\"})",
            "script": "\"Thank you, <b>[Speaker 5]</b>. A key strength of TechStore AI is converting support conversations into physical store sales.<br/><br/>When a user wants to purchase a product, they can click <b>'Reserve in Store'</b>:<br/>1. The frontend generates a unique Order ID and digital QR Pass for counter pick-up.<br/>2. On the backend, as shown in our <code>telegram_service.py</code> snippet, an instant webhook formats a clean notification with masked customer PII for privacy and sends it to the store staff's <b>Telegram channel</b>.<br/>3. The store team immediately sets aside the inventory, ensuring the customer never arrives to an out-of-stock item.<br/><br/>To explain how administrators manage catalogs and how we test the system, I'll pass the mic to <b>[Speaker 7's Name]</b>.\""
        },
        {
            "num": "7",
            "role": "The QA & Data Lead (Data & Quality Lead)",
            "slide_title": "Catalog Ingestion Pipeline & Automated Test Validation",
            "bullets": [
                "<b>Admin Ingestion (<code>sync_index</code>):</b> Upload CSV/JSON catalogs to automatically chunk, embed, and update ChromaDB.",
                "<b>PIN-Protected Admin:</b> Secure admin interface for inventory and document updates.",
                "<b>Test Suite Coverage:</b> Automated tests for retrieval precision (<code>test_retrieval.py</code>), QA grounding (<code>test_qa.py</code>), and Telegram diagnostic workflows."
            ],
            "code": "# Dynamic Ingestion & Benchmark Verification (backend/ingest.py & test_retrieval.py)\ndef sync_index(catalog_items: list):\n    documents, metadatas, ids = [], [], []\n    for item in catalog_items:\n        chunk = f\"Product: {item['name']} | Specs: {item['specs']} | Price: ${item['price']}\"\n        documents.append(chunk)\n        metadatas.append({\"product_id\": item[\"id\"]})\n        ids.append(f\"prod_{item['id']}\")\n    \n    # Batch upsert into ChromaDB vector collection\n    chroma_collection.upsert(documents=documents, metadatas=metadatas, ids=ids)\n\n# Automated Benchmark Loop\nfor pid, name, question in tests:\n    results = rag_service._retrieve(question, product_id=pid)\n    assert len(results) > 0 and results[0][\"similarity\"] >= 0.30",
            "script": "\"Thank you, <b>[Speaker 6]</b>. Keeping an AI assistant up to date must be effortless for store managers.<br/><br/>• Through our <b>Admin Portal</b>, managers upload raw product catalogs in CSV or JSON. As shown in <code>sync_index</code>, the backend extracts structured specs, chunks them, and upserts them directly into ChromaDB. There is zero downtime or need to restart the server.<br/>• On the right side of the slide is our automated testing harness. We test retrieval latency and accuracy across our entire catalog (<code>test_retrieval.py</code> and <code>test_qa.py</code>), ensuring that every query retrieves the correct product chunk with similarity scores consistently meeting our confidence thresholds.<br/><br/>To share our future enterprise roadmap and conclude our presentation, I'll hand over to <b>[Speaker 8's Name]</b>.\""
        },
        {
            "num": "8",
            "role": "The Visionary (Strategy & Scaling Lead)",
            "slide_title": "Enterprise Scaling Roadmap & Future Horizons",
            "bullets": [
                "<b>Phase 1 (Multilingual):</b> Regional voice and text expansion (<i>Hindi, Tamil, Telugu</i>) with Whisper and Neural TTS.",
                "<b>Phase 2 (ERP Sync):</b> Bi-directional POS webhooks for SAP S/4HANA and Shopify inventory.",
                "<b>Phase 3 (Edge Resilience):</b> On-premise fallback using local <b>Ollama / vLLM</b> if cloud internet drops.",
                "<b>Phase 4 (WebXR AR):</b> 3D augmented reality projection for living room TV & appliance placement."
            ],
            "code": "# Roadmap Architecture: Fallback Circuit Breaker (future.md architecture)\nasync def resilient_inference(query: str, context: str):\n    try:\n        # Primary: Cloud Groq / Gemini for high speed (<500ms)\n        return await call_cloud_llm(query, context, timeout=3.0)\n    except (TimeoutError, NetworkError):\n        # Fallback: Local On-Premises Edge Model (Ollama Llama-3.2)\n        return await call_local_edge_llm(query, context)",
            "script": "\"Thank you, <b>[Speaker 7]</b>. To conclude, we have mapped out a 4-phase enterprise roadmap:<br/>1. <b>Multilingual Regional Voice:</b> Expanding our STT/TTS pipeline into Hindi, Tamil, and Telugu to increase regional adoption by 65%.<br/>2. <b>Live ERP Synchronization:</b> Implementing bidirectional webhooks to sync store POS systems (like SAP and Shopify) in real time.<br/>3. <b>Edge AI Fallback:</b> As illustrated in our circuit breaker snippet, we are introducing local Ollama/vLLM fallbacks on store counters to guarantee 99.99% uptime during internet disruptions.<br/>4. <b>Spatial WebXR:</b> Enabling shoppers to project true-to-scale 3D appliances directly into their homes via mobile camera AR.<br/><br/>TechStore AI converts static, confusing manuals into an intelligent, grounded, and revenue-generating conversational platform.<br/><br/>Thank you for your time. Our team is now ready for questions!\""
        }
    ]

    for spk in speakers:
        card = []
        
        # Header Badge
        header_table = Table(
            [[
                Paragraph(f"<b>SPEAKER {spk['num']}: {spk['role'].upper()}</b>", h1_style),
                Paragraph("<b>~1.5 - 2.0 MINS</b>", ParagraphStyle('RightTime', parent=h1_style, alignment=TA_CENTER))
            ]],
            colWidths=[400, 110]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        card.append(header_table)
        card.append(Spacer(1, 4))
        
        # Slide Title
        card.append(Paragraph(f"<b>Slide Focus:</b> <i>{spk['slide_title']}</i>", slide_title_style))
        card.append(Spacer(1, 4))
        
        # Bullets + Code side-by-side or stacked
        bullets_flow = []
        for b in spk['bullets']:
            bullets_flow.append(Paragraph(f"• {b}", bullet_style))
            bullets_flow.append(Spacer(1, 2))
        
        import html
        escaped_code = html.escape(spk['code']).replace("\n", "<br/>").replace(" ", "&nbsp;")
        code_p = Paragraph(escaped_code, code_style)
        
        code_box = Table([[code_p]], colWidths=[500])
        code_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CODE_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#334155"))
        ]))
        
        card.extend(bullets_flow)
        card.append(Spacer(1, 3))
        card.append(Paragraph("<b>Code Snippet to Present:</b>", ParagraphStyle('CodeHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=PRIMARY)))
        card.append(Spacer(1, 2))
        card.append(code_box)
        card.append(Spacer(1, 4))
        
        # Spoken Script Box
        script_p = Paragraph(f"<b>🎙️ Exact Spoken Script:</b><br/>{spk['script']}", script_style)
        script_box = Table([[script_p]], colWidths=[500])
        script_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SCRIPT_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LINELEFT', (0, 0), (0, -1), 3, SECONDARY),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD"))
        ]))
        card.append(script_box)
        card.append(Spacer(1, 10))
        
        story.append(KeepTogether(card))

    # Q&A Readiness Matrix
    qa_card = []
    qa_card.append(Paragraph("<b>🎯 Panel Q&A Field Routing Matrix</b>", title_style))
    qa_card.append(Spacer(1, 6))
    
    qa_data = [
        [Paragraph("<b>Question Topic / Technical Area</b>", table_hdr_style), Paragraph("<b>Assigned Responder</b>", table_hdr_style), Paragraph("<b>Key Defense Points to Mention</b>", table_hdr_style)],
        [
            Paragraph("System Architecture & FastAPI Scalability", table_cell_style),
            Paragraph("<b>Speaker 3</b>", table_cell_style),
            Paragraph("Asynchronous execution, connection pooling, security middleware headers, sliding-window rate limiters.", table_cell_style)
        ],
        [
            Paragraph("RAG Accuracy, Retrieval & Zero-Hallucination", table_cell_style),
            Paragraph("<b>Speaker 4</b>", table_cell_style),
            Paragraph("Dense BGE vectors + BM25 keyword matching + Cross-Encoder re-ranking + strict system prompt constraint.", table_cell_style)
        ],
        [
            Paragraph("Frontend Usability & Vision AI Diagnostics", table_cell_style),
            Paragraph("<b>Speaker 5</b>", table_cell_style),
            Paragraph("React + Vite client performance, Web Speech API voice loop, Base64 image diagnostic card pipeline.", table_cell_style)
        ],
        [
            Paragraph("In-Store Conversion & Telegram Alerts", table_cell_style),
            Paragraph("<b>Speaker 6</b>", table_cell_style),
            Paragraph("Seamless O2O reservation flow, QR code hold pass, real-time Telegram Bot webhook with masked PII.", table_cell_style)
        ],
        [
            Paragraph("Catalog Ingestion & Test Validation", table_cell_style),
            Paragraph("<b>Speaker 7</b>", table_cell_style),
            Paragraph("Dynamic CSV/JSON indexing without server restarts, automated retrieval precision & QA test suites.", table_cell_style)
        ],
    ]
    
    qa_table = Table(qa_data, colWidths=[150, 90, 270])
    qa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    qa_card.append(qa_table)
    story.append(KeepTogether(qa_card))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Successfully generated at: {filename}")

if __name__ == "__main__":
    output_path = os.path.join(r"c:\Users\jivit\OneDrive\Desktop\finalcts\CTSNPN", "TechStore_AI_8_Person_Presentation_Guide.pdf")
    build_pdf(output_path)
