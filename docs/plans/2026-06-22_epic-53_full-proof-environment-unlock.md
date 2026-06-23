# Epic 53: Full Proof Environment Unlock

## Summary

Transformar o bloqueio atual do `prove-final-product --full` em uma tentativa operacional reproduzivel de PASS. O codigo e os gates locais estao verdes, mas o ambiente ainda nao oferece uma rota real para PostgreSQL e Qdrant: Docker engine esta inacessivel e os servicos nao estao ouvindo em localhost.

## Key Changes

- Enriquecer o `local_proof_doctor` com rota recomendada, comandos exatos, resumo humano e flags de retry sem mudanca de codigo.
- Criar um comando de tentativa de PASS que roda doctor, sobe servicos via Docker Compose quando disponivel, aceita servicos externos ja rodando e entao executa o full proof.
- Escrever `final_case_evidence/full_proof_pass_attempt.md` como resumo operacional final.
- Fazer o `final_proof_summary.json` apontar diretamente para o doctor quando a prova final for bloqueada por ambiente.
- Documentar as duas rotas oficiais: Docker Compose local e servicos externos via env vars.

## Test Plan

- Unit tests para selecao de rota, campos novos do doctor e resumo humano.
- Unit tests para tentativa de PASS com Docker bloqueado, Docker disponivel, servicos externos disponiveis e full proof PASS.
- Validar doctor, quick proof, full proof sem live, pytest focado, ruff, black e mypy.

## Assumptions

- Nenhum commit automatico.
- Nenhum volume, banco ou colecao sera apagado.
- Se o ambiente continuar bloqueado, o resultado correto continua sendo `BLOCKED_BY_ENVIRONMENT`, mas com comandos de remediacao e evidencia limpa.
