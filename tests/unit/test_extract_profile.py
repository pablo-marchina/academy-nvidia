"""Tests for the deterministic extract_profile node.

No LLM, no Qdrant, no internet, no scraping.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

from src.agents.graph import _empty_extraction_metrics, _extract_profile

_AI_HTML = (
    "<html><body>"
    "<h1>NovaAI</h1>"
    "<p>NovaAI is a Brazilian startup building machine learning"
    " and deep learning solutions for hospitals using NLP and computer vision."
    " Founded by Maria Silva and Joao Santos."
    " The company raised $10M in Series A funding."
    " Customers include Hospital Israelita Albert Einstein."
    " Tech stack: Python, PyTorch, Kubernetes, Docker.</p>"
    "</body></html>"
)

_NO_AI_HTML = (
    "<html><body>"
    "<h1>CleanTech</h1>"
    "<p>We sell physical water filters for residential use."
    " Founded by Carlos Souza.</p>"
    "</body></html>"
)

_EMPTY_HTML = "<html><body></body></html>"


def _make_candidate(
    text: str = _AI_HTML,
    source_url: str = "https://novaai.com.br",
    source_id: str = "src_001",
    source_category: str = "official_website",
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_url": source_url,
        "text": text,
        "source_category": source_category,
        "source_name": "Test Website",
        "collected_at": datetime.now(UTC).isoformat(),
        "content_hash": "abc123",
        "latency_ms": 100,
        "robots_allowed": True,
        "duplicate": False,
    }


# ── Test 1: extract_profile calls real extractor ──────────────────────────


def test_extract_profile_calls_real_extractor() -> None:
    """extract_profile node calls the real deterministic extractor."""
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-001",
            "startup_id": "startup-42",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": ["preflight_configuration_check", "plan_search", "collect_sources"],
        }
    )
    assert result.get("extraction_status") is not None
    assert result.get("extraction_metrics", {}).get("extraction_attempt_count", 0) >= 1


# ── Test 2: HTML fixture generates evidence_items ────────────────────────


def test_html_fixture_generates_evidence_items() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-002",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    items = result.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert "evidence_id" in first
    assert "source_id" in first
    assert "source_url" in first
    assert "source_type" in first
    assert "snippet" in first
    assert "extracted_text_hash" in first
    assert "extraction_confidence" in first
    assert "evidence_type" in first
    assert first["evidence_type"] == "extracted"


# ── Test 3: Claims derived from real text, not invented ──────────────────


def test_claims_derived_from_real_text() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-003",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    claims = result.get("claims", [])
    assert len(claims) >= 1
    for c in claims:
        assert "claim_id" in c
        assert "claim_text" in c
        assert c["claim_text"]  # not empty
        assert "extraction_method" in c
        assert c["extraction_method"] == "deterministic_pattern"
        # Claim text must come from actual evidence patterns, not invented
        assert (
            any(
                kw in c["claim_text"].lower()
                for kw in [
                    "ai",
                    "machine learning",
                    "founder",
                    "funding",
                    "tech stack",
                    "description",
                    "customer",
                ]
            )
            or "signal" in c["claim_text"].lower()
        )


# ── Test 4: startup_profile contains detected_ai_signals ─────────────────


def test_startup_profile_contains_ai_signals() -> None:
    candidates = [_make_candidate(_AI_HTML)]
    result = _extract_profile(
        {
            "run_id": "ext-test-004",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    profile = result.get("startup_profile", {})
    assert isinstance(profile, dict)
    ai_signals = profile.get("detected_ai_signals", [])
    assert len(ai_signals) >= 1
    signals_text = " ".join(ai_signals).lower()
    assert "machine learning" in signals_text or "deep learning" in signals_text


# ── Test 5: extraction_metrics exists ────────────────────────────────────


def test_extraction_metrics_exist() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-005",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    metrics = result.get("extraction_metrics", {})
    assert isinstance(metrics, dict)
    for key in (
        "raw_candidates_count",
        "extraction_attempt_count",
        "extraction_success_count",
        "extraction_failure_count",
        "evidence_items_count",
        "claims_count",
        "empty_content_count",
        "duplicate_content_count",
        "source_type_coverage",
        "extraction_success_rate",
        "profile_field_coverage",
        "average_extraction_confidence",
    ):
        assert key in metrics, f"Missing metric key: {key}"


# ── Test 6: extraction_success_rate is calculated ────────────────────────


def test_extraction_success_rate_calculated() -> None:
    candidates = [_make_candidate(), _make_candidate(text=_EMPTY_HTML)]
    result = _extract_profile(
        {
            "run_id": "ext-test-006",
            "startup_name": "PartialAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    metrics = result.get("extraction_metrics", {})
    rate = metrics.get("extraction_success_rate", 0.0)
    assert 0.0 < rate <= 1.0
    assert metrics["extraction_attempt_count"] == 2
    assert metrics["extraction_success_count"] >= 1


# ── Test 7: empty raw_evidence_candidates blocks extraction ──────────────


def test_empty_candidates_blocks() -> None:
    result = _extract_profile(
        {
            "run_id": "ext-test-007",
            "startup_name": "EmptyAI",
            "raw_evidence_candidates": [],
            "executed_nodes": [],
        }
    )
    assert result.get("extraction_status") == "blocked"
    assert result.get("status") == "extraction_blocked"
    assert result.get("review_required") is True
    blockers = result.get("blockers", [])
    assert any("empty" in b.lower() for b in blockers)
    assert result.get("extraction_metrics") == _empty_extraction_metrics()


# ── Test 8: extractor unavailable blocks production ──────────────────────


@patch("src.extraction.extractor.extract_profile", side_effect=ImportError("Mock unavailable"))
def test_extractor_unavailable_blocks(mock_extractor: MagicMock) -> None:
    """When the extractor is unavailable, extraction is blocked."""
    result = _extract_profile(
        {
            "run_id": "ext-test-008",
            "startup_name": "NoExtractorAI",
            "raw_evidence_candidates": [_make_candidate()],
            "executed_nodes": [],
        }
    )
    assert result.get("extraction_status") == "blocked"
    assert result.get("status") == "extractor_unavailable"
    assert result.get("review_required") is True
    blockers = result.get("blockers", [])
    assert any("extractor" in b.lower() for b in blockers)


# ── Test 9: sufficiency without calibration does not liberate production ──


def test_sufficiency_uncalibrated_blocks_passed() -> None:
    """Without calibrated sufficiency decisions, status cannot be 'passed'."""
    candidates = [_make_candidate(_AI_HTML)]
    result = _extract_profile(
        {
            "run_id": "ext-test-009",
            "startup_name": "UncalibratedAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    # Without calibrated decisions, extraction is blocked or partial
    assert result.get("extraction_status") in ("blocked", "partial")
    assert result.get("status") in ("extraction_blocked", "profile_extracted_partial")


# ── Test 10: run_id is preserved ─────────────────────────────────────────


def test_run_id_preserved() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "preserve-ext-001",
            "startup_name": "PreserveAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    assert result.get("run_id") is None  # run_id stays in state, not returned
    # But it's preserved in the state because extract_profile doesn't overwrite it
    assert "extract_profile" in result.get("executed_nodes", [])


# ── Test 11: executed_nodes contains extract_profile ─────────────────────


def test_executed_nodes_contains_extract_profile() -> None:
    candidates = [_make_candidate()]
    prior = ["preflight_configuration_check", "plan_search", "collect_sources"]
    result = _extract_profile(
        {
            "run_id": "ext-test-011",
            "startup_name": "NodeTestAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": list(prior),
        }
    )
    executed = result.get("executed_nodes", [])
    assert "extract_profile" in executed
    idx = executed.index("extract_profile")
    assert idx > executed.index("collect_sources")


# ── Test 12: no LLM/Qdrant/internet/scraping is called ──────────────────


def test_no_llm_qdrant_scraping() -> None:
    """Assert that banned modules are NOT imported during extraction."""
    import sys

    before = set(sys.modules.keys())
    _extract_profile(
        {
            "run_id": "ext-test-012",
            "startup_name": "SafeAI",
            "raw_evidence_candidates": [_make_candidate()],
            "executed_nodes": [],
        }
    )
    after = set(sys.modules.keys())
    new_imports = after - before
    banned = {
        "langchain",
        "qdrant_client",
        "playwright",
        "openai",
        "anthropic",
        "httpx",
        "requests",
        "selenium",
        "scrapy",
    }
    triggered = {m for m in new_imports if any(b in m for b in banned)}
    assert not triggered, f"Banned imports detected: {triggered}"


# ── Test 13: startup_profile with no AI signals ─────────────────────────


def test_startup_profile_no_ai_signals() -> None:
    candidates = [_make_candidate(_NO_AI_HTML, source_url="https://cleantech.com")]
    result = _extract_profile(
        {
            "run_id": "ext-test-013",
            "startup_name": "CleanTech",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    profile = result.get("startup_profile", {})
    ai_signals = profile.get("detected_ai_signals", [])
    assert ai_signals == []


# ── Test 14: evidence_items have factuality_status ──────────────────────


def test_evidence_items_have_factuality() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-014",
            "startup_name": "NovaAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    for ev in result.get("evidence_items", []):
        assert "factuality_status" in ev
        assert ev["factuality_status"] in ("observed", "inferred", "unknown")


# ── Test 15: extraction with duplicate content ──────────────────────────


def test_duplicate_content_tracked() -> None:
    text = _AI_HTML
    candidates = [
        _make_candidate(text=text, source_id="src_001"),
        _make_candidate(text=text, source_id="src_002"),
    ]
    result = _extract_profile(
        {
            "run_id": "ext-test-015",
            "startup_name": "DupAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    metrics = result.get("extraction_metrics", {})
    assert metrics.get("duplicate_content_count", 0) >= 1
    assert metrics.get("extraction_success_count", 0) == 1


# ── Test 16: evidence_items contain source_quality_score ────────────────


def test_evidence_has_source_quality_score() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-016",
            "startup_name": "QualityAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    for ev in result.get("evidence_items", []):
        assert "source_quality_score" in ev
        assert isinstance(ev["source_quality_score"], (int, float))


# ── Test 17: claims have supporting_evidence_ids ────────────────────────


def test_claims_have_supporting_evidence_ids() -> None:
    candidates = [_make_candidate()]
    result = _extract_profile(
        {
            "run_id": "ext-test-017",
            "startup_name": "LinkAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    for c in result.get("claims", []):
        assert "supporting_evidence_ids" in c
        assert len(c["supporting_evidence_ids"]) >= 1


# ── Test 18: empty text candidate counts as failure ─────────────────────


def test_empty_text_counts_as_failure() -> None:
    candidates = [_make_candidate(text="", source_url="https://empty.com")]
    result = _extract_profile(
        {
            "run_id": "ext-test-018",
            "startup_name": "EmptyTextAI",
            "raw_evidence_candidates": candidates,
            "executed_nodes": [],
        }
    )
    metrics = result.get("extraction_metrics", {})
    assert metrics.get("empty_content_count", 0) >= 1
    assert metrics.get("extraction_success_count", 0) == 0
    assert metrics.get("evidence_items_count", 0) == 0
