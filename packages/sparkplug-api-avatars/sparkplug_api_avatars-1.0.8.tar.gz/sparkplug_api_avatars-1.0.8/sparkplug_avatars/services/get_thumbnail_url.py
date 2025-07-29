from decouple import config
from django.conf import settings
from sorl.thumbnail import get_thumbnail

from ..models import Avatar


def get_thumbnail_url(
    obj: Avatar,
    crop_image: bool,
    thumbnail_size: str,
) -> str:
    if not obj.file:
        return ""

    file_width = obj.file.width
    file_height = obj.file.height
    landscape = file_width >= file_height

    thumbnail_config = {"quality": 100}

    if crop_image:
        thumbnail_config["crop"] = "center"
        geometry_string = thumbnail_size

    else:
        preset_width, preset_height = thumbnail_size.split("x")
        geometry_string = f"x{preset_height}"
        if landscape:
            geometry_string = preset_width

    thumbnail_config["geometry_string"] = geometry_string

    thumbnail = get_thumbnail(
        obj.file,
        **thumbnail_config,
    )

    environment = config("API_ENV")
    thumbnail_url = thumbnail.url
    if environment == "dev":
        thumbnail_url = f"{settings.API_URL}{thumbnail.url}"

    return thumbnail_url
