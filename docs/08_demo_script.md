# Demo Script

> Duração estimada: 3-5 minutos.
> Cenário: Startup brasileira AI-native real submetida ao Radar.
> Formato: CLI (ou API response em terminal).

---

## Ato 1 — Apresentação (30s)

**Mensagem:** "O NVIDIA Startup AI Radar é uma plataforma de Opportunity Intelligence para o NVIDIA Inception. Ela transforma sinais públicos de startups brasileiras em um ranking acionável com scores, evidências e experimentos técnicos sugeridos."

**Tela:** Logo do projeto + descrição one-liner.

---

## Ato 2 — Input (15s)

**Ação:** Submeter nome da startup.

```bash
python -m radar.analyze --startup "StartupX" --vertical "HealthTech"
```

**Tela:** Confirmação do input + início da pipeline.

---

## Ato 3 — Pipeline em Ação (60s)

**Ação:** Mostrar o progresso da pipeline em tempo real (ou simulado, se for demo).

**Estágios exibidos:**

1. **Search Planner** — "Definindo objetivos de coleta para StartupX..."
2. **Source Search** — "Buscando fontes nível 1 e 2... [website oficial, blog, LinkedIn, imprensa]"
3. **Extractor** — "Extraindo fatos estruturados do texto cru... [fundação, equipe, produto, tecnologia]"
4. **Classifier** — "Classificando maturidade AI-native... [Nível 3 - AI-native detectado]"
5. **Evidence Validator** — "Validando 12 evidências... [8 fatos, 3 inferências, 1 hipótese]"

**Tela:** Barras de progresso ou log em tempo real para cada etapa.

---

## Ato 4 — Dual Scoring Engine (45s)

**Ação:** Exibir os scores calculados.

```
┌─────────────────────────────────────────────────┐
│               DUAL SCORING ENGINE               │
├──────────────────────┬──────────────────────────┤
│ Defensibility Score  │ Inception Fit Score       │
│       78/100         │       65/100              │
├──────────────────────┴──────────────────────────┤
│ Score Composto: 72/100 (Quality Mode: α=0.6)    │
│ Confidence: Alta (82% — 8 fontes nível 1)       │
└─────────────────────────────────────────────────┘
```

**Narração:** "Defensibility Score 78 — startup tem dados proprietários e aprendizado acumulado. Inception Fit Score 65 — gaps técnicos em inferência e latência que NVIDIA resolve bem."

---

## Ato 5 — Production AI Readiness (20s)

```
Production AI Readiness: MADURO
├── Observability: ✅ Logs de inferência em produção
├── Deployment pipeline: ✅ CI/CD para modelos
├── Model governance: ✅ Versionamento e testes
├── Quality evaluation: ✅ Métricas offline e online
├── Scalability: ⚠️ Arquitetura horizontal parcial
└── Security & compliance: ✅ LGPD implementado
```

---

## Ato 6 — Confidence-aware Ranking (20s)

**Ação:** Mostrar a posição da startup no ranking, com badge de confiança.

```
RANKING: StartupX está na posição #3 de 12
├── Confidence: Alta (82%) 🟢
├── Defensibility Rank: #2
├── Inception Fit Rank: #5
└── Comparáveis: StartupY (#2), StartupZ (#1)
```

---

## Ato 7 — NVIDIA RAG + Recomendação (30s)

**Ação:** Exibir gaps → tecnologias → justificativa.

```
GAPS IDENTIFICADOS:
1. high_inference_cost → TensorRT-LLM
   → Justificativa: StartupX processa 100k+ req/dia com LLM via API externa.
     TensorRT-LLM pode reduzir custo por token em ~70% com auto-hospedagem.
2. agent_governance_gap → NeMo Guardrails
   → Justificativa: Agente de atendimento precisa de limites de atuação
     e conformidade com LGPD.
```

---

## Ato 8 — Suggested Technical Experiment (30s)

**Ação:** Mostrar o experimento técnico sugerido em destaque.

```
┌────────────────────────────────────────────────────────────┐
│           SUGGESTED TECHNICAL EXPERIMENT                    │
├────────────────────────────────────────────────────────────┤
│ Título: Acelerar inferência com TensorRT-LLM               │
│ Gap alvo: high_inference_cost + high_latency               │
│ Hipótese: Substituir API OpenAI por TensorRT-LLM           │
│   reduz latência p75 em 60% e custo em 70%                 │
│ Métrica: Latência p75, custo por inferência, taxa de erro  │
│ Duração: 2-4 semanas                                       │
│ Tecnologia: TensorRT-LLM + Triton Inference Server          │
│ Próximo passo: Compartilhar benchmark público com CTO       │
└────────────────────────────────────────────────────────────┘
```

**Narração:** "Este é o diferencial do Radar. Não é só 'use NVIDIA' — é um experimento concreto que um engenheiro pode começar a avaliar hoje."

---

## Ato 9 — Startup Action Brief (30s)

**Ação:** Exibir o brief completo em markdown.

```markdown
# Startup Action Brief: StartupX

## Score Card
- Defensibility: 78/100 | Inception Fit: 65/100 | Composto: 72/100
- Confidence: Alta

## Classificação: Nível 3 — AI-native
O produto depende diretamente de IA para entregar valor central.

## Technical Gaps
1. high_inference_cost
2. agent_governance_gap

## NVIDIA Recommendations
1. TensorRT-LLM — Acelerar inferência LLM
2. NeMo Guardrails — Governança de agente

## Suggested Technical Experiment
Acelerar inferência com TensorRT-LLM (ver Ato 8)

## Próxima Ação
Agendar call técnica com CTO para apresentar benchmark TensorRT-LLM
e oferecer créditos NVIDIA LaunchPad para POC de 2 semanas.
```

---

## Ato 10 — Encerramento (10s)

**Mensagem final:** "StartupX está classificada como AI-native, com defensibilidade alta e fit claro com NVIDIA. O Suggested Technical Experiment é o gancho para a próxima conversa comercial. Radar completo em 3 minutos."

**Tela:** Resumo one-liner + convite para perguntas.

---

## Variações da Demo

| Variação | Quando usar |
|---|---|
| **Startup não AI-native** | Mostrar que o Radar identifica corretamente LLM-wrappers (nível 2 ou inferior) e explica o porquê |
| **Evidência insuficiente** | Mostrar Confidence-aware Ranking com badge amarelo/vermelho e sugestão de fontes adicionais |
| **Múltiplas startups** | Mostrar ranking comparativo e explicar critérios de desempate |

---

## Checklist de Preparação

- [ ] Pipeline funcional para uma startup de teste
- [ ] Output formatado em markdown e JSON
- [ ] Scores calculados com pesos padrão (α=0.6, β=0.4)
- [ ] Fontes de exemplo registradas com metadata
- [ ] Experimento técnico válido para o gap da startup escolhida
- [ ] Briefing completo com todos os campos preenchidos
- [ ] Script testado ponta-a-ponta sem falhas
