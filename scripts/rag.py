import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed"
)

RECORDS_FILE = (
    PROCESSED_DATA_DIR
    / "embedded_knowledge.json"
)

EMBEDDINGS_FILE = (
    PROCESSED_DATA_DIR
    / "knowledge_embeddings.npy"
)


# =========================================================
# MODELS
# =========================================================

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

GENERATION_MODEL_NAME = (
    "gemini-3.6-flash"
)


# =========================================================
# RETRIEVAL CONFIGURATION
# =========================================================

TOP_K = 5

# Initial MVP threshold based on our retrieval evaluation.
#
# Known relevant questions:
# Minimum score = 0.4101
#
# Irrelevant questions:
# Maximum score = 0.2683
#
# Therefore, 0.40 is being used as the initial
# relevance gate.
SIMILARITY_THRESHOLD = 0.40


# =========================================================
# SAFE FALLBACK RESPONSE
# =========================================================

FALLBACK_RESPONSE = (
    "I couldn't find enough relevant information in the "
    "available product knowledge to answer that question "
    "confidently."
)


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found.\n"
        "Make sure your .env file contains:\n"
        "GEMINI_API_KEY=YOUR_API_KEY"
    )


# =========================================================
# INITIALIZE GEMINI
# =========================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# LOAD KNOWLEDGE RECORDS
# =========================================================

def load_records() -> list[dict]:
    """
    Load the knowledge records generated during
    the embedding stage.
    """

    if not RECORDS_FILE.exists():
        raise FileNotFoundError(
            f"\nKnowledge records not found:\n"
            f"{RECORDS_FILE}\n\n"
            f"Run embed_knowledge.py first."
        )

    with RECORDS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "Knowledge records must be a JSON list."
        )

    return records


# =========================================================
# LOAD EMBEDDINGS
# =========================================================

def load_embeddings() -> np.ndarray:
    """
    Load the precomputed knowledge embeddings.
    """

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"\nKnowledge embeddings not found:\n"
            f"{EMBEDDINGS_FILE}\n\n"
            f"Run embed_knowledge.py first."
        )

    embeddings = np.load(
        EMBEDDINGS_FILE
    )

    if embeddings.ndim != 2:
        raise ValueError(
            "Knowledge embeddings must be a "
            "2-dimensional NumPy array."
        )

    return embeddings


# =========================================================
# COSINE SIMILARITY
# =========================================================

def cosine_similarity(
    query_vector: np.ndarray,
    document_vectors: np.ndarray,
) -> np.ndarray:
    """
    Calculate cosine similarity between the query vector
    and every knowledge vector.
    """

    query_norm = np.linalg.norm(
        query_vector
    )

    document_norms = np.linalg.norm(
        document_vectors,
        axis=1
    )

    if query_norm == 0:
        raise ValueError(
            "Query vector has zero magnitude."
        )

    if np.any(document_norms == 0):
        raise ValueError(
            "One or more knowledge vectors "
            "have zero magnitude."
        )

    similarities = (
        document_vectors @ query_vector
    ) / (
        document_norms * query_norm
    )

    return similarities


# =========================================================
# CREATE QUERY EMBEDDING
# =========================================================

def create_query_embedding(
    model: SentenceTransformer,
    query: str,
) -> np.ndarray:
    """
    Convert the user's question into the same
    embedding space used by the knowledge base.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Query cannot be empty."
        )

    embedding = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    if embedding.ndim != 1:
        raise ValueError(
            "Query embedding must be a 1-dimensional vector."
        )

    return embedding


# =========================================================
# RETRIEVE TOP-K KNOWLEDGE
# =========================================================

def retrieve(
    query: str,
    embedding_model: SentenceTransformer,
    records: list[dict],
    embeddings: np.ndarray,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Retrieve the Top-K most semantically similar
    knowledge records.
    """

    query_vector = create_query_embedding(
        embedding_model,
        query
    )

    if query_vector.shape[0] != embeddings.shape[1]:
        raise ValueError(
            "Query and knowledge embedding dimensions "
            "do not match."
        )

    scores = cosine_similarity(
        query_vector,
        embeddings
    )

    actual_k = min(
        top_k,
        len(scores)
    )

    top_indices = np.argsort(
        scores
    )[-actual_k:][::-1]

    results = []

    for index in top_indices:

        index = int(index)

        results.append(
            {
                "index": index,
                "score": float(scores[index]),
                "record": records[index],
            }
        )

    return results


# =========================================================
# RELEVANCE GATE
# =========================================================

def passes_relevance_gate(
    retrieved_results: list[dict],
) -> bool:
    """
    Determine whether the strongest retrieved result
    is sufficiently relevant to use as evidence.

    The MVP uses the highest cosine similarity score.
    """

    if not retrieved_results:
        return False

    best_score = retrieved_results[0]["score"]

    return (
        best_score >= SIMILARITY_THRESHOLD
    )


# =========================================================
# BUILD RAG CONTEXT
# =========================================================

def build_context(
    retrieved_results: list[dict]
) -> str:
    """
    Convert retrieved records into structured context
    for Gemini.
    """

    context_parts = []

    for rank, result in enumerate(
        retrieved_results,
        start=1
    ):

        record = result["record"]

        source_name = record.get(
            "source_name",
            "Unknown"
        )

        source_type = record.get(
            "source_type",
            "Unknown"
        )

        metadata = record.get(
            "metadata",
            {}
        )

        content = record.get(
            "content",
            ""
        )

        context_parts.append(
            f"""
--- SOURCE {rank} ---

Source Type:
{source_type}

Source Name:
{source_name}

Metadata:
{metadata}

Similarity Score:
{result["score"]:.4f}

Content:
{content}
""".strip()
        )

    return "\n\n".join(
        context_parts
    )


# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """
You are an Intelligent Product Support Assistant.

Your job is to answer customer questions about products
using the product knowledge provided to you.

IMPORTANT RULES:

1. Use the supplied product context as your primary
   source of information.

2. Do not invent product features, prices,
   specifications, instructions, policies, or
   other product information.

3. If the supplied context does not contain enough
   information to answer the question, clearly state
   that the information is not available in the
   provided product knowledge.

4. Do not pretend that an unsupported answer is certain.

5. When explaining product instructions, preserve
   important steps, warnings, conditions, and
   limitations from the source.

6. Answer in a clear, helpful, customer-friendly manner.

7. Do not mention internal retrieval mechanisms,
   embeddings, vectors, cosine similarity, or RAG
   unless the customer explicitly asks about them.

8. Do not treat similarity scores as product information.
   They are only internal retrieval signals.

9. If the provided context does not support the answer,
   do not use your general knowledge to manufacture an
   answer.
""".strip()


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(
    question: str,
    context: str,
) -> str:
    """
    Send the retrieved context and user question
    to Gemini for grounded answer generation.
    """

    prompt = f"""
PRODUCT KNOWLEDGE CONTEXT:

{context}

CUSTOMER QUESTION:

{question}

Using the product knowledge context above, answer the
customer's question accurately and clearly.
""".strip()

    response = gemini_client.models.generate_content(
        model=GENERATION_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


# =========================================================
# DISPLAY RETRIEVED SOURCES
# =========================================================

def display_retrieved_sources(
    retrieved_results: list[dict]
) -> None:

    print(
        "\n" + "=" * 70
    )

    print(
        "RETRIEVED KNOWLEDGE"
    )

    print(
        "=" * 70
    )

    for rank, result in enumerate(
        retrieved_results,
        start=1
    ):

        record = result["record"]

        print(
            f"\n[{rank}] "
            f"Similarity: "
            f"{result['score']:.4f}"
        )

        print(
            f"Source: "
            f"{record['source_name']}"
        )

        print(
            f"Type: "
            f"{record['source_type']}"
        )

        print(
            f"Metadata: "
            f"{record['metadata']}"
        )

        print(
            "\nContent:"
        )

        print(
            record["content"][:500]
        )


# =========================================================
# DISPLAY RELEVANCE DECISION
# =========================================================

def display_relevance_decision(
    retrieved_results: list[dict]
) -> None:

    best_score = retrieved_results[0]["score"]

    print(
        "\n" + "=" * 70
    )

    print(
        "RELEVANCE CHECK"
    )

    print(
        "=" * 70
    )

    print(
        f"Best similarity score : "
        f"{best_score:.4f}"
    )

    print(
        f"Required threshold    : "
        f"{SIMILARITY_THRESHOLD:.4f}"
    )

    if best_score >= SIMILARITY_THRESHOLD:

        print(
            "Decision              : PASS"
        )

        print(
            "Retrieval is considered "
            "sufficiently relevant."
        )

    else:

        print(
            "Decision              : REJECT"
        )

        print(
            "Retrieval is not sufficiently "
            "relevant."
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "=" * 70
    )

    print(
        "INTELLIGENT PRODUCT SUPPORT - RAG MVP"
    )

    print(
        "=" * 70
    )

    print(
        "\nConfiguration:"
    )

    print(
        f"Embedding Model : "
        f"{EMBEDDING_MODEL_NAME}"
    )

    print(
        f"Generation Model: "
        f"{GENERATION_MODEL_NAME}"
    )

    print(
        f"Top-K           : "
        f"{TOP_K}"
    )

    print(
        f"Threshold       : "
        f"{SIMILARITY_THRESHOLD}"
    )

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print(
        "\nLoading embedding model..."
    )

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    print(
        "Embedding model loaded."
    )

    # -----------------------------------------------------
    # Load knowledge
    # -----------------------------------------------------

    print(
        "\nLoading knowledge..."
    )

    records = load_records()

    embeddings = load_embeddings()

    if len(records) != len(embeddings):

        raise RuntimeError(
            "Knowledge records and embeddings "
            "are not aligned."
        )

    print(
        f"Knowledge records: "
        f"{len(records)}"
    )

    print(
        f"Embedding matrix: "
        f"{embeddings.shape}"
    )

    print(
        "\nRAG system ready."
    )

    # -----------------------------------------------------
    # Interactive loop
    # -----------------------------------------------------

    while True:

        question = input(
            "\nCustomer Question "
            "(type 'exit' to quit): "
        ).strip()

        if question.lower() == "exit":

            print(
                "\nExiting RAG system."
            )

            break

        if not question:

            print(
                "Please enter a question."
            )

            continue

        # -------------------------------------------------
        # RETRIEVAL
        # -------------------------------------------------

        retrieved_results = retrieve(
            query=question,
            embedding_model=embedding_model,
            records=records,
            embeddings=embeddings,
            top_k=TOP_K,
        )

        display_retrieved_sources(
            retrieved_results
        )

        # -------------------------------------------------
        # RELEVANCE CHECK
        # -------------------------------------------------

        display_relevance_decision(
            retrieved_results
        )

        # -------------------------------------------------
        # RELEVANCE GATE
        # -------------------------------------------------

        if not passes_relevance_gate(
            retrieved_results
        ):

            print(
                "\n" + "=" * 70
            )

            print(
                "ASSISTANT"
            )

            print(
                "=" * 70
            )

            print(
                f"\n{FALLBACK_RESPONSE}"
            )

            continue

        # -------------------------------------------------
        # BUILD CONTEXT
        # -------------------------------------------------

        context = build_context(
            retrieved_results
        )

        # -------------------------------------------------
        # GENERATION
        # -------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "GENERATING ANSWER..."
        )

        print(
            "=" * 70
        )

        answer = generate_answer(
            question=question,
            context=context,
        )

        # -------------------------------------------------
        # FINAL ANSWER
        # -------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "ASSISTANT"
        )

        print(
            "=" * 70
        )

        print(
            f"\n{answer}"
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()