# Use a slim Python base
FROM python:3.9-slim-buster

WORKDIR /app

# Install all Python deps in one step
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip cache purge

# Copy your application code
COPY . .

# Make PORT available as an environment variable
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Make sure gunicorn can find our app
ENV PYTHONPATH=/app

# Declare the port & start the app with more explicit configuration
EXPOSE 8000
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--timeout=120", "--workers=2", "--threads=2", "--log-level=info", "application:application"]

