from django.core.management.base import BaseCommand, CommandError

from mailings.models import Mailing


class Command(BaseCommand):
    help = "Отправляет рассылку по указанному ID"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "mailing_id",
            type=int,
            help="ID рассылки для отправки",
        )

    def handle(self, *args, **kwargs):
        mailing_id = kwargs.get("mailing_id")
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            if mailing.status == "created":
                mailing.send_mailing()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Рассылка {mailing_id} успешно отправлена"
                    ),
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Рассылка {mailing_id} уже "
                        "была отправлена или завершена"
                    ),
                )
        except Mailing.DoesNotExist:
            raise CommandError(f"Рассылка с ID {mailing_id} не найдена")
