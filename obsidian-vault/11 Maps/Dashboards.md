```dataview
TABLE sector, ai_level, confidence, sources_count, last_reviewed
FROM "03 Research/Startups"
WHERE type = "startup"
SORT confidence DESC
```

```dataview
TABLE startup, claim, source_type, confidence
FROM "07 Evidence"
WHERE type = "evidence" AND confidence = "low"
```

```dataview
TABLE date, area, status
FROM "04 Decisions"
WHERE type = "decision"
SORT date DESC
```

## Regression Dashboard

- Local output: `data/regression_reports/latest_dashboard.md`
- JSON output: `data/regression_reports/latest_dashboard.json`
- Command: `make regression-dashboard`
- CI: appended to GitHub Actions Job Summary in `corpus-maintenance.yml`
