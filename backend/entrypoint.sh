#!/bin/sh

echo "Waiting for Postgres to be ready..."
until pg_isready -h postgres -p 5432; do
	echo "Postgres is unavailable - waiting..."
	sleep 2
done

echo "Postgres is ready!"
echo "Applying database migrations..."

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
