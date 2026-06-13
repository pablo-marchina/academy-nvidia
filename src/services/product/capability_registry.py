"""Central registry of product capabilities.

Each capability tracks its status, dependencies, and configuration
requirements. The registry is the single source of truth for what
the product can do and why a feature might be unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CapabilityStatus(str, Enum):
    available = "available"
    unavailable = "unavailable"
    not_configured = "not_configured"
    missing_dependency = "missing_dependency"
    degraded = "degraded"
    disabled = "disabled"
    experimental = "experimental"


class CapabilityCategory(str, Enum):
    core = "core"
    database = "database"
    rag = "rag"
    evidence = "evidence"
    claims = "claims"
    playbooks = "playbooks"
    dossier = "dossier"
    quality = "quality"
    structured_outputs = "structured_outputs"
    llm_judge = "llm_judge"
    export = "export"
    frontend = "frontend"
    developer_tools = "developer_tools"


@dataclass
class CapabilityDefinition:
    capability_id: str
    name: str
    description: str
    category: CapabilityCategory
    required: bool = False
    enabled_by_default: bool = True
    required_env_vars: list[str] = field(default_factory=list)
    optional_env_vars: list[str] = field(default_factory=list)
    required_extras: list[str] = field(default_factory=list)
    required_services: list[str] = field(default_factory=list)
    health_check_key: str = ""
    setup_instructions: str = ""
    failure_mode: str = ""
    user_visible: bool = True
    documentation_ref: str = ""


CAPABILITIES: dict[str, CapabilityDefinition] = {}


def _reg(*, category: CapabilityCategory, **kwargs: Any) -> CapabilityDefinition:
    cd = CapabilityDefinition(category=category, **kwargs)
    CAPABILITIES[cd.capability_id] = cd
    return cd


# ---------------------------------------------------------------------------
# Core / Product
# ---------------------------------------------------------------------------
_reg(
    capability_id="product_api",
    name="Product API",
    description="REST API for product operations (startups, analysis runs, reviews)",
    category=CapabilityCategory.core,
    required=True,
    setup_instructions="Run the FastAPI app with uvicorn.",
    documentation_ref="docs/contracts/product_api_contract.md",
)
_reg(
    capability_id="product_database",
    name="Product Database",
    description="Transactional SQLite/PostgreSQL database for product records",
    category=CapabilityCategory.core,
    required=True,
    required_env_vars=["PRODUCT_DB_URL"],
    setup_instructions="Set PRODUCT_DB_URL (default: sqlite:///data/product/product.db).",
    health_check_key="product_db",
    documentation_ref="docs/contracts/product_api_contract.md",
)
_reg(
    capability_id="startup_management",
    name="Startup Management",
    description="CRUD operations for startup profiles",
    category=CapabilityCategory.core,
    required=True,
    setup_instructions="Available once product_database is configured.",
)
_reg(
    capability_id="analysis_run_lifecycle",
    name="Analysis Run Lifecycle",
    description="Create, track, and retrieve analysis runs with pipeline outputs",
    category=CapabilityCategory.core,
    required=True,
    setup_instructions="Available once product_database is configured.",
)
_reg(
    capability_id="opportunities",
    name="Opportunities",
    description="Ranked list of startup opportunities with scoring and review status",
    category=CapabilityCategory.core,
    required=True,
    setup_instructions="Available once product_database is configured.",
)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
_reg(
    capability_id="sqlite_product_db",
    name="SQLite Product DB",
    description="Local SQLite database for product records (default backend)",
    category=CapabilityCategory.database,
    required=True,
    enabled_by_default=True,
    setup_instructions="Set PRODUCT_DB_URL=sqlite:///data/product/product.db (default).",
)
_reg(
    capability_id="postgres_validation_optional",
    name="PostgreSQL Validation (Optional)",
    description="Optional PostgreSQL backend validation via integration tests",
    category=CapabilityCategory.database,
    required=False,
    enabled_by_default=False,
    required_env_vars=["PRODUCT_DB_TEST_URL"],
    setup_instructions="Set PRODUCT_DB_TEST_URL for PostgreSQL integration tests.",
)
_reg(
    capability_id="alembic_migrations",
    name="Alembic Migrations",
    description="Database schema migrations via Alembic",
    category=CapabilityCategory.database,
    required=True,
    setup_instructions="Run `alembic upgrade head` to apply migrations.",
)

# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------
_reg(
    capability_id="qdrant_vector_store",
    name="Qdrant Vector Store",
    description="Persistent vector store for NVIDIA corpus retrieval",
    category=CapabilityCategory.rag,
    required=False,
    required_env_vars=["QDRANT_URL", "QDRANT_COLLECTION"],
    optional_env_vars=["QDRANT_API_KEY", "QDRANT_VECTOR_SIZE"],
    required_services=["Qdrant server"],
    setup_instructions="Set QDRANT_URL and QDRANT_COLLECTION. Start Qdrant via docker-compose.",
    health_check_key="qdrant",
    documentation_ref="docs/39_qdrant_persistent_vector_store.md",
)
_reg(
    capability_id="sentence_transformer_embeddings",
    name="Sentence Transformer Embeddings",
    description="Embedding provider using sentence-transformers",
    category=CapabilityCategory.rag,
    required=False,
    required_extras=["rag"],
    required_env_vars=["RAG_EMBEDDING_MODEL"],
    setup_instructions="Install with `pip install -e .[rag]` and set RAG_EMBEDDING_MODEL.",
    failure_mode="Falls back to MockEmbeddingProvider for deterministic embeddings.",
)
_reg(
    capability_id="rag_retrieval",
    name="RAG Retrieval",
    description="Lexical, semantic, and hybrid retrieval from NVIDIA corpus",
    category=CapabilityCategory.rag,
    required=False,
    setup_instructions=(
        "RAG works with in-memory index by default; " "Qdrant and embeddings are optional."
    ),
    health_check_key="rag",
    documentation_ref="docs/35_product_rag_design.md",
)

# ---------------------------------------------------------------------------
# Evidence / Claims
# ---------------------------------------------------------------------------
_reg(
    capability_id="evidence_records",
    name="Evidence Records",
    description="Persisted startup evidence with source tracking",
    category=CapabilityCategory.evidence,
    required=True,
    setup_instructions="Available once product_database is configured.",
)
_reg(
    capability_id="claim_ledger",
    name="Claim Ledger",
    description="Deterministic claim generation and evidence-to-claim linkage",
    category=CapabilityCategory.claims,
    required=True,
    setup_instructions="Available once product_database is configured.",
    documentation_ref="docs/58_evidence_claim_ledger.md",
)
_reg(
    capability_id="evidence_coverage",
    name="Evidence Coverage",
    description="Ratio of supported to total claims per analysis run",
    category=CapabilityCategory.claims,
    required=True,
    setup_instructions="Available once claim_ledger is configured.",
)
_reg(
    capability_id="unsupported_claim_detection",
    name="Unsupported Claim Detection",
    description="Identifies claims without sufficient evidence support",
    category=CapabilityCategory.claims,
    required=True,
    setup_instructions="Available once claim_ledger is configured.",
)

# ---------------------------------------------------------------------------
# Activation / Playbooks
# ---------------------------------------------------------------------------
_reg(
    capability_id="nvidia_activation_playbooks",
    name="NVIDIA Activation Playbooks",
    description="YAML-defined playbook library for activation motions",
    category=CapabilityCategory.playbooks,
    required=True,
    setup_instructions="Playbooks are loaded from data/nvidia_corpus/playbooks/ at startup.",
    documentation_ref="docs/59_activation_playbook_library.md",
)
_reg(
    capability_id="activation_recommendations",
    name="Activation Recommendations",
    description="Deterministic playbook matching and recommendation generation",
    category=CapabilityCategory.playbooks,
    required=True,
    setup_instructions="Available once playbooks are loaded and analysis run exists.",
)

# ---------------------------------------------------------------------------
# Dossier
# ---------------------------------------------------------------------------
_reg(
    capability_id="startup_activation_dossier",
    name="Startup Activation Dossier",
    description="Comprehensive JSON dossier with scores, gaps, claims, and readiness",
    category=CapabilityCategory.dossier,
    required=True,
    setup_instructions="Available once analysis run is completed.",
    documentation_ref="docs/60_startup_activation_dossier.md",
)
_reg(
    capability_id="dossier_markdown",
    name="Dossier Markdown",
    description="Human-readable markdown rendering of the activation dossier",
    category=CapabilityCategory.dossier,
    required=True,
    setup_instructions="Available once startup_activation_dossier is generated.",
)
_reg(
    capability_id="dossier_json",
    name="Dossier JSON Export",
    description="Raw JSON export of the activation dossier",
    category=CapabilityCategory.dossier,
    required=True,
    setup_instructions="Available once startup_activation_dossier is generated.",
)

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------
_reg(
    capability_id="product_quality_layer",
    name="Product Quality Layer",
    description="Deterministic quality evaluation for analysis runs",
    category=CapabilityCategory.quality,
    required=True,
    setup_instructions="Available once product_database is configured.",
    documentation_ref="docs/61_product_quality_layer.md",
)
_reg(
    capability_id="deterministic_quality_metrics",
    name="Deterministic Quality Metrics",
    description="Evidence coverage, dossier completeness, playbook actionability, etc.",
    category=CapabilityCategory.quality,
    required=True,
    setup_instructions="Available once product_quality_layer is configured.",
)
_reg(
    capability_id="optional_ragas_trial",
    name="Ragas Trial (Optional)",
    description="Optional RAGAS evaluation integration (future)",
    category=CapabilityCategory.quality,
    required=False,
    enabled_by_default=False,
    required_extras=["eval"],
    setup_instructions="Install with `pip install -e .[eval]` and configure ENABLE_RAGAS_TRIAL.",
    failure_mode="Not configured; quality gates use deterministic metrics only.",
)
_reg(
    capability_id="optional_deepeval_trial",
    name="DeepEval Trial (Optional)",
    description="Optional DeepEval evaluation integration (future)",
    category=CapabilityCategory.quality,
    required=False,
    enabled_by_default=False,
    required_extras=["eval"],
    setup_instructions="Install with `pip install -e .[eval]` and configure ENABLE_DEEPEVAL_TRIAL.",
    failure_mode="Not configured; quality gates use deterministic metrics only.",
)

# ---------------------------------------------------------------------------
# Structured Outputs
# ---------------------------------------------------------------------------
_reg(
    capability_id="pydantic_structured_output_adapter",
    name="Pydantic Structured Output Adapter",
    description="Validation and repair layer for all structured outputs",
    category=CapabilityCategory.structured_outputs,
    required=True,
    setup_instructions="Built-in; no additional configuration needed.",
    documentation_ref="docs/62_structured_output_reliability.md",
)
_reg(
    capability_id="structured_output_trace",
    name="Structured Output Trace",
    description="Retry count, repair status, validation errors, and latency tracking",
    category=CapabilityCategory.structured_outputs,
    required=True,
    setup_instructions="Built-in; available when pydantic_structured_output_adapter is active.",
)
_reg(
    capability_id="optional_instructor_trial",
    name="Instructor Trial (Optional)",
    description="Optional instructor library for LLM structured output parsing",
    category=CapabilityCategory.structured_outputs,
    required=False,
    enabled_by_default=False,
    required_extras=["llm-judge"],
    setup_instructions=(
        "Install with `pip install -e .[llm-judge]` and configure " "ENABLE_INSTRUCTOR_TRIAL=true."
    ),
    failure_mode="Not installed; LLM Judge uses NullLLMJudgeProvider (deterministic offline).",
)

# ---------------------------------------------------------------------------
# LLM Judge
# ---------------------------------------------------------------------------
_reg(
    capability_id="optional_llm_judge",
    name="LLM Judge (Optional)",
    description="Optional LLM-based answer quality evaluation",
    category=CapabilityCategory.llm_judge,
    required=False,
    enabled_by_default=False,
    required_env_vars=["ANSWER_QUALITY_LLM_JUDGE_ENABLED"],
    setup_instructions=(
        "Set ANSWER_QUALITY_LLM_JUDGE_ENABLED=true and choose a provider " "(default: null)."
    ),
    failure_mode="Disabled by default; deterministic NullLLMJudgeProvider used.",
    documentation_ref="docs/48_optional_llm_judge.md",
)
_reg(
    capability_id="optional_openai_structured_outputs",
    name="OpenAI Structured Outputs (Optional)",
    description="Future OpenAI structured output support",
    category=CapabilityCategory.llm_judge,
    required=False,
    enabled_by_default=False,
    required_env_vars=["OPENAI_API_KEY"],
    setup_instructions="Set OPENAI_API_KEY. Requires future provider abstraction.",
    failure_mode="Not implemented; instructor trial is the current approach.",
)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
_reg(
    capability_id="json_export",
    name="JSON Export",
    description="Export analysis outputs as JSON files",
    category=CapabilityCategory.export,
    required=True,
    setup_instructions="Available once analysis run is completed.",
)
_reg(
    capability_id="markdown_export",
    name="Markdown Export",
    description="Export analysis outputs as Markdown files",
    category=CapabilityCategory.export,
    required=True,
    setup_instructions="Available once analysis run is completed.",
)

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
_reg(
    capability_id="frontend_workspace",
    name="Frontend Workspace (Optional)",
    description="React + Vite + TypeScript demo UI",
    category=CapabilityCategory.frontend,
    required=False,
    enabled_by_default=False,
    setup_instructions="Run `cd frontend && npm install && npm run dev`.",
    failure_mode="Not built or served; API-only mode works without it.",
)

# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
_reg(
    capability_id="startup_discovery",
    name="Startup Discovery Engine",
    description=(
        "Multi-source discovery of AI-native Brazilian startups" " with signal detection and dedup"
    ),
    category=CapabilityCategory.core,
    required=False,
    setup_instructions="Available once product_database is configured.",
    failure_mode=(
        "Manual seed discovery works without external sources;"
        " URL list discovery requires httpx."
    ),
)
_reg(
    capability_id="discovery_sources",
    name="Discovery Source Registry",
    description=(
        "Configurable registry of discovery sources" " (manual, URL list, incubators, accelerators)"
    ),
    category=CapabilityCategory.core,
    required=False,
    setup_instructions="Sources defined in src/config/discovery_sources.json.",
)
_reg(
    capability_id="ai_native_signal_detection",
    name="AI-Native Signal Detection",
    description="Keyword-based detection of AI-native signals (AI, IA, LLM, GPU, CUDA, TensorRT)",
    category=CapabilityCategory.core,
    required=False,
    setup_instructions="Built into discovery module; no external dependencies required.",
)
_reg(
    capability_id="candidate_promotion",
    name="Candidate to Startup Promotion",
    description="Promote discovered candidates to Startup records with evidence migration",
    category=CapabilityCategory.core,
    required=False,
    setup_instructions="Available once discovery engine and product_database are configured.",
)

# ---------------------------------------------------------------------------
# Developer Tools
# ---------------------------------------------------------------------------
_reg(
    capability_id="check_scope",
    name="Scope Check Script",
    description="Detects sensitive area changes requiring contract/doc updates",
    category=CapabilityCategory.developer_tools,
    required=False,
    setup_instructions="Run `python scripts/check_scope.py` before commit.",
)
_reg(
    capability_id="check_docs_closure",
    name="Docs Closure Check Script",
    description="Verifies plan, ROADMAP, EVALS, Obsidian before epic close",
    category=CapabilityCategory.developer_tools,
    required=False,
    setup_instructions="Run `python scripts/check_docs_closure.py` before epic close.",
)
_reg(
    capability_id="pytest_validation",
    name="Pytest Validation",
    description="Run unit, integration, and eval tests",
    category=CapabilityCategory.developer_tools,
    required=False,
    setup_instructions="Run `pytest` or `make test`.",
)
_reg(
    capability_id="ruff_black_mypy",
    name="Ruff / Black / MyPy",
    description="Linting, formatting, and type checking",
    category=CapabilityCategory.developer_tools,
    required=False,
    setup_instructions="Run `ruff check .`, `black --check .`, `mypy src`.",
)


def get_capability(capability_id: str) -> CapabilityDefinition | None:
    return CAPABILITIES.get(capability_id)


def list_capabilities() -> list[CapabilityDefinition]:
    return list(CAPABILITIES.values())


def list_capabilities_by_category(
    category: CapabilityCategory,
) -> list[CapabilityDefinition]:
    return [c for c in CAPABILITIES.values() if c.category == category]


def get_required_capabilities() -> list[CapabilityDefinition]:
    return [c for c in CAPABILITIES.values() if c.required]


def get_optional_capabilities() -> list[CapabilityDefinition]:
    return [c for c in CAPABILITIES.values() if not c.required]


def get_capabilities_requiring_extras() -> list[CapabilityDefinition]:
    return [c for c in CAPABILITIES.values() if c.required_extras]
