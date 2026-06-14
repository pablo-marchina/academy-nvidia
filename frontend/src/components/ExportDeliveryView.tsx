import { useState } from "react";

interface ChecklistItem {
  id: string;
  label: string;
  done: boolean;
}

export function ExportDeliveryView() {
  const [checklist, setChecklist] = useState<ChecklistItem[]>([
    { id: "1", label: "Identify target startup for activation", done: false },
    { id: "2", label: "Complete analysis pipeline (all nodes finished)", done: false },
    { id: "3", label: "Review dossier evidence coverage (>= 70%)", done: false },
    { id: "4", label: "Verify activation playbook has recommended motion", done: false },
    { id: "5", label: "Check opportunity score for export readiness >= 0.7", done: false },
    { id: "6", label: "Generate Action Brief (POST /analysis-runs/{id}/brief)", done: false },
    { id: "7", label: "Generate Dossier (POST /analysis-runs/{id}/dossier)", done: false },
    { id: "8", label: "Compute Opportunity Score (POST /analysis-runs/{id}/opportunity-score)", done: false },
    { id: "9", label: "Create Export (POST /analysis-runs/{id}/exports)", done: false },
    { id: "10", label: "Download or copy the deliverable", done: false },
  ]);

  const allDone = checklist.every((c) => c.done);

  function toggleItem(id: string) {
    setChecklist((prev) =>
      prev.map((c) => (c.id === id ? { ...c, done: !c.done } : c)),
    );
  }

  function resetChecklist() {
    setChecklist((prev) => prev.map((c) => ({ ...c, done: false })));
  }

  const exportCommands = [
    { label: "Export Action Brief (JSON)", cmd: `curl -X POST "http://localhost:8000/analysis-runs/{RUN_ID}/exports" -H "Content-Type: application/json" -d '{"export_type": "json"}'` },
    { label: "Export Action Brief (Markdown)", cmd: `curl -X POST "http://localhost:8000/analysis-runs/{RUN_ID}/exports" -H "Content-Type: application/json" -d '{"export_type": "markdown"}'` },
    { label: "Download Export by ID", cmd: `curl "http://localhost:8000/exports/{EXPORT_ID}"` },
    { label: "Get Dossier Markdown", cmd: `curl "http://localhost:8000/analysis-runs/{RUN_ID}/dossier/markdown"` },
    { label: "Get Action Brief", cmd: `curl "http://localhost:8000/analysis-runs/{RUN_ID}/brief"` },
  ];

  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  async function copyCommand(cmd: string, idx: number) {
    try {
      await navigator.clipboard.writeText(cmd);
      setCopiedIdx(idx);
      setTimeout(() => setCopiedIdx(null), 2000);
    } catch {
      // clipboard not available
    }
  }

  return (
    <div className="export-delivery-page">
      <div className="panel">
        <div className="panel-header">
          <h2>Export Delivery Checklist</h2>
          <div className="panel-header-actions">
            <button type="button" className="secondary-button" onClick={resetChecklist}>
              Reset
            </button>
          </div>
        </div>
        <div className="panel-body">
          {allDone && (
            <div className="message info-message">
              All checklist items completed! The deliverable is ready for export.
            </div>
          )}

          <div className="checklist-section">
            {checklist.map((item) => (
              <div key={item.id} className="checklist-row">
                <label className="checklist-label">
                  <input
                    type="checkbox"
                    checked={item.done}
                    onChange={() => toggleItem(item.id)}
                  />
                  <span className={item.done ? "check-done" : ""}>{item.label}</span>
                </label>
              </div>
            ))}
          </div>

          <div className="progress-label">
            {checklist.filter((c) => c.done).length} / {checklist.length} items done
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header"><h2>Export Commands</h2></div>
        <div className="panel-body">
          <p className="hint-text">
            Replace <code>{`{RUN_ID}`}</code> and <code>{`{EXPORT_ID}`}</code> with actual values.
          </p>
          {exportCommands.map((ec, idx) => (
            <div key={idx} className="export-command-row">
              <div className="export-command-label">{ec.label}</div>
              <div className="export-command-cmd">
                <code>{ec.cmd}</code>
                <button
                  type="button"
                  className="badge-button"
                  onClick={() => copyCommand(ec.cmd, idx)}
                >
                  {copiedIdx === idx ? "Copied!" : "Copy"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel panel-warning">
        <div className="panel-header"><h2>Limitations & Notes</h2></div>
        <div className="panel-body">
          <ul className="stack-list warning-list">
            <li><strong>No PDF export</strong><span>Only JSON and Markdown export types are supported.</span></li>
            <li><strong>Export requires completed analysis</strong><span>The analysis run must be in "completed" or "degraded" status before export is available.</span></li>
            <li><strong>Dossier & Brief must be generated first</strong><span>POST endpoints for dossier and brief must be called before export creation.</span></li>
            <li><strong>Local storage only</strong><span>Exports are stored on the server filesystem. No cloud storage or sharing is implemented.</span></li>
            <li><strong>Language</strong><span>Output language depends on the analysis pipeline configuration. Currently defaults to Portuguese for Brazilian market focus.</span></li>
          </ul>
        </div>
      </div>
    </div>
  );
}