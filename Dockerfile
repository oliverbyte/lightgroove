# LightGroove Dockerfile
# Professional DMX Lighting Controller - Docker Container

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create volume mount points for configuration persistence
VOLUME ["/app/config"]

# Expose HTTP port
EXPOSE 5555

# Set environment variable for HTTP port (can be overridden)
ENV LIGHTGROOVE_HTTP_PORT=5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5555/api/grandmaster')" || exit 1

# Run the application
CMD ["python", "main.py"]
