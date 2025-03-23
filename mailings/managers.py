from django.db import models


class RecipientManager(models.Manager):
    """Менеджер получателя рассылки."""

    def for_user(self, user) -> models.QuerySet:
        if user.has_perm("mailings.can_view_all_recipients"):
            return self.all()
        return self.filter(owner=user)


class MessageManager(models.Manager):
    """Менеджер сообщения для рассылки."""

    def for_user(self, user) -> models.QuerySet:
        if user.has_perm("mailings.can_view_all_messages"):
            return self.all()
        return self.filter(owner=user)


class MailingManager(models.Manager):
    """Менеджер рассылки."""

    def for_user(self, user) -> models.QuerySet:
        if user.has_perm("mailings.can_view_all_mailings"):
            return self.all()
        return self.filter(owner=user)
