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


urlpatterns = [path("recipients/", include(recipients_urls))]
