#!/usr/bin/env python3
"""Apply the one-time missing functools import fix."""
from pathlib import Path

path = Path("src/rag/rag_service_factory.py")
text = path.read_text(encoding="utf-8")
old = "from datetime import UTC, datetime\nimport math\n"
new = "from datetime import UTC, datetime\nfrom functools import lru_cache\nimport math\n"
if new not in text:
    if old not in text:
        raise RuntimeError("rag_service_factory import block not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
Path(__file__).unlink()
print("added functools.lru_cache import")
