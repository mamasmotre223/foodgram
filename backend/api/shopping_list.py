from datetime import datetime

from django.db.models import Sum

from recipes.models import Recipe, RecipeIngredient


def build_shopping_list_text(user):
    ingredients = (
        RecipeIngredient.objects.filter(recipe__in_shopping_carts__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(total_amount=Sum("amount"))
        .order_by("ingredient__name")
    )
    recipes = (
        Recipe.objects.filter(in_shopping_carts__user=user)
        .select_related("author")
        .prefetch_related("tags")
        .distinct()
    )
    return "\n".join(
        [
            f"Список покупок от {datetime.now().strftime('%Y-%m-%d')}",
            "Продукты:",
            *[
                (
                    f"{index}. {item['ingredient__name'].capitalize()} "
                    f"({item['ingredient__measurement_unit']})"
                    f" — {item['total_amount']}"
                )
                for index, item in enumerate(ingredients, start=1)
            ],
            "Рецепты:",
            *[
                (
                    f"- {recipe.name} — {recipe.author.username} "
                    f"({', '.join(tag.name for tag in recipe.tags.all())})"
                )
                for recipe in recipes
            ],
        ]
    )
