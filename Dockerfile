FROM python:3.10-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first for layer caching
COPY pyproject.toml requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application source
COPY biorxiv_server.py biorxiv_web_search.py ./

# Run as non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

CMD ["python", "biorxiv_server.py"]
