from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> tuple[Path, str]:
    target = ROOT / path
    return target, target.read_text(encoding="utf-8-sig")


def _write(path: Path, text: str) -> None:
    if path.suffix == ".py":
        ast.parse(text)
    path.write_text(text, encoding="utf-8")


def _replace_once(path: str, old: str, new: str, *, label: str) -> bool:
    target, text = _read(path)
    if new in text:
        print(f"[already] {label}")
        return False
    if old not in text:
        raise RuntimeError(f"Could not locate expected block for {label} in {path}")
    updated = text.replace(old, new, 1)
    _write(target, updated)
    print(f"[fixed] {label}")
    return True


def _regex_once(path: str, pattern: str, replacement: str, *, label: str, flags: int = 0) -> bool:
    target, text = _read(path)
    if re.search(pattern, text, flags=flags) is None:
        if replacement in text:
            print(f"[already] {label}")
            return False
        raise RuntimeError(f"Could not locate expected pattern for {label} in {path}")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Expected one replacement for {label}, got {count}")
    _write(target, updated)
    print(f"[fixed] {label}")
    return True


def _function_bounds(lines: list[str], function_name: str) -> tuple[int, int]:
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"def {function_name}("):
            start = index
            break
    if start is None:
        raise RuntimeError(f"Function not found: {function_name}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("def "):
            end = index
            break
    return start, end


def _insert_in_function(path: str, function_name: str, anchor: str, required: str, payload: list[str]) -> bool:
    target, text = _read(path)
    lines = text.splitlines(keepends=True)
    start, end = _function_bounds(lines, function_name)
    block = "".join(lines[start:end])
    if required in block:
        print(f"[already] {function_name}: {required}")
        return False
    anchor_index = None
    for index in range(start, end):
        if anchor in lines[index]:
            anchor_index = index
            break
    if anchor_index is None:
        raise RuntimeError(f"Anchor not found in {function_name}: {anchor}")
    lines[anchor_index + 1:anchor_index + 1] = payload
    updated = "".join(lines)
    _write(target, updated)
    print(f"[fixed] {function_name}: {required}")
    return True


def repair_http_collector() -> None:
    _replace_once(
        "src/scraping/http_collector.py",
        "from src.scraping.fetcher import fetch_page",
        "from src.scraping.fetcher import FetchResult, fetch_page",
        label="import FetchResult",
    )
    old = '''        except (_RetryableServerOrRateLimitError, _RetryableNetwork) as exc:\n            if hasattr(exc, "args") and exc.args:\n                return exc.args[0]\n            return FetchResult(\n                url=url, status=None, raw_html="", fetched_at=datetime.now(UTC),\n                error=f"All {max_retries} retries exhausted",\n            )\n'''
    new = '''        except (_RetryableServerOrRateLimitError, _RetryableNetwork) as exc:\n            payload = exc.args[0] if getattr(exc, "args", ()) else None\n            if isinstance(payload, FetchResult):\n                return payload\n            return FetchResult(\n                url=url,\n                status=None,\n                raw_html="",\n                fetched_at=datetime.now(UTC),\n                error=str(payload or f"All {max_retries} retries exhausted"),\n            )\n'''
    _replace_once(
        "src/scraping/http_collector.py",
        old,
        new,
        label="normalize retry exception payload to FetchResult",
    )


def repair_collection_gate() -> None:
    _regex_once(
        "src/orchestration/node_impl.py",
        r'@_register\("collect_sources",\s*"Collect evidence from governed sources",\s*critical=True\)',
        '@_register("collect_sources", "Collect evidence from governed sources", critical=False)',
        label="allow degraded source collection to continue",
        flags=re.MULTILINE,
    )
    _replace_once(
        "src/orchestration/node_impl.py",
        '''    if len(evidence_items) < min_raw:\n        critical_failures.append("minimum_raw_evidence_count_not_met")\n''',
        '''    if len(evidence_items) == 0:\n        critical_failures.append("no_raw_evidence_collected")\n    elif len(evidence_items) < min_raw:\n        degraded_failures.append("minimum_raw_evidence_count_not_met")\n''',
        label="separate zero evidence from partial evidence",
    )


def repair_gap_features() -> None:
    _insert_in_function(
        "src/diagnosis/gap_diagnosis_scoring.py",
        "extract_gap_severity_features",
        "all_texts = ev_texts + ac_texts + claim_texts",
        "has_relevant_signal = bool(matching_items)",
        [
            "\n",
            "    matching_items = _matching_evidence_items(evidence_items, gap_type)\n",
            "    has_relevant_signal = bool(matching_items)\n",
        ],
    )
    _insert_in_function(
        "src/diagnosis/gap_diagnosis_scoring.py",
        "extract_gap_confidence_features",
        "related_keywords = _technical_gap_keywords(related_tech_gaps)",
        "matching_items = _matching_evidence_items(evidence_items, gap_type)",
        ["\n", "    matching_items = _matching_evidence_items(evidence_items, gap_type)\n"],
    )


def repair_mapping_abstention_flow() -> None:
    _regex_once(
        "src/orchestration/node_impl.py",
        r'@_register\("map_nvidia_technologies",\s*"Map NVIDIA technologies to diagnosed gaps",\s*critical=True\)',
        '@_register("map_nvidia_technologies", "Map NVIDIA technologies to diagnosed gaps", critical=False)',
        label="allow auditable mapping abstention",
        flags=re.MULTILINE,
    )
    old = '''    blocked = mapping_status in {"blocked_uncalibrated_mapping", "failed", "needs_more_evidence"}\n    product_blocked = _is_product_mode() and blocked\n\n    return NodeResult(\n        status=NodeStatus.FAILED if product_blocked else (NodeStatus.DEGRADED if blocked else NodeStatus.COMPLETED),\n        state_updates={\n            "nvidia_mappings": mappings,\n            "mapping_ids": list(dict.fromkeys(state.mapping_ids + persisted_mapping_ids + [str(item.get("mapping_id", "")) for item in mappings if item.get("mapping_id")])),\n            "node_outputs": node_outputs,\n        },\n        degraded_reason=f"NVIDIA mapping status: {mapping_status}" if blocked and not product_blocked else None,\n        error_message=f"NVIDIA mapping status: {mapping_status}" if product_blocked else None,\n    )\n'''
    new = '''    hard_blocked = mapping_status in {"blocked_uncalibrated_mapping", "failed"}\n    needs_more_evidence = mapping_status == "needs_more_evidence"\n    product_blocked = _is_product_mode() and hard_blocked\n\n    return NodeResult(\n        status=(\n            NodeStatus.FAILED\n            if product_blocked\n            else NodeStatus.DEGRADED\n            if hard_blocked or needs_more_evidence\n            else NodeStatus.COMPLETED\n        ),\n        state_updates={\n            "nvidia_mappings": mappings,\n            "mapping_ids": list(dict.fromkeys(state.mapping_ids + persisted_mapping_ids + [str(item.get("mapping_id", "")) for item in mappings if item.get("mapping_id")])),\n            "node_outputs": node_outputs,\n        },\n        degraded_reason=(\n            f"NVIDIA mapping status: {mapping_status}"\n            if (hard_blocked or needs_more_evidence) and not product_blocked\n            else None\n        ),\n        error_message=f"NVIDIA mapping status: {mapping_status}" if product_blocked else None,\n    )\n'''
    _replace_once(
        "src/orchestration/node_impl.py",
        old,
        new,
        label="treat needs_more_evidence as nonfatal abstention",
    )
    _replace_once(
        "src/recommendation/recommendation_engine.py",
        '''    if mapping_status in (\n        "blocked_uncalibrated_mapping",\n        "failed",\n        "needs_more_evidence",\n    ):\n''',
        '''    if mapping_status in (\n        "blocked_uncalibrated_mapping",\n        "failed",\n    ):\n''',
        label="rank abstention mappings into not-recommended actions",
    )


def repair_proxy_and_frontend_build() -> None:
    _replace_once(
        "frontend/nginx.conf",
        "        proxy_read_timeout 30s;\n        proxy_send_timeout 30s;",
        "        proxy_read_timeout 1800s;\n        proxy_send_timeout 1800s;",
        label="align nginx timeout with runtime verifier",
    )
    _replace_once(
        "frontend/Dockerfile",
        "RUN npm ci",
        '''RUN --mount=type=cache,target=/root/.npm \\\n    npm config set fetch-retries 5 \\\n    && npm config set fetch-retry-mintimeout 20000 \\\n    && npm config set fetch-retry-maxtimeout 120000 \\\n    && npm ci --prefer-offline --no-audit --no-fund''',
        label="make npm install resilient to transient resets",
    )


def repair_verifier_optional_properties() -> None:
    target, text = _read("scripts/verify_runtime_output.ps1")
    helper = '''\nfunction Get-OptionalProperty {\n    param(\n        [Parameter(Mandatory)] [object]$Object,\n        [Parameter(Mandatory)] [string]$Name\n    )\n    if ($null -eq $Object) { return $null }\n    $property = $Object.PSObject.Properties[$Name]\n    if ($null -eq $property) { return $null }\n    return $property.Value\n}\n'''
    if "function Get-OptionalProperty" not in text:
        anchor = "function Convert-ComposePsOutput {"
        if anchor not in text:
            raise RuntimeError("Could not find verifier helper insertion anchor")
        text = text.replace(anchor, helper + "\n" + anchor, 1)
    replacements = {
        "$errorText = [string]$result.error": '$errorText = [string](Get-OptionalProperty -Object $result -Name "error")',
        "$reason = [string]$result.degraded_reason": '$reason = [string](Get-OptionalProperty -Object $result -Name "degraded_reason")',
        '-Detail "status=$status error=$errorText degraded_reason=$([string]$result.degraded_reason)"': '-Detail "status=$status error=$errorText degraded_reason=$reason"',
        "$runError = [string]$run.error_message": '$runError = [string](Get-OptionalProperty -Object $run -Name "error_message")',
        'degraded_reason = [string]$run.degraded_reason': 'degraded_reason = [string](Get-OptionalProperty -Object $run -Name "degraded_reason")',
    }
    changed = False
    for old, new in replacements.items():
        if new in text:
            continue
        if old not in text:
            raise RuntimeError(f"Could not find verifier expression: {old}")
        text = text.replace(old, new, 1)
        changed = True
    target.write_text(text, encoding="utf-8")
    print("[fixed] verifier optional response properties" if changed else "[already] verifier optional response properties")


def write_regression_tests() -> None:
    path = ROOT / "tests/unit/test_runtime_repair_regressions.py"
    content = '''from __future__ import annotations\n\nfrom datetime import UTC, datetime\n\n\ndef test_network_retry_returns_fetch_result(monkeypatch):\n    import src.scraping.http_collector as module\n    from src.scraping.fetcher import FetchResult\n\n    def fake_fetch(url, **kwargs):\n        return FetchResult(\n            url=url,\n            status=None,\n            raw_html="",\n            fetched_at=datetime.now(UTC),\n            error="simulated network failure",\n        )\n\n    monkeypatch.setattr(module, "fetch_page", fake_fetch)\n    result = module.HttpSourceCollector._fetch_with_tenacity(\n        url="https://example.invalid",\n        timeout_s=1,\n        max_retries=1,\n        backoff_base=0.01,\n        cached_etag=None,\n        cached_last_modified=None,\n    )\n    assert isinstance(result, FetchResult)\n    assert result.error == "simulated network failure"\n\n\ndef test_gap_feature_extractors_define_matching_items():\n    from src.diagnosis.gap_diagnosis_scoring import (\n        extract_gap_confidence_features,\n        extract_gap_severity_features,\n    )\n    from src.diagnosis.schemas import GapType\n\n    gap = GapType.COMPUTE_ACCELERATION_GAP\n    severity = extract_gap_severity_features(gap, [], [], [], [], {}, {})\n    confidence = extract_gap_confidence_features(gap, [], [], [], {}, {})\n    assert severity.relevant_signal_absence == 1.0\n    assert confidence.supporting_evidence_count == 0.0\n\n\ndef test_needs_more_evidence_produces_auditable_negative_recommendation():\n    from src.orchestration.node_impl import _runtime_decision_inventory\n    from src.recommendation.recommendation_engine import rank_recommendations_from_mappings\n\n    result = rank_recommendations_from_mappings(\n        run_id="run-test",\n        mapping_status="needs_more_evidence",\n        inventory=_runtime_decision_inventory(),\n        nvidia_technology_mappings=[\n            {\n                "mapping_id": "map-test-1",\n                "gap_type": "compute_acceleration_gap",\n                "nvidia_technology": "CUDA",\n                "mapping_score": 0.1,\n                "mapping_confidence": 0.1,\n                "uncertainty": 0.9,\n                "supporting_rag_context_ids": [],\n                "supporting_evidence_ids": [],\n                "calibration_decision_ids": [],\n                "production_allowed": False,\n                "blockers": ["Insufficient evidence"],\n            }\n        ],\n    )\n    assert result["ranking_status"] == "needs_review"\n    assert len(result["nvidia_recommendations"]) == 1\n    recommendation = result["nvidia_recommendations"][0]\n    assert recommendation["production_allowed"] is False\n    assert recommendation["recommendation_action"] == "not_recommended"\n    assert recommendation["why_not"]\n\n\ndef test_runtime_nodes_allow_declared_degradation():\n    import src.orchestration.node_impl  # noqa: F401\n    from src.orchestration.nodes import WORKFLOW_NODES\n\n    nodes = {node.name: node for node in WORKFLOW_NODES}\n    assert nodes["collect_sources"].critical is False\n    assert nodes["map_nvidia_technologies"].critical is False\n\n\ndef test_proxy_timeout_matches_verifier_timeout():\n    from pathlib import Path\n\n    config = Path("frontend/nginx.conf").read_text(encoding="utf-8")\n    assert "proxy_read_timeout 1800s;" in config\n    assert "proxy_send_timeout 1800s;" in config\n'''
    path.write_text(content, encoding="utf-8")
    ast.parse(content)
    print("[written] runtime regression tests")


def main() -> None:
    repair_http_collector()
    repair_collection_gate()
    repair_gap_features()
    repair_mapping_abstention_flow()
    repair_proxy_and_frontend_build()
    repair_verifier_optional_properties()
    write_regression_tests()
    print("Runtime repairs applied successfully.")


if __name__ == "__main__":
    main()
