from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone

from mailings.constants import MailingStatus
from mailings.models import Mailing, MailingAttempt


@pytest.mark.django_db
class TestMailingIntegration:

    @pytest.fixture(autouse=True)
    def setup(self, user, client, mocker):
        """Базовая настройка для всех тестов."""
        self._user = user
        self.client = client

        mocker.patch("django.core.mail.send_mail")

    def test_create_mailing(self, mailing_data):
        """Проверка создания рассылки через форму."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.post(
            reverse("mailings:mailing_create"),
            mailing_data,
            follow=True,
        )

        assert response.status_code == HTTPStatus.OK
        assert (
            reverse("mailings:mailing_list") in response.request["PATH_INFO"]
        )
        assert Mailing.objects.filter(
            owner=self._user,
            message__subject="Тест интеграции",
        ).exists()

    def test_send_mailing(self, message, recipient):
        """Проверка отправки существующей рассылки."""
        mailing = Mailing.objects.create(
            start_time=timezone.now() - timezone.timedelta(minutes=1),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=message,
            owner=self._user,
        )
        mailing.recipients.add(recipient)
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.post(
            reverse(
                "mailings:mailing_detail",
                kwargs={"pk": mailing.pk},
            )
        )

        assert response.status_code == HTTPStatus.FOUND

        mailing.refresh_from_db()

        assert mailing.status == MailingStatus.COMPLETED
        assert MailingAttempt.objects.filter(
            mailing=mailing, status="success"
        ).exists()

    def test_create_and_send_mailing_invalid_start_time(
        self, message, recipient
    ):
        """Проверка ошибки при создании рассылки с некорректным start_time."""
        invalid_data = {
            "start_time": timezone.now() - timezone.timedelta(minutes=1),
            "end_time": timezone.now() + timezone.timedelta(days=1),
            "message": message.pk,
            "recipients": [recipient.pk],
        }
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.post(
            reverse("mailings:mailing_create"), invalid_data
        )

        assert response.status_code == HTTPStatus.OK
        assert (
            "Дата и время первой отправки не могут быть в прошлом"
            in response.content.decode("utf-8")
        )
        assert not Mailing.objects.filter(
            message__subject="Тест интеграции"
        ).exists()
