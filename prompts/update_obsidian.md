# Update Obsidian

Atualize o vault Obsidian com as informacoes do epico atual.

## O que criar/atualizar

### Para todo epico concluido

1. **Nota de decisao** em `obsidian-vault/04 Decisions/`
   - Titulo: `Decision {NNN} - {Title}.md`
   - Conteudo: contexto, decisao, consequencias, status
   - Template: use ADR format

2. **Nota resumo** em `obsidian-vault/03 Research/`
   - Titulo: `Epic {N} - {Title}.md`
   - Conteudo: objetivo, entregues, decisoes, dependencias, status

3. **Known Limitations.md** em `obsidian-vault/02 Project Control/`
   - Adicione novas limitacoes
   - Remova limitacoes que foram resolvidas pelo epico

### Para epico de workspace

4. **Nota de workspace** em `obsidian-vault/02 Project Control/`
   - Titulo descritivo (ex.: `Development Workspace Quality System.md`)
   - Conteudo: visao geral, arquivos criados, regras

### Sempre

5. **Project Home.md** em `obsidian-vault/02 Project Control/`
   - Adicione links para novas notas relevantes
   - Mantenha a seccao "Links para notas principais" atualizada

## Formato

Use links Obsidian `[[...]]` para referenciar outras notas.
Use tags `#epic`, `#decision`, `#workspace` conforme aplicavel.
