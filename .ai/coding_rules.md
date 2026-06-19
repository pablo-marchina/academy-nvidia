# Coding Rules — NVIDIA Startup AI Radar

## Escopo Pequeno
- Trabalhe em tarefas pequenas e entregáveis.
- Modifique o menor número possível de arquivos por tarefa.
- Nunca implemente feature fora do plano aprovado.

## Planejamento
- Leia `.ai/project_context.md` e contratos em `docs/contracts/` antes de alterar módulo.
- Tarefas não triviais exigem plano salvo em `docs/plans/`.
- Planeje antes de implementar.

## Reutilização
- Reutilize serviços existentes — não crie novos módulos para funcionalidade já implementada.
- Não duplique lógica; prefira composição a cópia.

## Tratamento de Erros
- Nunca crie fallback silencioso em produção — falhas devem ser explícitas.
- Não use `except Exception: pass` ou `except: pass` amplos.
- Erros devem ser logados e propagados, nunca engolidos.

## Dependências
- Não adicione dependência nova sem justificativa por escrito.
- Prefira bibliotecas já no projeto.

## Testes
- Não enfraqueça testes existentes (não remova asserts, não relaxe validação).
- Todo código novo exige teste ou justificativa explícita.

## Segurança
- Nunca commitar segredos, .env, .venv, node_modules, caches ou bancos locais.
- Use variáveis de ambiente para configuração sensível.

## Scoring e Recomendações
- Todo score deve expor: features usadas, pesos, confidence e uncertainty.
- Toda recomendação NVIDIA deve conter: evidência, suporte RAG, confidence score, business impact, implementation complexity e next best action.

## Modularidade
- Todo módulo implementado deve ser usado, removido ou marcado como experimental.
- Módulos sem uso claro devem ser eliminados.

## Decisões
- Separe fato, inferência e hipótese em todo output.
- Prefira scores numéricos a conceitos qualitativos.
