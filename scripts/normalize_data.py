import csv
import json
import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

CSV_FILE = RAW_DATA_DIR / "customer_support.csv"
JSONL_FILE = RAW_DATA_DIR / "train_expanded.json"

OUTPUT_FILE = PROCESSED_DATA_DIR / "normalized_knowledge.json"


# ---------------------------------------------------------
# Text utilities
# ---------------------------------------------------------

def clean_text(value: Any) -> str:
    """
    Convert a value to clean, normalized text.

    - Handles None safely.
    - Converts non-string values to strings.
    - Removes leading/trailing whitespace.
    - Collapses repeated whitespace.
    """
    if value is None:
        return ""

    text = str(value).strip()

    # Replace multiple whitespace characters with one space.
    text = re.sub(r"\s+", " ", text)

    return text


# ---------------------------------------------------------
# CSV normalization
# ---------------------------------------------------------

def load_csv_records(file_path: Path) -> tuple[list[dict], int]:
    """
    Load and normalize the customer-support CSV.

    Expected columns:
        flags
        instruction
        category
        intent
        response

    Returns:
        records, duplicate_count
    """

    records: list[dict] = []
    seen_records: set[tuple] = set()
    duplicate_count = 0

    required_columns = {
        "flags",
        "instruction",
        "category",
        "intent",
        "response",
    }

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header row.")

        actual_columns = {
            column.strip()
            for column in reader.fieldnames
            if column is not None
        }

        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                f"CSV is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):

            instruction = clean_text(row.get("instruction"))
            response = clean_text(row.get("response"))
            category = clean_text(row.get("category"))
            intent = clean_text(row.get("intent"))
            flags = clean_text(row.get("flags"))

            # A knowledge record is not useful if both the
            # question and answer are empty.
            if not instruction and not response:
                continue

            # Exact duplicate detection is performed using
            # the original logical fields.
            duplicate_key = (
                instruction,
                response,
                category,
                intent,
                flags,
            )

            if duplicate_key in seen_records:
                duplicate_count += 1
                continue

            seen_records.add(duplicate_key)

            # The natural-language content is what will
            # eventually be embedded and searched.
            content = f"{instruction}\n{response}".strip()

            record = {
                "content": content,
                "source_type": "dataset",
                "source_name": "customer_support_csv",
                "metadata": {
                    "category": category,
                    "intent": intent,
                    "flags": flags,
                    "source_row": row_number,
                },
            }

            records.append(record)

    return records, duplicate_count


# ---------------------------------------------------------
# JSONL normalization
# ---------------------------------------------------------

def load_jsonl_records(file_path: Path) -> tuple[list[dict], int]:
    """
    Load and normalize the train_expanded.json file.

    The supplied file is JSON Lines (JSONL):
    one JSON object per line.

    Expected fields:
        question
        answer

    Returns:
        records, duplicate_count
    """

    records: list[dict] = []
    seen_records: set[tuple] = set()
    duplicate_count = 0

    with file_path.open(
        mode="r",
        encoding="utf-8-sig"
    ) as file:

        for line_number, line in enumerate(file, start=1):

            line = line.strip()

            # Ignore completely empty lines.
            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                ) from error

            if not isinstance(item, dict):
                raise ValueError(
                    f"Expected a JSON object on line {line_number}."
                )

            question = clean_text(item.get("question"))
            answer = clean_text(item.get("answer"))

            if not question and not answer:
                continue

            duplicate_key = (
                question,
                answer,
            )

            if duplicate_key in seen_records:
                duplicate_count += 1
                continue

            seen_records.add(duplicate_key)

            content = f"{question}\n{answer}".strip()

            record = {
                "content": content,
                "source_type": "dataset",
                "source_name": "train_expanded_json",
                "metadata": {
                    "source_line": line_number,
                },
            }

            records.append(record)

    return records, duplicate_count


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

def validate_records(records: list[dict]) -> None:
    """
    Validate the final normalized records.

    Raises ValueError if the normalized structure
    does not satisfy our project requirements.
    """

    required_fields = {
        "content",
        "source_type",
        "source_name",
        "metadata",
    }

    for index, record in enumerate(records):

        missing_fields = required_fields - record.keys()

        if missing_fields:
            raise ValueError(
                f"Record {index} is missing fields: "
                f"{sorted(missing_fields)}"
            )

        if not isinstance(record["content"], str):
            raise ValueError(
                f"Record {index}: content must be a string."
            )

        if not record["content"].strip():
            raise ValueError(
                f"Record {index}: content cannot be empty."
            )

        if not isinstance(record["metadata"], dict):
            raise ValueError(
                f"Record {index}: metadata must be a dictionary."
            )


# ---------------------------------------------------------
# Save normalized data
# ---------------------------------------------------------

def save_records(
    records: list[dict],
    output_file: Path
) -> None:

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
        mode="w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=2
        )


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main() -> None:

    print("=" * 60)
    print("INTELLIGENT PRODUCT SUPPORT")
    print("DATA NORMALIZATION")
    print("=" * 60)

    # -----------------------------------------------------
    # Check input files
    # -----------------------------------------------------

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found:\n{CSV_FILE}"
        )

    if not JSONL_FILE.exists():
        raise FileNotFoundError(
            f"JSONL file not found:\n{JSONL_FILE}"
        )

    print("\n[1/5] Loading CSV dataset...")

    csv_records, csv_duplicates = load_csv_records(CSV_FILE)

    print(f"      Normalized records: {len(csv_records)}")
    print(f"      Exact duplicates removed: {csv_duplicates}")

    print("\n[2/5] Loading JSONL dataset...")

    json_records, json_duplicates = load_jsonl_records(JSONL_FILE)

    print(f"      Normalized records: {len(json_records)}")
    print(f"      Exact duplicates removed: {json_duplicates}")

    # -----------------------------------------------------
    # Combine
    # -----------------------------------------------------

    print("\n[3/5] Combining knowledge sources...")

    all_records = csv_records + json_records

    print(f"      Total normalized records: {len(all_records)}")

    # -----------------------------------------------------
    # Validate
    # -----------------------------------------------------

    print("\n[4/5] Validating records...")

    validate_records(all_records)

    print("      Validation successful.")

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    print("\n[5/5] Saving normalized knowledge...")

    save_records(
        all_records,
        OUTPUT_FILE
    )

    print(f"      Output: {OUTPUT_FILE}")

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("NORMALIZATION COMPLETE")
    print("=" * 60)

    print(f"CSV records:       {len(csv_records)}")
    print(f"JSON records:      {len(json_records)}")
    print(f"Total records:     {len(all_records)}")
    print(f"Output file:       {OUTPUT_FILE}")

    print("\nNext stage:")
    print("Normalized knowledge → Chunking → Embeddings")


if __name__ == "__main__":
    main()