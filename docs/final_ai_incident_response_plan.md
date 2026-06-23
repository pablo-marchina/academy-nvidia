# Final AI Incident Response Plan

Each incident record must use these fields:

```text
incident_id
severity
trigger
detection_method
impact
immediate_action
rollback
owner
root_cause
regression_test_added
prevention
status
```

Severity values are `TBD_BY_SECURITY_POLICY`.

## Required Incidents

| Incident | Trigger | Immediate action |
|---|---|---|
| recommendation_without_evidence | Recommendation lacks evidence, RAG support, confidence, business impact, implementation complexity, or next action | Block publication and open RCA |
| prompt_injection_detected | External content attempts to control tools, system prompts, or policy | Quarantine source and record context firewall event |
| source_poisoning_detected | Source content contradicts trusted evidence or shows manipulation | Demote source trust and require human review |
| secret_exposure | Secret-like material appears in context, logs, release ZIP, or output | Rotate affected credential and remove artifact |
| mcp_tool_policy_violation | Tool call violates approval, scope, or source policy | Stop run and require owner review |
| rag_quality_drop | Retrieval quality falls outside `TBD_BY_BASELINE` budget | Roll back retrieval candidate and rerun evals |
| nvidia_mapping_error | NVIDIA product mapping is unsupported or contradicted | Remove mapping and add regression case |
| temporal_leakage_detected | Output uses future or stale evidence incorrectly | Rebuild corpus with valid timestamps |
| source_compliance_violation | Source lacks approved robots, terms, storage, or redistribution status | Disable source and purge restricted data |
| benchmark_contamination_detected | Benchmark data overlaps with calibration/evaluation labels improperly | Invalidate benchmark and regenerate split |

## Evidence

- `final_case_evidence/context_firewall_report.json`
- `final_case_evidence/prompt_injection_test_report.json`
- `final_case_evidence/rca_workflow_report.json`
