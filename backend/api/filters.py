import django_filters
from django.db.models import Q
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__istartswith=value)


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

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return queryset.none() if int(value) else queryset
        condition = Q(favorited_by__user=user)
        return queryset.filter(condition) if int(value) else queryset.exclude(condition)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return queryset.none() if int(value) else queryset
        condition = Q(in_shopping_carts__user=user)
        return queryset.filter(condition) if int(value) else queryset.exclude(condition)
