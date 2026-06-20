# Evidence Contract

## Modules
- `src/extraction/schemas.py` — `Evidence`, `SourceType`, `ConfidenceLevel`
- `src/validation/evidence_validator.py` — `ValidatedEvidence`, `EvidenceKind`

## What Evidence Is

A piece of information about a startup with:
- Source URL (must be reachable and policy-compliant)
- Source type (`official_site`, `news`, `blog`, `social_media`, `technical_doc`, `other`)
- Claim (what the evidence asserts)
- Quote or evidence (verbatim text supporting the claim)
- Confidence (`HIGH`, `MEDIUM`, `LOW`)
- Collection timestamp

## Evidence Lifecycle

```
Raw text → Extraction → Evidence (with initial confidence)
                                          ↓
                              Evidence Validator
                                          ↓
                              ValidatedEvidence
                              (with evidence_kind + recalibrated confidence)
```

## Evidence Kind Tags

| Tag | Meaning |
|-----|---------|
| `FACT` | Direct, verifiable quote from official source |
| `STRONG_INFERENCE` | Strong indirect signal (e.g., job posting for ML engineers) |
| `WEAK_INFERENCE` | Weak indirect signal (e.g., mentions "AI" in marketing) |
| `HYPOTHESIS` | No direct evidence, but plausible based on context |
| `UNVERIFIED` | Source cannot be accessed or validated |

## What This Contract Requires

1. Every `Evidence` must have a `source_url`
2. Every `ValidatedEvidence` must trace back to an `Evidence`
3. `evidence_kind` is assigned by the validator, not by extraction
4. Confidence can be recalibrated down but never up during validation
5. Evidence without a verifiable source is `UNVERIFIED`

## Final Product Readiness Update - 2026-06-19

Product analysis requires persisted, source-backed evidence. Mock, sample, fixture, synthetic, or placeholder evidence is limited to tests and cannot satisfy product readiness. Product outputs must keep evidence provenance visible and classify every downstream claim as fact, inference, hypothesis, or unverified so recommendations never appear more certain than the source trail supports.

## Contract Version
1.0 — June 2026
