from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/rag/rag_service_factory.py"
text = path.read_text(encoding="utf-8")
old = "from functools import lru_cache\nimport math\nfrom typing import Any\n"
new = "from functools import lru_cache\nimport math\nimport os\nfrom typing import Any\n"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one import block, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
