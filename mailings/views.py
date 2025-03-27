from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from mailings.constants import DEFAULT_PAGE_SIZE, MailingStatus
from mailings.forms import MailingForm
from mailings.models import Mailing, MailingAttempt, Message, Recipient
from utils import is_manager


class RecipientListView(LoginRequiredMixin, ListView):
    """Список получателей."""

    model = Recipient
    template_name = "mailings/recipient_list.html"
    context_object_name = "recipients"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return Recipient.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["is_manager"] = is_manager(self.request.user)

        return context


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о получателе."""

    model = Recipient
    template_name = "mailings/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self) -> QuerySet:
        return Recipient.objects.for_user(self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового получателя."""

    model = Recipient
    fields = ["last_name", "first_name", "patronymic", "email", "comment"]
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя."""

    model = Recipient
    fields = ["last_name", "first_name", "patronymic", "email", "comment"]
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def get_queryset(self) -> QuerySet:
        return Recipient.objects.for_user(self.request.user)

    def form_valid(self, form) -> HttpResponseRedirect:
        if form.instance.owner != self.request.user:
            return self.handle_no_permission()
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя."""

    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipient_list")

    def get_queryset(self) -> QuerySet:
        return Recipient.objects.for_user(self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    """Список сообщений."""

    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return Message.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["is_manager"] = is_manager(self.request.user)

        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о сообщении."""

    model = Message
    template_name = "mailings/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        return Message.objects.for_user(self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сообщения."""

    model = Message
    fields = ["subject", "body"]
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование сообщения."""

    model = Message
    fields = ["subject", "body"]
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.for_user(self.request.user)

    def form_valid(self, form):
        if form.instance.owner != self.request.user:
            return self.handle_no_permission()
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения."""

    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.for_user(self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок."""

    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return Mailing.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["is_manager"] = is_manager(self.request.user)

        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о рассылке."""

    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self) -> QuerySet:
        return Mailing.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Добавление пагинации для получателей в контекст."""
        context = super().get_context_data(**kwargs)

        paginator = Paginator(
            self.object.recipients.all(),
            DEFAULT_PAGE_SIZE,
        )
        page_number = self.request.GET.get("recipients_page")
        recipients_page = paginator.get_page(page_number)

        context["recipients_page"] = recipients_page
        context["is_paginated"] = recipients_page.has_other_pages()
        context["is_manager"] = is_manager(self.request.user)

        return context

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Обработка отправки рассылки."""
        mailing = self.get_object()
        if mailing.status == MailingStatus.CREATED:
            mailing.send_mailing()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "mailings:mailing_detail",
            kwargs={"pk": self.get_object().pk},
        )


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["message"].queryset = Message.objects.for_user(
            self.request.user
        )
        form.fields["recipients"].queryset = Recipient.objects.for_user(
            self.request.user
        )
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.for_user(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["message"].queryset = Message.objects.for_user(
            self.request.user
        )
        form.fields["recipients"].queryset = Recipient.objects.for_user(
            self.request.user
        )
        return form

    def form_valid(self, form):
        if form.instance.owner != self.request.user:
            return self.handle_no_permission()
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки."""

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.for_user(self.request.user)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список попыток рассылки."""

    model = MailingAttempt
    template_name = "mailings/mailing_attempt_list.html"
    context_object_name = "attempts"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return MailingAttempt.objects.filter(
            mailing__owner=self.request.user,
        )


class DisableMailingView(LoginRequiredMixin, View):
    def post(
        self,
        request,
        pk,
    ) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
        if not is_manager(request.user):
            raise PermissionDenied(
                "Только менеджеры могут отключать рассылки",
            )

        mailing = get_object_or_404(Mailing, pk=pk)

        mailing.status = MailingStatus.DISABLED
        mailing.save()

        return redirect(reverse_lazy("mailings:mailing_list"))
