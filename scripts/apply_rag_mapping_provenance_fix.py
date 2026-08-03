from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:180]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_reranker() -> None:
    path = ROOT / "src/rag/rag_service_factory.py"
    old = '''    model_name = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")\n    try:\n        model = _load_local_cross_encoder(model_name)\n'''
    new = '''    model_name = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")\n    if not contexts:\n        return [], {\n            "called": False,\n            "provider": "local_cross_encoder",\n            "model": model_name,\n            "input_count": 0,\n            "reason": "no_contexts_to_rerank",\n        }\n    try:\n        model = _load_local_cross_encoder(model_name)\n'''
    replace_once(path, old, new)


def patch_mapping() -> None:
    path = ROOT / "src/recommendation/nvidia_technology_mapping.py"
    old = '''def _text_contains_any(text: str, keywords: list[str]) -> bool:\n    lower = text.lower()\n    return any(kw.lower() in lower for kw in keywords)\n'''
    new = '''def _text_contains_any(text: str, keywords: list[str]) -> bool:\n    lower = text.casefold()\n    return any(kw.casefold() in lower for kw in keywords if kw)\n\n\ndef _evidence_text(item: dict[str, Any]) -> str:\n    return str(\n        item.get("text")\n        or item.get("quote_or_evidence")\n        or item.get("snippet")\n        or item.get("claim")\n        or ""\n    )\n\n\ndef _evidence_id(item: dict[str, Any]) -> str:\n    return str(item.get("id") or item.get("evidence_id") or "")\n'''
    replace_once(path, old, new)

    old = '''    tech_keywords = [technology.lower(), technology.lower().replace("nvidia ", "")]\n    ev_for_tech = [\n        item\n        for item in evidence_items\n        if _text_contains_any(\n            str(item.get("text", "") or item.get("snippet", "") or item.get("claim", "")),\n            tech_keywords,\n        )\n    ]\n    evidence_count = len(ev_for_tech)\n'''
    new = '''    # Company evidence proves the diagnosed need; governed NVIDIA RAG contexts\n    # prove that a technology addresses that need. Requiring the company source\n    # to already name the recommended NVIDIA product would make novel\n    # recommendations impossible and would conflate adoption with suitability.\n    gap_support_ids = set(gap_result.supporting_evidence_ids if gap_result else [])\n    ev_for_tech = [item for item in evidence_items if _evidence_id(item) in gap_support_ids]\n    evidence_count = len(ev_for_tech)\n'''
    replace_once(path, old, new)

    replace_once(
        path,
        '    startup_text = " ".join(str(item.get("text", "") or item.get("snippet", "") or "") for item in evidence_items)',
        '    startup_text = " ".join(_evidence_text(item) for item in evidence_items)',
    )

    old = '''            ev_ids: list[str] = []\n            tech_keywords_search = [tech.lower(), tech.replace("nvidia ", "").strip().lower()]\n            for item in evidence_items:\n                eid = item.get("id") or item.get("evidence_id") or ""\n                if eid and _text_contains_any(\n                    str(item.get("text", "") or item.get("snippet", "") or item.get("claim", "")),\n                    tech_keywords_search,\n                ):\n                    ev_ids.append(str(eid))\n'''
    new = '''            ev_ids: list[str] = []\n            gap_support_ids = set(gap_result.supporting_evidence_ids if gap_result else [])\n            for item in evidence_items:\n                eid = _evidence_id(item)\n                if eid and eid in gap_support_ids:\n                    ev_ids.append(eid)\n'''
    replace_once(path, old, new)

    replace_once(
        path,
        '                f"RAG contexts supporting: {rag_count}, Evidence items: {ev_count}",',
        '                f"RAG technology contexts: {rag_count}, Company gap evidence items: {ev_count}",',
    )


def main() -> None:
    patch_reranker()
    patch_mapping()


if __name__ == "__main__":
    main()
