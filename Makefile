.PHONY: test lint format-check typecheck validate rag-eval answer-quality-junit answer-quality-llm-judge ci ingest ingest-qdrant sync-corpus-dry-run sync-corpus corpus-maintenance-dry-run corpus-maintenance-evals corpus-maintenance-ingest regression-dashboard

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

answer-quality-junit:
	python -c "from pathlib import Path; Path('data/regression_reports').mkdir(parents=True, exist_ok=True)"
	python -m pytest tests/evals/test_answer_quality_golden.py --junit-xml=data/regression_reports/answer_quality_eval_junit.xml

answer-quality-llm-judge:
	@echo "Running optional/experimental Answer Quality LLM judge with offline null provider."
	python scripts/run_answer_quality_llm_judge.py

ci: validate

ingest:
	python scripts/ingest_nvidia_corpus.py --mock-embeddings --backend in_memory --dry-run

ingest-qdrant:
	python scripts/ingest_nvidia_corpus.py

sync-corpus-dry-run:
	python scripts/sync_nvidia_sources.py --dry-run

sync-corpus:
	python scripts/sync_nvidia_sources.py --staging-only

corpus-maintenance-dry-run:
	python scripts/run_corpus_maintenance.py --run-sync --no-run-ingestion --no-run-evals --no-promote-sources --no-recreate-collection --no-fail-on-stale --fail-on-expired

corpus-maintenance-evals:
	python scripts/run_corpus_maintenance.py --run-sync --no-run-ingestion --run-evals --no-promote-sources --no-recreate-collection --no-fail-on-stale --fail-on-expired

corpus-maintenance-ingest:
	python scripts/run_corpus_maintenance.py --run-sync --run-ingestion --run-evals --no-promote-sources --no-recreate-collection --no-fail-on-stale --fail-on-expired

regression-dashboard:
	python scripts/build_regression_dashboard.py
