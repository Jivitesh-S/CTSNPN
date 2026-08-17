# Intelligent Product Support Assistant

An intelligent, grounded conversational agent designed to help customers obtain accurate and understandable answers about products. The assistant leverages authorized product knowledge (such as manuals, FAQs, and support datasets) to provide clear support answers without hallucinating facts.

## Overview

Finding and interpreting product information across lengthy manuals, FAQs, and support materials is often slow and frustrating. The **Intelligent Product Support Assistant** solves this by using semantic retrieval (RAG) and conversational AI to provide direct, well-grounded answers. 

### How It Solves The Problem
Customers often struggle to find specific answers in long, technical documents or fragmented web pages, leading to frustration and poor support experiences. Traditional keyword searches frequently miss the mark because they don't understand the customer's intent or paraphrasing. 

This project tackles these pain points by:
- **Semantic Retrieval:** Understanding the *meaning* behind a user's question, rather than just matching keywords, ensuring relevant information is found even if phrased differently.
- **Direct Answers, Not Just Links:** Synthesizing the retrieved evidence into a concise, easy-to-understand response, saving the user from reading through multiple pages.
- **Dynamic Knowledge Ingestion:** Allowing administrators to seamlessly upload product catalogs and support datasets, ensuring the assistant always has the most up-to-date pricing, stock, and specifications.

### Key Features
- **Accurate Product Support:** Answers questions about features, specifications, pricing, setup, maintenance, and troubleshooting across various products.
- **Strict Grounding (No Hallucination):** Factual claims are exclusively supported by retrieved, authorized context. The assistant does not invent specifications, prices, or policies.
- **Safe Handling of Unsupported Questions:** When information is unavailable in the provided knowledge base, the assistant clearly states the limitation instead of inventing plausible answers.
- **Multi-Shop Architecture:** Supports cross-shop product search, enabling customers to compare products across different store branches.
- **Conversational Experience:** Provides a natural chat interface, while gracefully redirecting unrelated coding, math, or general-knowledge requests to product support.
- **Admin Dashboard & Catalog Management:** Provides secure endpoints for administrators to add shops, upload product datasets (JSON/CSV), and manage inventory.

## Project Structure

```text
.
├── backend/              # FastAPI application, RAG service, database, and ingestion logic
├── frontend/             # React + Vite chat interface
├── scripts/              # Utilities for knowledge indexing, semantic search, and evaluation
├── data/                 # Approved product knowledge and support datasets
├── requirements.txt      # Python dependencies for the backend
└── problem.md            # Canonical product-problem definition
```

## Prerequisites

- **Node.js**: v18 or later (for the frontend)
- **Python**: 3.10+ (for the backend)
- **API Keys**: A Gemini API key with access to configured chat and embedding models.

## Getting Started

### Backend Setup

1. **Navigate to the root directory:**
   ```bash
   cd CTSNPN
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory (you can use `.env.example` as a template) and configure your API keys (e.g., `GEMINI_API_KEY`).

5. **Run the backend server:**
   ```bash
   uvicorn backend.main:app --reload
   ```
   The backend API will be available at `http://localhost:8000`.

*(Note: Depending on your setup, you may need to run indexing scripts from the `scripts/` directory to populate your local vector database before querying).*

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or the port specified by Vite).

## User Endpoints (API Reference)

The backend provides several RESTful endpoints for both users and administrators.

### Public User Endpoints
- **`GET /health`** - System health check.
- **`POST /chat`** - Main conversational interface. Accepts a user query and optional chat history, returning a grounded, RAG-assisted answer.
- **`GET /shops`** - List all registered shops, with optional search and city filters.
- **`GET /shops/{shop_id}`** - Retrieve details for a specific shop.
- **`GET /shops/{shop_id}/products`** - List all products available in a specific shop.
- **`GET /products/search`** - Perform a cross-shop semantic search for products based on a query string.

### Admin Endpoints (Requires PIN)
- **`POST /admin/login`** - Authenticate an administrator.
- **`POST /shops`** - Register a new shop.
- **`DELETE /shops/{shop_id}`** - Remove a shop and its associated products.
- **`POST /shops/{shop_id}/upload`** - Upload and index a product dataset (JSON or CSV) for a specific shop.
- **`DELETE /shops/{shop_id}/products/{product_id}`** - Delete a specific product from a shop's catalog.

## Architecture & Security

- **State Management:** Chat history is kept in the browser memory for the session and sent with each request to provide context.
- **Retrieval-Augmented Generation (RAG):** Uses a hybrid architecture for core/stable knowledge and dynamic knowledge to ensure source provenance and trust.
- **Security:** The API keys stay in the backend environment. Public responses never expose internal vector scores, prompts, or provider errors.

For more detailed context on the problem this solves, please refer to [problem.md](problem.md).