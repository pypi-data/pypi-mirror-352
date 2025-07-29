from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_notifications.factories import NotificationFactory
from sparkplug_notifications.views.list import ListView

from ..utils import create_partition_for_today


class TestListView(TestCase):
    def setUp(self):
        # Create a partition for the current date
        create_partition_for_today()

        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.other_user = UserFactory()

        # Create notifications for testing
        self.notification1 = NotificationFactory(
            recipient=self.user,
            is_starred=True,
            has_read=False,
        )
        self.notification2 = NotificationFactory(
            recipient=self.user,
            is_starred=False,
            has_read=True,
        )
        self.notification3 = NotificationFactory(
            recipient=self.other_user,
            is_starred=True,
            has_read=False,
        )

    def test_list_view_returns_notifications_for_user(self):
        request = self.factory.get("/notifications/")
        force_authenticate(request, user=self.user)

        view = ListView.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert self.notification1.uuid in [
            notification["uuid"] for notification in response.data["results"]
        ]
        assert self.notification2.uuid in [
            notification["uuid"] for notification in response.data["results"]
        ]

    def test_list_view_filters_is_starred_notifications(self):
        request = self.factory.get("/notifications/", {"is_starred": "true"})
        force_authenticate(request, user=self.user)

        view = ListView.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert self.notification1.uuid in [
            notification["uuid"] for notification in response.data["results"]
        ]

    def test_list_view_excludes_other_users_notifications(self):
        request = self.factory.get("/notifications/")
        force_authenticate(request, user=self.other_user)

        view = ListView.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert self.notification3.uuid in [
            notification["uuid"] for notification in response.data["results"]
        ]
