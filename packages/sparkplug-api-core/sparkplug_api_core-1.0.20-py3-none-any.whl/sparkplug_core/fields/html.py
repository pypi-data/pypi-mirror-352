from bleach import clean
from bleach.sanitizer import ALLOWED_TAGS
from rest_framework import serializers


class HtmlField(serializers.CharField):
    EXTRA_ALLOWED_TAGS = (
        "br",
        "p",
        "s",  # strike
        "strike",
        "u",
    )

    def to_internal_value(self, data: dict) -> dict:
        value = super().to_internal_value(data)

        tags = ALLOWED_TAGS + self.EXTRA_ALLOWED_TAGS

        return clean(value, tags=tags)
