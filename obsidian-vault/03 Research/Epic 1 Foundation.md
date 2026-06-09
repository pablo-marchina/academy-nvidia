---
type: epic
status: completed
date: 2026-06
---

# Epic 1 — Foundation (Scraping + Extraction)

## Objetivo
Construir a camada base de coleta e extracao estruturada de dados publicos de startups.

## Modulos criados
- `src/scraping/fetcher.py` — HTTP GET com timeout, tratamento de erro
- `src/scraping/parser.py` — extracao de texto limpo via trafilatura + BS4 fallback
- `src/scraping/source_policy.py` — classificacao de fontes, blocklist
- `src/extraction/extractor.py` — extracao estruturada (sector, signals, tech stack, customers, funding)
- `src/extraction/schemas.py` — modelos Pydantic (StartupProfile, Evidence, enums)

## Testes
- 14 testes no extrator
- 7 testes no fetcher (mocked)
- 4 testes no parser
- 3 testes no source policy
- 4 testes nos schemas

## Decisoes
- Schemas Pydantic como fonte unica de verdade
- Regex-based extraction (sem LLM)
- Source policy baseada em URL

## Links
- [[../04 Decisions]]
