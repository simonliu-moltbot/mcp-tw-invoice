# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all files
COPY . .

# Install dependencies and the project
RUN pip install --no-cache-dir .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the HTTP port
EXPOSE 8000

# Run FastMCP in streamable-http mode by default for Docker
CMD ["python", "src/server.py", "--mode", "http", "--port", "8000"]
