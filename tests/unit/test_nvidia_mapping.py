from src.extraction.schemas import TechnicalGap
from src.recommendation.nvidia_mapping import map_gap_to_nvidia_technologies


def test_mapping_returns_expected_candidates() -> None:
    technologies = map_gap_to_nvidia_technologies(TechnicalGap.HIGH_INFERENCE_COST)
    assert "TensorRT-LLM" in technologies
    assert "NVIDIA Triton Inference Server" in technologies


def test_mapping_handles_voice_need() -> None:
    technologies = map_gap_to_nvidia_technologies(TechnicalGap.VOICE_NEED)
    assert technologies == ["NVIDIA Riva"]
