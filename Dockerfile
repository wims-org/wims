# ====================== BACKEND ======================
FROM python:3.14-slim AS backendbuilder

COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

WORKDIR /backend

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY backend/uv.lock backend/pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY backend/src/ src/
COPY backend/alembic/ alembic/
COPY backend/alembic.ini .
COPY backend/run.sh .

# ====================== FRONTEND ======================

FROM node:25-alpine AS frontendbuilder
WORKDIR /app
COPY /vue_frontend/package*.json ./
RUN npm ci

# Copy the rest of the application code to the working directory
COPY /vue_frontend/ .

ARG VITE_API_URL
RUN npm run build 

# ====================== WIMS ======================

FROM python:3.14-slim AS runtime

# install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Add the backend
ARG COMMIT_HASH=unknown
ENV COMMIT_HASH=${COMMIT_HASH}
ENV PATH="/backend/.venv/bin:$PATH"

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /backend -s /bin/false appuser

WORKDIR /backend

COPY --from=backendbuilder --chown=appuser:appgroup /backend .
RUN echo $COMMIT_HASH > /backend/COMMIT_HASH && chown appuser:appgroup /backend/COMMIT_HASH

RUN mkdir -p /data && chown appuser:appgroup /data

VOLUME [ "/data" ]

# Add the frontend
COPY --from=frontendbuilder /app/dist/ /var/www/html/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Entrypoint: starts nginx as root, then drops to appuser for the backend
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]