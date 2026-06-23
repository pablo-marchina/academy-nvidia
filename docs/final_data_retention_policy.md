# Final Data Retention Policy

Retention values are `TBD_BY_COMPLIANCE_REVIEW` until approved by compliance review.

## Policy

| Area | Rule |
|---|---|
| what to store | Store evidence, source metadata, retrieval chunks, benchmark outputs, and audit logs with explicit purpose |
| why store | Preserve traceability from recommendation to evidence and decision |
| retention period | `TBD_BY_COMPLIANCE_REVIEW` |
| deletion | Delete by source, evidence id, run id, or startup id through documented operational procedure |
| source invalidation | Mark source inactive, remove from retrieval, and rerun affected recommendations |
| reprocessing | Rebuild chunks, embeddings, lineage, and affected action briefs |
| evidence exclusion | Remove unsupported or disallowed evidence from RAG and generated outputs |
| logs/traces | Retain only fields required for audit, debugging, security, and benchmark reproducibility |

## Least-Context Rule

Collect the maximum necessary for the decision, store only data with purpose, and send the minimum supported evidence to the LLM.

## Evidence

- `final_case_evidence/data_minimization_report.json`
- `final_case_evidence/least_context_report.json`
