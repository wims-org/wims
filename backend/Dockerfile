# ref https://depot.dev/docs/container-builds/optimal-dockerfiles/python-uv-dockerfile
FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY schemas/ schemas/
COPY run.sh .

FROM python:3.14-slim AS runtime

ARG COMMIT_HASH=unknown
ENV COMMIT_HASH=${COMMIT_HASH}
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /app -s /bin/false appuser

WORKDIR /app

COPY --from=build --chown=appuser:appgroup /app .
RUN echo $COMMIT_HASH > /app/COMMIT_HASH

RUN mkdir -p /data && chown appuser:appgroup /data

USER appuser

VOLUME [ "/data" ]

WORKDIR /app
ENTRYPOINT ["./run.sh"]
