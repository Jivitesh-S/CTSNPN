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

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "retrieval_evaluation.json"
)


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# RETRIEVAL CONFIGURATION
# =========================================================

TOP_K = 5


# =========================================================
# EVALUATION QUESTIONS
# =========================================================

TEST_QUESTIONS = [

    # -----------------------------------------------------
    # RELEVANT QUESTIONS
    # -----------------------------------------------------

    {
        "category": "relevant",
        "question": "What must I do before removing any FRU or CRU from the computer?",
    },

    {
        "category": "relevant",
        "question": "How many screws need to be removed to take off the lower case of the 15-inch models?",
    },

    {
        "category": "relevant",
        "question": "What is the warranty period?",
    },

    {
        "category": "relevant",
        "question": "What should I do if the LCD breaks and fluid gets into my eyes?",
    },

    # -----------------------------------------------------
    # PARAPHRASED QUESTIONS
    # -----------------------------------------------------

    {
        "category": "paraphrased",
        "question": (
            "Will my warranty cover a cracked screen if I drop the laptop?"
        ),
    },

    {
        "category": "paraphrased",
        "question": (
            "How can I make sure I haven't left any loose screws inside the computer after a repair?"
        ),
    },

    {
        "category": "paraphrased",
        "question": (
            "Is it safe to use a third-party replacement battery if it fits?"
        ),
    },

    # -----------------------------------------------------
    # IRRELEVANT QUESTIONS
    # -----------------------------------------------------

    {
        "category": "irrelevant",
        "question": "I am Kannan",
    },

    {
        "category": "irrelevant",
        "question": "I love you",
    },

    {
        "category": "irrelevant",
        "question": (
            "What is the capital of France?"
        ),
    },

    {
        "category": "irrelevant",
        "question": (
            "Tell me a joke about football."
        ),
    },
]


# =========================================================
# LOAD KNOWLEDGE RECORDS
# =========================================================

def load_records() -> list[dict]:
    """
    Load the knowledge records that were saved during
    the embedding stage.

    The record order must match the embedding order.
    """

    if not RECORDS_FILE.exists():
        raise FileNotFoundError(
            f"\nKnowledge records file not found:\n"
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
    Load the previously generated knowledge embeddings.
    """

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"\nEmbedding file not found:\n"
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
    Calculate cosine similarity between one query vector
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
# GET TOP-K RESULTS
# =========================================================

def get_top_results(
    question: str,
    model: SentenceTransformer,
    records: list[dict],
    embeddings: np.ndarray,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Convert the question into an embedding and retrieve
    the top-K most similar knowledge records.
    """

    # -----------------------------------------------------
    # Create query embedding
    # -----------------------------------------------------

    query_embedding = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # -----------------------------------------------------
    # Validate dimensions
    # -----------------------------------------------------

    if query_embedding.ndim != 1:
        raise ValueError(
            "Query embedding must be a 1-dimensional vector."
        )

    if query_embedding.shape[0] != embeddings.shape[1]:
        raise ValueError(
            "Query embedding dimension does not match "
            "knowledge embedding dimension."
        )

    # -----------------------------------------------------
    # Calculate similarity
    # -----------------------------------------------------

    scores = cosine_similarity(
        query_embedding,
        embeddings
    )

    # -----------------------------------------------------
    # Get Top-K indices
    # -----------------------------------------------------

    actual_k = min(
        top_k,
        len(scores)
    )

    top_indices = np.argsort(
        scores
    )[-actual_k:][::-1]

    # -----------------------------------------------------
    # Build results
    # -----------------------------------------------------

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
# DISPLAY TOP-K RESULTS
# =========================================================

def display_top_results(
    results: list[dict]
) -> None:
    """
    Display the Top-K similarity scores and the
    corresponding knowledge sources.
    """

    print(
        "\nTop 5 scores:"
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        record = result["record"]

        print(
            f"  {rank}. "
            f"{result['score']:.4f} "
            f"| "
            f"{record['source_name']}"
        )


# =========================================================
# CALCULATE CATEGORY STATISTICS
# =========================================================

def calculate_category_statistics(
    results: list[dict],
) -> None:
    """
    Calculate minimum, maximum, and average Top-1
    similarity score for each evaluation category.
    """

    categories = [
        "relevant",
        "paraphrased",
        "irrelevant",
    ]

    print(
        "\n" + "=" * 80
    )

    print(
        "SCORE DISTRIBUTION"
    )

    print(
        "=" * 80
    )

    for category in categories:

        category_scores = [
            result["top_score"]
            for result in results
            if result["category"] == category
        ]

        if not category_scores:
            continue

        minimum = min(
            category_scores
        )

        maximum = max(
            category_scores
        )

        average = sum(
            category_scores
        ) / len(
            category_scores
        )

        print(
            f"\n{category.upper()}"
        )

        print(
            f"Minimum : {minimum:.4f}"
        )

        print(
            f"Maximum : {maximum:.4f}"
        )

        print(
            f"Average : {average:.4f}"
        )


# =========================================================
# SAVE EVALUATION RESULTS
# =========================================================

def save_results(
    results: list[dict]
) -> None:
    """
    Save the complete evaluation results so we can
    inspect them later without rerunning the model.
    """

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "=" * 80
    )

    print(
        "RETRIEVAL EVALUATION"
    )

    print(
        "=" * 80
    )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    print(
        "\nLoading embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Model loaded successfully."
    )

    # -----------------------------------------------------
    # Load records
    # -----------------------------------------------------

    print(
        "\nLoading knowledge records..."
    )

    records = load_records()

    print(
        f"Knowledge records: "
        f"{len(records)}"
    )

    # -----------------------------------------------------
    # Load embeddings
    # -----------------------------------------------------

    print(
        "\nLoading knowledge embeddings..."
    )

    embeddings = load_embeddings()

    print(
        f"Embedding matrix: "
        f"{embeddings.shape}"
    )

    # -----------------------------------------------------
    # Validate alignment
    # -----------------------------------------------------

    if len(records) != len(embeddings):

        raise RuntimeError(
            "\nRecord/embedding mismatch!\n"
            f"Records: {len(records)}\n"
            f"Embeddings: {len(embeddings)}\n"
            "\nThe record order and embedding order "
            "must be identical."
        )

    # -----------------------------------------------------
    # Evaluation
    # -----------------------------------------------------

    evaluation_results = []

    print(
        "\nStarting evaluation..."
    )

    for test_case in TEST_QUESTIONS:

        category = test_case[
            "category"
        ]

        question = test_case[
            "question"
        ]

        # -------------------------------------------------
        # Retrieve Top-K
        # -------------------------------------------------

        top_results = get_top_results(
            question=question,
            model=model,
            records=records,
            embeddings=embeddings,
            top_k=TOP_K,
        )

        # -------------------------------------------------
        # Best result
        # -------------------------------------------------

        best_result = top_results[0]

        top_score = best_result[
            "score"
        ]

        best_record = best_result[
            "record"
        ]

        # -------------------------------------------------
        # Store evaluation result
        # -------------------------------------------------

        evaluation_result = {
            "category": category,
            "question": question,
            "top_score": top_score,
            "top_scores": [
                result["score"]
                for result in top_results
            ],
            "top_sources": [
                result["record"]["source_name"]
                for result in top_results
            ],
            "best_source": (
                best_record["source_name"]
            ),
            "best_source_type": (
                best_record["source_type"]
            ),
            "best_metadata": (
                best_record["metadata"]
            ),
            "best_content": (
                best_record["content"]
            ),
        }

        evaluation_results.append(
            evaluation_result
        )

        # -------------------------------------------------
        # Display
        # -------------------------------------------------

        print(
            "\n" + "-" * 80
        )

        print(
            f"Category : {category}"
        )

        print(
            f"Question : {question}"
        )

        display_top_results(
            top_results
        )

        print(
            "\nBest Result:"
        )

        print(
            f"Similarity : "
            f"{top_score:.4f}"
        )

        print(
            f"Source     : "
            f"{best_record['source_name']}"
        )

        print(
            f"Type       : "
            f"{best_record['source_type']}"
        )

        print(
            f"Content    : "
            f"{best_record['content'][:250]}..."
        )

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    calculate_category_statistics(
        evaluation_results
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_results(
        evaluation_results
    )

    print(
        "\nEvaluation results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    # -----------------------------------------------------
    # Completion
    # -----------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "RETRIEVAL EVALUATION COMPLETE"
    )

    print(
        "=" * 80
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()