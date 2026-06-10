# Build Epic

Voce esta em **Build Mode**. O plano foi aprovado.

## Pre-requisitos

- [ ] O plano foi salvo em docs/plans/ (exceto hotfix trivial)
- [ ] Contratos relevantes foram lidos (docs/contracts/)
- [ ] Escopo esta claro

## Regras

1. Implemente apenas o que esta no escopo do plano aprovado.
2. Nao implemente nada marcado como "Out of Scope".
3. Leia o contrato do modulo antes de altera-lo.
4. Prefira incrementos pequenos e testaveis.
5. Se encontrar algo inesperado, pare e reporte — nao continue implementando.

## Ao Finalizar

1. Execute Review Diff (prompts/review_diff.md)
2. Execute validacoes (pytest, ruff, black, mypy)
3. Atualize documentacao (README, ROADMAP, DECISIONS, EVALS)
4. Atualize Obsidian
5. Prepare mensagem de commit

## Lembretes

- "Enquanto estou aqui" nao e justificativa para escopo extra.
- Se nao tiver teste para o novo codigo, justifique explicitamente.
- Nao adicione dependencias sem aprovacao.
