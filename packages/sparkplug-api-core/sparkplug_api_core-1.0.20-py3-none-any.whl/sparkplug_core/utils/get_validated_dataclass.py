from dataclasses import dataclass

from rest_framework.exceptions import ValidationError
from rest_framework_dataclasses.serializers import DataclassSerializer


def get_validated_dataclass(
    serializer_class: DataclassSerializer,
    *,
    input_data: dict,
) -> dataclass:
    """Validate serializer input data and return a dataclass."""
    serializer = serializer_class(data=input_data)
    if not serializer.is_valid():
        raise ValidationError(detail=serializer.errors)

    # Return the validated dataclass instance directly
    return serializer.validated_data
