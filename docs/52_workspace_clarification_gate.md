# Workspace Clarification Gate

## Context

The NVIDIA Startup AI Radar project has grown to include many modules (pipeline, RAG, Qdrant, evals, dashboard, CLI, API, UI, docs, workflows). As the AI assistant generates larger artifacts, the risk of making unchecked assumptions increases — especially for frontend, API, architecture, contracts, workflows, dependencies, and scope changes.

The Clarification Gate is a workspace rule (Epic 26.1) that instructs the AI to ask clarifying questions before generating or modifying anything when critical ambiguity exists. It is defined in `AGENTS.md` under the "Workspace Clarification Gate" section.

## Purpose

1. Prevent the AI from generating large artifacts based on unchecked assumptions
2. Reduce retrabalho caused by wrong defaults (stack, scope, format, error policy)
3. Keep simple tasks fast — no bureaucracy for hotfixes or obvious steps
4. Provide safe fallback if the user does not respond to clarification requests

## How it works

### Triggers (when to ask)

Ask before generating when any of these is ambiguous:

- **Stack** — language, framework, libraries
- **Scope** — what is in and what is out
- **API contract** — input, output, error handling
- **Output format** — JSON, Markdown, specific schema
- **Expected behavior** — edge cases, defaults, nullability
- **Error policy** — raise exception, return default, log silently
- **Allowed dependencies** — existing only or can add new ones
- **Target environment** — dev, test, prod, CI, container
- **Example data** — format, representative values
- **Priority** — simplicity, robustness, or demonstrability first

### High-risk operations (always consider asking)

- Creating or modifying **frontend/UI**
- Creating or modifying **API endpoints**
- Changing **architecture** (modularity, coupling, layers)
- Changing **contracts** in `docs/contracts/`
- Adding a **new dependency**
- Changing **workflow/CI** (`.github/workflows/`)
- Generating **large documentation** (>50 lines)
- Creating a **new large epic** (>3 steps)
- Working on **pipeline** or **RAG**

### Non-triggers (when NOT to ask)

- **Small hotfix** (1-5 lines, no side effects)
- Decision already **explicit in context** (AGENTS.md, contract, approved plan, previous conversation)
- **Clear project pattern** (e.g., all modules use Pydantic, tests use pytest, schemas in `src/*/schemas.py`)
- Question **would only delay without changing the solution** (e.g., button color in a backend hotfix)
- **Smallest safe scope** is obvious (what causes least damage if wrong is clear)

### Limits

- Maximum **3 questions per turn**
- Short, objective questions (1 sentence each)
- If many doubts exist, ask **only the blocking ones**
- **Always include a recommended default** with each question

### Fallback (user does not answer)

1. **Smallest safe scope** — the choice that causes least damage if wrong
2. **Log the assumption** — e.g., "Assumed TypeScript stack because no answer was given"
3. **Avoid irreversible changes** — don't change public schema, migrate database, or refactor broadly
4. **Avoid new dependencies** — use only existing libraries
5. **Avoid broad refactoring** — prefer localized changes

### Format

Questions must start with:

    Perguntas bloqueantes antes de gerar:

Each question:

    1. <short question> Recomendado: <default>.

When proceeding without asking:

    Não há ambiguidade bloqueante. Segui com o menor escopo seguro.

## Examples

### Example 1 — UI stack
**User:** "Cria uma página de login."
**AI:**
```
Perguntas bloqueantes antes de gerar:
1. Stack da UI: React + Vite + TypeScript ou JS puro? Recomendado: TypeScript.
2. Estilo: CSS puro ou Tailwind? Recomendado: CSS puro (sem dependência nova).
3. Autenticação: endpoint existente ou criar mock? Recomendado: mock local.
```

### Example 2 — API endpoint contract
**User:** "Adiciona um endpoint para listar startups."
**AI:**
```
Perguntas bloqueantes antes de gerar:
1. Formato de resposta: lista de IDs ou objetos completos? Recomendado: objetos completos com paginação.
2. Filtros: por setor e score mínimo? Recomendado: sim, ambos opcionais.
3. Erro: 404 se vazio ou 200 com lista vazia? Recomendado: 200 com lista vazia.
```

### Example 3 — Qdrant destructive recreate
**User:** "Precisa dropar a collection do Qdrant e recriar."
**AI:**
```
Perguntas bloqueantes antes de gerar:
1. Collection name: a mesma ou nova? Recomendado: mesma (evita dangling references).
2. Backup: precisa salvar dados atuais antes? Recomendado: sim, exportar antes.
3. Impacto: há consumers rodando agora? Recomendado: verificar antes de dropar.
```

### Example 4 — Dependency addition
**User:** "Adiciona suporte a PDF parsing."
**AI:**
```
Perguntas bloqueantes antes de gerar:
1. Biblioteca: PyMuPDF, pdfminer.six ou pdfplumber? Recomendado: PyMuPDF (mais rápida).
2. Escopo: parse de texto apenas ou também tabelas/imagens? Recomendado: apenas texto por enquanto.
3. Instalação: adicionar ao pyproject.toml como extra opcional? Recomendado: sim, extra opcional.
```

### Example 5 — Large docs generation
**User:** "Gera documentação completa da arquitetura de agents."
**AI:**
```
Perguntas bloqueantes antes de gerar:
1. Formato: Markdown ou diagrama Mermaid? Recomendado: Markdown + Mermaid.
2. Público: time interno ou stakeholders NVIDIA? Recomendado: interno (menos glossário).
3. Escopo: todos os 9 agentes ou apenas os implementados? Recomendado: apenas os implementados (stubs ignorados).
```

### Example 6 — Hotfix (no questions)
**User:** "Corrige o typo no arquivo de configuração."
**AI:** "Não há ambiguidade bloqueante. Segui com o menor escopo seguro."
[Applies 2-line fix]

### Example 7 — Obvious step (no questions)
**User:** "Roda os testes para ver se está tudo verde."
**AI:** "Não há ambiguidade bloqueante. Segui com o menor escopo seguro."
[Runs pytest]

## Integration with existing workspace rules

The Clarification Gate is complementary to existing workspace rules:

1. **Plan first** — Clarification Gate happens *before* the plan, reducing retrabalho
2. **Contracts** — Gate asks about contract ambiguity *before* modifying modules
3. **Review Diff** — Gate does not replace review; it prevents wrong code from being written
4. **Discipline** — Gate reinforces "no features outside approved plan" by clarifying scope first

## Validation

The Clarification Gate is validated through:

- **Conversation log review** — questions use correct format, ≤3 per turn, include defaults
- **EVALS.md** — workspace quality criterion "Clarification Gate respeitado"
- **No automation needed** — the rule is a behavioral instruction for the AI, not a script

## References

- `AGENTS.md` — "Workspace Clarification Gate" section
- `DECISIONS.md` — Decision WSD-006
- `EVALS.md` — workspace quality criteria
- `README.md` — Clarification Gate mention in workspace rules
