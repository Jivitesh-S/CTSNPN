import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SHOP_DATA_DIR = PROJECT_ROOT / "data" / "shop"

DB_PATH = SHOP_DATA_DIR / "products.db"

CATALOG_FILE = SHOP_DATA_DIR / "catalog.json"


# ============================================================
# CONNECTION MANAGEMENT
# ============================================================

_lock = threading.Lock()

_conn = None


def _get_conn():

    global _conn

    if _conn is None:

        SHOP_DATA_DIR.mkdir(parents=True, exist_ok=True)

        _conn = sqlite3.connect(
            str(DB_PATH),
            check_same_thread=False,
        )

        _conn.row_factory = sqlite3.Row

        _conn.execute("PRAGMA journal_mode=WAL")

        _conn.execute("PRAGMA busy_timeout=5000")

        _migrate()

        _init_schema()

        _seed()

    return _conn


# ============================================================
# MIGRATION (drop old single-shop table shape)
# ============================================================

def _migrate():

    tables = [
        row["name"]
        for row in _conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name = 'products'"
        ).fetchall()
    ]

    if tables:

        columns = [
            row["name"]
            for row in _conn.execute(
                "PRAGMA table_info(products)"
            ).fetchall()
        ]

        if "shop_id" not in columns:

            _conn.execute("DROP TABLE products")

    _conn.commit()


# ============================================================
# SCHEMA
# ============================================================

def _init_schema():

    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS shops (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT,
            phone TEXT,
            email TEXT,
            timings TEXT,
            created_at TEXT
        )
        """
    )

    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            shop_id TEXT NOT NULL,
            id TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            price INTEGER,
            stock TEXT,
            warranty_months INTEGER,
            description TEXT,
            specs TEXT,
            created_at TEXT,
            PRIMARY KEY (shop_id, id)
        )
        """
    )

    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            telegram_chat_id TEXT,
            model_bought TEXT NOT NULL,
            product_category TEXT,
            purchase_date TEXT NOT NULL,
            price INTEGER,
            status TEXT NOT NULL,
            warranty_months INTEGER DEFAULT 12,
            return_window_days INTEGER DEFAULT 14,
            created_at TEXT
        )
        """
    )

    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS service_tokens (
            token_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            model_name TEXT NOT NULL,
            request_type TEXT NOT NULL,
            reason TEXT,
            status TEXT NOT NULL DEFAULT 'Pending Contact',
            admin_notes TEXT,
            created_at TEXT
        )
        """
    )

    _conn.commit()


# ============================================================
# SEED: TechStore shop + its existing products & dummy orders
# ============================================================

def _seed():

    count = _conn.execute(
        "SELECT COUNT(*) FROM shops"
    ).fetchone()[0]

    if count == 0:
        techstore = {
            "id": "S001",
            "name": "TechStore",
            "description": (
                "TechStore is a gadget shop selling smartphones, "
                "laptops and accessories."
            ),
            "category": "electronics",
            "address": "Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Greater Chennai, Tamil Nadu 600066",
            "city": "Chennai",
            "pincode": "600066",
            "phone": "+91 9087086182",
            "email": "",
            "timings": "10:00 AM - 9:00 PM, all days",
        }

        _insert_shop_raw(techstore)

    # Always ensure products table contains catalog.json products
    prod_count = _conn.execute("SELECT COUNT(*) FROM products WHERE shop_id = 'S001'").fetchone()[0]
    if CATALOG_FILE.exists():
        with open(CATALOG_FILE, "r", encoding="utf-8") as file:
            products = json.load(file)

        if prod_count < len(products):
            for product in products:
                product = dict(product)
                product["shop_id"] = "S001"
                _insert_product_raw(product)

    # Seed initial dummy orders if empty
    orders_count = _conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    if orders_count == 0:
        seed_orders = [
            {
                "order_id": "ORD-1001",
                "customer_name": "Rupika S",
                "phone": "+91 98765 43210",
                "email": "rupika@example.com",
                "telegram_chat_id": "8660932733",
                "model_bought": "Samsung Galaxy S24 Ultra",
                "product_category": "phone",
                "purchase_date": "2026-08-15",
                "price": 129999,
                "status": "Processing",
                "warranty_months": 12,
                "return_window_days": 14,
                "created_at": datetime.now().isoformat(),
            },
            {
                "order_id": "ORD-1002",
                "customer_name": "Aravind Kumar",
                "phone": "+91 90870 86182",
                "email": "aravind.k@example.com",
                "telegram_chat_id": "8660932733",
                "model_bought": "Samsung Galaxy Book4",
                "product_category": "laptop",
                "purchase_date": "2026-08-13",
                "price": 54990,
                "status": "Shipped",
                "warranty_months": 12,
                "return_window_days": 14,
                "created_at": datetime.now().isoformat(),
            },
            {
                "order_id": "ORD-1003",
                "customer_name": "Priya Sharma",
                "phone": "+91 98401 23456",
                "email": "priya.s@example.com",
                "telegram_chat_id": "8660932733",
                "model_bought": "Samsung Galaxy Z Flip6",
                "product_category": "phone",
                "purchase_date": "2026-08-10",
                "price": 109999,
                "status": "Delivered",
                "warranty_months": 12,
                "return_window_days": 14,
                "created_at": datetime.now().isoformat(),
            },
            {
                "order_id": "ORD-1004",
                "customer_name": "Karthik Raman",
                "phone": "+91 94440 98765",
                "email": "karthik.r@example.com",
                "telegram_chat_id": "8660932733",
                "model_bought": "Samsung Galaxy Buds3 Pro",
                "product_category": "audio",
                "purchase_date": "2026-07-01",
                "price": 19999,
                "status": "Delivered",
                "warranty_months": 12,
                "return_window_days": 7,
                "created_at": datetime.now().isoformat(),
            },
            {
                "order_id": "ORD-1005",
                "customer_name": "Sneha Patel",
                "phone": "+91 91234 56789",
                "email": "sneha.p@example.com",
                "telegram_chat_id": "8660932733",
                "model_bought": "Samsung Neo QLED 8K TV",
                "product_category": "tv",
                "purchase_date": "2026-08-16",
                "price": 319990,
                "status": "Processing",
                "warranty_months": 24,
                "return_window_days": 14,
                "created_at": datetime.now().isoformat(),
            },
        ]

        for order in seed_orders:
            _conn.execute(
                """
                INSERT OR REPLACE INTO orders (
                    order_id, customer_name, phone, email, telegram_chat_id,
                    model_bought, product_category, purchase_date, price,
                    status, warranty_months, return_window_days, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order["order_id"],
                    order["customer_name"],
                    order["phone"],
                    order["email"],
                    order["telegram_chat_id"],
                    order["model_bought"],
                    order["product_category"],
                    order["purchase_date"],
                    order["price"],
                    order["status"],
                    order["warranty_months"],
                    order["return_window_days"],
                    order["created_at"],
                ),
            )

    _conn.commit()



# ============================================================
# ROW <-> DICT HELPERS
# ============================================================

def _shop_to_dict(row) -> dict:

    return dict(row)


def _row_to_dict(row) -> dict:

    product = dict(row)

    try:
        product["specs"] = json.loads(product.get("specs") or "{}")
    except (json.JSONDecodeError, TypeError):
        product["specs"] = {}

    return product


def _insert_shop_raw(shop: dict):

    _conn.execute(
        """
        INSERT OR REPLACE INTO shops (
            id, name, description, category, address, city,
            pincode, phone, email, timings, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            shop.get("id", ""),
            shop.get("name", ""),
            shop.get("description", ""),
            shop.get("category", ""),
            shop.get("address", ""),
            shop.get("city", ""),
            shop.get("pincode", ""),
            shop.get("phone", ""),
            shop.get("email", ""),
            shop.get("timings", ""),
            shop.get("created_at", datetime.now().isoformat()),
        ),
    )


def _insert_product_raw(product: dict):

    _conn.execute(
        """
        INSERT OR REPLACE INTO products (
            shop_id, id, name, brand, category, price, stock,
            warranty_months, description, specs, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product.get("shop_id", ""),
            product.get("id", ""),
            product.get("name", ""),
            product.get("brand", ""),
            product.get("category", ""),
            product.get("price", 0),
            product.get("stock", "In stock"),
            product.get("warranty_months", 0),
            product.get("description", ""),
            json.dumps(product.get("specs", {})),
            product.get("created_at", datetime.now().isoformat()),
        ),
    )


# ============================================================
# ID GENERATION
# ============================================================

_CATEGORY_PREFIX = {
    "phone": "P",
    "laptop": "L",
    "accessory": "A",
}


def _next_shop_id() -> str:

    rows = _conn.execute(
        "SELECT id FROM shops WHERE id LIKE 'S%'"
    ).fetchall()

    max_num = 0

    for row in rows:

        suffix = row["id"][1:]

        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"S{max_num + 1:03d}"


def _next_product_id(shop_id: str, category: str) -> str:

    prefix = _CATEGORY_PREFIX.get(
        (category or "").lower(),
        "P",
    )

    rows = _conn.execute(
        "SELECT id FROM products WHERE shop_id = ? AND id LIKE ?",
        (shop_id, f"{prefix}%"),
    ).fetchall()

    max_num = 0

    for row in rows:

        suffix = row["id"][len(prefix):]

        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"{prefix}{max_num + 1:03d}"


# ============================================================
# SHOPS API
# ============================================================

def list_shops() -> list:

    conn = _get_conn()

    rows = conn.execute(
        """
        SELECT s.*,
               (SELECT COUNT(*) FROM products p
                WHERE p.shop_id = s.id) AS product_count
        FROM shops s
        ORDER BY s.name
        """
    ).fetchall()

    return [_shop_to_dict(row) for row in rows]


def get_shop(shop_id: str):

    conn = _get_conn()

    row = conn.execute(
        """
        SELECT s.*,
               (SELECT COUNT(*) FROM products p
                WHERE p.shop_id = s.id) AS product_count
        FROM shops s WHERE s.id = ?
        """,
        (shop_id,),
    ).fetchone()

    if row is None:
        return None

    return _shop_to_dict(row)


def add_shop(data: dict) -> dict:

    conn = _get_conn()

    shop = dict(data)

    shop["id"] = data.get("id") or _next_shop_id()

    _insert_shop_raw(shop)

    conn.commit()

    return get_shop(shop["id"])


def delete_shop(shop_id: str) -> bool:

    conn = _get_conn()

    cursor = conn.execute(
        "DELETE FROM shops WHERE id = ?",
        (shop_id,),
    )

    if cursor.rowcount > 0:
        conn.execute(
            "DELETE FROM products WHERE shop_id = ?",
            (shop_id,),
        )

    conn.commit()

    return cursor.rowcount > 0


# ============================================================
# PRODUCTS API (scoped by shop)
# ============================================================

def list_products(shop_id: str = None) -> list:

    conn = _get_conn()

    if shop_id:

        rows = conn.execute(
            "SELECT * FROM products WHERE shop_id = ? ORDER BY id",
            (shop_id,),
        ).fetchall()

    else:

        rows = conn.execute(
            "SELECT * FROM products ORDER BY shop_id, id"
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_product(shop_id: str, product_id: str):

    conn = _get_conn()

    row = conn.execute(
        "SELECT * FROM products WHERE shop_id = ? AND id = ?",
        (shop_id, product_id),
    ).fetchone()

    if row is None:
        return None

    return _row_to_dict(row)


def add_product(shop_id: str, data: dict) -> dict:

    conn = _get_conn()

    product = dict(data)

    product["shop_id"] = shop_id

    product["id"] = data.get("id") or _next_product_id(
        shop_id,
        data.get("category", ""),
    )

    _insert_product_raw(product)

    conn.commit()

    return get_product(shop_id, product["id"])


def bulk_add(shop_id: str, products: list) -> dict:

    conn = _get_conn()

    added = []
    skipped = []

    for product in products:

        name = (product.get("name") or "").strip()

        if not name:
            skipped.append(product)
            continue

        if product.get("id") and get_product(shop_id, product["id"]):
            skipped.append(product)
            continue

        product["shop_id"] = shop_id

        product["id"] = product.get("id") or _next_product_id(
            shop_id,
            product.get("category", ""),
        )

        _insert_product_raw(product)

        added.append(product)

    conn.commit()

    return {
        "added": added,
        "skipped": skipped,
    }


def delete_product(shop_id: str, product_id: str) -> bool:

    conn = _get_conn()

    cursor = conn.execute(
        "DELETE FROM products WHERE shop_id = ? AND id = ?",
        (shop_id, product_id),
    )

    conn.commit()

    return cursor.rowcount > 0


# ============================================================
# EXPORT TO CATALOG.JSON (all shops)
# ============================================================

def export_catalog():

    products = list_products()

    with open(CATALOG_FILE, "w", encoding="utf-8") as file:

        json.dump(
            products,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return products


# ============================================================
# ORDERS & SERVICE TOKENS
# ============================================================

def get_order(order_id: str) -> Optional[dict]:
    if not order_id:
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM orders WHERE UPPER(order_id) = UPPER(?)",
        (order_id.strip(),),
    ).fetchone()
    return dict(row) if row else None


def list_orders() -> List[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM orders ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def update_order_status(order_id: str, status: str) -> bool:
    conn = _get_conn()
    cursor = conn.execute(
        "UPDATE orders SET status = ? WHERE UPPER(order_id) = UPPER(?)",
        (status, order_id.strip()),
    )
    conn.commit()
    return cursor.rowcount > 0


def create_service_token(
    order_id: str,
    customer_name: str,
    phone: str,
    model_name: str,
    request_type: str,
    reason: str = "",
    status: str = "Pending Contact"
) -> dict:
    conn = _get_conn()
    import random
    prefix = "CAN" if "cancel" in request_type.lower() else "REP" if "replace" in request_type.lower() else "SRV"
    token_id = f"{prefix}-{random.randint(1000, 9999)}"
    now = datetime.now().isoformat()

    conn.execute(
        """
        INSERT INTO service_tokens (
            token_id, order_id, customer_name, phone, model_name,
            request_type, reason, status, admin_notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            token_id,
            order_id.upper(),
            customer_name,
            phone,
            model_name,
            request_type,
            reason or f"{request_type} request for {order_id}",
            status,
            "",
            now,
        ),
    )
    conn.commit()

    # Also update order status accordingly
    if "cancel" in request_type.lower():
        update_order_status(order_id, "Cancelled")
    elif "replace" in request_type.lower():
        update_order_status(order_id, "Replacement Requested")

    return get_service_token(token_id)


def get_service_token(token_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM service_tokens WHERE UPPER(token_id) = UPPER(?)",
        (token_id.strip(),),
    ).fetchone()
    return dict(row) if row else None


def list_service_tokens() -> List[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM service_tokens WHERE status != 'Rejected' ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def delete_service_token(token_id: str) -> bool:
    """Deletes a service token from the database."""
    conn = _get_conn()
    cursor = conn.execute(
        "DELETE FROM service_tokens WHERE UPPER(token_id) = UPPER(?)",
        (token_id.strip(),),
    )
    conn.commit()
    return cursor.rowcount > 0


def update_service_token_status(token_id: str, status: str, admin_notes: str = "") -> bool:
    conn = _get_conn()
    cursor = conn.execute(
        """
        UPDATE service_tokens 
        SET status = ?, admin_notes = COALESCE(NULLIF(?, ''), admin_notes)
        WHERE UPPER(token_id) = UPPER(?)
        """,
        (status, admin_notes, token_id.strip()),
    )
    conn.commit()

    # If rejected, restore order status back to active Processing state
    if status.lower() == "rejected":
        token = get_service_token(token_id)
        if token and token.get("order_id"):
            update_order_status(token["order_id"], "Processing")

    return cursor.rowcount > 0



