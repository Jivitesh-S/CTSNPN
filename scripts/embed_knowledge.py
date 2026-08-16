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

DATASET_FILE = (
    PROCESSED_DATA_DIR
    / "normalized_knowledge.json"
)

DOCUMENT_FILE = (
    PROCESSED_DATA_DIR
    / "document_knowledge.json"
)

EMBEDDED_RECORDS_FILE = (
    PROCESSED_DATA_DIR
    / "embedded_knowledge.json"
)

EMBEDDINGS_FILE = (
    PROCESSED_DATA_DIR
    / "knowledge_embeddings.npy"
)


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

BATCH_SIZE = 64


# =========================================================
# LOAD JSON RECORDS
# =========================================================

def load_json_records(
    file_path: Path
) -> list[dict]:
    """
    Load a JSON file containing a list of
    normalized knowledge records.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in:\n{file_path}"
        )

    return data


# =========================================================
# VALIDATE RECORDS
# =========================================================

def validate_records(
    records: list[dict]
) -> None:
    """
    Validate that every record has the structure
    created by our normalization/document ingestion
    pipelines.
    """

    required_fields = {
        "content",
        "source_type",
        "source_name",
        "metadata",
    }

    for index, record in enumerate(records):

        missing_fields = (
            required_fields - record.keys()
        )

        if missing_fields:
            raise ValueError(
                f"Record {index} is missing fields: "
                f"{sorted(missing_fields)}"
            )

        if not isinstance(
            record["content"],
            str
        ):
            raise ValueError(
                f"Record {index}: content must be a string."
            )

        if not record["content"].strip():
            raise ValueError(
                f"Record {index}: content cannot be empty."
            )

        if not isinstance(
            record["metadata"],
            dict
        ):
            raise ValueError(
                f"Record {index}: metadata must be a dictionary."
            )


# =========================================================
# SAVE RECORDS
# =========================================================

def save_records(
    records: list[dict]
) -> None:
    """
    Save the exact record order used during embedding.

    The order is extremely important because:

        record[0] <-> embedding[0]
        record[1] <-> embedding[1]
        ...
    """

    with EMBEDDED_RECORDS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# SAVE EMBEDDINGS
# =========================================================

def save_embeddings(
    embeddings: np.ndarray
) -> None:
    """
    Save embeddings as a NumPy matrix.
    """

    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D matrix."
        )

    np.save(
        EMBEDDINGS_FILE,
        embeddings
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print("=" * 65)
    print("LOCAL KNOWLEDGE EMBEDDING PIPELINE")
    print("=" * 65)

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    print(
        "\n[1/6] Loading normalized dataset..."
    )

    dataset_records = load_json_records(
        DATASET_FILE
    )

    print(
        f"      Dataset records: "
        f"{len(dataset_records)}"
    )

    # -----------------------------------------------------
    # Load user documents
    # -----------------------------------------------------

    print(
        "\n[2/6] Loading document knowledge..."
    )

    document_records = load_json_records(
        DOCUMENT_FILE
    )

    print(
        f"      Document chunks: "
        f"{len(document_records)}"
    )

    # -----------------------------------------------------
    # Combine
    # -----------------------------------------------------

    all_records = (
        dataset_records
        + document_records
    )

    print(
        f"\n      Total knowledge records: "
        f"{len(all_records)}"
    )

    # -----------------------------------------------------
    # Validate
    # -----------------------------------------------------

    print(
        "\n[3/6] Validating knowledge records..."
    )

    validate_records(
        all_records
    )

    print(
        "      Validation successful."
    )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    print(
        "\n[4/6] Loading embedding model..."
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        f"      Model: {MODEL_NAME}"
    )

    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    texts = [
        record["content"]
        for record in all_records
    ]

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print(
        "\n[5/6] Generating local embeddings..."
    )

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    # -----------------------------------------------------
    # Validate embeddings
    # -----------------------------------------------------

    if embeddings.ndim != 2:
        raise RuntimeError(
            "Embedding output must be a 2D matrix."
        )

    if len(embeddings) != len(all_records):
        raise RuntimeError(
            "Embedding count does not match "
            "knowledge record count."
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    print(
        "\n[6/6] Saving embedding data..."
    )

    save_records(
        all_records
    )

    save_embeddings(
        embeddings
    )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print(
        "\n" + "=" * 65
    )

    print(
        "LOCAL EMBEDDING PIPELINE COMPLETE"
    )

    print(
        "=" * 65
    )

    print(
        f"Knowledge records: "
        f"{len(all_records)}"
    )

    print(
        f"Embedding matrix shape: "
        f"{embeddings.shape}"
    )

    print(
        f"Embedding dimension: "
        f"{embeddings.shape[1]}"
    )

    print(
        "\nMetadata:"
    )

    print(
        f"  {EMBEDDED_RECORDS_FILE}"
    )

    print(
        "\nVectors:"
    )

    print(
        f"  {EMBEDDINGS_FILE}"
    )

    print(
        "\nNext stage:"
    )

    print(
        "Query Embedding → Cosine Similarity → Top-K Retrieval"
    )


if __name__ == "__main__":
    main()