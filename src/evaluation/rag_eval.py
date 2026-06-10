"""Offline RAG Evaluation — retrieval metrics and quality gates.

No external calls, no LLM judge.
Epic 13 adds multi-mode evaluation: lexical, semantic, and hybrid.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation.rag_eval_schemas import (
    ModeEvalResult,
    RagEvalCase,
    RagEvalComparison,
    RagEvalResult,
    RagQualityGateResult,
    RagRetrievalMetrics,
    RetrievalMode,
)
from src.rag.embeddings import EmbeddingProvider, MockEmbeddingProvider
from src.rag.hybrid_retrieval import hybrid_retrieve
from src.rag.retrieval import ChunkIndex, build_default_index
from src.rag.schemas import RetrievalQuery
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.vector_store import InMemoryVectorStore

_GOLDEN_QUERIES_PATH = Path("examples/rag_eval/golden_queries.json")
_EXPECTED_CONTEXTS_PATH = Path("examples/rag_eval/expected_contexts.json")

_GATE_HIT_AT_3 = "hit_at_3_for_critical"
_GATE_TOP_1 = "top_1_for_critical"
_GATE_ZERO_MISSING = "zero_missing_for_known"
_GATE_PROVENANCE = "provenance_check"
_GATE_IRRELEVANT_LIMIT = "irrelevant_below_limit"


def _load_golden_queries(path: Path = _GOLDEN_QUERIES_PATH) -> list[RagEvalCase]:
    """Load golden queries from JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases: list[RagEvalCase] = []
    for item in raw["queries"]:
        q = RetrievalQuery(**item["query"])
        cases.append(
            RagEvalCase(
                case_id=item["case_id"],
                description=item["description"],
                query=q,
                expected_source_ids=item.get("expected_source_ids", []),
                expected_products=item.get("expected_products", []),
                is_critical=item.get("is_critical", False),
                top_k_for_test=item.get("top_k_for_test", 3),
            )
        )
    return cases


def _load_expected_contexts(path: Path = _EXPECTED_CONTEXTS_PATH) -> dict[str, list[str]]:
    """Load expected chunk IDs per case_id."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {k: list(v) for k, v in raw.get("expected_chunks", {}).items()}


def _compute_metrics(
    retrieved: list,
    case: RagEvalCase,
) -> RagRetrievalMetrics:
    """Compute retrieval metrics for a single query against golden expectations.

    missing_context_count counts expected source_ids that did NOT appear
    in the retrieved results. This is top_k-aware: if top_k is smaller than
    the number of expected sources, some sources will naturally be absent.
    """
    total = len(retrieved)
    retrieved_source_ids = {r.source_id for r in retrieved}
    retrieved_products = {r.product for r in retrieved}

    hit_at_k = False
    top_1_expected = False
    if retrieved and case.expected_source_ids:
        hit_at_k = any(s in case.expected_source_ids for s in retrieved_source_ids)
        top_1_expected = retrieved[0].source_id in case.expected_source_ids

    source_coverage = 0.0
    if case.expected_source_ids:
        found_sources = sum(1 for s in case.expected_source_ids if s in retrieved_source_ids)
        source_coverage = found_sources / len(case.expected_source_ids)

    product_coverage = 0.0
    if case.expected_products:
        found_products = sum(1 for p in case.expected_products if p in retrieved_products)
        product_coverage = found_products / len(case.expected_products)

    irrelevant = 0
    if case.expected_source_ids and total > 0:
        for r in retrieved:
            if r.source_id not in case.expected_source_ids:
                irrelevant += 1

    missing = 0
    if case.expected_source_ids:
        missing = sum(1 for s in case.expected_source_ids if s not in retrieved_source_ids)

    precision = 0.0
    if total > 0 and case.expected_source_ids:
        relevant = total - irrelevant
        precision = relevant / total

    return RagRetrievalMetrics(
        hit_at_k=hit_at_k,
        expected_source_coverage=round(source_coverage, 4),
        expected_product_coverage=round(product_coverage, 4),
        irrelevant_context_count=irrelevant,
        missing_context_count=missing,
        top_1_expected_match=top_1_expected,
        context_precision=round(precision, 4),
    )


def _check_provenance(retrieved: list) -> list[str]:
    """Check that all retrieved chunks have source_id and url."""
    failures: list[str] = []
    for r in retrieved:
        reasons: list[str] = []
        if not r.source_id:
            reasons.append(f"missing source_id on chunk {r.chunk_id}")
        if not r.url:
            reasons.append(f"missing url on chunk {r.chunk_id}")
        if reasons:
            failures.append(f"{r.chunk_id}: {'; '.join(reasons)}")
    return failures


def _eval_one_case(
    case: RagEvalCase,
    retrieved: list,
) -> RagEvalResult:
    """Evaluate a single case given its retrieved contexts."""
    metrics = _compute_metrics(retrieved, case)
    failure_reasons: list[str] = []

    if case.is_critical and case.expected_source_ids:
        if not metrics.hit_at_k:
            failure_reasons.append(
                f"critical case '{case.case_id}': hit_at_k=False " f"(top_{case.top_k_for_test})"
            )
        if not metrics.top_1_expected_match:
            failure_reasons.append(f"critical case '{case.case_id}': top_1_expected_match=False")
    if case.expected_source_ids and metrics.missing_context_count > 0:
        failure_reasons.append(
            f"case '{case.case_id}': missing_context_count="
            f"{metrics.missing_context_count} "
            f"(found {len({r.source_id for r in retrieved})}/"
            f"{len(case.expected_source_ids)} expected sources)"
        )
    provenance_issues = _check_provenance(retrieved)
    if provenance_issues:
        failure_reasons.extend(f"provenance: {issue}" for issue in provenance_issues)

    passed = len(failure_reasons) == 0
    if not case.expected_source_ids and len(retrieved) > 0:
        passed = False
        failure_reasons.append(
            f"case '{case.case_id}': expected empty but got {len(retrieved)} results"
        )

    return RagEvalResult(
        case_id=case.case_id,
        case_description=case.description,
        passed=passed,
        is_critical=case.is_critical,
        metrics=metrics,
        retrieved_contexts=retrieved,
        expected_source_ids=case.expected_source_ids,
        expected_products=case.expected_products,
        failure_reasons=failure_reasons,
    )


def run_rag_eval(
    index: ChunkIndex | None = None,
    golden_path: Path = _GOLDEN_QUERIES_PATH,
    expected_path: Path = _EXPECTED_CONTEXTS_PATH,
) -> list[RagEvalResult]:
    """Evaluate all golden queries against a ChunkIndex (lexical mode).

    Returns a list of RagEvalResult, one per query.
    This function is unchanged from Epic 12 for backward compatibility.
    """
    idx = index if index is not None else build_default_index()
    cases = _load_golden_queries(golden_path)

    results: list[RagEvalResult] = []
    for case in cases:
        retrieved = idx.retrieve(case.query, top_k=case.top_k_for_test)
        results.append(_eval_one_case(case, retrieved))

    return results


def run_mode_eval(
    mode: RetrievalMode,
    golden_path: Path = _GOLDEN_QUERIES_PATH,
    *,
    chunk_index: ChunkIndex | None = None,
    vector_store: InMemoryVectorStore | None = None,
    embedding_model: EmbeddingProvider | None = None,
) -> ModeEvalResult:
    """Evaluate golden queries in a single retrieval mode.

    Parameters
    ----------
    mode:
        One of LEXICAL, SEMANTIC, or HYBRID.
    golden_path:
        Path to golden queries JSON.
    chunk_index:
        Required for LEXICAL and HYBRID. Defaults to ``build_default_index()``.
    vector_store:
        Required for SEMANTIC and HYBRID. If empty/None, semantic returns [].
    embedding_model:
        Required for SEMANTIC and HYBRID. If None, uses MockEmbeddingProvider.

    Returns
    -------
    ModeEvalResult
        Evaluation results + quality gates for this mode.
    """
    idx = chunk_index if chunk_index is not None else build_default_index()
    emb = embedding_model if embedding_model is not None else MockEmbeddingProvider()
    cases = _load_golden_queries(golden_path)

    results: list[RagEvalResult] = []
    for case in cases:
        if mode == RetrievalMode.LEXICAL:
            retrieved = idx.retrieve(case.query, top_k=case.top_k_for_test)
        elif mode == RetrievalMode.SEMANTIC:
            if vector_store is None or vector_store.size == 0:
                retrieved = []
            else:
                retrieved = semantic_retrieve(
                    case.query, emb, vector_store, top_k=case.top_k_for_test
                )
        elif mode == RetrievalMode.HYBRID:
            if vector_store is None or vector_store.size == 0:
                retrieved = idx.retrieve(case.query, top_k=case.top_k_for_test)
            else:
                retrieved = hybrid_retrieve(
                    case.query, idx, emb, vector_store, top_k=case.top_k_for_test
                )
        else:
            retrieved = []
        results.append(_eval_one_case(case, retrieved))

    gates = run_quality_gates(results)
    passed = sum(1 for r in results if r.passed)

    return ModeEvalResult(
        mode=mode,
        results=results,
        gates=gates,
        passed_cases=passed,
        total_cases=len(results),
    )


def run_comparison_eval(
    chunk_index: ChunkIndex | None = None,
    vector_store: InMemoryVectorStore | None = None,
    embedding_model: EmbeddingProvider | None = None,
    golden_path: Path = _GOLDEN_QUERIES_PATH,
) -> RagEvalComparison:
    """Run evaluation in all three modes and compare results.

    Detects critical regressions: cases where semantic or hybrid
    fails a critical query that lexical passes.

    Returns
    -------
    RagEvalComparison
        Side-by-side results with regression list.
    """
    lexical = run_mode_eval(
        RetrievalMode.LEXICAL,
        golden_path,
        chunk_index=chunk_index,
        vector_store=vector_store,
        embedding_model=embedding_model,
    )
    semantic = run_mode_eval(
        RetrievalMode.SEMANTIC,
        golden_path,
        chunk_index=chunk_index,
        vector_store=vector_store,
        embedding_model=embedding_model,
    )
    hybrid = run_mode_eval(
        RetrievalMode.HYBRID,
        golden_path,
        chunk_index=chunk_index,
        vector_store=vector_store,
        embedding_model=embedding_model,
    )

    lex_pass = {r.case_id for r in lexical.results if r.passed and r.is_critical}
    regressions: list[str] = []
    for r in semantic.results:
        if r.is_critical and r.case_id in lex_pass and not r.passed:
            regressions.append(f"semantic/{r.case_id}")
    for r in hybrid.results:
        if r.is_critical and r.case_id in lex_pass and not r.passed:
            regressions.append(f"hybrid/{r.case_id}")

    return RagEvalComparison(
        lexical=lexical,
        semantic=semantic,
        hybrid=hybrid,
        critical_regressions=regressions,
    )


def run_quality_gates(
    eval_results: list[RagEvalResult],
) -> list[RagQualityGateResult]:
    """Run all quality gates over evaluation results."""
    gates: list[RagQualityGateResult] = []

    critical_hits: list[str] = [
        r.case_id
        for r in eval_results
        if r.is_critical and r.expected_source_ids and not r.metrics.hit_at_k
    ]
    gates.append(
        RagQualityGateResult(
            gate_name=_GATE_HIT_AT_3,
            passed=len(critical_hits) == 0,
            details=(
                f"{len(critical_hits)} critical cases failed hit_at_k"
                if critical_hits
                else "all critical cases pass hit_at_k"
            ),
            failed_cases=critical_hits,
        )
    )

    critical_top1: list[str] = [
        r.case_id
        for r in eval_results
        if r.is_critical and r.expected_source_ids and not r.metrics.top_1_expected_match
    ]
    gates.append(
        RagQualityGateResult(
            gate_name=_GATE_TOP_1,
            passed=len(critical_top1) == 0,
            details=(
                f"{len(critical_top1)} critical cases failed top_1_expected_match"
                if critical_top1
                else "all critical cases pass top_1_expected_match"
            ),
            failed_cases=critical_top1,
        )
    )

    missing_known: list[str] = [
        r.case_id
        for r in eval_results
        if r.expected_source_ids and r.metrics.missing_context_count > 0
    ]
    gates.append(
        RagQualityGateResult(
            gate_name=_GATE_ZERO_MISSING,
            passed=len(missing_known) == 0,
            details=(
                f"{len(missing_known)} known queries have missing contexts"
                if missing_known
                else "all known queries have zero missing contexts"
            ),
            failed_cases=missing_known,
        )
    )

    provenance_fails: list[str] = []
    for r in eval_results:
        for ctx in r.retrieved_contexts:
            if not ctx.source_id or not ctx.url:
                provenance_fails.append(r.case_id)
                break
    gates.append(
        RagQualityGateResult(
            gate_name=_GATE_PROVENANCE,
            passed=len(provenance_fails) == 0,
            details=(
                f"{len(provenance_fails)} cases have provenance issues"
                if provenance_fails
                else "all retrieved contexts have provenance"
            ),
            failed_cases=provenance_fails,
        )
    )

    irrelevant_over: list[str] = []
    for r in eval_results:
        if r.expected_source_ids and r.metrics.irrelevant_context_count > 1:
            irrelevant_over.append(r.case_id)
    gates.append(
        RagQualityGateResult(
            gate_name=_GATE_IRRELEVANT_LIMIT,
            passed=len(irrelevant_over) <= 1,
            details=(
                f"{len(irrelevant_over)} cases exceed irrelevant limit"
                if irrelevant_over
                else "irrelevant context count within limit"
            ),
            failed_cases=irrelevant_over,
        )
    )

    return gates


def format_eval_summary(
    results: list[RagEvalResult],
    gates: list[RagQualityGateResult],
) -> str:
    """Return a human-readable summary of RAG evaluation results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    lines: list[str] = [
        f"RAG Evaluation: {passed}/{total} cases passed",
        "",
    ]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"  [{status}] {r.case_id}: {r.case_description}")
        if not r.passed:
            for reason in r.failure_reasons:
                lines.append(f"         - {reason}")

    lines.append("")
    lines.append("Quality Gates:")
    for g in gates:
        status = "PASS" if g.passed else "FAIL"
        lines.append(f"  [{status}] {g.gate_name}: {g.details}")

    return "\n".join(lines)


def format_comparison_summary(comparison: RagEvalComparison) -> str:
    """Format a multi-mode evaluation comparison as human-readable text."""
    lines: list[str] = []
    for mode_result in [comparison.lexical, comparison.semantic, comparison.hybrid]:
        lines.append(f"=== {mode_result.mode.value.upper()} ===")
        lines.append(format_eval_summary(mode_result.results, mode_result.gates))
        lines.append("")

    lines.append("=== REGRESSION CHECK ===")
    if comparison.critical_regressions:
        lines.append(f"REGRESSIONS ({len(comparison.critical_regressions)}):")
        for reg in comparison.critical_regressions:
            lines.append(f"  - {reg}")
    else:
        lines.append("No critical regressions detected.")

    return "\n".join(lines)
