# Final Security Risk Plan

The final product treats external content as untrusted input.

Required controls:

- Prompt injection and source poisoning checks for external documents
- Secret scanning and dependency scanning before release
- Source compliance and data rights registry
- Tool and agent audit coverage when MCP/tools are active
- No arbitrary shell or unscoped filesystem access in product workflows
- Human approval for critical write actions when tool orchestration is active
- Incident records for recommendation-without-evidence, prompt injection,
  source poisoning, secret exposure, tool policy violation, RAG quality drop,
  NVIDIA mapping error, temporal leakage, and data rights violation

Final security evidence is stored under `final_case_evidence/`.
