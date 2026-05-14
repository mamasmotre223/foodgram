import base64
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User

PIXEL = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/"
    "x8AAusB9Y9Hn8QAAAAASUVORK5CYII="
)


class Command(BaseCommand):
    help = "Create demo users, tags, recipes and relations"

    def handle(self, *args, **options):
        tags = [
            Tag.objects.get_or_create(name="Завтрак", slug="breakfast")[0],
            Tag.objects.get_or_create(name="Обед", slug="lunch")[0],
            Tag.objects.get_or_create(name="Ужин", slug="dinner")[0],
        ]

        users_data = [
            {
                "email": "admin@foodgram.local",
                "username": "admin",
                "first_name": "Админ",
                "last_name": "Фудграм",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "chef1@foodgram.local",
                "username": "chef1",
                "first_name": "Анна",
                "last_name": "Поварова",
            },
            {
                "email": "chef2@foodgram.local",
                "username": "chef2",
                "first_name": "Илья",
                "last_name": "Рецептов",
            },
        ]

        users = []
        for data in users_data:
            email = data["email"]
            user, created = User.objects.get_or_create(email=email, defaults=data)
            if created:
                user.set_password("admin12345" if user.is_superuser else "testpass123")
                user.save()
            users.append(user)

        ingredients = list(Ingredient.objects.all()[:6])
        if len(ingredients) < 6:
            fallback = [
                ("Картофель", "г"),
                ("Соль", "г"),
                ("Яйцо куриное", "шт."),
                ("Молоко", "мл"),
                ("Сахар", "г"),
                ("Мука", "г"),
            ]
            for name, unit in fallback:
                Ingredient.objects.get_or_create(name=name, measurement_unit=unit)
            ingredients = list(Ingredient.objects.all()[:6])

        recipes_data = [
            {
                "author": users[1],
                "name": "Омлет на завтрак",
                "text": "Простой омлет с молоком.",
                "cooking_time": 10,
                "tags": [tags[0]],
                "ingredients": [
                    (ingredients[2], 2),
                    (ingredients[3], 150),
                    (ingredients[1], 2),
                ],
            },
            {
                "author": users[2],
                "name": "Картофель на ужин",
                "text": "Запеченный картофель с солью.",
                "cooking_time": 40,
                "tags": [tags[2], tags[1]],
                "ingredients": [(ingredients[0], 500), (ingredients[1], 5)],
            },
        ]

        for recipe_data in recipes_data:
            recipe, created = Recipe.objects.get_or_create(
                author=recipe_data["author"],
                name=recipe_data["name"],
                defaults={
                    "text": recipe_data["text"],
                    "cooking_time": recipe_data["cooking_time"],
                },
            )
            if not recipe.image:
                recipe.image.save(
                    f"{uuid4()}.png",
                    ContentFile(base64.b64decode(PIXEL)),
                    save=True,
                )
            recipe.text = recipe_data["text"]
            recipe.cooking_time = recipe_data["cooking_time"]
            recipe.save()
            recipe.tags.set(recipe_data["tags"])
            recipe.recipe_ingredients.all().delete()
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=amount,
                    )
                    for ingredient, amount in recipe_data["ingredients"]
                ]
            )

        Subscription.objects.get_or_create(user=users[1], author=users[2])
        favorite_recipe = Recipe.objects.filter(author=users[2]).first()
        shopping_recipe = Recipe.objects.filter(author=users[1]).first()
        if favorite_recipe:
            Favorite.objects.get_or_create(user=users[1], recipe=favorite_recipe)
        if shopping_recipe:
            ShoppingCart.objects.get_or_create(user=users[2], recipe=shopping_recipe)

        self.stdout.write(self.style.SUCCESS("Demo data created."))
