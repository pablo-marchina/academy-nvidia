.PHONY: test lint format-check typecheck validate rag-eval ci ingest ingest-qdrant sync-corpus-dry-run sync-corpus

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

ingest:
	python scripts/ingest_nvidia_corpus.py --mock-embeddings --backend in_memory --dry-run

ingest-qdrant:
	python scripts/ingest_nvidia_corpus.py

sync-corpus-dry-run:
	python scripts/sync_nvidia_sources.py --dry-run

sync-corpus:
	python scripts/sync_nvidia_sources.py --staging-only
