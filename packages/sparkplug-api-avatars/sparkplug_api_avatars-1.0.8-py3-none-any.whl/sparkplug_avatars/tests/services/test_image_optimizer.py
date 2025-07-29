from unittest.mock import MagicMock, patch

from django.test import TestCase
from PIL import Image

from sparkplug_avatars.services.image_optimizer import ImageOptimizer


class TestImageOptimizer(TestCase):
    def setUp(self):
        self.source = "/path/to/source/image.png"
        self.filename = "optimized_image"
        self.max_long = 1920
        self.max_short = 1080

    @patch("sparkplug_avatars.services.image_optimizer.Image.open")
    @patch(
        "sparkplug_avatars.services.image_optimizer.ImageOptimizer._save_image"
    )
    def test_optimize_resizes_large_image(
        self, mock_save_image, mock_image_open
    ):
        # Mock the image object
        mock_image = MagicMock(spec=Image)
        mock_image.size = (4000, 3000)  # Large image dimensions
        mock_image.width = 4000
        mock_image.height = 3000
        mock_image.format = "PNG"  # Set the format to a non-JPEG value
        mock_image.resize = MagicMock(return_value=mock_image)
        mock_image.crop = MagicMock(return_value=mock_image)
        mock_image.convert = MagicMock(return_value=mock_image)
        mock_image_open.return_value.__enter__.return_value = mock_image

        optimizer = ImageOptimizer(
            source=self.source,
            filename=self.filename,
            max_long=self.max_long,
            max_short=self.max_short,
        )
        filepath, optimized = optimizer.optimize()

        assert optimized is True
        assert filepath == f"/tmp/{self.filename}.jpg"
        mock_image.resize.assert_called_once_with((1440, 1080))
        mock_image.convert.assert_called_once_with("RGB")
        mock_save_image.assert_called_once()

    @patch("sparkplug_avatars.services.image_optimizer.Image.open")
    def test_optimize_skips_small_image(self, mock_image_open):
        # Mock the image object
        mock_image = MagicMock(spec=Image)
        mock_image.size = (800, 600)  # Small image dimensions
        mock_image.format = "JPEG"
        mock_image.width = 800
        mock_image.height = 600
        mock_image.crop = MagicMock()
        mock_image.resize = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        optimizer = ImageOptimizer(
            source=self.source,
            filename=self.filename,
            max_long=self.max_long,
            max_short=self.max_short,
        )
        filepath, optimized = optimizer.optimize()

        assert optimized is False
        assert filepath == f"/tmp/{self.filename}.jpg"
        mock_image.resize.assert_not_called()
        mock_image.crop.assert_not_called()  # Ensure crop is not called for small images

    @patch("sparkplug_avatars.services.image_optimizer.Image.open")
    def test_optimize_crops_to_aspect_ratio(self, mock_image_open):
        # Mock the image object
        mock_image = MagicMock(spec=Image)
        mock_image.format = "JPEG"
        mock_image.size = (2000, 1000)  # Aspect ratio mismatch
        mock_image.width = 2000
        mock_image.height = 1000
        mock_image.resize = MagicMock(return_value=mock_image)
        mock_image.crop = MagicMock(return_value=mock_image)
        mock_image.save = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        optimizer = ImageOptimizer(
            source=self.source,
            filename=self.filename,
            max_long=self.max_long,
            max_short=self.max_short,
        )
        optimizer.optimize()

        # Ensure crop is called with the correct dimensions
        mock_image.crop.assert_called_once_with((111, 0, 1888, 1000))

        # Ensure save is called with the correct arguments
        mock_image.save.assert_called_once_with(
            f"/tmp/{self.filename}.jpg",
            quality=80,
            optimize=True,
        )

    @patch("sparkplug_avatars.services.image_optimizer.Image.open")
    def test_optimize_converts_to_jpeg(self, mock_image_open):
        # Mock the image object
        mock_image = MagicMock(spec=Image)
        mock_image.format = "PNG"  # Non-JPEG format
        mock_image.size = (800, 600)  # Small image dimensions
        mock_image.width = 800
        mock_image.height = 600
        mock_image.convert = MagicMock(return_value=mock_image)
        mock_image.save = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image

        optimizer = ImageOptimizer(
            source=self.source,
            filename=self.filename,
            max_long=self.max_long,
            max_short=self.max_short,
        )
        optimizer.optimize()

        # Ensure the image is converted to RGB
        mock_image.convert.assert_called_once_with("RGB")

        # Ensure the image is saved with the correct arguments
        mock_image.save.assert_called_once_with(
            f"/tmp/{self.filename}.jpg",
            quality=80,
            optimize=True,
        )
