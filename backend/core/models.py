from django.core.validators import MinValueValidator
from django.db import models


class NamedModel(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="Название")

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name


class CreatedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ("-created",)


class AmountMixin(models.Model):
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        abstract = True

