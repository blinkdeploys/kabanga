#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py populate
uwsgi --http "0.0.0.0:8000" --module kabanga.wsgi:application --master --processes 4 --threads 2 --static-map /static=/code/static
