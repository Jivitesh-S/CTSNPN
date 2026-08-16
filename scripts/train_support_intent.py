import json
import pickle
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
)
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "shop"
    / "support_clean.json"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "data"
    / "shop"
    / "intent_model.pkl"
)

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

RANDOM_STATE = 42

TEST_SIZE = 0.15


def main() -> int:

    print()
    print("=" * 70)
    print("SUPPORT INTENT CLASSIFIER TRAINING")
    print("=" * 70)

    if not CLEAN_FILE.exists():

        print(f"Clean data not found: {CLEAN_FILE}")
        print("Run clean_support_data.py first.")
        return 1

    with open(
        CLEAN_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        records = json.load(file)

    instructions = [
        record["instruction"]
        for record in records
    ]

    intents = [
        record["intent"]
        for record in records
    ]

    print(f"Records: {len(records)}")
    print(f"Intent classes: {len(set(intents))}")

    classes = sorted(set(intents))

    class_to_index = {
        intent: index
        for index, intent in enumerate(classes)
    }

    labels = np.array(
        [class_to_index[intent] for intent in intents]
    )

    # --------------------------------------------------------
    # Embed instructions using the same model as the RAG
    # --------------------------------------------------------

    print()
    print(
        f"Loading embedding model "
        f"({EMBEDDING_MODEL_NAME})..."
    )

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    print("Creating instruction embeddings...")

    embeddings = embedding_model.encode(
        instructions,
        show_progress_bar=True,
        batch_size=64,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        embeddings,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    # --------------------------------------------------------
    # Train classifier
    # --------------------------------------------------------

    print()
    print("Training LogisticRegression classifier...")

    classifier = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=RANDOM_STATE,
    )

    classifier.fit(X_train, y_train)

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    predictions = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print()
    print(f"Test accuracy: {accuracy:.4f}")
    print()

    print(classification_report(
        y_test,
        predictions,
        target_names=classes,
        zero_division=0,
    ))

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        MODEL_FILE,
        "wb"
    ) as file:

        pickle.dump(
            {
                "classifier": classifier,
                "classes": classes,
                "class_to_index": class_to_index,
                "embedding_model_name": EMBEDDING_MODEL_NAME,
                "test_accuracy": float(accuracy),
            },
            file,
        )

    print(f"Model saved: {MODEL_FILE}")

    return 0


if __name__ == "__main__":

    sys.exit(main())
