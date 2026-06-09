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

## Fluxo de trabalho esperado
1. Entender a tarefa.
2. Conferir arquivos relevantes.
3. Propor plano curto.
4. Executar menor incremento util.
5. Validar resultado.
6. Atualizar documentacao se necessario.
7. Sugerir proximo passo.

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

## Estilo de codigo
- Python tipado.
- Pydantic para schemas.
- Funcoes pequenas.
- Separacao clara de responsabilidades.
- Codigo sem acoplamento desnecessario.
