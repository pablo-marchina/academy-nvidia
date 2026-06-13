# Product Capability & Configuration Registry

## Objetivo

Criar uma camada central que permite ao usuário e ao produto saber:

- Quais funcionalidades existem?
- Quais estão habilitadas?
- Quais exigem configuração?
- Quais variáveis de ambiente estão faltando?
- Quais dependências opcionais estão instaladas?
- O produto está pronto para ser usado?

## Arquitetura

```
src/services/product/
  capability_registry.py   — Definições de 25+ capabilities
  config_registry.py       — Definições de 17+ configurações (env vars, extras)
  readiness_service.py     — Agrega status e produz relatório de readiness

src/api/
  product_schemas.py       — Schemas Pydantic para API
  product_routes.py        — 4 endpoints: /product/capabilities, /product/configuration,
                             /product/setup-checklist, /product/readiness
```

## Capabilities

Cada capability possui:

| Campo | Descrição |
|---|---|
| capability_id | Identificador único |
| name | Nome legível |
| description | Descrição funcional |
| category | core, database, rag, evidence, claims, playbooks, dossier, quality, structured_outputs, llm_judge, export, frontend, developer_tools |
| required | True = produto não funciona sem ela |
| enabled_by_default | True = ativa sem configuração adicional |
| status | available, unavailable, not_configured, missing_dependency, degraded, disabled, experimental |
| required_env_vars | Variáveis obrigatórias para a capability |
| optional_env_vars | Variáveis opcionais |
| required_extras | Extras pip necessários (ex: llm-judge) |
| required_services | Serviços externos (ex: Qdrant server) |
| setup_instructions | Instruções de setup |
| failure_mode | Comportamento quando não configurada |
| user_visible | Se aparece em listagens públicas |
| documentation_ref | Link para documentação |

## Configurações

Cada item de configuração possui:

| Campo | Descrição |
|---|---|
| key | Nome da env var |
| description | Descrição funcional |
| required | Obrigatória para o core |
| required_for | Lista de capability_ids que dependem dela |
| secret | Se true, valor é mascarado (****) |
| default | Valor padrão |
| current_value | Valor atual (resolvido do environment) |
| is_set | True se configurada |

## Status Resolution

O status de cada capability é computado na hora:

1. Se `enabled_by_default=False` e não `required` → `disabled` (a menos que tenha env_vars ou extras)
2. Se `required_extras` não instalado → `missing_dependency`
3. Se `required_env_vars` não configurado → `not_configured`
4. Se passou em tudo → `available`

## Readiness Report

O relatório readiness contém:

- `ready`: bool — true se nenhuma config obrigatória está faltando
- `blocking_missing_config`: capabilities required com status != available
- `optional_missing_config`: capabilities opcionais com status != available
- `unavailable_capabilities`: capabilities unavailable/missing_dependency
- `degraded_capabilities`: capabilities degraded
- `setup_checklist`: lista de itens de configuração com status
- `user_messages`: mensagens legíveis para o usuário

## Endpoints

| Método | Path | Descrição |
|---|---|---|
| GET | /product/capabilities | Lista todas as capabilities com status |
| GET | /product/configuration | Lista todas as configurações com valores |
| GET | /product/setup-checklist | Checklist de setup com progresso |
| GET | /product/readiness | Relatório completo de readiness |

## Comportamento

- Required config ausente → `ready=false` com blocking_missing_config populado
- Extra opcional ausente (instructor) → capability `missing_dependency`, produto principal continua funcionando
- Feature opcional desabilitada → não bloqueia readiness
- Secrets são mascarados (****) na API
- Nenhuma importação de dependência opcional no fluxo padrão
