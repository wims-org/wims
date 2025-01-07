FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt update && apt install -y curl
RUN pip install --no-cache-dir poetry

RUN poetry install --no-root

COPY . .

EXPOSE 5000
CMD [ "/app/.venv/bin/python", "app.py" ]
