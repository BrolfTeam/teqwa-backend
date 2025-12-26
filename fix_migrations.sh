#!/bin/bash
echo "Fixing database migrations..."

# Make migrations for specific apps that showed changes
docker compose exec backend python manage.py makemigrations authentication donations education futsal_booking itikaf memberships students

# Make migrations for everything else just in case
docker compose exec backend python manage.py makemigrations

# Apply all migrations
docker compose exec backend python manage.py migrate

echo "Done! Database should be ready."
