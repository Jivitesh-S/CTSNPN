import csv
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "customer_support.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "shop"
    / "support_clean.json"
)

PLACEHOLDER_PATTERN = re.compile(
    r"\{\{.*?\}\}"
)


def clean_text(text: str) -> str:

    if not text:
        return ""

    text = PLACEHOLDER_PATTERN.sub("", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def main() -> int:

    print()
    print("=" * 70)
    print("CUSTOMER SUPPORT DATA CLEANING")
    print("=" * 70)

    if not CSV_FILE.exists():

        print(f"CSV not found: {CSV_FILE}")
        return 1

    records = []

    seen = set()

    placeholders_removed = 0

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            instruction = clean_text(
                row.get("instruction", "")
            )

            response = clean_text(
                row.get("response", "")
            )

            category = clean_text(
                row.get("category", "")
            )

            intent = clean_text(
                row.get("intent", "")
            )

            if not instruction or not response:
                continue

            key = (intent, instruction)

            if key in seen:
                continue

            seen.add(key)

            if "{{" in row.get("instruction", "") or (
                "{{" in row.get("response", "")
            ):
                placeholders_removed += 1

            records.append(
                {
                    "instruction": instruction,
                    "response": response,
                    "category": category,
                    "intent": intent,
                }
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Cleaned records: {len(records)}")

    print(f"Rows with placeholders cleaned: {placeholders_removed}")

    print(f"Output: {OUTPUT_FILE}")

    return 0


if __name__ == "__main__":

    sys.exit(main())
