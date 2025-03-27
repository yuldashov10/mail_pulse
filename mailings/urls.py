from django.urls import include, path

from . import views

app_name = "mailings"

recipients_urls = [
    path(
        "",
        views.RecipientListView.as_view(),
        name="recipient_list",
    ),
    path(
        "create/",
        views.RecipientCreateView.as_view(),
        name="recipient_create",
    ),
    path(
        "<int:pk>/",
        views.RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "<int:pk>/update/",
        views.RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "<int:pk>/delete/",
        views.RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
]

messages_urls = [
    path(
        "",
        views.MessageListView.as_view(),
        name="message_list",
    ),
    path(
        "create/",
        views.MessageCreateView.as_view(),
        name="message_create",
    ),
    path(
        "<int:pk>/",
        views.MessageDetailView.as_view(),
        name="message_detail",
    ),
    path(
        "<int:pk>/update/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "<int:pk>/delete/",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
]

mailings_urls = [
    path(
        "",
        views.MailingListView.as_view(),
        name="mailing_list",
    ),
    path(
        "create/",
        views.MailingCreateView.as_view(),
        name="mailing_create",
    ),
    path(
        "<int:pk>/",
        views.MailingDetailView.as_view(),
        name="mailing_detail",
    ),
    path(
        "<int:pk>/update/",
        views.MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "<int:pk>/delete/",
        views.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path(
        "<int:pk>/disable/",
        views.DisableMailingView.as_view(),
        name="mailing_disable",
    ),
]

attempts_urls = [
    path(
        "",
        views.MailingAttemptListView.as_view(),
        name="mailing_attempt_list",
    ),
]

urlpatterns = [
    path("recipients/", include(recipients_urls)),
    path("messages/", include(messages_urls)),
    path("mailings/", include(mailings_urls)),
    path("attempts/", include(attempts_urls)),
]
