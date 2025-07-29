from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_notifications.factories import NotificationFactory
from sparkplug_notifications.views.mark_read import MarkReadView

from ..utils import create_partition_for_today


class TestMarkReadView(TestCase):
    def setUp(self):
        # Create a partition for the current date
        create_partition_for_today()

        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.other_user = UserFactory()

        # Create notifications for testing
        self.notification1 = NotificationFactory(
            recipient=self.user, has_read=False
        )
        self.notification2 = NotificationFactory(
            recipient=self.user, has_read=False
        )
        self.notification3 = NotificationFactory(
            recipient=self.other_user, has_read=False
        )

    def test_mark_read_marks_notifications_as_read(self):
        uuids = [self.notification1.uuid, self.notification2.uuid]
        request = self.factory.patch(
            "/notifications/mark-read/", {"uuids": uuids}, format="json"
        )
        force_authenticate(request, user=self.user)

        view = MarkReadView.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.notification3.refresh_from_db()

        assert self.notification1.has_read is True
        assert self.notification2.has_read is True
        assert self.notification3.has_read is False

    def test_mark_read_does_not_affect_other_users_notifications(self):
        uuids = [self.notification1.uuid]
        request = self.factory.patch(
            "/notifications/mark-read/", {"uuids": uuids}, format="json"
        )
        force_authenticate(request, user=self.user)

        view = MarkReadView.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.notification1.refresh_from_db()
        self.notification3.refresh_from_db()

        assert self.notification1.has_read is True
        assert self.notification3.has_read is False
