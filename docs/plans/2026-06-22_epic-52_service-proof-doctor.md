# Epic 52: Service Proof Doctor e Rota PASS com Servicos Externos

## Summary

Adicionar um diagnostico local antes do `prove-final-product --full` para separar bloqueios de ambiente de falhas reais do produto. O full proof deve continuar preferindo Docker Compose, mas deve aceitar PostgreSQL e Qdrant ja rodando por env vars quando o Docker estiver bloqueado.

## Key Changes

- Criar `scripts/local_proof_doctor.py` para verificar Docker, leitura do config Docker, portas, Postgres, Qdrant, Alembic, corpus NVIDIA, modelo de embedding e env vars criticas.
- Integrar o doctor ao `scripts/prove_final_product.py --full`, com `--skip-doctor`, `--external-services-ok` e `--require-docker-compose`.
- Fortalecer `scripts/real_service_proof.py` para prosseguir com servicos externos acessiveis mesmo quando o auto-start Docker falhar, mantendo `BLOCKED_BY_ENVIRONMENT` quando nenhum caminho real estiver disponivel.
- Gerar `final_case_evidence/local_proof_doctor_report.json` e propagar o resultado para os reports agregados.
- Documentar a operacao local em Windows/Docker Desktop e o uso de servicos externos.

## Test Plan

- Unit tests para classificacao do doctor e shape do JSON.
- Unit tests para agregacao de full proof com Docker bloqueado, servicos externos acessiveis e ausencia total de servicos.
- CLI tests para `scripts/local_proof_doctor.py`.
- Validacao focada com quick proof, full proof sem live, pytest, ruff, black e mypy nos modulos tocados.

## Assumptions

- Nenhum dado local, volume, banco ou colecao sera apagado.
- Docker e o caminho preferencial, mas nao obrigatorio quando Postgres e Qdrant reais ja estiverem acessiveis.
- Ambientes bloqueados devem gerar evidencia objetiva e acionavel, nunca falso PASS.
