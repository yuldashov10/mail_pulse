# Generated by Django 4.2 on 2025-03-23 20:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Mailing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        verbose_name="Дата и время первой отправки"
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        verbose_name="Дата и время окончания"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Создана"),
                            ("running", "Запущена"),
                            ("completed", "Завершена"),
                        ],
                        default="created",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рассылка",
                "verbose_name_plural": "Рассылки",
                "ordering": ("start_time",),
                "permissions": (
                    (
                        "can_view_all_mailings",
                        "Может просматривать все рассылки",
                    ),
                    ("can_block_mailings", "Может отключать рассылки"),
                ),
            },
        ),
        migrations.CreateModel(
            name="Recipient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        verbose_name="Электронная почта",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(max_length=100, verbose_name="Фамилия"),
                ),
                (
                    "first_name",
                    models.CharField(max_length=100, verbose_name="Имя"),
                ),
                (
                    "patronymic",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Отчество"
                    ),
                ),
                (
                    "comment",
                    models.TextField(blank=True, verbose_name="Комментарий"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_recipients",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Получатель",
                "verbose_name_plural": "Получатели",
                "ordering": ("last_name", "first_name"),
                "permissions": (
                    (
                        "can_view_all_recipients",
                        "Может просматривать всех получателей",
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        max_length=255, verbose_name="Тема письма"
                    ),
                ),
                ("body", models.TextField(verbose_name="Тело письма")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сообщение",
                "verbose_name_plural": "Сообщения",
                "ordering": ("subject",),
                "permissions": (
                    (
                        "can_view_all_messages",
                        "Может просматривать все сообщения",
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="MailingAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attempt_time",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время попытки"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("success", "Успешно"),
                            ("failed", "Не успешно"),
                        ],
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "server_response",
                    models.TextField(
                        blank=True, verbose_name="Ответ почтового сервера"
                    ),
                ),
                (
                    "mailing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mailings.mailing",
                        verbose_name="Рассылка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Попытка рассылки",
                "verbose_name_plural": "Попытки рассылки",
                "ordering": ("-attempt_time",),
            },
        ),
        migrations.AddField(
            model_name="mailing",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="mailings.message",
                verbose_name="Сообщение",
            ),
        ),
        migrations.AddField(
            model_name="mailing",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_mailings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Владелец",
            ),
        ),
        migrations.AddField(
            model_name="mailing",
            name="recipients",
            field=models.ManyToManyField(
                to="mailings.recipient", verbose_name="Получатели"
            ),
        ),
    ]
