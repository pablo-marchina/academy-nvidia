---
tags: [decision, epic-19]
date: 2026-06-10
---

# Decision 026 — Source Sync com Allowlist e Staging

**Context:** O corpus local (data/nvidia_corpus/) precisava ser atualizado manualmente.
O sync automatizado precisava de controles de seguranca (rate limit, robots.txt, timeout)
e separacao entre staging e promocao.

**Decision:** Criar scripts/sync_nvidia_sources.py com:
1. Allowlist versionada em YAML (source_allowlist.yaml)
2. Staging separado do corpus (staging/ antes de promover)
3. Archive automatico de versoes anteriores (archive/)
4. Comparacao de hash para evitar writes desnecessarios
5. Modo dry-run, staging-only, e promote
6. Controles de seguranca (robots.txt, rate limit, timeout, max-size)

**Alternativas consideradas:**
- Baixar direto para o corpus (rejeitado: sem rollback, sem validacao)
- Usar git submodules (rejeitado: complexidade desnecessaria)
- Scraping generico (rejeitado: sem controles de allowlist)

**Riscos:**
- URLs podem ficar obsoletas (404) — registrado como failed no relatorio
- Conteudo baixado pode ter formato imprevisivel — expected_format + validacao
- Fetcher pode ser bloqueado — robots.txt + rate limit mitigam

**Status:** Implementado no Epic 19.
