# Demo Input Samples

> **ARCHIVED:** This directory is preserved as a fixture source for integration tests. The product flow uses persisted entities, not demo sample files. The sample input file is kept for backward-compatible test use.

This directory contains sample startup input files for the CLI demo
(`scripts/run_startup_radar_demo.py`).

## Files

- `sample_startup_input.json` — Fictional HealthTech AI-native startup "Nexus AI Labs"

## Format

Each input file contains:

| Field | Required | Description |
|---|---|---|
| `startup_name` | yes | Name of the startup |
| `description` | no | Free-text description (for metadata only) |
| `source_url` | no | Fictional source URL |
| `metadata` | no | Tracking metadata (schema version, generation timestamp) |
| `profile` | yes | Structured profile (sector, description, signals, etc.) |
| `evidence` | yes | List of evidence claims with confidence levels |

## Rules

- All startups in this directory are **fictional**.
- No real company data is used without explicit evidence.
- Inputs follow the same schema as the golden eval cases in `examples/golden/`.

## Adding a new sample

1. Copy `sample_startup_input.json` to a new file.
2. Replace `startup_name`, `profile`, and `evidence`.
3. Update `metadata.description` to indicate the startup is fictional.
4. Run the CLI:
   ```bash
   python scripts/run_startup_radar_demo.py --input examples/demo/your_input.json
   ```
