# Local Proof Doctor

Status: `BLOCKED_BY_ENVIRONMENT`
Effective route: `blocked_no_service_route`
Recommended route: Fix Docker access or start PostgreSQL and Qdrant outside Codex, then rerun full proof.
Environment fix required: `True`
Can retry without code changes: `True`

Doctor is blocked by environment via blocked_no_service_route. Blocking checks: langgraph_import, qdrant_client_import, postgres_driver_import, docker_cli, postgres_port, postgres_connection, qdrant_port, qdrant_service, qdrant_collection, embedding_provider. Fix services or provide external PostgreSQL/Qdrant, then retry without code changes.

## Exact Commands

- `python scripts/local_proof_doctor.py`
- `docker compose up -d postgres qdrant`
- `python scripts/prove_final_product.py --full --skip-live`
- `# If Docker is blocked, start PostgreSQL/Qdrant externally and set PRODUCT_DB_URL/QDRANT_URL.`

## Blocking Checks

- `langgraph_import`: Install missing dependency with `pip install -e .[agents]`.
- `qdrant_client_import`: Install missing dependency with `pip install -e .[rag]`.
- `postgres_driver_import`: Install missing dependency with `pip install -e .[postgres]`.
- `docker_cli`: Start Docker Desktop and confirm the current user can access the Docker engine., On Windows, verify access to npipe:////./pipe/docker_engine.
- `postgres_port`: Start the service listening on localhost:5432 or update the env var for this endpoint.
- `postgres_connection`: Install backend dependencies with `pip install -e .[postgres]` or `pip install -e .[full]`.
- `qdrant_port`: Start the service listening on localhost:6333 or update the env var for this endpoint.
- `qdrant_service`: Start Qdrant locally or set QDRANT_URL to a reachable Qdrant instance.
- `qdrant_collection`: Make Qdrant reachable before validating or ingesting the configured collection.
- `embedding_provider`: Install the RAG extra or package: `pip install -e .[rag]`.
