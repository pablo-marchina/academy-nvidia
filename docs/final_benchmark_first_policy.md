# Final Benchmark-First Policy

The canonical roadmap is `final_final_benchmark_first_roadmap_all_changes.md`.

Every technology, technique, tool, module, endpoint, document, dependency, and
dataset must have one status:

- `DOCUMENTED_CANDIDATE`
- `BENCHMARK_CONFIGURED`
- `BENCHMARKED`
- `PROMOTED_TO_RUNTIME`
- `REJECTED_BY_EVIDENCE`
- `REMOVED_UNUSED`
- `FUTURE_RESEARCH`

Candidates may not be promoted because they are fashionable, complex, local, or
listed in the roadmap. They require measurable product output value,
traceability, configuration, tests, cost/latency/risk evidence, and
documentation.

The selection rule is value-first: within each technology family, choose the
candidate that produces the highest measured output-quality lift after
accounting for cost, latency, risk, governance, and reproducibility. A local
implementation is acceptable only when it wins or when it is the best available
benchmark proxy. Local-first is not an absolute preference.

Free external APIs or services are allowed as benchmark candidates when all of
these are true:

- the free tier is usable for the product's benchmark workload;
- the benchmark path is documented in the candidate metadata;
- no paid credential, private license, hardware, or hidden manual step is
  required;
- secrets are provided only through environment variables when needed;
- local tests still pass with null providers, skips, or explicit
  `BLOCKED_BY_ENVIRONMENT` evidence;
- source terms, robots, rate limits, and data rights are respected.

The canonical registry for these candidates is
`docs/free_external_candidate_registry.json`. The registry has three important
effects:

- only `FREE_EXTERNAL_BENCHMARKABLE` entries may enter the ranked benchmark
  queue as executable external candidates;
- `NEEDS_FREE_TIER_VERIFICATION` entries stay blocked until current no-cost
  terms, rate limits, credentials, and data rights are documented;
- registry eligibility is never runtime promotion. Promotion still requires a
  direct benchmark, output-quality lift, cost/latency/risk evidence, and a
  decision-ledger entry.

If a candidate requires unavailable paid SaaS, hardware, license, private access,
or paid credentials, a local or free substitute may benchmark the category. That
substitute does not promote the original candidate. The original remains
blocked, documented, or future research until direct evidence exists.

This policy also applies to existing runtime components. A runtime component is
kept only while its evidence shows it is required, currently best, or not yet
beaten by a higher-value alternative. Runtime choices must be re-benchmarked
against viable local and free external/API alternatives when a family has
credible output-quality headroom. Replacement requires direct evidence that the
alternative improves product output after cost, latency, risk, governance,
reproducibility, and operational complexity are accounted for.
