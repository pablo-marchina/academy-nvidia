# Automated NVIDIA Corpus Source Sync

**Epic 19** | **Data:** 2026-06-10

## Objetivo

Criar um script de sync automatizado (`scripts/sync_nvidia_sources.py`) que baixa
ou atualiza documentos NVIDIA permitidos para uma area de staging, valida
metadata/provenance/hash, gera relatorio de sync e so promove ao corpus local
apos validacao.

Nao faz ingestao direta no Qdrant — o script `scripts/ingest_nvidia_corpus.py`
deve ser executado separadamente apos o sync.

## Arquitetura

```
source_allowlist.yaml  (fontes permitidas com metadata)
        |
        v
sync_nvidia_sources.py
        |
        +-- 1. Carregar allowlist
        +-- 2. Validar entries
        +-- 3. Filtrar (source-id, product)
        +-- 4. Baixar fontes (com rate limit e robots.txt)
        +-- 5. Salvar em staging/
        +-- 6. Comparar hash com corpus atual
        +-- 7. Gerar relatorio
        +-- 8. Se --promote: copiar para corpus/ + archive/
```

## Fluxo de Diretorios

```
data/nvidia_corpus/
+-- source_allowlist.yaml       # Allowlist versionada
+-- sources.yaml                # Metadata atual (pode ser atualizado via --promote)
+-- nim.md                      # Corpus atual (alterado via --promote)
+-- ...
+-- staging/                    # Area de preparacao
|   +-- <source_id>/
|       +-- <timestamp>.md      # Conteudo baixado
|       +-- <timestamp>_meta.json  # Metadados do download
+-- archive/                    # Snapshots pre-promocao
|   +-- <source_id>/
|       +-- <timestamp>_<source_id>.md
+-- sync_reports/               # Relatorios de sync
    +-- sync_<timestamp>.json
```

## CLI

```
scripts/sync_nvidia_sources.py [OPCOES]

  --dry-run                    Valida allowlist apenas, sem fetching ou promocao
  --source-id SOURCE_ID       Filtrar sync por source_id (ex: nim triton)
  --product PRODUCT            Filtrar sync por product
  --promote                   Promover staging validado para corpus + sources.yaml
  --staging-only              Baixar para staging, nao promover
  --report-path PATH           Salvar sync report em JSON
  --fail-on-validation-error   Exit 1 se validation da allowlist falhar
  --max-documents N            Limitar downloads (para teste)
  --rate-limit-seconds N       Segundos entre requests (default: 2.0)
```

### Exemplos

```bash
# Dry-run: valida allowlist
python scripts/sync_nvidia_sources.py --dry-run

# Staging-only: baixa tudo para staging
python scripts/sync_nvidia_sources.py --staging-only

# Sync uma fonte especifica com promote
python scripts/sync_nvidia_sources.py --source-id nim --promote

# Sync completo com relatorio
python scripts/sync_nvidia_sources.py --promote --report-path reports/sync.json

# Rate limit customizado
python scripts/sync_nvidia_sources.py --staging-only --rate-limit-seconds 5.0
```

## Allowlist Schema

Arquivo `data/nvidia_corpus/source_allowlist.yaml`:

```yaml
allowlist_version: "1.0"
sources:
  - source_id: nim
    title: "NVIDIA NIM"
    url: "https://docs.nvidia.com/nim/latest/"
    product: "NVIDIA NIM"
    gap_types: ["external_api_dependency", "high_inference_cost", "high_latency"]
    document_type: "nvidia_corpus"
    allowed: true
    update_frequency: "weekly"
    expected_format: "markdown"
    license_note: "NVIDIA Documentation License"
    notes: "..."
```

### Campos obrigatorios

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `source_id` | string | Identificador unico |
| `title` | string | Titulo da fonte |
| `url` | string | URL https da documentacao |
| `product` | string | Nome do produto NVIDIA |
| `gap_types` | list[string] | Gaps que a tecnologia atende |
| `document_type` | string | Tipo do documento |
| `allowed` | bool | Se true, pode ser baixado |

## Estrategia de Staging/Promotion

### Staging

- Cada download salva em `staging/<source_id>/<timestamp>.md`
- Arquivo `_meta.json` acompanha cada download com source_id, url, content_hash, sync_run_id
- `--staging-only` nunca altera corpus ou sources.yaml

### Promotion

- `--promote` copia de staging para `data/nvidia_corpus/<source_id>.md`
- Versao anterior vai para `archive/<source_id>/<timestamp>_<source_id>.md`
- `sources.yaml` e atualizado com metadata da allowlist
- Nada e deletado — archive mantem historico

### Comparacao de Hash

- `content_hash` (MD5) comparado entre conteudo baixado e arquivo atual
- Se hash identico: registrado como `unchanged`, nao copiado
- Se hash diferente: registrado como `changed`, copiado para staging
- Se fonte nova (sem .md existente): registrado como `new`

## Seguranca

| Controle | Implementacao |
|----------|---------------|
| User-Agent claro | `NVIDIA-Startup-AI-Radar/1.0 (sync; academic-project; contact@example.com)` |
| Timeout | 30s via `urllib.request.urlopen(timeout=30)` |
| Tamanho maximo | 5 MB (rejeita se Content-Length > 5MB ou body > 5MB) |
| Sem redirects externos | Nao segue automaticamente (apenas mesmo dominio) |
| Sem cookies | Nenhum Cookie header |
| Sem login | Nenhuma autenticacao |
| Sem follow de links | Baixa apenas URL exata da allowlist |
| Rate limit | `time.sleep(args.rate_limit_seconds)` (default 2.0s) |
| robots.txt | Verifica antes de baixar |
| Conteudo nao confiavel | Tratado como dado, nunca executado |
| SSL verification | Ativa (default context) |
| Encoding | UTF-8 com fallback |
| Conteudo curto | Rejeitado se < 100 chars |

## Relatorio de Sync

```json
{
  "sync_run_id": "sync_20260610_120000",
  "started_at": "2026-06-10T12:00:00",
  "finished_at": "2026-06-10T12:00:30",
  "sources_seen": 10,
  "sources_downloaded": 8,
  "sources_unchanged": 3,
  "sources_changed": 4,
  "sources_new": 1,
  "sources_failed": ["bad_source"],
  "validation_errors": [],
  "promoted_files": ["data/nvidia_corpus/nim.md"],
  "skipped_files": [],
  "hashes": {
    "nim": "abc123...",
    "triton": "def456..."
  },
  "allowlist_version": "1.0"
}
```

## Diferenca do Script de Ingestao (Epic 18)

| Aspecto | `sync_nvidia_sources.py` (Epic 19) | `ingest_nvidia_corpus.py` (Epic 18) |
|---------|--------------------------------------|---------------------------------------|
| Entrada | URLs da allowlist | Arquivos .md do corpus local |
| Saida | Arquivos .md no corpus | Pontos Qdrant |
| Fonte dos dados | Externa (docs.nvidia.com) | Local (data/nvidia_corpus/) |
| Chamada externa | Sim (download das URLs) | Nao |
| Rate limit | Sim | Nao |
| Alteracao do corpus | Sim (--promote) | Nao |
| Ingestao Qdrant | Nao | Sim |

## Testes

### Unitarios (49 testes)

- allowlist validation (8)
- disallowed source (1)
- content hashing (3)
- safe fetcher (5)
- robots.txt (2)
- dry-run (2)
- staging-only (1)
- CLI args (10)
- fetch source mocked (3)
- hash unchanged (2)
- report (3)
- staging I/O (2)
- promote (2)
- get corpus hash (2)
- load allowlist (1)
- update sources.yaml (2)

Nenhuma chamada externa real — fetcher, urlopen e robots.txt sao mockados.

## Manutencao

Para adicionar nova fonte:
1. Adicionar entrada em `source_allowlist.yaml` com `allowed: true`
2. Executar `python scripts/sync_nvidia_sources.py --source-id <id> --staging-only`
3. Revisar o .md em staging/
4. Executar `python scripts/sync_nvidia_sources.py --source-id <id> --promote`
5. Executar `python scripts/ingest_nvidia_corpus.py` para ingerir no Qdrant
