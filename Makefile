.PHONY: test test-unit test-integration test-acceptance test-e2e test-slow test-optional lint format-check typecheck validate validate-fast validate-full validate-backend validate-frontend validate-docs validate-output validate-brief-output validate-dashboard-output rag-eval answer-quality-junit answer-quality-llm-judge ci ingest ingest-qdrant sync-corpus-dry-run sync-corpus corpus-maintenance-dry-run corpus-maintenance-evals corpus-maintenance-ingest regression-dashboard api api-dev api-test ui-install ui-dev ui-build ui-e2e ui-e2e-product demo-acceptance demo-full-check demo-full demo-cli demo-cli-offline demo-cli-rag db-upgrade db-downgrade db-migrate db-current db-history acceptance acceptance-backend prepare-release product-readiness-report ui-lint ui-lint-fix validate-no-demo

test:
	python -m pytest -m "not (integration or acceptance or e2e or slow or optional or external_service)" --tb=short

test-unit: test

test-integration:
	python -m pytest -m integration --tb=short

test-slow:
	python -m pytest -m slow --tb=short

test-optional:
	python -m pytest -m optional --tb=short

.PHONY: db-upgrade
db-upgrade:
	alembic upgrade head

.PHONY: db-downgrade
db-downgrade:
	alembic downgrade -1

.PHONY: db-migrate
db-migrate:
	alembic revision --autogenerate -m "$(msg)"

.PHONY: db-current
db-current:
	alembic current

.PHONY: db-history
db-history:
	alembic history

lint:
	ruff check .

format-check:
	black --check .

typecheck:
	mypy src

validate: lint format-check typecheck test

validate-fast: lint format-check typecheck test

validate-backend: validate-fast

validate-frontend: ui-lint ui-build

validate-no-demo:
	python scripts/check_no_demo_dependency.py

validate-docs:
	python scripts/check_scope.py && python scripts/check_docs_closure.py

validate-full: validate-fast validate-docs validate-frontend

validate-output:
	python -m pytest tests/unit/test_output_validation.py --tb=short

validate-brief-output:
	python -m pytest tests/unit/test_output_validation.py -k "brief" --tb=short

validate-dashboard-output:
	python -m pytest tests/unit/test_output_validation.py -k "dashboard" --tb=short

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

api:
	uvicorn src.api.main:app

api-dev:
	uvicorn src.api.main:app --reload

api-test:
	python -m pytest tests/integration/test_api_demo.py tests/integration/test_demo_acceptance.py -v

ui-install:
	cd frontend && npm install --no-package-lock

ui-dev:
	cd frontend && npm run dev

ui-build:
	cd frontend && npm run build

ui-lint:
	cd frontend && npx tsc --noEmit

ui-lint-fix:
	cd frontend && npx tsc --noEmit

ui-e2e:
	cd frontend && npm run test:e2e

ui-e2e-product:
	cd frontend && npm run test:e2e:product

demo-acceptance: api-test ui-install ui-build ui-e2e

demo-full-check: demo-acceptance

acceptance:
	python -m pytest tests/acceptance/ -m acceptance --tb=short --basetemp .pytest_tmp_acceptance

acceptance-backend:
	python -m pytest tests/acceptance/ -m acceptance --tb=short --basetemp .pytest_tmp_acceptance -k "not e2e"

prepare-release: validate-full acceptance

product-readiness-report:
	python scripts/product_acceptance_report.py --api-url http://localhost:8000

demo-full:
	@echo "Run the local demo in two terminals:"
	@echo "  make api-dev"
	@echo "  make ui-dev"

demo-cli:
	python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json

demo-cli-offline:
	python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json --offline

demo-cli-rag:
	python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json --use-rag --rag-backend local
