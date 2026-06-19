# Testing Rules — NVIDIA Startup AI Radar

## Validação Mínima Backend
```bash
pytest                          # todos os testes
ruff check .                    # linter
black --check .                 # formatação
mypy src                        # checagem de tipos
```

## Validação Mínima Frontend
```bash
cd frontend && npm run lint     # linter frontend
cd frontend && npm run build    # build frontend
```

## Integração com PostgreSQL / Qdrant / Redis
```bash
pytest tests/integration/       # testes de integração
docker compose up -d            # sobe dependências (postgres, qdrant, redis)
pytest tests/integration/test_storage.py   # storage
pytest tests/integration/test_vector.py    # qdrant
```

## RAG / Evals
```bash
pytest tests/rag/               # testes de RAG
pytest tests/rag/test_retrieval.py   # qualidade do retrieval
python scripts/run_evals.py     # evals completos
```

## Acceptance Tests
```bash
make acceptance                 # golden path de ponta a ponta
make prepare-release            # validate + acceptance + ui-build
```

## Responsabilidades da IA
- Ao finalizar uma tarefa, informe **quais testes rodou** e **quais não rodou**.
- Se um teste falhar, corrija o erro sem remover asserts, sem enfraquecer validação e sem reduzir cobertura.
- Não crie testes fantasmas ou vazios — todo teste deve validar comportamento real.
