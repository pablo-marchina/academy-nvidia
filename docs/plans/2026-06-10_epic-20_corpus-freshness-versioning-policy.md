> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan: Epic 20 - Corpus Freshness, Versioning & Deprecation Policy

**Data:** 2026-06-10
**Status:** Aprovado para implementacao

## Summary

Implementar uma politica minima para versionamento, frescor, expiracao, deprecacao e reingestao segura do corpus NVIDIA. O objetivo e impedir que o Product RAG recupere conteudo obsoleto, expirado, duplicado ou substituido sem rastreabilidade.

## Key Changes

- Criar `docs/44_corpus_freshness_versioning_policy.md` com regras de lifecycle do corpus.
- Adicionar metadata de freshness/versioning aos manifests em `data/nvidia_corpus/`.
- Criar `scripts/audit_nvidia_corpus_freshness.py` com CLI offline e relatorios JSON/Markdown.
- Propagar metadata nova pela ingestao, schemas RAG, payload Qdrant e retrieval.
- Filtrar retrieval padrao para usar apenas `is_active=true`, nao deprecated e nao expired.
- Atualizar contrato RAG, README, ROADMAP, EVALS, DECISIONS quando aplicavel e Obsidian.

## Metadata

- `version`
- `content_hash`
- `previous_content_hash`
- `collected_at`
- `last_checked_at`
- `valid_from`
- `valid_until`
- `freshness_policy`
- `stale_after_days`
- `is_active`
- `deprecated_at`
- `superseded_by`
- `deprecation_reason`

## Rules

- Uma fonte pode ter multiplas versoes registradas no manifest.
- Apenas uma versao ativa por `source_id`, salvo excecao explicita futura.
- Mudanca de `content_hash` gera nova versao.
- Promocao de nova versao desativa/deprecia a anterior.
- Retrieval padrao exclui deprecated, inactive e expired.
- Documentos stale aparecem em auditoria; expired ficam fora do retrieval padrao.
- Fontes sem `last_checked_at` aparecem em `missing_metadata`.

## Test Plan

- Auditoria detecta stale source.
- Auditoria detecta expired source.
- Auditoria detecta deprecated/superseded source.
- Auditoria detecta metadata ausente.
- Auditoria detecta duas versoes ativas do mesmo `source_id`.
- Relatorio contem contadores corretos.
- `--fail-on-stale` falha quando aplicavel.
- `--fail-on-expired` falha quando aplicavel.
- Retrieval padrao ignora deprecated/expired.
- Ingestao preserva metadata no payload.

## Assumptions

- Sem chamadas externas e sem baixar novas fontes.
- Sem novas dependencias.
- O manifest `sources.yaml` continua sendo a fonte autoritativa para lifecycle do corpus.
- Datas desconhecidas nao devem ser inventadas; quando ausentes, a auditoria deve reportar lacuna.

