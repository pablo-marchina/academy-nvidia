# All Candidate Benchmark Documentation

This document records the benchmark disposition for every technology in the canonical roadmap catalog.

Adoption rule: a technology is added only when a direct benchmark shows measurable output-quality lift over the current product baseline. Readiness, file presence, or category coverage alone are not adoption evidence.

## Summary

- Total candidates: 408
- Total benchmark results: 408
- Direct/current-product benchmarks: 371
- External/future research: 37
- Add to product now: 0
- Keep baseline: 358
- Keep required runtime: 11
- Needs direct quality benchmark: 0

## Decisions

| Candidate | Category | Decision | Quality delta | Reason |
|---|---|---:|---:|---|
| Alembic | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Docker Compose | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| FastAPI | 8.1 Runtime core | REJECT_BY_EVIDENCE |  | No module named 'sqlalchemy' |
| PostgreSQL | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Qdrant | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| React | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| SQLAlchemy | 8.1 Runtime core | REJECT_BY_EVIDENCE |  | No module named 'sqlalchemy' |
| TypeScript | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Vite | 8.1 Runtime core | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Bayesian scoring | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Pareto frontier | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| bandit-style exploration | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| confidence-based model routing | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| constraint-based recommendation | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| cost-aware AI routing | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| decision-theoretic ranking | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| expected information gain | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| expected utility | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| latency-aware pipeline selection | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| learning-to-rank | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| learning-to-recommend | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| missing evidence prediction | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multi-objective optimization | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| probabilistic evidence aggregation | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| quality-cost Pareto routing | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| recommendation system | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| test-time compute control | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| value of information | 8.10 Recommendation, ranking and scoring | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OCR-aware retrieval | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| PDF layout-aware retrieval | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| chart understanding | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| document layout understanding | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| late-interaction visual retrieval | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multimodal RAG | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multimodal evidence fusion | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multimodal ingestion | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| page-image retrieval | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| table-aware RAG | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| table-to-graph extraction | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| visual document retrieval | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| visual reranking | 8.11 Multimodal AI and Document AI | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Apache Tika | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Camelot | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Chart extraction | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Docling | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| GROBID | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Image extraction | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LayoutParser | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LlamaParse | 8.12 Parsing, OCR and extraction tools | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Marker | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NVIDIA NeMo Retriever extraction | 8.12 Parsing, OCR and extraction tools | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| PDF parsing | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| PaddleOCR | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Pitch deck parsing | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| PyMuPDF | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Surya OCR | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Table extraction | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Tabula | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Tesseract | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Unstructured | 8.12 Parsing, OCR and extraction tools | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Custom NVIDIA eval harness | 8.13 Evaluation frameworks and judges | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| DeepEval | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Deepchecks | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Giskard | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Human adjudication protocol | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LLM-as-a-judge calibrado | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenAI Evals | 8.13 Evaluation frameworks and judges | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Opik | 8.13 Evaluation frameworks and judges | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Parea AI | 8.13 Evaluation frameworks and judges | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Promptfoo | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| RAGAS | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| TruLens | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| UpTrain | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Verifier model | 8.13 Evaluation frameworks and judges | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| AgentOps | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Aim | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Braintrust | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Evidently | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Fiddler | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Grafana | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Grafana Alloy | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Helicone | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Jaeger | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LangSmith | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Langfuse | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Loki | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| MLflow | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Maxim | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Neptune | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| OpenInference | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenLLMetry / Traceloop | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenTelemetry | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenTelemetry GenAI semantic conventions | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Phoenix | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Prometheus | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Sentry | 8.14 Observability, LLMOps and experiment tracking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Weights & Biases | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Weights & Biases Weave | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| WhyLabs | 8.14 Observability, LLMOps and experiment tracking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Bandit | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Context Firewall | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Data poisoning detection | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Dependabot | 8.15 Security, guardrails and red team | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Garak | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Giskard | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Gitleaks | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Grype | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Guardrails AI | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Jailbreak-resistant tool policy | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LLM Guard | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Lakera Guard | 8.15 Security, guardrails and red team | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Llama Guard | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NIST AI RMF mapping | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NeMo Guardrails | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OWASP LLM Top 10 controls | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenGuardrails | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenSSF Scorecard | 8.15 Security, guardrails and red team | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Prompt injection defenses | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Promptfoo | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Rebuff | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Renovate | 8.15 Security, guardrails and red team | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| SBOM | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| SLSA | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Semgrep | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Sigstore Cosign | 8.15 Security, guardrails and red team | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Source poisoning detection | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Syft | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Trivy | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| detect-secrets | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| npm audit | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| pip-audit | 8.15 Security, guardrails and red team | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| A2A / Agent-to-Agent Protocol | 8.16 MCP, tools and agent protocols | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| AGNTCY / Agent Connect | 8.16 MCP, tools and agent protocols | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Function calling | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LangChain Tools | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LlamaIndex Tools | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| MCP | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenAPI tool calling | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| REST tools | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Secure MCP gateway | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Semantic Kernel plugins | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Temporal activities | 8.16 MCP, tools and agent protocols | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| agent blast-radius controls | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| gRPC tools | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| tool allowlist | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| tool audit ledger | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| tool schema validation | 8.16 MCP, tools and agent protocols | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Apache Arrow | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Avro | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| CSV/TSV | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Guidance | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Instructor | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| JSON | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| JSON Lines / NDJSON | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| JSON Schema constrained decoding | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LMQL | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Markdown tables | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| MessagePack | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Outlines | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Parquet | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Protocol Buffers | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Pydantic JSON Schema | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| TOON | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| TRON | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| XML tags | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| YAML | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| context compression | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| context diffing | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| context packer | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| context priority scoring | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| context registry | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| prompt assembler | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| prompt registry | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| prompt snapshotting | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| structured context DSL | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| token budgeter | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| tool result schema validation | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| xgrammar | 8.17 TOON, context formats and structured interfaces | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Apify | 8.18 Sourcing and crawling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Crawl4AI | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Data rights registry | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Expected information gain sourcing | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Firecrawl | 8.18 Sourcing and crawling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Playwright | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Robots compliance checker | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Scrapy | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Source compliance registry | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Source trust scoring service | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Value of information sourcing | 8.18 Sourcing and crawling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Argilla | 8.19 Human review, active learning and labeling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Humanloop | 8.19 Human review, active learning and labeling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Label Studio | 8.19 Human review, active learning and labeling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| Prodigy | 8.19 Human review, active learning and labeling | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| active error discovery | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| active learning | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| active learning by uncertainty | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| custom review UI | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| dataset curation with disagreement sampling | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| disagreement-based sampling | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| distillation | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| fine-tuning / LoRA if justified | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| human feedback loop | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| human override governance | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| human preference optimization | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| knowledge distillation from expert reviews | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| labeling functions | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| learning-to-rank from review data | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| mixture-of-experts routing | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| programmatic labeling | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| weak supervision | 8.19 Human review, active learning and labeling | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Apache Iceberg | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| BigQuery/Snowflake | 8.2 Data layer, storage, versioning and governance | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| ClickHouse | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| DVC | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| DataHub | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Dataset cards | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Deequ | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Delta Lake | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Dolt | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| DuckDB | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Evidently | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Feast | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Git LFS | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Great Expectations | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LakeFS | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Marquez | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| MinIO | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Model cards | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenLineage | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| OpenMetadata | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Polars | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Soda | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| System cards | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| WhyLabs | 8.2 Data layer, storage, versioning and governance | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| dbt | 8.2 Data layer, storage, versioning and governance | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| AI Incident Response Plan | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| AI governance maturity report | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Cold Start Reproducibility Test | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Data retention policy | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Deprecation policy | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Documentation Consistency Gate | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Evidence-first UI mode | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| External Reviewer Mode | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Final Case Evidence Pack | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Final Delivery Index | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Final Evaluator Checklist | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| License and Third-Party Compliance | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| No Hidden Manual Step Gate | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| No Hidden State Rule | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Operational runbooks | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Repository Cleanliness Gate | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Repository Purpose Manifest | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Reproducible case package | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Root Cause Analysis workflow | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Supply Chain Maturity Gate | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| make prove-final-product | 8.20 Release, supply chain, repo cleanliness and delivery | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| BM25 | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ColBERT | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Elasticsearch | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Hybrid retrieval | 8.3 Vector/search/retrieval | KEEP_BASELINE | -0.155 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Jina AI / DocArray | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LanceDB | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Learned sparse retrieval | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Marqo | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Milvus | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NVIDIA NeMo Retriever Embedding NIM | 8.3 Vector/search/retrieval | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| NVIDIA NeMo Retriever Reranker | 8.3 Vector/search/retrieval | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| OpenSearch | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Postgres pgvector | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Qdrant | 8.3 Vector/search/retrieval | KEEP_REQUIRED_RUNTIME |  | Direct readiness benchmark passed for an active runtime/governance component. This is not evidence of output-quality lift, so it does not justify adding a new technology. |
| Vespa | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Weaviate | 8.3 Vector/search/retrieval | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| DRIFT-like search | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| FalkorDB | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| GraphRAG global search | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| GraphRAG local search | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Kùzu | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LlamaIndex PropertyGraphIndex | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Memgraph | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Neo4j | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NetworkX | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Temporal GraphRAG | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Temporal Knowledge Graph | 8.4 Graph and GraphRAG | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| BM25 retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ColBERT / late-interaction retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| HyDE | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| RAG-Fusion | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| RAPTOR / hierarchical retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Reciprocal Rank Fusion | 8.5 RAG/retrieval techniques | KEEP_BASELINE | -0.155 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| access-control-aware RAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| active retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| adaptive RAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| atomic fact extraction | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| auto-merging retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| cache-aware retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| contextual compression | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| contextual retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| corrective RAG / CRAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| counter-evidence retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| cross-lingual retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| fusion retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| hierarchical summarization | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| hybrid retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | -0.155 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| iterative retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| learned sparse retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| least-context retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| long-context RAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| meta-retrieval / router de retrievers | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| metadata filtering | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| metadata-aware chunking | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multi-hop retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multi-query retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| parent-child retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| permission-preserving retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| proposition-based chunking | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| query expansion | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| query intent classification | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| query rewriting | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| query transformation | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| retrieval budget allocation | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| self-RAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| semantic cache | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| semantic chunking | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| sentence-window retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| skeptical RAG | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| small-to-big retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| translation-aware retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| vector retrieval | 8.5 RAG/retrieval techniques | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| LLM reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| NVIDIA reranker benchmark | 8.6 Reranking | FUTURE_RESEARCH |  | Original candidate requires unavailable SaaS, license, hardware, or credentials. |
| cross-encoder reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| freshness-aware reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| listwise reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| neural reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| pointwise reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| source-trust-aware reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| visual reranking | 8.6 Reranking | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| abstention / refusal policy | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| answerability detection | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| bayesian model averaging | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| claim decomposition | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| claim verification | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| claim-evidence alignment | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| confidence calibration | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| conformal prediction | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| conformal risk control | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| contradiction detection | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| counter-evidence retrieval | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| data sufficiency score | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ensemble of evaluators | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| entailment-based verification | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| evidence coverage score | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| evidence extraction before generation | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| evidence sufficiency classifier | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| factual consistency scoring | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| hallucination detection pós-geração | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| knowledge conflict resolution | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| model disagreement detection | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| selective prediction | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| source diversity enforcement | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| stepwise evidence accumulation | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| uncertainty estimation | 8.7 Evidence, verification, uncertainty and abstention | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Program-of-Thought | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ReAct | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| Tree-of-Thought | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| abductive reasoning | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| automatic prompt repair | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| belief state tracking | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| blackboard architecture | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| causal graph light | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| citation-aware generation | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| code-assisted reasoning | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| constrained decoding | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| contradiction-aware summarization | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| counterfactual reasoning | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| critic-as-tool | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| debate / multi-agent critique | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| decomposition prompting | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| factored decomposition | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| grammar-based output | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| hypothesis generation + testing | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| least-to-most prompting | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| plan-and-execute | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| prompt ensembling | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| provenance-aware generation | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| reflection loops | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| reliability-aware generation | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| rubric-based generation | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| selective generation | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| self-consistency | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| step-back prompting | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| structured outputs | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| toolformer-style function calling | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| uncertainty-aware prompting | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| verifier-guided decoding | 8.8 Reasoning, agents and generation | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| case-based reasoning | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| community detection | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| evidence graph construction | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| graph consistency checking | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| graph neural ranking | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| knowledge graph construction | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| multi-hop graph traversal | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ontology learning semi-automático | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| ontology-guided extraction | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| schema linking | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| similar startup retrieval | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| table-to-graph extraction | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
| truth maintenance system | 8.9 Graph intelligence | KEEP_BASELINE | 0.0 | Direct output-quality benchmark did not improve result quality against the baseline. Do not add as a quality improvement. |
