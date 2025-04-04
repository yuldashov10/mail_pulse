import pytest
from django.utils import timezone

from mailings.models import Message, Recipient


@pytest.fixture
def manager(django_user_model):
    """Создаёт пользователя с правами менеджера."""
    manager = django_user_model.objects.create_user(
        email="manager@example.com",
        username="manager",
        password="manager123",
        is_active=True,
    )
    manager.groups.create(name="Менеджеры")
    return manager


@pytest.fixture
def referer_client(client):
    """Клиент с поддержкой заголовка HTTP_REFERER."""

    def _set_referer(url):
        return client.get(url, HTTP_REFERER=url)

    return _set_referer


@pytest.fixture
def user(django_user_model):
    """Создаёт обычного пользователя."""
    return django_user_model.objects.create_user(
        email="user@example.com",
        username="username",
        password="pass123",
        is_active=True,
    )


@pytest.fixture
def message(user):
    """Создаёт тестовое сообщение."""
    return Message.objects.create(
        subject="Тест интеграции",
        body="Привет, это тест!",
        owner=user,
    )


@pytest.fixture
def recipient(user):
    """Создаёт тестового получателя."""
    return Recipient.objects.create(
        email="recipient@example.com",
        last_name="Иванов",
        first_name="Иван",
        owner=user,
    )


@pytest.fixture
def mailing_data(message, recipient):
    """Данные для создания рассылки."""
    now = timezone.now()
    return {
        "start_time": now + timezone.timedelta(minutes=10),
        "end_time": now + timezone.timedelta(days=1),
        "message": message.pk,
        "recipients": [recipient.pk],
    }
