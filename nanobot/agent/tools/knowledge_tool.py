"""Read-only knowledge retrieval tool for the MCI Chatbot prototype.

This tool performs simple keyword-based retrieval over the lightweight
index produced by `scripts/build_index.py` (knowledge/index/index.json).

Behavioral notes:
- Read-only: never writes to the knowledge tree.
- Returns top-N fragments with source id, path, score and a short snippet.
- The runner should refuse generation when no approved fragments are found.

This is a minimal, easy-to-understand tool suitable for the prototype. It can
be replaced later with a vector-based retrieval implementation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Any


KB_ROOT = Path(__file__).resolve().parents[3] / "knowledge"
INDEX_PATH = KB_ROOT / "index" / "index.json"


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())


class KnowledgeRetrievalTool:
    """Simple retrieval over `knowledge/index/index.json`.

    Intended for prototype use only. Matching is a case-insensitive
    token overlap score between the query and each indexed fragment's
    `text_preview`.
    """

    def __init__(self, index_path: Path | None = None):
        self.index_path = Path(index_path) if index_path else INDEX_PATH
        self._index = None

    def _load_index(self) -> List[Dict[str, Any]]:
        if self._index is not None:
            return self._index

        # Build a list of candidate index paths (configured path + sensible fallbacks)
        tried_paths = [self.index_path]
        if not self.index_path.exists():
            tried_paths.append(Path.cwd() / "knowledge" / "index" / "index.json")
            p = Path.cwd()
            for _ in range(4):
                p = p.parent
                tried_paths.append(p / "knowledge" / "index" / "index.json")

        for p in tried_paths:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf8") as f:
                        self._index = json.load(f)
                        # remember the successful path for future calls
                        self.index_path = p
                        break
                except Exception as e:
                    # surface JSON / encoding errors in CI logs for diagnosis
                    import sys

                    print(
                        f"KnowledgeRetrievalTool: error loading index from {p!s}: {e!r}",
                        file=sys.stderr,
                    )
                    # continue to next candidate path
                    continue

        if self._index is None:
            # nothing worked — be explicit in logs so CI shows why search returned no results
            import sys

            print(
                f"KnowledgeRetrievalTool: index not found; attempted paths: {[str(x) for x in tried_paths]}",
                file=sys.stderr,
            )
            self._index = []
        return self._index

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return up to `top_k` matching fragments.

        Each result contains: `id`, `path`, `source`, `score`, `text_preview`.
        """
        if not query or not query.strip():
            return []
        tokens = _tokenize(query)
        if not tokens:
            return []

        index = self._load_index()
        scored = []
        for entry in index:
            preview = (entry.get("text_preview") or "").lower()
            preview_tokens = _tokenize(preview)
            # simple overlap score
            score = sum(preview_tokens.count(t) for t in tokens)
            if score > 0:
                scored.append({"entry": entry, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        results = []
        for item in scored[:top_k]:
            e = item["entry"]
            results.append(
                {
                    "id": e.get("id"),
                    "path": e.get("path"),
                    "source": e.get("source"),
                    "score": item["score"],
                    "text_preview": e.get("text_preview"),
                }
            )

        # If token-overlap on previews produced no results, fall back to
        # searching the full fragment files referenced by the index (or the
        # normalized fragments in the repo). This helps CI tests pass when
        # index.json isn't available or previews don't contain the query.
        if not results:
            q = query.strip().lower()
            fallback = []
            # If the index is empty, still attempt to scan normalized/ to find
            # matching fragments (helps CI where index.json may be missing).
            entries_to_scan = index if index else []
            if not entries_to_scan:
                # scan the normalized directory under KB_ROOT
                norm_dir = KB_ROOT / "normalized"
                if norm_dir.exists():
                    for p in norm_dir.rglob("*.md"):
                        try:
                            text = p.read_text(encoding="utf8")
                        except Exception:
                            continue
                        if q in text.lower():
                            fallback.append({
                                "id": p.name,
                                "path": str(p.relative_to(KB_ROOT)),
                                "source": "fallback",
                                "score": 1,
                                "text_preview": None,
                            })
                            if len(fallback) >= top_k:
                                break
            else:
                for entry in entries_to_scan:
                    p = entry.get("path")
                    if not p:
                        continue
                    full = KB_ROOT / Path(p)
                    try:
                        text = full.read_text(encoding="utf8")
                    except Exception:
                        continue
                    if q in text.lower():
                        fallback.append({
                            "id": entry.get("id"),
                            "path": entry.get("path"),
                            "source": entry.get("source"),
                            "score": 1,
                            "text_preview": entry.get("text_preview"),
                        })
                        if len(fallback) >= top_k:
                            break
            if fallback:
                return fallback

        return results

    def get_fragment_text(self, path: str) -> str | None:
        """Read and return the full fragment text for a normalized fragment path.

        `path` is relative to `knowledge/` as stored in the index (e.g.
        `normalized/mci_selfcare/00_raw.md`). Returns None if not found.
        """
        full = KB_ROOT / Path(path)
        try:
            return full.read_text(encoding="utf8")
        except Exception:
            return None


if __name__ == "__main__":
    # simple CLI for quick testing
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("query", help="Query text")
    p.add_argument("--k", type=int, default=3, help="Top K results")
    args = p.parse_args()
    tool = KnowledgeRetrievalTool()
    res = tool.search(args.query, top_k=args.k)
    print(json.dumps(res, ensure_ascii=False, indent=2))
