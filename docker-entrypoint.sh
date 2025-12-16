#!/bin/bash
set -e

echo "=== Teqwa Backend Docker Entrypoint ==="

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "
import psycopg
import os
try:
    conn = psycopg.connect(
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'Teqwa123'),
        dbname=os.environ.get('DB_NAME', 'postgres')
    )
    conn.close()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser
echo "Creating superuser..."
python manage.py create_superuser_auto

# Collect static files (for production)
if [ "$DEBUG" != "1" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "=== Starting Django Development Server ==="
exec python manage.py runserver 0.0.0.0:8000