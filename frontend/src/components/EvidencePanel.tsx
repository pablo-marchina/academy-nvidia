import type { JsonObject } from "../api/client";

type EvidencePanelProps = {
  evidence: unknown;
  missingEvidence: unknown;
  uncertainties: unknown;
  warnings: string[];
};

function asObjects(value: unknown): JsonObject[] {
  return Array.isArray(value)
    ? value.filter((item): item is JsonObject => !!item && typeof item === "object")
    : [];
}

function asStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : [];
}

function text(value: unknown, fallback = "n/a"): string {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }
  return String(value);
}

export function EvidencePanel({
  evidence,
  missingEvidence,
  uncertainties,
  warnings,
}: EvidencePanelProps) {
  const evidenceRows = asObjects(evidence);
  const missingRows = asStrings(missingEvidence);
  const uncertaintyRows = asObjects(uncertainties);

  return (
    <section className="panel evidence-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Traceability</p>
          <h2>Evidence, warnings, uncertainties</h2>
        </div>
      </div>

      <div className="evidence-columns">
        <div>
          <h3>Evidence used</h3>
          {evidenceRows.length === 0 ? (
            <p className="empty-state">No evidence returned.</p>
          ) : (
            <ul className="stack-list">
              {evidenceRows.map((item, index) => (
                <li key={`${text(item.claim)}-${index}`}>
                  <strong>{text(item.claim)}</strong>
                  <span>
                    {text(item.tag)} | {text(item.confidence)} | {text(item.source_type)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3>Warnings</h3>
          {warnings.length === 0 ? (
            <p className="empty-state">No API warnings.</p>
          ) : (
            <ul className="stack-list warning-list">
              {warnings.map((warning, index) => (
                <li key={`${warning}-${index}`}>{warning}</li>
              ))}
            </ul>
          )}

          <h3>Missing evidence</h3>
          {missingRows.length === 0 ? (
            <p className="empty-state">No missing evidence returned.</p>
          ) : (
            <ul className="stack-list">
              {missingRows.map((item, index) => (
                <li key={`${item}-${index}`}>{item}</li>
              ))}
            </ul>
          )}

          <h3>Uncertainties</h3>
          {uncertaintyRows.length === 0 ? (
            <p className="empty-state">No uncertainties returned.</p>
          ) : (
            <ul className="stack-list">
              {uncertaintyRows.map((item, index) => (
                <li key={`${text(item.description)}-${index}`}>
                  <strong>{text(item.description)}</strong>
                  <span>{text(item.impact, "")}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
