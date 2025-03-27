from django.conf import settings
from django.db import models


class BaseManager(models.Manager):
    def for_user(self, user) -> models.QuerySet:
        if user.groups.filter(name=settings.NAME_MANAGERS_GROUP).exists():
            return self.all()
        return self.filter(owner=user)


class RecipientManager(BaseManager):
    """Менеджер получателя рассылки."""

    pass


class MessageManager(BaseManager):
    """Менеджер сообщения для рассылки."""

    pass


class MailingManager(BaseManager):
    """Менеджер рассылки."""

    pass
