from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "email", "username", "first_name", "last_name", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("id",)
    fieldsets = DjangoUserAdmin.fieldsets + (("Профиль", {"fields": ("avatar",)}),)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Профиль", {"fields": ("first_name", "last_name", "avatar")}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = (
        "user__email",
        "author__email",
        "user__username",
        "author__username",
    )

