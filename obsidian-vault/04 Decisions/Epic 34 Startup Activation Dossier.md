# Epic 34 Startup Activation Dossier

**Decision:** Dossier Versioned and Deterministic (no LLM)

**Context:** Epic 34 — Startup Activation Dossier. Precisa-se de um artifact consolidado que projete todos os registros persistidos de um AnalysisRun (scores, gaps, mappings, activation, claims, reviews, readiness) em um JSON + Markdown versionado.

**Decision:** Dossier é deterministico (sem LLM), idempotente (POST retorna existente por default), versionado (versão 1..N por analysis_run), e honesto sobre dados ausentes (missing → uncertainty explícita). Readiness checks viram risks não-bloqueantes.

**Alternatives:** LLM-summarized dossier (não-determinismo), Generated-on-read (sem versionamento), Always-regenerate (sem idempotência).

**Status:** Implementado no Epic 34.
