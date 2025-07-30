# Use Python 3.11 slim image as base
FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY README.md ./

# Create a virtual environment and install dependencies using uv
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN uv pip install -e .

# Install system dependencies for Playwright
RUN playwright install-deps chromium

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app /opt/venv

# Switch to app user
USER app

# Set environment variables for the app user
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/home/app/.cache/ms-playwright
ENV CONTAINER=docker

# Install Playwright browsers as the app user
RUN playwright install chromium

# Expose port for HTTP transport (optional)
EXPOSE 3000

COPY mcp_server.py ./
# Default command - explicitly use HTTP transport for Docker
CMD ["python", "mcp_server.py", "--headless"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from mcp_server import browser_manager; asyncio.run(browser_manager.ensure_browser())" || exit 1

# build command: docker build -t stealth-browser-mcp .
# run command: docker run -p 3000:3000 stealth-browser-mcp
# run command with http: docker run -p 3000:3000 stealth-browser-mcp python mcp_server.py --headless --http --host 0.0.0.0 --port 3000