# Foodgram

Foodgram — это сервис для обмена рецептами. Пользователи могут публиковать рецепты, добавлять рецепты в избранное, подписываться на авторов и скачивать список покупок с суммированными ингредиентами.

## Развёрнутый проект

- Сайт: http://icantbreathe.myftp.biz/
- Админ-панель: http://icantbreathe.myftp.biz/admin/
- Документация API: http://icantbreathe.myftp.biz/api/docs/

## Демо-аккаунты

- Администратор: `admin1@foodgram.local` / `admin123`
- Пользователь 1: `chef1@foodgram.local` / `testpass123`
- Пользователь 2: `chef2@foodgram.local` / `testpass123`

## Технологический стек

- Python
- Django
- Django REST Framework
- Djoser (токен-аутентификация)
- PostgreSQL
- Gunicorn
- Nginx
- Docker Compose
- React SPA (фронтенд)

## Структура проекта

- `backend/` — Django REST API.
- `frontend/` — одностраничное приложение на React.
- `infra/` — конфигурация Docker Compose и Nginx.
- `data/` — исходные данные ингредиентов.
- `docs/` — OpenAPI-схема и страница Redoc.

## Запуск локально

Создайте файл `backend/.env`:

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

Запустите проект:

```bash
cd infra
sudo docker compose up -d --build
```
