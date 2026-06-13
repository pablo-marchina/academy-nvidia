# Structured Output Reliability Layer

## Objetivo

Criar uma camada comum de parsing, validação, reparo e rastreio de outputs
estruturados, reutilizável por qualquer componente que produza JSON com
schema Pydantic.

## Inventário de Outputs Estruturados

| Componente | Formato | Tem LLM? | Schema Pydantic? | Risco |
|---|---|---|---|---|
| StartupActionBrief | dict | não | StartupActionBrief (briefing/schemas.py) | baixo |
| ActivationDossier | dict | não | nenhum (antes deste épico) | médio |
| LLMJudgeScore | dict | não* | LLMJudgeScore | médio |
| PipelineResult | dict | não | PipelineResult | baixo |
| RagEvalResult | dict | não | RagEvalResult | baixo |
| Dashboard | dict | não | DashboardMetrics | baixo |

*\* LLMJudgeScore é produzido por provider determinístico; provider real usaria LLM no futuro.*

## Arquitetura

```
src/evaluation/structured_outputs.py
  ├── parse_json_output()          # raw str → dict | None
  ├── repair_json_if_safe()        # str → dict | None (reparo leve)
  ├── validate_output()            # str|dict|BaseModel → StructuredOutputResult
  ├── run_validation_with_repair() # valida + repara + retry
  ├── build_structured_output_result()
  ├── readiness_check_payload_from_result()
  └── quality_metrics_from_results()
```

## Estados de Degradação

Novos códigos em `src/services/product/degraded.py`:

- `STRUCTURED_OUTPUT_INVALID` — schema inválido
- `STRUCTURED_OUTPUT_REPAIRED` — reparo aplicado com sucesso
- `STRUCTURED_OUTPUT_RETRY_EXHAUSTED` — retries esgotados
- `STRUCTURED_OUTPUT_SCHEMA_DRIFT` — campo desconhecido
- `STRUCTURED_OUTPUT_MISSING_REQUIRED_FIELD` — campo obrigatório ausente

## Métricas de Qualidade

Novas métricas em `src/quality/constants.py`:

- `structured_output_valid_rate`
- `structured_output_repair_rate`
- `structured_output_failure_rate`
- `avg_retry_count`
- `schema_validation_error_count`
- `missing_required_field_count`

## Integração com Componentes Reais

### Activation Dossier (primeiro componente integrado)

1. `DossierJsonSchema` Pydantic model adicionado em `dossier_service.py`
2. `run_validation_with_repair()` chamado após `_build_dossier_json()`
3. Se falhar: log warning + cria `ProductReadinessCheck` via `readiness_check_payload_from_result()`

### LLM Judge (futuro)

- `InstructorTrialAdapter` em `evaluation/llm_judge_instructor_adapter.py`
- Opcional: `pip install -e ".[llm-judge]"`
- Lazy import de `instructor`

## Política de Retry

- `run_validation_with_repair()` aceita `max_retries` (default 1)
- Reparo via `repair_json_if_safe()` (trailing commas, single quotes, unquoted keys)
- Se todas as tentativas falharem, status = `"failed"`
- Para input pré-parado (dict/BaseModel), não há retry

## Schemas de Saída

### StructuredOutputResult

```python
@dataclass
class StructuredOutputResult:
    status: Literal["valid", "invalid", "failed"]
    parsed_output: Any
    raw_output: str | None
    output_type: str
    schema_name: str
    validation_errors: list[ValidationErrorDetail]
    retry_count: int
    repaired: bool
    latency_ms: float
    provider: str | None
    model_name: str | None
    metadata_json: dict
```

### ValidationErrorDetail

```python
class ValidationErrorDetail(TypedDict):
    field: str
    message: str
    value: Any
```
