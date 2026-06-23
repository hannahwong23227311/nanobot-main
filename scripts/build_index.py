"""Build a lightweight JSON index from `knowledge/normalized/` fragments.

This produces `knowledge/index/index.json` containing metadata for simple retrieval.
"""
from pathlib import Path
import json

KB_ROOT = Path(__file__).resolve().parents[1] / "knowledge"
NORMALIZED_DIR = KB_ROOT / "normalized"
INDEX_DIR = KB_ROOT / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)


def build_index():
    index = []
    for source_dir in NORMALIZED_DIR.iterdir():
        if not source_dir.is_dir():
            continue
        for md in source_dir.glob("*.md"):
            content = md.read_text(encoding="utf8")
            index.append({
                "id": f"{source_dir.name}/{md.name}",
                "source": source_dir.name,
                "path": str(md.relative_to(KB_ROOT)),
                "text_preview": content[:400]
            })
    out = INDEX_DIR / "index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"Wrote index: {out} (entries={len(index)})")


if __name__ == "__main__":
    build_index()
