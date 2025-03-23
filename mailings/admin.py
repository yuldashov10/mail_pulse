from django.contrib import admin

from mailings.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Админка для получателей."""

    list_display = ("email", "full_name", "owner")
    list_filter = ("owner",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для сообщений."""

    list_display = ("subject", "owner")
    list_filter = ("owner",)
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админка для рассылок."""

    list_display = ("message", "status", "start_time", "end_time", "owner")
    list_filter = ("status", "owner")
    search_fields = ("message__subject",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Админка для попыток рассылки."""

    list_display = ("mailing", "status", "attempt_time")
    list_filter = ("status", "mailing__owner")
    search_fields = ("mailing__message__subject",)
