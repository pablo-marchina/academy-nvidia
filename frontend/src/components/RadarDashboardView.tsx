import { useEffect, useMemo, useState } from "react";
import type { RadarDashboardItem, RadarPopulateResponse, JsonValue } from "../api/types";
import { getRadarDashboard, populateRadarDashboard } from "../api/product";

interface RadarDashboardViewProps {
  onSelectStartup: (startupId: string) => void;
  onSelectRun: (runId: string) => void;
}

function formatScore(value: number | null | undefined): string {
  return typeof value === "number" ? value.toFixed(1) : "—";
}

function formatCoverage(value: number | null | undefined): string {
  return typeof value === "number" ? `${Math.round(value * 100)}%` : "—";
}

function shortList(values: string[], _limit = 4): string {
  if (!values.length) return "—";
  return values.join(", ");
}

function asRecord(value: JsonValue | undefined): Record<string, JsonValue> {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value;
  }
  return {};
}

function describeInformation(item: RadarDashboardItem): string {
  const info = item.information;
  const description = info.description;
  const productSummary = info.product_summary;
  if (typeof description === "string" && description.trim()) return description;
  if (typeof productSummary === "string" && productSummary.trim()) return productSummary;
  const scores = asRecord(info.scores);
  const scoreKeys = Object.keys(scores);
  if (scoreKeys.length > 0) return `Scores: ${scoreKeys.join(", ")}`;
  return "Runtime artifacts available in details.";
}

function countFailures(response: RadarPopulateResponse | null): number {
  if (!response) return 0;
  return (
    response.discovery_results.filter((item) => item.status === "failed" || item.status === "degraded").length +
    response.promoted_candidates.filter((item) => item.status === "failed" || item.status === "degraded").length +
    response.pipeline_results.filter((item) => item.status === "failed").length
  );
}

export function RadarDashboardView({ onSelectStartup, onSelectRun }: RadarDashboardViewProps) {
  const [items, setItems] = useState<RadarDashboardItem[]>([]);
  const [total, setTotal] = useState(0);
  const [analyzedTotal, setAnalyzedTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [populating, setPopulating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [populateResult, setPopulateResult] = useState<RadarPopulateResponse | null>(null);
  const [runPipeline, setRunPipeline] = useState(true);
  const [forceRerun, setForceRerun] = useState(false);
  const limit = 100;
  const [activeTab, setActiveTab] = useState<"ready" | "discovery" | "blockers" | "rejected">("ready");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const response = await getRadarDashboard(limit);
      setItems(response.items);
      setTotal(response.total);
      setAnalyzedTotal(response.analyzed_total);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function populate() {
    setPopulating(true);
    setError(null);
    try {
      const response = await populateRadarDashboard(limit, 8, runPipeline, forceRerun);
      setPopulateResult(response);
      setItems(response.dashboard.items);
      setTotal(response.dashboard.total);
      setAnalyzedTotal(response.dashboard.analyzed_total);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setPopulating(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const analyzedCount = useMemo(
    () => items.filter((item) => item.row_type === "analyzed_startup").length,
    [items],
  );
  const recommendationReadyCount = useMemo(
    () => items.filter((item) => item.recommendation_status === "ready").length,
    [items],
  );
  const failureCount = countFailures(populateResult);
  const discoveryQueueCount = populateResult?.discovery_queue?.length ?? 0;
  const rejectedCount = populateResult?.rejected_entities?.length ?? 0;

  if (loading) {
    return <div className="panel"><div className="panel-body"><p className="loading-text">Loading unified radar dashboard...</p></div></div>;
  }

  return (
    <div className="radar-dashboard-page">
      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Unified runtime pipeline</p>
            <h2>Radar Dashboard</h2>
          </div>
          <div className="panel-header-actions">
            <label className="toggle-row">
              <input
                type="checkbox"
                checked={runPipeline}
                onChange={(event) => setRunPipeline(event.target.checked)}
              />
              Run full analysis
            </label>
            <label className="toggle-row">
              <input
                type="checkbox"
                checked={forceRerun}
                onChange={(event) => setForceRerun(event.target.checked)}
              />
              Force rerun
            </label>
            <button type="button" className="secondary-button" onClick={load} disabled={populating}>Refresh</button>
            <button type="button" className="primary-button-sm" onClick={populate} disabled={populating}>
              {populating ? "Populating..." : "Populate Dashboard"}
            </button>
          </div>
        </div>

        <div className="score-grid panel-body">
          <div className="score-card primary-score">
            <span>Companies displayed</span>
            <strong>{total}</strong>
          </div>
          <div className="score-card">
            <span>Analyzed companies</span>
            <strong>{analyzedCount}/{analyzedTotal}</strong>
          </div>
          <div className="score-card">
            <span>Ready recommendations</span>
            <strong>{recommendationReadyCount}</strong>
          </div>
          <div className="score-card">
            <span>Runtime blockers</span>
            <strong>{failureCount}</strong>
          </div>
        </div>

        <div className="tab-row panel-body compact-tabs">
          <button type="button" className={activeTab === "ready" ? "active" : ""} onClick={() => setActiveTab("ready")}>Ready recommendations ({items.length})</button>
          <button type="button" className={activeTab === "discovery" ? "active" : ""} onClick={() => setActiveTab("discovery")}>Discovery queue ({discoveryQueueCount})</button>
          <button type="button" className={activeTab === "blockers" ? "active" : ""} onClick={() => setActiveTab("blockers")}>Runtime blockers ({failureCount})</button>
          <button type="button" className={activeTab === "rejected" ? "active" : ""} onClick={() => setActiveTab("rejected")}>Rejected entities ({rejectedCount})</button>
        </div>

        {error && <div className="message error-message">{error}</div>}

        {activeTab === "blockers" && populateResult && failureCount > 0 && (
          <details className="json-details">
            <summary>Runtime blockers returned by the central pipeline</summary>
            <pre>{JSON.stringify({
              discovery_results: populateResult.discovery_results,
              promoted_candidates: populateResult.promoted_candidates,
              pipeline_results: populateResult.pipeline_results,
            }, null, 2)}</pre>
          </details>
        )}

        {activeTab === "blockers" && populateResult && failureCount === 0 && (
          <p className="empty-state">No runtime blockers were returned by the latest central pipeline run.</p>
        )}

        {activeTab === "discovery" && (
          <details className="json-details" open>
            <summary>Valid candidates not yet promoted/analyzed</summary>
            <pre>{JSON.stringify(populateResult?.discovery_queue ?? [], null, 2)}</pre>
          </details>
        )}

        {activeTab === "rejected" && (
          <details className="json-details" open>
            <summary>Entities rejected by the quantitative company gate</summary>
            <pre>{JSON.stringify(populateResult?.rejected_entities ?? [], null, 2)}</pre>
          </details>
        )}

        {!error && activeTab === "ready" && items.length === 0 && (
          <p className="empty-state">
            No companies are available yet. Use Populate Dashboard to run configured discovery sources, promotion, analysis, recommendations, scoring, and dossier generation from one central runtime path.
          </p>
        )}

        {activeTab === "ready" && items.length > 0 && (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Pipeline status</th>
                  <th>Score</th>
                  <th>Evidence</th>
                  <th>NVIDIA fit</th>
                  <th>Recommendations</th>
                  <th>Information collected</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={`${item.row_type}-${item.startup_id ?? item.candidate_id ?? item.company_name}`}>
                    <td>
                      <strong>{item.company_name}</strong>
                      <span>{item.sector || "Unknown sector"}</span>
                      {item.website && <span className="url-cell">{item.website}</span>}
                    </td>
                    <td>
                      <span className={`badge status-${item.analysis_status ?? "unknown"}`}>
                        {item.analysis_status ?? item.row_type}
                      </span>
                      <span>{item.recommendation_status ?? "—"}</span>
                    </td>
                    <td>
                      <strong>{formatScore(item.opportunity_score)}</strong>
                      <span>{item.confidence ?? item.score_tier ?? "—"}</span>
                    </td>
                    <td>
                      <strong>{formatCoverage(item.evidence_coverage)}</strong>
                      <span>{item.source_count} sources</span>
                      <span>{item.unsupported_claim_count ?? "—"} unsupported claims</span>
                    </td>
                    <td>
                      <strong>{shortList(item.top_nvidia_technologies)}</strong>
                      <span>{shortList(item.top_gaps, 3)}</span>
                    </td>
                    <td>
                      {item.activation_recommendations.length > 0 ? (
                        <ul className="stack-list compact-stack-list">
                          {item.activation_recommendations.map((rec) => (
                            <li key={`${item.company_name}-${rec.playbook_name ?? rec.recommended_motion ?? rec.priority}`}>
                              <strong>{rec.playbook_name ?? rec.recommended_motion ?? "Recommendation"}</strong>
                              <span>{shortList(rec.nvidia_technologies, 3)}</span>
                              {rec.next_step && <span>{rec.next_step}</span>}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <span className="muted">Not generated yet</span>
                      )}
                    </td>
                    <td>
                      <span>{describeInformation(item)}</span>
                    </td>
                    <td>
                      {item.startup_id && (
                        <button type="button" className="link-button" onClick={() => onSelectStartup(item.startup_id!)}>
                          Startup
                        </button>
                      )}
                      {item.analysis_run_id && (
                        <button type="button" className="link-button" onClick={() => onSelectRun(item.analysis_run_id!)}>
                          Run
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
