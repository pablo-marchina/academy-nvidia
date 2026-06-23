# Final Evaluation Plan

Final evaluation combines existing product validation with benchmark-first
governance.

Required proof layers:

- Backend unit and acceptance tests
- Frontend TypeScript build and UI smoke path
- RAG/Qdrant readiness checks in product mode
- Candidate catalog completeness
- Benchmark result schema validation
- Numeric governance and calibration checks
- Source compliance and live collection report
- Data lineage and evidence-to-decision coverage
- Security, license, release, and no-hidden-manual-step reports

Run:

```bash
make prove-final-product
```

Expensive or environment-dependent checks must fail explicitly when required
configuration is missing. They must not silently fall back to demo or mock data.
