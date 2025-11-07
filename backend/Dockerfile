FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock alembic.ini .coveragerc ./

# # Installer les dépendances
# RUN uv sync --frozen --no-dev 

# Install dependencies (simplifié sans hatchling)
RUN uv pip install --system -r pyproject.toml

# Installer les dépendances de test (optionnelles)
RUN uv pip install --system ".[test]"

# Copy application code
COPY ./scripts /app/scripts
COPY ./app/ /app/app
COPY ./tests /app/tests

# Expose port
EXPOSE 8000

# Start application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]