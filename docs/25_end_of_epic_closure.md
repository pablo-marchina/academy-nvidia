# End-of-Epic Autonomous Closure

## Objetivo

Garantir que todo épico entregue seja auditável, documentado e rastreável antes de ser marcado como concluído. Este documento define o processo obrigatório de fechamento.

## Gatilho

O closure é disparado automaticamente quando o último item funcional do épico é implementado e validado.

## Checklist obrigatório

### 1. Validação de código

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.

### 2. Documentação

- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do épico.
- [ ] `DECISIONS.md` atualizado com decisoes arquiteturais do épico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.

### 3. docs/

- [ ] Documentacao relevante atualizada ou criada.
- [ ] Nenhuma feature fantasma foi documentada.

### 4. Obsidian vault

- [ ] Nota de decisao criada em `obsidian-vault/04 Decisions/`.
- [ ] Nota resumo do épico criada em `obsidian-vault/03 Research/`.
- [ ] `obsidian-vault/02 Project Control/Known Limitations.md` revisado.

### 5. Qualidade

- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Todo codigo novo tem teste ou justificativa documentada.

## Regra

Se qualquer item do checklist falhar, o épico **nao pode** ser marcado como concluído. Deve-se corrigir antes de prosseguir.

## Exceções

- Se um épico nao produz codigo (ex.: pesquisa), os itens 1 e 5 sao opcionais.
- Se um épico nao produz decisoes arquiteturais, o item de DECISIONS.md e a nota de decisao no Obsidian sao opcionais.
- Qualquer excecao deve ser documentada no PR ou no commit de fechamento do épico.
