from typing import Optional

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import (
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.contrib.auth.views import (
    PasswordResetView as BasePasswordResetView,
)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    UpdateView,
)

from users.forms import RegistrationForm, UserChangeForm
from users.models import EmailVerificationToken, User
from utils.users import is_manager


class RegisterView(CreateView):
    """Регистрация пользователя с подтверждением email."""

    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:email_verification_sent")

    def form_valid(self, form) -> HttpResponseRedirect:
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = EmailVerificationToken.objects.create(user=user)
        verification_url = self.request.build_absolute_uri(
            reverse_lazy(
                "users:verify_email",
                kwargs={"token": str(token.token)},
            )
        )
        send_mail(
            "Подтверждение регистрации в Mail Pulse",
            f"Перейдите по ссылке для активации: {verification_url}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class EmailVerificationSentView(TemplateView):
    """Страница после отправки письма подтверждения."""

    template_name = "users/email_verification_sent.html"


class VerifyEmailView(TemplateView):
    """Подтверждение email."""

    template_name = "users/email_verified.html"

    def get(self, request, *args, **kwargs) -> TemplateResponse:
        token = self.kwargs.get("token")
        try:
            verification_token = EmailVerificationToken.objects.get(
                token=token,
            )
            user = verification_token.user
        except EmailVerificationToken.DoesNotExist:
            return self.render_to_response(
                {"error": "Недействительная ссылка"}
            )

        if not verification_token.is_valid():
            return self.render_to_response(
                {"error": "Срок действия ссылки истёк"}
            )

        user.is_active = True
        user.save()
        verification_token.delete()  # Удаляем токен после использования
        login(request, user)
        return super().get(request, *args, **kwargs)


class LoginView(BaseLoginView):
    """Вход пользователя."""

    template_name = "users/login.html"
    success_url = reverse_lazy("home")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Просмотр профиля пользователя."""

    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None) -> User:
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = UserChangeForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None) -> User:
        return self.request.user


class PasswordResetView(BasePasswordResetView):
    """Сброс пароля."""

    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.txt"
    html_email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")

    def form_valid(self, form) -> HttpResponseRedirect:
        email = form.cleaned_data["email"]

        if not User.objects.filter(email=email).exists():
            form.add_error("email", "Пользователь с таким email не найден")
            return self.form_invalid(form)

        return super().form_valid(form)


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    """Подтверждение сброса пароля."""

    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form) -> HttpResponseRedirect:
        # Получаем пользователя из формы сброса
        user = self.get_user(self.kwargs["uidb64"])
        if not user:
            return self.form_invalid(form)

        new_password = form.cleaned_data["new_password1"]
        if check_password(new_password, user.password):
            form.add_error(
                "new_password2",
                "Новый пароль не может совпадать со старым",
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_user(self, uidb64) -> Optional[User]:
        """Получает пользователя из uidb64."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

        return user


class BlockUserView(LoginRequiredMixin, View):
    """Блокировка пользователя."""

    template_name = "users/block_user_confirm.html"

    def __is_manager(self, user):
        if not is_manager(user):
            raise PermissionDenied(
                "Только менеджеры могут блокировать пользователей"
            )

    def __is_not_self(self, user_to_block, curr_user):
        if user_to_block == curr_user:
            raise PermissionDenied("Нельзя заблокировать самого себя")

    def get(
        self,
        request,
        pk,
    ) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
        self.__is_manager(request.user)

        user = get_object_or_404(User, pk=pk)
        self.__is_not_self(user, request.user)

        if user.is_blocked:
            return redirect(reverse_lazy("mailings:mailing_list"))

        return render(request, self.template_name, {"user_to_block": user})

    def post(
        self,
        request,
        pk,
    ) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
        self.__is_manager(request.user)

        user = get_object_or_404(User, pk=pk)
        self.__is_not_self(user, request.user)

        user.is_blocked = True
        user.save()

        return redirect(reverse_lazy("mailings:mailing_list"))
