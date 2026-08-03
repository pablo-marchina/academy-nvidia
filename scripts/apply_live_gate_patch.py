#!/usr/bin/env python3
"""Add the mandatory fuzzy-matching dependency and fail-closed live gate."""
from pathlib import Path

pyproject = Path("pyproject.toml")
text = pyproject.read_text(encoding="utf-8")
old = '  "trafilatura",\n  "playwright",\n'
new = '  "trafilatura",\n  "rapidfuzz>=3.0",\n  "playwright",\n'
if new not in text:
    if old not in text:
        raise RuntimeError("pyproject dependency insertion point not found")
    pyproject.write_text(text.replace(old, new, 1), encoding="utf-8")

script = Path("scripts/validate_live_outputs.py")
text = script.read_text(encoding="utf-8")
helper_marker = "\ndef main() -> int:\n"
helper = '''\n\ndef _validation_exit_code(results: list[dict[str, Any]]) -> int:
    """Return success only when every sampled company passes all checks."""
    return 0 if results and all(bool(item.get("passed")) for item in results) else 1
'''
if "def _validation_exit_code" not in text:
    if helper_marker not in text:
        raise RuntimeError("live validation main marker not found")
    text = text.replace(helper_marker, helper + helper_marker, 1)
old_return = "    return 0 if successful_outputs else 1\n"
new_return = "    return _validation_exit_code(results)\n"
if new_return not in text:
    if old_return not in text:
        raise RuntimeError("live validation return pattern not found")
    text = text.replace(old_return, new_return, 1)
script.write_text(text, encoding="utf-8")

Path(__file__).unlink()
print("added rapidfuzz core dependency and strict live validation exit gate")
