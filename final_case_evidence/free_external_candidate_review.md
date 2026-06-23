# Free External Candidate Review

Status: `PASS`

- Registry entries: 36
- Matched catalog entries: 36
- Ranking eligible: 20
- Needs free-tier verification: 14
- Not in catalog: 0

| Candidate | Status | Catalog | Ranking eligible | Benchmark path |
|---|---|---:|---:|---|
| WhyLabs | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare monitoring signal quality only after no-cost terms are verified. |
| BigQuery/Snowflake | PAID_OR_TRIAL_ONLY | True | False | Use local DuckDB/PostgreSQL proxy until direct no-cost cloud benchmark is approved. |
| NVIDIA NeMo Retriever Embedding NIM | FREE_API_BENCHMARKABLE | True | True | Benchmark retrieval quality, latency, cost, and failure behavior against local sentence-transformers embeddings and Qdrant. |
| NVIDIA NeMo Retriever Reranker | FREE_API_BENCHMARKABLE | True | True | Benchmark output-quality lift against deterministic reranking, source-quality ranking, and counter-evidence retrieval. |
| NVIDIA reranker benchmark | FREE_API_BENCHMARKABLE | True | True | Run reranker quality benchmark against the existing RAG golden queries. |
| NVIDIA NeMo Retriever extraction | FREE_API_BENCHMARKABLE | True | True | Compare document extraction quality against local parser baselines on fixed corpus fixtures. |
| LlamaParse | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare parsing quality against Docling/PyMuPDF/local parser baselines after no-cost terms are verified. |
| OpenAI Evals | FREE_LOCAL_SUBSTITUTE | True | True | Evaluate whether the harness improves evaluator coverage and defect detection using local/null providers first. |
| Parea AI | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare evaluator coverage only after free/no-cost account terms are verified. |
| Opik | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare evaluation trace/report quality against existing evidence reports. |
| Custom NVIDIA eval harness | INTERNAL_LOCAL_BENCHMARKABLE | True | True | Run existing evaluation harness against RAG/recommendation quality fixtures. |
| Phoenix | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare trace/evaluation evidence completeness against current local reports using synthetic acceptance runs. |
| Langfuse | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare trace completeness, evaluator usability, and operational evidence quality against current local reports. |
| LangSmith | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare trace/eval quality only after no-cost account terms are verified. |
| Braintrust | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare evaluator and trace quality only after no-cost account terms are verified. |
| Weights & Biases Weave | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare trace/eval quality against current evidence reports after terms are verified. |
| Helicone | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare request observability and cost evidence against current local reports. |
| Maxim | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare evaluator and observability quality only after no-cost account terms are verified. |
| Fiddler | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare monitoring value only after no-cost terms are verified. |
| AgentOps | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare agent trace quality only after no-cost account terms are verified. |
| Weights & Biases | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare experiment tracking output quality only after no-cost account terms are verified. |
| Neptune | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare experiment tracking output quality only after no-cost account terms are verified. |
| Lakera Guard | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare prompt-injection/security detection quality only after no-cost terms are verified. |
| OpenSSF Scorecard | FREE_EXTERNAL_BENCHMARKABLE | True | True | Run against repository metadata or local checkout to compare supply-chain risk signal quality against the current security/release report. |
| Sigstore Cosign | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare release provenance and verification evidence against current release artifact manifest. |
| Renovate | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare dependency update signal quality, false positives, and actionable remediation detail against current manifest-only license/security inventory. |
| Dependabot | FREE_API_BENCHMARKABLE | True | True | Compare dependency alert/update signal quality against Renovate and current local inventory. |
| Temporal activities | FREE_LOCAL_SUBSTITUTE | True | True | Compare orchestration reliability and retry evidence against current local workflow. |
| A2A / Agent-to-Agent Protocol | FREE_LOCAL_SUBSTITUTE | True | True | Compare protocol interoperability and schema value against current tool contracts. |
| AGNTCY / Agent Connect | FREE_LOCAL_SUBSTITUTE | True | True | Compare interoperability and governance value against current tool contracts. |
| Firecrawl | FREE_LOCAL_SUBSTITUTE | True | True | Compare live sourcing coverage, provenance quality, robots/terms compliance, latency, and cost against current collectors. |
| Apify | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare source coverage and evidence freshness against governed in-repo collectors after no-cost terms are verified. |
| Label Studio | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare human review throughput, schema fit, and evidence correction quality against current manual evaluator checklist. |
| Argilla | FREE_EXTERNAL_BENCHMARKABLE | True | True | Compare review quality, disagreement capture, and dataset export value against current evaluator checklist. |
| Humanloop | NEEDS_FREE_TIER_VERIFICATION | True | False | Compare human review and feedback workflow quality only after no-cost account terms are verified. |
| Prodigy | PAID_OR_TRIAL_ONLY | True | False | Use Label Studio/Argilla as no-cost benchmark alternatives. |
