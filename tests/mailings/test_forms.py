import pytest
from django.utils import timezone

from mailings.forms import MailingForm


class TestMailingForm:

    @pytest.fixture
    def data(self, message, recipient):
        """Базовые данные для формы рассылки."""
        return {
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(days=1),
            "message": message.pk,
            "recipients": [recipient.pk],
        }

    def test_mailing_form_valid(self, data):
        """Проверка валидности формы с корректными данными."""
        form = MailingForm(data=data)

        assert form.is_valid()

    def test_mailing_form_invalid_start_time(self, data):
        """Проверка ошибки при start_time в прошлом."""
        data["start_time"] = timezone.now() - timezone.timedelta(seconds=10)

        form = MailingForm(data=data)

        assert not form.is_valid()
        assert (
            "Дата и время первой отправки не могут быть в прошлом"
            in form.errors["start_time"]
        )

    def test_mailing_form_invalid_end_time(self, data):
        """Проверка ошибки при end_time раньше start_time."""
        data["start_time"] = timezone.now() + timezone.timedelta(days=1)
        data["end_time"] = timezone.now() + timezone.timedelta(minutes=1)

        form = MailingForm(data=data)

        assert not form.is_valid()
        assert (
            "Дата окончания должна быть позже даты начала"
            in form.errors["__all__"]
        )
