# Structured Output Contract

## Propósito

Define o contrato da camada de parsing, validação, reparo e rastreio de
outputs estruturados (`src/evaluation/structured_outputs.py`).

## Schemas

### StructuredOutputResult

```
status: "valid" | "invalid" | "failed"
parsed_output: Any | None
raw_output: str | None
output_type: str          # ex: "dossier", "llm_judge_score"
schema_name: str          # ex: "DossierJsonSchema"
validation_errors: list[ValidationErrorDetail]
retry_count: int
repaired: bool
latency_ms: float
provider: str | None
model_name: str | None
metadata_json: dict
```

### ValidationErrorDetail

```
field: str
message: str
value: Any
```

## Funções Públicas

### `parse_json_output(raw_text: str | None) -> StructuredOutputResult`
Parsing JSON sem schema validation. Status = "failed" se input for None.

### `validate_output(schema, raw_or_obj, ...) -> StructuredOutputResult`
Valida str/dict/BaseModel contra schema Pydantic. Retorna validation_errors
detalhados em caso de falha.

### `repair_json_if_safe(raw_text: str | None) -> dict | None`
Tenta reparos seguros: unescape, trailing commas, single quotes, unquoted keys.
Retorna None se não houver reparo ou se for irreparável.

### `run_validation_with_repair(schema, raw_text, ...) -> StructuredOutputResult`
Valida → repara → re-valida → retry. Para input pré-parado (dict/BaseModel),
não tenta reparo/retry.

### `build_structured_output_result(...) -> StructuredOutputResult`
Factory method para criar StructuredOutputResult com campos opcionais.

### `readiness_check_payload_from_result(result, analysis_run_id) -> dict | None`
Converte StructuredOutputResult em payload para ProductReadinessCheck.
Retorna None se status == "valid".

### `quality_metrics_from_results(results) -> dict`
Agrega métricas de qualidade: valid_rate, repair_rate, failure_rate,
avg_retry_count, has_degradation, etc.

## Estados de Degradação (degraded.py)

| Código | Severidade | Dispara quando |
|---|---|---|
| STRUCTURED_OUTPUT_INVALID | error | schema validation falha |
| STRUCTURED_OUTPUT_REPAIRED | warning | reparo foi aplicado com sucesso |
| STRUCTURED_OUTPUT_RETRY_EXHAUSTED | error | max_retries atingido sem sucesso |
| STRUCTURED_OUTPUT_SCHEMA_DRIFT | warning | campo inesperado detectado |
| STRUCTURED_OUTPUT_MISSING_REQUIRED_FIELD | error | campo obrigatório ausente |

## Métricas de Qualidade (quality/constants.py)

| Métrica | Tipo | Threshold |
|---|---|---|
| structured_output_valid_rate | float [0,1] | >= 0.95 |
| structured_output_repair_rate | float [0,1] | <= 0.10 |
| structured_output_failure_rate | float [0,1] | <= 0.05 |
| avg_retry_count | float | <= 1.0 |
| schema_validation_error_count | int | 0 |
| missing_required_field_count | int | 0 |

## Invariantes

1. Nenhuma exceção escapa das funções públicas (são tratadas internamente,
   transformadas em status "invalid" ou "failed").
2. `parsed_output` só é preenchido se status == "valid".
3. `validation_errors` nunca é None; lista vazia se não houver erros.
4. Input pré-parado (dict/BaseModel) nunca passa por repair_json_if_safe.
5. `readiness_check_payload_from_result` retorna None se status == "valid".
6. Para input str inválido, `validate_output` sempre tenta JSON.parse antes
   de declarar falha.

## Exemplos de Uso

```python
from pydantic import BaseModel
from src.evaluation.structured_outputs import run_validation_with_repair

class MySchema(BaseModel):
    name: str = ""
    score: float = 0.0

result = run_validation_with_repair(MySchema, '{"name": "x", "score": 0.5}')
assert result.status == "valid"
```

## Integração Mínima

Para integrar em um novo componente:

1. Definir (ou reutilizar) schema Pydantic para o output
2. Chamar `run_validation_with_repair()` com o output bruto
3. Se resultado for válido, usar `result.parsed_output`
4. Se inválido, chamar `readiness_check_payload_from_result()` para criar
   readiness check e logar warning
5. Agregar múltiplos resultados via `quality_metrics_from_results()`
