import { useEffect, useState } from "react";
import type { OpportunityListItem } from "../api/types";
import { listOpportunities } from "../api/product";

interface OpportunitiesViewProps {
  onSelectRun: (runId: string) => void;
  onSelectStartup: (startupId: string) => void;
}

export function OpportunitiesView({ onSelectRun, onSelectStartup }: OpportunitiesViewProps) {
  const [opps, setOpps] = useState<OpportunityListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 50;

  async function load(pageOffset = 0) {
    setLoading(true);
    setError(null);
    try {
      const resp = await listOpportunities(pageOffset, limit);
      setOpps(resp.items);
      setTotal(resp.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(offset); }, [offset]);

  if (loading) return <div className="panel"><div className="panel-body"><p className="loading-text">Loading opportunities...</p></div></div>;

  return (
    <div className="opportunities-page">
      <div className="panel">
        <div className="panel-header">
          <h2>Opportunities</h2>
          <div className="panel-header-actions">
            <span className="muted">{total} total</span>
            <button type="button" className="secondary-button" onClick={() => load(offset)}>Refresh</button>
          </div>
        </div>
        <div className="panel-body">
          {error && <div className="message error-message">{error}</div>}

          {!error && opps.length === 0 && (
            <p className="empty-state">No opportunities yet. Run analyses to generate them.</p>
          )}

          {opps.length > 0 && (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Startup</th>
                  <th>Composite Score</th>
                  <th>Motion</th>
                  <th>Activation Playbook</th>
                  <th>Evidence Coverage</th>
                  <th>Unsupported Claims</th>
                  <th>Export Ready</th>
                  <th>Review Ready</th>
                  <th>Dossier</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {opps.map((o) => (
                  <tr key={o.startup_id}>
                    <td>
                      <button
                        type="button"
                        className="link-button"
                        onClick={() => onSelectStartup(o.startup_id)}
                      >
                        {o.startup_name}
                      </button>
                    </td>
                    <td><strong>{o.composite_score?.toFixed(1) ?? "—"}</strong></td>
                    <td><span className="badge">{o.recommended_motion ?? "—"}</span></td>
                    <td>
                      {o.top_activation_playbook ? (
                        <span title={`Confidence: ${o.activation_confidence ?? "—"}`}>
                          {o.top_activation_playbook}
                        </span>
                      ) : <span className="muted">—</span>}
                    </td>
                    <td>{o.evidence_coverage != null ? `${Math.round(o.evidence_coverage * 100)}%` : "—"}</td>
                    <td>{o.unsupported_claim_count ?? "—"}</td>
                    <td>
                      <span className={`badge ${o.export_readiness_score != null && o.export_readiness_score >= 0.7 ? "cap-ok" : "cap-warn"}`}>
                        {o.export_readiness_score != null ? o.export_readiness_score.toFixed(2) : "—"}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${o.review_readiness_score != null && o.review_readiness_score >= 0.7 ? "cap-ok" : "cap-warn"}`}>
                        {o.review_readiness_score != null ? o.review_readiness_score.toFixed(2) : "—"}
                      </span>
                    </td>
                    <td>{o.dossier_available ? <span className="badge cap-ok">Yes</span> : <span className="muted">No</span>}</td>
                    <td>
                      {o.latest_analysis_run_id && (
                        <button
                          type="button"
                          className="link-button"
                          onClick={() => onSelectRun(o.latest_analysis_run_id!)}
                        >
                          View Run
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {total > limit && (
            <div className="pagination-row">
              <button
                type="button"
                className="secondary-button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
              >
                Previous
              </button>
              <span className="muted">Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}</span>
              <button
                type="button"
                className="secondary-button"
                disabled={offset + limit >= total}
                onClick={() => setOffset(offset + limit)}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
