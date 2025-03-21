from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import COUNTRY_LEN, PHONE_NUMBER_LEN


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(
        "Электронная почта",
        unique=True,
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        max_length=PHONE_NUMBER_LEN,
        blank=True,
    )
    country = models.CharField(
        max_length=COUNTRY_LEN,
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("email",)

    def __str__(self) -> str:
        return str(self.email)
