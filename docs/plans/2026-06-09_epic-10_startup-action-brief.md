# Plan: Epic 10 — Startup Action Brief

## Objective

Consolidar scores, evidencias, gaps, tecnologias NVIDIA, experimentos e recomendacoes em um unico output chamado Startup Action Brief. Nenhuma nova logica de scoring, diagnosis ou recommendation.

## Context Read

- AGENTS.md, README.md, ROADMAP.md, DECISIONS.md, EVALS.md
- docs/contracts/ (pipeline_output, evidence, diagnosis, recommendation, scoring)
- docs/16_briefing_template.md, docs/14_evidence_policy.md, docs/plans/PLAN_TEMPLATE.md
- src/pipeline/run_pipeline.py (PipelineResult)
- src/briefing/ (novo — nao existe)
- src/diagnosis/schemas.py, src/recommendation/schemas.py
- src/extraction/schemas.py, src/validation/evidence_validator.py
- src/scoring/defensibility_score.py, inception_fit_score.py, production_readiness.py, composite_ranking.py
- tests/unit/test_pipeline.py, obsidian-vault/

## Relevant Files

- **Create:** `src/briefing/__init__.py`, `src/briefing/schemas.py`, `src/briefing/action_brief.py`
- **Create:** `tests/unit/test_action_brief.py`
- **Create:** `docs/contracts/briefing_contract.md`
- **Update:** `docs/16_briefing_template.md`
- **Update:** `README.md`, `ROADMAP.md`, `DECISIONS.md`, `EVALS.md`
- **Update:** `obsidian-vault/03 Research/`, `04 Decisions/`

## Scope

- Criar modulo `src/briefing/` com schemas, builder e markdown renderer
- StartupActionBrief consolida PipelineResult em formato executivo
- 8+ testes unitarios cobrindo high-fit, weak-evidence, no-gap, missing-evidence, tech-blocked, uncertainties, markdown
- Contrato, template markdown, EVALS, README, ROADMAP, DECISIONS, Obsidian

## Out of Scope

- Sem alterar scoring/, diagnosis/, recommendation/ (exceto compatibilidade minima)
- Sem Product RAG, LangGraph, interface, PDF, frontend, novas dependencias
- Sem chamadas externas

## Proposed Implementation

1. Salvar plano em `docs/plans/`
2. Criar `src/briefing/schemas.py` com BriefVerdict, BriefUncertainty, BriefEvidenceItem, BriefSection, StartupActionBrief
3. Criar `src/briefing/action_brief.py` com `build_action_brief(PipelineResult) -> StartupActionBrief`
4. Criar `src/briefing/__init__.py` exportando API publica
5. Criar `tests/unit/test_action_brief.py` com 8+ testes
6. Atualizar `docs/16_briefing_template.md` com template real
7. Criar `docs/contracts/briefing_contract.md`
8. Atualizar EVALS.md, README.md, ROADMAP.md, DECISIONS.md
9. Obsidian backfill
10. pytest, ruff, black, mypy

## Tests/Validations

```bash
pytest
ruff check .
black --check .
mypy src
```

Test functions: `test_high_fit_startup`, `test_weak_evidence_brief`, `test_no_gaps_clear`, `test_missing_evidence_included`, `test_no_tech_without_gap`, `test_uncertainties_section`, `test_markdown_render`, `test_brief_schema_validation`, `test_json_serialization`

## Risks

| Risk | Mitigation |
|------|-----------|
| Brief duplica PipelineResult | Brief e uma projecao, nao uma copia cega |
| Acoplamento excessivo | Importa schemas existentes sem modifica-los |
| Brief longo demais | Secoes curtas (2-5 linhas); secoes vazias sao omitidas |
| Verdict inconsistente com motion | Logica deterministica: verdict = f(confidence, motion) |

## Definition of Done

- [ ] pytest 152 passing
- [ ] ruff, black, mypy sem erros novos
- [ ] build_action_brief retorna StartupActionBrief valido
- [ ] Markdown renderizado com 13 secoes
- [ ] docs/ updates feitos
- [ ] Obsidian backfill realizado

---

*Gerado em: 2026-06-09*
*Modo: Plan -> Build -> Review -> Commit*
