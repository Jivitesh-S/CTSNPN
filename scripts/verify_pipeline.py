import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag_service import RAGService


def verify_retrieval(svc: RAGService):
    print("=" * 70)
    print("STEP 2: VERIFY RETRIEVAL FOR NEW PRODUCTS")
    print("=" * 70)

    with open(PROJECT_ROOT / "data" / "shop" / "catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)
    by_id = {p["id"]: p["name"] for p in catalog}

    test_pids = [
        "P020", "P021", "P022", "P023", "P024", "P025", "P026", "P027", "P028",
        "A015", "A016", "A017", "A018", "A019", "A020", "A021",
        "L015", "L016", "L017"
    ]

    print("\n--- 2A: Retrieval by Exact Product Query ---")
    for pid in test_pids:
        name = by_id.get(pid, pid)
        results = svc._retrieve(f"{name} specs")
        if results:
            meta = results[0].get("metadata", {}) or {}
            pname = meta.get("product_name") or meta.get("name")
            sim = results[0].get("similarity", 0)
            score = results[0].get("score", 0)
            print(f"[{pid}] {name:35} -> Top: {str(pname):35} sim={sim:.3f}")
        else:
            print(f"[{pid}] {name:35} -> NO RESULTS")

    print("\n--- 2B: Retrieval with Product ID Pinning ---")
    for pid in test_pids:
        name = by_id.get(pid, pid)
        results = svc._retrieve("What are the key specs and features?", product_id=pid)
        if results:
            meta = results[0].get("metadata", {}) or {}
            pname = meta.get("product_name") or meta.get("name")
            sim = results[0].get("similarity", 0)
            print(f"[{pid}] {name:35} -> Top: {str(pname):35} sim={sim:.3f}")
        else:
            print(f"[{pid}] {name:35} -> NO RESULTS")


def verify_qa(svc: RAGService):
    print()
    print("=" * 70)
    print("STEP 3: END-TO-END QA TEST (Galaxy S26 Ultra & Multiple New Products)")
    print("=" * 70)

    test_questions = [
        "What are the key specs of Galaxy S26 Ultra?",
        "What are the features of Samsung Galaxy Watch8 40mm?",
        "What are the specs of Samsung Galaxy Book6 Ultra 16\"?",
        "Tell me about Samsung Galaxy Buds4 Pro",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        resp = svc.chat(question, history=[], shop_id="S001")
        print(f"Intent: {resp.get('intent')} | Relevant: {resp.get('relevant')} | Score: {resp.get('similarity_score', 0):.3f}")
        print(f"A: {resp.get('answer')}")


def main():
    svc = RAGService()
    verify_retrieval(svc)
    verify_qa(svc)


if __name__ == "__main__":
    main()

