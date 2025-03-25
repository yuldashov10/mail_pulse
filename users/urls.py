from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
)
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "email-verification-sent/",
        views.EmailVerificationSentView.as_view(),
        name="email_verification_sent",
    ),
    path(
        "verify-email/<uuid:token>/",
        views.VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutView.as_view(next_page="users:login"),
        name="logout",
    ),
    path(
        "profile/",
        views.ProfileDetailView.as_view(),
        name="profile_detail",
    ),
    path(
        "profile/edit/",
        views.ProfileEditView.as_view(),
        name="profile_edit",
    ),
    path(
        "password_reset/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
