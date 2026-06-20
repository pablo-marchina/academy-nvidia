import type { JsonObject } from "../api/client";

type EvaluationResponse = {
  status?: string;
  metrics?: JsonObject;
  failure_reasons?: unknown[];
  warnings?: unknown[];
};

type EvalStatusPanelProps = {
  evalResult: EvaluationResponse | JsonObject | null;
  isEvaluating: boolean;
  evalError: string | null;
  canEvaluate: boolean;
  onEvaluate: () => void;
};

function statusFromEval(evalResult: EvaluationResponse | JsonObject | null): string {
  if (!evalResult) {
    return "not run";
  }
  const status = "status" in evalResult ? evalResult.status : undefined;
  if (status) {
    return String(status);
  }
  const metrics =
    "metrics" in evalResult && evalResult.metrics && typeof evalResult.metrics === "object"
      ? (evalResult.metrics as JsonObject)
      : null;
  return metrics?.answer_quality_status ? String(metrics.answer_quality_status) : "available";
}

function failureReasons(evalResult: EvaluationResponse | JsonObject | null): string[] {
  if (!evalResult || !("failure_reasons" in evalResult)) {
    return [];
  }
  return Array.isArray(evalResult.failure_reasons)
    ? evalResult.failure_reasons.map((item) => String(item))
    : [];
}

function warnings(evalResult: EvaluationResponse | JsonObject | null): string[] {
  if (!evalResult || !("warnings" in evalResult)) {
    return [];
  }
  return Array.isArray(evalResult.warnings) ? evalResult.warnings.map((item) => String(item)) : [];
}

export function EvalStatusPanel({
  evalResult,
  isEvaluating,
  evalError,
  canEvaluate,
  onEvaluate,
}: EvalStatusPanelProps) {
  const status = statusFromEval(evalResult);
  const failures = failureReasons(evalResult);
  const evalWarnings = warnings(evalResult);

  return (
    <section className="panel eval-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Answer quality</p>
          <h2>Evaluation</h2>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onEvaluate}
          disabled={!canEvaluate || isEvaluating}
        >
          {isEvaluating ? "Evaluating..." : "Evaluate brief"}
        </button>
      </div>

      <div className={`status-chip ${status === "PASS" ? "ok" : status === "FAIL" ? "bad" : "warn"}`}>
        {status}
      </div>

      {evalError ? <div className="message error-message">{evalError}</div> : null}

      {failures.length > 0 ? (
        <>
          <h3>Failure reasons</h3>
          <ul className="stack-list warning-list">
            {failures.map((failure, index) => (
              <li key={`${failure}-${index}`}>{failure}</li>
            ))}
          </ul>
        </>
      ) : null}

      {evalWarnings.length > 0 ? (
        <>
          <h3>Warnings</h3>
          <ul className="stack-list">
            {evalWarnings.map((warning, index) => (
              <li key={`${warning}-${index}`}>{warning}</li>
            ))}
          </ul>
        </>
      ) : null}

      {evalResult ? (
        <details className="json-details">
          <summary>Evaluation JSON</summary>
          <pre>{JSON.stringify(evalResult, null, 2)}</pre>
        </details>
      ) : null}
    </section>
  );
}
