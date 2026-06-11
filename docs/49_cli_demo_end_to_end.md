# CLI Demo End-to-End

**Epic 24** | **Date:** 2026-06-11

## Objective

Provide a simple CLI to demonstrate the NVIDIA Startup AI Radar product
end-to-end without a frontend. The CLI runs the full pipeline on a sample input,
generates a Startup Action Brief, and optionally evaluates answer quality.

## Architecture

```
scripts/
  run_startup_radar_demo.py          # Main CLI entry point

examples/demo/
  sample_startup_input.json          # Fictional startup input
  README.md                          # Sample documentation

data/demo_runs/latest/
  startup_action_brief.md            # Markdown brief
  startup_action_brief.json           # JSON brief
  demo_run_report.json               # Run metadata report
  answer_quality_eval.json           # Optional quality eval report
```

## CLI Interface

```
scripts/run_startup_radar_demo.py --input PATH [options]
```

### Arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--input` | str (required) | — | Path to sample startup input JSON |
| `--output-dir` | str | `data/demo_runs/latest` | Output directory |
| `--use-rag` | flag | off | Enable Product RAG pipeline (Step 11) |
| `--rag-backend` | `qdrant\|local` | `local` | RAG vector store backend |
| `--run-answer-quality-eval` | flag | off | Run answer quality evaluation |
| `--offline` | flag | off | No external dependencies (MockEmbeddingProvider) |
| `--format` | `markdown\|json\|both` | `both` | Brief output format |

### Exit Codes

- `0`: Success
- `1`: Error (input not found, Qdrant unavailable, pipeline failure)

## Pipeline Flow

1. Load input JSON
2. Build `StartupProfile` and `Evidence` list
3. (Optional) Build RAG dependencies: `ChunkIndex`, `EmbeddingProvider`, `VectorStore`
4. Call `run_full_pipeline()` (existing pipeline — no logic duplicated)
5. Call `build_action_brief()` → `StartupActionBrief`
6. Export Markdown and/or JSON
7. (Optional) Call `evaluate_answer_quality()` with a generic quality case
8. Export run report

## Design Decisions

### Why argparse
The project already uses `argparse` in all existing scripts
(`ingest_nvidia_corpus.py`, `sync_nvidia_sources.py`, etc.). No new dependency
(Typer/Click) is needed.

### No logic duplication
The CLI is a thin orchestrator. It:
- Builds `StartupProfile` and `Evidence` from JSON input (same pattern as
  `tests/evals/helpers.py`)
- Calls `run_full_pipeline()` — unchanged
- Calls `build_action_brief()` — unchanged
- Calls `evaluate_answer_quality()` — unchanged

### Offline mode
Uses `MockEmbeddingProvider` + `InMemoryVectorStore` — the same deterministic
offline providers used in all golden tests. No Qdrant, no sentence-transformers,
no external calls.

### RAG mode
- `--rag-backend local`: InMemoryVectorStore + MockEmbeddingProvider (no
  external deps, corpus still required)
- `--rag-backend qdrant`: Try `QdrantStore`, fail with clear message if
  unavailable

### Answer quality eval
Uses a generic `AnswerQualityEvalCase` checking:
- Required sections present
- Forbidden absolute language count
- Nvidia technology → gap consistency
- Citation coverage

Not a replacement for golden eval cases — just a basic quality gate for demos.

## Contract Coverage

| Contract | CLI interaction |
|---|---|
| `pipeline_output_contract.md` | CLI respects PipelineResult schema |
| `briefing_contract.md` | CLI uses build_action_brief + render_action_brief_markdown |
| `rag_contract.md` | RAG mode respects VectorStore interface |
| `evidence_contract.md` | Evidence built from user input, not scraped |

## Known Limitations

- Sample input is fictional — not a real startup.
- Answer quality eval uses a generic case, not golden cases.
- Qdrant mode requires `qdrant-client` and a running Qdrant instance.
- Corpus must exist in `data/nvidia_corpus/` for RAG to work.
- Pipeline heuristics may produce different results than expected for
  real-world startups.
