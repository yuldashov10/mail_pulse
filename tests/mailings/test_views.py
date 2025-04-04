from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone

from mailings.constants import MailingStatus
from mailings.models import Mailing, Message, Recipient


@pytest.mark.django_db
class TestRecipientViews:

    @pytest.fixture(autouse=True)
    def setup(self, user, client):
        """Создание тестового получателя и настройка клиента."""
        self.user = user
        self.client = client
        self._recipient = Recipient.objects.create(
            email="recipient@example.com",
            last_name="Иванов",
            first_name="Иван",
            owner=self.user,
        )

    def test_recipient_list_view(self):
        """Проверка отображения списка получателей."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.get(reverse("mailings:recipient_list"))

        assert response.status_code == HTTPStatus.OK
        assert "mailings/recipient_list.html" in [
            t.name for t in response.templates
        ]
        assert self._recipient in response.context["recipients"]

    def test_recipient_create_view_post(self):
        """Проверка создания нового получателя."""
        self.client.login(email="user@example.com", password="pass123")
        data = {
            "email": "new@example.com",
            "last_name": "Петров",
            "first_name": "Пётр",
            "patronymic": "",
            "comment": "Тест",
        }

        response = self.client.post(
            reverse("mailings:recipient_create"),
            data,
        )

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("mailings:recipient_list")
        assert Recipient.objects.filter(email="new@example.com").exists()


@pytest.mark.django_db
class TestMessageViews:

    @pytest.fixture(autouse=True)
    def setup(self, user, client):
        """Создание тестового сообщения и настройка клиента."""
        self.user = user
        self.client = client
        self._message = Message.objects.create(
            subject="Тест", body="Привет", owner=self.user
        )

    def test_message_list_view(self):
        """Проверка отображения списка сообщений."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.get(reverse("mailings:message_list"))

        assert response.status_code == HTTPStatus.OK
        assert "mailings/message_list.html" in [
            t.name for t in response.templates
        ]
        assert self._message in response.context["messages"]

    def test_message_create_view_post(self):
        """Проверка создания нового сообщения."""
        self.client.login(email="user@example.com", password="pass123")
        data = {"subject": "Новое письмо", "body": "Тестовое тело"}

        response = self.client.post(
            reverse("mailings:message_create"),
            data,
        )

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("mailings:message_list")
        assert Message.objects.filter(subject="Новое письмо").exists()


@pytest.mark.django_db
class TestMailingViews:

    @pytest.fixture(autouse=True)
    def setup(self, user, manager, client, mocker):
        """Создание тестовой рассылки и настройка клиента."""
        self.user = user
        self.manager = manager
        self.client = client
        self._message = Message.objects.create(
            subject="Тест",
            body="Привет",
            owner=self.user,
        )
        self._recipient = Recipient.objects.create(
            email="recipient@example.com",
            last_name="Иванов",
            first_name="Иван",
            owner=self.user,
        )
        self.mailing = Mailing.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=self._message,
            owner=self.user,
        )
        self.mailing.recipients.add(self._recipient)

        mocker.patch("django.core.mail.send_mail")

    def test_mailing_list_view(self):
        """Проверка отображения списка рассылок."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.get(reverse("mailings:mailing_list"))

        assert response.status_code == HTTPStatus.OK
        assert "mailings/mailing_list.html" in [
            t.name for t in response.templates
        ]
        assert self.mailing in response.context["mailings"]

    def test_mailing_detail_view_get(self):
        """Проверка отображения деталей рассылки."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.get(
            reverse(
                "mailings:mailing_detail",
                kwargs={"pk": self.mailing.pk},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "mailings/mailing_detail.html" in [
            t.name for t in response.templates
        ]
        assert response.context["mailing"] == self.mailing

    def test_mailing_detail_view_post(self):
        """Проверка отправки рассылки."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.post(
            reverse(
                "mailings:mailing_detail",
                kwargs={"pk": self.mailing.pk},
            )
        )

        assert response.status_code == HTTPStatus.FOUND
        self.mailing.refresh_from_db()
        assert self.mailing.status == MailingStatus.COMPLETED

    def test_disable_mailing_view_get_manager(self):
        """
        Проверка отображения страницы отключения рассылки менеджером.
        """
        self.client.login(
            email="manager@example.com",
            password="manager123",
        )

        response = self.client.get(
            reverse(
                "mailings:mailing_disable",
                kwargs={"pk": self.mailing.pk},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "mailings/mailing_disable_confirm.html" in [
            t.name for t in response.templates
        ]

    def test_disable_mailing_view_post_manager(self, referer_client):
        """Проверка отключения рассылки менеджером."""
        self.client.login(
            email="manager@example.com",
            password="manager123",
        )
        referer_url = reverse("mailings:mailing_list")

        response = self.client.post(
            reverse(
                "mailings:mailing_disable",
                kwargs={"pk": self.mailing.pk},
            ),
            HTTP_REFERER=referer_url,
        )

        assert response.status_code == HTTPStatus.FOUND
        assert response.url == referer_url

        self.mailing.refresh_from_db()

        assert self.mailing.status == MailingStatus.DISABLED

    def test_disable_mailing_view_not_manager(self):
        """Проверка запрета отключения рассылки не менеджером."""
        self.client.login(email="user@example.com", password="pass123")

        response = self.client.get(
            reverse(
                "mailings:mailing_disable",
                kwargs={"pk": self.mailing.pk},
            )
        )

        assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
class TestHomeView:

    def test_home_view_anonymous(self, client):
        """
        Проверка отображения главной страницы для анонимного пользователя.
        """
        response = client.get(reverse("home"))

        assert response.status_code == HTTPStatus.OK
        assert "home.html" in [t.name for t in response.templates]
        assert "stats" not in response.context

    def test_home_view_authenticated_empty(self, user, client):
        """
        Проверка главной страницы для авторизованного пользователя без данных.
        """
        client.login(email="user@example.com", password="pass123")

        response = client.get(reverse("home"))

        assert response.status_code == HTTPStatus.OK
        assert "home.html" in [t.name for t in response.templates]
        assert "stats" in response.context
        assert response.context["stats"] == {
            "total_mailings": 0,
            "active_mailings": 0,
            "unique_recipients": 0,
        }

    def test_home_view_authenticated_with_data(self, user, client):
        """Проверка главной страницы с данными пользователя."""
        _message = Message.objects.create(
            subject="Тестовое сообщение",
            body="Тест",
            owner=user,
        )
        recipient_1 = Recipient.objects.create(
            email="recipient1@example.com",
            last_name="Иванов",
            first_name="Иван",
            owner=user,
        )
        recipient_2 = Recipient.objects.create(
            email="recipient2@example.com",
            last_name="Петров",
            first_name="Пётр",
            owner=user,
        )
        mailing_1 = Mailing.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=_message,
            owner=user,
            status=MailingStatus.RUNNING,
        )
        mailing_1.recipients.add(recipient_1)
        mailing_2 = Mailing.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=_message,
            owner=user,
            status=MailingStatus.COMPLETED,
        )
        mailing_2.recipients.add(recipient_2)

        client.login(email="user@example.com", password="pass123")

        response = client.get(reverse("home"))

        assert response.status_code == HTTPStatus.OK
        assert "home.html" in [t.name for t in response.templates]
        assert "stats" in response.context
        assert response.context["stats"] == {
            "total_mailings": 2,
            "active_mailings": 1,
            "unique_recipients": 2,
        }
