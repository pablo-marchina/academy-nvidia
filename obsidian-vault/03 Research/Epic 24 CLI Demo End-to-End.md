# Epic 24 — CLI Demo End-to-End

**Date:** 2026-06-11

## Summary

CLI demo que conecta pipeline → briefing → output file. Permite demonstrar o produto de ponta a ponta sem frontend.

## What was built

- `scripts/run_startup_radar_demo.py` — CLI com 6 flags
- `examples/demo/sample_startup_input.json` — startup fictícia Nexus AI Labs
- `tests/integration/test_cli_demo.py` — 6 testes de integração

## Key outputs

- `startup_action_brief.md` / `.json` — brief do pipeline
- `demo_run_report.json` — metadados de execução
- `answer_quality_eval.json` — qualidade opcional

## Design principle

CLI não duplica lógica. Chama `run_full_pipeline()`, `build_action_brief()`, `render_action_brief_markdown()` e `evaluate_answer_quality()` diretamente.
