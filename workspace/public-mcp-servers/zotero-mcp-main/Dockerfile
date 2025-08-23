FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Install application
ADD README.md LICENSE pyproject.toml uv.lock src /app/
WORKDIR /app
ENV UV_FROZEN=true
RUN uv sync

# Check basic functionality
RUN uv run zotero-mcp --help

LABEL org.opencontainers.image.title="zotero-mcp"
LABEL org.opencontainers.image.description="Model Context Protocol Server for Zotero"
LABEL org.opencontainers.image.url="https://github.com/zotero/zotero-mcp"
LABEL org.opencontainers.image.source="https://github.com/zotero/zotero-mcp"
LABEL org.opencontainers.image.license="MIT"

# Command to run the server
ENTRYPOINT ["uv", "run", "--quiet", "zotero-mcp"]
