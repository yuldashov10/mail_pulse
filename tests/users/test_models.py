from datetime import timedelta

import pytest
from django.utils import timezone

from users.models import EmailVerificationToken, User


@pytest.mark.django_db
def test_user_str():
    """Проверка метода __str__ модели User."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )

    assert str(user) == "test@example.com"


@pytest.mark.django_db
def test_user_fields():
    """Проверка полей модели User."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert not user.is_active
    assert not user.is_blocked


@pytest.mark.django_db
def test_email_verification_token_str():
    """Проверка метода __str__ токена."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )
    token = EmailVerificationToken.objects.create(user=user)

    assert str(token) == f"Токен для {user}"


@pytest.mark.django_db
def test_email_verification_token_expires_at_default():
    """Проверка установки expires_at при создании."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )
    token = EmailVerificationToken.objects.create(user=user)
    expected_expiry = token.created_at + timedelta(minutes=60)

    assert abs((token.expires_at - expected_expiry).total_seconds()) < 1


@pytest.mark.django_db
def test_email_verification_token_is_valid_true():
    """Проверка метода is_valid для действительного токена."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )
    token = EmailVerificationToken.objects.create(user=user)

    assert token.is_valid()


@pytest.mark.django_db
def test_email_verification_token_is_valid_false():
    """Проверка метода is_valid для просроченного токена."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )
    token = EmailVerificationToken.objects.create(user=user)
    token.expires_at = timezone.now() - timedelta(minutes=1)
    token.save()

    assert not token.is_valid()
