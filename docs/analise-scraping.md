# Análise do Sistema de Scraping — NVIDIA Startup AI Radar

## 1. Visão Geral

O módulo de scraping do **NVIDIA Startup AI Radar** é responsável por descobrir, coletar, extrair e monitorar informações sobre startups brasileiras de IA. O sistema é construído em Python com uma arquitetura **governada**, **orientada a estratégias** e **altamente resiliente**, projetada para operar em produção com conformidade legal e técnica.

### 1.1 Propósito

- Coletar dados de startups do ecossistema brasileiro de inovação
- Extrair sinais de adoção de IA, stack tecnológico, funding e equipe
- Monitorar mudanças em páginas ao longo do tempo
- Alimentar downstream: banco PostgreSQL, vetor store Qdrant, pipelines de scoring e briefing

---

## 2. Arquitetura Geral

```
                          ┌─────────────────────────────┐
                          │   CLI Scripts / Scheduler    │
                          │  (radar_scheduler.py,        │
                          │   run_full_scraping...)      │
                          └───────────┬─────────────────┘
                                      │
                          ┌───────────▼─────────────────┐
                          │    HttpSourceCollector       │
                          │   (orquestração governada)   │
                          └───┬───────┬──────┬──────────┘
                              │       │      │
                   ┌──────────▼──┐ ┌──▼───┐ ┌▼──────────┐
                   │ Compliance  │ │Robots│ │Strategy   │
                   │ Validation  │ │Check │ │Dispatcher │
                   └─────────────┘ └──────┘ └──┬────────┘
                                               │
         ┌───────────┬───────────┬───────┬─────▼────┬───────────┐
         │ YouTube   │ RSS/Atom  │  PDF  │Playwright │ Firecrawl │
         │ Collector │ Collector │Collect│ Collector │ Collector  │
         └───────────┴───────────┴───────┴──────────┴───────────┘
                                               │
              ┌────────────────────────────────▼──────────────────┐
              │            fetch_page() [httpx HTTP/2]             │
              │            + cache.py [diskcache LRU]              │
              │            + domain_rate_limiter.py                │
              │            + circuit_breaker.py                    │
              │            + tenacity retry (exponential backoff)  │
              └────────────────────────────────┬──────────────────┘
                                               │
              ┌────────────────────────────────▼──────────────────┐
              │         parser.py (extração de texto)             │
              │   readability-lxml → trafilatura → bs4            │
              └────────────────────────────────┬──────────────────┘
                                               │
              ┌────────────────────────────────▼──────────────────┐
              │   content_quality.py (validação)                  │
              │   fuzzy_dedup.py (dedup exato + fuzzy)            │
              └────────────────────────────────┬──────────────────┘
                                               │
              ┌────────────────────────────────▼──────────────────┐
              │   SourceFetchResult → downstream (DB, Qdrant)     │
              └──────────────────────────────────────────────────┘
```

---

## 3. Estrutura do Módulo

### 3.1 Core (`src/scraping/`)

| Arquivo | Responsabilidade |
|---------|------------------|
| `config.py` | Configuração centralizada via Pydantic Settings para todos os sub-módulos |
| `fetcher.py` | Fetch HTTP/2 via `httpx` com rotação de User-Agent, timeouts granulares |
| `parser.py` | Extração de texto limpo: `readability-lxml` → `trafilatura` → `selectolax` → `BeautifulSoup` |
| `cache.py` | Cache LRU em disco via `diskcache` (SQLite) com TTL por política de frescor |
| `http_collector.py` | Coletor HTTP principal com governança (compliance, robots.txt, rate limit, circuit breaker, retry, dedup, validação de qualidade) |
| `playwright_collector.py` | Coleta de páginas JS-heavy via `crawl4ai` (Playwright headless) |
| `firecrawl_collector.py` | Scraping via API Firecrawl |
| `youtube_collector.py` | Transcrição de vídeos YouTube via `youtube-transcript-api` |
| `rss_collector.py` | Coleta de feeds RSS/Atom via `feedparser` |
| `pdf_collector.py` | Extração de texto de PDFs via PyMuPDF (`fitz`) |
| `github_collector.py` | Coleta de dados via API GitHub (orgs, usuários, repositórios, READMEs) |
| `crunchbase_collector.py` | Scraping de perfis públicos Crunchbase |
| `strategies.py` | Registry de estratégias — dispatch de sources para o collector correto |
| `source_registry.py` | Gerenciamento de source records, validação de production readiness, allowlist |
| `source_policy.py` | Classificação de URLs (official, news, job, blog) |
| `rate_limit_policy.py` | Definições de rate limit policies (default_polite, github_api, news_site, etc.) |
| `domain_rate_limiter.py` | Rate limiting por domínio (mínimo entre todas as políticas ativas) |
| `circuit_breaker.py` | Circuit breaker por domínio (abre após 5 falhas, half-open após 300s) |
| `content_quality.py` | Validação de qualidade (boilerplate, paywall, login, idioma) |
| `change_detector.py` | Detecção de mudanças entre runs com classificação de severidade |
| `fuzzy_dedup.py` | Deduplicação exata (SHA-256) + fuzzy (rapidfuzz token_set_ratio) |
| `page_discovery.py` | Descoberta de URLs via sitemap.xml, paths comuns e crawling de links |
| `startup_crawler.py` | Orquestrador de crawling por startup (site, blog, careers) |
| `founder_discovery.py` | Extração de nomes de founders e links sociais |
| `tech_stack_detector.py` | Detecção de stack tecnológico (LLM, GPU, inference, data, devops) |
| `directory_extractor.py` | Extração de listagens de startups de páginas de diretório |
| `directory_paginator.py` | Estratégias de paginação (query param, infinite scroll, next-link) |
| `scrapy_bridge.py` | Bridge para ingerir output JSON do Scrapy no pipeline governado |
| `metrics.py` | Métricas Prometheus para todo o pipeline de scraping |

### 3.2 Scrapers Específicos (`src/scraping/scrapers/`)

| Arquivo | Alvo |
|---------|------|
| `ace_scraper.py` | ACE Startups portfolio |
| `bossa_scraper.py` | Bossa Invest portfolio |
| `cubo_scraper.py` | Cubo Itau innovation hub |
| `distrito_scraper.py` | Distrito startup programs |
| `inovativa_scraper.py` | Inovativa accelerator |
| `openstartups_scraper.py` | 100 Open Startups ranking |

### 3.3 Sourcing Adapters (`src/sourcing/adapters/`)

| Arquivo | Propósito |
|---------|-----------|
| `base.py` | `SourceAdapter` abstrato, `EvidenceSpan`, `SourceResult` |
| `static_html.py` | Coleta de páginas HTML estáticas via pipeline governado |
| `official_website.py` | Site oficial de startup com extração de título |
| `news.py` | Coleta de artigos de notícias com validação de URL |
| `founder_profile.py` | Extração de informações de founders |
| `dynamic_page.py` | Coleta de páginas JS-heavy via Playwright |
| `directory.py` | Scraping de diretórios de aceleradoras/ecossistema |
| `career_page.py` | Coleta de páginas de carreiras com validação de relevância |

### 3.4 Scripts CLI

| Script | Função |
|--------|--------|
| `run_full_scraping_pipeline.py` | Pipeline completo: sync NVIDIA + discovery + report |
| `radar_scheduler.py` | Rescrape periódico com detecção de mudanças |
| `scheduler_refresh.py` | Refresh de fontes obsoletas baseado em políticas de frescor |
| `calibrate_scraping_baseline.py` | Calibração de baseline de scraping |
| `proactive_discovery.py` | Descoberta proativa via web search + Reddit + HN |
| `live_collect.py` | Verificação de reachabilidade de URLs |
| `sync_nvidia_sources.py` | Sincronização do corpus NVIDIA |
| `source_coverage_report.py` | Relatório de cobertura de fontes |
| `verify_source_urls.py` | Verificação de URLs |
| `generate_spiders.py` | Gerador de spiders Scrapy |

---

## 4. Fluxo de Dados Detalhado

### 4.1 Ciclo de Vida de uma Coleta

1. **Configuração**: Fontes definidas em `data/scraping/source_records.yaml` (~40 fontes) + `data/nvidia_corpus/source_allowlist.yaml` (~18 fontes NVIDIA)

2. **Validação de Production Readiness**: Cada fonte é verificada contra:
   - `calibrated_priority_score` definido
   - `paywall_risk` não é "mandatory"
   - `requires_login` é False
   - `rate_limit_policy_id` existe no registry
   - `robots_required` está definido
   - API keys disponíveis (se required)

3. **Compliance Check**: Validação individual por `_validate_source()`:
   - `production_enabled == True`
   - `requires_login == False`
   - `paywall_risk != "mandatory"`
   - `calibrated_priority_score` não é None
   - `rate_limit_policy_id` existe

4. **Robots.txt Check**: Verificação de permissão via parser customizado com suporte a Allow/Disallow/Crawl-delay e longest-matching-path. Cache de 24h.

5. **Strategy Dispatch**: Baseado no `collector_type`:
   - `http` → fetch_page() com httpx
   - `youtube` → youtube_transcript_api
   - `rss` → feedparser
   - `pdf` → PyMuPDF
   - `playwright` → crawl4ai
   - `firecrawl` → Firecrawl API
   - `optional_playwright` → tenta http primeiro, fallback playwright

6. **Rate Limiting**: Por domínio, calcula o mínimo entre todas as políticas ativas para aquele domínio

7. **Circuit Breaker**: Por domínio, 5 falhas consecutivas → aberto por 300s

8. **Cache Check**: SQLite LRU via diskcache. Suporta ETag/Last-Modified para conditional requests. TTL por política de frescor:
   - daily → 24h (news, rss)
   - weekly → 7d (blog, directory, github)
   - monthly → 30d (official, nvidia)
   - static → 365d

9. **Fetch com Retry**: `tenacity` com exponential backoff:
   - Retry em: 429 (rate limit), 5xx, erros de rede
   - Não retry em: 4xx (exceto 429)
   - Timeout configurável (default 15s)
   - Limite de 5MB por resposta

10. **Extração de Texto**: Pipeline cascata:
    - readability-lxml (artigo)
    - trafilatura
    - selectolax
    - BeautifulSoup

11. **Validação de Qualidade**: Detecta:
    - Conteúdo muito curto (< 200 chars)
    - Boilerplate (erros 404, access denied, Cloudflare)
    - Login walls
    - Paywalls
    - Idioma inesperado (não pt/en)
    - CAPTCHA

12. **Deduplicação**: Duas camadas:
    - Exata: SHA-256 do texto
    - Fuzzy: `rapidfuzz.token_set_ratio` (threshold 0.85)

13. **Detecção de Mudanças** (radar_scheduler):
    - Compara hash atual com histórico
    - Gera diff por linhas
    - Classifica severidade:
      - CRITICAL: aquisição, IPO, unicórnio
      - HIGH: funding, série, investimento
      - MEDIUM: lançamento, parceria, contratação
      - LOW: outras mudanças
    - Persiste alertas HIGH/CRITICAL em `.radar_alerts.json`

14. **Armazenamento**: Resultados como `SourceFetchResult` → downstream para PostgreSQL + Qdrant

---

## 5. Fontes Configuradas

### 5.1 Diretórios de Aceleradoras e Hubs (ecosystem_directory)
ACE Startups, Bossa Invest, Cubo Itau, Distrito, Inovativa, 100 Open Startups, Endeavor, Liga Ventures, WOW Aceleradora, Darwin Startups, ABStartups, Anjos do Brasil, Latitud

### 5.2 Notícias de Funding e Negócios (funding_news)
Brazil Journal, Exame, NeoFeed, Pipeline Capital, Startups.com.br, PEGN, Startupi

### 5.3 Mídia Geral (media)
Valor Econômico, Meio & Mensagem, Mobile Time, StartSe

### 5.4 Ecossistema NVIDIA (nvidia_or_partner_ecosystem)
NIM, NeMo, NeMo Guardrails, Triton, TensorRT-LLM, RAPIDS (cuDF, cuML), Riva, Morpheus, Isaac, Omniverse, Clara/MONAI, NVIDIA Inception, NVIDIA Developer, YouTube playlists NVIDIA, API Catalog

### 5.5 Outras Categorias
- `jobs`: LinkedIn, startup career pages
- `official_website`: site oficial de startup (runtime)
- `technical_docs`: documentação técnica (runtime)
- `github_or_code`: GitHub API

---

## 6. Métricas e Observabilidade

Métricas Prometheus exportadas via `src/scraping/metrics.py`:

| Métrica | Tipo | Labels |
|---------|------|--------|
| `scraping_fetches_total` | Counter | status |
| `scraping_fetch_duration_seconds` | Histogram | - |
| `scraping_fetch_bytes_total` | Counter | - |
| `scraping_cache_hits_total` | Counter | - |
| `scraping_cache_misses_total` | Counter | - |
| `scraping_cache_size_bytes` | Gauge | - |
| `scraping_cache_evictions_total` | Counter | - |
| `scraping_duplicates_detected_total` | Counter | method |
| `scraping_fuzzy_index_size` | Gauge | - |
| `scraping_circuit_breaker_trips_total` | Counter | domain |
| `scraping_circuit_breaker_state` | Gauge | domain |
| `scraping_rate_limit_throttled_total` | Counter | domain |
| `scraping_content_quality_failures_total` | Counter | reason |
| `scraping_collection_runs_total` | Counter | status |
| `scraping_sources_collected_total` | Counter | - |
| `scraping_robots_check_total` | Counter | result |
| `scraping_parse_duration_seconds` | Histogram | - |
| `scraping_parse_failures_total` | Counter | parser |

---

## 7. Dependências

### Produção
| Biblioteca | Uso |
|-----------|-----|
| `httpx` | Cliente HTTP/2 para todas as requisições |
| `requests` | Fallback HTTP |
| `beautifulsoup4` | Parsing HTML |
| `trafilatura` | Extração de texto de artigos |
| `playwright` / `crawl4ai` | Navegador headless para JS-heavy |
| `diskcache` | Cache LRU em disco (SQLite) |
| `rapidfuzz` | Fuzzy matching para deduplicação |
| `youtube-transcript-api` | Transcrição de vídeos YouTube |
| `feedparser` | Parsing de feeds RSS/Atom |
| `pymupdf` | Extração de texto de PDFs |
| `fake-useragent` | Rotação de User-Agent |
| `tenacity` | Retry com backoff exponencial |
| `tldextract` | Extração de domínio |
| `selectolax` | Parsing HTML rápido |
| `readability-lxml` | Extração de artigo |
| `langdetect` | Detecção de idioma |
| `orjson` | JSON rápido |
| `pydantic` / `pydantic-settings` | Configuração e modelos |
| `prometheus_client` | Métricas |
| `praw` | API Reddit (discovery) |
| `markitdown` | Conversão para markdown |
| `python-dotenv` | Variáveis de ambiente |

### Opcionais (scraping)
Instalação: `pip install academy-nvidia[scraping]`

---

## 8. Configuração

### 8.1 Variáveis de Ambiente (`.env`)
```
SCRAPING_HTTP_TIMEOUT_SECONDS=15
SCRAPING_CACHE_DIRECTORY=.cache/scraping
SCRAPING_RATE_LIMIT_MIN_RPS_FLOOR=0.5
FIRECRAWL_API_KEY=...
GITHUB_TOKEN=...
```

### 8.2 Source Records (`data/scraping/source_records.yaml`)
Cada fonte possui:
- `source_id`, `source_name`, `source_category`
- `base_url`, `allowed_paths`, `disallowed_paths`
- `rate_limit_policy_id`, `collector_type`, `parser_type`
- `calibrated_priority_score`, `priority_calibration_decision_id`
- `expected_evidence_types`, `expected_claim_types`
- `paywall_risk`, `requires_login`, `robots_required`
- `production_enabled` (calculado automaticamente)

### 8.3 Rate Limit Policies (`rate_limit_policy.py`)
| Policy | RPS | Concurrent | Retry | Uso |
|--------|-----|------------|-------|-----|
| `default_polite` | 2 | 1 | 3 | Geral |
| `news_site` | 1 | 1 | 2 | Sites de notícia |
| `directory_listing` | 5 | 1 | 2 | Diretórios |
| `github_api` | 1.3 | 1 | 3 | API GitHub |
| `nvidia_eco` | 3 | 1 | 2 | NVIDIA |
| `search_engine` | 1 | 1 | 1 | Motores de busca |

---

## 9. Mecanismos de Resiliência

### Circuit Breaker
- Estado: CLOSED → OPEN (5 falhas consecutivas) → HALF-OPEN (após 300s) → CLOSED (1 sucesso)
- Atua por domínio
- Thread-safe

### Rate Limiter
- Por domínio, agregando múltiplas políticas
- Intervalo efetivo = mínimo entre todas as políticas ativas
- Thread-safe

### Retry
- Exponencial: `multiplier=2.0, min=1s, max=30s`
- Retry em: 429, 5xx, erros de rede
- Não retry em: 4xx (exceto 429)
- Stale-content fallback: serve cache se fetch falhar

### Desligamento Gracioso
- Signal handlers (SIGINT/SIGTERM)
- `atexit` cleanup (fecha conexões)
- Futures cancelados em shutdown

---

## 10. Detecção de Tecnologia

O `tech_stack_detector.py` identifica sinais em 5 categorias:

| Categoria | Exemplos |
|-----------|----------|
| **LLM** | GPT-4, Claude, LangChain, RAG, OpenAI, Anthropic |
| **GPU** | CUDA, A100, H100, PyTorch GPU, cuDF |
| **Inferência** | Triton, vLLM, TGI, model serving |
| **Dados** | Spark, Kafka, Postgres, Airflow |
| **DevOps** | Kubernetes, Docker, CI/CD, AWS, GCP |

Além disso, detecta cargos em páginas de careers (ML Engineer, Data Scientist, etc.) e requisitos técnicos.

---

## 11. Descoberta de Páginas

O `page_discovery.py` usa 3 estratégias sequenciais:

1. **Sitemap.xml**: tenta `/sitemap.xml`, `/sitemap_index.xml`, `/sitemap/` e filtra por paths relevantes
2. **Paths comuns**: `/about`, `/team`, `/careers`, `/blog`, `/product`, etc.
3. **Crawling de links**: se HTML fornecido e depth > 0, extrai links internos

Priorização: paths exatos > paths parciais > root

---

## 12. Conformidade e Ética

- **Robots.txt**: parser customizado respeita Allow/Disallow/Crawl-delay
- **Rate limiting**: por domínio, respeita Crawl-delay do robots.txt
- **Termos de uso**: `terms_review_required` flag para fontes que exigem revisão
- **Paywall detection**: identificação de paywalls obrigatórios (block) e opcionais (warning)
- **Login detection**: bloqueio de fontes que exigem login
- **User-Agent**: identificação transparente (`NVIDIAStartupAIRadar/0.1`)

---

## 13. Pipeline de Execução

O pipeline completo (`run_full_scraping_pipeline.py`) executa:

1. **NVIDIA source sync** → download de documentação NVIDIA para staging
2. **Discovery runs** → scraping de fontes de diretório via service layer
3. **Coverage report** → sumário de cobertura

O scheduler (`radar_scheduler.py`) faz rescrape periódico com detecção de mudanças, ideal para execução em cron jobs ou containers.

---

## 14. Testes

O projeto possui testes unitários e de integração no diretório `tests/`. A calibração do baseline de scraping é feita via `scripts/calibrate_scraping_baseline.py`, que realiza grid search sobre parâmetros e avalia marginal gains.

---

## 15. Diagrama de Classes Simplificado

```
ScrapingConfig
  ├── HTTPSettings
  ├── CacheSettings
  ├── RateLimitSettings
  ├── CircuitBreakerSettings
  ├── ContentQualitySettings
  ├── ParserSettings
  └── ...

SourceRecord (Pydantic)
  ├── source_id, source_name, source_category
  ├── base_url, collector_type, rate_limit_policy_id
  ├── calibrated_priority_score
  └── production_enabled

HttpSourceCollector
  ├── collect(request: CollectionRequest) → CollectionResult
  ├── collect_one(source) → SourceFetchResult
  ├── _validate_source()
  ├── _fetch_with_tenacity()
  └── _compute_metrics()

SourceFetchResult
  ├── status: "fetched" | "duplicate" | "blocked" | "failed" | "dry_run"
  ├── extracted_text, raw_html
  ├── content_hash, latency_ms
  └── error_code, error_message_sanitized

Strategies Registry
  ├── register("youtube", fn)
  ├── register("rss", fn)
  └── resolve(source) → fn

DomainRateLimiter → wait_if_needed(url, rps)
CircuitBreaker → is_open(url) / record_failure(url) / record_success(url)
ContentQualityValidator → validate(html) → ContentQuality
DedupIndex → is_duplicate(text) / index(text)
ChangeDetector → detect(old_hash, new_hash, old_text, new_text) → ChangeReport
```

---

> **Nota**: Este documento reflete a arquitetura e implementação atuais do módulo de scraping. Para detalhes atualizados, consulte o código-fonte e os testes correspondentes.
