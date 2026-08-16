import csv
import io
import json
import os
import threading
from typing import Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend import db as shop_db
from backend.ingest import sync_index
from backend.rag_service import RAGService


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="TechStore Assistant",
    description=(
        "AI-powered multi-shop support API using "
        "hybrid retrieval (ChromaDB + BM25), intent routing, "
        "and Groq LLM generation."
    ),
    version="1.0.0",
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# RAG SERVICE
# =========================================================

rag_service = RAGService()


# =========================================================
# CHAT MODELS
# =========================================================

class ChatTurn(BaseModel):

    role: str = Field(
        ...,
        description="Either 'user' or 'assistant'.",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="Message text.",
    )


class ChatRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Customer question.",
    )

    history: Optional[List[ChatTurn]] = Field(
        default=None,
        description="Recent conversation turns for context.",
    )

    shop_id: Optional[str] = Field(
        default=None,
        description=(
            "Shop to scope the answer to. Omit for cross-shop "
            "(compare products across all shops)."
        ),
    )


class ChatResponse(BaseModel):

    success: bool

    answer: str

    relevant: bool

    similarity_score: float

    intent: Optional[str] = None

    support_intent: Optional[str] = None

    shop_id: Optional[str] = None

    shop_name: Optional[str] = None


# =========================================================
# SHOP MODELS
# =========================================================

class AddShopRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        description="Shop name.",
    )

    description: str = Field(
        default="",
        description="Short shop description.",
    )

    category: str = Field(
        default="electronics",
        description="Shop category (electronics, mobile, etc.).",
    )

    address: str = Field(
        default="",
        description="Street address.",
    )

    city: str = Field(
        default="",
        description="City / area.",
    )

    pincode: str = Field(
        default="",
        description="Pincode.",
    )

    phone: str = Field(
        default="",
        description="Contact phone.",
    )

    email: str = Field(
        default="",
        description="Contact email.",
    )

    timings: str = Field(
        default="",
        description="Opening hours.",
    )


class ShopResponse(BaseModel):

    id: str

    name: str

    description: str

    category: str

    address: str

    city: str

    pincode: str

    phone: str

    email: str

    timings: str

    created_at: str

    product_count: int = 0


# =========================================================
# ADMIN AUTHENTICATION
# =========================================================

ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")


class AdminLoginRequest(BaseModel):

    pin: str = Field(
        ...,
        min_length=1,
        description="Admin password / PIN.",
    )


@app.post("/admin/login")
def admin_login(
    request: AdminLoginRequest,
):

    if request.pin == ADMIN_PIN:

        return {
            "ok": True,
        }

    raise HTTPException(
        status_code=401,
        detail="Incorrect password.",
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "TechStore Assistant API is running."
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# CHAT
# =========================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    try:

        history = None

        if request.history:

            history = [
                {
                    "role": turn.role,
                    "content": turn.content,
                }
                for turn in request.history
            ]

        result = rag_service.chat(
            request.question,
            history=history,
            shop_id=request.shop_id,
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        print(
            f"Internal server error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred "
                "while processing the question."
            ),
        )


# =========================================================
# SHOP & DATASET MANAGEMENT
# =========================================================

_shop_lock = threading.Lock()

VALID_CATEGORIES = {"phone", "laptop", "accessory"}

VALID_STOCK = {"In stock", "Low stock", "Out of stock"}


def _normalize_product(data: dict) -> dict:

    name = str(data.get("name") or "").strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Product 'name' is required.",
        )

    category = str(
        data.get("category") or "accessory"
    ).lower()

    if category not in VALID_CATEGORIES:

        raise HTTPException(
            status_code=400,
            detail=(
                f"category must be one of "
                f"{sorted(VALID_CATEGORIES)}."
            ),
        )

    stock = str(data.get("stock") or "In stock")

    if stock not in VALID_STOCK:

        raise HTTPException(
            status_code=400,
            detail=(
                f"stock must be one of {sorted(VALID_STOCK)}."
            ),
        )

    try:
        price = int(float(data.get("price") or 0))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="price must be a number.",
        )

    try:
        warranty_months = int(
            data.get("warranty_months")
            or data.get("warranty")
            or 0
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="warranty_months must be a number.",
        )

    specs = data.get("specs") or {}

    if not isinstance(specs, dict):

        raise HTTPException(
            status_code=400,
            detail="specs must be an object.",
        )

    specs = {
        str(key).strip(): str(value).strip()
        for key, value in specs.items()
        if str(key).strip() and value is not None
    }

    return {
        "id": str(data.get("id") or "").strip() or None,
        "name": name,
        "brand": str(data.get("brand") or "").strip(),
        "category": category,
        "price": max(0, price),
        "stock": stock,
        "warranty_months": max(0, warranty_months),
        "description": str(
            data.get("description") or ""
        ).strip(),
        "specs": specs,
    }


def _reindex():

    sync_index(
        embedding_model=rag_service.embedding_model,
        chroma_client=rag_service.chroma_client,
    )

    rag_service.reload()


# ---------------------------------------------------------
# Shop directory
# ---------------------------------------------------------

@app.get("/shops")
def shop_list(
    search: str = "",
    city: str = "",
):

    shops = shop_db.list_shops()

    if search:

        needle = search.strip().lower()

        shops = [
            shop
            for shop in shops
            if needle in (
                f"{shop.get('name', '')} "
                f"{shop.get('city', '')} "
                f"{shop.get('address', '')} "
                f"{shop.get('category', '')}"
            ).lower()
        ]

    if city:

        needle = city.strip().lower()

        shops = [
            shop
            for shop in shops
            if needle in (shop.get("city") or "").lower()
        ]

    return {
        "count": len(shops),
        "shops": shops,
    }


# ---------------------------------------------------------
# Add a shop (admin)
# ---------------------------------------------------------

@app.post(
    "/shops",
    response_model=ShopResponse,
)
def shop_add(
    request: AddShopRequest,
):

    data = request.dict()

    data["name"] = data.get("name", "").strip()

    if not data["name"]:
        raise HTTPException(
            status_code=400,
            detail="Shop name is required.",
        )

    with _shop_lock:

        shop = shop_db.add_shop(data)

        shop_db.export_catalog()

        _reindex()

    return shop


# ---------------------------------------------------------
# Get one shop
# ---------------------------------------------------------

@app.get(
    "/shops/{shop_id}",
    response_model=ShopResponse,
)
def shop_get(
    shop_id: str,
):

    shop = shop_db.get_shop(shop_id)

    if shop is None:

        raise HTTPException(
            status_code=404,
            detail=f"Shop '{shop_id}' not found.",
        )

    return shop


# ---------------------------------------------------------
# Delete a shop (admin)
# ---------------------------------------------------------

@app.delete("/shops/{shop_id}")
def shop_delete(
    shop_id: str,
):

    with _shop_lock:

        deleted = shop_db.delete_shop(shop_id)

        if not deleted:

            raise HTTPException(
                status_code=404,
                detail=f"Shop '{shop_id}' not found.",
            )

        shop_db.export_catalog()

        _reindex()

    return {
        "ok": True,
        "id": shop_id,
    }


# ---------------------------------------------------------
# List a shop's products
# ---------------------------------------------------------

@app.get("/shops/{shop_id}/products")
def shop_products(
    shop_id: str,
):

    shop = shop_db.get_shop(shop_id)

    if shop is None:

        raise HTTPException(
            status_code=404,
            detail=f"Shop '{shop_id}' not found.",
        )

    products = shop_db.list_products(shop_id)

    return {
        "shop_id": shop_id,
        "shop_name": shop.get("name"),
        "count": len(products),
        "products": products,
    }


# ---------------------------------------------------------
# Upload a product dataset (JSON or CSV) for a shop
# ---------------------------------------------------------

@app.post("/shops/{shop_id}/upload")
async def shop_upload_dataset(
    shop_id: str,
    file: UploadFile = File(...),
):

    shop = shop_db.get_shop(shop_id)

    if shop is None:

        raise HTTPException(
            status_code=404,
            detail=f"Shop '{shop_id}' not found.",
        )

    content = await file.read()

    filename = (file.filename or "").lower()

    try:

        if filename.endswith(".csv"):

            raw_rows = list(
                csv.DictReader(
                    io.StringIO(
                        content.decode("utf-8-sig")
                    )
                )
            )

        else:

            data = json.loads(
                content.decode("utf-8")
            )

            if isinstance(data, dict):
                raw_rows = data.get("products", [])
            else:
                raw_rows = data

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not parse upload. "
                "Provide a JSON array of products "
                "or a CSV file."
            ),
        )

    products = []

    errors = []

    for index, row in enumerate(raw_rows):

        if not isinstance(row, dict):

            errors.append(
                {
                    "row": index + 1,
                    "error": "Row is not an object.",
                }
            )

            continue

        try:

            product = _normalize_product(row)

            products.append(product)

        except HTTPException as error:

            errors.append(
                {
                    "row": index + 1,
                    "error": str(error.detail),
                }
            )

    if not products:

        raise HTTPException(
            status_code=400,
            detail=(
                "No valid products found in the upload. "
                "Check the name/category/price columns."
            ),
        )

    with _shop_lock:

        result = shop_db.bulk_add(shop_id, products)

        shop_db.export_catalog()

        _reindex()

    return {
        "shop_id": shop_id,
        "added": len(result["added"]),
        "skipped": len(result["skipped"]),
        "errors": errors[:20],
        "products": result["added"],
    }


# ---------------------------------------------------------
# Delete a product from a shop
# ---------------------------------------------------------

@app.delete("/shops/{shop_id}/products/{product_id}")
def shop_delete_product(
    shop_id: str,
    product_id: str,
):

    with _shop_lock:

        deleted = shop_db.delete_product(
            shop_id,
            product_id,
        )

        if not deleted:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product '{product_id}' not found "
                    f"in shop '{shop_id}'."
                ),
            )

        shop_db.export_catalog()

        _reindex()

    return {
        "ok": True,
        "shop_id": shop_id,
        "id": product_id,
    }


# =========================================================
# GLOBAL PRODUCT SEARCH (cross-shop, no LLM)
# =========================================================

@app.get("/products/search")
def product_search(
    q: str,
):

    query = (q or "").strip()

    if not query:

        return {
            "count": 0,
            "results": [],
        }

    results = rag_service.search_products(query)

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }
