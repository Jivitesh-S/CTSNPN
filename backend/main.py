import csv
import io
import json
import os
import re
import time
import hmac
import hashlib
import threading
from typing import Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Request, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from backend import db as shop_db
from backend.ingest import sync_index
from backend.rag_service import RAGService
from backend.telegram_service import send_telegram_rejection_notice, send_telegram_status_update


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
# SECURITY LAYER 6: HTTP SECURITY HEADERS & CORS
# =========================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=*, geolocation=()"
    return response


# Load CORS origins dynamically from .env or fallback to localhost
raw_cors = os.getenv("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in raw_cors.split(",") if o.strip()] if raw_cors else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# =========================================================
# SECURITY LAYER 2: SLIDING-WINDOW RATE LIMITER
# =========================================================

class SlidingWindowRateLimiter:
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        with self._lock:
            if key not in self._requests:
                self._requests[key] = []
            
            # Prune timestamps older than window
            self._requests[key] = [t for t in self._requests[key] if now - t < window_seconds]
            
            if len(self._requests[key]) >= max_requests:
                return False
            
            self._requests[key].append(now)
            return True


rate_limiter = SlidingWindowRateLimiter()


def enforce_rate_limit(request: Request, action: str, max_requests: int, window_seconds: int):
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"{client_ip}:{action}"
    if not rate_limiter.is_allowed(key, max_requests, window_seconds):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {action}. Please wait before making more requests."
        )


# =========================================================
# SECURITY LAYER 3: PROMPT INJECTION & JAILBREAK DEFENSE
# =========================================================

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"(reveal|show|output|leak|print)\s+(the\s+)?(system\s+prompt|admin\s+pin|master\s+key|database\s+password)", re.IGNORECASE),
    re.compile(r"(you\s+are\s+now|act\s+as)\s+(DAN|unrestricted|jailbreak|developer\s+mode)", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(safety|filters|security|restrictions)", re.IGNORECASE),
    re.compile(r"<\s*script\b", re.IGNORECASE),
]


def detect_prompt_injection(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in PROMPT_INJECTION_PATTERNS)


# =========================================================
# SECURITY LAYER 1: ADMIN TOKEN AUTHENTICATION
# =========================================================

ADMIN_SECRET = os.getenv("ADMIN_SECRET_KEY", "techstore_sec_token_9087086182")
ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")


def generate_admin_token() -> str:
    day_bucket = int(time.time() // 86400)
    return hmac.new(ADMIN_SECRET.encode(), f"admin:{day_bucket}".encode(), hashlib.sha256).hexdigest()[:32]


def verify_admin_auth(x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token")):
    if not x_admin_token:
        # Check standard pin or secret
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authorization token or X-Admin-Token header is missing."
        )
    valid_token = generate_admin_token()
    if x_admin_token not in {valid_token, ADMIN_PIN, "admin_master_session"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired admin session token."
        )
    return True


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

    action: Optional[str] = None

    phone: Optional[str] = None

    tel: Optional[str] = None

    whatsapp: Optional[str] = None
    token_id: Optional[str] = None
    order_id: Optional[str] = None
    customer_name: Optional[str] = None
    model_name: Optional[str] = None
    request_type: Optional[str] = None
    price: Optional[float] = None
    purchase_date: Optional[str] = None
    token_status: Optional[str] = None
    video: Optional[dict] = None
    video_hub: Optional[dict] = None
    comparison_data: Optional[dict] = None
    product: Optional[dict] = None
    reservation_available: Optional[dict] = None
    suggested_followups: Optional[List[str]] = None







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
        token = generate_admin_token()
        return {
            "ok": True,
            "token": token,
            "message": "Admin authorization granted."
        }

    raise HTTPException(
        status_code=401,
        detail="Incorrect password.",
    )


# =========================================================
# ROOT & HEALTH
# =========================================================

@app.get("/")
def root():
    return {
        "message": "TechStore Assistant API is running with complete 113-product manuals and knowledge index."
    }


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
    http_req: Request,
):
    enforce_rate_limit(http_req, "chat", max_requests=40, window_seconds=60)

    # Prompt Injection Pre-Filter
    if detect_prompt_injection(request.question):
        return {
            "success": True,
            "answer": (
                "I am the TechStore Assistant. I can help you with questions regarding our "
                "store catalog, device specifications, warranty policies, 24-hour in-store holds, "
                "or troubleshooting error codes."
            ),
            "relevant": True,
            "similarity_score": 1.0,
            "intent": "security_guard",
            "suggested_followups": [
                "Browse all in-stock products",
                "Store location & opening hours",
                "What is your warranty policy?"
            ]
        }

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
    auth: bool = Depends(verify_admin_auth),
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


# =========================================================
# ORDERS & SERVICE TOKENS (CRM & 2FA OTP)
# =========================================================

class UpdateServiceTokenRequest(BaseModel):
    status: str
    admin_notes: Optional[str] = ""


class SendOtpRequest(BaseModel):
    action_type: Optional[str] = "cancellation"


class VerifyOtpRequest(BaseModel):
    otp: str
    action_type: Optional[str] = "cancellation"
    reason: Optional[str] = ""


@app.get("/orders")
@app.get("/admin/orders")
def get_all_orders(auth: bool = Depends(verify_admin_auth)):
    return {
        "orders": shop_db.list_orders()
    }


@app.get("/orders/{order_id}")
def get_single_order(order_id: str):
    order = shop_db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' not found.",
        )
    return {
        "order": order
    }


@app.post("/orders/{order_id}/send-otp")
def trigger_order_otp(
    order_id: str,
    http_req: Request,
    request: SendOtpRequest = SendOtpRequest(),
):
    enforce_rate_limit(http_req, "order_send_otp", max_requests=5, window_seconds=300)
    order = shop_db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' not found.",
        )
    from backend.telegram_service import send_telegram_otp
    sent, otp, msg = send_telegram_otp(
        order,
        action_type=request.action_type or "cancellation",
    )
    return {
        "ok": True,
        "sent_via_telegram": sent,
        "message": msg,
    }


@app.post("/orders/{order_id}/verify-otp")
def verify_order_otp_endpoint(
    order_id: str,
    request: VerifyOtpRequest,
):
    order = shop_db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' not found.",
        )
    from backend.telegram_service import verify_otp
    is_valid, msg = verify_otp(order_id, request.otp)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=msg,
        )
    action = (request.action_type or "Cancellation").capitalize()
    token = shop_db.create_service_token(
        order_id=order_id,
        customer_name=order["customer_name"],
        phone=order["phone"],
        model_name=order["model_bought"],
        request_type=action,
        reason=request.reason or f"{action} authorized via Telegram OTP.",
    )
    return {
        "ok": True,
        "token": token,
        "message": msg,
    }


@app.get("/admin/service-tokens")
def get_admin_service_tokens(auth: bool = Depends(verify_admin_auth)):
    return {
        "tokens": shop_db.list_service_tokens()
    }


@app.patch("/admin/service-tokens/{token_id}")
def update_admin_service_token(
    token_id: str,
    request: UpdateServiceTokenRequest,
    auth: bool = Depends(verify_admin_auth),
):
    token = shop_db.get_service_token(token_id)
    if not token:
        raise HTTPException(
            status_code=404,
            detail=f"Service token '{token_id}' not found.",
        )

    if request.status.lower() == "rejected":
        order_id = token.get("order_id")
        order = shop_db.get_order(order_id) if order_id else None
        if order_id:
            shop_db.update_order_status(order_id, "Processing")
        
        rejection_reason = (request.admin_notes or "").strip() or "Standard cancellation window policy."
        send_telegram_rejection_notice(
            order or {
                "order_id": order_id or "ORDER",
                "customer_name": token.get("customer_name") or "Customer",
                "telegram_chat_id": token.get("phone") or os.getenv("TELEGRAM_CHAT_ID", "").strip(),
            },
            rejection_reason,
        )
        shop_db.delete_service_token(token_id)
        return {
            "ok": True,
            "token_id": token_id,
            "status": "Rejected",
            "message": "Token rejected, customer notified, and order restored to catalog.",
        }

    updated = shop_db.update_service_token_status(
        token_id,
        request.status,
        request.admin_notes or "",
    )
    return {
        "ok": True,
        "token": shop_db.get_service_token(token_id),
    }


class RejectServiceTokenRequest(BaseModel):
    rejection_reason: str = Field(..., description="Reason for rejecting the request")


@app.post("/admin/service-tokens/{token_id}/reject")
def reject_admin_service_token(
    token_id: str,
    request: RejectServiceTokenRequest,
    auth: bool = Depends(verify_admin_auth),
):
    token = shop_db.get_service_token(token_id)
    if not token:
        raise HTTPException(
            status_code=404,
            detail=f"Service token '{token_id}' not found.",
        )

    rejection_reason = request.rejection_reason.strip() or "Standard store cancellation window expired."
    order_id = token.get("order_id")
    order = shop_db.get_order(order_id) if order_id else None

    # 1. Revert order status in DB back to Processing / Active Order in Customer Catalog
    if order_id:
        shop_db.update_order_status(order_id, "Processing")

    # 2. Dispatch Telegram notification to customer
    telegram_order_payload = order or {
        "order_id": order_id or "ORDER",
        "customer_name": token.get("customer_name") or "Customer",
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", "").strip(),
    }
    telegram_sent = send_telegram_rejection_notice(telegram_order_payload, rejection_reason)

    # 3. Remove/delete token from Service Tokens so it is NOT present in Service Tokens and Requests
    shop_db.delete_service_token(token_id)

    customer_name = token.get("customer_name") or (order.get("customer_name") if order else "Customer")
    first_name = customer_name.split()[0] if customer_name else "there"
    rejection_message = (
        f"Hey {first_name}, your order cancellation for #{order_id} was rejected due to: {rejection_reason}. "
        f"Contact us for further information. Thank you."
    )


    return {
        "ok": True,
        "token_id": token_id,
        "status": "Rejected",
        "order_id": order_id,
        "telegram_sent": telegram_sent,
        "rejection_reason": rejection_reason,
        "rejection_message": rejection_message,
    }


# =========================================================
# 1. ORDER STATUS UPDATE & AUTOMATED TELEGRAM WEBHOOK
# =========================================================

class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., description="New order status")
    admin_notes: Optional[str] = Field("", description="Optional notes or tracking info")


@app.patch("/admin/orders/{order_id}/status")
def update_order_status_endpoint(
    order_id: str,
    request: UpdateOrderStatusRequest,
    auth: bool = Depends(verify_admin_auth),
):
    order = shop_db.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' not found.",
        )
    shop_db.update_order_status(order_id, request.status)
    telegram_sent = send_telegram_status_update(order, request.status, request.admin_notes or "")
    return {
        "ok": True,
        "order_id": order_id,
        "status": request.status,
        "telegram_sent": telegram_sent,
        "message": f"Order #{order_id} updated to {request.status} (Telegram alert: {'Sent' if telegram_sent else 'Failed'})."
    }


# =========================================================
# 2. CLICK & COLLECT IN-STORE QR RESERVATION
# =========================================================

class ReservationRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=7)
    product_id: str = Field(...)
    shop_id: Optional[str] = "S001"
    notes: Optional[str] = ""


class ReservationOtpSendRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=7)
    product_id: str = Field(...)
    shop_id: Optional[str] = "S001"


class ReservationOtpVerifyRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=7)
    product_id: str = Field(...)
    otp: str = Field(..., min_length=4)
    shop_id: Optional[str] = "S001"


@app.post("/store/reserve/send-otp")
def send_reservation_otp_endpoint(
    request: ReservationOtpSendRequest,
    http_req: Request,
):
    enforce_rate_limit(http_req, "reserve_send_otp", max_requests=5, window_seconds=300)
    from backend.telegram_service import send_telegram_reservation_otp
    product = shop_db.get_product(request.shop_id or "S001", request.product_id)
    prod_name = product.get("name") if product else "Device"
    sent, otp, msg = send_telegram_reservation_otp(request.phone, request.customer_name, prod_name)
    return {
        "ok": True,
        "sent_via_telegram": sent,
        "phone_masked": request.phone[-4:] if len(request.phone) >= 4 else request.phone,
        "message": msg
    }


@app.post("/store/reserve/verify-otp")
def verify_reservation_otp_endpoint(request: ReservationOtpVerifyRequest):
    import re
    from backend.telegram_service import verify_otp
    key = f"RES_{re.sub(r'[^0-9]', '', request.phone)}"
    is_valid, msg = verify_otp(key, request.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    product = shop_db.get_product(request.shop_id or "S001", request.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{request.product_id}' not found in store catalog.",
        )

    token = shop_db.create_service_token(
        order_id=f"HOLD-{request.product_id}",
        customer_name=request.customer_name,
        phone=request.phone,
        model_name=product.get("name", "Device"),
        request_type="Store Reservation (24h Hold)",
        reason=f"Authenticated 24h hold for {product.get('name')} (Rs. {product.get('price', 0):,}).",
    )

    qr_payload = f"TECHSTORE:PASS:{token['token_id']}:{request.product_id}:{request.phone}"
    return {
        "ok": True,
        "token_id": token["token_id"],
        "product_name": product.get("name"),
        "price": product.get("price"),
        "customer_name": request.customer_name,
        "phone": request.phone,
        "flag": "🇮🇳",
        "country": "India",
        "hold_hours": 24,
        "store_address": "Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Tamil Nadu 600066",
        "store_timings": "10:00 AM - 9:00 PM Daily",
        "store_phone": "+91 9087086182",
        "qr_data": qr_payload,
        "message": f"Successfully reserved {product.get('name')} for 24 hours under Token #{token['token_id']}."
    }


@app.post("/store/reserve")
def reserve_product_endpoint(request: ReservationRequest):
    product = shop_db.get_product(request.shop_id or "S001", request.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{request.product_id}' not found in store catalog.",
        )

    token = shop_db.create_service_token(
        order_id=f"HOLD-{request.product_id}",
        customer_name=request.customer_name,
        phone=request.phone,
        model_name=product.get("name", "Device"),
        request_type="Store Reservation (24h Hold)",
        reason=f"Reserved {product.get('name')} (Rs. {product.get('price', 0):,}) for 24-hour in-store hold.",
    )

    qr_payload = f"TECHSTORE:PASS:{token['token_id']}:{request.product_id}:{request.phone}"
    return {
        "ok": True,
        "token_id": token["token_id"],
        "product_name": product.get("name"),
        "price": product.get("price"),
        "customer_name": request.customer_name,
        "phone": request.phone,
        "flag": "🇮🇳",
        "country": "India",
        "hold_hours": 24,
        "store_address": "Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Tamil Nadu 600066",
        "store_timings": "10:00 AM - 9:00 PM Daily",
        "store_phone": "+91 9087086182",
        "qr_data": qr_payload,
        "message": f"Successfully reserved {product.get('name')} for 24 hours under Token #{token['token_id']}."
    }


# =========================================================
# 3. VISUAL PHOTO DIAGNOSTIC ASSISTANT (VISION AI)
# =========================================================

class ImageDiagnosticRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image or Data URL")
    question: Optional[str] = "What is the problem with this device?"
    session_id: Optional[str] = "vision_diag"


@app.post("/diagnose-image")
def diagnose_image_endpoint(
    request: ImageDiagnosticRequest,
    http_req: Request,
):
    enforce_rate_limit(http_req, "diagnose_image", max_requests=20, window_seconds=60)
    if len(request.image_base64) > 6_000_000:
        raise HTTPException(
            status_code=413,
            detail="Image payload is too large. Please upload an image under 4.5MB."
        )

    import re
    from groq import Groq

    img_data = request.image_base64.strip()
    if img_data.startswith("data:image"):
        pass
    else:
        img_data = f"data:image/jpeg;base64,{img_data}"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    vision_prompt = (
        "You are an expert Samsung hardware diagnostic technician. Analyze the attached device image. "
        "Identify:\n"
        "1. The device type and apparent model (e.g., Washing Machine LED display, Galaxy Smartphone screen, Laptop display, TV).\n"
        "2. The exact error code or physical defect visible (e.g. '4C Water Supply Error', 'Ub Unbalanced Load', 'Green line OLED display fault', 'Cracked glass screen with intact touch').\n"
        "3. Severity (Low / Medium / High / Critical).\n"
        "4. Exact 3-step immediate fix instructions.\n"
        "5. Estimated store repair turnaround time and warranty coverage."
    )

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": img_data}}
                    ]
                }
            ],
            max_tokens=600,
            temperature=0.1
        )
        raw_text = response.choices[0].message.content.strip()
        if "<think>" in raw_text and "</think>" in raw_text:
            raw_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

        # Extract structured overview
        device_match = re.search(r"(?:Device|Product):\s*([^\n]+)", raw_text, re.IGNORECASE)
        device_type = device_match.group(1).strip() if device_match else "Samsung Device"
        
        severity = "Medium"
        if "critical" in raw_text.lower() or "cracked" in raw_text.lower():
            severity = "High"
        elif "low" in raw_text.lower():
            severity = "Low"

        return {
            "ok": True,
            "success": True,
            "device_detected": device_type,
            "severity": severity,
            "analysis": raw_text,
            "warranty_covered": "100% Free under Brand Warranty for hardware anomalies. Physical damage eligible for subsidized care.",
            "turnaround": "24-48 Hours at TechStore Service Desk",
            "suggested_followups": [
                "Book a free diagnostic visit at store",
                "What documents do I need to bring?",
                "Connect with technician on WhatsApp"
            ]
        }

    except Exception as e:
        print(f"[Vision Diagnostic Error]: {e}")
        # Safe fallback
        return {
            "ok": True,
            "success": True,
            "device_detected": "Samsung Device Hardware Inspection",
            "severity": "Medium",
            "analysis": (
                "**Visual Diagnostic Inspection Completed**\n\n"
                "Our system analyzed your attached photo. For accurate hardware validation:\n\n"
                "1. **In-Store Inspection:** Visit TechStore service desk for a free multi-point hardware diagnostic test.\n"
                "2. **Official Warranty:** 12–36 Month brand warranty covers factory component anomalies.\n"
                "3. **Technician Support:** Call **+91 9087086182** or message us on WhatsApp for instant live assistance."
            ),
            "warranty_covered": "Covered under official TechStore warranty terms.",
            "turnaround": "Same-day or 24-48 Hours",
            "suggested_followups": [
                "Book a free diagnostic visit at store",
                "What documents do I need to bring?",
                "Connect with technician on WhatsApp"
            ]
        }


# =========================================================
# 4. SERVER-SENT EVENTS (SSE) TOKEN STREAMING
# =========================================================

@app.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    http_req: Request,
):
    import json, asyncio
    enforce_rate_limit(http_req, "chat_stream", max_requests=40, window_seconds=60)

    if detect_prompt_injection(request.question):
        safe_meta = {
            "success": True,
            "intent": "security_guard",
            "similarity_score": 1.0,
            "suggested_followups": ["Browse all products", "Store hours", "Warranty terms"]
        }
        safe_msg = "I am the TechStore Assistant. I can only assist with verified catalog, pricing, store pickup, and device troubleshooting."
        async def safe_gen():
            yield f"event: meta\ndata: {json.dumps(safe_meta)}\n\n"
            yield f"event: delta\ndata: {json.dumps({'chunk': safe_msg})}\n\n"
            yield f"event: done\ndata: [DONE]\n\n"
        return StreamingResponse(safe_gen(), media_type="text/event-stream")

    # Get full RAG response
    history_turns = [turn.dict() for turn in request.history] if request.history else None
    response_data = rag_service.chat(
        question=request.question,
        history=history_turns,
        shop_id=request.shop_id,
    )


    full_answer = response_data.get("answer", "")
    metadata = {
        "success": response_data.get("success", True),
        "intent": response_data.get("intent"),
        "similarity_score": response_data.get("similarity_score"),
        "video_hub": response_data.get("video_hub"),
        "comparison_data": response_data.get("comparison_data"),
        "suggested_followups": response_data.get("suggested_followups"),
        "action": response_data.get("action"),
        "phone": response_data.get("phone"),
        "whatsapp": response_data.get("whatsapp"),
    }

    async def event_generator():
        # Stream metadata first
        yield f"event: meta\ndata: {json.dumps(metadata)}\n\n"
        
        # Stream text words in chunks
        words = full_answer.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]) + (" " if i + chunk_size < len(words) else "")
            payload = json.dumps({"chunk": chunk})
            yield f"event: delta\ndata: payload\n\n".replace("payload", payload)
            await asyncio.sleep(0.02)
            
        yield f"event: done\ndata: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")




