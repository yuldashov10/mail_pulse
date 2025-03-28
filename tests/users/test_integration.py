from http import HTTPStatus

import pytest
from django.urls import reverse

from users.models import EmailVerificationToken, User


@pytest.mark.django_db
def test_registration_to_verification(client, mocker):
    """Регистрация → верификация."""
    mocker.patch("django.core.mail.send_mail")

    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password1": "testpass123",
        "password2": "testpass123",
    }
    response = client.post(reverse("users:register"), data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("users:email_verification_sent")

    user = User.objects.get(email="test@example.com")

    assert not user.is_active

    token = EmailVerificationToken.objects.get(user=user)
    response = client.get(
        reverse(
            "users:verify_email",
            kwargs={"token": token.token},
        )
    )

    assert response.status_code == HTTPStatus.OK

    user.refresh_from_db()

    assert user.is_active

    response = client.post(
        reverse("users:login"),
        {
            "username": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("home")
