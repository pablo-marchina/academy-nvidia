from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/agents/extractor_agent.py"


def main() -> None:
    text = PATH.read_text(encoding="utf-8-sig")
    old = '''    item: dict[str, Any] = {
        "evidence_id": str(uuid.uuid4()),
'''
    new = '''    item: dict[str, Any] = {
        "evidence_id": str(upstream_evidence_id or uuid.uuid4()),
'''

    if new in text:
        print("[already] upstream evidence identifier is preserved")
        return
    if old not in text:
        raise RuntimeError("Could not locate evidence_id assignment in extractor_agent.py")

    updated = text.replace(old, new, 1)
    ast.parse(updated)
    PATH.write_text(updated, encoding="utf-8")
    print("[fixed] preserve upstream evidence identifier")


if __name__ == "__main__":
    main()
