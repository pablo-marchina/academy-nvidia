# AGENTS.md

## Projeto
NVIDIA Startup AI Radar.

## Objetivo
Construir uma plataforma multiagente para identificar startups brasileiras AI-native, coletar evidencias publicas, diagnosticar maturidade tecnica e recomendar tecnologias NVIDIA.

## Prioridades
1. Rastreabilidade
2. Evidencias
3. Qualidade tecnica
4. Clareza executiva
5. Modularidade
6. Avaliacao continua
7. Nao inventar informacoes

## Regras obrigatorias
- Nenhuma afirmacao sobre startup deve ser aceita sem fonte.
- Nenhuma recomendacao NVIDIA deve ser feita sem gap tecnico explicito.
- Separar fato, inferencia e hipotese.
- Todo output estruturado deve seguir schema.
- Toda decisao tecnica importante deve ser registrada em DECISIONS.md.
- Todo codigo novo deve vir com teste ou justificativa de por que ainda nao tem teste.
- Nao priorizar frontend antes da pipeline principal funcionar.
- Nao criar componentes fantasmas na documentacao.
- Nao fazer scraping agressivo.
- Nao burlar login, paywall, robots.txt ou mecanismos de protecao.
- Preferir entregas pequenas e testaveis.

## Regras do Workspace de Desenvolvimento

### Plano
1. Todo trabalho nao trivial comeca em Plan Mode.
2. Todo plano aprovado deve ser salvo em `docs/plans/YYYY-MM-DD_epic-XX_nome-do-plano.md`.
3. Build Mode nao deve comecar sem plano salvo, exceto hotfix trivial justificado.

### Contratos
4. Antes de alterar um modulo, leia o contrato correspondente em `docs/contracts/`.
5. Respeite o escopo do plano aprovado.

### Revisao
6. Review Diff e obrigatorio antes do commit (use `prompts/review_diff.md`).

### Documentacao
7. O agente deve atualizar README, ROADMAP, DECISIONS, EVALS, Known Limitations e Obsidian quando aplicavel.
8. Erros relevantes devem ser registrados em `ERROR_LOG.md`.

### Disciplina
9. O agente nao deve implementar features fora do plano aprovado.
10. Se um item de fechamento nao se aplica, diga explicitamente por que.

### Validacao
11. Sempre rodar `make validate` (ou `scripts/validate.sh`) antes do commit.
12. Rodar `python scripts/check_scope.py` para verificar contratos e docs quando alterar `src/` ou `tests/`.
13. Antes de fechar um épico, rodar `python scripts/check_docs_closure.py`.

## Fluxo de trabalho esperado
1. Entender a tarefa.
2. Conferir arquivos relevantes (AGENTS.md, contratos, planos anteriores).
3. Propor plano curto (se nao trivial, salvar em `docs/plans/`).
4. Executar menor incremento util.
5. Rodar Review Diff antes do commit.
6. Rodar validacoes (`make validate` ou `scripts/validate.sh`).
7. Atualizar documentacao se necessario (README, ROADMAP, DECISIONS, EVALS, ERROR_LOG).
8. Atualizar Obsidian (decisoes, resumos, limitações).
9. Sugerir proximo passo.

## End-of-Epic Autonomous Closure

Ao finalizar um épico (antes de marcar como concluído), executar obrigatoriamente:

### Checklist de fechamento

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do épico.
- [ ] `DECISIONS.md` atualizado com decisoes arquiteturais do épico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.
- [ ] `docs/` — documentacao relevante atualizada ou criada.
- [ ] `python scripts/check_scope.py` passa (ou overrides justificados).
- [ ] `python scripts/check_docs_closure.py` passa (ou justificativa).
- [ ] `obsidian-vault/` — backfill realizado:
  - Nota de decisao em `04 Decisions/`
  - Nota resumo do épico em `03 Research/`
  - `Known Limitations.md` revisado
- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

### Regra
Se qualquer item do checklist falhar, o épico nao pode ser marcado como concluido. Corrigir antes de prosseguir.

## Comandos de validacao
- pytest
- ruff check .
- black --check .
- mypy src
- make validate (ou scripts/validate.sh)
- python scripts/check_scope.py
- python scripts/check_docs_closure.py

## Estilo de codigo
- Python tipado.
- Pydantic para schemas.
- Funcoes pequenas.
- Separacao clara de responsabilidades.
- Codigo sem acoplamento desnecessario.
