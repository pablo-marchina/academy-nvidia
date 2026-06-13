from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

AI_NATIVE_KEYWORDS: list[tuple[str, str, float]] = [
    (r"\bAI\b", "Mentions AI/Artificial Intelligence", 0.15),
    (r"\bIA\b", "Mentions IA (Inteligência Artificial)", 0.15),
    (r"\binteligência artificial\b", "Mentions Inteligência Artificial", 0.15),
    (r"\binteligencia artificial\b", "Mentions Inteligência Artificial", 0.15),
    (r"\bmachine learning\b", "Mentions Machine Learning", 0.15),
    (r"\baprendizado de máquina\b", "Mentions Aprendizado de Máquina", 0.15),
    (r"\bLLM\b", "Mentions LLM (Large Language Model)", 0.2),
    (r"\blarge language model", "Mentions Large Language Model", 0.2),
    (r"\bgenerative AI\b", "Mentions Generative AI", 0.2),
    (r"\bIA generativa\b", "Mentions IA Generativa", 0.2),
    (r"\bdeep learning\b", "Mentions Deep Learning", 0.15),
    (r"\bcomputer vision\b", "Mentions Computer Vision", 0.15),
    (r"\bvisão computacional\b", "Mentions Visão Computacional", 0.15),
    (r"\bNLP\b", "Mentions NLP", 0.15),
    (r"\bprocessamento de linguagem natural\b", "Mentions PLN", 0.15),
    (r"\bmachine learning model", "Mentions ML Model", 0.15),
    (r"\bneural network", "Mentions Neural Networks", 0.15),
    (r"\bredes neurais\b", "Mentions Redes Neurais", 0.15),
    (r"\bmodel serving\b", "Mentions Model Serving", 0.2),
    (r"\binference\b", "Mentions Inference", 0.15),
    (r"\bGPU\b", "Mentions GPU", 0.2),
    (r"\btensorflow\b", "Mentions TensorFlow", 0.1),
    (r"\bpytorch\b", "Mentions PyTorch", 0.1),
    (r"\btransformers?\b", "Mentions Transformer Architecture", 0.15),
    (r"\bautomação inteligente\b", "Mentions Intelligent Automation", 0.1),
    (r"\bintelligent automation\b", "Mentions Intelligent Automation", 0.1),
    (r"\bTriton\b", "Mentions NVIDIA Triton Inference Server", 0.25),
    (r"\bTensorRT\b", "Mentions NVIDIA TensorRT", 0.25),
    (r"\bRAPIDS\b", "Mentions NVIDIA RAPIDS", 0.25),
    (r"\bNeMo\b", "Mentions NVIDIA NeMo", 0.25),
    (r"\bcuda\b", "Mentions CUDA", 0.2),
    (r"\bdata science\b", "Mentions Data Science", 0.05),
    (r"\bciência de dados\b", "Mentions Ciência de Dados", 0.05),
]


def detect_ai_native_signals(
    text: str,
    *,
    source_url: str = "",
    source_id: str = "",
) -> dict[str, Any]:
    if not text:
        return {
            "signals": [],
            "signal_count": 0,
            "confidence_contribution": 0.0,
            "evidence_excerpts": [],
        }

    signals: list[dict[str, Any]] = []
    evidence_excerpts: list[dict[str, Any]] = []
    total_boost = 0.0

    for pattern, label, boost in AI_NATIVE_KEYWORDS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            signals.append(
                {
                    "signal": label,
                    "keyword": pattern.strip("\\b"),
                    "boost": boost,
                    "count": len(matches),
                }
            )
            total_boost += boost * min(len(matches), 3)
            excerpt_start = max(0, matches[0].start() - 40)
            excerpt_end = min(len(text), matches[0].end() + 40)
            excerpt = text[excerpt_start:excerpt_end].strip()
            evidence_excerpts.append(
                {
                    "excerpt": excerpt,
                    "signal": label,
                    "source_url": source_url,
                    "source_id": source_id,
                    "collected_at": datetime.now(UTC).isoformat(),
                }
            )

    total_boost = min(total_boost, 0.6)
    if total_boost > 0:
        total_boost = round(total_boost, 2)

    return {
        "signals": signals,
        "signal_count": len(signals),
        "confidence_contribution": total_boost,
        "evidence_excerpts": evidence_excerpts,
        "has_nvidia_tech": any(
            s["signal"]
            in (
                "Mentions NVIDIA TensorRT",
                "Mentions NVIDIA Triton Inference Server",
                "Mentions NVIDIA RAPIDS",
                "Mentions NVIDIA NeMo",
                "Mentions CUDA",
            )
            for s in signals
        ),
    }


def calculate_confidence(
    *,
    has_name: bool = False,
    has_website: bool = False,
    signal_contribution: float = 0.0,
    is_manual_seed: bool = False,
    source_reliable: bool = False,
) -> str:
    base = 0.0
    if has_name:
        base += 0.3
    if has_website:
        base += 0.1
    if is_manual_seed:
        base += 0.2
    if source_reliable:
        base += 0.1

    total = base + signal_contribution
    total = max(0.0, min(1.0, total))

    if total >= 0.7:
        return "high"
    elif total >= 0.4:
        return "medium"
    else:
        return "low"
