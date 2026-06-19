# Prompt Templates — NVIDIA Startup AI Radar

Templates reutilizáveis para operar o roadmap com agentes de IA.

---

## 1. Planning Prompt

**Objetivo:** Planejar antes de implementar.

```
## Planejamento: <título da tarefa>

### Arquivos que serão alterados
- <path>

### Arquivos que serão criados
- <path>

### Serviços existentes que serão reutilizados
- <serviço>

### Testes que serão criados/alterados
- <path>

### Gates quantitativos afetados
- <gate> — <métrica>

### Riscos
- <risco>

### Fora de escopo
- <item>

### Confirmação
Nenhum código será escrito nesta etapa. Apenas o plano.
```

---

## 2. Implementation Prompt

**Objetivo:** Implementar apenas o plano aprovado.

```
## Implementação: <título da tarefa>

### Regras
- Não alterar arquivos fora do plano.
- Não adicionar fallback silencioso em produção.
- Não duplicar lógica.
- Não enfraquecer testes existentes.
- Não adicionar dependências sem justificativa.

### Arquivos modificados
- <path>

### Testes a rodar
pytest <path>
ruff check .
black --check .
mypy src
```

---

## 3. Review Prompt

**Objetivo:** Revisar diff gerado por IA.

```
## Revisão: <título da tarefa>

### Verificações
- [ ] Escopo indevido — arquivo fora do plano foi alterado?
- [ ] Duplicação — lógica repetida foi introduzida?
- [ ] Fallback silencioso — try/except genérico sem tratamento?
- [ ] Ausência de testes — código novo sem teste?
- [ ] Ausência de métrica quantitativa — score sem confidence/uncertainty?
- [ ] Segurança — segredo, .env ou cache no diff?
- [ ] Regressão arquitetural — acoplamento desnecessário?
- [ ] Compatibilidade com produto real — demo/mock introduzido?
- [ ] Aderência aos acceptance gates — métrica aplicável foi violada?

### Resultado
- Aprovado / Correções necessárias / Bloqueado
```

---

## 4. Test Failure Fix Prompt

**Objetivo:** Corrigir falhas de teste sem enfraquecer validação.

```
## Correção de teste: <teste com falha>

### Causa raiz
<explicação>

### Regras
- Corrigir apenas o erro — não refatorar fora do escopo.
- Não remover asserts.
- Não relaxar validação sem justificativa forte registrada.
- Não alterar comportamento do código de produção além do necessário para corrigir o teste.

### Testes a rodar após correção
pytest <path>
```

---

## 5. Issue Creation Prompt

**Objetivo:** Transformar épico do roadmap em issue pequena.

```
## Issue: <título>

### Objetivo único
<uma frase>

### Contexto
<referência ao épico, decisão ou necessidade>

### Arquivos prováveis
- <path>

### Requisitos
- <item>

### Critérios quantitativos de aceite
- <gate> — <métrica alvo>

### Testes obrigatórios
- <descrição do teste>

### Fora de escopo
- <item>
```

---

## 6. Documentation Update Prompt

**Objetivo:** Atualizar docs quando mudança de produto for feita.

```
## Atualização de documentação

### Mudança realizada
<descrição>

### Docs a atualizar
- [ ] <path>

### Decisão arquitetural
- <se houver mudança, registrar em DECISIONS.md>

### Regras
- Atualizar apenas docs relacionadas à mudança.
- Não criar documentação duplicada.
- Não remover documentação existente sem justificativa.
- Não gerar docs para features não implementadas.
```
