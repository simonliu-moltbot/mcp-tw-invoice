# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all files first so that build backends (like hatchling) can see the package structure
COPY . .

# Install dependencies and the project itself
RUN pip install --no-cache-dir .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the HTTP port
EXPOSE 8000

# Run the server in HTTP mode by default
CMD ["python", "src/server.py", "--mode", "http", "--port", "8000"]
