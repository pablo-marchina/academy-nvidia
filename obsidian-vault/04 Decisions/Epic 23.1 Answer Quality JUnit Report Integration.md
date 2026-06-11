# Epic 23.1 Answer Quality JUnit Report Integration

**Date:** 2026-06-11
**Decision:** Use pytest JUnit XML as the Answer Quality reporting bridge.

## Context

Answer Quality evals already run offline, and the dashboard already consolidates
JUnit from RAG and golden evals. The missing piece was automatic generation and
dashboard parsing of a dedicated Answer Quality JUnit report.

## Decision

Generate `answer_quality_eval_junit.xml` through pytest in Makefile and corpus
maintenance, then parse it in the regression dashboard. Missing XML is a
controlled WARN; failures or errors in the XML produce dashboard FAIL.

## Consequences

- GitHub Actions can publish the report as an artifact without a custom report
  format.
- The dashboard gets standard operational counters.
- Detailed semantic metrics remain in the deterministic harness, not in JUnit.
