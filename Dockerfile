# ============================================
# Stage 1: Base Python Image with Dependencies
# ============================================
FROM python:3.11-slim as backend-base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Production Backend
# ============================================
FROM python:3.11-slim as backend-production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from base
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories for runtime
RUN mkdir -p /app/logs /app/data /app/uploads

# Expose the API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the FastAPI server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
