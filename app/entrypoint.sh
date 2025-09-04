#!/bin/sh

# Ожидание доступности базы данных
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations

# Применение миграций
python manage.py migrate --noinput

# Сбор статических файлов
python manage.py collectstatic --noinput

# Запуск Gunicorn
exec gunicorn task_tracker.wsgi:application --bind 0.0.0.0:8000