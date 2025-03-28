import uuid
from datetime import timedelta
from http import HTTPStatus

import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from users.models import EmailVerificationToken, User


@pytest.fixture
def referer_client(client):
    """Фикстура для установки HTTP_REFERER."""

    def _set_referer(url):
        return client.get(url, HTTP_REFERER=url)

    return _set_referer


@pytest.mark.django_db
def test_register_view_get(client):
    """Проверка GET-запроса к странице регистрации."""
    response = client.get(reverse("users:register"))

    assert response.status_code == HTTPStatus.OK
    assert "users/register.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_register_view_post_valid(client, mocker):
    """Проверка успешной регистрации."""
    mocker.patch("django.core.mail.send_mail")
    data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password1": "testpass123",
        "password2": "testpass123",
    }
    response = client.post(reverse("users:register"), data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:email_verification_sent")

    user = User.objects.get(email=data["email"])

    assert not user.is_active
    assert EmailVerificationToken.objects.filter(user=user).exists()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_register_view_post_invalid(client):
    """Проверка регистрации с некорректными данными."""
    data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password1": "testpass123",
        "password2": "wrongpass",
    }
    response = client.post(reverse("users:register"), data)

    assert response.status_code == HTTPStatus.OK
    assert not User.objects.filter(email=data["email"]).exists()


@pytest.mark.django_db
def test_verify_email_view_valid(client):
    """Проверка успешной верификации email."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        is_active=False,
    )
    token = EmailVerificationToken.objects.create(user=user)

    response = client.get(
        reverse("users:verify_email", kwargs={"token": token.token})
    )

    assert response.status_code == HTTPStatus.OK
    assert "users/email_verified.html" in [t.name for t in response.templates]

    user.refresh_from_db()

    assert user.is_active
    assert not EmailVerificationToken.objects.filter(
        token=token.token
    ).exists()


@pytest.mark.django_db
def test_verify_email_view_expired(client):
    """Проверка верификации с просроченным токеном."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        is_active=False,
    )
    token = EmailVerificationToken.objects.create(user=user)
    token.expires_at = timezone.now() - timedelta(minutes=1)
    token.save()

    response = client.get(
        reverse("users:verify_email", kwargs={"token": token.token})
    )

    assert response.status_code == HTTPStatus.OK
    assert "Срок действия ссылки истёк" in response.content.decode("UTF-8")


@pytest.mark.django_db
def test_verify_email_view_invalid(client):
    """Проверка верификации с неверным токеном."""
    response = client.get(
        reverse("users:verify_email", kwargs={"token": uuid.uuid4()})
    )

    assert response.status_code == HTTPStatus.OK
    assert "Недействительная ссылка" in response.content.decode("UTF-8")


@pytest.mark.django_db
def test_block_user_view_get_manager(client, django_user_model):
    """Проверка GET-запроса на страницу блокировки для менеджера."""
    manager = django_user_model.objects.create_user(
        email="manager@example.com",
        username="manager",
        password="managerpass123",
        is_active=True,
    )
    manager.groups.create(name=settings.NAME_MANAGERS_GROUP)
    user = django_user_model.objects.create_user(
        email="user@example.com",
        username="user",
        password="userpass123",
        is_active=True,
    )

    client.login(email="manager@example.com", password="managerpass123")
    response = client.get(
        reverse("users:user_block", kwargs={"pk": user.pk}),
    )

    assert response.status_code == HTTPStatus.OK
    assert "users/block_user_confirm.html" in [
        t.name for t in response.templates
    ]


@pytest.mark.django_db
def test_block_user_view_post_manager(
    client, django_user_model, referer_client
):
    """Проверка успешной блокировки пользователем-менеджером."""
    manager = django_user_model.objects.create_user(
        email="manager@example.com",
        username="manager",
        password="managerpass123",
        is_active=True,
    )
    manager.groups.create(name=settings.NAME_MANAGERS_GROUP)
    user = django_user_model.objects.create_user(
        email="user@example.com",
        username="user",
        password="userpass123",
        is_active=True,
    )

    client.login(email="manager@example.com", password="managerpass123")
    referer_url = reverse("mailings:message_list")
    response = client.post(
        reverse("users:user_block", kwargs={"pk": user.pk}),
        HTTP_REFERER=referer_url,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == referer_url

    user.refresh_from_db()

    assert user.is_blocked


@pytest.mark.django_db
def test_block_user_view_post_manager_no_referer(client, django_user_model):
    """Проверка редиректа без HTTP_REFERER."""
    manager = django_user_model.objects.create_user(
        email="manager@example.com",
        username="manager",
        password="managerpass123",
        is_active=True,
    )
    manager.groups.create(name=settings.NAME_MANAGERS_GROUP)
    user = django_user_model.objects.create_user(
        email="user@example.com",
        username="user",
        password="userpass123",
        is_active=True,
    )

    client.login(email="manager@example.com", password="managerpass123")
    response = client.post(
        reverse("users:user_block", kwargs={"pk": user.pk}),
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("mailings:mailing_list")

    user.refresh_from_db()

    assert user.is_blocked


@pytest.mark.django_db
def test_block_user_view_not_manager(client, django_user_model):
    """Проверка попытки блокировки не менеджером."""
    user = django_user_model.objects.create_user(
        email="user@example.com",
        username="user",
        password="userpass123",
        is_active=True,
    )
    other_user = django_user_model.objects.create_user(
        email="other@example.com",
        username="other",
        password="otherpass123",
        is_active=True,
    )

    client.login(email="user@example.com", password="userpass123")
    response = client.get(
        reverse("users:user_block", kwargs={"pk": other_user.pk})
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_block_user_view_self(client, django_user_model):
    """Проверка попытки заблокировать самого себя."""
    manager = django_user_model.objects.create_user(
        email="manager@example.com",
        username="manager",
        password="managerpass123",
        is_active=True,
    )
    manager.groups.create(name=settings.NAME_MANAGERS_GROUP)

    client.login(email="manager@example.com", password="managerpass123")
    response = client.post(
        reverse("users:user_block", kwargs={"pk": manager.pk})
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
