from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Recipient


class RecipientListView(LoginRequiredMixin, ListView):
    """Список получателей."""

    model = Recipient
    template_name = "mailings/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        return Recipient.objects.for_user(self.request.user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о получателе."""

    model = Recipient
    template_name = "mailings/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self):
        return Recipient.objects.for_user(self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового получателя."""

    model = Recipient
    fields = ["last_name", "first_name", "patronymic", "email", "comment"]
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя."""

    model = Recipient
    fields = ["last_name", "first_name", "patronymic", "email", "comment"]
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def get_queryset(self):
        return Recipient.objects.for_user(self.request.user)

    def form_valid(self, form):
        if form.instance.owner != self.request.user:
            return self.handle_no_permission()
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя."""

    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def get_queryset(self):
        return Recipient.objects.for_user(self.request.user)
