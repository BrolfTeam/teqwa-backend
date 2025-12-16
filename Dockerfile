FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (excluding __pycache__ via .dockerignore)
COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Make scripts executable
RUN chmod +x docker-entrypoint.sh docker-entrypoint.py

# Use Python entrypoint script
CMD ["python", "docker-entrypoint.py"]