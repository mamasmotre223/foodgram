from django.utils import timezone

from recipes.models import Recipe, RecipeIngredient


def build_shopping_list_text(user):
    recipe_ingredients = (
        RecipeIngredient.objects.filter(recipe__shoppingcarts__user=user)
        .select_related("ingredient", "recipe", "recipe__author")
        .order_by("ingredient__name")
    )
    recipes = (
        Recipe.objects.filter(shoppingcarts__user=user)
        .select_related("author")
        .prefetch_related("tags")
        .distinct()
    )
    product_totals = {}
    for recipe_ingredient in recipe_ingredients:
        key = (
            recipe_ingredient.ingredient.name,
            recipe_ingredient.ingredient.measurement_unit,
        )
        product_totals[key] = product_totals.get(key, 0) + recipe_ingredient.amount

    return "\n".join(
        [
            f"Список покупок от {timezone.localdate().strftime('%d.%m.%Y')}",
            "",
            "Продукты:",
            *[
                f"{index}. {name.capitalize()} ({unit}) - {amount}"
                for index, ((name, unit), amount) in enumerate(
                    product_totals.items(),
                    start=1,
                )
            ],
            "",
            "Рецепты:",
            *[
                (
                    f"{index}. {recipe.name} - {recipe.author.username}"
                    f" ({', '.join(tag.name for tag in recipe.tags.all())})"
                )
                for index, recipe in enumerate(recipes, start=1)
            ],
        ]
    )
