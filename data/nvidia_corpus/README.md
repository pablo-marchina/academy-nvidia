# NVIDIA Startup AI Radar — Product RAG Corpus

## Purpose

This directory contains curated Markdown documents describing NVIDIA technologies
that are relevant to the Product RAG module (`src/rag/`). Each document is a
controlled, versioned source of technical context used to enrich recommendations
and Startup Action Briefs.

## Sources

See `sources.yaml` for metadata (source_id, url, product, gap_types).

## Adding a New Document

1. Create a new `.md` file with the following structure:

```markdown
# {Technology Name}

## Product
{product name as used in _TECH_MATRIX}

## Gaps Addressed
- {technical_gap_value}
- {technical_gap_value}

## Description
{2-4 sentences describing the technology}

## Keywords
{comma-separated list of search keywords}

## Use Cases
- {use case 1}
- {use case 2}
```

2. Add an entry to `sources.yaml`.
3. Run `pytest tests/unit/test_rag_ingestion.py` to verify the file loads.
4. Run `pytest tests/unit/test_rag_retrieval.py` to verify retrieval works.

## Current Documents (10)

| File | Product | Gaps |
|---|---|---|
| `nim.md` | NVIDIA NIM | external_api_dependency, high_inference_cost, high_latency |
| `tensorrt_llm.md` | TensorRT-LLM | high_inference_cost, high_latency |
| `triton.md` | Triton Inference Server | high_inference_cost, high_latency |
| `nemo_guardrails.md` | NeMo Guardrails | agent_governance_gap |
| `rapids.md` | RAPIDS (cuDF, cuML) | slow_data_pipeline, heavy_tabular_processing |
| `riva.md` | NVIDIA Riva | voice_need |
| `omniverse.md` | NVIDIA Omniverse | simulation_need |
| `isaac.md` | NVIDIA Isaac | robotics_need |
| `clara_monai.md` | Clara / MONAI | healthcare_compliance_need |
| `morpheus.md` | NVIDIA Morpheus | ai_cybersecurity_need |
