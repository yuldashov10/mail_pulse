import pytest
from django.utils import timezone

from mailings.constants import AttemptStatus, MailingStatus
from mailings.models import Mailing, MailingAttempt, Message, Recipient


@pytest.mark.django_db
class TestRecipientModel:

    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Создание тестового получателя."""
        self._recipient = Recipient.objects.create(
            email="recipient@example.com",
            last_name="Иванов",
            first_name="Иван",
            patronymic="Иванович",
            owner=user,
        )

    def test_recipient_str(self):
        """Проверка строкового представления получателя."""
        assert str(self._recipient) == "Иванов Иван Иванович"

    def test_recipient_full_name(self):
        """Проверка полного имени получателя."""
        assert self._recipient.full_name == "Иванов Иван Иванович"

    def test_recipient_fields(self):
        """Проверка полей получателя."""
        assert self._recipient.email == "recipient@example.com"
        assert self._recipient.last_name == "Иванов"
        assert self._recipient.first_name == "Иван"
        assert self._recipient.patronymic == "Иванович"
        assert self._recipient.owner.email == "user@example.com"


@pytest.mark.django_db
class TestMessageModel:

    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Создание тестового сообщения."""
        self._message = Message.objects.create(
            subject="Тестовое письмо",
            body="Привет, это тест!",
            owner=user,
        )

    def test_message_str(self):
        """Проверка строкового представления сообщения."""
        assert str(self._message) == "Тестовое письмо"

    def test_message_fields(self):
        """Проверка полей сообщения."""
        assert self._message.subject == "Тестовое письмо"
        assert self._message.body == "Привет, это тест!"
        assert self._message.owner.email == "user@example.com"


@pytest.mark.django_db
class TestMailingModel:

    @pytest.fixture(autouse=True)
    def setup(self, user, mocker):
        """Создание тестовой рассылки."""
        self._message = Message.objects.create(
            subject="Тестовое письмо",
            body="Тест",
            owner=user,
        )
        self._recipient = Recipient.objects.create(
            email="recipient@example.com",
            last_name="Иванов",
            first_name="Иван",
            owner=user,
        )
        self._mailing = Mailing.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=self._message,
            owner=user,
        )
        self._mailing.recipients.add(self._recipient)

        mocker.patch("django.core.mail.send_mail")

    def test_mailing_str(self):
        """Проверка строкового представления рассылки."""
        assert (
            str(self._mailing) == f"Тестовое письмо ({MailingStatus.CREATED})"
        )

    def test_mailing_fields(self):
        """Проверка полей рассылки."""
        assert self._mailing.status == MailingStatus.CREATED
        assert self._mailing.message == self._message
        assert self._recipient in self._mailing.recipients.all()

    def test_send_mailing_success(self):
        """Проверка успешной отправки рассылки."""
        self._mailing.send_mailing()
        self._mailing.refresh_from_db()

        assert self._mailing.status == MailingStatus.COMPLETED

        attempt = MailingAttempt.objects.get(mailing=self._mailing)

        assert attempt.status == AttemptStatus.SUCCESS

    def test_send_mailing_owner_blocked(self):
        """Проверка отправки рассылки с заблокированным владельцем."""
        self._mailing.owner.is_blocked = True
        self._mailing.owner.save()
        self._mailing.send_mailing()
        self._mailing.refresh_from_db()

        assert self._mailing.status == MailingStatus.CREATED

        attempt = MailingAttempt.objects.get(mailing=self._mailing)

        assert attempt.status == AttemptStatus.FAILED
        assert "Владелец рассылки заблокирован" in attempt.server_response


@pytest.mark.django_db
class TestMailingAttemptModel:

    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Создание тестовой попытки рассылки."""
        self._message = Message.objects.create(
            subject="Тестовое письмо",
            body="Тест",
            owner=user,
        )
        self._recipient = Recipient.objects.create(
            email="recipient@example.com",
            last_name="Иванов",
            first_name="Иван",
            owner=user,
        )
        self._mailing = Mailing.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            message=self._message,
            owner=user,
        )
        self._mailing.recipients.add(self._recipient)

    def test_mailing_attempt_create(self):
        """Проверка создания попытки рассылки."""
        attempt = MailingAttempt.objects.create(
            mailing=self._mailing, status=AttemptStatus.SUCCESS
        )

        assert attempt.mailing == self._mailing
        assert attempt.status == AttemptStatus.SUCCESS
