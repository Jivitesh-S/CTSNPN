import json
from pathlib import Path

import numpy as np
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
# MODEL
# =========================================================

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# LOAD RECORDS
# =========================================================

def load_records() -> list[dict]:

    if not RECORDS_FILE.exists():
        raise FileNotFoundError(
            f"Records file not found:\n"
            f"{RECORDS_FILE}\n\n"
            "Run embed_knowledge.py first."
        )

    with RECORDS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "Embedded knowledge must be a JSON list."
        )

    return records


# =========================================================
# LOAD EMBEDDINGS
# =========================================================

def load_embeddings() -> np.ndarray:

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Embedding file not found:\n"
            f"{EMBEDDINGS_FILE}\n\n"
            "Run embed_knowledge.py first."
        )

    embeddings = np.load(
        EMBEDDINGS_FILE
    )

    if embeddings.ndim != 2:
        raise ValueError(
            "Embedding matrix must be 2-dimensional."
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
    Calculate cosine similarity between the query
    vector and every knowledge vector.
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
    vector space used by the knowledge embeddings.
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
            "Query embedding must be a 1D vector."
        )

    return embedding


# =========================================================
# SEARCH
# =========================================================

def search(
    query: str,
    model: SentenceTransformer,
    records: list[dict],
    embeddings: np.ndarray,
    top_k: int = 5,
) -> list[tuple[int, float]]:

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    if len(records) != len(embeddings):
        raise ValueError(
            "Number of records and embeddings "
            "must be identical."
        )

    query_vector = create_query_embedding(
        model,
        query
    )

    if query_vector.shape[0] != embeddings.shape[1]:
        raise ValueError(
            "Query and knowledge embeddings "
            "have different dimensions."
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

        results.append(
            (
                int(index),
                float(scores[index])
            )
        )

    return results


# =========================================================
# DISPLAY RESULTS
# =========================================================

def display_results(
    query: str,
    results: list[tuple[int, float]],
    records: list[dict],
) -> None:

    print(
        "\n" + "=" * 70
    )

    print(
        "SEMANTIC SEARCH RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nQuery:\n{query}"
    )

    for rank, (
        index,
        score
    ) in enumerate(
        results,
        start=1
    ):

        record = records[index]

        print(
            "\n" + "-" * 70
        )

        print(
            f"Rank: {rank}"
        )

        print(
            f"Similarity: {score:.4f}"
        )

        print(
            f"Source Type: "
            f"{record['source_type']}"
        )

        print(
            f"Source: "
            f"{record['source_name']}"
        )

        print(
            f"Metadata: "
            f"{record['metadata']}"
        )

        print(
            "\nContent:"
        )

        print(
            record["content"]
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "Loading local embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Model loaded."
    )

    records = load_records()

    embeddings = load_embeddings()

    print(
        f"Loaded {len(records)} knowledge records."
    )

    print(
        f"Embedding matrix shape: "
        f"{embeddings.shape}"
    )

    query = input(
        "\nEnter your question: "
    ).strip()

    results = search(
        query=query,
        model=model,
        records=records,
        embeddings=embeddings,
        top_k=5,
    )

    display_results(
        query,
        results,
        records
    )


if __name__ == "__main__":
    main()