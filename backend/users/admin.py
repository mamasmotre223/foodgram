from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.safestring import mark_safe

from users.models import Subscription, User


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
    @mark_safe
    def avatar_preview(self, user):
        return f'<img src="{user.avatar.url}" width="50" />' if user.avatar else "-"

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
