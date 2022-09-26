#!/bin/sh

# Waiting for database to be started
if [ "$DATABASE" = "postgres" ]
then
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
fi

# Collect static files
python manage.py collectstatic --no-input --clear

exec "$@"

# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/