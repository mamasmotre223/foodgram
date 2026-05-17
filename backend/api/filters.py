import django_filters
from django.db.models import Q

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_name(self, ingredients, name, value):
        return ingredients.filter(name__istartswith=value)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
        conjoined=False,
    )
    author = django_filters.NumberFilter(field_name="author__id")
    is_favorited = django_filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("author", "tags")

    def filter_is_favorited(self, recipes, name, value):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return recipes.none() if int(value) else recipes
        condition = Q(favorites__user=user)
        return (
            recipes.filter(condition)
            if int(value)
            else recipes.exclude(condition)
        )

    def filter_is_in_shopping_cart(self, recipes, name, value):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return recipes.none() if int(value) else recipes
        condition = Q(shoppingcarts__user=user)
        return (
            recipes.filter(condition)
            if int(value)
            else recipes.exclude(condition)
        )
