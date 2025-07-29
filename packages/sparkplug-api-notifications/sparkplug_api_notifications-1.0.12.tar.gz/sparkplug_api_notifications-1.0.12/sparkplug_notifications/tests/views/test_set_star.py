from unittest.mock import patch

from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_notifications.factories import NotificationFactory
from sparkplug_notifications.views import SetStarView

from ..utils import create_partition_for_today


@patch("sparkplug_notifications.views.set_star.enforce_permission")
class TestSetStarView(TestCase):
    def setUp(self):
        # Create a partition for the current date
        create_partition_for_today()

        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.notification = NotificationFactory(
            recipient=self.user,
            is_starred=False,
        )

    def test_set_star_view_updates_is_starred_field(
        self, mock_enforce_permission
    ):
        # Mock enforce_permission to return True for the recipient
        mock_enforce_permission.return_value = True

        request = self.factory.patch(
            f"/notifications/set-star/{self.notification.uuid}/",
            data={"is_starred": True},
            format="json",
        )
        force_authenticate(request, user=self.user)

        view = SetStarView.as_view()
        response = view(request, uuid=self.notification.uuid)

        self.notification.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert self.notification.is_starred is True

    def test_set_star_view_fails_for_unauthorized_user(
        self, mock_enforce_permission
    ):
        # Mock enforce_permission to raise PermissionDenied for unauthorized user
        mock_enforce_permission.side_effect = PermissionDenied

        request = self.factory.patch(
            f"/notifications/set-star/{self.notification.uuid}/",
            data={"is_starred": True},
            format="json",
        )
        force_authenticate(request, user=self.other_user)

        view = SetStarView.as_view()
        response = view(request, uuid=self.notification.uuid)

        self.notification.refresh_from_db()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert self.notification.is_starred is False

    def test_set_star_view_fails_for_invalid_data(
        self, mock_enforce_permission
    ):
        # Mock enforce_permission to return True for the recipient
        mock_enforce_permission.return_value = True

        request = self.factory.patch(
            f"/notifications/set-star/{self.notification.uuid}/",
            data={"is_starred": "invalid_value"},
            format="json",
        )
        force_authenticate(request, user=self.user)

        view = SetStarView.as_view()
        response = view(request, uuid=self.notification.uuid)

        self.notification.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.notification.is_starred is False
