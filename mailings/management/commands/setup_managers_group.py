from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Настраивает группу 'Менеджеры' с необходимыми разрешениями."""

    help = (
        "Создаёт группу 'Менеджеры' и назначает "
        "ей разрешения для управления рассылками."
    )

    def handle(self, *args, **options) -> None:
        group, created = Group.objects.get_or_create(name="Менеджеры")
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
            self.style.SUCCESS(f"Группа 'Менеджеры' успешно {action}")
        )
