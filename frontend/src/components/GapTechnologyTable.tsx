import type { JsonObject } from "../api/client";

type GapTechnologyTableProps = {
  gaps: unknown;
  technologies: unknown;
  recommendations: unknown;
};

function asObjects(value: unknown): JsonObject[] {
  return Array.isArray(value)
    ? value.filter((item): item is JsonObject => !!item && typeof item === "object")
    : [];
}

function text(value: unknown, fallback = "n/a"): string {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }
  if (Array.isArray(value)) {
    return value.map((item) => text(item, "")).filter(Boolean).join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function gapName(gap: JsonObject): string {
  return text(gap.gap_type ?? gap.name ?? gap.id ?? gap.gap_name);
}

function technologiesForGap(gap: JsonObject, technologies: JsonObject[]): string {
  const name = gapName(gap);
  const matches = technologies.filter((tech) => {
    const gapField = text(tech.gap_type ?? tech.gap_name ?? tech.addresses_gap, "");
    return gapField === name || gapField.includes(name) || name.includes(gapField);
  });
  if (matches.length === 0) {
    return technologies
      .slice(0, 3)
      .map((tech) => text(tech.technology_name ?? tech.name ?? tech.product, "technology"))
      .join(", ");
  }
  return matches
    .map((tech) => text(tech.technology_name ?? tech.name ?? tech.product, "technology"))
    .join(", ");
}

function recommendationForGap(gap: JsonObject, recommendations: JsonObject[]): string {
  const name = gapName(gap);
  const match = recommendations.find((rec) => {
    const gapField = text(rec.gap_type ?? rec.gap_name ?? rec.gap, "");
    return gapField === name || gapField.includes(name) || name.includes(gapField);
  });
  return match
    ? text(match.action ?? match.recommended_action ?? match.priority ?? match.next_step)
    : "n/a";
}

export function GapTechnologyTable({
  gaps,
  technologies,
  recommendations,
}: GapTechnologyTableProps) {
  const gapRows = asObjects(gaps);
  const techRows = asObjects(technologies);
  const recommendationRows = asObjects(recommendations);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Gaps and NVIDIA mapping</p>
          <h2>Production AI gaps</h2>
        </div>
      </div>

      {gapRows.length === 0 ? (
        <p className="empty-state">No gaps returned in the brief.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Gap</th>
                <th>Confidence</th>
                <th>Evidence tag</th>
                <th>NVIDIA technologies</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {gapRows.map((gap, index) => (
                <tr key={`${gapName(gap)}-${index}`}>
                  <td>
                    <strong>{gapName(gap)}</strong>
                    <span>{text(gap.reasoning ?? gap.description, "")}</span>
                  </td>
                  <td>{text(gap.confidence)}</td>
                  <td>{text(gap.evidence_tag ?? gap.tag)}</td>
                  <td>{technologiesForGap(gap, techRows)}</td>
                  <td>{recommendationForGap(gap, recommendationRows)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
