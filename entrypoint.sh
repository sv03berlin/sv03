#!/bin/sh

set -e
set -m

echo "collectstatic is in progress"
python3 /code/manage.py collectstatic --no-input

if [ "$DJANGO_MIGRATE" = "true" ]; then
    echo "migrating is in progress"
    python3 /code/manage.py migrate
else
    echo "Migration flag not set. Skipping migrations."
fi

if [ "$DJANGO_FIXTURES" = "true" ]; then
    echo "loading fixtures is in progress"
    python3 /code/manage.py loadfixtures
else
    echo "Fixtures flag not set. Skipping loading fixtures."
fi

exec "$@"
