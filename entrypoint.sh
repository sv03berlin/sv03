#!/bin/bash

set -e
set -m

if [[ -d /etc/nginx/vhost.d ]]
then
    echo "Copying nginx config"
    cp "/code/nginx/nginx_domain_file" "/etc/nginx/vhost.d/"
    mv "/etc/nginx/vhost.d/nginx_domain_file" "/etc/nginx/vhost.d/${VIRTUAL_HOST}"
    cp "/code/nginx/nginx_domain_file_location" "/etc/nginx/vhost.d/"
    mv "/etc/nginx/vhost.d/nginx_domain_file_location" "/etc/nginx/vhost.d/${VIRTUAL_HOST}_location"
    cp /code/nginx/backend.conf /etc/nginx/conf.d
fi

echo "collectstatic is in progress"
python3 /code/manage.py collectstatic --no-input

if [ "$DJANGO_MIGRATE" = "true" ]; then
    echo "migrating is in progress"
    python3 /code/manage.py migrate
else
    echo "Migration flag not set. Skipping migrations."
fi

echo "Django docker is fully configured successfully."

exec "$@"