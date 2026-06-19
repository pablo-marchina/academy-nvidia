# Acceptance Gates — NVIDIA Startup AI Radar

Gates objetivos que qualquer agente de IA deve respeitar antes de considerar uma tarefa concluída.

---

## 1. Security Gate
- `forbidden_artifacts_found = 0`
- `tracked_secret_files = 0`
- `secret_scan_pass = true`
- Nenhum `.env`, `.venv`, `node_modules`, cache ou banco local no commit.

## 2. Repository Hygiene Gate
- `missing_required_capabilities = 0`
- Nenhum arquivo fantasma (criado mas não referenciado).
- Nenhuma dependência nova sem justificativa no commit.

## 3. Configuration & Readiness Gate
- `blocked_routes_when_not_ready = 100%`
- Toda rota/funcionalidade bloqueia com erro claro se configuração obrigatória estiver faltando.
- Produto não roda sem configuração explícita — sem defaults silenciosos.

## 4. Runtime Gate
- Nenhum fallback silencioso em produção.
- Nenhum `except Exception: pass` ou equivalente.

## 5. LangGraph Workflow Gate
- `workflow_nodes_executed >= 12`
- `workflow_trace_coverage = 100%`
- Todos os nós do grafo principal são executados e rastreáveis.
- LangGraph orquestra obrigatoriamente o workflow principal.

## 6. Scraping & Source Coverage Gate
- `active_source_adapters >= 20`
- `source_categories >= 6`
- `scraping_success_rate >= 0.80`
- Rate limit explícito e rastreável.
- Scraping governado por política de robots.txt.

## 7. Evidence & Claim Ledger Gate
- `independent_sources_per_startup >= 3`
- `evidence_items_per_startup >= 8`
- `critical_claims_with_evidence = 100%`
- `unsupported_critical_claims = 0`
- Toda claim crítica tem evidência com URL e timestamp.
- Fato, inferência e hipótese separados em todo output.

## 8. Quantitative Scoring Gate
- `all_scores_have_features = 100%`
- `all_scores_have_confidence = 100%`
- `all_scores_have_uncertainty = 100%`
- Todo score expõe: features usadas, pesos, confidence, uncertainty.

## 9. RAG & Retrieval Gate
- `qdrant_collection_ready = true`
- `qdrant_min_documents >= 100`
- `hybrid_search_enabled = true`
- `reranking_enabled = true`
- `citation_precision >= 0.90`
- `rag_groundedness >= 0.85`
- Qdrant obrigatório para RAG em produção.

## 10. Recommendation Gate
- `recommendations_with_confidence = 100%`
- `recommendations_with_rag_support = 100%`
- Toda recomendação NVIDIA contém: evidência, suporte RAG, confidence score, business impact, implementation complexity, next best action.

## 11. Frontend Product Flow Gate
- `setup_to_export_e2e_pass = true`
- Fluxo de ponta a ponta funcional (setup → coleta → scoring → recomendação → exportação).

## 12. Observability Gate
- Toda execução gera log estruturado.
- Erros são explícitos e rastreáveis.
- Métricas de workflow, scraping e RAG disponíveis.

## 13. CI/CD Gate
- `unit_tests_pass = true`
- `integration_tests_pass = true`
- `acceptance_tests_pass = true`
- `ruff check .` sem erros.
- `black --check .` sem erros.
- `mypy src` sem erros.

## 14. Final Product Acceptance Gate
- Setup completo configura obrigatoriamente Postgres, Qdrant e Redis.
- Pipeline LangGraph executa de ponta a ponta sem erros.
- Action Brief gerado com todas as seções obrigatórias preenchidas.
- Nenhum placeholder (`TODO`, `TBD`, `{placeholder}`) no output final.

---

## How AI Agents Must Use These Gates

1. **Toda issue/tarefa deve declarar quais gates afeta** no momento do planejamento.
2. **Toda implementação deve adicionar ou atualizar testes** que medem a métrica do gate correspondente.
3. **Se uma métrica ainda não puder ser medida automaticamente**, a tarefa deve criar a medição (teste, script, checker) antes de afirmar que o gate foi atingido.
4. **A IA não pode declarar uma tarefa concluída sem listar os gates aplicáveis** e o status de cada métrica envolvida.
5. **Gates não aplicáveis devem ser explicitamente justificados** — não podem ser ignorados silenciosamente.
6. **Se qualquer métrica obrigatória falhar**, a tarefa não está concluída — corrija antes de prosseguir.
