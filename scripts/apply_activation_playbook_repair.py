from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/orchestration/node_impl.py"


def main() -> None:
    text = PATH.read_text(encoding="utf-8-sig")
    pattern = (
        r'@_register\("match_activation_playbooks",\s*'
        r'"Match activation playbooks to diagnosed gaps",\s*critical=True\)'
    )
    replacement = (
        '@_register("match_activation_playbooks", '
        '"Match activation playbooks to diagnosed gaps", critical=False)'
    )

    if replacement in text:
        print("[already] activation playbook abstention is nonfatal")
        return

    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError("Could not locate critical activation playbook decorator")

    ast.parse(updated)
    PATH.write_text(updated, encoding="utf-8")
    print("[fixed] activation playbook abstention is nonfatal")


if __name__ == "__main__":
    main()
