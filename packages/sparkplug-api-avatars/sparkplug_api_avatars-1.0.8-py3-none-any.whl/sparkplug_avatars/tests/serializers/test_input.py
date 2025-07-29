from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from sparkplug_avatars.serializers.input import InputData, InputSerializer


class TestInputData(TestCase):
    def test_valid_file_extension(self):
        mock_file = MagicMock(spec=SimpleUploadedFile, name="image.jpg")
        input_data = InputData(file=mock_file)
        self.assertEqual(input_data.file, mock_file)

    def test_invalid_file_extension(self):
        mock_file = SimpleUploadedFile(
            "document.pdf", b"file_content", content_type="application/pdf"
        )
        with self.assertRaises(ValidationError) as excinfo:
            InputData(file=mock_file)
        self.assertIn(
            "File must have one of the following extensions",
            str(excinfo.exception),
        )


class TestInputSerializer(TestCase):
    def test_serializer_with_valid_data(self):
        file = SimpleUploadedFile(
            "image.png", b"file_content", content_type="image/png"
        )
        data = {"file": file}
        serializer = InputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertEqual(validated_data.file, file)

    def test_serializer_with_invalid_data(self):
        file = SimpleUploadedFile(
            "document.pdf", b"file_content", content_type="application/pdf"
        )
        data = {"file": file}
        serializer = InputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)
        self.assertIn(
            "File must have one of the following extensions: jpg, jpeg, png",
            serializer.errors["file"],
        )
