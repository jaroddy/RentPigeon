# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install uv and resolve deps from lockfile
RUN pip install --upgrade pip && pip install uv
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project

# Copy app and install it
COPY rentpigeon ./rentpigeon
RUN --mount=type=cache,target=/root/.cache/uv uv pip install -e .

# Non-root user (optional)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Streamlit defaults
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Exec-form healthcheck (no curl)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python","-c","import urllib.request,sys; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)"]

# Use exec form; call streamlit directly
CMD ["streamlit","run","rentpigeon/ui/streamlit_app.py","--server.port=8501","--server.headless=true"]
