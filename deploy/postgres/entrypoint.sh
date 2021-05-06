#!/bin/sh

if [ "$PRODUCTION" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py collectstatic --no-input --clear
python manage.py migrate

exec "$@"