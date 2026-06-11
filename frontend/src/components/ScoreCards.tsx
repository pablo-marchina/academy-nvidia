import type { JsonObject } from "../api/client";

type ScoreCardsProps = {
  briefJson: JsonObject | null;
  runReport: JsonObject | null;
};

function valueOf(data: JsonObject | null, key: string): string {
  const value = data?.[key];
  if (value === undefined || value === null || value === "") {
    return "n/a";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }
  return String(value);
}

function nestedScore(data: JsonObject | null, key: string): string {
  const scoreObject = data?.[key];
  if (!scoreObject || typeof scoreObject !== "object" || Array.isArray(scoreObject)) {
    return "n/a";
  }
  const obj = scoreObject as JsonObject;
  const score = obj.score ?? obj.final_score ?? obj.total_score ?? obj.value;
  if (typeof score === "number") {
    return `${score.toFixed(1)}/100`;
  }
  return score ? String(score) : "n/a";
}

export function ScoreCards({ briefJson, runReport }: ScoreCardsProps) {
  return (
    <section className="score-grid" aria-label="Brief scores">
      <article className="score-card primary-score">
        <span>Priority score</span>
        <strong>{valueOf(briefJson, "final_priority_score")}/100</strong>
      </article>
      <article className="score-card">
        <span>Recommended motion</span>
        <strong>{valueOf(briefJson, "recommended_motion")}</strong>
      </article>
      <article className="score-card">
        <span>Verdict</span>
        <strong>{valueOf(briefJson, "verdict")}</strong>
      </article>
      <article className="score-card">
        <span>Confidence</span>
        <strong>{valueOf(briefJson, "confidence")}</strong>
      </article>
      <article className="score-card">
        <span>Defensibility</span>
        <strong>{nestedScore(briefJson, "defensibility_score")}</strong>
      </article>
      <article className="score-card">
        <span>Inception fit</span>
        <strong>{nestedScore(briefJson, "inception_fit_score")}</strong>
      </article>
      <article className="score-card">
        <span>Production readiness</span>
        <strong>{nestedScore(briefJson, "production_readiness_score")}</strong>
      </article>
      <article className="score-card">
        <span>Gaps detected</span>
        <strong>{valueOf((runReport?.pipeline_summary as JsonObject) || null, "gaps_detected")}</strong>
      </article>
    </section>
  );
}
