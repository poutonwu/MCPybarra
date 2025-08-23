# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools
RUN pip install --upgrade pip wheel build

# Copy project files
COPY pyproject.toml .
COPY src src

# Build the project wheel without dependencies
RUN pip wheel . --no-deps --wheel-dir /app/dist

FROM python:3.13-slim AS runtime

WORKDIR /app

# Install the wheel from the builder stage
COPY --from=builder /app/dist/*.whl /app/
RUN pip install --no-cache-dir /app/*.whl

# Default entrypoint for the MCP Tavily server
ENTRYPOINT ["python", "-m", "mcp_server_tavily"]