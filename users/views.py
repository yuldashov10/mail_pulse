from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import (
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.contrib.auth.views import (
    PasswordResetView as BasePasswordResetView,
)
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import RegistrationForm, UserChangeForm
from .models import User


class RegisterView(CreateView):
    """Регистрация пользователя с подтверждением email."""

    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:email_verification_sent")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = self.request.build_absolute_uri(
            reverse_lazy(
                "users:verify_email",
                kwargs={"uidb64": uid, "token": token},
            )
        )
        send_mail(
            "Подтверждение регистрации в MailPulse",
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

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return super().get(request, *args, **kwargs)
        return self.render_to_response({"error": "Недействительная ссылка"})


class LoginView(BaseLoginView):
    """Вход пользователя."""

    template_name = "users/login.html"
    success_url = reverse_lazy("mailings:home")


class ProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = UserChangeForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("mailings:home")

    def get_object(self, queryset=None):
        return self.request.user


class PasswordResetView(BasePasswordResetView):
    """Сброс пароля."""

    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.txt"
    html_email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    """Подтверждение сброса пароля."""

    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:login")
