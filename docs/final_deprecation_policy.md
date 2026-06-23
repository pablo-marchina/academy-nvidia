# Final Deprecation Policy

Deprecation removes or archives project material that no longer has a final-product role.

## Remove When

| Item | Removal trigger |
|---|---|
| tool | No active runtime, benchmark, release, or governance role remains |
| dependency | No imported runtime/test use remains or a safer equivalent is selected |
| document | It contradicts final runtime or only describes obsolete demo behavior |
| experiment | It is not promoted, not future research, and not needed for evidence |
| feature | It lacks benchmark value, owner, or operational documentation |
| endpoint | It is unused, unsupported, or superseded by a documented product API |
| old benchmark | It is contaminated, uncalibrated, or measures proxy value only |
| expired calibrated number | Recalibration trigger fires or validity period ends |
| invalid source | Robots, terms, redistribution, or storage policy becomes disallowed |
| obsolete model/reranker/embedding | A benchmarked replacement wins on output value or the provider becomes unavailable |

## Evidence

- `final_case_evidence/repository_purpose_manifest.csv`
- `final_case_evidence/runtime_bill_of_materials.csv`
- `final_case_evidence/decision_ledger.csv`
