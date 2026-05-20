# Foodgram

[![Main Kittygram workflow](https://github.com/mamasmotre223/foodgram/actions/workflows/foodgram.yml/badge.svg)](https://github.com/mamasmotre223/foodgram/actions/workflows/foodgram.yml)

Автор: Никита Лебедев, [GitHub](https://github.com/mamasmotre223).

Foodgram - сервис публикации рецептов, избранного, подписок и списка покупок.

## Развернутый проект

- [Сайт](http://icantbreathe.myftp.biz/)
- [Админ-панель](http://icantbreathe.myftp.biz/admin/)
- [Документация API](http://icantbreathe.myftp.biz/api/docs/)

## Технологический стек

Python, Django, DRF, Djoser, PostgreSQL, Gunicorn, Nginx, Docker Compose, React.

## Развертывание через Docker

```bash
git clone https://github.com/mamasmotre223/foodgram.git
cd foodgram/infra
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_ingredients --path /app/data/ingredients.json
docker compose exec backend python manage.py load_tags --path /app/data/tags.json
```

## Создание пользователя для доступа к админке на сервере

```bash
cd foodgram/infra
docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); user, created = User.objects.get_or_create(username='review', defaults={'email': 'review@admin.ru'}); user.email='review@admin.ru'; user.is_staff=True; user.is_superuser=True; user.set_password('revw1admn'); user.save(); print('created' if created else 'updated')"
```

## Запуск через Docker

```bash
cd foodgram/infra
docker compose up -d
```


## Развертывание без Docker

```bash
git clone https://github.com/mamasmotre223/foodgram.git
cd foodgram/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py load_ingredients --path ../data/ingredients.json
python manage.py load_tags --path ../data/tags.json
python manage.py runserver
```
