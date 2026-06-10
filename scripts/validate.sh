#!/usr/bin/env bash
set -euo pipefail

echo "=== validate.sh ==="
echo "Running full local validation..."
echo ""

echo "--- ruff check . ---"
ruff check .
echo "PASS"
echo ""

echo "--- black --check . ---"
black --check .
echo "PASS"
echo ""

echo "--- mypy src ---"
mypy src
echo "PASS"
echo ""

echo "--- pytest (unit only) ---"
python -m pytest -m "not integration" --tb=short
echo "PASS"
echo ""

echo "=== All validations passed. ==="
