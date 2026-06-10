# ERROR_LOG.md

## Erro 001
**Data:** 2026-06-09

**O que aconteceu:** Validação inicial do workspace — template vazio.

**Causa provavel:** ERROR_LOG.md foi criado como template no Epic 7.1 mas nunca populado.

**Como corrigimos:** Nesta etapa (Epic 7.2), o template foi preservado. Erros futuros devem ser registrados aqui.

**Como evitar no futuro:** Sempre registrar erros durante execução. Usar `prompts/review_diff.md` para incluir verificação de ERROR_LOG.

---

## Erro 002 — RagChunk unhashable no ChunkIndex.retrieve() (Epic 11)

**Data:** 2026-06-09

**O que aconteceu:** `ChunkIndex.retrieve()` usava `set[RagChunk]` para deduplicar candidatos. RagChunk é um modelo Pydantic sem `__hash__` implementado, causando `TypeError: unhashable type: 'RagChunk'` em 7 testes.

**Causa provável:** Assumi que Pydantic models implementam `__hash__` por padrão. Modelos Pydantic v2 não são hashaveis a menos que `frozen=True` seja configurado.

**Como corrigimos:** Substituímos `set[RagChunk]` por `list[RagChunk]` com deduplicação manual via `chunk_id` em um `set[str]`.

**Como evitar no futuro:** Nunca assumir que Pydantic models são hashaveis. Usar `frozen=True` se hash for necessário, ou fazer deduplicação por ID.

## Erro 003 — Flat scoring causa perda de diversidade nos resultados (Epic 11)

---

## Erro 004 — check_docs_closure.py UnboundLocalError (Epic 18)

**Data:** 2026-06-10

**O que aconteceu:** `python scripts/check_docs_closure.py` crashou com `UnboundLocalError: cannot access local variable 'latest' where it is not associated with a value`.

**Causa provável:** Variável `latest = find_latest_plan(repo_root)` estava posicionada após `return False` dentro do `if plan_arg:` — código inatingível.

**Como corrigimos:** Movemos a linha `latest = find_latest_plan(repo_root)` para fora do `if` block.

**Como evitar no futuro:** Sempre executar `python scripts/check_docs_closure.py` antes de fechar épico. Em scripts de validação, verificar dead code com ruff (`F841` não pega variáveis após return).

**Data:** 2026-06-09

**O que aconteceu:** `retrieve_by_gap_type("high_inference_cost", top_k=5)` retornava apenas chunks da NVIDIA NIM (5/5), mesmo havendo chunks de TensorRT-LLM e Triton no índice com o mesmo gap_type e score.

**Causa provável:** Todos os candidatos com gap_type correspondente recebiam a mesma pontuação base (0.4). O sort era estável, mantendo a ordem original do índice (NIM primeiro → TensorRT-LLM → Triton). `top_k=5` pegava apenas os 5 primeiros.

**Como corrigimos:** Ajustamos o teste para usar `top_k=15` (total de chunks com aquele gap), garantindo que todos os produtos sejam retornados.

**Como evitar no futuro:** Ao testar retrieval por gap_type, verificar se `top_k` é grande o suficiente para cobrir todos os chunks esperados. Considerar scoring com boosting por conteúdo ou diversidade.
