# Use the Python dev container as the base image
FROM mcr.microsoft.com/vscode/devcontainers/python:3.12-bookworm

ENV PYTHONUNBUFFERED 1

# Install Python dependencies
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt && rm -rf /tmp/pip-tmp

# Install additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    curl \
    npm

# Install playwright dependencies for wayland
RUN apt-get -y install --no-install-recommends libx11-6 libxcomposite1 libxrandr2 libxdamage1 libxext6 libxfixes3 \
    libxcb1 libxkbcommon0 libwayland-client0 libwayland-cursor0 libwayland-egl1 libegl1-mesa libgbm1 libgtk-3-0 python3-opencv

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Docker and Docker Compose plugin
RUN curl -fsSL https://get.docker.com | bash \
    && curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Add the current user to the Docker group
ARG USERNAME=vscode
RUN groupadd -f docker && usermod -aG docker,users $USERNAME

# bash history
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && mkdir /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R $USERNAME /commandhistory \
    && echo "$SNIPPET" >> "/home/$USERNAME/.bashrc"

# Install Node.js dependencies
COPY ./vue_frontend /workspace/vue_frontend
RUN cd /workspace/vue_frontend && npm install

# Install Python backend dependencies
WORKDIR /workspace
COPY ./backend/pyproject.toml ./backend/poetry.lock /workspace/backend/
RUN cd /workspace/backend && poetry install
