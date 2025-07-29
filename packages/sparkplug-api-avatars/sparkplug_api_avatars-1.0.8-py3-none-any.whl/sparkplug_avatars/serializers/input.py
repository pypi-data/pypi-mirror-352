from dataclasses import dataclass

from django.core.files import File
from rest_framework.exceptions import ValidationError
from rest_framework.fields import FileField
from rest_framework_dataclasses.serializers import DataclassSerializer


@dataclass
class InputData:
    file: File

    def __post_init__(self):
        allowed_extensions = ["jpg", "jpeg", "png"]
        if not any(self.file.name.endswith(ext) for ext in allowed_extensions):
            ext_msg = ", ".join(allowed_extensions)
            msg = f"File must have one of the following extensions: {ext_msg}"
            raise ValidationError({"file": msg})


class InputSerializer(DataclassSerializer):
    serializer_field_mapping = {
        **DataclassSerializer.serializer_field_mapping,
        File: FileField,
    }

    class Meta:
        dataclass = InputData
