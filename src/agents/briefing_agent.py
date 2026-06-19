"""Generate a startup action brief from accumulated pipeline state."""

from __future__ import annotations

from typing import Any


def generate_brief(
    startup_name: str,
    profile: dict[str, Any] | None,
    classification_raw: dict[str, Any] | None,
    scores: dict[str, float] | None,
    gaps: list[str],
    gap_diagnosis_raw: dict[str, Any] | None,
    recommendations: list[str],
    rag_contexts: list[str],
) -> tuple[str, list[str]]:
    errors: list[str] = []
    lines: list[str] = []

    lines.append(f"# Startup Action Brief: {startup_name}")
    lines.append("")

    if profile:
        sector = profile.get("sector", "N/A")
        desc = profile.get("description", "")
        product = profile.get("product_summary", "")
        lines.append(f"**Sector:** {sector}")
        if desc:
            lines.append(f"**Description:** {desc}")
        if product:
            lines.append(f"**Product:** {product}")
        lines.append("")

    if classification_raw:
        cls = classification_raw.get("classification", "unknown")
        conf = classification_raw.get("confidence", "low")
        lines.append(f"**AI-Native Classification:** {cls} (confidence: {conf})")
        lines.append("")

    if scores:
        lines.append("## Scores")
        for key, val in scores.items():
            if isinstance(val, (int, float)):
                lines.append(f"- {key}: {val:.1f}")
            else:
                lines.append(f"- {key}: {val}")
        lines.append("")

    if gaps:
        lines.append("## Detected Gaps")
        for g in gaps:
            lines.append(f"- {g}")
        lines.append("")

    if recommendations:
        lines.append("## Recommendations")
        for r in recommendations:
            lines.append(f"- {r}")
        lines.append("")

    if rag_contexts:
        lines.append(f"## NVIDIA Context ({len(rag_contexts)} chunks retrieved)")
        lines.append("")

    brief = "\n".join(lines) if lines else f"No data available for {startup_name}"
    return brief, errors
