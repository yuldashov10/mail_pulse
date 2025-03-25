"""Константы для приложения mailings."""

from django.db.models import TextChoices

EMAIL_LEN: int = 254
LAST_NAME_LEN: int = 100
FIRST_NAME_LEN: int = 100
PATRONYMIC_LEN: int = 100
SUBJECT_LEN: int = 255
STATUS_LEN: int = 20

DEFAULT_PAGE_SIZE: int = 5


class MailingStatus(TextChoices):
    """Статусы рассылки."""

    CREATED = ("created", "Создана")
    RUNNING = ("running", "Запущена")
    COMPLETED = ("completed", "Завершена")


class AttemptStatus(TextChoices):
    """Статусы попытки рассылки."""

    SUCCESS = ("success", "Успешно")
    FAILED = ("failed", "Не успешно")
