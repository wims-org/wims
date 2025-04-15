# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app
RUN apt-get update && apt-get install -y curl iputils-ping mosquitto
# Install the dependencies
# Install Poetry
RUN pip install --no-cache-dir poetry

# Ensure the correct Python version is used by Poetry
ENV POETRY_VIRTUALENVS_CREATE=false
# Copy the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5005

WORKDIR /app/src
# Command to run the application

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5005"]