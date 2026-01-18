# Hugging Face Spaces Dockerfile
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
    MPLCONFIGDIR=/tmp/matplotlib \
    PORT=7860

# Create matplotlib cache directory
RUN mkdir -p /tmp/matplotlib && chmod 777 /tmp/matplotlib

# Expose port 7860 (HF Spaces default)
EXPOSE 7860

# Run with single worker to save memory
CMD gunicorn --bind 0.0.0.0:7860 \
    --workers 1 \
    --threads 1 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    app:app
