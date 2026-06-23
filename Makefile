.PHONY: test test-unit test-integration test-acceptance test-e2e test-slow test-optional lint format-check typecheck validate validate-fast validate-full validate-backend validate-frontend validate-docs validate-output validate-brief-output validate-dashboard-output rag-eval answer-quality-junit answer-quality-llm-judge ci ingest ingest-qdrant ingest-real-sources run-evals run sync-corpus-dry-run sync-corpus corpus-maintenance-dry-run corpus-maintenance-evals corpus-maintenance-ingest regression-dashboard api api-dev api-test ui-install ui-dev ui-build ui-e2e ui-e2e-product product-ui-acceptance db-upgrade db-downgrade db-migrate db-current db-history acceptance acceptance-backend prepare-release product-readiness-report ui-lint ui-lint-fix validate-no-demo setup benchmark benchmark-free-external evidence-pack package-final-release package-release check-repository-clean check-final-release-zip audit-release-package live-collect local-services-up local-proof-doctor doctor full-proof-pass-attempt prove-final-product candidate-governance check-candidate-governance graphrag-direct-benchmark source-quality-direct-benchmark test-security-llm scan-secrets scan-dependencies scan-release check-product-configuration check-no-mock-runtime

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

ingest-real-sources: sync-corpus ingest-qdrant

run-evals: rag-eval

run: api

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
	python -m pytest tests/integration/test_product_api.py tests/integration/test_product_workflow_api.py -v --basetemp .pytest_tmp_api

ui-install:
	cd frontend && npm ci

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

product-ui-acceptance: ui-install ui-build ui-e2e-product

acceptance:
	python -m pytest tests/acceptance/ -m acceptance --tb=short --basetemp .pytest_tmp_acceptance

acceptance-backend:
	python -m pytest tests/acceptance/ -m acceptance --tb=short --basetemp .pytest_tmp_acceptance -k "not e2e"

prepare-release: validate-full acceptance

product-readiness-report:
	python scripts/product_acceptance_report.py --api-url http://localhost:8000

setup:
	python scripts/generate_final_evidence_pack.py
	python scripts/generate_finalization_evidence.py
	python scripts/generate_candidate_governance_final_closure.py

benchmark:
	python scripts/run_benchmark.py

benchmark-free-external:
	python scripts/review_free_external_candidates.py
	python scripts/run_free_external_candidate_benchmarks.py

evidence-pack:
	python scripts/generate_final_evidence_pack.py
	python scripts/generate_finalization_evidence.py
	python scripts/generate_candidate_governance_final_closure.py

candidate-governance:
	python scripts/generate_candidate_governance_final_closure.py

check-candidate-governance:
	python scripts/check_candidate_governance_final_closure.py

graphrag-direct-benchmark:
	python scripts/run_graphrag_direct_benchmark.py

source-quality-direct-benchmark:
	python scripts/run_source_quality_direct_benchmark.py

test-security-llm:
	python scripts/run_llm_security_suite.py

scan-secrets:
	python scripts/check_security_release.py

scan-dependencies:
	python scripts/check_security_release.py

scan-release:
	python scripts/check_final_release_zip.py

check-product-configuration:
	python scripts/check_product_configuration.py

check-no-mock-runtime:
	python scripts/check_no_mock_runtime.py

package-final-release:
	python scripts/package_final_release.py

package-release: package-final-release

check-repository-clean:
	python scripts/check_repository_clean.py

check-final-release-zip:
	python scripts/check_final_release_zip.py

audit-release-package: package-final-release check-final-release-zip

live-collect:
	python scripts/live_collect.py --live

local-services-up:
	docker compose up -d postgres qdrant

local-proof-doctor:
	python scripts/local_proof_doctor.py

doctor: local-proof-doctor

full-proof-pass-attempt:
	python scripts/full_proof_pass_attempt.py

prove-final-product:
	python scripts/prove_final_product.py $(PROVE_ARGS)
