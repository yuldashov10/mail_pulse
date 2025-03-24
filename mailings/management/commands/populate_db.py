import random

from django.core.management.base import BaseCommand
from faker import Faker

from mailings.constants import MailingStatus
from mailings.models import Mailing, Message, Recipient
from users.models import User


class Command(BaseCommand):
    """Заполняет базу данных случайными данными."""

    help = (
        "Генерирует случайных пользователей, "
        "получателей, сообщения и рассылки."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker("ru_RU")

    def create_users(self) -> list[User]:
        """Создаёт случайных пользователей."""
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                email=self.fake.email(),
                username=self.fake.user_name(),
                password="testpass123",
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                phone_number=self.fake.phone_number()[:15],
                country=self.fake.country(),
            )
            users.append(user)
        return users

    def create_recipients(self, user: User) -> None:
        """Создаёт случайных получателей для пользователя."""
        for _ in range(random.randint(3, 10)):
            Recipient.objects.create(
                last_name=self.fake.last_name(),
                first_name=self.fake.first_name(),
                patronymic=self.fake.middle_name(),
                email=self.fake.email(),
                comment=self.fake.text(max_nb_chars=200),
                owner=user,
            )

    def create_messages(self, user: User) -> None:
        """Создаёт случайные сообщения для пользователя."""
        for _ in range(random.randint(2, 5)):
            Message.objects.create(
                subject=self.fake.sentence(nb_words=4),
                body=self.fake.paragraph(nb_sentences=3),
                owner=user,
            )

    def create_mailings(self, user: User) -> None:
        """Создаёт случайные рассылки для пользователя."""
        messages = Message.objects.filter(owner=user)
        recipients = Recipient.objects.filter(owner=user)

        if not messages.exists() or not recipients.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Пропущены рассылки для {user.email}: "
                    "нет сообщений или получателей."
                )
            )
            return

        for _ in range(random.randint(1, 3)):
            mailing = Mailing.objects.create(
                start_time=self.fake.past_datetime(start_date="-30d"),
                end_time=self.fake.future_datetime(end_date="+30d"),
                status=random.choice(MailingStatus.values),
                message=random.choice(messages),
                owner=user,
            )
            mailing.recipients.set(
                random.sample(
                    list(recipients),
                    k=min(random.randint(1, 3), recipients.count()),
                )
            )

    def handle(self, *args, **options):
        """Основной метод команды."""
        for user in self.create_users():
            self.create_recipients(user)
            self.create_messages(user)
            self.create_mailings(user)

        self.stdout.write(
            self.style.SUCCESS(
                "База данных успешно заполнена случайными данными."
            )
        )
