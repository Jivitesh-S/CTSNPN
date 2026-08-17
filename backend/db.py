import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path


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

    _conn.commit()


# ============================================================
# SEED: TechStore shop + its existing products (first run)
# ============================================================

def _seed():

    count = _conn.execute(
        "SELECT COUNT(*) FROM shops"
    ).fetchone()[0]

    if count > 0:
        return

    techstore = {
        "id": "S001",
        "name": "TechStore",
        "description": (
            "TechStore is a gadget shop selling smartphones, "
            "laptops and accessories."
        ),
        "category": "electronics",
        "address": "123, Tech Market Road, City Center",
        "city": "City Center",
        "pincode": "560001",
        "phone": "+91 9087086182",
        "email": "",
        "timings": "10:00 AM - 9:00 PM, all days",
    }

    _insert_shop_raw(techstore)

    if CATALOG_FILE.exists():

        with open(CATALOG_FILE, "r", encoding="utf-8") as file:
            products = json.load(file)

        for product in products:
            product = dict(product)
            product["shop_id"] = "S001"
            _insert_product_raw(product)

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
