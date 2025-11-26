FROM python:3.11-slim

RUN groupadd -r authuser && useradd -r -g authuser -m -d /home/authuser authuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY --chown=authuser:authuser . .

RUN rm -rf .git .idea .venv __pycache__ build dist *.pyc *.pyo *.egg-info

RUN uv pip install --system -e .

USER authuser

EXPOSE 8000

ENV PORT=8000
ENV WORKERS=1
ENV LOG_LEVEL=INFO
ENV LOG_DIRECTORY=/var/log/auth

RUN chmod +x ./scripts/entrypoint.sh

ENTRYPOINT ["./scripts/entrypoint.sh"]