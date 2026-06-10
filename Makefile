.PHONY: test lint format-check typecheck validate rag-eval ci

test:
	python -m pytest -m "not integration" --tb=short

lint:
	ruff check .

format-check:
	black --check .

typecheck:
	mypy src

validate: lint format-check typecheck test

rag-eval:
	python -m pytest tests/unit/test_rag_eval.py tests/unit/test_rag_eval_semantic.py tests/unit/test_rag_eval_reranking.py --tb=short

ci: validate
