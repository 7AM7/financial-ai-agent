FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot --home /home/nonroot nonroot

WORKDIR /app
ENV HOME=/home/nonroot
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/home/nonroot/.cache/uv

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-group dev

COPY . /app
RUN chown -R nonroot:nonroot /app /home/nonroot

USER nonroot

WORKDIR /app/src
EXPOSE 8000
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
