# AddToCalendar Agent Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy backend modules (will be mounted in docker-compose)
# Backend path will be available at /app/backend

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "api.py"]