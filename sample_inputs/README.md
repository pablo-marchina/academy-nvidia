# Sample Inputs

## Policy

Sample inputs in this directory are **controlled test/demo data only**. They are:

- Used for manual demonstration and smoke testing
- Never used as automatic fallback in the product flow
- Never stored in `data/demo_runs/`
- Never loaded by the product API or UI without explicit user action

## How to Use

To load a sample startup manually via the API:

```bash
curl -X POST http://localhost:8000/startups \
  -H "Content-Type: application/json" \
  -d @sample_inputs/<file.json>
```

To use in the CLI demo (legacy):

```bash
python scripts/run_startup_radar_demo.py --input sample_inputs/<file.json>
```

## Difference Between Fixture, Sample Input, and Demo Data

| Type | Location | Purpose | Loaded by product? |
|---|---|---|---|
| Test fixture | `tests/fixtures/` | Automated tests | No |
| Sample input | `sample_inputs/` | Manual demo | Only via explicit API call |
| Demo data (legacy) | `data/demo_runs/` | Removed (Epic 31) | Never |
