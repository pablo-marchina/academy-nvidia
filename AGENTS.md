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
