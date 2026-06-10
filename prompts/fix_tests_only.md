# Fix Tests Only

**Escopo restrito:** corrigir apenas testes quebrados. Nao altere logica de producao.

## Regras

1. Identifique qual teste falhou e por que.
2. Determine se o teste esta errado (assertiva incorreta) ou o codigo esta errado.
3. Se o codigo de producao estiver errado, **crie um plano separado** — nao corrija aqui.
4. Se o teste estiver errado (ex.: mock desatualizado, schema mudou), corrija o teste.
5. Nao adicione novos testes — apenas corrija os existentes.
6. Nao altere `src/` a menos que o bug esteja no teste (ex.: import errado).
7. Execute `pytest` apos cada correcao.

## Justificativa Obrigatoria

Para cada correcao, explique:
- O que estava errado
- Por que a correcao e segura (nao mascara bug real)
- Por que nao alterou `src/`
