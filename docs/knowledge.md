# Knowledge pipeline (project notes)

This document explains the minimal knowledge pipeline for the MCI Chatbot prototype.

- Place original source files (PDF, HTML snapshots) in `knowledge/sources/`.
- Run `python scripts/ingest.py --source knowledge/sources/<file>` to create a normalized Markdown fragment under `knowledge/normalized/<source_id>/`.
- Run `python scripts/build_index.py` to generate `knowledge/index/index.json` for lightweight retrieval.
- After manual review, move approved fragments into `knowledge/published/` and update `knowledge/sources.yaml` review_status to `approved`.
- The running nanobot will use a read-only retrieval tool to query `knowledge/index/index.json` and return fragments. If no approved fragment exists, it should reply: "現有資料無法回答".

Add more detailed ingestion and HTML/PDF parsing steps when you provide the first PDFs/web snapshots.
