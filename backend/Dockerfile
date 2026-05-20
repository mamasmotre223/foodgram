FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "until python -c \"import os, psycopg2; psycopg2.connect(dbname=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PASSWORD'), host=os.getenv('DB_HOST', 'db'), port=int(os.getenv('DB_PORT', '5432'))).close()\"; do echo 'Waiting for database...'; sleep 1; done; python manage.py migrate && python manage.py collectstatic --noinput && python manage.py load_ingredients && python manage.py load_tags && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]
