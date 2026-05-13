# Foodgram

Foodgram is a recipe sharing service. Users can publish recipes, add recipes
to favorites, subscribe to authors, and download a shopping list with summed
ingredients.

## Deployed Project

- Site: http://icantbreathe.myftp.biz/
- Server IP: http://81.26.180.71/
- Admin: http://icantbreathe.myftp.biz/admin/
- API docs: http://icantbreathe.myftp.biz/api/docs/

## Demo Accounts

- Admin: `admin@foodgram.local` / `admin12345`
- User: `chef1@foodgram.local` / `testpass123`
- User: `chef2@foodgram.local` / `testpass123`

## Tech Stack

- Python
- Django
- Django REST Framework
- Djoser token authentication
- PostgreSQL
- Gunicorn
- Nginx
- Docker Compose
- React SPA frontend

## Project Structure

- `backend/` - Django REST API.
- `frontend/` - React single page application.
- `infra/` - Docker Compose and Nginx configuration.
- `data/` - ingredient source data.
- `docs/` - OpenAPI schema and Redoc page.

## Local Run

Create `backend/.env`:

```env
DEBUG=True
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
TIME_ZONE=Europe/Moscow
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

Start the project:

```bash
cd infra
docker compose up --build
```

Open:

```text
http://localhost/
http://localhost/admin/
http://localhost/api/docs/
```

## Server Run

On the server, create `backend/.env`:

```env
DEBUG=False
DJANGO_SECRET_KEY=change-me-to-a-long-secret
ALLOWED_HOSTS=icantbreathe.myftp.biz,81.26.180.71,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://icantbreathe.myftp.biz,http://81.26.180.71
TIME_ZONE=Europe/Moscow
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

Run:

```bash
cd infra
sudo docker compose up -d --build
```

Check containers:

```bash
sudo docker compose ps
```

## Useful Commands

```bash
sudo docker compose logs -f
sudo docker compose logs --tail=80 backend
sudo docker compose logs --tail=80 nginx
sudo docker compose restart nginx
sudo docker compose down
```
