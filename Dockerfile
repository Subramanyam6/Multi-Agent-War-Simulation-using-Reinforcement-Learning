# Use Python 3.9 slim
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib

# Create matplotlib cache directory
RUN mkdir -p /tmp/matplotlib && chmod 777 /tmp/matplotlib

# Expose port (Render sets PORT env var)
EXPOSE 10000

# Run with gunicorn - simpler config
CMD gunicorn --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:app
