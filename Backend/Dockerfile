FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies first so this layer is cached on rebuilds
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code (secrets come from env vars at runtime, not baked in)
COPY main.py ./
COPY app/ ./app/

# Expose and run
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
