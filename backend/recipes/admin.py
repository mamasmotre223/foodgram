from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db.models import Count
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
    User,
)

admin.site.unregister(Group)
admin.site.unregister(Site)


class RelatedRecipeCountAdmin(admin.ModelAdmin):
    @admin.display(description="Рецептов")
    def recipes_count(self, entity):
        return entity.recipes.count()


class HasRecipesFilter(admin.SimpleListFilter):
    title = "Есть в рецептах"
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return (("yes", "Да"), ("no", "Нет"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True)
        return queryset


@admin.register(Tag)
class TagAdmin(RelatedRecipeCountAdmin):
    list_display = ("id", "name", "slug", "recipes_count")
    search_fields = ("name", "slug")


@admin.register(Ingredient)
class IngredientAdmin(RelatedRecipeCountAdmin):
    list_display = ("id", "name", "measurement_unit", "recipes_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit", HasRecipesFilter)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class CookingTimeCategoryFilter(admin.SimpleListFilter):
    title = "Время"
    parameter_name = "cooking_time_group"

    def lookups(self, request, model_admin):
        return (("fast", "Быстрые"), ("medium", "Средние"), ("long", "Долгие"))

    def queryset(self, request, queryset):
        if self.value() == "fast":
            return queryset.filter(cooking_time__lte=30)
        if self.value() == "medium":
            return queryset.filter(cooking_time__gt=30, cooking_time__lte=60)
        if self.value() == "long":
            return queryset.filter(cooking_time__gt=60)
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cooking_time_display",
        "author_username",
        "favorites_count",
        "ingredients_html",
        "tags_html",
        "image_preview",
    )
    search_fields = (
        "name",
        "author__username",
        "author__email",
        "tags__name",
        "ingredients__name",
    )
    list_filter = ("tags", "author__username", CookingTimeCategoryFilter)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ("image_preview",)
    fields = (
        "name",
        "author",
        "text",
        "cooking_time",
        "tags",
        ("image", "image_preview"),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_favorites_count=Count("favorites"))
            .select_related("author")
            .prefetch_related("tags", "ingredients")
        )

    @admin.display(
        description=mark_safe("Время<br>(мин)"),
        ordering="cooking_time",
    )
    def cooking_time_display(self, recipe):
        return recipe.cooking_time

    @admin.display(description="Автор", ordering="author__username")
    def author_username(self, recipe):
        return recipe.author.username

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
    def image_preview(self, recipe):
        if not recipe.image:
            return "-"
        return mark_safe(f'<img src="{recipe.image.url}" width="220" />')


class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__email", "recipe__name")


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeRelationAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeRelationAdmin):
    pass


class HasRecipesUserFilter(admin.SimpleListFilter):
    title = "Есть рецепты"
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return (("yes", "Да"), ("no", "Нет"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True)
        return queryset


class HasSubscriptionsUserFilter(admin.SimpleListFilter):
    title = "Есть подписки"
    parameter_name = "has_subscriptions"

    def lookups(self, request, model_admin):
        return (("yes", "Да"), ("no", "Нет"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                follower_subscriptions__isnull=False
            ).distinct()
        if self.value() == "no":
            return queryset.filter(follower_subscriptions__isnull=True)
        return queryset


class HasSubscribersUserFilter(admin.SimpleListFilter):
    title = "Есть подписчики"
    parameter_name = "has_subscribers"

    def lookups(self, request, model_admin):
        return (("yes", "Да"), ("no", "Нет"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                author_subscriptions__isnull=False
            ).distinct()
        if self.value() == "no":
            return queryset.filter(author_subscriptions__isnull=True)
        return queryset


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
    list_filter = (
        HasRecipesUserFilter,
        HasSubscriptionsUserFilter,
        HasSubscribersUserFilter,
    )
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Профиль", {"fields": (("avatar", "avatar_preview"),)}),
    )
    readonly_fields = ("avatar_preview",)

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


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")
