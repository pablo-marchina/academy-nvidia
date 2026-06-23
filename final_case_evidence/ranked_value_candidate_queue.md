# Ranked Value Candidate Queue

Candidates are ordered by expected output-quality lift. Non-executable candidates are implementation backlog, not quality-benchmarked adoption candidates.

| Rank | Candidate | Category | Score | Executable | Benchmark | Rationale |
|---:|---|---|---:|---:|---|---|
| 1 | source-trust-aware reranking | 8.6 Reranking | 270 | False |  | source-trust, ranking, source-trust |
| 2 | counter-evidence retrieval | 8.5 RAG/retrieval techniques | 255 | False |  | counter-evidence, evidence, retrieval |
| 3 | counter-evidence retrieval | 8.7 Evidence, verification, uncertainty and abstention | 255 | False |  | counter-evidence, evidence, retrieval |
| 4 | evidence graph construction | 8.9 Graph intelligence | 225 | False |  | evidence graph, evidence |
| 5 | NVIDIA reranker benchmark | 8.6 Reranking | 210 | True |  | reranking, ranking, free external benchmark path |
| 6 | visual reranking | 8.11 Multimodal AI and Document AI | 200 | False |  | reranking, ranking |
| 7 | cross-encoder reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 8 | freshness-aware reranking | 8.6 Reranking | 200 | False |  | freshness-aware, ranking |
| 9 | listwise reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 10 | LLM reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 11 | neural reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 12 | pointwise reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 13 | visual reranking | 8.6 Reranking | 200 | False |  | reranking, ranking |
| 14 | missing evidence prediction | 8.10 Recommendation, ranking and scoring | 195 | False |  | evidence, recommendation |
| 15 | probabilistic evidence aggregation | 8.10 Recommendation, ranking and scoring | 195 | False |  | evidence, recommendation |
| 16 | factual consistency scoring | 8.7 Evidence, verification, uncertainty and abstention | 195 | False |  | evidence, scoring |
| 17 | DRIFT-like search | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 18 | FalkorDB | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 19 | GraphRAG global search | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 20 | GraphRAG local search | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 21 | Kùzu | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 22 | LlamaIndex PropertyGraphIndex | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 23 | Memgraph | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 24 | Neo4j | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 25 | NetworkX | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 26 | Temporal GraphRAG | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 27 | Temporal Knowledge Graph | 8.4 Graph and GraphRAG | 180 | False |  | graphrag, rag |
| 28 | Source trust scoring service | 8.18 Sourcing and crawling | 170 | False |  | scoring, sourcing |
| 29 | corrective RAG / CRAG | 8.5 RAG/retrieval techniques | 170 | False |  | crag, retrieval |
| 30 | HyDE | 8.5 RAG/retrieval techniques | 170 | False |  | hyde, retrieval |
| 31 | self-RAG | 8.5 RAG/retrieval techniques | 170 | False |  | self-rag, retrieval |
| 32 | skeptical RAG | 8.5 RAG/retrieval techniques | 170 | False |  | skeptical rag, retrieval |
| 33 | multi-query retrieval | 8.5 RAG/retrieval techniques | 165 | False |  | multi-query, retrieval |
| 34 | query expansion | 8.5 RAG/retrieval techniques | 165 | False |  | query expansion, retrieval |
| 35 | query rewriting | 8.5 RAG/retrieval techniques | 165 | False |  | query rewriting, retrieval |
| 36 | query transformation | 8.5 RAG/retrieval techniques | 165 | False |  | query transformation, retrieval |
| 37 | bayesian model averaging | 8.7 Evidence, verification, uncertainty and abstention | 155 | False |  | evidence, rag |
| 38 | evidence coverage score | 8.7 Evidence, verification, uncertainty and abstention | 155 | False |  | evidence, rag |
| 39 | Evidence-first UI mode | 8.20 Release, supply chain, repo cleanliness and delivery | 130 | False |  | evidence, release |
| 40 | Final Case Evidence Pack | 8.20 Release, supply chain, repo cleanliness and delivery | 130 | False |  | evidence, release |
| 41 | knowledge graph construction | 8.9 Graph intelligence | 130 | False |  | knowledge graph |
| 42 | multi-hop graph traversal | 8.9 Graph intelligence | 130 | False |  | multi-hop graph |
| 43 | multimodal evidence fusion | 8.11 Multimodal AI and Document AI | 105 | False |  | evidence |
| 44 | active learning by uncertainty | 8.19 Human review, active learning and labeling | 105 | False |  | uncertainty |
| 45 | abstention / refusal policy | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 46 | answerability detection | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 47 | claim decomposition | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | claim |
| 48 | claim-evidence alignment | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | claim |
| 49 | claim verification | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | claim |
| 50 | confidence calibration | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 51 | conformal prediction | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 52 | conformal risk control | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 53 | contradiction detection | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 54 | data sufficiency score | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 55 | ensemble of evaluators | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 56 | entailment-based verification | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 57 | evidence extraction before generation | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 58 | evidence sufficiency classifier | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 59 | hallucination detection pós-geração | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 60 | knowledge conflict resolution | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 61 | model disagreement detection | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 62 | selective prediction | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 63 | source diversity enforcement | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 64 | stepwise evidence accumulation | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 65 | uncertainty estimation | 8.7 Evidence, verification, uncertainty and abstention | 105 | False |  | evidence |
| 66 | contradiction-aware summarization | 8.8 Reasoning, agents and generation | 105 | False |  | contradiction |
| 67 | uncertainty-aware prompting | 8.8 Reasoning, agents and generation | 105 | False |  | uncertainty |
| 68 | bandit-style exploration | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 69 | Bayesian scoring | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 70 | confidence-based model routing | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 71 | constraint-based recommendation | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 72 | cost-aware AI routing | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 73 | decision-theoretic ranking | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 74 | expected information gain | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 75 | expected utility | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 76 | latency-aware pipeline selection | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 77 | learning-to-rank | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 78 | learning-to-recommend | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 79 | multi-objective optimization | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 80 | Pareto frontier | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 81 | quality-cost Pareto routing | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 82 | recommendation system | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 83 | test-time compute control | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 84 | value of information | 8.10 Recommendation, ranking and scoring | 100 | False |  | recommendation |
| 85 | Dependabot | 8.15 Security, guardrails and red team | 100 | True |  | guardrails, free external benchmark path |
| 86 | OpenSSF Scorecard | 8.15 Security, guardrails and red team | 100 | True |  | guardrails, free external benchmark path |
| 87 | Renovate | 8.15 Security, guardrails and red team | 100 | True |  | guardrails, free external benchmark path |
| 88 | Sigstore Cosign | 8.15 Security, guardrails and red team | 100 | True |  | guardrails, free external benchmark path |
| 89 | context priority scoring | 8.17 TOON, context formats and structured interfaces | 100 | False |  | scoring |
| 90 | graph neural ranking | 8.9 Graph intelligence | 100 | False |  | ranking |
| 91 | Bandit | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 92 | Context Firewall | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 93 | Data poisoning detection | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 94 | detect-secrets | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 95 | Garak | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 96 | Giskard | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 97 | Gitleaks | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 98 | Grype | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 99 | Guardrails AI | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 100 | Jailbreak-resistant tool policy | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 101 | Llama Guard | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 102 | LLM Guard | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 103 | NeMo Guardrails | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 104 | NIST AI RMF mapping | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 105 | npm audit | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 106 | OpenGuardrails | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 107 | OWASP LLM Top 10 controls | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 108 | pip-audit | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 109 | Prompt injection defenses | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 110 | Promptfoo | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 111 | Rebuff | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 112 | SBOM | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 113 | Semgrep | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 114 | SLSA | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 115 | Source poisoning detection | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 116 | Syft | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 117 | Trivy | 8.15 Security, guardrails and red team | 90 | False |  | guardrails |
| 118 | Firecrawl | 8.18 Sourcing and crawling | 90 | True |  | sourcing, free external benchmark path |
| 119 | Crawl4AI | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 120 | Data rights registry | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 121 | Expected information gain sourcing | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 122 | Playwright | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 123 | Robots compliance checker | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 124 | Scrapy | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 125 | Source compliance registry | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 126 | Value of information sourcing | 8.18 Sourcing and crawling | 80 | False |  | sourcing |
| 127 | BM25 | 8.3 Vector/search/retrieval | 75 | True | rag_mode_quality | vector |
| 128 | Hybrid retrieval | 8.3 Vector/search/retrieval | 75 | True | rag_mode_quality | vector |
| 129 | BM25 retrieval | 8.5 RAG/retrieval techniques | 75 | True | rag_mode_quality | retrieval |
| 130 | fusion retrieval | 8.5 RAG/retrieval techniques | 75 | True | rag_mode_quality | retrieval |
| 131 | hybrid retrieval | 8.5 RAG/retrieval techniques | 75 | True | rag_mode_quality | retrieval |
| 132 | Reciprocal Rank Fusion | 8.5 RAG/retrieval techniques | 75 | True | rag_mode_quality | retrieval |
| 133 | NVIDIA NeMo Retriever Embedding NIM | 8.3 Vector/search/retrieval | 70 | True |  | vector, free external benchmark path |
| 134 | NVIDIA NeMo Retriever Reranker | 8.3 Vector/search/retrieval | 70 | True |  | vector, free external benchmark path |
| 135 | late-interaction visual retrieval | 8.11 Multimodal AI and Document AI | 60 | False |  | retrieval |
| 136 | multimodal RAG | 8.11 Multimodal AI and Document AI | 60 | False |  | rag |
| 137 | OCR-aware retrieval | 8.11 Multimodal AI and Document AI | 60 | False |  | retrieval |
| 138 | page-image retrieval | 8.11 Multimodal AI and Document AI | 60 | False |  | retrieval |
| 139 | PDF layout-aware retrieval | 8.11 Multimodal AI and Document AI | 60 | False |  | retrieval |
| 140 | table-aware RAG | 8.11 Multimodal AI and Document AI | 60 | False |  | rag |
| 141 | visual document retrieval | 8.11 Multimodal AI and Document AI | 60 | False |  | retrieval |
| 142 | RAGAS | 8.13 Evaluation frameworks and judges | 60 | False |  | rag |
| 143 | Apache Iceberg | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 144 | ClickHouse | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 145 | DataHub | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 146 | Dataset cards | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 147 | dbt | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 148 | Deequ | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 149 | Delta Lake | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 150 | Dolt | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 151 | DuckDB | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 152 | DVC | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 153 | Evidently | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 154 | Feast | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 155 | Git LFS | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 156 | Great Expectations | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 157 | LakeFS | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 158 | Marquez | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 159 | MinIO | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 160 | Model cards | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 161 | OpenLineage | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 162 | OpenMetadata | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 163 | Polars | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 164 | Soda | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 165 | System cards | 8.2 Data layer, storage, versioning and governance | 60 | False |  | rag |
| 166 | ColBERT | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 167 | Elasticsearch | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 168 | Jina AI / DocArray | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 169 | LanceDB | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 170 | Learned sparse retrieval | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 171 | Marqo | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 172 | Milvus | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 173 | OpenSearch | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 174 | Postgres pgvector | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 175 | Qdrant | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 176 | Vespa | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 177 | Weaviate | 8.3 Vector/search/retrieval | 60 | False |  | vector |
| 178 | access-control-aware RAG | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 179 | active retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 180 | adaptive RAG | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 181 | atomic fact extraction | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 182 | auto-merging retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 183 | cache-aware retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 184 | ColBERT / late-interaction retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 185 | contextual compression | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 186 | contextual retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 187 | cross-lingual retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 188 | hierarchical summarization | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 189 | iterative retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 190 | learned sparse retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 191 | least-context retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 192 | long-context RAG | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 193 | meta-retrieval / router de retrievers | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 194 | metadata-aware chunking | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 195 | metadata filtering | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 196 | multi-hop retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 197 | parent-child retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 198 | permission-preserving retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 199 | proposition-based chunking | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 200 | query intent classification | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 201 | RAG-Fusion | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 202 | RAPTOR / hierarchical retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 203 | retrieval budget allocation | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 204 | semantic cache | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 205 | semantic chunking | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 206 | sentence-window retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 207 | small-to-big retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 208 | translation-aware retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | retrieval |
| 209 | vector retrieval | 8.5 RAG/retrieval techniques | 60 | False |  | vector |
| 210 | similar startup retrieval | 8.9 Graph intelligence | 60 | False |  | retrieval |
| 211 | Helicone | 8.14 Observability, LLMOps and experiment tracking | 45 | True |  | observability, free external benchmark path |
| 212 | Langfuse | 8.14 Observability, LLMOps and experiment tracking | 45 | True |  | observability, free external benchmark path |
| 213 | Phoenix | 8.14 Observability, LLMOps and experiment tracking | 45 | True |  | observability, free external benchmark path |
| 214 | Alembic | 8.1 Runtime core | 35 | False |  | runtime |
| 215 | Docker Compose | 8.1 Runtime core | 35 | False |  | runtime |
| 216 | FastAPI | 8.1 Runtime core | 35 | False |  | runtime |
| 217 | PostgreSQL | 8.1 Runtime core | 35 | False |  | runtime |
| 218 | Qdrant | 8.1 Runtime core | 35 | False |  | runtime |
| 219 | React | 8.1 Runtime core | 35 | False |  | runtime |
| 220 | SQLAlchemy | 8.1 Runtime core | 35 | False |  | runtime |
| 221 | TypeScript | 8.1 Runtime core | 35 | False |  | runtime |
| 222 | Vite | 8.1 Runtime core | 35 | False |  | runtime |
| 223 | Aim | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 224 | Evidently | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 225 | Grafana | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 226 | Grafana Alloy | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 227 | Jaeger | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 228 | Loki | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 229 | MLflow | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 230 | OpenInference | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 231 | OpenLLMetry / Traceloop | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 232 | OpenTelemetry | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 233 | OpenTelemetry GenAI semantic conventions | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 234 | Prometheus | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 235 | Sentry | 8.14 Observability, LLMOps and experiment tracking | 35 | False |  | observability |
| 236 | AI governance maturity report | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 237 | AI Incident Response Plan | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 238 | Cold Start Reproducibility Test | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 239 | Data retention policy | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 240 | Deprecation policy | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 241 | Documentation Consistency Gate | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 242 | External Reviewer Mode | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 243 | Final Delivery Index | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 244 | Final Evaluator Checklist | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 245 | License and Third-Party Compliance | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 246 | make prove-final-product | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 247 | No Hidden Manual Step Gate | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 248 | No Hidden State Rule | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 249 | Operational runbooks | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 250 | Repository Cleanliness Gate | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 251 | Repository Purpose Manifest | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 252 | Reproducible case package | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 253 | Root Cause Analysis workflow | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 254 | Supply Chain Maturity Gate | 8.20 Release, supply chain, repo cleanliness and delivery | 35 | False |  | release |
| 255 | NVIDIA NeMo Retriever extraction | 8.12 Parsing, OCR and extraction tools | 20 | True |  | free external benchmark path |
| 256 | Custom NVIDIA eval harness | 8.13 Evaluation frameworks and judges | 20 | True |  | free external benchmark path |
| 257 | OpenAI Evals | 8.13 Evaluation frameworks and judges | 20 | True |  | free external benchmark path |
| 258 | Opik | 8.13 Evaluation frameworks and judges | 20 | True |  | free external benchmark path |
| 259 | A2A / Agent-to-Agent Protocol | 8.16 MCP, tools and agent protocols | 20 | True |  | free external benchmark path |
| 260 | AGNTCY / Agent Connect | 8.16 MCP, tools and agent protocols | 20 | True |  | free external benchmark path |
| 261 | Temporal activities | 8.16 MCP, tools and agent protocols | 20 | True |  | free external benchmark path |
| 262 | Argilla | 8.19 Human review, active learning and labeling | 20 | True |  | free external benchmark path |
| 263 | Label Studio | 8.19 Human review, active learning and labeling | 20 | True |  | free external benchmark path |
| 264 | chart understanding | 8.11 Multimodal AI and Document AI | 10 | False |  | lower expected output-quality leverage |
| 265 | document layout understanding | 8.11 Multimodal AI and Document AI | 10 | False |  | lower expected output-quality leverage |
| 266 | multimodal ingestion | 8.11 Multimodal AI and Document AI | 10 | False |  | lower expected output-quality leverage |
| 267 | table-to-graph extraction | 8.11 Multimodal AI and Document AI | 10 | False |  | lower expected output-quality leverage |
| 268 | Apache Tika | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 269 | Camelot | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 270 | Chart extraction | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 271 | Docling | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 272 | GROBID | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 273 | Image extraction | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 274 | LayoutParser | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 275 | Marker | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 276 | PaddleOCR | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 277 | PDF parsing | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 278 | Pitch deck parsing | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 279 | PyMuPDF | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 280 | Surya OCR | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 281 | Table extraction | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 282 | Tabula | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 283 | Tesseract | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 284 | Unstructured | 8.12 Parsing, OCR and extraction tools | 10 | False |  | lower expected output-quality leverage |
| 285 | Deepchecks | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 286 | DeepEval | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 287 | Giskard | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 288 | Human adjudication protocol | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 289 | LLM-as-a-judge calibrado | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 290 | Promptfoo | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 291 | TruLens | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 292 | UpTrain | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 293 | Verifier model | 8.13 Evaluation frameworks and judges | 10 | False |  | lower expected output-quality leverage |
| 294 | agent blast-radius controls | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 295 | Function calling | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 296 | gRPC tools | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 297 | LangChain Tools | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 298 | LlamaIndex Tools | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 299 | MCP | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 300 | OpenAPI tool calling | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 301 | REST tools | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 302 | Secure MCP gateway | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 303 | Semantic Kernel plugins | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 304 | tool allowlist | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 305 | tool audit ledger | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 306 | tool schema validation | 8.16 MCP, tools and agent protocols | 10 | False |  | lower expected output-quality leverage |
| 307 | Apache Arrow | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 308 | Avro | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 309 | context compression | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 310 | context diffing | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 311 | context packer | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 312 | context registry | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 313 | CSV/TSV | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 314 | Guidance | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 315 | Instructor | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 316 | JSON | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 317 | JSON Lines / NDJSON | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 318 | JSON Schema constrained decoding | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 319 | LMQL | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 320 | Markdown tables | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 321 | MessagePack | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 322 | Outlines | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 323 | Parquet | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 324 | prompt assembler | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 325 | prompt registry | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 326 | prompt snapshotting | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 327 | Protocol Buffers | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 328 | Pydantic JSON Schema | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 329 | structured context DSL | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 330 | token budgeter | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 331 | tool result schema validation | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 332 | TOON | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 333 | TRON | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 334 | xgrammar | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 335 | XML tags | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 336 | YAML | 8.17 TOON, context formats and structured interfaces | 10 | False |  | lower expected output-quality leverage |
| 337 | active error discovery | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 338 | active learning | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 339 | custom review UI | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 340 | dataset curation with disagreement sampling | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 341 | disagreement-based sampling | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 342 | distillation | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 343 | fine-tuning / LoRA if justified | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 344 | human feedback loop | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 345 | human override governance | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 346 | human preference optimization | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 347 | knowledge distillation from expert reviews | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 348 | labeling functions | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 349 | learning-to-rank from review data | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 350 | mixture-of-experts routing | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 351 | programmatic labeling | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 352 | weak supervision | 8.19 Human review, active learning and labeling | 10 | False |  | lower expected output-quality leverage |
| 353 | abductive reasoning | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 354 | automatic prompt repair | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 355 | belief state tracking | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 356 | blackboard architecture | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 357 | causal graph light | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 358 | citation-aware generation | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 359 | code-assisted reasoning | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 360 | constrained decoding | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 361 | counterfactual reasoning | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 362 | critic-as-tool | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 363 | debate / multi-agent critique | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 364 | decomposition prompting | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 365 | factored decomposition | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 366 | grammar-based output | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 367 | hypothesis generation + testing | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 368 | least-to-most prompting | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 369 | plan-and-execute | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 370 | Program-of-Thought | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 371 | prompt ensembling | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 372 | provenance-aware generation | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 373 | ReAct | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 374 | reflection loops | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 375 | reliability-aware generation | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 376 | rubric-based generation | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 377 | selective generation | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 378 | self-consistency | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 379 | step-back prompting | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 380 | structured outputs | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 381 | toolformer-style function calling | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 382 | Tree-of-Thought | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 383 | verifier-guided decoding | 8.8 Reasoning, agents and generation | 10 | False |  | lower expected output-quality leverage |
| 384 | case-based reasoning | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 385 | community detection | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 386 | graph consistency checking | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 387 | ontology-guided extraction | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 388 | ontology learning semi-automático | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 389 | schema linking | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 390 | table-to-graph extraction | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
| 391 | truth maintenance system | 8.9 Graph intelligence | 10 | False |  | lower expected output-quality leverage |
