import { useEffect, useState } from "react";
import type { OpportunityScoreRead, OpportunityScoreCreateResponse } from "../api/types";
import { getOpportunityScore, computeOpportunityScore } from "../api/product";

interface OpportunityDetailPanelProps {
  analysisRunId: string;
  onBack: () => void;
}

export function OpportunityDetailPanel({ analysisRunId, onBack }: OpportunityDetailPanelProps) {
  const [score, setScore] = useState<OpportunityScoreRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [computing, setComputing] = useState(false);
  const [computeResult, setComputeResult] = useState<OpportunityScoreCreateResponse | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const s = await getOpportunityScore(analysisRunId);
      setScore(s);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [analysisRunId]);

  async function handleCompute() {
    setComputing(true);
    setError(null);
    try {
      const result = await computeOpportunityScore(analysisRunId);
      setComputeResult(result);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setComputing(false);
    }
  }

  if (loading) return <div className="panel"><div className="panel-body"><p className="loading-text">Loading opportunity score...</p></div></div>;

  const displayScore = score;

  return (
    <div className="opportunity-detail-page">
      <div className="panel">
        <div className="panel-header">
          <div className="panel-header-left">
            <button type="button" className="back-button" onClick={onBack}>← Back</button>
            <h2>Opportunity Score Detail</h2>
          </div>
          <div className="panel-header-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={handleCompute}
              disabled={computing}
            >
              {computing ? "Computing..." : "Compute Score"}
            </button>
          </div>
        </div>

        <div className="panel-body">
          {error && <div className="message error-message">{error}</div>}

          {computeResult && (
            <div className="message info-message">
              Score computed: {computeResult.opportunity_score?.toFixed(4)} ({computeResult.score_tier})
            </div>
          )}

          {displayScore ? (
            <>
              <table className="data-table">
                <tbody>
                  <tr>
                    <td className="label-cell">Score</td>
                    <td>
                      <strong className="score-value" style={{ fontSize: 28 }}>
                        {displayScore.opportunity_score?.toFixed(4) ?? "—"}
                      </strong>
                      <span className={`badge ${displayScore.score_tier === "high" ? "cap-ok" : displayScore.score_tier === "medium" ? "cap-warn" : "cap-bad"}`}>
                        {displayScore.score_tier}
                      </span>
                    </td>
                  </tr>
                  <tr><td className="label-cell">Version</td><td>{displayScore.score_version}</td></tr>
                  <tr><td className="label-cell">Recommended Action</td><td>{displayScore.recommended_action || <span className="muted">—</span>}</td></tr>
                  <tr><td className="label-cell">Penalty Total</td><td>{displayScore.penalty_total?.toFixed(4) ?? "0"}</td></tr>
                </tbody>
              </table>

              <h3>Reasoning</h3>
              <pre className="markdown-block">{displayScore.reasoning || "No reasoning available."}</pre>

              {displayScore.penalties?.length > 0 && (
                <>
                  <h3>Penalties</h3>
                  <table className="data-table">
                    <thead>
                      <tr><th>Type</th><th>Value</th><th>Detail</th></tr>
                    </thead>
                    <tbody>
                      {displayScore.penalties.map((p, i) => (
                        <tr key={i}>
                          <td>{String(p.type)}</td>
                          <td className="text-warn">{String(p.value)}</td>
                          <td>{String(p.detail)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}

              {displayScore.evidence_refs?.length > 0 && (
                <>
                  <h3>Evidence References ({displayScore.evidence_refs.length})</h3>
                  <pre className="json-block">{JSON.stringify(displayScore.evidence_refs, null, 2)}</pre>
                </>
              )}

              <h3>Raw Components</h3>
              <pre className="json-block">{JSON.stringify(displayScore.components, null, 2)}</pre>
            </>
          ) : (
            <div className="empty-state">
              No opportunity score found. Click "Compute Score" to generate one.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}