# Epic 55: Complete Candidate Benchmark Coverage

## Summary

Fechar a lacuna do roadmap benchmark-first: todas as 408 tecnologias e tecnicas candidatas devem ter uma saida explicita do benchmark harness. Candidatas locais recebem benchmark/proxy local por categoria; candidatas SaaS, hardware, API, licenca ou credencial indisponivel recebem status bloqueado/future research com motivo e substituto de categoria quando aplicavel. Nenhuma candidata nova sera promovida para runtime sem benchmark direto, decisao registrada e evidencia reproduzivel.

## Key Changes

- Estender `scripts/run_benchmark.py` com modo `--suite complete-catalog` que emite resultado para todas as candidatas.
- Adicionar tarefas de proxy por categoria para RAG/retrieval, security/guardrails, evaluation, evidence/abstention, TOON/context, docs/release, observability, sourcing, graph, human review e data governance.
- Marcar resultados nao executaveis como `blocked` ou `future_research`, nunca `passed`.
- Gerar `final_case_evidence/benchmark_debt_report.json` e `final_case_evidence/benchmark_coverage_report.json`.
- Atualizar `candidate_status_summary.json` para refletir cobertura total por status, categoria, benchmarkability e dependencia externa.
- Integrar a cobertura completa ao proof local sem fingir benchmark direto de SaaS/hardware indisponivel.

## Test Plan

- Unit tests para classificacao de benchmark complete-catalog e status blocked/future_research.
- Unit tests para reports de coverage/debt e preservacao de candidatas nao promoviveis.
- Rodar `python scripts/run_benchmark.py --suite complete-catalog`.
- Rodar `python scripts/check_candidate_catalog.py`.
- Rodar `python scripts/prove_final_product.py --quick --skip-live`.
- Rodar `ruff`, `black --check`, `mypy` focados.

## Assumptions

- O roadmap final continua fonte canonica do catalogo.
- Benchmarks de categoria sao evidencias de benchmarkability/proxy, nao equivalencia direta para promocao do candidato original.
- Dependencias externas indisponiveis permanecem `FUTURE_RESEARCH` ou `blocked`, sem promocao automatica.
