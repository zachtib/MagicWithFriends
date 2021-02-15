release: python manage.py migrate
web: uvicorn app.asgi:app --host=0.0.0.0 --port=$PORT
