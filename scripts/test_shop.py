"""
End-to-end test for the TechStore RAG pipeline.

Uses a stub LLM so all retrieval / routing / catalog / FAQ
layers can be verified WITHOUT a Groq API key.
"""

import os
import sys
from pathlib import Path

os.environ["GROQ_API_KEY"] = "test-key-placeholder"

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)

from backend.rag_service import (  # noqa: E402
    CatalogLookup,
    FaqMatcher,
    IntentRouter,
    RAGService,
)


def run():

    print()
    print("=" * 70)
    print("TECHSTORE PIPELINE TESTS")
    print("=" * 70)

    # -------------------------------------------------
    # 1. Intent router tests
    # -------------------------------------------------

    router = IntentRouter()

    intent_cases = [
        ("hi", "greeting"),
        ("hello", "greeting"),
        ("thank you", "thanks"),
        ("bye", "farewell"),
        ("who are you", "identity"),
        ("What is the price of iPhone 15?", "price"),
        ("How much does the Galaxy A55 cost?", "price"),
        ("Is the MacBook Air M2 in stock?", "stock"),
        ("Do you have JBL Tune 520BT available?", "stock"),
        ("What is your return policy?", "policy"),
        ("Warranty period on phones?", "policy"),
        ("Best phone under Rs. 25,000?", "recommendation"),
        ("Which laptop should I buy for gaming?", "recommendation"),
        ("My phone won't charge", "troubleshooting"),
        ("How to fix a slow laptop?", "troubleshooting"),
    ]

    failures = 0

    for question, expected in intent_cases:

        actual = router.classify(question)

        status = "PASS" if actual == expected else "FAIL"

        if actual != expected:
            failures += 1

        print(
            f"[{status}] {question!r:55} -> {actual} "
            f"(expected {expected})"
        )

    # -------------------------------------------------
    # 2. Catalog lookup tests
    # -------------------------------------------------

    print()
    print("-" * 70)
    print("CATALOG LOOKUP")
    print("-" * 70)

    catalog = CatalogLookup(
        __import__("pathlib").Path(
            __import__("pathlib").Path(__file__).resolve().parent.parent
            / "data" / "shop" / "catalog.json"
        )
    )

    catalog_cases = [
        "Price of iPhone 15?",
        "How much is the samsung galaxy a55 5g?",
        "Galaxy S24 Ultra price",
        "What does the MacBook Air 13 M2 cost?",
        "Is the Xiaomi Redmi Note 13 Pro in stock?",
        "Do you have AirPods Pro 2 available?",
        "JBL Flip 6 price in your shop",
    ]

    for question in catalog_cases:

        product = catalog.find_product(question)

        if product:

            print(
                f"[FOUND] {question!r:55} -> "
                f"{product['name']} @ Rs. {product['price']:,} "
                f"({product['stock']})"
            )

        else:

            print(f"[MISS ] {question!r:55} -> no match")
            failures += 1

    # -------------------------------------------------
    # 3. FAQ matcher tests
    # -------------------------------------------------

    print()
    print("-" * 70)
    print("FAQ MATCHER")
    print("-" * 70)

    faq_matcher = FaqMatcher(
        __import__("pathlib").Path(
            __import__("pathlib").Path(__file__).resolve().parent.parent
            / "data" / "shop" / "faq.json"
        )
    )

    faq_cases = [
        "What are your store hours?",
        "What are your timings?",
        "Do you offer EMI options?",
        "How long does delivery take?",
        "Do you repair phones?",
    ]

    for question in faq_cases:

        faq = faq_matcher.match(question)

        if faq:

            print(
                f"[FOUND] {question!r:45} -> "
                f"{faq['question'][:50]}"
            )

        else:

            print(f"[MISS ] {question!r:45} -> no match")
            failures += 1

    # -------------------------------------------------
    # 4. Full service tests (stubbed LLM)
    # -------------------------------------------------

    print()
    print("-" * 70)
    print("FULL SERVICE (stubbed LLM)")
    print("-" * 70)

    import backend.rag_service as rag_module

    service = RAGService()

    service._generate_answer = (
        lambda question, context, history,
        is_comparison=False, shop=None, cross_shop=False: (
            "[STUB] LLM skipped - retrieved "
            + str(len(context.split("SOURCE"))) + " sources"
        )
    )

    service_cases = [
        "What is the price of iPhone 15?",
        "Is the Samsung Galaxy A55 5G in stock?",
        "What is your return policy?",
        "My phone battery drains too fast, what should I do?",
        "Best phone under Rs. 25,000?",
        "hello",
        "What is the capital of France?",
    ]

    for question in service_cases:

        result = service.chat(question)

        print()
        print(f"Q: {question}")
        print(f"   Intent: {result.get('intent')} | "
              f"Relevant: {result['relevant']} | "
              f"Score: {result['similarity_score']:.3f}")
        print(f"   A: {result['answer'][:110]}...")

    # -------------------------------------------------
    # 5. Conversation history test
    # -------------------------------------------------

    print()
    print("-" * 70)
    print("HISTORY TEST")
    print("-" * 70)

    history = [
        {"role": "user", "content": "Is iPhone 15 in stock?"},
        {"role": "assistant", "content": "Yes, it is in stock."},
        {"role": "user", "content": "What about the 256GB version?"},
    ]

    result = service.chat("What about the 256GB version?", history)

    print(f"Q (with history): What about the 256GB version?")
    print(f"   Intent: {result.get('intent')} | "
          f"Relevant: {result['relevant']}")

    print()
    print("=" * 70)

    if failures:

        print(f"RESULT: {failures} FAILURES")

    else:

        print("RESULT: ALL TESTS PASSED")

    print("=" * 70)


if __name__ == "__main__":

    run()
