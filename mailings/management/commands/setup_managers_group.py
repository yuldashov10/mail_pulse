from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Настраивает группу менеджеров с необходимыми разрешениями."""

    help = (
        f"Создаёт группу '{settings.NAME_MANAGERS_GROUP}' и назначает "
        "ей разрешения для управления рассылками."
    )

    def handle(self, *args, **options) -> None:
        group, created = Group.objects.get_or_create(
            name=settings.NAME_MANAGERS_GROUP
        )
        permission_codenames: tuple[str, ...] = (
            "can_view_all_recipients",
            "can_view_all_messages",
            "can_view_all_mailings",
            "can_block_mailings",
        )
        permissions = Permission.objects.filter(
            codename__in=permission_codenames
        )

        if not permissions.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Не найдены указанные разрешения. "
                    "Убедитесь, что они добавлены в модели"
                )
            )
            return

        group.permissions.set(permissions)
        action: str = "создана и настроена" if created else "обновлена"

        self.stdout.write(
            self.style.SUCCESS(
                f"Группа '{settings.NAME_MANAGERS_GROUP}' успешно {action}"
            )
        )
