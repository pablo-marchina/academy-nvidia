# Final RCA Workflow

Root Cause Analysis is required for failed final gates, unsupported recommendations, benchmark contamination, source compliance violations, security findings, and regressions.

## Fields

```text
failure_id
failure_type
affected_run
root_cause
impact
fix
regression_test_added
metric_affected
owner
status
```

## Workflow

1. Create one RCA record per failure.
2. Classify the failure as runtime, evidence, benchmark, source compliance, security, release, documentation, or environment.
3. Link the affected run or artifact.
4. Add a fix or formal non-runtime status.
5. Add or justify a regression test.
6. Rerun the impacted gate before closing.

## Evidence

- `final_case_evidence/rca_workflow_report.json`
