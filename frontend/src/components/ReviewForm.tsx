import { useEffect, useState } from "react";
import type { ReviewDecisionRead } from "../api/types";
import { createReview, listReviews } from "../api/product";

interface ReviewFormProps {
  analysisRunId: string;
}

const DECISIONS = [
  "approve", "reject", "needs_more_evidence",
  "monitor", "contact", "not_recommended",
];

export function ReviewForm({ analysisRunId }: ReviewFormProps) {
  const [reviews, setReviews] = useState<ReviewDecisionRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [decision, setDecision] = useState(DECISIONS[0]);
  const [reviewer, setReviewer] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function load() {
    setLoading(true);
    try {
      setReviews(await listReviews(analysisRunId));
    } catch {
      setReviews([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [analysisRunId]);

  async function handleSubmit() {
    if (!reviewer.trim()) {
      setError("Reviewer name is required.");
      return;
    }
    setSubmitting(true);
    setError(null);
    setSuccess(false);
    try {
      await createReview(analysisRunId, decision, reviewer.trim(), notes.trim());
      setSuccess(true);
      setNotes("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel-header"><h2>Review</h2></div>
      <div className="panel-body">
        <div className="form-inline">
          <div className="form-field">
            <label>Decision</label>
            <select value={decision} onChange={(e) => setDecision(e.target.value)}>
              {DECISIONS.map((d) => <option key={d} value={d}>{d.replace(/_/g, " ")}</option>)}
            </select>
          </div>
          <div className="form-field">
            <label>Reviewer *</label>
            <input type="text" value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="Your name" />
          </div>
          <div className="form-field">
            <label>Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
          </div>
          {error && <div className="message error-message">{error}</div>}
          {success && <div className="message info-message">Review submitted.</div>}
          <button type="button" className="primary-button" onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Review"}
          </button>
        </div>

        {!loading && reviews.length > 0 && (
          <div className="review-history">
            <h3>Previous Reviews</h3>
            {reviews.map((r) => (
              <div key={r.id} className="review-item">
                <span className="badge">{r.decision}</span>
                <span className="review-meta">
                  by <strong>{r.reviewer}</strong> on {new Date(r.created_at).toLocaleDateString()}
                </span>
                {r.notes && <p className="review-notes">{r.notes}</p>}
              </div>
            ))}
          </div>
        )}

        {loading && <p className="muted">Loading reviews...</p>}
      </div>
    </div>
  );
}
