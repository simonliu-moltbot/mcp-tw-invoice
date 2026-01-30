# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (none needed strictly, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source code
COPY src/ src/

# Expose port (FastMCP default often uses stdio, but if using SSE/HTTP)
# We will use the mcp run command or python -m src.server
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.server"]
