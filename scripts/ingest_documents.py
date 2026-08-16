import json
import re
from pathlib import Path

from pypdf import PdfReader


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "raw" / "documents"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "document_knowledge.json"
)


# ---------------------------------------------------------
# Chunk configuration
# ---------------------------------------------------------

TARGET_CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normalize extracted document text.
    """

    if not text:
        return ""

    # Normalize line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------
# Paragraph extraction
# ---------------------------------------------------------

def split_into_paragraphs(text: str) -> list[str]:
    """
    Split document text into paragraph-like units.
    """

    cleaned = clean_text(text)

    if not cleaned:
        return []

    paragraphs = re.split(r"\n\s*\n", cleaned)

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

def create_chunks(
    paragraphs: list[str],
    target_size: int = TARGET_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Combine paragraphs into chunks of approximately
    target_size characters while preserving paragraph
    boundaries as much as possible.

    A small overlap is retained between consecutive chunks.
    """

    if not paragraphs:
        return []

    if target_size <= 0:
        raise ValueError("target_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= target_size:
        raise ValueError(
            "overlap must be smaller than target_size."
        )

    chunks: list[str] = []
    current_paragraphs: list[str] = []
    current_length = 0

    for paragraph in paragraphs:

        paragraph_length = len(paragraph)

        # If the current chunk already contains content,
        # determine whether adding this paragraph would make
        # the chunk too large.
        if (
            current_paragraphs
            and current_length + paragraph_length + 2 > target_size
        ):
            chunk = "\n\n".join(current_paragraphs)
            chunks.append(chunk)

            # -------------------------------------------------
            # Create overlap from the end of the previous chunk.
            # -------------------------------------------------

            overlap_text = chunk[-overlap:] if overlap > 0 else ""

            if overlap_text:
                current_paragraphs = [overlap_text]
                current_length = len(overlap_text)
            else:
                current_paragraphs = []
                current_length = 0

        # -----------------------------------------------------
        # Handle a paragraph larger than target size.
        # -----------------------------------------------------

        if paragraph_length > target_size:

            # If there is already content, preserve it first.
            if current_paragraphs:
                chunk = "\n\n".join(current_paragraphs)
                chunks.append(chunk)

                current_paragraphs = []
                current_length = 0

            # Split the oversized paragraph into fixed-size
            # pieces.
            start = 0

            while start < paragraph_length:

                end = min(
                    start + target_size,
                    paragraph_length
                )

                piece = paragraph[start:end].strip()

                if piece:
                    chunks.append(piece)

                if end >= paragraph_length:
                    break

                start = end - overlap

            continue

        # -----------------------------------------------------
        # Add normal paragraph to current chunk.
        # -----------------------------------------------------

        current_paragraphs.append(paragraph)

        current_length = sum(
            len(item)
            for item in current_paragraphs
        ) + max(
            0,
            len(current_paragraphs) - 1
        ) * 2

    # ---------------------------------------------------------
    # Add remaining content.
    # ---------------------------------------------------------

    if current_paragraphs:

        chunk = "\n\n".join(current_paragraphs)

        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks


# ---------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------

def extract_pdf_pages(
    pdf_path: Path
) -> list[dict]:
    """
    Extract text page-by-page from a PDF.

    Returns a list containing:

        {
            "page": page_number,
            "text": extracted_text
        }
    """

    reader = PdfReader(str(pdf_path))

    pages: list[dict] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        text = clean_text(text)

        if not text:
            continue

        pages.append(
            {
                "page": page_number,
                "text": text,
            }
        )

    return pages


# ---------------------------------------------------------
# Convert PDF to knowledge records
# ---------------------------------------------------------

def process_pdf(
    pdf_path: Path
) -> list[dict]:
    """
    Extract and chunk one PDF into normalized
    knowledge records.
    """

    pages = extract_pdf_pages(pdf_path)

    records: list[dict] = []

    for page_data in pages:

        page_number = page_data["page"]
        page_text = page_data["text"]

        paragraphs = split_into_paragraphs(page_text)

        chunks = create_chunks(paragraphs)

        for chunk_index, chunk in enumerate(
            chunks,
            start=1
        ):

            record = {
                "content": chunk,
                "source_type": "user_document",
                "source_name": pdf_path.name,
                "metadata": {
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "file_type": "pdf",
                },
            }

            records.append(record)

    return records


# ---------------------------------------------------------
# Save records
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
# Main
# ---------------------------------------------------------

def main() -> None:

    print("=" * 60)
    print("USER DOCUMENT INGESTION")
    print("=" * 60)

    if not DOCUMENTS_DIR.exists():

        raise FileNotFoundError(
            f"Document directory not found:\n"
            f"{DOCUMENTS_DIR}"
        )

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    if not pdf_files:

        raise FileNotFoundError(
            "No PDF files were found in:\n"
            f"{DOCUMENTS_DIR}"
        )

    all_records: list[dict] = []

    print(
        f"\nFound {len(pdf_files)} PDF file(s)."
    )

    for pdf_file in pdf_files:

        print(
            f"\nProcessing: {pdf_file.name}"
        )

        records = process_pdf(pdf_file)

        print(
            f"  Generated chunks: {len(records)}"
        )

        all_records.extend(records)

    save_records(
        all_records,
        OUTPUT_FILE
    )

    print("\n" + "=" * 60)
    print("DOCUMENT INGESTION COMPLETE")
    print("=" * 60)

    print(
        f"Total document chunks: {len(all_records)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        "\nNext stage:"
        " document chunks + dataset records"
        " → unified knowledge"
    )


if __name__ == "__main__":
    main()