from django.urls import path

from . import views

app_name = "sparkplug_notifications"

urlpatterns = [
    path(
        "mark-read/",
        views.MarkReadView.as_view(),
        name="mark-read",
    ),
    path(
        "<str:uuid>/set-star/",
        views.SetStarView.as_view(),
        name="set-star",
    ),
    path(
        "unread-count/",
        views.UnreadCountView.as_view(),
        name="unread-count",
    ),
    path(
        "",
        views.ListView.as_view(),
        name="list",
    ),
]
