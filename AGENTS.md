# AGENTS.md

## Projeto
NVIDIA Startup AI Radar — Plataforma multiagente para descobrir startups brasileiras AI-native, evidenciar maturidade técnica e recomendar tecnologias NVIDIA via RAG.

## Como Planejar Antes de Implementar
1. Leia `.ai/project_context.md` para contexto completo.
2. Leia contratos em `docs/contracts/` se for alterar módulo.
3. Para tarefa não trivial, salve plano em `docs/plans/YYYY-MM-DD_epic-XX_nome.md`.
4. Só inicie Build Mode com plano aprovado (exceto hotfix trivial).
5. Pergunte antes se houver ambiguidade bloqueante (máx 3 perguntas, com default recomendado).

## Escopo Pequeno Sempre
- Entregue o menor incremento útil por vez.
- Nunca implemente feature fora do plano aprovado.
- Prefira mudanças localizadas e testáveis.

## Regras de Código
- Python tipado com Pydantic para schemas.
- Funções pequenas, separação clara de responsabilidades.
- Sem acoplamento desnecessário.
- Sem segredos no código (use variáveis de ambiente).
- Sem fallback silencioso em produção — falhas devem ser explícitas.
- Todo módulo implementado deve ser usado, removido ou experimental.

## Regras de Teste
- Todo código novo deve vir com teste ou justificativa explícita.
- pytest para testes unitários e de integração.
- Schemas Pydantic validados nos testes.
- Não criar testes fantasmas ou vazios.

## Regras de Segurança
- .env, .venv, node_modules, caches e bancos locais nunca commitados.
- Não burlar login, paywall, robots.txt ou rate limits.
- Scraping com rate limit explícito e rastreável.

## Regras para Decisões Quantitativas
- Prefira scores numéricos a conceitos qualitativos.
- Todo score expõe: features usadas, pesos, confidence e uncertainty.
- Toda recomendação NVIDIA requer evidência + suporte RAG + confidence + business impact + implementation complexity + next best action.
- Separe fato, inferência e hipótese em todo output.

## Comandos de Validação
```bash
pytest                          # testes
ruff check .                    # linter
black --check .                 # formatação
mypy src                        # tipos
make validate                   # alias rápido
make validate-full              # completo (docs + frontend)
make prepare-release            # validação pré-release
python scripts/check_scope.py   # verifica contratos e docs
python scripts/check_docs_closure.py  # verifica fechamento de épico
```

## Fluxo de Trabalho
1. Entenda a tarefa.
2. Leia AGENTS.md + contratos + planos anteriores.
3. Plano curto → execução → review diff → validação → documentação → próximo passo.
