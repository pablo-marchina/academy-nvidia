# Review Diff

Revise o diff abaixo antes do commit.

## Checklist

- [ ] **Escopo:** toda mudanca esta dentro do escopo do plano aprovado?
- [ ] **Fora de escopo:** alguma mudanca em src/ quando o epico e workspace?
- [ ] **Dependencias:** alguma nova dependencia foi adicionada sem justificativa?
- [ ] **Contratos:** schemas ou interfaces foram alterados sem atualizar o contrato em docs/contracts/?
- [ ] **Docs:** README, ROADMAP, DECISIONS, EVALS foram atualizados se aplicavel?
- [ ] **Obsidian:** nota de decisao criada? resumo do epico atualizado? Known Limitations revisado?
- [ ] **ERROR_LOG:** erros relevantes foram registrados?
- [ ] **Testes:** codigo novo tem teste (ou justificativa explicita por que nao tem)?
- [ ] **Alucinacao:** alguma fonte, tecnologia ou feature foi inventada?
- [ ] **Feature fantasma:** alguma feature foi documentada mas nao implementada?

## Formato de Saida

```
Review Diff: {PASS | FAIL}

Itens reprovados:
- {item}: {detalhe}

Se FAIL: corrija antes do commit.
Se PASS: commit pode prosseguir.
```
