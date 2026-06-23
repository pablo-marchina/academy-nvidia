# Direct Benchmark Protocol

## Baseline

Use the current product baseline: Qdrant/vector retrieval, BM25 lexical retrieval where available, deterministic fusion/reranking, evidence packing, persisted claims, and current recommendation generation.

## Candidate

Run one candidate at a time against the same golden eval cases. A candidate can be promoted only if it is reproducible, actively used, directly benchmarked, and improves a primary quality metric without unacceptable cost, latency, or security regression.

## Required Metrics

- context_precision
- context_recall
- faithfulness
- answer_relevancy
- unsupported_claim_rate
- recommendation_precision
- multi_hop_accuracy
- source_diversity
- latency_p50
- latency_p95
- cost_per_run
- failure_rate

## Promotion Rule

No PROXY or LOCAL_READINESS result may promote runtime adoption. Runtime promotion requires direct output quality evidence, a decision ledger entry, traceable evidence, configuration validation, tests, security gates, and release gates.

## Rejection Rule

Reject or hold candidates that duplicate current behavior, require unavailable paid services, increase latency without quality gain, reduce claim support, increase security risk, cannot be configured before use, or cannot be reproduced in the final environment.
