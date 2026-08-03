# syntax=docker/dockerfile:1.7
FROM nvcr.io/nvidia/tritonserver:26.06-py3

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/triton-model-cache \
    SENTENCE_TRANSFORMERS_HOME=/opt/triton-model-cache \
    CE_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2

RUN python3 -m pip install "sentence-transformers>=3.4,<6" \
    && python3 -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

RUN mkdir -p /models /opt/triton-model-cache

HEALTHCHECK --interval=20s --timeout=8s --start-period=90s --retries=10 \
  CMD curl -fsS http://127.0.0.1:8000/v2/models/cross_encoder/ready || exit 1

CMD ["tritonserver", "--model-repository=/models", "--model-control-mode=explicit", "--load-model=cross_encoder", "--strict-readiness=true"]
