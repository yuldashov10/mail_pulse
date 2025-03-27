from django.conf import settings

from users.models import User


def is_manager(user: User) -> bool:
    return user.groups.filter(name=settings.NAME_MANAGERS_GROUP).exists()
