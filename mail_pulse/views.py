from typing import Any

from django.views.generic import TemplateView

from mailings.models import Mailing, Recipient


class HomeView(TemplateView):
    """Главная страница с базовой статистикой."""

    template_name = "home.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            context["stats"] = {
                "total_mailings": Mailing.objects.for_user(user).count(),
                "active_mailings": Mailing.objects.for_user(user)
                .filter(status="running")
                .count(),
                "unique_recipients": Recipient.objects.for_user(user)
                .distinct()
                .count(),
            }
        return context
