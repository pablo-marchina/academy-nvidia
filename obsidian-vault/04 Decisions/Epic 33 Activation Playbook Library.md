# Decision 040 — Activation Playbook YAML Source

- **Epic:** 33
- **Date:** 2026-06-12
- **Context:** Fonte de verdade para 10 playbooks de ativação NVIDIA. Playbooks mudam com frequência.
- **Decision:** YAML em `src/config/playbooks/nvidia_activation_playbooks.yaml`.
- **Alternatives:** DB-first (rejeitado — versionamento via git é mais simples), JSON (rejeitado — YAML mais legível).
- **Validation:** 13 testes de loader (YAML válido, vazio, duplicado, campos ausentes, motions inválidos).

# Decision 041 — Activation Matching Determinístico v1

- **Epic:** 33
- **Date:** 2026-06-12
- **Context:** Playbooks precisam fazer match com gaps detectados.
- **Decision:** Matching determinístico: playbook matcha se target_gap_type contém gap detectado.
- **Alternatives:** LLM matching (rejeitado — custo, não-determinismo na v1), embedding similarity (rejeitado — overkill para 10 playbooks).
- **Validation:** 9 testes de matcher (match por gap, sem gap, gap não detectado, confidence boost/penalty, prioridade).

# Decision 042 — Activation Confidence por Fórmula Fixa

- **Epic:** 33
- **Date:** 2026-06-12
- **Context:** Recomendações precisam de confidence para priorização.
- **Decision:** Fórmula fixa: avg(gap_confidences) + boosts - penalties, clamped [0,1].
- **Alternatives:** ML model (rejeitado — sem dados históricos), regressão (rejeitado — complexidade desnecessária).
- **Validation:** Testes unitários cobrindo boost com mapping, penalty com unsupported claims, prioridade ordenada.

# Decision 043 — Idempotência via replace_recommendations_for_analysis_run

- **Epic:** 33
- **Date:** 2026-06-12
- **Context:** Geração de recomendações pode ser chamada múltiplas vezes.
- **Decision:** Delete all + bulk create na mesma transação.
- **Alternatives:** Upsert (rejeitado — deixaria órfãos se playbook for removido).
- **Validation:** Teste de integração verifica idempotência: duas chamadas POST geram mesmo número de recomendações.
