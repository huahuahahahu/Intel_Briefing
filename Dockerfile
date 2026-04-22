# Intel Briefing Engine
# Multi-stage build: slim Python image with system CA certs
FROM python:3.13-slim AS base

# System-level deps for lxml and SSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ensure reports dir exists
RUN mkdir -p reports/daily_briefings

# Default: run the CLI
ENTRYPOINT ["python", "cli.py"]
CMD ["--limit", "10"]
