# Free External Candidate Benchmark Report

Status: `PASS`

- Eligible candidates: 20
- Ready for product benchmark: 1
- Blocked by environment: 19

| Candidate | Status | Decision | Reason |
|---|---|---|---|
| NVIDIA NeMo Retriever Embedding NIM | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| NVIDIA NeMo Retriever Reranker | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| NVIDIA reranker benchmark | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| NVIDIA NeMo Retriever extraction | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| OpenAI Evals | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Opik | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Custom NVIDIA eval harness | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Phoenix | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Langfuse | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Helicone | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| OpenSSF Scorecard | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Sigstore Cosign | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Renovate | READY_FOR_PRODUCT_BENCHMARK | PRODUCT_BENCHMARK_REQUIRED | Candidate is locally available; run a product-output spike before adoption. |
| Dependabot | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Temporal activities | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| A2A / Agent-to-Agent Protocol | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| AGNTCY / Agent Connect | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Firecrawl | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Label Studio | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |
| Argilla | BLOCKED_BY_ENVIRONMENT | BLOCKED_BY_ENVIRONMENT | Candidate is registry-eligible but the local free/open-source tool is not installed or importable. |

## Benchmark Recipes

### NVIDIA NeMo Retriever Embedding NIM

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### NVIDIA NeMo Retriever Reranker

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### NVIDIA reranker benchmark

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### NVIDIA NeMo Retriever extraction

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### OpenAI Evals

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Opik

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Custom NVIDIA eval harness

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Phoenix

- Value hypothesis: Improve product-output evaluation by adding trace-level observability for recommendations, claims, and degraded evidence.
- Metrics: trace_step_coverage, evidence_debuggability, latency_attribution_coverage, failure_root_cause_specificity
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `.venv\Scripts\python.exe -m pip install arize-phoenix`
  - `If Windows native build fails, install Microsoft C++ Build Tools or use a Python version with compatible wheels.`

### Langfuse

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Helicone

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### OpenSSF Scorecard

- Value hypothesis: Improve release/supply-chain output by adding repo risk signals beyond local file checks.
- Metrics: actionable_security_findings, supply_chain_risk_coverage, false_positive_rate, remediation_specificity
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `install OpenSSF Scorecard CLI from its official release channel`

### Sigstore Cosign

- Value hypothesis: Improve release output by adding verifiable artifact signing/provenance evidence.
- Metrics: release_provenance_completeness, verification_reproducibility, manual_release_step_reduction
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `install Cosign CLI from its official release channel`

### Renovate

- Value hypothesis: Improve dependency-maintenance output by producing more actionable update/remediation evidence.
- Metrics: actionable_dependency_updates, security_update_coverage, config_validation_quality, false_positive_rate
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `npm install renovate --save-dev`

### Dependabot

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Temporal activities

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### A2A / Agent-to-Agent Protocol

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### AGNTCY / Agent Connect

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Firecrawl

- Value hypothesis: Evaluate whether this candidate improves final product output quality.
- Metrics: output_quality_delta
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `document candidate-specific activation before benchmark`

### Label Studio

- Value hypothesis: Improve human evaluation output by making claim/recommendation review structured and exportable.
- Metrics: review_schema_fit, unsupported_claim_detection_rate, human_correction_capture, review_export_completeness
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `.venv\Scripts\python.exe -m pip install label-studio`

### Argilla

- Value hypothesis: Improve evaluator feedback output by capturing disagreement, labels, and review datasets.
- Metrics: review_disagreement_capture, dataset_export_completeness, preference_signal_quality, review_workflow_reproducibility
- Benchmark command: `python scripts/run_free_external_candidate_benchmarks.py`
- Activation commands:
  - `.venv\Scripts\python.exe -m pip install argilla`
