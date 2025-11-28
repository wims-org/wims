# Use the official Python image from the Docker Hub
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl iputils-ping libgl1 libglib2.0-0 && apt-get clean

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false

# Layer caching for dependencies
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8000

WORKDIR /app/src

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]