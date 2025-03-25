from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from mailings.models import Mailing, Recipient


class HomeView(LoginRequiredMixin, ListView):
    """Главная страница с базовой статистикой."""

    template_name = "home.html"
    context_object_name = "stats"

    def get_queryset(self) -> dict[str, int]:
        user = self.request.user
        return {
            "total_mailings": Mailing.objects.for_user(user).count(),
            "active_mailings": Mailing.objects.for_user(user)
            .filter(status="running")
            .count(),
            "unique_recipients": Recipient.objects.for_user(user)
            .distinct()
            .count(),
        }
