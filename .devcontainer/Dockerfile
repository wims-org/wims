#FROM mcr.microsoft.com/devcontainers/python:1-${templateOption:imageVariant}
FROM mcr.microsoft.com/vscode/devcontainers/python:3.12-bookworm

ENV PYTHONUNBUFFERED 1

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends docker.io npm
RUN sudo usermod -aG docker $(whoami)

# Install project dependencies
COPY ./vue_frontend /workspace/vue_frontend
WORKDIR /workspace/vue_frontend
RUN npm install
WORKDIR /workspace
COPY ./backend/pyproject.toml ./backend/poetry.lock /workspace/backend/
WORKDIR /workspace/backend
RUN poetry install