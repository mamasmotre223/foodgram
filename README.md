# Foodgram

Автор: Никита Лебедев, [GitHub](https://github.com/).

Foodgram - сервис публикации рецептов, избранного, подписок и списка покупок.

## Развернутый проект

- [Сайт](http://icantbreathe.myftp.biz/)
- [Админ-панель](http://icantbreathe.myftp.biz/admin/)
- [Документация API](http://icantbreathe.myftp.biz/api/docs/)

## Технологический стек

Python, Django, DRF, Djoser, PostgreSQL, Gunicorn, Nginx, Docker Compose, React.

## Развертывание через Docker

```bash
git clone <repo_url>
cd foodgram/infra
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_ingredients --path /app/data/ingredients.json
docker compose exec backend python manage.py load_tags --path /app/data/tags.json
```

## Запуск через Docker

```bash
cd foodgram/infra
docker compose up -d
```

## Локальный запуск без Docker

```bash
git clone <repo_url>
cd foodgram/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py load_ingredients --path ../data/ingredients.json
python manage.py load_tags --path ../data/tags.json
python manage.py runserver
```
