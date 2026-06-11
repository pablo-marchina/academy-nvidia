# Answer Quality Evaluation

**Epic 23** | **Date:** 2026-06-11

## Objective

Evaluate the final `StartupActionBrief` answer quality offline, with deterministic
metrics and gates. The harness verifies that the brief stays anchored in startup
evidence, diagnosed gaps, deterministic NVIDIA recommendations, and packed RAG
context without allowing unsupported claims.

This epic does not change scoring, diagnosis, recommendation, retrieval, Qdrant, or
`recommended_motion`.

## Architecture

```
examples/answer_quality/
  golden_answer_quality_cases.json

src/evaluation/
  answer_quality_schemas.py
  answer_quality_eval.py

tests/evals/
  test_answer_quality_golden.py
```

The evaluator consumes a structured `StartupActionBrief` plus an
`AnswerQualityEvalCase`. Tests build briefs from the existing golden pipeline cases,
then apply negative in-memory mutations to prove that gates fail or warn as expected.

## Schemas

- `AnswerQualityEvalCase`
- `AnswerQualityEvalResult`
- `AnswerQualityMetrics`
- `UnsupportedClaim`
- `RequiredSectionCheck`
- `EvidenceCoverageCheck`
- `AnswerQualityGateResult`

## Metrics

- `required_sections_present`
- `missing_evidence_preserved`
- `uncertainty_preserved`
- `recommended_motion_consistent`
- `required_evidence_ids_present`
- `required_gap_ids_present`
- `required_technology_ids_present`
- `unsupported_claim_count`
- `rag_context_citation_coverage`
- `startup_evidence_citation_coverage`
- `forbidden_absolute_language_count`
- `answer_quality_status`

## Quality Gates

`FAIL` when:

- a required section is missing
- expected `missing_evidence` is omitted
- expected uncertainty is omitted, including low-confidence cases
- a NVIDIA technology appears without a corresponding diagnosed gap
- `recommended_motion` changes unexpectedly
- `unsupported_claim_count` exceeds the case limit
- required evidence, gap, or technology identifiers are missing

`WARN` when:

- RAG or startup evidence citation coverage is below the case threshold
- forbidden absolute language appears above the case threshold

`PASS` when all blocking gates pass and no warning gate fires.

## Golden Cases

- `high_fit_supported_answer`
- `weak_evidence_preserved`
- `non_ai_no_nvidia_push`
- `rag_context_good_gap`
- `gap_without_rag_context`
- `low_confidence_validate_manually`
- `irrelevant_or_conflicting_rag_context`
- `required_missing_evidence`

## Running

```bash
pytest tests/evals/test_answer_quality_golden.py -q
```

Para gerar o JUnit consumido pelo dashboard:

```bash
pytest tests/evals/test_answer_quality_golden.py --junit-xml=data/regression_reports/answer_quality_eval_junit.xml
```

Ou:

```bash
make answer-quality-junit
```

The tests run offline using existing golden fixtures, `MockEmbeddingProvider`, and
in-memory RAG/vector-store helpers already used by the golden pipeline evals.

## Dashboard Integration

`scripts/build_regression_dashboard.py` reads `answer_quality_eval_junit.xml` when
present in a corpus maintenance reports directory or at
`data/regression_reports/answer_quality_eval_junit.xml`. It exposes:

- `answer_quality_junit_present`
- `answer_quality_tests`
- `answer_quality_failures`
- `answer_quality_errors`
- `answer_quality_skipped`
- `answer_quality_passed`
- `answer_quality_failed_cases`
- `unsupported_claim_count`
- `required_sections_missing`
- `citation_coverage`
- `answer_quality_status`

Missing answer quality JUnit is controlled: the dashboard does not crash and marks
Answer Quality as `WARN`/not present unless a generated XML is available.

## RAGAS and LangSmith Relationship

This is a deterministic local analogue of common RAG quality dimensions:

- faithfulness / groundedness -> unsupported claim checks and citation coverage
- answer relevancy -> required gaps, technologies, and sections
- completeness -> missing evidence and uncertainty preservation
- honesty -> low-confidence cases must retain limitations

It does not provide semantic entailment, hosted traces, or judge-model scoring.

## Optional LLM Judge

Epic 23.2 adds an optional experimental judge adapter documented in
`docs/48_optional_llm_judge.md`. It can track:

- `faithfulness_score`
- `answer_relevancy_score`
- `groundedness_score`
- `completeness_score`
- `uncertainty_honesty_score`
- `executive_usefulness_score`

The only implemented provider is `NullLLMJudgeProvider`, which is offline and
deterministic. The judge is manual, informational, and not a CI gate. It does not
alter deterministic metrics, quality gates, JUnit XML, scoring, diagnosis,
recommendation, retrieval, or Action Brief logic.

## Limitations

- Unsupported-claim detection is pattern-based and only catches golden-case
  expectations.
- Citation coverage confirms presence of source/provenance, not full semantic
  entailment.
- The harness evaluates final answer quality; it does not improve generation logic.
- Optional LLM judge reports are experimental and informational; the null provider
  does not provide semantic model judgment.
