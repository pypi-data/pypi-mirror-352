from unittest.mock import MagicMock, patch

from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_avatars.models import Avatar
from sparkplug_avatars.views.upload import UploadView


class TestUploadView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()

    @patch("sparkplug_avatars.views.upload.get_validated_dataclass")
    @patch("sparkplug_avatars.views.upload.process_avatar_task")
    @patch("sparkplug_avatars.models.Avatar.objects.update_or_create")
    def test_upload_view_creates_avatar(
        self,
        mock_update_or_create,
        mock_process_avatar_task,
        mock_get_validated_dataclass,
    ):
        # Mock validated data
        mock_get_validated_dataclass.return_value = MagicMock(file="test.jpg")

        # Mock file-like object with width and height
        mock_file = MagicMock()
        mock_file.width = 100
        mock_file.height = 100

        # Mock Avatar instance
        mock_avatar = MagicMock(
            spec=Avatar, creator=self.user, file=mock_file, uuid="mock-uuid"
        )
        mock_update_or_create.return_value = (mock_avatar, True)

        # Create a POST request
        request = self.factory.post(
            "/api/avatars/upload/",
            data={"file": "test.jpg"},
            format="multipart",
        )
        force_authenticate(request, user=self.user)

        # Call the view
        response = UploadView.as_view()(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        mock_update_or_create.assert_called_once_with(
            creator=self.user, defaults={"file": "test.jpg"}
        )
        mock_process_avatar_task.assert_called_once_with("mock-uuid")

    @patch("sparkplug_avatars.views.upload.get_validated_dataclass")
    def test_upload_view_invalid_data(self, mock_get_validated_dataclass):
        # Mock invalid data
        mock_get_validated_dataclass.side_effect = ValidationError(
            "Invalid data"
        )

        # Create a POST request
        request = self.factory.post(
            "/api/avatars/upload/",
            data={"file": "invalid.txt"},
            format="multipart",
        )
        force_authenticate(request, user=self.user)

        # Call the view
        response = UploadView.as_view()(request)

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Avatar.objects.filter(creator=self.user).exists()
