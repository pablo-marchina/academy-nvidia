"""Runs ALL catalog techniques dynamically from the maximal CSV catalog.

Each technique is a module in src/rag/ with a class that has a
``run(contexts, **kwargs)`` method.

The pipeline order is now governed by the canonical candidate catalog
at ``candidate_catalog_maximal_final_complementary_governed(1).csv``.
Modules that exist in ``src/rag/`` but are NOT in the catalog are skipped.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from src.governance.runtime_catalog import RuntimeCatalog
from src.rag.schemas import RetrievedContext, TechniquesConfig

_RAG_DIR = Path(__file__).resolve().parent


def _discover_catalog_modules() -> list[str]:
    """Discover all .py files in src/rag/ that correspond to CSV catalog entries."""
    catalog = RuntimeCatalog.get_instance()
    if not catalog.is_loaded:
        catalog.load()

    csv_module_names: set[str] = set()
    for entry in catalog.all_entries:
        mod_name = catalog.module_for_candidate(entry.candidate_id)
        if mod_name:
            csv_module_names.add(mod_name)

    _INFRA = {
        "__init__",
        "schemas",
        "nvidia_client",
        "rag_service_factory",
        "rag_pipeline",
        "ingestion_pipeline",
        "technique_runner",
    }
    existing_modules = {path.stem for path in _RAG_DIR.glob("*.py") if path.stem not in _INFRA}

    return sorted(csv_module_names & existing_modules)


# Discover modules once at import time
CATALOG_PIPELINE: list[str] = _discover_catalog_modules()

MANUAL_CLASS_NAMES: dict[str, str] = {
    "adaptive_rag": "AdaptiveRAG",
    "skeptical_rag": "SkepticalRAG",
    "iterative_retrieval": "IterativeRetrieval",
    "multi_hop_retrieval": "MultiHopRetrieval",
    "active_retrieval": "ActiveRetrieval",
    "parent_child_retrieval": "ParentChildRetrieval",
    "contextual_retrieval": "ContextualRetrieval",
    "long_context_rag": "LongContextRAG",
    "hierarchical_summarization": "HierarchicalSummarization",
    "contextual_compression": "ContextualCompression",
    "semantic_chunking": "SemanticChunking",
    "counter_evidence": "CounterEvidenceRetrieval",
    "fusion_retrieval": "FusionRetrieval",
    "meta_retrieval": "MetaRetrieval",
    "hybrid_search": "HybridSearch",
    "listwise_reranking": "ListwiseReranker",
    "llm_reranking": "LLMReranker",
    "neural_reranking": "NeuralReranker",
    "pointwise_reranking": "PointwiseReranker",
    "factual_consistency": "FactualConsistencyScorer",
    "hallucination_detection": "HallucinationDetector",
    "contradiction_detection": "ContradictionDetector",
    "uncertainty_estimation": "UncertaintyEstimator",
    "confidence_calibration": "ConfidenceCalibrator",
    "conformal_prediction": "ConformalPredictor",
    "probabilistic_evidence": "ProbabilisticEvidenceScorer",
    "schema_linking": "SchemaLinker",
    "graph_consistency": "GraphConsistencyChecker",
    "truth_maintenance": "TruthMaintenanceSystem",
    "table_to_graph": "TableToGraphExtractor",
    "case_based_reasoning": "CaseBasedReasoner",
    "react_agent": "ReActAgent",
    "self_consistency": "SelfConsistency",
    "document_layout": "DocumentLayoutParser",
    "table_aware_rag": "TableAwareRAG",
    "pdf_layout": "PDFLayoutParser",
    "multimodal_ingestion": "MultimodalIngestion",
    "chart_understanding": "ChartUnderstanding",
    "visual_document": "VisualDocumentRetriever",
    "page_image": "PageImageAnalyzer",
    "learning_to_rank": "LearningToRank",
    "recommendation_system": "RecommendationSystem",
    "value_of_information": "ValueOfInformation",
    "expected_utility": "ExpectedUtility",
    "bayesian_scoring": "BayesianScorer",
    "prompt_injection": "PromptInjectionDetector",
    "data_poisoning": "DataPoisoningDetector",
    "context_firewall": "ContextFirewall",
    "source_trust": "SourceTrustScorer",
    "least_context": "LeastContextRetriever",
    "structured_outputs": "StructuredOutputGenerator",
    "context_registry": "ContextRegistry",
    "prompt_registry": "PromptRegistry",
    "token_budgeter": "TokenBudgeter",
    "prompt_assembler": "PromptAssembler",
    "query_intent": "QueryIntentClassifier",
    "retrieval_budget": "RetrievalBudgetAllocator",
    "multi_hop_graph": "MultiHopGraphTraverser",
}


def _to_title(snake: str) -> str:
    return MANUAL_CLASS_NAMES.get(snake, "".join(p.capitalize() for p in snake.split("_")))


def run_techniques(
    contexts: list[RetrievedContext],
    config: TechniquesConfig | None = None,
    **kwargs: Any,
) -> list[RetrievedContext]:
    """Run all catalog-discovered techniques, passing contexts through each."""
    cfg = config or TechniquesConfig()
    if not contexts:
        return contexts

    for mod_name in CATALOG_PIPELINE:
        config_attr = mod_name
        if not getattr(cfg, config_attr, True):
            continue

        try:
            mod = importlib.import_module(f"src.rag.{mod_name}")
            class_name = _to_title(mod_name)
            cls = getattr(mod, class_name, None)
            if cls is None:
                continue
            instance = cls()
            result = instance.run(contexts, **kwargs)
            if result is not None:
                contexts = result
        except Exception:
            pass

    return contexts
