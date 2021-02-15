release: python manage.py migrate
web: uvicorn app.asgi:application --host=0.0.0.0 --port=$PORT
