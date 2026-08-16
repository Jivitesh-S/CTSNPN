import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from backend.ingest import sync_index  # noqa: E402


# ============================================================
# MAIN INGESTION
# ============================================================

def main():

    print()
    print("=" * 70)
    print("TECHSTORE RAG INGESTION")
    print("=" * 70)

    try:

        result = sync_index()

    except Exception as error:

        print()
        print(f"INGESTION FAILED: {error}")
        return 1

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(f"Total knowledge records: {result['records']}")

    print(f"Total ChromaDB chunks: {result['chunks']}")

    print(f"Stale chunks removed: {result['stale_removed']}")

    print("TechStore knowledge is now indexed.")

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(main())
