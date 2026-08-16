from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:

    print("=" * 60)
    print("LOCAL EMBEDDING MODEL TEST")
    print("=" * 60)

    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")

    text = "When should I clean the filter?"

    print("\nGenerating embedding...")

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    print("Embedding generated successfully.")

    print(
        f"Embedding dimensions: {len(embedding)}"
    )

    print(
        f"First 5 values: {embedding[:5]}"
    )

    print("\n" + "=" * 60)
    print("LOCAL EMBEDDING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()