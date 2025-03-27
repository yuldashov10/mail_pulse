from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from mailings.constants import (
    EMAIL_LEN,
    FIRST_NAME_LEN,
    LAST_NAME_LEN,
    PATRONYMIC_LEN,
    STATUS_LEN,
    SUBJECT_LEN,
    AttemptStatus,
    MailingStatus,
)
from mailings.managers import MailingManager, MessageManager, RecipientManager


class Recipient(models.Model):
    """Модель получателя рассылки."""

    email = models.EmailField(
        "Электронная почта",
        max_length=EMAIL_LEN,
        unique=True,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=LAST_NAME_LEN,
    )
    first_name = models.CharField(
        "Имя",
        max_length=FIRST_NAME_LEN,
    )
    patronymic = models.CharField(
        "Отчество",
        max_length=PATRONYMIC_LEN,
        blank=True,
    )
    comment = models.TextField(
        "Комментарий",
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_recipients",
        verbose_name="Владелец",
    )
    objects = RecipientManager()

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ("last_name", "first_name")
        permissions = (
            (
                "can_view_all_recipients",
                "Может просматривать всех получателей",
            ),
        )

    @property
    def full_name(self) -> str:
        """Возвращает полное ФИО."""
        parts = [self.last_name, self.first_name]

        if self.patronymic:
            parts.append(self.patronymic)

        return " ".join(map(str, parts))

    def __str__(self) -> str:
        return self.full_name


class Message(models.Model):
    """Модель сообщения для рассылки."""

    subject = models.CharField(
        "Тема письма",
        max_length=SUBJECT_LEN,
    )
    body = models.TextField(
        "Тело письма",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_messages",
        verbose_name="Владелец",
    )
    objects = MessageManager()

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ("subject",)
        permissions = (
            ("can_view_all_messages", "Может просматривать все сообщения"),
        )

    def __str__(self) -> str:
        return str(self.subject)


class Mailing(models.Model):
    """Модель рассылки."""

    start_time = models.DateTimeField(
        "Дата и время первой отправки",
    )
    end_time = models.DateTimeField(
        "Дата и время окончания",
    )
    status = models.CharField(
        "Статус",
        max_length=STATUS_LEN,
        choices=MailingStatus.choices,
        default=MailingStatus.CREATED,
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
        related_name="mailings",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_mailings",
        verbose_name="Владелец",
    )
    objects = MailingManager()

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ("start_time",)
        permissions = (
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_block_mailings", "Может отключать рассылки"),
        )

    def _log_attempt(self, status: str, server_response: str) -> None:
        """Создаёт запись о попытке отправки."""
        MailingAttempt.objects.create(
            mailing=self,
            status=status,
            server_response=server_response,
        )

    def _set_running_status(self) -> None:
        """Устанавливает статус 'Запущена' перед отправкой."""
        self.status = MailingStatus.RUNNING
        self.save()

    def _can_send(self) -> bool:
        """Проверяет, можно ли отправить рассылку."""
        now = timezone.now()

        if self.owner.is_blocked:
            self._log_attempt(
                AttemptStatus.FAILED,
                "Владелец рассылки заблокирован",
            )
            return False

        if self.status == MailingStatus.DISABLED:
            self._log_attempt(
                AttemptStatus.FAILED,
                "Рассылка отключена менеджером",
            )
            return False

        if self.start_time > now:
            self._log_attempt(
                AttemptStatus.FAILED,
                "Рассылка ещё не началась",
            )
            return False

        if self.end_time and self.end_time < now:
            self._log_attempt(
                AttemptStatus.FAILED,
                "Срок действия рассылки истёк",
            )
            return False

        return True

    def _send_to_recipients(self) -> bool:
        """Отправляет письма каждому получателю и возвращает True, если все успешно."""
        recipients: QuerySet = self.recipients.all()
        all_success: bool = True

        for recipient in recipients:
            try:
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                self._log_attempt(
                    AttemptStatus.SUCCESS,
                    "Сообщение успешно отправлено",
                )
            except Exception as err_msg:
                self._log_attempt(
                    AttemptStatus.FAILED,
                    "Ошибка отправки",
                )
                all_success = False

        return all_success

    def _update_final_status(self, all_success: bool) -> None:
        """Обновляет финальный статус рассылки."""
        if not all_success:
            self.status = MailingStatus.RUNNING
        else:
            self.status = MailingStatus.COMPLETED
        self.save()

    def send_mailing(self) -> None:
        """
        Отправляет рассылки всем получателям с учётом статуса и блокировки.
        """
        if not self._can_send():
            return

        self._set_running_status()
        all_success = self._send_to_recipients()

        self._update_final_status(all_success)

    def __str__(self) -> str:
        return f"{self.message.subject} ({self.status})"


class MailingAttempt(models.Model):
    """Модель попытки отправки рассылки."""

    attempt_time = models.DateTimeField(
        "Дата и время попытки",
        auto_now_add=True,
    )
    status = models.CharField(
        "Статус",
        max_length=STATUS_LEN,
        choices=AttemptStatus.choices,
    )
    server_response = models.TextField(
        "Ответ почтового сервера",
        blank=True,
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ("-attempt_time",)

    def __str__(self) -> str:
        return f"{self.mailing} - {self.status.name}"
