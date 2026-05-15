from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


username_validator = RegexValidator(regex=settings.USERNAME_REGEX, message="Введите корректный username.")


class User(AbstractUser):
    username = models.CharField("Логин", max_length=150, unique=True, validators=[username_validator])
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    email = models.EmailField("Email", max_length=254, unique=True)
    avatar = models.ImageField("Аватар", upload_to="users/avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_subscriptions", verbose_name="Подписчик")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_subscriptions", verbose_name="Автор")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "author"), name="unique_subscription"),
            models.CheckConstraint(check=~models.Q(user=models.F("author")), name="prevent_self_subscription"),
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} -> {self.author}"
