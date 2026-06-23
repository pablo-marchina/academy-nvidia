# Direct Alternative Gap Benchmark Report

Status: PASS
Total alternatives: 63
Resolved alternatives: 63
Remaining direct gaps: 0
Direct lifts found: 0

## Families

| Family | Total | Resolved | Remaining |
| --- | ---: | ---: | ---: |
| Query rewriting and multi-query retrieval | 8 | 8 | 0 |
| Recommendation specificity and next action | 5 | 5 | 0 |
| GraphRAG and evidence graph | 12 | 12 | 0 |
| Counter-evidence retrieval and contradiction handling | 8 | 8 | 0 |
| Source trust, quality, and freshness | 5 | 5 | 0 |
| Evidence sufficiency and abstention | 25 | 25 | 0 |

## Results

| Family | Candidate | Outcome | Delta vs current |
| --- | --- | --- | ---: |
| Query rewriting and multi-query retrieval | Hybrid retrieval | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Query rewriting and multi-query retrieval | query rewriting | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Query rewriting and multi-query retrieval | query transformation | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Query rewriting and multi-query retrieval | query expansion | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Query rewriting and multi-query retrieval | multi-query retrieval | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Query rewriting and multi-query retrieval | HyDE | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Query rewriting and multi-query retrieval | Reciprocal Rank Fusion | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Query rewriting and multi-query retrieval | hybrid retrieval | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Recommendation specificity and next action | value of information | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Recommendation specificity and next action | expected information gain | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Recommendation specificity and next action | missing evidence prediction | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Recommendation specificity and next action | Expected information gain sourcing | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Recommendation specificity and next action | Value of information sourcing | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| GraphRAG and evidence graph | Neo4j | DIRECT_IMPLEMENTATION_NO_LIFT | -0.1051 |
| GraphRAG and evidence graph | Memgraph | DIRECT_IMPLEMENTATION_NO_LIFT | -0.1069 |
| GraphRAG and evidence graph | Kùzu | DIRECT_IMPLEMENTATION_NO_LIFT | -0.1105 |
| GraphRAG and evidence graph | FalkorDB | DIRECT_IMPLEMENTATION_NO_LIFT | -0.1087 |
| GraphRAG and evidence graph | NetworkX | DIRECT_IMPLEMENTATION_NO_LIFT | -0.0783 |
| GraphRAG and evidence graph | LlamaIndex PropertyGraphIndex | DIRECT_IMPLEMENTATION_NO_LIFT | -0.1048 |
| GraphRAG and evidence graph | GraphRAG local search | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| GraphRAG and evidence graph | GraphRAG global search | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| GraphRAG and evidence graph | DRIFT-like search | DIRECT_IMPLEMENTATION_NO_LIFT | -0.0765 |
| GraphRAG and evidence graph | Temporal GraphRAG | DIRECT_IMPLEMENTATION_NO_LIFT | -0.0533 |
| GraphRAG and evidence graph | Temporal Knowledge Graph | DIRECT_IMPLEMENTATION_NO_LIFT | -0.0551 |
| GraphRAG and evidence graph | knowledge graph construction | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Counter-evidence retrieval and contradiction handling | corrective RAG / CRAG | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Counter-evidence retrieval and contradiction handling | self-RAG | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Counter-evidence retrieval and contradiction handling | skeptical RAG | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Counter-evidence retrieval and contradiction handling | counter-evidence retrieval | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Counter-evidence retrieval and contradiction handling | claim verification | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Counter-evidence retrieval and contradiction handling | contradiction detection | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Counter-evidence retrieval and contradiction handling | knowledge conflict resolution | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Counter-evidence retrieval and contradiction handling | counter-evidence retrieval | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Source trust, quality, and freshness | source-trust-aware reranking | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Source trust, quality, and freshness | freshness-aware reranking | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Source trust, quality, and freshness | Source trust scoring service | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Source trust, quality, and freshness | Source compliance registry | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Source trust, quality, and freshness | Data rights registry | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | evidence extraction before generation | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | stepwise evidence accumulation | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | claim decomposition | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | claim-evidence alignment | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | claim verification | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | entailment-based verification | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | factual consistency scoring | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | hallucination detection pós-geração | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | contradiction detection | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | knowledge conflict resolution | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | counter-evidence retrieval | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | evidence sufficiency classifier | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | answerability detection | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | abstention / refusal policy | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | selective prediction | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | uncertainty estimation | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | confidence calibration | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | conformal prediction | DIRECT_IMPLEMENTATION_NO_LIFT | -0.191 |
| Evidence sufficiency and abstention | conformal risk control | DIRECT_IMPLEMENTATION_NO_LIFT | -0.0459 |
| Evidence sufficiency and abstention | bayesian model averaging | DIRECT_IMPLEMENTATION_NO_LIFT | -0.3399 |
| Evidence sufficiency and abstention | ensemble of evaluators | DIRECT_IMPLEMENTATION_NO_LIFT | -0.3316 |
| Evidence sufficiency and abstention | model disagreement detection | DIRECT_IMPLEMENTATION_NO_LIFT | -0.4156 |
| Evidence sufficiency and abstention | source diversity enforcement | DIRECT_BENCHMARK_NO_LIFT | -0.01 |
| Evidence sufficiency and abstention | data sufficiency score | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
| Evidence sufficiency and abstention | evidence coverage score | CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE | 0.0 |
