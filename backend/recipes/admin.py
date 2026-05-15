from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag

class RelatedRecipeCountAdmin(admin.ModelAdmin):
    @admin.display(description="Рецептов")
    def recipes_count(self, entity):
        return entity.recipes.count()


@admin.register(Tag)
class TagAdmin(RelatedRecipeCountAdmin):
    list_display = ("id", "name", "slug", "recipes_count")
    search_fields = ("name", "slug")


@admin.register(Ingredient)
class IngredientAdmin(RelatedRecipeCountAdmin):
    list_display = ("id", "name", "measurement_unit", "recipes_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cooking_time",
        "author",
        "favorites_count",
        "ingredients_html",
        "tags_html",
        "image_html",
    )
    search_fields = (
        "name",
        "author__username",
        "author__email",
        "tags__name",
        "ingredients__name",
    )
    list_filter = ("tags", "author")
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_favorites_count=Count("favorited_by"))
            .prefetch_related("tags", "ingredients")
        )

    @admin.display(description="В избранном")
    def favorites_count(self, recipe):
        return recipe._favorites_count

    @admin.display(description="Продукты")
    @mark_safe
    def ingredients_html(self, recipe):
        return "<br>".join(
            f"{item.name} ({item.measurement_unit})"
            for item in recipe.ingredients.all()
        )

    @admin.display(description="Теги")
    @mark_safe
    def tags_html(self, recipe):
        return "<br>".join(tag.name for tag in recipe.tags.all())

    @admin.display(description="Картинка")
    @mark_safe
    def image_html(self, recipe):
        return f'<img src="{recipe.image.url}" width="80" />' if recipe.image else "-"


class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__email", "recipe__name")


admin.site.register(Favorite, UserRecipeRelationAdmin)
admin.site.register(ShoppingCart, UserRecipeRelationAdmin)
