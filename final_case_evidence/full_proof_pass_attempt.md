# Full Proof PASS Attempt

Status: `FAIL`
Generated at: `2026-06-23T02:06:17.165849+00:00`
Doctor route: `blocked_no_service_route`
Recommended route: Fix Docker access or start PostgreSQL and Qdrant outside Codex, then rerun full proof.
Retry without code changes: `False`

Doctor is blocked by environment via blocked_no_service_route. Blocking checks: langgraph_import, qdrant_client_import, postgres_driver_import, docker_cli, postgres_port, postgres_connection, qdrant_port, qdrant_service, qdrant_collection, embedding_provider. Fix services or provide external PostgreSQL/Qdrant, then retry without code changes.

## Exact Commands

- `python scripts/local_proof_doctor.py`
- `docker compose up -d postgres qdrant`
- `python scripts/prove_final_product.py --full --skip-live`
- `# If Docker is blocked, start PostgreSQL/Qdrant externally and set PRODUCT_DB_URL/QDRANT_URL.`

## Proof Result

- Passed gates: `33`
- Failed gates: `1`
- Blocked by environment: `2`
- Final summary: `C:\Users\Inteli\Documents\Projetos\academy-nvidia\final_case_evidence\final_proof_summary.json`
- Doctor report: `C:\Users\Inteli\Documents\Projetos\academy-nvidia\final_case_evidence\local_proof_doctor_report.json`
