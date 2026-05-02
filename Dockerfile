FROM python:3.11-slim

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_PYTHON=python3.11

# copy dependency first (cache layer)
COPY pyproject.toml uv.lock ./

# install dependencies only
RUN uv sync --frozen --no-install-project --no-cache --python python3.11

# copy source code
COPY . .

# install project
RUN uv sync --frozen --no-cache --python python3.11

CMD ["uv", "run", "uvicorn", "llm_connect.app:app", "--host", "0.0.0.0", "--port", "8000"]