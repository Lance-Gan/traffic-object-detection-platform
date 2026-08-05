# syntax=docker/dockerfile:1.8

FROM python:3.13-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install \
        --yes \
        --no-install-recommends \
        ca-certificates \
        ffmpeg \
        gzip \
        tar \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd \
        --gid 10001 \
        app \
    && useradd \
        --uid 10001 \
        --gid app \
        --create-home \
        --shell /usr/sbin/nologin \
        app

WORKDIR /workspace/backend

COPY backend/requirements.txt \
    ./requirements.txt

ARG PYTORCH_CPU_INDEX_URL=https://download.pytorch.org/whl/cpu

RUN python -m pip install \
        --upgrade pip \
    && python -m pip install \
        --index-url "${PYTORCH_CPU_INDEX_URL}" \
        --only-binary=:all: \
        --no-deps \
        "torch==2.13.0+cpu" \
        "torchvision==0.28.0+cpu" \
    && python -m pip install \
        --requirement requirements.txt \
    && python -m pip check \
    && python -c "import torch; assert torch.version.cuda is None, f'Expected CPU-only PyTorch, got CUDA {torch.version.cuda}'; print(f'PyTorch {torch.__version__}: CPU-only build confirmed')"

COPY --chown=app:app \
    backend/alembic.ini \
    ./alembic.ini

COPY --chown=app:app \
    backend/migrations \
    ./migrations

COPY --chown=app:app \
    backend/app \
    ./app

RUN mkdir -p \
        /data/uploads/videos \
        /data/results/videos \
    && chown -R \
        app:app \
        /workspace/backend \
        /data

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips=*"]
