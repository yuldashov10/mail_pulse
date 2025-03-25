from django.conf import settings
from django.core.mail import send_mail
from django.db import models

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

    def send_mailing(self):
        """Отправляет рассылки всем получателям."""
        try:
            send_mail(
                self.message.subject,
                self.message.body,
                settings.EMAIL_HOST_USER,
                [recipient.email for recipient in self.recipients.all()],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=self,
                status=AttemptStatus.SUCCESS,
                server_response="Сообщение успешно отправлено",
            )
            self.status = MailingStatus.COMPLETED
            self.save()
        except Exception as err_msg:
            MailingAttempt.objects.create(
                mailing=self,
                status=AttemptStatus.FAILED,
                server_response=str(err_msg),
            )

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
