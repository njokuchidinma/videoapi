# python manage.py makemigrations 
python manage.py migrate
# python /app/manage.py collectstatic --no-input


gunicorn chromeapi.wsgi:application --bind 0.0.0.0:"$PORT"