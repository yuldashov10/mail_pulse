"""Константы для приложения mailings."""

EMAIL_LEN: int = 254
LAST_NAME_LEN: int = 100
FIRST_NAME_LEN: int = 100
PATRONYMIC_LEN: int = 100
SUBJECT_LEN: int = 255
STATUS_LEN: int = 20

from django.db.models import TextChoices


class MailingStatus(TextChoices):
    """Статусы рассылки."""

    CREATED = ("created", "Создана")
    RUNNING = ("running", "Запущена")
    COMPLETED = ("completed", "Завершена")


class AttemptStatus(TextChoices):
    """Статусы попытки рассылки."""

    SUCCESS = ("success", "Успешно")
    FAILED = ("failed", "Не успешно")
