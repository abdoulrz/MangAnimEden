# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (requires a dummy secret key for build time)
RUN DJANGO_SECRET_KEY=build-time-dummy python manage.py collectstatic --noinput

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Entrypoint handles migrations and gunicorn startup
ENTRYPOINT ["/app/docker-entrypoint.sh"]
