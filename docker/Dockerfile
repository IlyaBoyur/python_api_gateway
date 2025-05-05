FROM python:3.12-alpine

# Set environment variables
ARG POETRY_PARAMS=""
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_REQUESTS_TIMEOUT=60 \
    PATH="${PATH}:/root/.local/bin" \
    PYTHONWARNINGS=ignore

# Expose port 8000
EXPOSE 8000/tcp

# Set the working directory for the application
WORKDIR /app

# Copy just the dependencies installation from the current directory to the Docker image
# COPY pyproject.toml poetry.lock /app/
COPY pyproject.toml  /app/

# Install necessary dependencies
RUN set -ex; \
    apk update; \
    apk add --no-cache curl; \
    apk add --no-cache --virtual build-deps \
        cargo \
        gcc \
        git \
        build-base \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry==1.8.5 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction -vv --no-root \
    && apk del --no-cache build-deps

# Copy the current directory contents into the container
COPY . /app/

# Give necessary permissions to entrypoint
RUN chmod +x /app/docker/entrypoint.sh
