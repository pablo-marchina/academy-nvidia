#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.load_product_env import load_product_env
from src.rag.ingestion_pipeline import check_corpus_readiness
from src.rag.qdrant_store import build_qdrant_store


def _readiness_payload() -> tuple[bool, dict[str, object]]:
    store = build_qdrant_store()
    readiness = check_corpus_readiness(store)
    return readiness.production_allowed, asdict(readiness)


def main() -> int:
    load_product_env()
    ready, payload = _readiness_payload()
    if ready:
        print(json.dumps({"status": "already_ready", "readiness": payload}, indent=2))
        return 0

    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "ingest_nvidia_corpus.py"),
        "--recreate-collection",
        "--require-real-embeddings",
        "--fail-on-validation-error",
        "--report-path",
        str(PROJECT_ROOT / "data" / "product" / "nvidia_corpus_ingestion_report.json"),
    ]
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if completed.returncode != 0:
        return completed.returncode

    ready, payload = _readiness_payload()
    print(json.dumps({"status": "ready" if ready else "blocked", "readiness": payload}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
