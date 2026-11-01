FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app
ENV UV_NO_DEV=1
WORKDIR /app
RUN uv sync --locked

EXPOSE 8000
# ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]