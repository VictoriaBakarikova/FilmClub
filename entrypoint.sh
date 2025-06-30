#!/bin/sh

set -x

echo "Running migrations..."
python manage.py migrate
echo "DONE"

echo "Creating a superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
  User.objects.create_superuser('admin', 'admin@example.com', '1qaz')
  print("Superuser created")
else:
  print("Superuser already exists")
EOF

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000