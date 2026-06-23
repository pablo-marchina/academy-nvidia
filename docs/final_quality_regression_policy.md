# Final Quality Regression Policy

Regression budgets are symbolic until baselines are calibrated.

```text
retrieval_regression_budget = TBD_BY_BASELINE
rag_quality_regression_budget = TBD_BY_BASELINE
security_regression_budget = TBD_BY_SECURITY_POLICY
cost_regression_budget = TBD_BY_PRODUCT_BASELINE
latency_regression_budget = TBD_BY_PRODUCT_BASELINE
```

## Required Metrics

- faithfulness
- context_precision
- context_recall
- answer_relevancy
- claim_support_rate
- unsupported_claim_rate
- nvidia_mapping_groundedness
- recommendation_actionability
- abstention_accuracy
- evidence_to_decision_coverage
- human_review_agreement
- retrieval_quality_lift
- reranker_lift
- graph_rag_lift
- cost_quality_ratio
- latency_quality_ratio
- security_risk_delta

## Gate

`check_quality_regression_policy` passes only when every production threshold points to a calibrated baseline or approved policy, not a hard-coded uncalibrated number.
