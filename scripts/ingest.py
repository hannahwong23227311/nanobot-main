"""Simple ingest script template for the MCI Chatbot knowledge pipeline.

Usage (fill source files into knowledge/sources/ then run):
    python scripts/ingest.py --source knowledge/sources/mci_selfcare.pdf

This is a lightweight template — replace PDF/HTML parsing with project-preferred libraries.
"""
from pathlib import Path
import argparse

KB_ROOT = Path(__file__).resolve().parents[1] / "knowledge"
SOURCES_DIR = KB_ROOT / "sources"
NORMALIZED_DIR = KB_ROOT / "normalized"

NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(path: Path) -> str:
    # Placeholder: integrate pdfminer.six or tika for full extraction
    return f"[extracted text from {path.name}]"


def extract_text_from_html(path: Path) -> str:
    # Placeholder: integrate BeautifulSoup to clean HTML
    return f"[extracted text from {path.name}]"


def write_normalized(source_id: str, title: str, content: str):
    out_dir = NORMALIZED_DIR / source_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "00_raw.md"
    out_path.write_text(f"# {title}\n\n{content}")
    print(f"Wrote normalized fragment: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to source file under knowledge/sources/")
    args = parser.parse_args()
    src = Path(args.source)
    if not src.exists():
        print("Source not found:", src)
        return
    if src.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(src)
    else:
        text = extract_text_from_html(src)
    source_id = src.stem
    write_normalized(source_id, src.name, text)


if __name__ == "__main__":
    main()
