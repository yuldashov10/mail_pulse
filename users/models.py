import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from users.constants import (
    COUNTRY_LEN,
    PHONE_NUMBER_LEN,
    VERIFICATION_TOKEN_EXPIRES_MINUTE,
)


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
        "Номер телефона",
        max_length=PHONE_NUMBER_LEN,
        blank=True,
    )
    country = models.CharField(
        "Страна",
        max_length=COUNTRY_LEN,
        blank=True,
    )
    is_active = models.BooleanField(
        "Активен",
        default=False,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("email",)

    def __str__(self) -> str:
        return str(self.email)


class EmailVerificationToken(models.Model):
    """Модель для токенов подтверждения email."""

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    expires_at = models.DateTimeField("Истекает")

    class Meta:
        verbose_name = "Токен подтверждения email"
        verbose_name_plural = "Токены подтверждения email"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(
                minutes=VERIFICATION_TOKEN_EXPIRES_MINUTE
            )
        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        return self.expires_at > timezone.now()

    def __str__(self) -> str:
        return f"Токен для {self.user}"
