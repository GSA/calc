#!/bin/bash

set -e

if [ $CF_INSTANCE_INDEX = "0" ]; then
    echo "----- Migrating Database -----"
    python manage.py migrate --noinput

    echo "----- Updating search field -----"
    python manage.py update_search_field

    echo "----- Initializing Groups -----"
    python manage.py initgroups

fi
echo "------ Starting APP ------"
gunicorn calc.wsgi:application --timeout 180 --ciphers TLS_RSA_WITH_AES_256_CBC_SHA256 --workers 3 --log-level=debug
