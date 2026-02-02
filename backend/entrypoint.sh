#!/bin/env sh

echo "Waiting for Postgres to be ready ..."
until pg_isready -h $DB_HOST -p $DB_PORT; do
  echo "Postgres is unavailable - waiting ..."
  sleep 2
done

echo "Postgres is ready!"

if [ "$BACKEND_SERVICE_ADMIN_USER" != "" ] &&
  [ "$BACKEND_SERVICE_ADMIN_PASSWORD" != "" ] &&
  [ "$BACKEND_SERVICE_ADMIN_EMAIL" != "" ]; then
  echo "Creating admin user ..."
  cat <<EOF | /app/manage.py shell
import os
from django.contrib.auth import get_user_model

BACKEND_SERVICE_ADMIN_USER = os.getenv("BACKEND_SERVICE_ADMIN_USER")
BACKEND_SERVICE_ADMIN_PASSWORD = os.getenv("BACKEND_SERVICE_ADMIN_PASSWORD")
BACKEND_SERVICE_ADMIN_EMAIL = os.getenv("BACKEND_SERVICE_ADMIN_EMAIL")

User = get_user_model()  # get the currently active user model,

User.objects.filter(username=BACKEND_SERVICE_ADMIN_USER).exists() or \
    User.objects.create_superuser(
        BACKEND_SERVICE_ADMIN_USER,
        BACKEND_SERVICE_ADMIN_EMAIL,
        BACKEND_SERVICE_ADMIN_PASSWORD,
        is_staff=True,
        is_superuser=True
    )
EOF
else
  echo "Admin user already exists"
fi

# Generate a kubeconfig for in-cluster access
sh /app/scripts/setup_incluster_kubeconfig.sh

if [ "$SHARED_VCLUSTER_ENABLED" = "true" ]; then
  echo "Setting up a shared vcluster..."
  sh /app/scripts/setup_shared_vcluster.sh
else
  echo "Not using a shared vcluster..."
fi

if [ "$WORKSPACE_VCLUSTER_ENABLED" = "true" ] && [ "$WORKSPACE_API_SERVICE_URL" != "" ]; then
  echo "Checking Workspace API access for using user workspace vClusters..."
  . /app/scripts/check_service.sh
  check_service "${WORKSPACE_API_SERVICE_URL}/probe"
fi

echo "Collecting static files ..."
/app/manage.py collectstatic --noinput
echo "Applying database migrations ..."
/app/manage.py migrate
echo "Loading fixtures ..."
/app/manage.py loaddata /app/backend/fixtures/*
echo "Starting the server ..."
/app/manage.py runserver 0.0.0.0:8000
