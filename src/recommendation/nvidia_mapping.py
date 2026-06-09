"""Mappings between diagnosed gaps and candidate NVIDIA technologies."""

from src.extraction.schemas import TechnicalGap

_GAP_TO_TECHNOLOGIES: dict[TechnicalGap, list[str]] = {
    TechnicalGap.EXTERNAL_API_DEPENDENCY: ["NVIDIA NIM", "NVIDIA AI Enterprise"],
    TechnicalGap.HIGH_INFERENCE_COST: ["TensorRT-LLM", "NVIDIA Triton Inference Server"],
    TechnicalGap.HIGH_LATENCY: ["TensorRT-LLM", "NVIDIA Triton Inference Server"],
    TechnicalGap.AGENT_GOVERNANCE_GAP: ["NeMo Guardrails", "NVIDIA NeMo"],
    TechnicalGap.OBSERVABILITY_GAP: ["NVIDIA AI Enterprise", "NVIDIA Triton Inference Server"],
    TechnicalGap.MODEL_EVALUATION_GAP: ["NVIDIA NeMo", "NeMo Guardrails"],
    TechnicalGap.PRIVACY_OR_CONTROLLED_DEPLOYMENT_GAP: ["NVIDIA NIM", "NVIDIA AI Enterprise"],
    TechnicalGap.SLOW_DATA_PIPELINE: ["NVIDIA RAPIDS", "cuDF", "cuML"],
    TechnicalGap.HEAVY_TABULAR_PROCESSING: ["NVIDIA RAPIDS", "cuDF", "cuML"],
    TechnicalGap.VOICE_NEED: ["NVIDIA Riva"],
    TechnicalGap.SIMULATION_NEED: ["NVIDIA Omniverse"],
    TechnicalGap.COMPUTER_VISION_NEED: ["CUDA", "NVIDIA Triton Inference Server"],
    TechnicalGap.ROBOTICS_NEED: ["NVIDIA Isaac"],
    TechnicalGap.HEALTHCARE_COMPLIANCE_NEED: ["NVIDIA Clara"],
    TechnicalGap.AI_CYBERSECURITY_NEED: ["NVIDIA Morpheus"],
}


def map_gap_to_nvidia_technologies(gap: TechnicalGap) -> list[str]:
    """Return candidate NVIDIA technologies for a diagnosed technical gap."""

    return list(_GAP_TO_TECHNOLOGIES.get(gap, []))
