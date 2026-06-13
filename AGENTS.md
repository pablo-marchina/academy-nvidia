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
14. Rodar `make acceptance` para validar o Product Golden Path antes de release. Não incluído em `make validate` (aceitação é lenta e separada).
15. Rodar `make prepare-release` para validação completa (validate + acceptance + ui-build) antes de marcar release.

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

## Workspace Clarification Gate

Antes de gerar código, arquitetura, documentação grande (>50 linhas), workflow,
frontend, API ou prompt extenso, verifique se há ambiguidade crítica que pode
levar a retrabalho ou decisão incorreta.

### When to ask questions

Pergunte antes quando faltar definição clara sobre:

- **Stack** — linguagem, framework, bibliotecas específicas
- **Escopo** — o que está dentro e o que está fora
- **Contrato de API** — entrada, saída, erros esperados
- **Formato de output** — JSON, Markdown, schema específico
- **Comportamento esperado** — casos de borda, defaults, nulabilidade
- **Política de erro** — lançar exceção, retornar default, logar silenciosamente
- **Dependências permitidas** — apenas as existentes ou pode adicionar
- **Alvo de ambiente** — dev, test, prod, CI, container
- **Dados de exemplo** — formato, valores representativos
- **Prioridade** — simplicidade, robustez ou demonstrabilidade primeiro

Atenção especial para estas operações de alto risco de ambiguidade:

- Criar ou alterar **frontend/UI**
- Criar ou alterar **API endpoints**
- Alterar **arquitetura** (modular, acoplamento, camadas)
- Alterar **contratos** em `docs/contracts/`
- Adicionar **dependência** nova
- Alterar **workflow/CI** (`.github/workflows/`)
- Gerar **documentação grande** (>50 linhas)
- Criar **novo épico grande** (>3 steps)
- Mexer em **pipeline** ou **RAG**

### When not to ask questions

Não pergunte quando:

- A tarefa for **hotfix pequeno** (1-5 linhas, sem efeito colateral)
- A decisão já estiver **explícita no contexto** (AGENTS.md, contrato, plano
  aprovado, conversa anterior)
- Houver **padrão claro no projeto** (ex: todos os módulos usam Pydantic,
  testes com pytest, schemas em `src/*/schemas.py`)
- A pergunta **só atrasaria sem mudar a solução** (ex: cor de botão em hotfix
  de backend, nome de variável local)
- O **menor escopo seguro** for evidente (o que causa menos dano se estiver
  errado é óbvio)

### Maximum number of questions

- **No máximo 3 perguntas por rodada**
- Perguntas curtas e objetivas (1 frase cada)
- Se houver muitas dúvidas, pergunte **apenas as bloqueantes**
- **Sempre inclua um default recomendado** em cada pergunta

### Default behavior if user does not answer

Se o usuário não responder, seguir estas regras em ordem:

1. **Menor escopo seguro** — a escolha que causa menos dano se estiver errada
2. **Registre a suposição** — ex: "Assumi stack TypeScript porque não houve resposta"
3. **Evite mudança irreversível** — não altere schema público, não migre banco,
   não refatore amplamente
4. **Evite dependência nova** — use apenas bibliotecas já no projeto
5. **Evite refatoração ampla** — prefira mudança localizada

### Format

As perguntas devem começar com:

```
Perguntas bloqueantes antes de gerar:
```

Cada pergunta no formato:

```
1. <pergunta curta> Recomendado: <default>.
```

Exemplo:

```
Perguntas bloqueantes antes de gerar:
1. Stack da UI: React + Vite + TypeScript ou JS puro? Recomendado: TypeScript.
2. Estilo: CSS puro ou biblioteca? Recomendado: CSS puro (sem dependência nova).
3. Estado global: Context API ou useState local? Recomendado: useState local.
```

Quando seguir sem perguntar, registre ao final da resposta:

```
Não há ambiguidade bloqueante. Segui com o menor escopo seguro.
```

### Examples

**Exemplo 1 — UI stack (perguntar):**
Usuário: "Cria uma página de login."
IA:
```
Perguntas bloqueantes antes de gerar:
1. Stack da UI: React + Vite + TypeScript ou JS puro? Recomendado: TypeScript.
2. Estilo: CSS puro ou Tailwind? Recomendado: CSS puro (sem dependência nova).
3. Autenticação: endpoint existente ou criar mock? Recomendado: mock local.
```

**Exemplo 2 — API endpoint contract (perguntar):**
Usuário: "Adiciona um endpoint para listar startups."
IA:
```
Perguntas bloqueantes antes de gerar:
1. Formato de resposta: lista de IDs ou objetos completos? Recomendado: objetos completos com paginação.
2. Filtros: por setor e score mínimo? Recomendado: sim, ambos opcionais.
3. Erro: 404 se vazio ou 200 com lista vazia? Recomendado: 200 com lista vazia.
```

**Exemplo 3 — Qdrant destructive recreate (perguntar):**
Usuário: "Precisa dropar a collection do Qdrant e recriar."
IA:
```
Perguntas bloqueantes antes de gerar:
1. Collection name: a mesma ou nova? Recomendado: mesma (evita dangling references).
2. Backup: precisa salvar dados atuais antes? Recomendado: sim, exportar antes.
3. Impacto: há consumers rodando agora? Recomendado: verificar antes de dropar.
```

**Exemplo 4 — Dependency addition (perguntar):**
Usuário: "Adiciona suporte a PDF parsing."
IA:
```
Perguntas bloqueantes antes de gerar:
1. Biblioteca: PyMuPDF, pdfminer.six ou pdfplumber? Recomendado: PyMuPDF (mais rápida).
2. Escopo: parse de texto apenas ou também tabelas/imagens? Recomendado: apenas texto por enquanto.
3. Instalação: adicionar ao pyproject.toml como extra opcional? Recomendado: sim, extra opcional.
```

**Exemplo 5 — Docs large generation (perguntar):**
Usuário: "Gera documentação completa da arquitetura de agents."
IA:
```
Perguntas bloqueantes antes de gerar:
1. Formato: Markdown ou diagrama Mermaid? Recomendado: Markdown + Mermaid.
2. Público: time interno ou stakeholders NVIDIA? Recomendado: interno (menos glossário).
3. Escopo: todos os 9 agentes ou apenas os implementados? Recomendado: apenas os implementados (stubs ignorados).
```

**Exemplo 6 — Hotfix (não perguntar):**
Usuário: "Corrige o typo no arquivo de configuração."
IA: "Não há ambiguidade bloqueante. Segui com o menor escopo seguro."
[Aplica correção de 2 linhas]

**Exemplo 7 — Passo óbvio (não perguntar):**
Usuário: "Roda os testes para ver se está tudo verde."
IA: "Não há ambiguidade bloqueante. Segui com o menor escopo seguro."
[Executa pytest]

## Workspace Output Validation Gate

Antes de marcar uma tarefa como concluida, valide os outputs gerados ou alterados
na proporcao do risco da tarefa.

### Quando validar

Valide obrigatoriamente quando a tarefa gerar ou alterar:

- JSON estruturado
- Markdown/documentacao grande (>50 linhas)
- planos ou epicos
- prompts extensos
- API request/response
- UI output relevante
- Startup Action Brief
- Answer Quality Eval
- regression dashboard
- codigo em `src/` ou `tests/`

Hotfix pequeno (1-5 linhas, sem efeito colateral e sem output estruturado) nao
deve ser bloqueado por processo pesado. Ainda assim, registre a validacao minima
aplicavel.

### Checklist antes de concluir

Antes de dizer que a tarefa esta pronta, verificar:

1. **Contrato** - output respeita schema, contrato ou template aplicavel?
2. **Formato** - JSON, Markdown, API response ou report estao bem formados?
3. **Escopo** - output nao inclui feature, arquivo ou promessa fora do plano?
4. **Evidencia/incerteza** - evidencias, gaps, missing_evidence e incertezas foram preservados?
5. **Checks operacionais** - testes/checks relevantes foram rodados ou a impossibilidade foi explicada?

### JSON

- Validar contra Pydantic/JSON Schema quando existir.
- Se nao houver schema, reportar `WARN` controlado e registrar a limitacao.
- Para Action Brief, validar secoes obrigatorias, `recommended_motion`, scores,
  gaps, tecnologias NVIDIA, evidencias, `missing_evidence` e incerteza quando
  confidence for baixa.

### Markdown

- Validar headings obrigatorios.
- Validar que secoes criticas nao estao vazias.
- Procurar placeholders nao resolvidos (`TODO`, `TBD`, `{placeholder}`).
- Conferir links/paths quando forem parte do criterio de pronto.

### API/UI

- Validar contrato request/response quando houver schema.
- Preservar `warnings`.
- Estados esperados de erro devem ser controlados; por exemplo, Qdrant offline
  deve virar warning/status explicito, nao crash silencioso.

### Falhas

- Se a falha estiver no escopo, corrija antes de concluir.
- Se estiver fora do escopo, reporte como pendencia explicita.
- Se a validacao for incerta, reporte a incerteza e sugira o proximo menor passo.
- Nunca esconda falha de contrato, formato, escopo ou evidencia.

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
- make validate-fast (rapido, apenas unit tests)
- make validate-full (completo, inclui docs + frontend)
- make validate (alias para validate-fast ou scripts/validate.sh)
- make prepare-release (validate-full + acceptance + ui-build)
- python scripts/check_scope.py
- python scripts/check_docs_closure.py

## Estilo de codigo
- Python tipado.
- Pydantic para schemas.
- Funcoes pequenas.
- Separacao clara de responsabilidades.
- Codigo sem acoplamento desnecessario.
