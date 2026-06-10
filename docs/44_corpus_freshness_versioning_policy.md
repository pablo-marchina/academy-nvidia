# Corpus Freshness, Versioning & Deprecation Policy

**Epic:** 20 - Corpus Freshness, Versioning & Deprecation Policy
**Data:** 2026-06-10
**Status:** Implementado

## Objetivo

Controlar versoes, frescor, expiracao e deprecacao do corpus NVIDIA para impedir que o Product RAG recupere conteudo antigo, duplicado, substituido ou fora de validade.

O corpus continua local e allowlist-based. Este epico nao adiciona crawler, nao baixa novas fontes e nao altera scoring, diagnosis, recommendation ou `recommended_motion`.

## Fonte de Verdade

`data/nvidia_corpus/sources.yaml` e o manifest autoritativo de lifecycle do corpus. Cada source pode ter:

- metadata ativa no topo do source, para compatibilidade com leitores existentes;
- `versions`, lista historica de versoes do mesmo `source_id`.

`data/nvidia_corpus/source_allowlist.yaml` define a politica esperada de sync/freshness por fonte permitida, mas nao substitui o manifest do corpus.

## Metadata

Campos de lifecycle por source/version:

| Campo | Obrigatorio | Descricao |
|---|---:|---|
| `version` | Sim | Versao logica da fonte no corpus |
| `content_hash` | Sim | Hash MD5 do documento local completo |
| `previous_content_hash` | Condicional | Hash da versao anterior quando houver supersession |
| `collected_at` | Sim | Quando o conteudo entrou no corpus |
| `last_checked_at` | Sim | Quando a fonte foi verificada pela ultima vez |
| `valid_from` | Sim | Inicio da validade da versao |
| `valid_until` | Nao | Fim da validade; expirado fica fora do retrieval padrao |
| `freshness_policy` | Sim | Politica humana (`weekly`, `monthly`, `never`) |
| `stale_after_days` | Sim para fontes ativas | Dias ate ficar stale |
| `is_active` | Sim | Se a versao participa do retrieval padrao |
| `deprecated_at` | Condicional | Quando a versao foi depreciada |
| `superseded_by` | Condicional | Versao sucessora |
| `deprecation_reason` | Condicional | Razao controlada da deprecacao |

## Estados

| Estado | Condicao | Efeito |
|---|---|---|
| Active | `is_active=true`, sem `deprecated_at`, sem `superseded_by`, sem expiracao | Elegivel ao retrieval padrao |
| Stale | `last_checked_at + stale_after_days < now` | Audit warning; requer sync/revisao |
| Expired | `valid_until < now` | Excluido do retrieval padrao |
| Deprecated | `is_active=false` ou `deprecated_at` presente | Excluido do retrieval padrao |
| Superseded | `superseded_by` presente | Excluido do retrieval padrao |
| Missing metadata | Campo obrigatorio ausente | Audit warning; deve ser corrigido antes de fechar epico |

## Regras de Versionamento

1. Uma fonte pode ter multiplas versoes no manifest.
2. Apenas uma versao ativa por `source_id` e permitida por padrao.
3. Alteracao de `content_hash` gera nova versao logica.
4. A nova versao fica `is_active=true`.
5. A versao anterior fica `is_active=false`, recebe `deprecated_at`, `superseded_by` e `deprecation_reason=superseded_by_new_content_hash`.
6. O bump padrao incrementa a ultima parte numerica da versao (`1.0 -> 1.1`).
7. Datas desconhecidas nao devem ser inventadas; a auditoria deve reportar lacunas.

## Auditoria

O script `scripts/audit_nvidia_corpus_freshness.py` roda offline:

```bash
python scripts/audit_nvidia_corpus_freshness.py --format json
python scripts/audit_nvidia_corpus_freshness.py --format markdown --report-path audit.md
python scripts/audit_nvidia_corpus_freshness.py --fail-on-stale
python scripts/audit_nvidia_corpus_freshness.py --fail-on-expired
```

Filtros:

- `--source-id nim triton`
- `--product "NVIDIA NIM"`

Relatorio:

- `audit_run_id`
- `generated_at`
- `sources_seen`
- `active_sources`
- `stale_sources`
- `expired_sources`
- `deprecated_sources`
- `superseded_sources`
- `missing_metadata`
- `duplicate_active_versions`
- `recommendations`

## Ingestao e Retrieval

`scripts/ingest_nvidia_corpus.py` preserva lifecycle metadata em `VectorEntry` e payload Qdrant:

- `is_active`
- `valid_from`
- `valid_until`
- `freshness_policy`
- `stale_after_days`
- `version`
- `deprecated_at`
- `superseded_by`
- `deprecation_reason`

Retrieval padrao:

- inclui apenas `is_active=true`;
- exclui `deprecated_at` e `superseded_by`;
- exclui `valid_until` expirado;
- permite override explicito via `RetrievalQuery(include_deprecated=True, include_expired=True)`.

## Limitacoes

- Stale ainda e tratado como audit warning, nao como bloqueio automatico do Action Brief.
- O script de sync continua allowlist-only e nao descobre novas paginas.
- A politica nao executa limpeza retroativa de colecoes Qdrant antigas; reingestao deve ser feita apos atualizar o manifest.
