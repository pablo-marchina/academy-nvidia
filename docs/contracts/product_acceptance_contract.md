# Product Acceptance Contract

**Versão:** 1.0
**Data:** 2026-06-13
**Epic:** 38

## Propósito

Definir o contrato de aceitação end-to-end do produto. Este contrato estabelece o que o Product Golden Path promete e o que NÃO promete.

## Product Golden Path

### O que promete

1. **Readiness** — `GET /product/readiness` retorna `ready=true` quando configuração obrigatória está completa. Retorna `ready=false` com `blocking_missing_config` quando faltam requisitos.

2. **Capabilities** — `GET /product/capabilities` retorna >= 25 capabilities com status, categoria e campos obrigatórios.

3. **Startup CRUD** — `POST /startups` cria startup persistida com normalized_name único. `PATCH /startups/{id}` atualiza campos sem perder evidence. `GET /startups` lista com paginação.

4. **Analysis Run** — `POST /startups/{id}/analysis-runs` executa pipeline e persiste scores, gaps, mappings e Action Brief. Status pode ser `completed` ou `degraded`.

5. **Claims** — `GET /analysis-runs/{id}/claims` retorna claims geradas deterministicamente a partir dos registros persistidos. `evidence-coverage` retorna sumário com `total_claims`, `supported_claims`, `unsupported_claims`.

6. **Activation Recommendations** — `POST .../activation-recommendations/generate` faz match determinístico entre gaps detectados e playbooks NVIDIA. Persiste recomendações com confidence, priority e next_step.

7. **Dossier** — `POST /analysis-runs/{id}/dossier` gera dossier versionado (JSON + Markdown) combinando scores, gaps, mappings, activation, claims, reviews e readiness checks. Idempotente — retorna existente se chamado sem `force=true`.

8. **Quality Run** — `POST /analysis-runs/{id}/quality-runs` executa avaliadores de qualidade e gera métricas com pass/fail thresholds. `GET .../quality-summary` retorna `overall_status`.

9. **Opportunities** — `GET /opportunities` retorna lista ranqueada de startups com filtros, ordenação e paginação. Inclui `top_activation_playbook`, `evidence_coverage`, `unsupported_claim_count`.

10. **Exports** — `POST /analysis-runs/{id}/exports` gera export JSON ou Markdown a partir do Action Brief persistido. `status` pode ser `completed` ou `failed`.

11. **No demo dependency** — Nenhum endpoint do product flow lê `data/demo_runs`, `examples/demo` ou fixtures demo não autorizadas.

### O que NÃO promete

1. **Auth** — Nenhuma autenticação ou autorização. Todos os endpoints são públicos.
2. **PDF** — Export é apenas JSON e Markdown.
3. **RAG obrigatório** — Analysis runs funcionam sem RAG. `use_rag=true` sem configuração gera degraded.
4. **Qdrant obrigatório** — Product flow funciona sem Qdrant. Degradado se configurado mas offline.
5. **Performance** — Testes de aceitação validam contrato, não performance ou latência.
6. **PostgreSQL por padrão** — Aceitação usa SQLite. PostgreSQL requer `PRODUCT_DB_TEST_URL` e marcador integration.
7. **LLM Judge** — Não testado no acceptance path. Opcional e experimental.

## Fixture de Aceitação

### `tests/fixtures/product_golden_path/startup.json`

```json
{
  "name": "Golden Path AI",
  "website": "https://goldenpath-ai.example.com",
  "sector": "AI Infrastructure",
  "description": "AI infrastructure platform for production GPU inference and model serving",
  "product_summary": "Managed GPU inference with auto-scaling and model optimization",
  "tags": ["golden-path", "acceptance-test"],
  "evidence": [
    {"claim": "Operates GPU inference in production", "source_url": "https://gp.example.com/platform", "source_type": "official_site", "quote_or_evidence": "Platform runs production GPU inference workloads.", "confidence": "high"},
    {"claim": "Uses NVIDIA GPUs for model serving", "source_url": "https://gp.example.com/tech-stack", "source_type": "tech_blog", "quote_or_evidence": "Stack includes NVIDIA A100 GPUs for model serving.", "confidence": "medium"},
    {"claim": "500+ enterprise customers", "source_url": "https://gp.example.com/customers", "source_type": "official_site", "quote_or_evidence": "Serving 500+ enterprise customers.", "confidence": "low"}
  ]
}
```

## Marcadores de Teste

- `acceptance` — testes de aceitação que validam o Product Golden Path
- `integration` — testes que exigem serviços externos (Qdrant, PostgreSQL)
- `e2e` — testes Playwright end-to-end

Testes marcados `acceptance` não rodam em `make validate` (que usa `-m "not integration"`). Rodam via `make acceptance` ou `pytest -m acceptance`.
