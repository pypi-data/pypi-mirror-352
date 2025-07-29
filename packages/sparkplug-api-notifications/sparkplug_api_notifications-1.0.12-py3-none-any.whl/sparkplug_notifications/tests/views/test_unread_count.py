from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_notifications.factories import NotificationFactory
from sparkplug_notifications.views.unread_count import UnreadCountView

from ..utils import create_partition_for_today


class TestUnreadCountView(TestCase):
    def setUp(self):
        # Create a partition for the current date
        create_partition_for_today()

        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.other_user = UserFactory()

        # Create notifications for testing
        NotificationFactory(recipient=self.user, has_read=False)
        NotificationFactory(recipient=self.user, has_read=True)
        NotificationFactory(recipient=self.other_user, has_read=False)

    def test_unread_count_view_returns_correct_count(self):
        request = self.factory.get("/notifications/unread-count/")
        force_authenticate(request, user=self.user)

        view = UnreadCountView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert response.data == 1  # One unread notification for self.user

    def test_unread_count_view_returns_zero_for_no_notifications(self):
        new_user = UserFactory()
        request = self.factory.get("/notifications/unread-count/")
        force_authenticate(request, user=new_user)

        view = UnreadCountView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert response.data == 0  # No notifications for new_user
