import json
import os
import pickle
import re
from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import torch

from backend import db as shop_db


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SHOP_DATA_DIR = PROJECT_ROOT / "data" / "shop"

CATALOG_FILE = SHOP_DATA_DIR / "catalog.json"

FAQ_FILE = SHOP_DATA_DIR / "faq.json"

POLICIES_FILE = SHOP_DATA_DIR / "policies.txt"

TROUBLESHOOTING_FILE = SHOP_DATA_DIR / "troubleshooting_guide.txt"

RECOMMENDATIONS_FILE = SHOP_DATA_DIR / "recommendations.txt"

SUPPORT_CLEAN_FILE = SHOP_DATA_DIR / "support_clean.json"

PRODUCT_DOCS_DIR = SHOP_DATA_DIR / "product_docs"

CHROMA_DIR = SHOP_DATA_DIR / "chroma_db"

BM25_INDEX_FILE = SHOP_DATA_DIR / "bm25_index.pkl"


# ============================================================
# RAG SETTINGS
# ============================================================

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150

COLLECTION_NAME = "gadget_shop_knowledge"

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "BAAI/bge-small-en-v1.5",
)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text: str) -> str:

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"\.{3,}", "...", text)

    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
        "",
        text,
    )

    return text.strip()


def create_chunks(
    text: str,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):

    text = normalize_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def tokenize(text: str) -> list:

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return text.split()


# ============================================================
# FORMAT A PRODUCT AS KNOWLEDGE TEXT
# ============================================================

def format_product(product: dict) -> str:

    parts = []

    parts.append(f"Product: {product.get('name', 'Unknown')}")

    parts.append(f"Brand: {product.get('brand', 'Unknown')}")

    parts.append(f"Category: {product.get('category', 'Unknown')}")

    parts.append(f"Price: Rs. {product.get('price', 0):,}")

    parts.append(f"Stock status: {product.get('stock', 'Unknown')}")

    parts.append(
        f"Warranty: {product.get('warranty_months', 0)} months"
    )

    description = product.get("description", "")

    if description:
        parts.append(f"Description: {description}")

    specs = product.get("specs", {})

    if specs:
        spec_parts = [
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in specs.items()
        ]
        parts.append("Specifications: " + "; ".join(spec_parts))

    return "\n".join(parts)


# ============================================================
# SPLIT MARKDOWN-STYLE TEXT INTO SECTIONS
# ============================================================

def split_sections(text: str, level_prefix: str):

    sections = []

    current_title = "General"
    current_lines = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if line.startswith(level_prefix):

            if current_lines:
                sections.append(
                    (current_title, " ".join(current_lines))
                )

            current_title = line.lstrip("#").strip()
            current_lines = []

        else:

            if line:
                current_lines.append(line)

    if current_lines:
        sections.append(
            (current_title, " ".join(current_lines))
        )

    return sections


# ============================================================
# BUILD ALL RECORDS (with stable ids)
# ============================================================

def build_records() -> list:

    records = []

    # --------------------------------------------------------
    # 1. Product catalog (stable id: prod_<shop>_<id>)
    # --------------------------------------------------------

    shops = {
        shop["id"]: shop
        for shop in shop_db.list_shops()
    }

    if CATALOG_FILE.exists():

        with open(CATALOG_FILE, "r", encoding="utf-8") as file:
            products = json.load(file)

        for product in products:

            shop_id = str(product.get("shop_id", ""))
            product_id = str(product.get("id", ""))

            shop = shops.get(shop_id, {})

            records.append(
                {
                    "id": f"prod_{shop_id}_{product_id}",
                    "text": format_product(product),
                    "metadata": {
                        "kind": "product",
                        "product_id": product_id,
                        "shop_id": shop_id,
                        "shop_name": shop.get("name", shop_id),
                        "name": product.get("name", ""),
                        "product_name": product.get("name", ""),
                        "brand": product.get("brand", ""),
                        "category": product.get("category", ""),
                        "price": product.get("price", 0),
                        "stock": product.get("stock", ""),
                    },
                    "keywords": (
                        f"{product.get('name', '')} "
                        f"{product.get('brand', '')} "
                        f"{product.get('category', '')} "
                        f"price stock buy {product.get('name', '')}"
                    ),
                }
            )

        print(f"Products: {len(products)}")

    # --------------------------------------------------------
    # 1b. Shop basic details (stable id: shopinfo_<shop_id>)
    # --------------------------------------------------------

    for shop_id, shop in shops.items():

        info_parts = [f"Shop: {shop.get('name', '')}"]

        if shop.get("category"):
            info_parts.append(f"Category: {shop.get('category')}")

        if shop.get("address"):
            info_parts.append(f"Address: {shop.get('address')}")

        if shop.get("city"):
            info_parts.append(f"City: {shop.get('city')}")

        if shop.get("pincode"):
            info_parts.append(f"Pincode: {shop.get('pincode')}")

        if shop.get("timings"):
            info_parts.append(f"Timings: {shop.get('timings')}")

        if shop.get("phone"):
            info_parts.append(f"Phone: {shop.get('phone')}")

        if shop.get("email"):
            info_parts.append(f"Email: {shop.get('email')}")

        records.append(
            {
                "id": f"shopinfo_{shop_id}",
                "text": "\n".join(info_parts),
                "metadata": {
                    "kind": "shop",
                    "shop_id": shop_id,
                    "shop_name": shop.get("name", shop_id),
                },
                "keywords": (
                    f"{shop.get('name', '')} {shop.get('category', '')} "
                    f"{shop.get('city', '')} {shop.get('address', '')} "
                    f"{shop.get('timings', '')} shop timings address "
                    f"phone location hours open close"
                ),
            }
        )

    print(f"Shops: {len(shops)}")

    # --------------------------------------------------------
    # 2. FAQs (stable id: faq_<index>)
    # --------------------------------------------------------

    if FAQ_FILE.exists():

        with open(FAQ_FILE, "r", encoding="utf-8") as file:
            faqs = json.load(file)

        for index, faq in enumerate(faqs):

            question = faq.get("question", "")
            answer = faq.get("answer", "")

            records.append(
                {
                    "id": f"faq_{index}",
                    "text": (
                        f"Question: {question}\n"
                        f"Answer: {answer}"
                    ),
                    "metadata": {
                        "kind": "faq",
                        "question": question,
                    },
                    "keywords": question,
                }
            )

        print(f"FAQs: {len(faqs)}")

    # --------------------------------------------------------
    # 3. Policies (stable id: policy_<index>)
    # --------------------------------------------------------

    if POLICIES_FILE.exists():

        policy_text = POLICIES_FILE.read_text(encoding="utf-8")

        sections = split_sections(policy_text, "##")

        index = 0

        for title, content in sections:

            chunks = create_chunks(content)

            for chunk in chunks:

                records.append(
                    {
                        "id": f"policy_{index}",
                        "text": f"Policy: {title}\n{chunk}",
                        "metadata": {
                            "kind": "policy",
                            "policy_title": title,
                        },
                        "keywords": (
                            f"{title} policy warranty return "
                            f"refund delivery payment exchange"
                        ),
                    }
                )

                index += 1

        print(f"Policies: {len(sections)}")

    # --------------------------------------------------------
    # 4. Troubleshooting guide (stable id: troub_<index>)
    # --------------------------------------------------------

    if TROUBLESHOOTING_FILE.exists():

        guide_text = TROUBLESHOOTING_FILE.read_text(
            encoding="utf-8"
        )

        sections = split_sections(guide_text, "##")

        index = 0

        for title, content in sections:

            chunks = create_chunks(content)

            for chunk in chunks:

                records.append(
                    {
                        "id": f"troub_{index}",
                        "text": (
                            f"Troubleshooting: {title}\n{chunk}"
                        ),
                        "metadata": {
                            "kind": "troubleshooting",
                            "issue": title,
                        },
                        "keywords": (
                            f"fix repair problem issue "
                            f"not working {title}"
                        ),
                    }
                )

                index += 1

        print(f"Troubleshooting issues: {len(sections)}")

    # --------------------------------------------------------
    # 4b. Per-product support docs (stable id: pdoc_<pid>_<i>)
    # --------------------------------------------------------

    if PRODUCT_DOCS_DIR.exists():

        products_by_id = {}

        if CATALOG_FILE.exists():

            with open(
                CATALOG_FILE,
                "r",
                encoding="utf-8",
            ) as file:

                for product in json.load(file):

                    products_by_id[
                        str(product.get("id", ""))
                    ] = product

        doc_files = sorted(PRODUCT_DOCS_DIR.glob("*.txt"))

        doc_chunk_count = 0

        for doc_file in doc_files:

            product_id = doc_file.stem

            doc_text = doc_file.read_text(encoding="utf-8")

            if not doc_text.strip():
                continue

            product = products_by_id.get(product_id, {})

            product_name = product.get("name", product_id)

            chunks = create_chunks(doc_text)

            for index, chunk in enumerate(chunks):

                records.append(
                    {
                        "id": f"pdoc_{product_id}_{index}",
                        "text": (
                            f"Product: {product_name} "
                            f"(ID: {product_id})\n{chunk}"
                        ),
                        "metadata": {
                            "kind": "product_doc",
                            "product_id": product_id,
                            "product_name": product_name,
                            "shop_id": product.get(
                                "shop_id", "S001"
                            ),
                        },
                        "keywords": (
                            f"{product_name} {product_id} "
                            f"fix repair problem issue solution "
                            f"troubleshooting steps how to"
                        ),
                    }
                )

                doc_chunk_count += 1

        print(
            f"Product docs: {len(doc_files)} files, "
            f"{doc_chunk_count} chunks"
        )

    # --------------------------------------------------------
    # 5. Recommendations (stable id: rec_<index>)
    # --------------------------------------------------------

    if RECOMMENDATIONS_FILE.exists():

        rec_text = RECOMMENDATIONS_FILE.read_text(
            encoding="utf-8"
        )

        sections = split_sections(rec_text, "##")

        index = 0

        for title, content in sections:

            chunks = create_chunks(content)

            for chunk in chunks:

                records.append(
                    {
                        "id": f"rec_{index}",
                        "text": (
                            f"Recommendation: {title}\n{chunk}"
                        ),
                        "metadata": {
                            "kind": "recommendation",
                            "guide": title,
                        },
                        "keywords": (
                            f"best recommend choose buy guide "
                            f"under budget {title}"
                        ),
                    }
                )

                index += 1

        print(f"Recommendation guides: {len(sections)}")

    # --------------------------------------------------------
    # 6. Customer support dataset (stable id: sup_<index>)
    # --------------------------------------------------------

    if SUPPORT_CLEAN_FILE.exists():

        with open(
            SUPPORT_CLEAN_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            support_records = json.load(file)

        for index, support in enumerate(support_records):

            instruction = support.get("instruction", "")

            response = support.get("response", "")

            category = support.get("category", "")

            intent = support.get("intent", "")

            records.append(
                {
                    "id": f"sup_{index}",
                    "text": (
                        f"Question: {instruction}\n"
                        f"Answer: {response}"
                    ),
                    "metadata": {
                        "kind": "support",
                        "category": category,
                        "intent": intent,
                    },
                    "keywords": (
                        f"{instruction} {category} {intent} "
                        f"support help how do i can i question"
                    ),
                }
            )

        print(
            f"Support records: {len(support_records)}"
        )

    return records


# ============================================================
# SYNC INDEX (upsert + delete stale + rebuild BM25)
# ============================================================

def sync_index(
    embedding_model=None,
    chroma_client=None,
) -> dict:

    records = build_records()

    total = len(records)

    if total == 0:
        raise RuntimeError("No knowledge data found to index.")

    # --------------------------------------------------------
    # Load embedding model (reuse already-loaded model if given)
    # --------------------------------------------------------

    if embedding_model is None:

        print("Setting torch threads...")
        torch.set_num_threads(os.cpu_count() or 8)

        print("Loading embedding model...")

        embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    # --------------------------------------------------------
    # Connect to ChromaDB
    # --------------------------------------------------------

    print("Connecting to ChromaDB...")

    if chroma_client is None:

        chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "TechStore gadget shop knowledge: "
                "catalog, policies, FAQs, troubleshooting, "
                "recommendations"
            )
        },
    )

    print(f"Existing chunks: {collection.count()}")

    # --------------------------------------------------------
    # Prepare records
    # --------------------------------------------------------

    documents = []
    metadatas = []
    ids = []

    for record in records:

        documents.append(record["text"])
        metadatas.append(record["metadata"])
        ids.append(record["id"])

    # --------------------------------------------------------
    # Create embeddings
    # --------------------------------------------------------

    print("Creating embeddings...")

    embeddings = embedding_model.encode(
        documents,
        show_progress_bar=True,
        batch_size=128,
        normalize_embeddings=True,
    )

    # --------------------------------------------------------
    # Upsert (add new / replace changed by stable id)
    # --------------------------------------------------------

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(f"Chunks upserted: {len(ids)}")

    # --------------------------------------------------------
    # Remove stale chunks (deleted products)
    # --------------------------------------------------------

    current_ids = set(ids)

    existing_ids = set(collection.get(include=[])["ids"])

    stale_ids = sorted(existing_ids - current_ids)

    if stale_ids:

        collection.delete(ids=stale_ids)

        print(f"Stale chunks removed: {len(stale_ids)}")

    # --------------------------------------------------------
    # Rebuild BM25 keyword index
    # --------------------------------------------------------

    print("Building BM25 keyword index...")

    corpus = [
        " ".join(
            tokenize(record["text"])
            + tokenize(record.get("keywords", ""))
        )
        for record in records
    ]

    bm25 = BM25Okapi(corpus)

    with open(BM25_INDEX_FILE, "wb") as file:

        pickle.dump(
            {
                "corpus": corpus,
                "texts": documents,
                "metadatas": metadatas,
                "ids": ids,
            },
            file,
        )

    print(f"BM25 index saved: {BM25_INDEX_FILE.name}")

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print(
        f"Total ChromaDB chunks: {collection.count()}"
    )

    return {
        "records": total,
        "chunks": collection.count(),
        "stale_removed": len(stale_ids),
    }
