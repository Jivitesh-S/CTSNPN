import json
from pathlib import Path
from collections import Counter, defaultdict


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


# =========================================================
# LOAD KNOWLEDGE
# =========================================================

def load_records():

    if not RECORDS_FILE.exists():

        raise FileNotFoundError(
            f"\nKnowledge file not found:\n"
            f"{RECORDS_FILE}\n\n"
            f"Make sure embedded_knowledge.json exists."
        )

    with RECORDS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    if not isinstance(records, list):

        raise ValueError(
            "embedded_knowledge.json must contain a JSON list."
        )

    return records


# =========================================================
# DISPLAY SECTION
# =========================================================

def print_section(title):

    print(
        "\n" + "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


# =========================================================
# SOURCE SUMMARY
# =========================================================

def show_source_summary(records):

    print_section(
        "SOURCE SUMMARY"
    )

    source_names = Counter()

    source_types = Counter()

    for record in records:

        source_names[
            str(
                record.get(
                    "source_name",
                    "MISSING"
                )
            )
        ] += 1

        source_types[
            str(
                record.get(
                    "source_type",
                    "MISSING"
                )
            )
        ] += 1

    print(
        "\nSOURCE TYPES:"
    )

    for source_type, count in source_types.most_common():

        print(
            f"  {source_type}: {count}"
        )

    print(
        "\nSOURCE NAMES:"
    )

    for source_name, count in source_names.most_common():

        print(
            f"  {source_name}: {count}"
        )


# =========================================================
# METADATA SUMMARY
# =========================================================

def show_metadata_summary(records):

    print_section(
        "METADATA SUMMARY"
    )

    metadata_keys = Counter()

    for record in records:

        metadata = record.get(
            "metadata",
            {}
        )

        if isinstance(
            metadata,
            dict
        ):

            for key in metadata.keys():

                metadata_keys[key] += 1

    if not metadata_keys:

        print(
            "\nNo metadata keys were found."
        )

        return

    print(
        "\nMetadata keys:"
    )

    for key, count in metadata_keys.most_common():

        print(
            f"  {key}: {count} records"
        )


# =========================================================
# CATEGORY SUMMARY
# =========================================================

def show_category_summary(records):

    print_section(
        "CATEGORY / INTENT SUMMARY"
    )

    categories = Counter()

    intents = Counter()

    for record in records:

        metadata = record.get(
            "metadata",
            {}
        )

        if not isinstance(
            metadata,
            dict
        ):
            continue

        category = metadata.get(
            "category"
        )

        intent = metadata.get(
            "intent"
        )

        if category:

            categories[
                str(category)
            ] += 1

        if intent:

            intents[
                str(intent)
            ] += 1

    if categories:

        print(
            "\nCATEGORIES:"
        )

        for category, count in categories.most_common():

            print(
                f"  {category}: {count}"
            )

    else:

        print(
            "\nNo category metadata found."
        )

    if intents:

        print(
            "\nINTENTS:"
        )

        for intent, count in intents.most_common(20):

            print(
                f"  {intent}: {count}"
            )

    else:

        print(
            "\nNo intent metadata found."
        )


# =========================================================
# SAMPLE RECORDS BY SOURCE
# =========================================================

def show_source_samples(records):

    print_section(
        "SAMPLE RECORDS BY SOURCE"
    )

    grouped = defaultdict(list)

    for record in records:

        source_name = str(
            record.get(
                "source_name",
                "MISSING"
            )
        )

        if len(
            grouped[source_name]
        ) < 2:

            grouped[source_name].append(
                record
            )

    for source_name, samples in grouped.items():

        print(
            "\n" + "-" * 80
        )

        print(
            f"SOURCE: {source_name}"
        )

        print(
            "-" * 80
        )

        for index, record in enumerate(
            samples,
            start=1
        ):

            print(
                f"\nSample {index}:"
            )

            print(
                f"source_name: "
                f"{record.get('source_name')}"
            )

            print(
                f"source_type: "
                f"{record.get('source_type')}"
            )

            print(
                f"metadata: "
                f"{record.get('metadata')}"
            )

            content = str(
                record.get(
                    "content",
                    ""
                )
            )

            print(
                "\ncontent:"
            )

            print(
                content[:700]
            )


# =========================================================
# RECORD STRUCTURE
# =========================================================

def show_record_structure(records):

    print_section(
        "RECORD STRUCTURE"
    )

    if not records:

        print(
            "No records found."
        )

        return

    first_record = records[0]

    print(
        "\nTop-level fields:"
    )

    for key in first_record.keys():

        print(
            f"  - {key}"
        )

    print(
        "\nFirst complete record:"
    )

    print(
        json.dumps(
            first_record,
            indent=2,
            ensure_ascii=False
        )
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "=" * 80
    )

    print(
        "KNOWLEDGE BASE INSPECTION"
    )

    print(
        "=" * 80
    )

    records = load_records()

    print(
        f"\nTotal knowledge records: "
        f"{len(records)}"
    )

    show_record_structure(
        records
    )

    show_source_summary(
        records
    )

    show_metadata_summary(
        records
    )

    show_category_summary(
        records
    )

    show_source_samples(
        records
    )

    print(
        "\n" + "=" * 80
    )

    print(
        "INSPECTION COMPLETE"
    )

    print(
        "=" * 80
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()