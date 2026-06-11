import type {
  ArtifactListResponse,
  HealthResponse,
  RagStatusResponse,
} from "../api/client";

type RagStatusBadgeProps = {
  health: HealthResponse | null;
  ragStatus: RagStatusResponse | null;
  artifacts: ArtifactListResponse | null;
  healthError: string | null;
  ragError: string | null;
  onRefresh: () => void;
};

export function RagStatusBadge({
  health,
  ragStatus,
  artifacts,
  healthError,
  ragError,
  onRefresh,
}: RagStatusBadgeProps) {
  const apiOk = health?.status === "ok";
  const qdrantAvailable = ragStatus?.qdrant_available === true;

  return (
    <section className="panel status-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Runtime</p>
          <h2>API and RAG status</h2>
        </div>
        <button type="button" className="secondary-button" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      <div className="status-grid">
        <div className={`status-chip ${apiOk ? "ok" : "bad"}`}>
          API {apiOk ? "online" : "offline"}
        </div>
        <div className={`status-chip ${qdrantAvailable ? "ok" : "warn"}`}>
          Qdrant {qdrantAvailable ? "available" : "offline"}
        </div>
      </div>

      <dl className="compact-list">
        <div>
          <dt>Backend</dt>
          <dd>{ragStatus?.backend || "unknown"}</dd>
        </div>
        <div>
          <dt>Collection</dt>
          <dd>{ragStatus?.collection_name || "unknown"}</dd>
        </div>
        <div>
          <dt>Vector size</dt>
          <dd>{ragStatus?.vector_size || "unknown"}</dd>
        </div>
        <div>
          <dt>Artifacts</dt>
          <dd>{artifacts ? artifacts.total : "unknown"}</dd>
        </div>
      </dl>

      {healthError ? <div className="message error-message">{healthError}</div> : null}
      {ragError ? <div className="message warning-message">{ragError}</div> : null}
      {ragStatus?.error ? (
        <div className="message warning-message">Qdrant warning: {ragStatus.error}</div>
      ) : null}
    </section>
  );
}
