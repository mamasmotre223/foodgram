from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
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
from users.models import Subscription, User


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
    list_filter = ("tags", "author", "cooking_time")
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_favorites_count=Count("favorites"))
            .prefetch_related("tags", "ingredients")
        )

    @admin.display(description="В избранном")
    def favorites_count(self, recipe):
        return recipe._favorites_count

    @admin.display(description="Продукты")
    def ingredients_html(self, recipe):
        return mark_safe(
            "<br>".join(
                f"{item.name} ({item.measurement_unit})"
                for item in recipe.ingredients.all()
            )
        )

    @admin.display(description="Теги")
    def tags_html(self, recipe):
        return mark_safe("<br>".join(tag.name for tag in recipe.tags.all()))

    @admin.display(description="Картинка")
    def image_html(self, recipe):
        if not recipe.image:
            return "-"
        return mark_safe(f'<img src="{recipe.image.url}" width="80" />')


class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__email", "recipe__name")


admin.site.register(Favorite, UserRecipeRelationAdmin)
admin.site.register(ShoppingCart, UserRecipeRelationAdmin)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "id",
        "username",
        "full_name",
        "email",
        "avatar_preview",
        "recipes_count",
        "subscriptions_count",
        "subscribers_count",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Профиль", {"fields": ("avatar",)}),
    )

    @admin.display(description="ФИО")
    def full_name(self, user):
        return f"{user.first_name} {user.last_name}".strip()

    @admin.display(description="Аватар")
    def avatar_preview(self, user):
        if not user.avatar:
            return "-"
        return mark_safe(f'<img src="{user.avatar.url}" width="50" />')

    @admin.display(description="Рецептов")
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description="Подписок")
    def subscriptions_count(self, user):
        return user.follower_subscriptions.count()

    @admin.display(description="Подписчиков")
    def subscribers_count(self, user):
        return user.author_subscriptions.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = (
        "user__email",
        "author__email",
        "user__username",
        "author__username",
    )
